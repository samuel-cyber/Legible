"""Feature: "Ask about this equation" -- structure only, no AI.

Every question type from the brief, exercised on the demo page's own
equations (tests/cases.py GOLD), so these tests pin real structure, not
synthetic toy equations. No network, no model: equations.ask never imports
clients.meta.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from equations.ask import REFUSAL, ask, extract_facts
from tests.cases import GOLD_BY_ID

P1E1 = GOLD_BY_ID["p1e1"]   # \frac{p}{\rho g} + \frac{v^2}{2g} + z = H
P1E3 = GOLD_BY_ID["p1e3"]   # A_1 v_1 = A_2 v_2
P1E4 = GOLD_BY_ID["p1e4"]   # h_f = f \frac{L}{D} \frac{v^2}{2g}
P1E6 = GOLD_BY_ID["p1e6"]   # F_x = -\dot{m}(v_2 - v_1)


def test_no_model_import():
    """The entire point of this feature: it never touches the network."""
    import equations.ask as ask_mod
    assert "meta" not in ask_mod.__dict__ and "clients" not in dir(ask_mod)


# ------------------------------------------------------------- numerator ---

def test_numerator_single_fraction():
    a = ask(P1E4, "What's in the numerator?")
    assert "fractions" in a.text.lower()
    assert "L" in a.text and "v" in a.text


def test_numerator_lists_each_fraction_in_order():
    a = ask(P1E1, "What's in the numerator?")
    assert "Fraction 1: p." in a.text
    assert "Fraction 2:" in a.text and "v" in a.text


def test_denominator_lists_each_fraction_in_order():
    a = ask(P1E1, "What's in the denominator?")
    assert "rho" in a.text.lower() or "ρ" in a.text  # \rho -> ρ
    assert "2 g" in a.text


def test_numerator_no_fraction_present():
    a = ask(P1E3, "What's in the numerator?")
    assert "no fraction" in a.text.lower()


# --------------------------------------------------- exponent / subscript -

def test_exponent_of_symbol():
    a = ask(P1E1, "What's the exponent of v?")
    assert "2" in a.text


def test_exponent_missing_is_explicit():
    a = ask(P1E3, "What's the exponent of v?")
    assert "doesn't have an exponent" in a.text


def test_symbol_entirely_absent():
    a = ask(P1E3, "What's the exponent of Q?")
    assert "doesn't appear" in a.text


def test_subscript_disambiguates_between_two_occurrences():
    a1 = ask(P1E3, "What's the subscript of A_1?")
    a2 = ask(P1E3, "What's the subscript of A_2?")
    assert "1" in a1.text and "2" not in a1.text.split(":")[-1]
    assert "2" in a2.text


# ------------------------------------------------------------- brackets ---

def test_inside_brackets():
    a = ask(P1E6, "What's inside the brackets?")
    assert "v" in a.text and "-" in a.text


def test_no_brackets_present():
    a = ask(P1E1, "What's inside the brackets?")
    assert "no brackets" in a.text.lower()


def test_which_bracket_closes_after():
    a = ask(P1E6, "Which bracket closes after v_1?")
    assert "closes right after 'v_1'" in a.text


def test_bracket_question_symbol_not_present():
    a = ask(P1E6, "Which bracket closes after Q?")
    assert "doesn't appear" in a.text


# -------------------------------------------------------------- read slowly

def test_read_it_slowly_returns_ordered_parts():
    a = ask(P1E6, "Read it slowly")
    assert a.parts is not None
    assert len(a.parts) > 1
    assert "F" in a.parts[0]


def test_read_it_slowly_uses_the_same_words_as_spoken():
    from equations.tokens import latex_to_tokens, spoken
    a = ask(P1E3, "Read it slowly")
    full = spoken(latex_to_tokens(P1E3))
    assert " ".join(a.parts) == full.replace(",", "")


def test_read_it_slowly_one_part_per_token_even_without_a_fraction():
    """A fraction-free equation must still split into multiple parts."""
    a = ask(P1E6, "Read it slowly")
    assert len(a.parts) > 4


# ---------------------------------------------------------------- glossary

def test_glossary_hit():
    a = ask(P1E1, "What does z mean?", glossary=[("z", "the elevation head")])
    assert a.text == "'z' is the elevation head"


def test_glossary_miss_says_notes_dont_say():
    a = ask(P1E1, "What does z mean?", glossary=[])
    assert a.text == "The notes don't say."


def test_glossary_case_insensitive_symbol_match():
    a = ask(P1E1, "What does Z mean?", glossary=[("z", "the elevation head")])
    assert "elevation head" in a.text


# ------------------------------------------------------------ unanswerable

def test_unrelated_question_gets_fixed_refusal():
    a = ask(P1E1, "What's the weather like today?")
    assert a.text == REFUSAL


def test_empty_question_gets_fixed_refusal():
    a = ask(P1E1, "")
    assert a.text == REFUSAL


def test_invalid_latex_gets_fixed_refusal_not_a_crash():
    a = ask(r"\frac{1}{2", "What's in the numerator?")
    assert a.text == REFUSAL


# ---------------------------------------------- extract_facts (client-side)

def test_extract_facts_fractions_in_order():
    facts = extract_facts(P1E1)
    assert facts["ok"] is True
    assert [f["num"] for f in facts["fractions"]] == ["p", "v ^2"]
    assert [f["den"] for f in facts["fractions"]] == ["ρ g", "2 g"]


def test_extract_facts_scripts_disambiguate_by_display_name():
    facts = extract_facts(P1E3)
    assert facts["scripts"]["A_1"]["sub"] == "1"
    assert facts["scripts"]["A_2"]["sub"] == "2"
    assert facts["scripts"]["v_1"]["sub"] == "1"


def test_extract_facts_brackets_and_spoken_parts():
    facts = extract_facts(P1E6)
    assert facts["brackets"] == ["v _2 - v _1"]
    assert facts["spoken_parts"][0] == "F"
    assert len(facts["spoken_parts"]) > 4


def test_extract_facts_glossary_is_lowercased_for_lookup():
    facts = extract_facts(P1E1, glossary=[("z", "the elevation head")])
    assert facts["glossary"]["z"] == "the elevation head"


def test_extract_facts_invalid_latex_is_not_ok():
    assert extract_facts(r"\frac{1}{2")["ok"] is False


def test_extract_facts_agrees_with_ask_on_exponent():
    """The JSON facts and ask()'s own text must describe the same thing."""
    facts = extract_facts(P1E1)
    a = ask(P1E1, "What's the exponent of v?")
    assert facts["scripts"]["v"]["sup"] in a.text
