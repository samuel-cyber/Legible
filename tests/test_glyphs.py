"""Channel B (glyph-layer) tests against the real demo PDF.

These encode the two guarantees the README claims:
  - on the demo page, Channel B reconstructs all 6 equations so that they match
    their true LaTeX token-for-token, and
  - each of the 15 injected errors is caught (the glyph tokens differ from the
    corrupted reading).

If these fail after a change to glyphs.py or tokens.py, the change broke the
verifier and must not ship.
"""
from __future__ import annotations

import os

import pytest

from equations.glyphs import glyph_tokens
from equations.tokens import diff, latex_to_tokens
from ingest.pdf import find_display_equations, load_page
from tests.cases import CORRUPTIONS, GOLD, GOLD_BY_ID

PDF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "demo", "pages", "fluids.pdf")

pytestmark = pytest.mark.skipif(not os.path.exists(PDF), reason="demo PDF not built")


@pytest.fixture(scope="module")
def page():
    return load_page(PDF, 0)


@pytest.fixture(scope="module")
def glyphs_by_id(page):
    boxes = find_display_equations(page)
    assert len(boxes) == 6, f"expected 6 display equations, found {len(boxes)}"
    return {f"p1e{i + 1}": glyph_tokens(page, b) for i, b in enumerate(boxes)}


def test_three_channels_of_truth_available(page):
    """The demo page must have a glyph layer at all (born-digital)."""
    assert page.glyphs, "no glyphs extracted: the demo PDF is not born-digital"


@pytest.mark.parametrize("eq_id,latex", GOLD)
def test_channel_b_matches_true_latex(glyphs_by_id, eq_id, latex):
    """Channel B's glyph structure equals the true LaTeX token form exactly."""
    diffs = diff(glyphs_by_id[eq_id], latex_to_tokens(latex))
    assert diffs == [], [d.explain() for d in diffs]


@pytest.mark.parametrize("eq_id,latex,kind", CORRUPTIONS)
def test_channel_b_catches_injected_error(glyphs_by_id, eq_id, latex, kind):
    """Every injected error must show up as a disagreement with the glyphs."""
    diffs = diff(glyphs_by_id[eq_id], latex_to_tokens(latex))
    assert diffs, f"{eq_id} ({kind}): Channel B failed to catch {latex!r}"


def test_all_injected_errors_caught_by_channel_b(glyphs_by_id):
    caught = 0
    for eq_id, latex, _kind in CORRUPTIONS:
        if diff(glyphs_by_id[eq_id], latex_to_tokens(latex)):
            caught += 1
    assert caught == len(CORRUPTIONS), f"only {caught}/{len(CORRUPTIONS)} injected errors caught"
