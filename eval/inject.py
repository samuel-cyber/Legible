"""Generate corrupted LaTeX from gold equations, for the evaluation.

Each corruption is a small, realistic mis-reading of the kind a vision model
makes: a flipped sign, a wrong exponent, a changed digit, swapped subscripts, a
dropped term, a swapped Greek letter, a dropped accent, an inverted fraction.

Every corruption is asserted to actually change the token list, so the runner
can never count a "corruption" that the verifier is right to accept.
"""
from __future__ import annotations

import os
import random
import re
import sys
from dataclasses import dataclass

# Let `py eval/inject.py` find the repo modules.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from equations.tokens import diff, latex_to_tokens  # noqa: E402


@dataclass
class Corruption:
    id: str
    gold_id: str
    gold_latex: str
    read_latex: str        # what the (simulated) model "read"
    kind: str


# A pool of Greek/symbol swaps that are visually confusable in a low-res crop.
GREEK_SWAPS = [("\\mu", "\\nu"), ("\\rho", "p"), ("\\rho", "\\sigma"),
               ("\\nu", "\\mu"), ("\\theta", "\\phi"), ("\\eta", "\\theta")]


def _sign_flip(latex: str):
    """Flip the sign of one top-level +/- that is not a leading unary at index 0."""
    # Prefer a '-' (drop it) then a '+' (turn into '-').
    for i in range(1, len(latex)):
        if latex[i] == "-" and latex[i - 1] not in "^{":
            return latex[:i] + " " + latex[i + 1:], "sign flip"
    m = re.search(r"(?<![\^ ])\+", latex)
    if m:
        return latex[:m.start()] + "-" + latex[m.end():], "sign flip"
    return None, None


def _exponent(latex: str):
    m = re.search(r"\^\{?(\d+)\}?", latex)
    if not m:
        return None, None
    d = int(m.group(1))
    new = str(d + 1 if d != 2 else 3)
    return latex[:m.start(1)] + new + latex[m.end(1):], "exponent"


def _digit(latex: str):
    """Change one digit, preferring a subscript digit (e.g. A_2 -> A_3)."""
    m = re.search(r"_\s*(\{?\d)", latex) or re.search(r"(\d)", latex)
    if not m:
        return None, None
    d = int(m.group(1)[-1])
    new = str(d + 1 if d != 9 else d - 1)
    return latex[:m.end(1) - 1] + new + latex[m.end(1):], "digit"


def _swap_subscripts(latex: str):
    """Swap the letters of the first two subscripts, e.g. A_1 v_1 = A_2 v_2.

    The subscript value may be brace-wrapped (_{1}) or bare (_1); both are
    handled by operating on the captured value only.
    """
    matches = list(re.finditer(r"_\s*(\{[^{}]*\}|[A-Za-z0-9])", latex))
    if len(matches) < 2:
        return None, None

    def value(m):
        v = m.group(1)
        return v[1:-1] if v.startswith("{") else v

    # Find the first two subscripts whose values differ, so e.g.
    # A_1 v_1 = A_2 v_2 (whose first two are both "1") still yields a swap.
    pair = None
    for i in range(len(matches)):
        for j in range(i + 1, len(matches)):
            if value(matches[i]) != value(matches[j]):
                pair = (matches[i], matches[j])
                break
        if pair:
            break
    if not pair:
        return None, None

    (m0, m1) = pair
    a, b = value(m0), value(m1)
    # Rebuild right-to-left so earlier indices stay valid.
    out = latex
    for m, new in ((m1, a), (m0, b)):
        out = out[:m.start(1)] + new + out[m.end(1):]
    return out, "swapped subscript"


def _drop_term(latex: str):
    """Remove one additive term, e.g. '+ z' or '+ \\rho g h'."""
    tokens = re.split(r"(\s[+-]\s)", latex)
    # tokens like [t0, ' + ', t1, ' - ', t2, ...]
    if len(tokens) < 3:
        return None, None
    del tokens[1:3]           # drop the first operator and the term after it
    return "".join(tokens), "dropped term"


def _greek_swap(latex: str):
    for a, b in GREEK_SWAPS:
        if a in latex:
            return latex.replace(a, b, 1), "greek swap"
    return None, None


def _drop_accent(latex: str):
    m = re.search(r"\\dot\{([^{}]+)\}", latex)
    if not m:
        m2 = re.search(r"\\dot\s+([A-Za-z])", latex)
        if not m2:
            return None, None
        return latex[:m2.start()] + m2.group(1) + latex[m2.end():], "dropped accent"
    return latex[:m.start()] + m.group(1) + latex[m.end():], "dropped accent"


def _invert_fraction(latex: str):
    m = re.search(r"\\[dt]?frac\{([^{}]+)\}\{([^{}]+)\}", latex)
    if not m:
        return None, None
    return latex[:m.start()] + f"\\frac{{{m.group(2)}}}{{{m.group(1)}}}" + latex[m.end():], "inverted fraction"


STRATEGIES = [
    _sign_flip, _exponent, _digit, _swap_subscripts,
    _drop_term, _greek_swap, _drop_accent, _invert_fraction,
]


def make_corruptions(gold_latex: str) -> list[tuple[str, str]]:
    """Return (read_latex, kind) pairs that actually change the token list."""
    gold_tokens = latex_to_tokens(gold_latex)
    seen = {gold_latex}
    out: list[tuple[str, str]] = []
    for fn in STRATEGIES:
        read, kind = fn(gold_latex)
        if read is None or read in seen:
            continue
        try:
            toks = latex_to_tokens(read)
        except Exception:
            continue
        # Fail-closed guarantee: a corruption MUST differ from gold.
        if not diff(gold_tokens, toks):
            continue
        seen.add(read)
        out.append((read, kind))
    return out


def build_corpus(equations, per_equation: int | None = None, seed: int = 7) -> list[Corruption]:
    """Turn a list of gold equation dicts into a corruption corpus."""
    rng = random.Random(seed)
    corpus: list[Corruption] = []
    for eq in equations:
        pairs = make_corruptions(eq["latex"])
        if per_equation is not None and len(pairs) > per_equation:
            pairs = rng.sample(pairs, per_equation)
        for i, (read, kind) in enumerate(pairs):
            corpus.append(Corruption(
                id=f"{eq['id']}-c{i + 1}", gold_id=eq["id"], gold_latex=eq["latex"],
                read_latex=read, kind=kind,
            ))
    return corpus


if __name__ == "__main__":
    import json

    with open(os.path.join(ROOT, "eval", "gold.json"), encoding="utf-8") as f:
        gold = json.load(f)["equations"]
    corpus = build_corpus(gold)
    for c in corpus:
        print(f"{c.id:10s} {c.kind:18s} {c.read_latex}")
    print(f"\n{len(corpus)} corruptions from {len(gold)} gold equations")
