"""ask_json robustness tests (no network).

meta.ask is monkeypatched so we can exercise parsing and the one retry,
including bad JSON, fenced JSON, prose around JSON, and a non-object reply.
"""
from __future__ import annotations

import pytest

from clients import meta


def _patch(monkeypatch, replies):
    """Make meta.ask return successive replies from a list."""
    calls = {"n": 0}

    def fake_ask(prompt, images=(), route="meta", max_tokens=2000):
        r = replies[min(calls["n"], len(replies) - 1)]
        calls["n"] += 1
        meta.ask.__dict__["_last_prompt"] = prompt
        return r

    monkeypatch.setattr(meta, "ask", fake_ask)
    return calls


def test_plain_json(monkeypatch):
    _patch(monkeypatch, ['{"latex": "x=1"}'])
    assert meta.ask_json("p") == {"latex": "x=1"}


def test_fenced_json(monkeypatch):
    _patch(monkeypatch, ['```json\n{"latex": "x=1"}\n```'])
    assert meta.ask_json("p") == {"latex": "x=1"}


def test_prose_around_json(monkeypatch):
    _patch(monkeypatch, ['Sure, here you go: {"latex": "x=1"} hope that helps'])
    assert meta.ask_json("p") == {"latex": "x=1"}


def test_retry_once_then_succeed(monkeypatch):
    calls = _patch(monkeypatch, ["I cannot help with that.", '{"latex": "x=2"}'])
    assert meta.ask_json("p") == {"latex": "x=2"}
    assert calls["n"] == 2, "should have retried exactly once"


def test_retry_then_raise(monkeypatch):
    calls = _patch(monkeypatch, ["nope", "still not json"])
    with pytest.raises(meta.BadModelJSON):
        meta.ask_json("p")
    assert calls["n"] == 2, "should give up after a single retry"


def test_non_object_json_is_rejected(monkeypatch):
    _patch(monkeypatch, ["[1, 2, 3]", "[4, 5]"])
    with pytest.raises(meta.BadModelJSON):
        meta.ask_json("p")


def test_malformed_json_is_rejected(monkeypatch):
    _patch(monkeypatch, ['{"latex": "x=1",}', '{"latex": broken}'])
    with pytest.raises(meta.BadModelJSON):
        meta.ask_json("p")
