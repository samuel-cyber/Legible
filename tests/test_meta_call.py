"""Model-call reliability tests (no network).

These cover the brief's Channel-A/C reliability rules:

  - every call asks for at least 8000 output tokens,
  - temperature=0 is sent where supported (and dropped if rejected),
  - response_format is sent where supported (and dropped if rejected),
  - finish_reason "length" or an empty reply is a FAILED call (raises), never an
    empty answer,
  - a *timed-out* request is retried a bounded number of times (Muse Spark is
    slow, so a slow-but-good reading must not be recorded as a failed one), while
    any non-timeout error is propagated without retrying.

meta._client is monkeypatched with a fake OpenAI client, so no credentials or
network are needed.
"""
from __future__ import annotations

import types

import pytest

from clients import meta


class _Msg:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content, finish):
        self.message = _Msg(content)
        self.finish_reason = finish


class _Resp:
    def __init__(self, content, finish="stop"):
        self.choices = [_Choice(content, finish)]


class _Timeout(Exception):
    """Stands in for openai.APITimeoutError (matched by its message)."""

    def __init__(self):
        super().__init__("Request timed out.")


class _FakeCreate:
    def __init__(self, script):
        self.script = script
        self.calls: list[dict] = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        item = self.script[min(len(self.calls) - 1, len(self.script) - 1)]
        if isinstance(item, Exception):
            raise item
        return item


def _patch(monkeypatch, script):
    create = _FakeCreate(script)
    client = types.SimpleNamespace(
        chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))
    monkeypatch.setattr(meta, "_client", lambda route="meta": client)
    return create


@pytest.fixture(autouse=True)
def _reset_caps():
    """The capability flags are module-global; reset them around every test."""
    meta._TEMPERATURE_SUPPORTED = True
    meta._RESPONSE_FORMAT_SUPPORTED = True
    yield
    meta._TEMPERATURE_SUPPORTED = True
    meta._RESPONSE_FORMAT_SUPPORTED = True


# ------------------------------------------------------------- reliability ---

def test_min_tokens_and_temperature_zero(monkeypatch):
    create = _patch(monkeypatch, [_Resp('{"latex": "x=1"}')])
    meta.ask("p")
    kw = create.calls[0]
    assert kw["max_tokens"] >= meta.MIN_MAX_TOKENS >= 8000
    assert kw["temperature"] == 0


def test_ask_floor_even_when_caller_passes_small(monkeypatch):
    create = _patch(monkeypatch, [_Resp('{"latex": "x=1"}')])
    meta.ask("p", max_tokens=100)
    assert create.calls[0]["max_tokens"] >= 8000


def test_finish_reason_length_raises(monkeypatch):
    _patch(monkeypatch, [_Resp("\\frac{a}{", finish="length")])
    with pytest.raises(meta.ModelCallFailed):
        meta.ask("p")


def test_empty_content_raises(monkeypatch):
    _patch(monkeypatch, [_Resp("")])
    with pytest.raises(meta.ModelCallFailed):
        meta.ask("p")


def test_none_content_raises(monkeypatch):
    _patch(monkeypatch, [_Resp(None)])
    with pytest.raises(meta.ModelCallFailed):
        meta.ask("p")


def test_whitespace_content_raises(monkeypatch):
    _patch(monkeypatch, [_Resp("   \n  ")])
    with pytest.raises(meta.ModelCallFailed):
        meta.ask("p")


def test_truncated_json_never_becomes_empty_answer(monkeypatch):
    """A truncated reply must raise, not be parsed into an empty result."""
    _patch(monkeypatch, [_Resp('{"differences": [', finish="length")])
    with pytest.raises(meta.ModelCallFailed):
        meta.ask_json("p", schema=meta.COMPARE_SCHEMA)


# -------------------------------------------------------- structured output --

def test_response_format_sent_when_supported(monkeypatch):
    create = _patch(monkeypatch, [_Resp('{"latex": "x=1"}')])
    assert meta.ask_json("p", schema=meta.LATEX_SCHEMA) == {"latex": "x=1"}
    fmt = create.calls[0]["response_format"]
    assert fmt["type"] == "json_schema"
    assert fmt["json_schema"]["schema"]["required"] == ["latex"]


def test_response_format_falls_back_when_rejected(monkeypatch):
    create = _patch(monkeypatch, [
        Exception("response_format is not supported for this model"),
        _Resp('{"latex": "x=1"}'),
    ])
    assert meta.ask_json("p", schema=meta.LATEX_SCHEMA) == {"latex": "x=1"}
    assert len(create.calls) == 2
    assert "response_format" in create.calls[0]
    assert "response_format" not in create.calls[1]
    assert meta._RESPONSE_FORMAT_SUPPORTED is False


def test_temperature_falls_back_when_rejected(monkeypatch):
    create = _patch(monkeypatch, [
        Exception("temperature is not a valid parameter for this model"),
        _Resp('{"latex": "x=1"}'),
    ])
    assert meta.ask_json("p", schema=meta.LATEX_SCHEMA) == {"latex": "x=1"}
    assert "temperature" in create.calls[0]
    assert "temperature" not in create.calls[1]
    # response_format was fine, so it stays.
    assert "response_format" in create.calls[1]
    assert meta._TEMPERATURE_SUPPORTED is False


def test_reply_text_is_logged(monkeypatch, caplog):
    _patch(monkeypatch, [_Resp('{"latex": "x=1"}')])
    with caplog.at_level("INFO", logger="legible.meta"):
        meta.ask("p")
    assert "finish_reason='stop'" in caplog.text


# ------------------------------------------------------ timeouts / retries --

def test_timeout_is_configurable(monkeypatch):
    monkeypatch.setenv("META_TIMEOUT", "42")
    assert meta._timeout() == 42.0
    monkeypatch.setenv("META_TIMEOUT", "not-a-number")
    assert meta._timeout() == meta.DEFAULT_TIMEOUT


def test_client_sets_explicit_timeout(monkeypatch):
    """The OpenAI client must be built with an explicit wall-clock timeout."""
    openai = pytest.importorskip("openai")
    captured: dict = {}

    class _FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(openai, "OpenAI", _FakeClient)
    monkeypatch.setenv("META_API_KEY", "k")
    monkeypatch.setenv("META_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("META_TIMEOUT", "7")
    meta._client("meta")
    assert captured["timeout"] == 7.0
    assert captured["api_key"] == "k"
    assert captured["base_url"] == "https://example.invalid"


def test_timeout_is_retried_then_succeeds(monkeypatch):
    monkeypatch.setenv("META_TIMEOUT_BACKOFF", "0")
    create = _patch(monkeypatch, [_Timeout(), _Resp('{"latex": "x=1"}')])
    assert meta.ask("p") == '{"latex": "x=1"}'
    assert len(create.calls) == 2


def test_timeout_exhausts_bounded_attempts_and_raises(monkeypatch):
    monkeypatch.setenv("META_TIMEOUT_ATTEMPTS", "2")
    monkeypatch.setenv("META_TIMEOUT_BACKOFF", "0")
    create = _patch(monkeypatch, [_Timeout()])
    with pytest.raises(Exception, match="timed out"):
        meta.ask("p")
    assert len(create.calls) == 2


def test_non_timeout_error_is_not_retried(monkeypatch):
    """A definitive failure (bad key, HTTP 4xx) must propagate at once."""
    create = _patch(monkeypatch, [Exception("401 invalid api key")])
    with pytest.raises(Exception, match="401"):
        meta.ask("p")
    assert len(create.calls) == 1
