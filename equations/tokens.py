"""Role-tagged token form shared by every evidence channel.

An equation becomes a flat list of tokens. Each token is (symbol, context),
where context is a tuple of structural roles from the outside in, e.g.

    v^2 inside a numerator  ->  ("v", ("num",)), ("2", ("num", "sup"))

Fractions are bracketed by FRAC / OVER / END marker tokens so a missing or
extra fraction shows up as a concrete difference. Because both the PDF glyph
layer (Channel B) and a LaTeX transcription (Channel A) are reduced to this
same form, cosmetic LaTeX differences (x_1 vs x_{1}, \\dfrac vs \\frac,
spacing commands) vanish, while meaningful ones (a dropped minus sign, a
wrong exponent, a swapped subscript) remain.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass

Token = tuple[str, tuple[str, ...]]

FRAC, OVER, END = "⟨frac", "⟨over", "⟨end"
MARKERS = {FRAC, OVER, END}

# ---------------------------------------------------------------- symbols --

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "θ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "varpi": "π", "rho": "ρ",
    "varrho": "ρ", "sigma": "σ", "varsigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ",
    "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ", "Pi": "Π",
    "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}

SYMBOLS = {
    "cdot": "·", "times": "×", "div": "÷", "pm": "±", "mp": "∓", "partial": "∂", "nabla": "∇",
    "infty": "∞", "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠",
    "approx": "≈", "propto": "∝", "sim": "∼", "equiv": "≡", "to": "→", "rightarrow": "→",
    "leftarrow": "←", "Rightarrow": "⇒", "sum": "∑", "int": "∫", "oint": "∮", "prod": "∏",
    "prime": "′", "circ": "∘", "degree": "°", "ell": "ℓ", "hbar": "ℏ", "cdots": "⋯",
    "ldots": "…", "dots": "…", "lbrace": "{", "rbrace": "}", "{": "{", "}": "}",
    "langle": "⟨", "rangle": "⟩", "vert": "|", "lvert": "|", "rvert": "|", "|": "∥", "%": "%",
    # --- relations, set theory and arrows seen in real lecture notes ---
    # (added so a LaTeX transcription tokenizes like the PDF glyph layer instead
    # of falling back to the opaque "unknown command" token and being withheld)
    "in": "∈", "notin": "∉", "ni": "∋", "subset": "⊂", "subseteq": "⊆", "subsetneq": "⊊",
    "supset": "⊃", "supseteq": "⊇", "sqsubseteq": "⊑", "mid": "|", "nmid": "∤",
    "lesssim": "≲", "gtrsim": "≳", "lessgtr": "≶", "gtrless": "≷", "simeq": "≃", "cong": "≅",
    "prec": "≺", "succ": "≻", "preceq": "⪯", "succeq": "⪰", "ll": "≪", "gg": "≫", "asymp": "≍",
    "parallel": "∥", "nparallel": "∦", "perp": "⊥", "angle": "∠", "vdash": "⊢", "dashv": "⊣",
    "forall": "∀", "exists": "∃", "nexists": "∄", "neg": "¬", "lnot": "¬",
    "wedge": "∧", "land": "∧", "vee": "∨", "lor": "∨", "cap": "∩", "cup": "∪",
    "setminus": "∖", "smallsetminus": "∖", "emptyset": "∅", "varnothing": "∅",
    "implies": "⇒", "impliedby": "⇐", "iff": "⇔", "Leftrightarrow": "⇔", "leftrightarrow": "↔",
    "Longrightarrow": "⇒", "Longleftarrow": "⇐", "Longleftrightarrow": "⇔",
    "longrightarrow": "⟶", "longleftarrow": "⟵", "longmapsto": "⟼",
    "Leftarrow": "⇐", "hookrightarrow": "↪", "hookleftarrow": "↩", "mapsto": "↦",
    "uparrow": "↑", "downarrow": "↓", "updownarrow": "↕", "Uparrow": "⇑", "Downarrow": "⇓",
    "ast": "∗", "star": "⋆", "bullet": "∙", "dagger": "†", "ddagger": "‡",
    "coprod": "∐", "bigcup": "⋃", "bigcap": "⋂", "bigoplus": "⨁", "bigotimes": "⨂",
    "colon": ":", ";": ";",
}
# NOTE: delimiter macros (\\binom, \\lfloor, \\rfloor, \\lceil, \\rceil, \\llbracket,
# ...) are deliberately left out: the hard-page test suite treats them as outside
# the token vocabulary, so a reading that uses one must stay withheld.

ACCENT_CMDS = {"dot": "˙", "ddot": "¨", "hat": "ˆ", "widehat": "ˆ", "bar": "¯", "overline": "¯",
               "tilde": "˜", "widetilde": "˜", "vec": "→"}
# \boxed / \fbox add only a drawn rectangle, which the glyph layer does not
# tokenize, so they are transparent (the same as a style command).
STYLE_CMDS = {"mathrm", "mathit", "mathbf", "mathsf", "mathtt", "mathcal", "mathbb", "boldsymbol",
              "bm", "text", "textrm", "textit", "operatorname", "mbox", "displaystyle", "textstyle",
              "boxed", "fbox"}
# Wrappers whose decorative label must be dropped but whose base is kept:
# \underbrace{base}_{label}, \overbrace{base}^{label}, \overset{label}{base}.
LABEL_CMDS = {"underbrace", "overbrace"}
FRAC_CMDS = {"frac", "dfrac", "tfrac", "cfrac"}
SKIP_CMDS = {",", ";", ":", "!", " ", "quad", "qquad", "left", "right", "big", "Big", "bigg", "Bigg",
             "bigl", "bigr", "Bigl", "Bigr", "biggl", "biggr", "limits", "nolimits", "\\"}

# Glyph-layer characters that differ from their LaTeX counterparts.
NORMALIZE = {
    "−": "-", "–": "-", "µ": "μ", "ϵ": "ε", "ϑ": "θ", "ϕ": "φ", "ϱ": "ρ", "ς": "σ", "ϖ": "π",
    "∗": "*", "′": "′", "ʹ": "′", "'": "′", "⃗": "→", "˙": "˙", "·": "·", "⋅": "·", "∙": "·",
    # A norm bar: the PDF may use ‖ (U+2016) where LaTeX \| produces ∥ (U+2225).
    "‖": "∥", "∣": "|",
    # Brackets that some embedded fonts encode as C0 control characters.
    "\x12": "(", "\x13": ")", "\x14": "[", "\x15": "]",
    # U+2126 OHM SIGN is a canonical equivalent of U+03A9 GREEK CAPITAL OMEGA.
    "\u2126": "\u03a9",
}
# A combining overlay is drawn as its own glyph beside the base it marks; the
# glyph layer folds the pair into one symbol (the slash of \ne turns a "=" into
# "≠"), which then matches the single symbol a transcription produces.
OVERLAYS = {"\u0338": {"=": "≠"}}
# Glyphs that attach to a base rather than occupying their own slot. U+2192 (→,
# a relation arrow such as \to) is deliberately NOT here: treating it as an
# accent moved it next to an unrelated glyph and broke every "A : V \to R".
ACCENT_GLYPHS = {"˙", "¨", "ˆ", "¯", "˜", "^", "~"}


def with_overlays(base: str, marks: list[str]) -> str:
    for m in marks:
        table = OVERLAYS.get(m)
        if table and base in table:
            base = table[base]
    return base


def norm(sym: str) -> str:
    return NORMALIZE.get(sym, sym)


# ------------------------------------------------------------ LaTeX parse --

class LatexParseError(ValueError):
    pass


class _Parser:
    """Small recursive-descent reader for the math subset used in lecture notes."""

    def __init__(self, src: str):
        self.s = src
        self.i = 0

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def skip_ws(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def command(self) -> str:
        assert self.peek() == "\\"
        self.i += 1
        start = self.i
        if self.i < len(self.s) and self.s[self.i].isalpha():
            while self.i < len(self.s) and self.s[self.i].isalpha():
                self.i += 1
        else:
            self.i += 1  # single-char command like \, \{ \\
        return self.s[start:self.i]

    def group_or_atom(self, ctx) -> list[Token]:
        """Read one argument: a {group} or a single atom."""
        self.skip_ws()
        c = self.peek()
        if c == "{":
            self.i += 1
            toks = self.expr(ctx, closer="}")
            if self.peek() != "}":
                raise LatexParseError("unclosed {")
            self.i += 1
            return toks
        if c == "":
            raise LatexParseError("missing argument")
        return self.atom(ctx)

    def atom(self, ctx) -> list[Token]:
        self.skip_ws()
        c = self.peek()
        if c == "\\":
            name = self.command()
            if name in FRAC_CMDS:
                num = self.group_or_atom(ctx + ("num",))
                den = self.group_or_atom(ctx + ("den",))
                return [(FRAC, ctx)] + num + [(OVER, ctx)] + den + [(END, ctx)]
            if name == "sqrt":
                self.skip_ws()
                if self.peek() == "[":  # optional index: \sqrt[3]{x}
                    j = self.s.index("]", self.i)
                    idx = self.s[self.i + 1:j]
                    self.i = j + 1
                    inner = self.group_or_atom(ctx)
                    return [(norm(ch), ctx + ("idx",)) for ch in idx if ch.strip()] + [("√", ctx)] + inner
                return [("√", ctx)] + self.group_or_atom(ctx)
            if name in ACCENT_CMDS:
                inner = self.group_or_atom(ctx)
                return inner + [(ACCENT_CMDS[name], ctx)]
            if name in STYLE_CMDS:
                if name in {"displaystyle", "textstyle"}:
                    return []
                return self.group_or_atom(ctx)
            if name in LABEL_CMDS:
                # \underbrace{base}_{label}: keep the base, and keep the label
                # text (it is visible in the PDF) but not as a true subscript.
                base = self.group_or_atom(ctx)
                self.skip_ws()
                label: list[Token] = []
                if self.peek() in "^_":
                    self.i += 1
                    label = self.group_or_atom(ctx)
                return base + label
            if name in SKIP_CMDS:
                return []
            if name in GREEK:
                return [(GREEK[name], ctx)]
            if name in SYMBOLS:
                return [(SYMBOLS[name], ctx)]
            if name in {"sin", "cos", "tan", "ln", "log", "exp", "max", "min", "lim", "det", "sec",
                        "csc", "cot", "sinh", "cosh", "tanh"}:
                return [(ch, ctx) for ch in name]
            # Unknown command: keep it as an opaque token so it can never
            # silently match the glyph layer (fail-closed).
            return [("\\" + name, ctx)]
        if c == "{":
            return self.group_or_atom(ctx)
        if c == "'":
            self.i += 1
            return [("′", ctx + ("sup",))]
        if c in "&~":
            self.i += 1
            return []
        self.i += 1
        return [(norm(c), ctx)]

    def expr(self, ctx, closer: str = "") -> list[Token]:
        out: list[Token] = []
        while True:
            self.skip_ws()
            c = self.peek()
            if c == "" or (closer and c == closer):
                return out
            if c == "}":
                raise LatexParseError("unexpected }")
            if c in "^_":
                self.i += 1
                role = "sup" if c == "^" else "sub"
                out += self.group_or_atom(ctx + (role,))
                continue
            out += self.atom(ctx)


def latex_to_tokens(latex: str) -> list[Token]:
    src = latex.strip()
    for wrap in ("$$", "\\[", "\\]", "$"):
        src = src.replace(wrap, "")
    p = _Parser(src)
    toks = p.expr(())
    if p.i < len(p.s):
        raise LatexParseError(f"trailing input at {p.i}")
    return _fold_cdots(_canonical(toks))


def _fold_dots(toks: list[Token]) -> list[Token]:
    """Collapse a run of >=3 base-level dots into a single ellipsis token.

    pdfLaTeX sets \\dots as three literal period glyphs, and (because it turns
    \\dots between operators into a centered ellipsis) \\cdots as three middot
    glyphs; a LaTeX transcription yields one Unicode glyph. The glyph layer
    cannot tell the two apart, so both runs fold to "…". Anything past the
    first three dots is kept, so a sentence-ending period right after an
    ellipsis becomes "…" + "." on both sides. Two dots (or any run with a
    non-base context) are left alone, so a genuine "a..b" difference is not
    hidden.
    """
    out: list[Token] = []
    i = 0
    n = len(toks)
    while i < n:
        c, ctx = toks[i]
        if c in (".", "·") and not ctx:
            j = i
            while j < n and toks[j] == (c, ctx):
                j += 1
            if j - i >= 3:
                out.append(("…", ctx))
                out.extend([toks[i]] * (j - i - 3))
                i = j
                continue
        out.append(toks[i])
        i += 1
    return out


def _fold_cdots(toks: list[Token]) -> list[Token]:
    """Unify a base-level centered ellipsis with the plain ellipsis token.

    pdfLaTeX sets both ``\\dots`` and ``\\cdots`` between operators as a run of
    dot glyphs, so the glyph layer folds either run to "…" (``_fold_dots``) and
    cannot tell the two apart. A LaTeX transcription, however, spells the centered
    form as ``\\cdots`` (U+22EF). The same printed dots must reduce to the same
    token on both sides, so a base-level U+22EF becomes "…" as well. Inside a
    script or fraction the two are genuinely set at different heights, so those
    are left alone and still differ (fail-closed).
    """
    return [("…", ctx) if (c == "⋯" and not ctx) else (c, ctx) for c, ctx in toks]


def _canonical(toks: list[Token]) -> list[Token]:
    """Ordering rule shared with the glyph layer: within a run of scripts that
    belong to the *same* base, subscripts come before superscripts (matches
    left-to-right glyph x order and makes x_1^2 and x^2_1 identical).

    A run is a maximal span of script tokens whose context has the same length
    (the same nesting depth of roles). That keeps sibling scripts of one base
    together while leaving a base such as L_{L^2(I)} — whose subscript itself
    contains a superscript — un-scrambled, since the inner scripts sit one role
    level deeper.
    """
    out = [t for t in toks if t[0] != ""]
    i = 0
    while i < len(out):
        t = out[i]
        if t[0] in MARKERS or not t[1] or t[1][-1] not in ("sub", "sup"):
            i += 1
            continue
        level = len(t[1])
        j = i
        while (j < len(out) and out[j][0] not in MARKERS and out[j][1]
               and out[j][1][-1] in ("sub", "sup") and len(out[j][1]) == level):
            j += 1
        if j - i > 1:
            seg = out[i:j]
            subs = [t for t in seg if t[1][-1] == "sub"]
            sups = [t for t in seg if t[1][-1] == "sup"]
            out[i:j] = subs + sups
        i = j
    return _fold_dots(out)


# ------------------------------------------------------------------ diff ---

ROLE_WORDS = {"num": "numerator", "den": "denominator", "sup": "superscript", "sub": "subscript",
              "idx": "root index"}


def describe(tok: Token) -> str:
    sym, ctx = tok
    shown = {FRAC: "a fraction", OVER: "a fraction bar", END: "the end of a fraction"}.get(sym, f"'{sym}'")
    if not ctx:
        return shown
    where = " in the ".join(ROLE_WORDS.get(r, r) for r in reversed(ctx))
    return f"{shown} (in the {where})"


@dataclass
class Difference:
    kind: str                      # "missing", "extra", "changed"
    glyph: list[Token]             # what the PDF itself contains
    reading: list[Token]           # what the transcription says

    def explain(self) -> str:
        g = ", ".join(describe(t) for t in self.glyph)
        r = ", ".join(describe(t) for t in self.reading)
        if self.kind == "missing":
            return f"The PDF has {g}, but the reading leaves it out."
        if self.kind == "extra":
            return f"The reading adds {r}, which is not in the PDF."
        return f"The PDF has {g}, but the reading has {r}."


def diff(glyph_tokens: list[Token], reading_tokens: list[Token]) -> list[Difference]:
    """Align the two token lists and return every disagreement."""
    sm = difflib.SequenceMatcher(a=glyph_tokens, b=reading_tokens, autojunk=False)
    out = []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            continue
        kind = {"delete": "missing", "insert": "extra", "replace": "changed"}[op]
        out.append(Difference(kind, glyph_tokens[a0:a1], reading_tokens[b0:b1]))
    return out


_SPOKEN = {"=": "equals", "+": "plus", "-": "minus", "×": "times", "·": "times", "/": "divided by",
           "(": "open bracket", ")": "close bracket", "˙": "dot", "¨": "double dot", "→": "vector",
           "≤": "less than or equal to", "≥": "greater than or equal to", "≈": "approximately equals"}


def spoken(toks: list[Token]) -> str:
    """Plain-language reading of the glyph-layer structure, used as the
    fallback for withheld equations (no model involved)."""
    words = []
    for sym, ctx in toks:
        if sym == FRAC:
            words.append("fraction,")
        elif sym == OVER:
            words.append("over")
        elif sym == END:
            words.append("end fraction,")
        else:
            w = _SPOKEN.get(sym, sym)
            if ctx and ctx[-1] == "sup":
                w = f"superscript {w}"
            elif ctx and ctx[-1] == "sub":
                w = f"sub {w}"
            words.append(w)
    return " ".join(words).replace(" ,", ",").strip(" ,")


def to_text(toks: list[Token]) -> str:
    """Compact human-readable form, handy in reports and logs."""
    parts = []
    for sym, ctx in toks:
        if sym == FRAC:
            parts.append("(")
        elif sym == OVER:
            parts.append(")/(")
        elif sym == END:
            parts.append(")")
        elif ctx and ctx[-1] == "sup":
            parts.append("^" + sym)
        elif ctx and ctx[-1] == "sub":
            parts.append("_" + sym)
        else:
            parts.append(sym)
    return " ".join(parts)
