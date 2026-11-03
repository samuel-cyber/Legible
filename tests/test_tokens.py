"""Token-semantics tests.

These are the guard rail for rule 3: any change to the token form in
tokens.py must keep every cosmetic LaTeX variant equal and keep every injected
error different, or these tests fail.
"""
from __future__ import annotations

import pytest

from equations.tokens import diff, latex_to_tokens
from tests.cases import CORRUPTIONS, COSMETIC, GOLD, GOLD_BY_ID


@pytest.mark.parametrize("eq_id,latex", COSMETIC)
def test_cosmetic_variants_are_equal(eq_id, latex):
    """A valid reformatting of the same equation must produce no differences."""
    gold = latex_to_tokens(GOLD_BY_ID[eq_id])
    variant = latex_to_tokens(latex)
    assert diff(gold, variant) == [], f"{eq_id}: {latex!r} should be cosmetic"


@pytest.mark.parametrize("eq_id,latex,kind", CORRUPTIONS)
def test_injected_errors_differ(eq_id, latex, kind):
    """Every injected error must change the token list (fail-closed)."""
    gold = latex_to_tokens(GOLD_BY_ID[eq_id])
    corrupt = latex_to_tokens(latex)
    diffs = diff(gold, corrupt)
    assert diffs, f"{eq_id} ({kind}): {latex!r} should differ from the gold"


def test_all_injected_errors_are_distinct_from_gold():
    """Belt and braces: the whole corruption set is caught in one pass."""
    caught = 0
    for eq_id, latex, _kind in CORRUPTIONS:
        if diff(latex_to_tokens(GOLD_BY_ID[eq_id]), latex_to_tokens(latex)):
            caught += 1
    assert caught == len(CORRUPTIONS)


def test_gold_is_reproducible():
    """Sanity: every gold equation parses to a non-empty token list."""
    for eq_id, latex in GOLD:
        assert latex_to_tokens(latex), f"{eq_id} produced no tokens"


def test_raw_subscript_order_is_canonical():
    """x_1^2 and x^2_1 must be the same equation (sub before sup rule)."""
    a = latex_to_tokens(r"x_1^2")
    b = latex_to_tokens(r"x^2_1")
    assert diff(a, b) == []


def test_centered_and_plain_dots_are_the_same_printed_run():
    """Between operators, \\dots and \\cdots are the same three dot glyphs.

    The glyph layer folds either run to one ellipsis and cannot tell them apart,
    so a transcription spelling the centered form as \\cdots must reduce to the
    same token as \\dots -- otherwise a correct reading is withheld.
    """
    assert diff(latex_to_tokens(r"a \dots b"), latex_to_tokens(r"a \cdots b")) == []


def test_ellipsis_inside_a_script_still_differs():
    """Raised vs centered dots inside a script are not folded together (guard)."""
    assert diff(latex_to_tokens(r"x_{\dots}"), latex_to_tokens(r"x_{\cdots}"))


def test_unknown_command_cannot_match():
    """An unknown command stays opaque, so it can never silently match glyphs."""
    a = latex_to_tokens(r"\mystery x")
    b = latex_to_tokens(r"x")
    assert diff(a, b)
