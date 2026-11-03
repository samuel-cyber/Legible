"""Model-proposed display-equation regions, validated and snapped to glyphs.

Two finders live here:

  * ``heuristic`` -- ``ingest.pdf.find_display_equations``: groups indented
    text lines that contain math-font glyphs. Cheap, deterministic, and exact
    for the pages it was written for, but it needs a known math font and it can
    miss an equation set in an unusual font or with unusual indentation.

  * ``model`` -- Muse Spark looks at the whole page and proposes a bounding box
    per display equation, in reading order. A model can also propose nonsense,
    so every box is validated (on the page, big enough) and then snapped to the
    glyphs inside it; a box with no glyphs is dropped. The heuristic still runs
    as a cross-check: the result is the union, and every disagreement (a region
    one finder saw and the other did not) is logged. If the model fails or
    returns nothing, the heuristic is used on its own.

Only the validated-and-snapped model boxes ever leave this module. The region
choice never decides an equation by itself -- it only sets what gets cropped
and which glyphs Channel B may look at -- so a wrong region can only cause a
withhold (fail-closed), never a false accept.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile

import pymupdf

from clients import meta
from ingest.pdf import Page, find_display_equations

log = logging.getLogger(__name__)

BBox = tuple[float, float, float, float]

# A display equation must be at least this big (points); smaller boxes are noise.
MIN_W = 20.0
MIN_H = 4.0

# Coordinates the model returns may be off by a little; allow this much slack
# outside the page before rejecting a box outright.
PAGE_TOL = 12.0

REGIONS_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "regions",
        "schema": {
            "type": "object",
            "properties": {
                "regions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x0": {"type": "number"},
                            "y0": {"type": "number"},
                            "x1": {"type": "number"},
                            "y1": {"type": "number"},
                        },
                        "required": ["x0", "y0", "x1", "y1"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["regions"],
            "additionalProperties": False,
        },
    },
}

_PAGE_PROMPT = (
    "This image is one page of an engineering document, {w:.0f} points wide and "
    "{h:.0f} points tall (origin at the top-left, y increases downward). Find "
    "every DISPLAY equation: a mathematical formula set on its own line, not "
    "inline math inside a sentence and not ordinary prose. For each one give a "
    "tight bounding box in POINTS -- x0, y0 is the top-left corner and x1, y1 "
    "the bottom-right -- and list the boxes in reading order (top to bottom). "
    "Reply with a single JSON object only."
)


class RegionProposalFailed(RuntimeError):
    """The model region proposal could not be used (call failed or unusable)."""


def render_page(pdf_path: str, pno: int, out_png: str | None = None, zoom: float = 2.0) -> str:
    """Render a whole page to PNG for the region model."""
    if out_png is None:
        fd, out_png = tempfile.mkstemp(prefix="legible-page-", suffix=".png")
        os.close(fd)
    doc = pymupdf.open(pdf_path)
    try:
        pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        pix.save(out_png)
    finally:
        doc.close()
    return out_png


def _normalize(box: BBox) -> BBox:
    x0, y0, x1, y1 = box
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def valid_box(page: Page, box: BBox) -> bool:
    """True when the box is a plausible display-equation region for this page."""
    x0, y0, x1, y1 = box
    if x1 - x0 < MIN_W or y1 - y0 < MIN_H:
        return False
    if x0 < -PAGE_TOL or y0 < -PAGE_TOL:
        return False
    if x1 > page.width + PAGE_TOL or y1 > page.height + PAGE_TOL:
        return False
    return True


def snap_to_glyphs(page: Page, box: BBox, pad: float = 2.0) -> BBox | None:
    """Tighten a box to the glyphs whose centre it contains; None if empty.

    Snapping means a slightly-wrong model box still captures exactly the
    equation's glyphs (and nothing else), which is all Channel B needs.
    """
    x0, y0, x1, y1 = box
    inside = [g for g in page.glyphs if x0 <= g.cx <= x1 and y0 <= g.cy <= y1]
    if not inside:
        return None
    return (
        min(g.bbox[0] for g in inside) - pad,
        min(g.bbox[1] for g in inside) - pad,
        max(g.bbox[2] for g in inside) + pad,
        max(g.bbox[3] for g in inside) + pad,
    )


def _row_band(boxes: list[BBox]) -> float:
    if not boxes:
        return 1.0
    heights = sorted(b[3] - b[1] for b in boxes)
    band = heights[len(heights) // 2] * 0.6
    return band if band > 0 else 1.0


def order_key(boxes: list[BBox]):
    """A sort key putting boxes in reading order: by row band, then left to right."""
    band = _row_band(boxes)
    return lambda b: (round(b[1] / band), b[0])


def in_reading_order(boxes: list[BBox]) -> list[BBox]:
    if not boxes:
        return []
    return sorted(boxes, key=order_key(boxes))


def _iou(a: BBox, b: BBox) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = ix1 - ix0, iy1 - iy0
    if iw <= 0 or ih <= 0:
        return 0.0
    inter = iw * ih
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def cross_check(model_boxes: list[BBox], heuristic_boxes: list[BBox],
                iou: float = 0.4) -> tuple[list[BBox], list[BBox]]:
    """Return (model-only, heuristic-only) boxes -- the disagreements."""
    matched_m: set[int] = set()
    matched_h: set[int] = set()
    for i, m in enumerate(model_boxes):
        for j, h in enumerate(heuristic_boxes):
            if _iou(m, h) >= iou:
                matched_m.add(i)
                matched_h.add(j)
    extras = [b for i, b in enumerate(model_boxes) if i not in matched_m]
    missed = [b for i, b in enumerate(heuristic_boxes) if i not in matched_h]
    return extras, missed


def _dedupe(boxes: list[BBox], iou: float = 0.7) -> list[BBox]:
    kept: list[BBox] = []
    for b in boxes:
        if any(_iou(b, k) >= iou for k in kept):
            continue
        kept.append(b)
    return kept


def parse_regions(page: Page, data: dict) -> list[BBox]:
    """Validate, snap and order the model's raw region objects."""
    boxes: list[BBox] = []
    for r in data.get("regions", []):
        try:
            box = _normalize((float(r["x0"]), float(r["y0"]), float(r["x1"]), float(r["y1"])))
        except (KeyError, TypeError, ValueError):
            log.warning("dropping malformed model region %r", r)
            continue
        if not valid_box(page, box):
            log.warning("dropping invalid model region %r", box)
            continue
        snapped = snap_to_glyphs(page, box)
        if snapped is None:
            log.warning("dropping model region with no glyphs: %r", box)
            continue
        boxes.append(snapped)
    return in_reading_order(_dedupe(boxes))


