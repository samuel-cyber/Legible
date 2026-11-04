"""Feature: "Ask about this equation" -- structure only, no AI.

Every answer here is derived purely from ``equations.tokens.latex_to_tokens``
applied to the equation's own published LaTeX: the exact string that was
independently verified against the source (status "verified" or "repaired").
There is no model call anywhere in this module, and there never will be --
that is the entire point of the feature. A question that cannot be parsed,
or one asked of an equation whose structure was not independently verified,
gets the same fixed refusal.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from equations.tokens import END, FRAC, OVER, Token, latex_to_tokens, spoken, to_text

REFUSAL = "I can only answer questions about this equation's structure."
NOT_AVAILABLE = (
    "This equation's structure was not independently verified against the "
    "source, so I can't answer questions about it."
)


@dataclass
class Answer:
    text: str
    parts: list[str] | None = None   # set only for "read it slowly"


# ------------------------------------------------------------- fractions ---

def _fractions(tokens: list[Token]) -> list[tuple[list[Token], list[Token]]]:
    """Top-level (FRAC, num..., OVER, den..., END) blocks, in reading order.

    A fraction nested inside another's numerator/denominator is not split
    out separately here -- it stays part of that numerator's/denominator's
    own token list, exactly as it is nested in the equation itself.
    """
    out: list[tuple[list[Token], list[Token]]] = []
    i, n = 0, len(tokens)
    while i < n:
        sym, _ = tokens[i]
        if sym != FRAC:
            i += 1
            continue
        depth = 1
        over_idx = None
        j = i + 1
        while j < n and depth > 0:
            s2, _ = tokens[j]
            if s2 == FRAC:
                depth += 1
            elif s2 == END:
                depth -= 1
                if depth == 0:
                    break
            elif s2 == OVER and depth == 1 and over_idx is None:
                over_idx = j
            j += 1
        if over_idx is None:
            break  # malformed; stop rather than guess
        out.append((tokens[i + 1:over_idx], tokens[over_idx + 1:j]))
        i = j + 1
    return out


def _list_fractions(tokens: list[Token], part: str) -> str:
    fracs = _fractions(tokens)
    if not fracs:
        return "There's no fraction in this equation."
    idx = 0 if part == "numerator" else 1
    if len(fracs) == 1:
        return f"The {part} is: {to_text(fracs[0][idx])}"
    lines = [f"Fraction {i + 1}: {to_text(f[idx])}." for i, f in enumerate(fracs)]
    return f"This equation has {len(fracs)} fractions. " + " ".join(lines)


# --------------------------------------------------------- sub/superscript -

_TARGET_RE = re.compile(r"^(.+?)[_^]\{?([0-9A-Za-z]+)\}?$")


def _parse_target(raw: str) -> tuple[str, str | None]:
    """Split a user-typed symbol like 'A_1' into (base, disambiguator), so
    asking about a symbol that already has a subscript finds the right one
    of several occurrences of the same base (A_1 vs A_2)."""
    m = _TARGET_RE.match(raw)
    if m:
        return m.group(1), m.group(2)
    return raw, None


def _occurrences(tokens: list[Token], sym: str) -> list[int]:
    return [i for i, (s, ctx) in enumerate(tokens) if s == sym and not (ctx and ctx[-1] in ("sup", "sub"))]


def _run_at(tokens: list[Token], i: int, role: str) -> list[Token]:
    target = tokens[i][1] + (role,)
    run, j = [], i + 1
    while j < len(tokens) and tokens[j][1] == target:
        run.append(tokens[j])
        j += 1
    return run


def _find_occurrence(tokens: list[Token], base: str, disambiguator: str | None) -> int | None:
    occ = _occurrences(tokens, base)
    if not occ:
        return None
    if disambiguator is None or len(occ) == 1:
        return occ[0]
    for i in occ:
        run_symbols = "".join(s for s, _ in _run_at(tokens, i, "sub"))
        if run_symbols == disambiguator:
            return i
    return occ[0]


def _script_answer(tokens: list[Token], raw_sym: str, role: str) -> str:
    word = "exponent" if role == "sup" else "subscript"
    article = "an" if word == "exponent" else "a"
    base, disambiguator = _parse_target(raw_sym)
    idx = _find_occurrence(tokens, base, disambiguator)
    if idx is None:
        return f"'{raw_sym}' doesn't appear in this equation."
    run = _run_at(tokens, idx, role)
    if not run:
        return f"'{raw_sym}' doesn't have {article} {word} here."
    return f"The {word} of '{raw_sym}' is: {to_text(run)}"


# -------------------------------------------------------------- brackets ---

def _bracket_pairs(tokens: list[Token]) -> list[tuple[int, int]]:
    """(open_index, close_index) for every "(" ... ")" pair, by position."""
    stack: list[int] = []
    pairs: list[tuple[int, int]] = []
    for i, (s, _) in enumerate(tokens):
        if s == "(":
            stack.append(i)
        elif s == ")" and stack:
            pairs.append((stack.pop(), i))
    return sorted(pairs)


def _inside_brackets(tokens: list[Token]) -> str:
    pairs = _bracket_pairs(tokens)
    if not pairs:
        return "There are no brackets in this equation."
    top_level = [p for p in pairs if not any(o < p[0] and p[1] < c for o, c in pairs if (o, c) != p)]
    if len(top_level) == 1:
        o, c = top_level[0]
        return f"Inside the brackets: {to_text(tokens[o + 1:c])}"
    lines = [f"Bracket {i + 1}: {to_text(tokens[o + 1:c])}" for i, (o, c) in enumerate(top_level)]
    return f"This equation has {len(top_level)} bracketed groups. " + " ".join(lines)


def _bracket_closes_after(tokens: list[Token], raw_sym: str) -> str:
    base, disambiguator = _parse_target(raw_sym)
    idx = _find_occurrence(tokens, base, disambiguator)
    if idx is None:
        return f"'{raw_sym}' doesn't appear in this equation."
    # The occurrence itself may have a sub/sup run (e.g. v_1's "1"); the
    # bracket must close after all of it, not just the base glyph "v".
    end = idx
    for role in ("sub", "sup"):
        run = _run_at(tokens, idx, role)
        if run:
            end = max(end, idx + len(run))
    pairs = _bracket_pairs(tokens)
    after = sorted((o, c) for o, c in pairs if c > end)
    if not after:
        return f"No bracket closes after '{raw_sym}'."
    o, c = after[0]
    opener = to_text(tokens[o + 1:o + 2]) if o + 1 < len(tokens) else ""
    return f"The bracket that opened before '{opener}' closes right after '{raw_sym}'."


# -------------------------------------------------------------- glossary ---

def _glossary_answer(glossary: list[tuple[str, str]], sym: str) -> str:
    for g_sym, meaning in glossary or []:
        if g_sym.strip().lower() == sym.strip().lower():
            return f"'{sym}' is {meaning}"
    return "The notes don't say."


# ------------------------------------------------------------------ parse --

_PATTERNS = [
    (re.compile(r"\bnumerator\b"), "numerator"),
    (re.compile(r"\bdenominator\b"), "denominator"),
    (re.compile(r"\bexponent\b.*?\bof\b\s+([A-Za-z0-9\\{}_^']+)", re.I), "exponent"),
    (re.compile(r"\bsubscript\b.*?\bof\b\s+([A-Za-z0-9\\{}_^']+)", re.I), "subscript"),
    (re.compile(r"\bwhich\s+bracket\b.*?\bafter\b\s+([A-Za-z0-9\\{}_^']+)", re.I), "bracket_after"),
    (re.compile(r"\bclos(?:es|e)\s+after\b\s+([A-Za-z0-9\\{}_^']+)", re.I), "bracket_after"),
    (re.compile(r"\binside\b.*?\bbracket", re.I), "brackets"),
    (re.compile(r"\bread\b.*?\bslow", re.I), "slowly"),
    (re.compile(r"\bwhat\s+does\b\s+([A-Za-z0-9\\{}_^']+)\s+mean\b", re.I), "glossary"),
    (re.compile(r"\bmeaning\s+of\b\s+([A-Za-z0-9\\{}_^']+)", re.I), "glossary"),
]


def _strip_punct(s: str) -> str:
    return s.strip().strip("?.,!'\"")


def ask(latex: str, question: str, glossary: list[tuple[str, str]] = ()) -> Answer:
    """Answer ``question`` from ``latex``'s own token structure. Never calls
    a model. ``latex`` must be the published reading of a verified or
    repaired equation -- callers must not use this on a withheld or
    ai_read equation (see NOT_AVAILABLE)."""
    try:
        tokens = latex_to_tokens(latex)
    except Exception:
        return Answer(REFUSAL)

    q = (question or "").strip()
    if not q:
        return Answer(REFUSAL)

    for pattern, kind in _PATTERNS:
        m = pattern.search(q)
        if not m:
            continue
        if kind in ("numerator", "denominator"):
            return Answer(_list_fractions(tokens, kind))
        if kind == "exponent":
            return Answer(_script_answer(tokens, _strip_punct(m.group(1)), "sup"))
        if kind == "subscript":
            return Answer(_script_answer(tokens, _strip_punct(m.group(1)), "sub"))
        if kind == "brackets":
            return Answer(_inside_brackets(tokens))
        if kind == "bracket_after":
            return Answer(_bracket_closes_after(tokens, _strip_punct(m.group(1))))
        if kind == "slowly":
            parts = _spoken_parts(tokens)
            return Answer("Reading it slowly, one part at a time.", parts=parts)
        if kind == "glossary":
            return Answer(_glossary_answer(list(glossary), _strip_punct(m.group(1))))

    return Answer(REFUSAL)


# ------------------------------------------------------- precomputed facts

def _display_name(tokens: list[Token], i: int) -> str:
    """How a human would refer to this occurrence: 'A_1' if it already has
    a subscript, otherwise just the bare symbol."""
    sub = _run_at(tokens, i, "sub")
    if sub:
        return f"{tokens[i][0]}_{''.join(s for s, _ in sub)}"
    return tokens[i][0]


def extract_facts(latex: str, glossary: list[tuple[str, str]] = ()) -> dict:
    """Precomputed, JSON-able structural facts for one verified/repaired
    equation, for the standalone student page's client-side "ask" control
    (the generated page has no server to call back into).

    Every value here is produced by the exact same helpers ``ask()`` itself
    uses, so the two can never disagree -- this is not a second
    implementation of the structure walk, just its results written out.
    """
    try:
        tokens = latex_to_tokens(latex)
    except Exception:
        return {"ok": False}

    fractions = [{"num": to_text(n), "den": to_text(d)} for n, d in _fractions(tokens)]

    pairs = _bracket_pairs(tokens)
    top_level = [p for p in pairs if not any(o < p[0] and p[1] < c for o, c in pairs if (o, c) != p)]
    brackets = [to_text(tokens[o + 1:c]) for o, c in top_level]

    scripts: dict[str, dict] = {}
    bracket_after: dict[str, str] = {}
    for i, (sym, ctx) in enumerate(tokens):
        if ctx and ctx[-1] in ("sup", "sub"):
            continue
        if not sym.isalnum():
            continue  # skip operators/brackets/relations; only symbols are "askable"
        name = _display_name(tokens, i)
        if name in scripts:
            continue  # first occurrence wins, same as ask()'s own lookup
        entry = {}
        sup, sub = _run_at(tokens, i, "sup"), _run_at(tokens, i, "sub")
        if sup:
            entry["sup"] = to_text(sup).lstrip("^")
        if sub:
            entry["sub"] = to_text(sub).lstrip("_")
        scripts[name] = entry
        bracket_after[name] = _bracket_closes_after(tokens, name)

    return {
        "ok": True,
        "fractions": fractions,
        "brackets": brackets,
        "scripts": scripts,
        "bracket_after": bracket_after,
        "spoken_parts": _spoken_parts(tokens),
        "glossary": {s.strip().lower(): m for s, m in (glossary or [])},
    }


def _spoken_parts(tokens: list[Token]) -> list[str]:
    """``spoken()``'s own per-token wording (not a re-derivation), split
    into one short chunk per token instead of one long sentence, for "read
    it slowly". Splitting on token boundaries (rather than on spoken()'s
    joined-string punctuation) works the same way whether or not the
    equation has a fraction to create a natural pause at."""
    from equations.tokens import _SPOKEN  # same word choices as spoken()

    parts: list[str] = []
    for sym, ctx in tokens:
        if sym == FRAC:
            parts.append("fraction")
        elif sym == OVER:
            parts.append("over")
        elif sym == END:
            parts.append("end fraction")
        else:
            w = _SPOKEN.get(sym, sym)
            if ctx and ctx[-1] == "sup":
                w = f"superscript {w}"
            elif ctx and ctx[-1] == "sub":
                w = f"sub {w}"
            parts.append(w)
    return parts or [spoken(tokens)]
