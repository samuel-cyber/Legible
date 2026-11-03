"""Decision-rule tests (no network, no model).

These pin the new rule from the brief:

  B available  -> B is the gate, C is ADVISORY (a C finding never withholds).
  B unavailable-> C is the gate and fails closed (C error => withheld).
  A/B mismatch after one repair => withheld regardless of C.
  A model error => withheld; a C model error never verifies on its own.

A tiny synthetic glyph page stands in for Channel B, so the tests are fast and
do not depend on the demo PDF.
"""
from __future__ import annotations

import pytest

from clients import meta
from equations.decide import REPAIRED, VERIFIED, WITHHELD, verify_equation
from ingest.pdf import Glyph, Page


def _page_with(text: str) -> Page:
    """A synthetic born-digital page whose glyphs spell ``text`` on one baseline."""
    glyphs = []
    x = 100.0
    for ch in text:
        if ch.strip():
            glyphs.append(Glyph(c=ch, font="CMMI", size=10.0, x=x, y=100.0,
                                bbox=(x, 90.0, x + 6.0, 102.0)))
        x += 8.0
    return Page(number=0, width=600.0, height=800.0, glyphs=glyphs)


BBOX = (90.0, 85.0, 220.0, 110.0)          # covers the glyphs above


def _no_glyph_page() -> Page:
    """A scanned/image equation: the page has no glyphs, so B is unavailable."""
    return Page(number=0, width=600.0, height=800.0, glyphs=[])


def _render(latex, out_png, crop_png=None, fontsize=None):
    # Return the LaTeX as the "rendered" path so a compare stub can key on it.
    return latex


# --------------------------------------------------------- B available -------

def test_b_available_c_false_flag_is_advisory_not_withheld():
    """B confirms the reading and C flags a spurious difference => verified + advice."""
    page = _page_with("x=1")

    def compare(crop, rendered):
        return ["Image 1 has '1' but image 2 has 'l'"]

    r = verify_equation("e1", page, BBOX, "crop.png",
                        transcribe=lambda c: "x=1", compare=compare, render=_render,
                        use_glyphs=True)
    assert r.status == VERIFIED
    assert r.latex == "x=1"
    first = r.attempts[0]
    assert first.advisory is True
    assert first.visual_diffs == ["Image 1 has '1' but image 2 has 'l'"]
    assert first.passed, "an advisory C finding must not withhold"
    assert "advisory" in r.explanation.lower()
    assert "glyph layer confirmed" in r.explanation.lower()


def test_b_available_c_clean_is_verified():
    page = _page_with("x=1")
    r = verify_equation("e1", page, BBOX, "crop.png",
                        transcribe=lambda c: "x=1",
                        compare=lambda crop, rendered: [], render=_render,
                        use_glyphs=True)
    assert r.status == VERIFIED
    assert r.attempts[0].advisory is True
    assert r.attempts[0].visual_clean


def test_ab_mismatch_after_repair_withheld_regardless_of_c():
    """B never moves; a repair that still disagrees means withheld, even if C is clean."""
    page = _page_with("x=1")
    r = verify_equation("e1", page, BBOX, "crop.png",
                        transcribe=lambda c: "x=-1",
                        repair=lambda c, latex, diffs: "x=-1",
                        compare=lambda crop, rendered: [], render=_render,
                        use_glyphs=True)
    assert r.status == WITHHELD
    assert r.latex is None
    assert len(r.attempts) == 2, "should repair exactly once"
    assert all(a.glyph_diffs for a in r.attempts), "B must still be reporting a difference"


def test_ab_mismatch_repaired_then_verified():
    page = _page_with("x=1")
    r = verify_equation("e1", page, BBOX, "crop.png",
                        transcribe=lambda c: "x=-1",
                        repair=lambda c, latex, diffs: "x=1",
                        compare=lambda crop, rendered: [], render=_render,
                        use_glyphs=True)
    assert r.status == REPAIRED
    assert r.latex == "x=1"
    assert r.attempts[0].glyph_diffs and not r.attempts[1].glyph_diffs


# ------------------------------------------------------- B unavailable -------

def test_b_unavailable_c_clean_is_verified():
    """No glyph layer: a clean visual check is the whole gate."""
    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1",
                        compare=lambda crop, rendered: [], render=_render,
                        use_glyphs=True)
    assert r.status == VERIFIED
    assert r.latex == "x=1"
    assert "B" not in r.channels


def test_b_unavailable_c_error_is_withheld():
    """No glyph layer and the visual check errors => fail closed."""
    def compare(crop, rendered):
        raise meta.BadModelJSON("no JSON object in model reply")

    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1", compare=compare, render=_render,
                        use_glyphs=True)
    assert r.status == WITHHELD
    assert r.latex is None
    assert r.attempts[-1].visual_diffs, "the C error must be recorded as a finding"


def test_b_unavailable_c_unparseable_is_withheld():
    """Unparseable C output is a failure, never a clean pass."""
    def compare(crop, rendered):
        raise ValueError("model reply was not valid JSON")

    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1", compare=compare, render=_render,
                        use_glyphs=True)
    assert r.status == WITHHELD


def test_b_unavailable_c_flag_withholds():
    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1",
                        compare=lambda crop, rendered: ["different character"], render=_render,
                        use_glyphs=True)
    assert r.status == WITHHELD


def test_b_unavailable_c_flag_repaired_is_repaired():
    def compare(crop, rendered):
        return [] if rendered == "x=2" else ["different character"]

    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1",
                        repair=lambda c, latex, diffs: "x=2",
                        compare=compare, render=_render,
                        use_glyphs=True)
    assert r.status == REPAIRED
    assert r.latex == "x=2"


def test_b_unavailable_and_no_c_is_withheld():
    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1", use_glyphs=True)
    assert r.status == WITHHELD


# -------------------------------------------------- model-error guarantees ---

def test_a_model_error_is_withheld_even_when_c_is_clean():
    """A model error in A must never verify, whatever C says."""
    page = _page_with("x=1")

    def transcribe(crop):
        raise meta.ModelCallFailed("reply was truncated (finish_reason='length')")

    r = verify_equation("e1", page, BBOX, "crop.png",
                        transcribe=transcribe,
                        compare=lambda crop, rendered: [], render=_render,
                        use_glyphs=True)
    assert r.status == WITHHELD
    assert r.latex is None
    assert r.attempts and r.attempts[-1].parse_error


def test_c_error_alone_never_verifies():
    """With no glyph layer, a C error cannot produce a verification."""
    def compare(crop, rendered):
        raise meta.ModelCallFailed("reply was empty")

    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1", compare=compare, render=_render,
                        use_glyphs=True)
    assert r.status == WITHHELD


def test_render_failure_does_not_verify():
    """A render error is a C failure => withheld when B is absent."""
    def render(latex, out_png, crop_png=None, fontsize=None):
        raise RuntimeError("mathtext rejected the command")

    r = verify_equation("e1", _no_glyph_page(), BBOX, "crop.png",
                        transcribe=lambda c: "x=1",
                        compare=lambda crop, rendered: [], render=render,
                        use_glyphs=True)
    assert r.status == WITHHELD