def propose_regions(page: Page, page_png: str, ask=None) -> list[BBox]:
    """Ask the model for this page's display-equation boxes.

    ``ask`` mirrors ``clients.meta.ask_json`` (prompt, images, schema) so a test
    can substitute a deterministic double without a network call.
    """
    ask = ask or (lambda prompt, images=(), schema=None: meta.ask_json(
        prompt, images=images, schema=schema))
    prompt = _PAGE_PROMPT.format(w=page.width, h=page.height)
    try:
        data = ask(prompt, images=[page_png], schema=REGIONS_SCHEMA)
    except Exception as e:  # model call failed / unparseable JSON
        raise RegionProposalFailed(f"region model call failed: {e}") from e
    if not isinstance(data, dict):
        raise RegionProposalFailed("region model did not return a JSON object")
    return parse_regions(page, data)


def find_regions(page: Page, pdf_path: str | None = None, pno: int = 0,
                 mode: str = "heuristic", ask=None, page_png: str | None = None,
                 zoom: float = 2.0) -> list[tuple[BBox, str]]:
    """Return [(bbox, source)] for the page's display equations.

    mode="heuristic" -> the deterministic finder only.
    mode="model"     -> the model's boxes, cross-checked against the heuristic
                        (union), falling back to the heuristic if the model
                        fails or returns nothing. Sources are tagged so the
                        report can say where each region came from.
    """
    heuristic = find_display_equations(page)
    if mode == "heuristic":
        return [(b, "heuristic") for b in heuristic]
    if mode != "model":
        raise ValueError(f"unknown region mode: {mode!r}")

    try:
        if page_png is None:
            if pdf_path is None:
                raise RegionProposalFailed("no page image and no pdf path to render one")
            page_png = render_page(pdf_path, pno, zoom=zoom)
        model_boxes = propose_regions(page, page_png, ask=ask)
    except RegionProposalFailed as e:
        log.warning("model regions unavailable (%s); using the heuristic", e)
        return [(b, "heuristic") for b in heuristic]

    if not model_boxes:
        log.warning("model proposed no valid regions; using the heuristic")
        return [(b, "heuristic") for b in heuristic]

    extras, missed = cross_check(model_boxes, heuristic)
    for b in extras:
        log.warning("cross-check: model found a region the heuristic missed: %r", b)
    for b in missed:
        log.warning("cross-check: heuristic found a region the model missed: %r", b)

    combined = [(b, "model") for b in model_boxes] + [(b, "heuristic") for b in missed]
    # Build the key once: list.sort() temporarily empties the list while sorting,
    # so a key function that re-read ``combined`` would see it empty.
    key = order_key([b for b, _ in combined])
    combined.sort(key=lambda item: key(item[0]))
    return combined
