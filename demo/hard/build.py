"""Build a harder demo page *without* a LaTeX toolchain.

Channel B (equations/glyphs.py) works purely on geometry: baselines, glyph
sizes and horizontal rules. So a page that reproduces those numbers exercises
exactly the same code as a compiled one. We typeset a small math subset by
placing glyphs and rules with PyMuPDF, using a real font embedded with the
Unicode codepoints preserved.

The font is a renamed copy of DejaVu Sans whose family is set to "CambriaMath",
one of the prefixes ingest/pdf.py recognises as a math font, so the page is
also discoverable by the pipeline's own equation finder
(find_display_equations) and is a drop-in for:

    py pipeline.py demo/hard/hard.pdf out/hard --replay demo/hard/replay.json

Nothing here calls a model. Rebuild with:

    py demo/hard/build.py
"""
from __future__ import annotations

import json
import os
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

HARD_PDF = os.path.join(HERE, "hard.pdf")
MATH_FONT = os.path.join(HERE, "_cambriamath.ttf")

BASE = 10.0          # body / math size, matches the demo (10pt)
SCRIPT = 0.7         # script ratio, matches LaTeX's 7pt-in-10pt
GAP = 0.16           # inter-item spacing, in em


# ------------------------------------------------------------------ font ---

def ensure_math_font(dest: str = MATH_FONT) -> str:
    """A copy of a Unicode math-capable font whose family starts with a
    MATH_FONT_PREFIXES entry, so the pipeline's finder can see it."""
    if os.path.exists(dest):
        return dest
    import matplotlib
    from fontTools.ttLib import TTFont

    src = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans.ttf")
    font = TTFont(src)
    for rec in font["name"].names:
        if rec.nameID in (1, 4, 6, 16, 17):
            rec.string = "CambriaMath"
        elif rec.nameID == 2:
            rec.string = "Regular"
    font.save(dest)
    return dest


# ---------------------------------------------------------------- canvas ---

class Canvas:
    """Places glyphs and rules, and records the extent of each equation.

    push()/pop() isolate a sub-region so, for example, the radical can measure
    just its radicand and draw the vinculum above everything in it.
    """

    def __init__(self, page: pymupdf.Page, fontfile: str):
        self.page = page
        self.font = pymupdf.Font(fontfile=fontfile)
        page.insert_font(fontname="MATH", fontfile=fontfile)
        self._box: list[float] | None = None
        self._stack: list[list[float]] = []

    def begin(self):
        self._box = [1e9, 1e9, -1e9, -1e9]

    def end(self) -> tuple[float, float, float, float]:
        b = tuple(self._box)
        self._box = None
        return b

    def push(self):
        self._stack.append(self._box)
        self._box = [1e9, 1e9, -1e9, -1e9]

    def pop(self) -> tuple[float, float, float, float]:
        b = tuple(self._box)
        self._box = self._stack.pop()
        self._touch(*b)
        return b

    def _touch(self, x0, y0, x1, y1):
        if self._box is None:
            return
        self._box[0] = min(self._box[0], x0)
        self._box[1] = min(self._box[1], y0)
        self._box[2] = max(self._box[2], x1)
        self._box[3] = max(self._box[3], y1)

    def width(self, text: str, size: float) -> float:
        return self.font.text_length(text, fontsize=size)

    def run(self, x: float, y: float, text: str, size: float = BASE) -> float:
        self.page.insert_text((x, y), text, fontname="MATH", fontsize=size, color=(0, 0, 0))
        w = self.width(text, size)
        self._touch(x, y - 0.82 * size, x + w, y + 0.24 * size)
        return w

    def rule(self, x0: float, x1: float, y: float, width: float = 0.6):
        self.page.draw_line(pymupdf.Point(x0, y), pymupdf.Point(x1, y), color=(0, 0, 0), width=width)
        self._touch(x0, y - 1.0, x1, y + 1.0)

    def text(self, x: float, y: float, s: str, size: float = 11.0):
        self.page.insert_text((x, y), s, fontname="MATH", fontsize=size, color=(0, 0, 0))


