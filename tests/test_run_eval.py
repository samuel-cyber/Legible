"""Evaluation-harness tests (no network, no model, no PDFs needed).

The runner must check every equation against the glyphs of the page it is
actually on. An earlier version cached pages by PDF path alone, so every
equation in a multi-page document was checked against whichever page of that
document loaded first -- silently withholding hundreds of correct equations.
These tests pin the (pdf, page) keying with an injected fake loader.
"""
from __future__ import annotations

import os

from eval.run_eval import load_pages


def _eq(eq_id: str, pdf: str, page: int) -> dict:
    return {"id": eq_id, "pdf": pdf, "page": page, "bbox": [0, 0, 1, 1], "latex": "x"}


def test_pages_are_keyed_by_pdf_and_page():
    calls = []

    def fake_loader(path, number):
        calls.append((path, number))
        return {"path": path, "page": number}

    gold = [
        _eq("a", "eval/pdfs/doc-a.pdf", 1),
        _eq("b", "eval/pdfs/doc-a.pdf", 2),
        _eq("c", "eval/pdfs/doc-a.pdf", 1),   # same page as "a": no reload
        _eq("d", "eval/pdfs/doc-b.pdf", 1),
    ]
    pages = load_pages(gold, loader=fake_loader)

    assert sorted(pages) == [("eval/pdfs/doc-a.pdf", 1), ("eval/pdfs/doc-a.pdf", 2),
                             ("eval/pdfs/doc-b.pdf", 1)]
    # Three distinct (pdf, page) pairs -> exactly three loads.
    assert len(calls) == 3
    assert pages[("eval/pdfs/doc-a.pdf", 2)]["page"] == 2


def test_no_page_is_reused_across_pages_of_one_document():
    """A page-2 equation must not see page-1 glyphs."""
    def fake_loader(path, number):
        return {"path": path, "page": number}

    pages = load_pages(
        [_eq("a", "doc.pdf", 1), _eq("b", "doc.pdf", 2)], loader=fake_loader)
    assert pages[("doc.pdf", 1)]["page"] == 1
    assert pages[("doc.pdf", 2)]["page"] == 2


def test_looks_up_pages_under_root():
    seen = {}

    def fake_loader(path, number):
        seen["path"] = path
        return object()

    load_pages([_eq("a", "eval/pdfs/doc.pdf", 5)], loader=fake_loader)
    assert os.path.basename(seen["path"]) == "doc.pdf"
    assert os.path.isabs(seen["path"])
