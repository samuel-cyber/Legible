"""List every display equation Legible finds in a PDF, for building eval/gold.json.

    py eval/list_equations.py path/to/notes.pdf

Prints, for every page, every region find_display_equations locates: its bbox,
the glyph-layer text (equations.glyphs.glyph_text) and the token form
(equations.tokens.to_text applied to equations.glyphs.glyph_tokens). Copy the
bbox and page into a gold.json entry and type in the true LaTeX yourself —
this script never invents gold LaTeX.
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Windows consoles default to a codepage (e.g. cp1252) that can't print the
# Greek/math symbols glyph_text and to_text produce.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pymupdf

from equations.glyphs import GlyphLayerUnavailable, glyph_text, glyph_tokens
from equations.tokens import to_text
from ingest.pdf import find_display_equations, load_page


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    n_pages = doc.page_count
    doc.close()

    total = 0
    for pno in range(n_pages):
        page = load_page(a.pdf, pno)
        boxes = find_display_equations(page)
        if not boxes:
            continue
        print(f"\n== page {pno} ({len(boxes)} equation(s)) ==")
        for k, bbox in enumerate(boxes):
            eq_id = f"p{pno + 1}e{k + 1}"
            total += 1
            try:
                tokens = glyph_tokens(page, bbox)
                token_form = to_text(tokens)
            except GlyphLayerUnavailable:
                token_form = "<no glyph layer>"
            text = glyph_text(page, bbox)
            bbox_list = [round(c, 2) for c in bbox]
            print(f"{eq_id:8s} page={pno} bbox={bbox_list}")
            print(f"           glyph_text: {text}")
            print(f"           token_form: {token_form}")

    print(f"\n{total} equation(s) found across {n_pages} page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
