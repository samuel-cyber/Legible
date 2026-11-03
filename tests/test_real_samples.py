"""Channel B regression tests on real glyphs from actual TeX output.

Unlike ``test_glyphs.py`` (which uses the hand-built demo page), these run the
glyph layer against regions clipped straight out of the published lecture notes
in ``eval/pdfs/`` -- real pdfLaTeX geometry, real fonts. Each example pairs the
region with the LaTeX the source really contains, so these pin down the fixes
made while building the evaluation gold set:

  * a slash overlay (U+0338) folds into the "=" it strikes, giving "ne";
  * three literal dot glyphs fold into one ellipsis matching \\dots (and the
    centered \\cdots a reading may use for the same printed dots);
  * a genuine "=" with no overlay is left alone.

The two entries in ``KNOWN_MISMATCHES`` are geometry the glyph layer cannot
resolve; they must keep differing so the pipeline withholds them (fail-closed)
rather than accepting a plausible-looking reading.
"""
from __future__ import annotations

import os

import pytest

from equations.glyphs import GlyphLayerUnavailable, glyph_tokens
from equations.tokens import diff, latex_to_tokens
from eval.test_samples import KNOWN_MISMATCHES, PDFS, SAMPLES
from ingest.pdf import load_page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pytestmark = pytest.mark.skipif(
    not all(os.path.exists(os.path.join(ROOT, p)) for p in PDFS),
    reason="eval PDFs not present (see eval/sources.md)",
)

_pages: dict[tuple[str, int], object] = {}


def _page(pdf: str, number: int):
    key = (pdf, number)
    if key not in _pages:
        _pages[key] = load_page(os.path.join(ROOT, pdf), number)
    return _pages[key]


@pytest.mark.parametrize("sample", SAMPLES, ids=[s.name for s in SAMPLES])
def test_glyph_layer_matches_real_latex(sample):
    """Every fixed case must agree with its real LaTeX, token for token."""
    toks = glyph_tokens(_page(sample.pdf, sample.page), sample.bbox)
    diffs = diff(toks, latex_to_tokens(sample.latex))
    assert diffs == [], f"{sample.name}: {[d.explain() for d in diffs]}"


def _corrupt(latex: str) -> str:
    """Change one symbol's meaning without changing the equation's shape."""
    for a, b in (("0", "1"), ("1", "0"), ("2", "3"), ("u", "v"), ("v", "w"), ("x", "y")):
        if a in latex:
            return latex.replace(a, b, 1)
    raise AssertionError(f"cannot corrupt {latex!r}")


@pytest.mark.parametrize("sample", SAMPLES, ids=[s.name for s in SAMPLES])
def test_wrong_reading_is_still_caught(sample):
    """A one-glyph change to a matched sample must still be rejected."""
    corrupted = _corrupt(sample.latex)
    assert corrupted != sample.latex, sample.name
    toks = glyph_tokens(_page(sample.pdf, sample.page), sample.bbox)
    assert diff(toks, latex_to_tokens(corrupted)), f"{sample.name}: corruption slipped through"


@pytest.mark.parametrize("sample", KNOWN_MISMATCHES, ids=[s.name for s in KNOWN_MISMATCHES])
def test_ambiguous_geometry_stays_withheld(sample):
    """These must keep differing, so the pipeline withholds instead of guessing."""
    toks = glyph_tokens(_page(sample.pdf, sample.page), sample.bbox)
    assert diff(toks, latex_to_tokens(sample.latex)), (
        f"{sample.name}: geometry is no longer ambiguous -- move it into SAMPLES "
        f"and record why in eval/test_samples.py"
    )


def test_samples_are_glyph_backed():
    """Each sample region must actually contain glyphs (not a scan)."""
    for sample in SAMPLES + KNOWN_MISMATCHES:
        try:
            toks = glyph_tokens(_page(sample.pdf, sample.page), sample.bbox)
        except GlyphLayerUnavailable as exc:  # pragma: no cover - diagnostic
            pytest.fail(f"{sample.name}: {exc}")
        assert toks, sample.name


def test_printed_dots_match_either_ellipsis_spelling():
    """One printed dot run must match \\dots and \\cdots alike.

    lec_notes sets a single run of dot glyphs there; pdfLaTeX draws it the same
    way for both commands, so a reading that writes \\cdots must not be withheld.
    """
    toks = glyph_tokens(_page("eval/pdfs/lec_notes.pdf", 5), (204.37, 264.26, 351.05, 281.16))
    for spelling in (r"0 = x_0 < x_1 < \dots < x_n = 1,",
                     r"0 = x_0 < x_1 < \cdots < x_n = 1,"):
        assert diff(toks, latex_to_tokens(spelling)) == [], spelling
