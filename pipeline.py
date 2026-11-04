"""Legible pipeline: PDF in, accessible page + verification report out.

    python pipeline.py demo/pages/fluids.pdf out/
    python pipeline.py demo/pages/fluids.pdf out/ --replay demo/readings.json   # offline test mode

With META_API_KEY set, Channel A (reading), C (visual check) and the repair
step call Muse Spark. In --replay mode, readings come from a JSON file instead
(used for tests and for evaluating the verifier on known errors); the glyph
layer, the decision rule and the output are exactly the same code either way.
"""
from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

import pymupdf

from assemble.html import render_report, render_student
from assemble.layout import PageInfo, page_blocks, scan_page_blocks
from clients import meta
from equations import renderback, vision
from equations.decide import EquationResult, decide_scanned_equation, verify_equation
from ingest import scan
from ingest.pdf import load_page, render_crop
from layout import regions as region_finder


def _title_of(pdf_path: str) -> str:
    doc = pymupdf.open(pdf_path)
    t = (doc.metadata or {}).get("title") or ""
    doc.close()
    return t.strip() or os.path.splitext(os.path.basename(pdf_path))[0].replace("_", " ").title()


def process(
    pdf_path: str,
    outdir: str,
    transcribe: Optional[Callable] = None,
    repair: Optional[Callable] = None,
    compare: Optional[Callable] = None,
    use_glyphs: bool = True,
    regions: str = "heuristic",
    scan_regions_ask: Optional[Callable] = None,
    on_event: Callable[[dict], None] = lambda e: None,
    workers: int = 6,
) -> dict:
    """Run the full pipeline.

    Channel control (each of these is an ablation switch):
      transcribe  Channel A. None -> use Muse Spark when an API key is set.
      repair      evidence-guided re-read. None -> use Muse Spark when available.
      compare     Channel C. None -> default (use Muse Spark when available).
                  False -> Channel C is explicitly OFF and is never called, even
                  when META_API_KEY is set. This is what keeps --replay offline.
      use_glyphs  Channel B. False -> disable the glyph layer (ablation).
      regions     layout finder. "heuristic" -> deterministic glyph grouping;
                  "model" -> Muse Spark proposes display-equation boxes, each
                  validated and snapped to glyphs, cross-checked against the
                  heuristic (union of the two). A regions finder only chooses
                  what gets cropped and which glyphs Channel B may read, so it
                  can never turn a wrong reading into a verified one.

    Pages with no usable glyph layer (``ingest.scan.is_scanned_page``) never
    go through the above at all: they take a separate, lower-trust path
    (``equations.decide.decide_scanned_equation``) that can only produce
    "ai_read" or "withheld", never "verified" or "repaired". This is
    automatic and per-page -- a born-digital page is completely unaffected,
    whether or not the document also has scanned pages.

      scan_regions_ask  override for the scanned-page region proposal's model
                  call (tests/offline use only; mirrors ``ask`` in
                  layout.regions.find_regions_scanned). None -> real Muse
                  Spark call when available.
    """
    os.makedirs(outdir, exist_ok=True)
    crops_dir = os.path.join(outdir, "crops")
    os.makedirs(crops_dir, exist_ok=True)

    live = meta.available()
    transcribe = transcribe or (vision.transcribe if live else None)
    repair = repair if repair is not None else (vision.repair if live else None)
    # compare=False means "off" (distinct from None meaning "default"), so a
    # replay/ablation run cannot accidentally call the model for Channel C.
    if compare is False:
        compare = None
    elif compare is None:
        compare = renderback.compare if live else None
    if transcribe is None:
        raise RuntimeError("No reader available: set META_API_KEY or pass --replay")
    on_event({
        "type": "config",
        "channels": ["A"] + (["B"] if use_glyphs else []) + (["C"] if compare else []),
        "repair": repair is not None,
    })

    doc = pymupdf.open(pdf_path)
    n_pages = doc.page_count
    doc.close()

    all_results: list[EquationResult] = []
    all_blocks = []
    all_pages: list[PageInfo] = []
    render = renderback.render_latex if compare else None
    for pno in range(n_pages):
        page = load_page(pdf_path, pno)

        # A page with no usable glyph layer (a scan or a photo of
        # handwriting) never reaches verify_equation at all: it takes a
        # separate, lower-trust path that can only produce "ai_read" or
        # "withheld". Born-digital pages are completely unaffected by this
        # branch's existence -- is_scanned_page is false for every one of
        # them, by construction (see ingest/scan.py).
        if scan.is_scanned_page(page, pdf_path, pno):
            results, blocks, page_info = _process_scanned_page(
                page, pdf_path, pno, transcribe, compare, render, crops_dir,
                ask=scan_regions_ask, on_event=on_event, n_pages=n_pages, workers=workers,
            )
            all_results += results
            all_blocks += blocks
            all_pages.append(page_info)
            continue

        found = region_finder.find_regions(page, pdf_path=pdf_path, pno=pno, mode=regions)
        boxes = [b for b, _ in found]
        on_event({
            "type": "page", "page": pno + 1, "pages": n_pages, "equations": len(boxes),
            "regions": regions,
            "sources": [src for _, src in found],
        })
        jobs = []
        for k, bbox in enumerate(boxes):
            eq_id = f"p{pno + 1}e{k + 1}"
            crop = render_crop(pdf_path, pno, bbox, os.path.join(crops_dir, f"{eq_id}.png"))
            jobs.append((eq_id, bbox, crop))

        def run(job):
            eq_id, bbox, crop = job
            on_event({"type": "equation_start", "id": eq_id})
            r = verify_equation(
                eq_id, page, bbox, crop, transcribe=transcribe, repair=repair,
                compare=compare, render=render,
                use_glyphs=use_glyphs, workdir=crops_dir,
            )
            on_event({"type": "equation_done", "id": eq_id, "status": r.status, "why": r.plain_explanation})
            return r

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(run, jobs))
        all_results += results
        all_blocks += page_blocks(page, [(r.id, r.bbox) for r in results])
        all_pages.append(PageInfo(number=pno + 1, is_scan=False))

    title = _title_of(pdf_path)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_student(title, all_blocks, all_results, pages=all_pages))
    with open(os.path.join(outdir, "report.html"), "w", encoding="utf-8") as f:
        f.write(render_report(title, all_results, pages=all_pages))
    # Unchanged on purpose: these three keys and this exact dict are the
    # born-digital regression contract (the replay demo's printed summary).
    # ai_read is a new, separate status and is deliberately NOT added here;
    # it is available via all_results / all_pages for any caller that wants it.
    summary = {s: sum(r.status == s for r in all_results) for s in ("verified", "repaired", "withheld")}
    on_event({"type": "done", **summary})
    return {"title": title, "results": all_results, "summary": summary, "pages": all_pages}


