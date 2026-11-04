"""Meta Model API client (OpenAI-compatible Chat Completions endpoint).

Configure with environment variables (or a .env file):
    META_API_KEY      your Meta Model API key
    META_BASE_URL     the API base URL from the Meta quickstart
    META_MODEL        Muse Spark model id permitted by the event (e.g. muse-spark-1.3)

Optional open-weight route (for the open-weight bonus), via Baseten:
    BASETEN_API_KEY, BASETEN_BASE_URL, BASETEN_MODEL=meta-models/muse-spark-open-1026

Muse Spark 1.3 is a *reasoning* model: it thinks before it answers, so a reply can
be cut off if the output budget is too small. Every call here therefore

  - asks for at least 8000 output tokens (``MIN_MAX_TOKENS``),
  - sends ``temperature=0`` where the endpoint supports it,
  - requests a JSON Schema via ``response_format`` where the endpoint supports it
    (see https://dev.meta.ai/docs/structured-output), falling back to the plain
    prompt-plus-parse path if the endpoint rejects it,
  - gives every request an explicit wall-clock timeout (``META_TIMEOUT``) and
    retries a bounded number of times when a request *times out*: Muse Spark is
    slow, not broken, and a slow-but-good reading must not be recorded as a
    failed one (see ``META_TIMEOUT_ATTEMPTS`` / ``META_TIMEOUT_BACKOFF``),
  - and treats a truncated (``finish_reason == "length"``) or empty reply as a
    FAILED call: it raises ``ModelCallFailed`` instead of returning an empty
    answer, so an empty reading can never be mistaken for "no differences".
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

log = logging.getLogger("legible.meta")

# Muse Spark 1.3 reasons internally before answering; a small budget truncates it.
MIN_MAX_TOKENS = 8000
DEFAULT_MAX_TOKENS = 8000

# Wall-clock seconds to wait for one reply. Muse Spark reasons before it answers,
# so this is generous; override with the META_TIMEOUT env var for a slow endpoint.
DEFAULT_TIMEOUT = 180.0
# A timeout is the one failure worth retrying: the endpoint is slow, not wrong.
# Retry a bounded number of times, backing off, so a slow-but-good reading is not
# thrown away. A definitive failure (bad key, rejected parameter, HTTP 4xx) is
# never retried here — it still fails closed.
DEFAULT_TIMEOUT_ATTEMPTS = 3
DEFAULT_TIMEOUT_BACKOFF = 4.0

# Capability flags, flipped off the first time the endpoint rejects an optional
# parameter, so we fall back cleanly instead of failing the run.
_TEMPERATURE_SUPPORTED = True
_RESPONSE_FORMAT_SUPPORTED = True


class ModelUnavailable(RuntimeError):
    pass


class ModelCallFailed(RuntimeError):
    """The model was reached, but the reply is unusable (truncated or empty)."""


class BadModelJSON(ValueError):
    """The model replied, but with text we could not parse as a JSON object."""


def _timeout() -> float:
    """Per-request wall-clock timeout, from META_TIMEOUT or the default."""
    try:
        return float(os.getenv("META_TIMEOUT", DEFAULT_TIMEOUT))
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT


def _timeout_attempts() -> int:
    """How many times to (re)send a request that keeps timing out."""
    try:
        return max(1, int(os.getenv("META_TIMEOUT_ATTEMPTS", DEFAULT_TIMEOUT_ATTEMPTS)))
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT_ATTEMPTS


def _timeout_backoff() -> float:
    """Seconds to wait between timeout retries."""
    try:
        return max(0.0, float(os.getenv("META_TIMEOUT_BACKOFF", DEFAULT_TIMEOUT_BACKOFF)))
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT_BACKOFF


def _is_timeout(e: Exception) -> bool:
    """True for a request that timed out (a transport timeout, not a bad request).

    Only timeouts are retried: they mean the endpoint was slow, not that the
    request was wrong. Everything else is re-raised so it still fails closed.
    """
    try:
        from openai import APITimeoutError
    except Exception:  # pragma: no cover - openai is a hard dependency in practice
        APITimeoutError = ()  # type: ignore[assignment]
    if APITimeoutError and isinstance(e, APITimeoutError):
        return True
    return isinstance(e, TimeoutError) or "timed out" in str(e).lower()


def _client(route: str = "meta"):
    from openai import OpenAI
    if route == "baseten":
        key, url = os.getenv("BASETEN_API_KEY"), os.getenv("BASETEN_BASE_URL")
    else:
        key, url = os.getenv("META_API_KEY"), os.getenv("META_BASE_URL")
    if not key or not url:
        raise ModelUnavailable(f"{route} API key or base URL not set")
    # An explicit timeout keeps a slow call from hanging forever; a timed-out
    # call is retried in _create rather than recorded as a failed reading.
    return OpenAI(api_key=key, base_url=url, timeout=_timeout())


def model_name(route: str = "meta") -> str:
    if route == "baseten":
        return os.getenv("BASETEN_MODEL", "meta-models/muse-spark-open-1026")
    return os.getenv("META_MODEL", "muse-spark-1.3")


def available(route: str = "meta") -> bool:
    try:
        _client(route)
        return True
    except ModelUnavailable:
        return False


def _image_part(png_path: str) -> dict:
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}


def _reply_text(resp, route: str) -> str:
    """Return the reply text, or raise if the call did not produce a usable one.

    A reasoning model can stop because it ran out of room (``finish_reason ==
    "length"``) or produce nothing at all. Both are failures, never an empty
    answer: callers must not treat "" as a valid reading or as "no differences".
    """
    choice = resp.choices[0]
    finish = getattr(choice, "finish_reason", None)
    text = choice.message.content
    n = len(text or "")
    if finish == "length":
        log.warning("%s reply truncated: finish_reason=length chars=%d", route, n)
        raise ModelCallFailed(
            f"{route} reply was truncated (finish_reason='length'); "
            f"raise max_tokens above {DEFAULT_MAX_TOKENS}"
        )
    if not text or not text.strip():
        log.warning("%s reply empty: finish_reason=%r", route, finish)
        raise ModelCallFailed(f"{route} reply was empty (finish_reason={finish!r})")
    log.info("%s reply ok: finish_reason=%r chars=%d", route, finish, n)
    return text


def _mentions(e: Exception, name: str) -> bool:
    return name.lower() in str(e).lower()


def _create(route: str, content, max_tokens: int, response_format):
    """Call chat.completions.create, with timeout retries and param fallback.

    A *timed-out* request is retried (bounded, with backoff): Muse Spark is slow,
    and a slow-but-good reply must not be recorded as a failed reading. Any other
    error keeps the original behaviour — drop a rejected optional parameter once
    and retry, otherwise propagate so the caller fails closed.
    """
    global _TEMPERATURE_SUPPORTED, _RESPONSE_FORMAT_SUPPORTED
    kwargs = {
        "model": model_name(route),
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max(max_tokens, MIN_MAX_TOKENS),
    }
    if _TEMPERATURE_SUPPORTED:
        kwargs["temperature"] = 0
    if response_format is not None and _RESPONSE_FORMAT_SUPPORTED:
        kwargs["response_format"] = response_format

    attempts = _timeout_attempts()
    for attempt in range(1, attempts + 1):
        try:
            return _client(route).chat.completions.create(**kwargs)
        except Exception as e:
            if _is_timeout(e):
                if attempt < attempts:
                    log.warning(
                        "%s request timed out (attempt %d/%d); retrying in %.1fs: %s",
                        route, attempt, attempts, _timeout_backoff(), e)
                    time.sleep(_timeout_backoff())
                    continue
                raise
            changed = False
            if "temperature" in kwargs and _mentions(e, "temperature"):
                _TEMPERATURE_SUPPORTED = False
                kwargs.pop("temperature")
                changed = True
                log.warning("endpoint rejected temperature; retrying without it: %s", e)
            if "response_format" in kwargs and _mentions(e, "response_format"):
                _RESPONSE_FORMAT_SUPPORTED = False
                kwargs.pop("response_format")
                changed = True
                log.warning("endpoint rejected response_format; retrying without it: %s", e)
            if not changed:
                raise
            return _client(route).chat.completions.create(**kwargs)
    # Unreachable: the loop returns or raises on its final attempt.
    raise ModelCallFailed(f"{route} request failed without a reply")


def ask(
    prompt: str,
    images: list[str] = (),
    route: str = "meta",
    max_tokens: int = DEFAULT_MAX_TOKENS,
    response_format: dict | None = None,
) -> str:
    """Send text plus images to Muse Spark and return the (non-empty) text reply.

    Raises ``ModelCallFailed`` when the model was truncated or returned nothing.
    """
    content = [{"type": "text", "text": prompt}] + [_image_part(p) for p in images]
    resp = _create(route, content, max_tokens, response_format)
    return _reply_text(resp, route)


# ----------------------------------------------------- structured output ---

def json_schema(name: str, properties: dict, required: list[str]) -> dict:
    """Build a ``response_format`` that constrains decoding to a JSON object."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "schema": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