# --------------------------------------------------------------- nodes ---

def R(t):            return ("r", t)
def SEQ(*items):     return ("seq", list(items))
def FRAC(n, d):      return ("frac", n, d)
def BIG(op, sub, sup): return ("big", op, sub, sup)
def SQRT(inner):     return ("sqrt", inner)
def DOT(base):       return ("dot", base)
def STACK(top, bot): return ("stack", top, bot)


def SCR(base, sub=None, sup=None):
    if sub is not None and sup is not None:
        return ("subsup", base, sub, sup)
    if sub is not None:
        return ("sub", base, sub)
    return ("sup", base, sup)


def width_of(node, size: float, cv: Canvas) -> float:
    kind = node[0]
    if kind == "r":
        return cv.width(node[1], size)
    if kind == "seq":
        items = node[1]
        if not items:
            return 0.0
        total = sum(width_of(c, size, cv) for c in items)
        return total + GAP * size * (len(items) - 1)
    if kind == "frac":
        return max(width_of(node[1], size, cv), width_of(node[2], size, cv))
    if kind in ("sub", "sup"):
        base, script = node[1], node[2]
        return width_of(base, size, cv) + width_of(script, size * SCRIPT, cv) + 0.05 * size
    if kind == "subsup":
        base = node[1]
        s = width_of(node[2], size * SCRIPT, cv) + width_of(node[3], size * SCRIPT, cv)
        return width_of(base, size, cv) + s + 0.05 * size
    if kind == "big":
        w = width_of(node[1], size, cv)
        if node[2] is not None:
            w += width_of(node[2], size * SCRIPT, cv) + 0.05 * size
        if node[3] is not None:
            w += width_of(node[3], size * SCRIPT, cv) + 0.05 * size
        return w
    if kind == "sqrt":
        return cv.width("\u221a", size) + 0.1 * size + width_of(node[1], size, cv)
    if kind == "dot":
        return width_of(node[1], size, cv)
    if kind == "stack":
        return max(width_of(node[1], size, cv), width_of(node[2], size, cv))
    raise ValueError(f"unknown node {kind!r}")


def render(node, x: float, y: float, size: float, cv: Canvas) -> float:
    kind = node[0]
    if kind == "r":
        return cv.run(x, y, node[1], size)
    if kind == "seq":
        cx = x
        for i, child in enumerate(node[1]):
            w = render(child, cx, y, size, cv)
            cx += w + (GAP * size if i + 1 < len(node[1]) else 0)
        return cx - x
    if kind == "frac":
        wn = width_of(node[1], size, cv)
        wd = width_of(node[2], size, cv)
        w = max(wn, wd)
        render(node[1], x + (w - wn) / 2, y - 0.9 * size, size, cv)
        cv.rule(x, x + w, y - 0.35 * size)
        render(node[2], x + (w - wd) / 2, y + 0.55 * size, size, cv)
        return w
    if kind in ("sub", "sup"):
        base, script = node[1], node[2]
        wb = width_of(base, size, cv)
        render(base, x, y, size, cv)
        sx = x + wb + 0.05 * size
        sy = y - 0.45 * size if kind == "sup" else y + 0.30 * size
        render(script, sx, sy, size * SCRIPT, cv)
        return sx + width_of(script, size * SCRIPT, cv) - x
    if kind == "subsup":
        base, sub, sup = node[1], node[2], node[3]
        wb = width_of(base, size, cv)
        render(base, x, y, size, cv)
        sx = x + wb + 0.05 * size
        render(sub, sx, y + 0.30 * size, size * SCRIPT, cv)
        sx += width_of(sub, size * SCRIPT, cv)
        render(sup, sx, y - 0.45 * size, size * SCRIPT, cv)
        return sx + width_of(sup, size * SCRIPT, cv) - x
    if kind == "big":
        op, sub, sup = node[1], node[2], node[3]
        w = render(op, x, y, size, cv)
        cx = x + w + 0.05 * size
        if sub is not None:
            cx += render(sub, cx, y + 0.30 * size, size * SCRIPT, cv)
        if sup is not None:
            cx += render(sup, cx, y - 0.45 * size, size * SCRIPT, cv)
        return cx - x
    if kind == "sqrt":
        ws = cv.run(x, y, "\u221a", size)
        ix = x + ws + 0.1 * size
        cv.push()
        wi = render(node[1], ix, y, size, cv)
        _, top, _, _ = cv.pop()          # radicand extent
        cv.rule(ix, ix + wi, top - 0.12 * size)
        return ws + 0.1 * size + wi
    if kind == "dot":
        base = node[1]
        wb = width_of(base, size, cv)
        render(base, x, y, size, cv)
        # The accent glyph is the SAME size as the base (as TeX emits it), so
        # Channel B classifies it as an accent, not a superscript.
        aw = cv.width("\u02d9", size)
        cv.run(x + (wb - aw) / 2, y - 0.95 * size, "\u02d9", size)
        return wb
    if kind == "stack":
        w1 = width_of(node[1], size, cv)
        w2 = width_of(node[2], size, cv)
        w = max(w1, w2)
        render(node[1], x + (w - w1) / 2, y - 0.85 * size, size, cv)
        render(node[2], x + (w - w2) / 2, y + 0.55 * size, size, cv)
        return w
    raise ValueError(f"unknown node {kind!r}")


