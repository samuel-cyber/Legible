"""PDF ingestion: glyphs with positions, horizontal rules, and page/crop images.

Everything here is deterministic (no model). It is the raw material for
Channel B (glyph-layer reconstruction) and for cropping images that the
vision channels look at.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pymupdf

# Fonts that LaTeX/Word use for math. Used only by the fallback equation
# finder; Channel B itself works on whatever glyphs sit inside a bbox.
MATH_FONT_PREFIXES = ("CMMI", "CMSY", "CMEX", "MSAM", "MSBM", "CambriaMath", "STIX", "LMMath", "Asana")


@dataclass
class Glyph:
    c: str
    font: str
    size: float
    x: float          # origin x (left of glyph on baseline)
    y: float          # baseline y (PDF coords grow downward)
    bbox: tuple[float, float, float, float]

    @property
    def cx(self) -> float:
        return (self.bbox[0] + self.bbox[2]) / 2

    @property
    def cy(self) -> float:
        return (self.bbox[1] + self.bbox[3]) / 2

    @property
    def is_math_font(self) -> bool:
        return self.font.startswith(MATH_FONT_PREFIXES)


@dataclass
class Rule:
    """A horizontal line segment, e.g. a fraction bar."""
    x0: float
    x1: float
    y: float


@dataclass
class Page:
    number: int
    width: float
    height: float
    glyphs: list[Glyph] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    lines: list[list[Glyph]] = field(default_factory=list)  # PDF text lines, for layout


def load_page(path: str, number: int = 0) -> Page:
    doc = pymupdf.open(path)
    p = doc[number]
    page = Page(number=number, width=p.rect.width, height=p.rect.height)

    raw = p.get_text("rawdict")
    for block in raw["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            line_glyphs = []
            for span in line["spans"]:
                for ch in span["chars"]:
                    if not ch["c"].strip():
                        continue
                    g = Glyph(
                        c=ch["c"],
                        font=span["font"].split("+")[-1],
                        size=round(span["size"], 2),
                        x=ch["origin"][0],
                        y=ch["origin"][1],
                        bbox=tuple(ch["bbox"]),
                    )
                    page.glyphs.append(g)
                    line_glyphs.append(g)
            if line_glyphs:
                page.lines.append(line_glyphs)

    for d in p.get_drawings():
        r = d["rect"]
        # Thin, wide shapes are horizontal rules (fraction bars, overlines).
        if r.height < 1.5 and r.width > 2:
            page.rules.append(Rule(x0=r.x0, x1=r.x1, y=(r.y0 + r.y1) / 2))
    doc.close()
    return page


def find_display_equations(page: Page, left_margin: float | None = None, indent: float = 40.0) -> list[tuple]:
    """Fallback equation finder for born-digital PDFs.

    Groups indented text lines that contain math-font glyphs into display
    equations and returns their bounding boxes. In the full pipeline Muse
    Spark proposes equation regions; this keeps Channel B testable alone.
    """
    if not page.lines:
        return []
    if left_margin is None:
        left_margin = min(l[0].x for l in page.lines)

    candidates = [
        l for l in page.lines
        if l[0].x > left_margin + indent and any(g.is_math_font for g in l)
    ]
    candidates.sort(key=lambda l: min(g.bbox[1] for g in l))

    groups: list[list[Glyph]] = []
    for line in candidates:
        top = min(g.bbox[1] for g in line)
        if groups and top - max(g.bbox[3] for g in groups[-1]) < 6:
            groups[-1].extend(line)
        else:
            groups.append(list(line))

    boxes = []
    for grp in groups:
        x0 = min(g.bbox[0] for g in grp) - 2
        y0 = min(g.bbox[1] for g in grp) - 2
        x1 = max(g.bbox[2] for g in grp) + 2
        y1 = max(g.bbox[3] for g in grp) + 2
        boxes.append((x0, y0, x1, y1))
    return boxes


def render_crop(path: str, number: int, bbox: tuple, out_png: str, zoom: float = 4.0, pad: float = 1.0) -> str:
    """Render a region of a page to PNG for the vision channels."""
    doc = pymupdf.open(path)
    p = doc[number]
    clip = pymupdf.Rect(bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
    pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    pix.save(out_png)
    doc.close()
    return out_png