LATEX_SCHEMA = json_schema("latex", {"latex": {"type": "string"}}, ["latex"])
PAGE_TEXT_SCHEMA = json_schema("page_text", {"text": {"type": "string"}}, ["text"])
COMPARE_SCHEMA = json_schema(
    "differences",
    {"differences": {"type": "array", "items": {"type": "string"}}},
    ["differences"],
)
REPAIR_SCHEMA = json_schema(
    "repair",
    {
        "latex": {"type": "string"},
        "changed": {"type": "boolean"},
        "note": {"type": "string"},
    },
    ["latex", "changed", "note"],
)

# The instruction appended to every JSON request, used both as a prompt nudge and
# as the fallback contract when the endpoint does not support response_format.
_JSON_HINT = "\n\nReply with a single JSON object only."


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a reply, tolerating code fences."""
    # Prefer a fenced ```json block when present, else the first {...}.
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = fence.group(1) if fence else None
    if candidate is None:
        m = re.search(r"\{.*\}", text, re.S)
        candidate = m.group(0) if m else None
    if candidate is None:
        raise BadModelJSON(f"no JSON object in model reply: {text[:200]!r}")
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as e:
        raise BadModelJSON(f"model reply was not valid JSON ({e}): {candidate[:200]!r}")
    if not isinstance(data, dict):
        raise BadModelJSON(f"model reply was a {type(data).__name__}, not an object")
    return data


def ask_json(
    prompt: str,
    images: list[str] = (),
    route: str = "meta",
    schema: dict | None = None,
) -> dict:
    """Ask for a JSON object and parse it.

    When ``schema`` is given, it is sent as ``response_format`` so decoding is
    constrained (the Meta API documents this); if the endpoint rejects it we fall
    back to prompt-plus-parse automatically. Retries once (with a firmer
    instruction) if the first reply is not parseable as a JSON object, then
    raises ``BadModelJSON``.
    """
    fmt = schema if (_RESPONSE_FORMAT_SUPPORTED and schema is not None) else None
    # Only pass response_format when we actually have a schema, so a caller (or a
    # test double) whose ask() has the original signature keeps working.
    extra = {"response_format": fmt} if fmt is not None else {}
    text = ask(prompt + _JSON_HINT, images, route, **extra)
    try:
        return _extract_json(text)
    except BadModelJSON:
        retry_text = ask(
            prompt + "\n\nYour previous reply was not valid JSON. "
            "Reply with a single JSON object and nothing else — no prose, no code fences.",
            images, route, **extra,
        )
        return _extract_json(retry_text)