def _process_scanned_page(page, pdf_path, pno, transcribe, compare, render, crops_dir,
                          ask, on_event, n_pages, workers) -> tuple[list, list, PageInfo]:
    """The scan/handwriting path for one page: no verify_equation, no repair,
    no heuristic region fallback -- see decide_scanned_equation and
    find_regions_scanned for why each of those is deliberately absent here.
    """
    body_text = scan.ocr_layer_text(page)
    source = "ocr" if body_text else ""

    if not body_text:
        body_text = scan.tesseract_text(pdf_path, pno)
        source = "ocr" if body_text else ""

    page_png = None
    if not body_text:
        try:
            # Same zoom as find_regions_scanned's default below -- a scanned
            # page needs a sharp image for the model to read or locate
            # anything accurately (see that function's docstring).
            page_png = region_finder.render_page(pdf_path, pno, zoom=4.0)
            body_text = vision.page_text(page_png)
            source = "ai" if body_text else ""
        except Exception:
            body_text, source = None, ""

    boxes = region_finder.find_regions_scanned(page, pdf_path, pno, ask=ask, page_png=page_png)
    on_event({
        "type": "page", "page": pno + 1, "pages": n_pages, "equations": len(boxes),
        "regions": "scanned", "sources": ["scanned"] * len(boxes),
    })

    jobs = []
    for k, bbox in enumerate(boxes):
        eq_id = f"p{pno + 1}e{k + 1}"
        crop = render_crop(pdf_path, pno, bbox, os.path.join(crops_dir, f"{eq_id}.png"))
        jobs.append((eq_id, bbox, crop))

    def run(job):
        eq_id, bbox, crop = job
        on_event({"type": "equation_start", "id": eq_id})
        ocr_text = scan.ocr_text_in_bbox(page, bbox)
        r = decide_scanned_equation(
            eq_id, bbox, crop, transcribe=transcribe, compare=compare, render=render,
            ocr_text=ocr_text, workdir=crops_dir,
        )
        on_event({"type": "equation_done", "id": eq_id, "status": r.status, "why": r.plain_explanation})
        return r

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(run, jobs))

    note = ("This page is a scan or handwritten, so equations couldn't be "
            "independently verified against the original.")
    if source:
        note += f" Body text read by {'OCR' if source == 'ocr' else 'AI'}."
    blocks = scan_page_blocks(note, body_text, [(r.id, r.bbox) for r in results])
    return results, blocks, PageInfo(number=pno + 1, is_scan=True, body_text_source=source)


def replay_reader(path: str):
    """Readings from a JSON file: {"p1e1": {"read": "...", "repair": "..."}}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    def _key(crop):
        return os.path.splitext(os.path.basename(crop))[0]

    def transcribe(crop):
        return data[_key(crop)]["read"]

    def repair(crop, latex, problems):
        entry = data[_key(crop)]
        return entry.get("repair", entry["read"])

    return transcribe, repair


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("--replay", help="JSON file of readings (offline test mode)")
    ap.add_argument("--no-glyphs", action="store_true", help="ablation: disable Channel B")
    ap.add_argument("--no-visual", action="store_true", help="ablation: disable Channel C")
    ap.add_argument("--regions", choices=("heuristic", "model"), default="heuristic",
                    help="how to find display equations (default: heuristic)")
    a = ap.parse_args()
    t = r = None
    if a.replay:
        t, r = replay_reader(a.replay)
    # --replay is offline by contract: never reach for the model for Channel C,
    # even if META_API_KEY happens to be set in the environment.
    compare = False if (a.replay or a.no_visual) else None
    # Likewise, the region model is a model call: with --replay we stay offline
    # and use the deterministic finder no matter what was requested.
    regions_mode = "heuristic" if a.replay else a.regions
    out = process(a.pdf, a.outdir, transcribe=t, repair=r, compare=compare,
                  use_glyphs=not a.no_glyphs, regions=regions_mode,
                  on_event=lambda e: print(json.dumps(e)))
    print(out["summary"])
