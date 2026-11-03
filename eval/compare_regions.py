"""Compare the two display-equation finders on the gold PDFs.

    python eval/compare_regions.py                 # heuristic counts (offline)
    python eval/compare_regions.py --live          # ask Muse Spark, then compare
    python eval/compare_regions.py --live --save   # ... and cache the model boxes

For every page of every eval PDF we run the deterministic heuristic and (in
--live mode) the model region proposal, then cross-check them: a region both
found is *matched*, one only the model found is *extra*, one only the heuristic
found is *missed*. The model box is compared as it leaves the layout module --
already validated and snapped to the page's glyphs.

Note: ``eval/gold.json``'s bboxes were themselves taken from the heuristic
finder, so this compares model against heuristic; that is exactly the point of
the task. Offline (no cache, no --live) it only reports what the heuristic finds.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest.pdf import find_display_equations, load_page  # noqa: E402
from layout import regions as region_finder  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "eval", "regions_cache.json")
DEFAULT_PDFS = [
    "eval/pdfs/lec_notes.pdf",
    "eval/pdfs/deriving-navier-stokes.pdf",
]


def _page_count(pdf: str) -> int:
    import pymupdf
    doc = pymupdf.open(os.path.join(ROOT, pdf))
    n = doc.page_count
    doc.close()
    return n


def _load_cache() -> dict:
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def _model_boxes(pdf: str, pno: int, page, live: bool, cache: dict) -> list[tuple]:
    """Model boxes for a page, from the cache or (if --live) the model."""
    key = f"{pdf}#{pno}"
    if live:
        boxes = region_finder.propose_regions(
            page, region_finder.render_page(os.path.join(ROOT, pdf), pno))
        cache[key] = [list(b) for b in boxes]
        return [(b, "model") for b in boxes]
    if key in cache:
        return [(tuple(b), "model") for b in cache[key]]
    return []


def compare_on_pdf(pdf: str, live: bool, cache: dict, pages: int | None = None) -> dict:
    n = _page_count(pdf)
    if pages is not None:
        n = min(n, pages)
    totals = {"pages": 0, "heuristic": 0, "model": 0, "matched": 0, "missed": 0, "extra": 0}
    rows = []
    for pno in range(n):
        page = load_page(os.path.join(ROOT, pdf), pno)
        heur = find_display_equations(page)
        model = _model_boxes(pdf, pno, page, live, cache)
        if model:
            extra, missed = region_finder.cross_check([b for b, _ in model], heur)
            matched = len(model) - len(extra)
        else:
            extra, missed, matched = [], [], 0
        totals["pages"] += 1
        totals["heuristic"] += len(heur)
        totals["model"] += len(model)
        totals["matched"] += matched
        totals["extra"] += len(extra)
        totals["missed"] += len(missed)
        rows.append((pno + 1, len(heur), len(model), matched, len(missed), len(extra)))
    return {"totals": totals, "rows": rows}


def _markdown(results: dict, live: bool) -> str:
    have_model = any(r["totals"]["model"] for r in results.values())
    out = ["# Region finder comparison", ""]
    if not have_model:
        out += [
            "Model boxes were not available in this run (no `--live`, no cache).",
            "Only the heuristic counts are shown; re-run with `--live` to compare.",
            "",
        ]
    out += [
        "| PDF | Pages | Heuristic | Model | Matched | Model extra | Heuristic missed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    grand = {"pages": 0, "heuristic": 0, "model": 0, "matched": 0, "missed": 0, "extra": 0}
    for pdf, res in results.items():
        t = res["totals"]
        for k in grand:
            grand[k] += t[k]
        out.append(
            f"| `{os.path.basename(pdf)}` | {t['pages']} | {t['heuristic']} | {t['model']} "
            f"| {t['matched']} | {t['extra']} | {t['missed']} |"
        )
    out.append(
        f"| **total** | {grand['pages']} | {grand['heuristic']} | {grand['model']} "
        f"| {grand['matched']} | {grand['extra']} | {grand['missed']} |"
    )
    out += ["", "Per page:", ""]
    out += ["| PDF | Page | Heuristic | Model | Matched | Model extra | Heuristic missed |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for pdf, res in results.items():
        for (pno, h, m, matched, missed, extra) in res["rows"]:
            if not m:
                continue
            out.append(f"| `{os.path.basename(pdf)}` | {pno} | {h} | {m} | {matched} | {extra} | {missed} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", action="append", help="eval PDF (repeatable; default both)")
    ap.add_argument("--pages", type=int, help="only the first N pages of each PDF")
    ap.add_argument("--live", action="store_true", help="call Muse Spark for model boxes")
    ap.add_argument("--save", action="store_true", help="cache the model boxes")
    ap.add_argument("--out", default=os.path.join(ROOT, "eval", "regions_compare.md"))
    a = ap.parse_args()

    pdfs = a.pdf or DEFAULT_PDFS
    cache = _load_cache()
    results = {}
    for pdf in pdfs:
        print(f"# {pdf}", flush=True)
        results[pdf] = compare_on_pdf(pdf, a.live, cache, a.pages)
        t = results[pdf]["totals"]
        print(f"  pages={t['pages']} heuristic={t['heuristic']} model={t['model']} "
              f"matched={t['matched']} extra={t['extra']} missed={t['missed']}", flush=True)
    if a.live and a.save:
        _save_cache(cache)
        print(f"cached model boxes -> {CACHE}")
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(_markdown(results, a.live))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