# ---------------------------------------------------------------- specs ---

G = "\u03c1"      # rho
MU = "\u03bc"     # mu
PART = "\u2202"   # partial
INT = "\u222b"
SUM = "\u2211"
INF = "\u221e"
DELTA = "\u0394"
MINUS = "\u2212"
LFLOOR, RFLOOR = "\u230a", "\u230b"

# expected: "match" = Channel B should reproduce the true LaTeX exactly;
# "withhold" = a construct the token vocabulary cannot represent.
EQ_SPECS = [
    {
        "id": "h1",
        "heading": "Navier-Stokes (x-momentum), inviscid",
        "construct": "partial derivatives; four fractions; Greek",
        "expected": "match",
        "latex": r"\frac{\partial u}{\partial t} + u \frac{\partial u}{\partial x} "
                 r"= -\frac{1}{\rho} \frac{\partial p}{\partial x}",
        "node": SEQ(
            FRAC(R(PART + "u"), R(PART + "t")), R("+"), R("u"),
            FRAC(R(PART + "u"), R(PART + "x")), R("="), R(MINUS),
            FRAC(R("1"), R(G)), FRAC(R(PART + "p"), R(PART + "x")),
        ),
    },
    {
        "id": "h2",
        "heading": "Deflection integral",
        "construct": "definite integral; limits; fraction in the integrand",
        "expected": "match",
        "latex": r"\int_0^L \frac{q}{EI} \, dx",
        "node": SEQ(
            BIG(R(INT), R("0"), R("L")),
            FRAC(R("q"), R("EI")),
            R("dx"),
        ),
    },
    {
        "id": "h3",
        "heading": "Aggregate variance",
        "construct": "summation with limits; subscript and superscript in a fraction",
        "expected": "match",
        "latex": r"\sum_{i=1}^{n} \frac{x_i}{s^2}",
        "node": SEQ(
            BIG(R(SUM), R("i=1"), R("n")),
            FRAC(SCR(R("x"), sub=R("i")), SCR(R("s"), sup=R("2"))),
        ),
    },
    {
        "id": "h4",
        "heading": "Wave speed from the radical",
        "construct": "radical whose radicand is itself a fraction",
        "expected": "match",
        "latex": r"\sqrt{\frac{2 g h}{1 + f}}",
        "node": SQRT(FRAC(R("2gh"), SEQ(R("1"), R("+"), R("f")))),
    },
    {
        "id": "h5",
        "heading": "Energy balance with a mass flow rate",
        "construct": "multi-letter subscripts; accent over a base; Greek",
        "expected": "match",
        "latex": r"v_{in} = v_{out} + \dot{m} c_p \Delta T",
        "node": SEQ(
            SCR(R("v"), sub=R("in")), R("="), SCR(R("v"), sub=R("out")), R("+"),
            DOT(R("m")), SCR(R("c"), sub=R("p")), R(DELTA + "T"),
        ),
    },
    {
        "id": "h6",
        "heading": "Buckling coefficient",
        "construct": "subscript and superscript together inside a numerator",
        "expected": "match",
        "latex": r"a_i = \frac{x_i^2}{2 L}",
        "node": SEQ(
            SCR(R("a"), sub=R("i")), R("="),
            FRAC(SCR(R("x"), sub=R("i"), sup=R("2")), R("2L")),
        ),
    },
    {
        "id": "h7",
        "heading": "Binomial coefficient",
        "construct": "two rows in brackets with no bar (not a fraction)",
        "expected": "withhold",
        "latex": r"\binom{n}{k} = \frac{n!}{k!\,(n-k)!}",
        "node": SEQ(
            SEQ(R("("), STACK(R("n"), R("k")), R(")")),
            R("="),
            FRAC(R("n!"), SEQ(R("k!"), R("("), R("n"), R(MINUS), R("k"), R(")!"))),
        ),
    },
    {
        "id": "h8",
        "heading": "Floor of a scaled sample",
        "construct": "floor brackets: a macro outside the token vocabulary",
        "expected": "withhold",
        "latex": r"\lfloor x \rfloor = 3",
        "node": SEQ(R(LFLOOR), R("x"), R(RFLOOR), R("="), R("3")),
    },
]


