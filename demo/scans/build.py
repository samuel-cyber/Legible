"""Build an image-only (no text layer) version of the fluids demo page.

Rasterizes ``demo/pages/fluids.pdf`` to a pixmap and embeds it as the only
content of a new single-page PDF, so ``ingest.pdf.load_page`` sees zero
glyphs and zero rules on it -- exactly what a scanned page looks like to
Legible. The true equations on this page are already known
(``tests/cases.py``'s ``GOLD``), so a run over the fixture can be scored for
accuracy against a page whose answer we already have.

Rebuild with:
    py demo/scans/build.py
"""
from __future__ import annotations

import os
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SOURCE_PDF = os.path.join(ROOT, "demo", "pages", "fluids.pdf")
SCAN_PDF = os.path.join(HERE, "fluids_scan.pdf")


def build(zoom: float = 3.0, out_path: str = SCAN_PDF) -> str:
    src = pymupdf.open(SOURCE_PDF)
    page = src[0]
    rect = page.rect
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    src.close()

    out = pymupdf.open()
    new_page = out.new_page(width=rect.width, height=rect.height)
    new_page.insert_image(new_page.rect, pixmap=pix)
    out.save(out_path)
    out.close()
    return out_path


if __name__ == "__main__":
    path = build()
    print(f"wrote {path}")
