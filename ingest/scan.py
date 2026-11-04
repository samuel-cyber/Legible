"""Detection and support code for scanned / handwritten pages.

A second, clearly lower trust tier: these pages have no stored characters, so
anything read on them can be reported but never proven against the source.
Everything here only ever feeds the new "ai_read" path in
``equations.decide``; it is never called for a page that has a usable glyph
layer, so it cannot change behaviour for born-digital pages.
"""
from __future__ import annotations

import logging

import pymupdf

from ingest.pdf import Page

log = logging.getLogger(__name__)

BBox = tuple[float, float, float, float]

# A single image covering most of the page is the classic scan signature,
# even when an OCR text layer has been added on top of it.
DOMINANT_IMAGE_AREA_RATIO = 0.6


def is_scanned_page(page: Page, pdf_path: str, pno: int) -> bool:
    """True when this page has no usable glyph layer for math.

    Two independent signals, either one is enough:
      - no text at all (``page.glyphs`` empty): nothing to build structure
        from, full stop.
      - a dominant full-page image: even if an OCR text layer sits on top
        (so ``page.glyphs`` is non-empty), OCR text has no fraction bars, no
        sub/superscript geometry -- it cannot carry math structure, so the
        page is still routed to the lower-trust path.
    """
    if not page.glyphs:
        return True
    doc = pymupdf.open(pdf_path)
    try:
        p = doc[pno]
        page_area = p.rect.width * p.rect.height
        if page_area <= 0:
            return False
        for info in p.get_image_info():
            bbox = info.get("bbox")
            if not bbox:
                continue
            w = max(0.0, bbox[2] - bbox[0])
            h = max(0.0, bbox[3] - bbox[1])
            if (w * h) / page_area >= DOMINANT_IMAGE_AREA_RATIO:
                return True
    finally:
        doc.close()
    return False


def ocr_layer_text(page: Page) -> str | None:
    """Reading-order text from an existing (OCR'd) text layer, or None.

    On a page already classified as scanned, any text in ``page.glyphs`` is
    by definition an OCR layer, not hand-typeset text -- there is no other
    way characters could be there.
    """
    if not page.lines:
        return None
    lines = sorted(page.lines, key=lambda l: min(g.bbox[1] for g in l))
    out = []
    for line in lines:
        chars = sorted(line, key=lambda g: g.x)
        out.append("".join(g.c for g in chars))
    text = "\n".join(out).strip()
    return text or None


def ocr_text_in_bbox(page: Page, bbox: BBox) -> str | None:
    """Characters from an existing text layer that fall inside one equation's
    region, or None. Used only as the weak OCR-mismatch caution signal --
    never to verify anything."""
    chars = [g.c for g in page.glyphs if bbox[0] <= g.cx <= bbox[2] and bbox[1] <= g.cy <= bbox[3]]
    text = "".join(chars).strip()
    return text or None


def tesseract_text(pdf_path: str, pno: int, zoom: float = 3.0) -> str | None:
    """Body text via Tesseract, or None if pytesseract/Tesseract is unavailable.

    Soft dependency by design: a missing Python package or a missing system
    ``tesseract`` binary must never crash the pipeline, only fall through to
    the next source (Muse Spark).
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None
    doc = pymupdf.open(pdf_path)
    try:
        pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    finally:
        doc.close()
    try:
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        text = pytesseract.image_to_string(img)
    except Exception as e:  # TesseractNotFoundError, corrupt image, etc.
        log.warning("tesseract unavailable or failed (%s); falling back", e)
        return None
    text = text.strip()
    return text or None


def snap_to_ink(pdf_path: str, pno: int, box: BBox, zoom: float = 4.0,
                pad: float = 2.0, threshold: int = 200) -> BBox | None:
    """Tighten a proposed box to the dark pixels inside it; None if blank.

    The glyph-layer snap (``layout.regions.snap_to_glyphs``) needs PDF glyph
    objects, which a scanned page does not have. This is the scan
    equivalent: render just the proposed box and tighten to whatever ink is
    actually there, in page-point space.
    """
    import numpy as np

    doc = pymupdf.open(pdf_path)
    try:
        p = doc[pno]
        clip = pymupdf.Rect(*box)
        pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, colorspace=pymupdf.csGRAY)
    finally:
        doc.close()
    if pix.width <= 0 or pix.height <= 0:
        return None
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    dark = arr[..., 0] < threshold
    if not dark.any():
        return None
    ys, xs = np.where(dark)
    x0 = box[0] + float(xs.min()) / zoom - pad
    y0 = box[1] + float(ys.min()) / zoom - pad
    x1 = box[0] + float(xs.max() + 1) / zoom + pad
    y1 = box[1] + float(ys.max() + 1) / zoom + pad
    return (x0, y0, x1, y1)