def build(out_pdf: str = HARD_PDF, *, verbose: bool = False) -> list[dict]:
    """Write the PDF and return each equation's spec plus its bbox."""
    fontfile = ensure_math_font()
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    cv = Canvas(page, fontfile)

    cv.text(72, 70, "Engineering Mathematics 2 - harder verification page", 15)
    y = 110.0
    placed = []
    for spec in EQ_SPECS:
        cv.text(72, y, spec["heading"], 11)
        y += 22.0
        cv.begin()
        render(spec["node"], 118.0, y, BASE, cv)
        bbox = cv.end()
        placed.append({**spec, "bbox": bbox})
        if verbose:
            print(f"  {spec['id']}: bbox=({bbox[0]:.1f},{bbox[1]:.1f},{bbox[2]:.1f},{bbox[3]:.1f})")
        y += 62.0

    doc.save(out_pdf)
    doc.close()
    return placed


def write_replay(placed: list[dict], path: str = os.path.join(HERE, "replay.json")) -> str:
    """The offline readings: each equation's *true* LaTeX, keyed by the ids the
    pipeline assigns (p1e1..p1e8). This lets the whole system run with no API
    key. For h7/h8 the reading is correct, yet Channel B still withholds them,
    which is the fail-closed behaviour we want to show."""
    data = {f"p1e{i + 1}": {"read": spec["latex"]} for i, spec in enumerate(placed)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def _check() -> None:
    """Build, reload through ingest.load_page, and diff Channel B against gold."""
    from ingest.pdf import find_display_equations, load_page
    from equations.glyphs import glyph_tokens
    from equations.tokens import diff, latex_to_tokens, to_text

    placed = build(verbose=True)
    page = load_page(HARD_PDF, 0)
    print(f"\nfinder sees {len(find_display_equations(page))} equation region(s)")
    for spec in placed:
        gold = latex_to_tokens(spec["latex"])
        try:
            got = glyph_tokens(page, spec["bbox"])
        except Exception as e:  # noqa: BLE001
            print(f"{spec['id']} [{spec['expected']}]: Channel B unavailable: {e}")
            continue
        d = diff(gold, got)
        verdict = "MATCH" if not d else f"{len(d)} difference(s)"
        print(f"{spec['id']} [{spec['expected']}]: {verdict}")
        if d:
            print("    gold :", to_text(gold))
            print("    glyph:", to_text(got))
            for item in d:
                print("    - " + item.explain())


if __name__ == "__main__":
    _check()
    write_replay(build())
    print("\nwrote", HARD_PDF)
    print("wrote", os.path.join(HERE, "replay.json"))
