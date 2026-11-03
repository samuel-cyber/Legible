"""Channel B: rebuild an equation's structure from the PDF glyph layer.

No model is involved. Structure comes from geometry alone:
  - fraction bars are horizontal rules; glyphs above are numerator, below are denominator
  - smaller glyphs raised above the local baseline are superscripts, lowered are subscripts
  - accent glyphs (the dot in m-dot) attach to the nearest base glyph

Because it reads what the PDF actually contains, this channel cannot
hallucinate. It fails in different ways from a vision model: on scanned pages
(no glyphs at all) and on unusual layouts, which the caller reports as
"glyph layer unavailable" rather than guessing.
"""
from __future__ import annotations

from dataclasses import dataclass

from ingest.pdf import Glyph, Page, Rule
from equations.tokens import (
    ACCENT_GLYPHS, END, FRAC, OVER, OVERLAYS, Token, _canonical, norm, with_overlays,
)


@dataclass
class _Frac:
    bar: Rule
    num: list
    den: list

    @property
    def x(self) -> float:
        return self.bar.x0


class GlyphLayerUnavailable(Exception):
    pass


def _inside(g: Glyph, bbox) -> bool:
    return bbox[0] <= g.cx <= bbox[2] and bbox[1] <= g.cy <= bbox[3]


def _build(glyphs: list[Glyph], rules: list[Rule]) -> list:
    """Return a list of items (Glyph or _Frac), outermost fractions first."""
    if not rules:
        return list(glyphs)
    main = max(g.size for g in glyphs) if glyphs else 10
    band = 2.6 * main
    # Widest bar first, so nested fractions are handled inside their parent.
    for bar in sorted(rules, key=lambda r: r.x1 - r.x0, reverse=True):
        col = [g for g in glyphs if bar.x0 - 1 <= g.cx <= bar.x1 + 1 and abs(g.cy - bar.y) < band]
        num = [g for g in col if g.cy < bar.y]
        den = [g for g in col if g.cy > bar.y]
        rest_rules = [r for r in rules if r is not bar]
        if not num or not den:
            # An overline (e.g. a square-root vinculum), not a fraction: ignore the rule.
            return _build(glyphs, rest_rules)
        inner_rules = [r for r in rest_rules if bar.x0 - 1 <= r.x0 and r.x1 <= bar.x1 + 1 and abs(r.y - bar.y) < band]
        num_rules = [r for r in inner_rules if r.y < bar.y]
        den_rules = [r for r in inner_rules if r.y > bar.y]
        outer_rules = [r for r in rest_rules if r not in inner_rules]
        taken = set(map(id, col))
        others = [g for g in glyphs if id(g) not in taken]
        frac = _Frac(bar, _build(num, num_rules), _build(den, den_rules))
        return _build(others, outer_rules) + [frac]
    return list(glyphs)


def _script_roles(glyphs: list[Glyph]) -> dict[int, str]:
    """Classify each glyph in one level as base / sup / sub.

    A script (or accent) sits on the shoulder of the glyph immediately left of
    it, so the host is the nearest preceding glyph and the offset is measured
    against that host, not against one baseline for the whole level. In
    L^p(I) the "p" is only slightly above the level's main baseline but clearly
    raised above the "L" that owns it. A small glyph on the host's own baseline
    (the "-1" in x_{i-1}) inherits the host's role so a multi-glyph script stays
    one script.
    """
    roles: dict[int, str] = {}
    if not glyphs:
        return roles
    main = max(g.size for g in glyphs)
    ordered = sorted(glyphs, key=lambda g: g.cx)
    for idx, g in enumerate(ordered):
        role = "base"
        if g.size < main - 0.5:
            ref = ordered[idx - 1] if idx else None
            dy = g.y - ref.y if ref is not None else 0.0
            if dy < -0.8:
                role = "sup"
            elif dy > 0.8:
                role = "sub"
            elif ref is not None:
                role = roles.get(id(ref), "base")
        roles[id(g)] = role
    return roles


def _emit(items: list, ctx: tuple) -> list[Token]:
    glyphs = [it for it in items if isinstance(it, Glyph)]
    roles = _script_roles([g for g in glyphs if g.c not in ACCENT_GLYPHS])

    # Attach accents to the nearest non-accent glyph.
    accents: dict[int, list[Glyph]] = {}
    plain = [g for g in glyphs if g.c not in ACCENT_GLYPHS]
    for a in (g for g in glyphs if g.c in ACCENT_GLYPHS):
        if plain:
            host = min(plain, key=lambda g: abs(g.cx - a.cx))
            accents.setdefault(id(host), []).append(a)

    # An overlay (e.g. the slash of \ne) is drawn as its own glyph next to the
    # base it strikes; fold it into that base so "=" reads as "≠". The mark
    # goes to the nearest glyph at or just right of it, falling back to the
    # nearest glyph on its left.
    overlay_marks: dict[int, list[str]] = {}
    marks = [g for g in glyphs if g.c in OVERLAYS]
    others = [g for g in glyphs if g.c not in OVERLAYS]
    for m in marks:
        right = [g for g in others if g.cx >= m.cx - 1.0]
        left = [g for g in others if g.cx < m.cx - 1.0]
        pool, key = (right, min) if right else (left, max)
        if pool:
            host = key(pool, key=lambda g: abs(g.cx - m.cx))
            overlay_marks.setdefault(id(host), []).append(m.c)

    ordered = sorted(
        [it for it in items
         if not (isinstance(it, Glyph) and (it.c in ACCENT_GLYPHS or it.c in OVERLAYS))],
        key=lambda it: it.x if isinstance(it, _Frac) else it.bbox[0],
    )
    out: list[Token] = []
    for it in ordered:
        if isinstance(it, _Frac):
            out.append((FRAC, ctx))
            out += _emit(it.num, ctx + ("num",))
            out.append((OVER, ctx))
            out += _emit(it.den, ctx + ("den",))
            out.append((END, ctx))
        else:
            role = roles.get(id(it), "base")
            c = ctx if role == "base" else ctx + (role,)
            out.append((with_overlays(norm(it.c), overlay_marks.get(id(it), [])), c))
            for a in accents.get(id(it), []):
                out.append((norm(a.c), c))
    return out


def glyph_tokens(page: Page, bbox) -> list[Token]:
    glyphs = [g for g in page.glyphs if _inside(g, bbox)]
    if not glyphs:
        raise GlyphLayerUnavailable("no glyphs in region (scanned page or image equation)")
    rules = [r for r in page.rules if bbox[0] - 2 <= r.x0 and r.x1 <= bbox[2] + 2 and bbox[1] <= r.y <= bbox[3]]
    return _canonical(_emit(_build(glyphs, rules), ()))


def glyph_text(page: Page, bbox) -> str:
    """Raw left-to-right text of the region: the fallback shown for withheld equations."""
    glyphs = sorted((g for g in page.glyphs if _inside(g, bbox)), key=lambda g: (round(g.cy / 6), g.x))
    return "".join(norm(g.c) for g in glyphs)
