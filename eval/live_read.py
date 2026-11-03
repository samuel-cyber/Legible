"""Run the REAL Channel A over the gold set and classify every A/B disagreement.

    python eval/live_read.py                 # 152 crops, real Muse Spark readings
    python eval/live_read.py --limit 20      # quick sample

``eval/run_eval.py --live`` still feeds A from the stored reading (it is built to
measure the *decision* rule and Channel C). To see the reader's real mistakes we
have to let Muse Spark read the crops itself. For each gold equation this:

  1. crops the equation (the same crop the pipeline would use),
  2. asks Muse Spark to transcribe it (Channel A),
  3. runs the fail-closed gate (A vs B; Channel C off, no repair),

and then splits the outcomes:

  * ``agrees``    -- A matched B: the reader got it right.
  * ``muse_error``-- A disagreed with B, and B reproduces the gold equation, so
                     the *reading* is the thing that is wrong. This is the list
                     of real Muse Spark errors.
  * ``b_gap``     -- B cannot reproduce the gold equation for this construct, so
                     a disagreement here is a Channel B limitation (the known
                     "withheld" set), not evidence about the reader.

Writes ``eval/live_read.json`` and ``eval/live_read.md``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from equations.decide import verify_equation  # noqa: E402
from equations.glyphs import glyph_tokens, glyph_text, GlyphLayerUnavailable  # noqa: E402
from equations.tokens import diff, latex_to_tokens, to_text  # noqa: E402
from equations import vision  # noqa: E402
from ingest.pdf import load_page, render_crop  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD = os.path.join(ROOT, "eval", "gold.json")


def b_reproduces_gold(page, bbox, gold_latex: str) -> bool:
    """True when Channel B rebuilds the gold equation for this bbox."""
    try:
        b = glyph_tokens(page, tuple(bbox))
    except GlyphLayerUnavailable:
        return False
    return not diff(b, latex_to_tokens(gold_latex))


def read_one(eq, pages, workdir, transcribe):
    crop = render_crop(
        os.path.join(ROOT, eq["pdf"]), eq["page"], tuple(eq["bbox"]),
        os.path.join(workdir, f"{eq['id']}.png"),
    )
    page = pages[(eq["pdf"], eq["page"])]
    b_ok = b_reproduces_gold(page, eq["bbox"], eq["latex"])
    result = verify_equation(
        eq["id"], page, tuple(eq["bbox"]), crop,
        transcribe=transcribe, repair=None, compare=False, render=None,
        use_glyphs=True, workdir=workdir,
    )
    if result.status == "verified":
        kind = "agrees"
    elif b_ok:
        kind = "muse_error"
    else:
        kind = "b_gap"
    # When the gate withholds, result.latex stays None by design; the reading
    # itself is kept on the attempt, which is what we want to show here.
    read = result.latex
    if read is None and result.attempts:
        read = result.attempts[0].latex or None
    return {
        "id": eq["id"], "pdf": eq["pdf"], "page": eq["page"],
        "gold": eq["latex"], "read": read,
        "status": result.status, "kind": kind,
        "why": result.explanation,
        "glyph": glyph_text(page, tuple(eq["bbox"])),
    }


def _markdown(rows: list[dict]) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    out = [
        "# Real Muse Spark reading (Channel A) vs Channel B",
        "",
        f"- Equations: {len(rows)}",
        f"- agrees (A matched B): {counts.get('agrees', 0)}",
        f"- Muse Spark errors (A wrong, B reproduces gold): {counts.get('muse_error', 0)}",
        f"- Channel B gaps (B cannot reproduce gold): {counts.get('b_gap', 0)}",
        "",
    ]
    errs = [r for r in rows if r["kind"] == "muse_error"]
    if errs:
        out += ["## Muse Spark errors", "",
                "| Equation | Page | What A read | What the PDF says |",
                "| --- | ---: | --- | --- |"]
        for r in errs:
            out.append(f"| `{r['id']}` | {r['page'] + 1} | `{r['read']}` | `{r['glyph']}` |")
        out += ["", "Full explanations:", ""]
        for r in errs:
            out.append(f"- **{r['id']}**: {r['why']}")
        out.append("")
    out += ["## All readings", "",
            "| Equation | Kind | Read | Gold |", "| --- | --- | --- | --- |"]
    for r in rows:
        out.append(f"| `{r['id']}` | {r['kind']} | `{r['read']}` | `{r['gold']}` |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, help="only the first N equations")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    with open(GOLD, encoding="utf-8") as f:
        gold = json.load(f)["equations"]
    if a.limit:
        gold = gold[: a.limit]

    workdir = tempfile.mkdtemp(prefix="legible-live-")
    pages = {}
    for eq in gold:
        key = (eq["pdf"], eq["page"])
        if key not in pages:
            pages[key] = load_page(os.path.join(ROOT, eq["pdf"]), eq["page"])

    def job(eq):
        try:
            return read_one(eq, pages, workdir, vision.transcribe)
        except Exception as e:  # a failed call must not look like a reading
            return {"id": eq["id"], "pdf": eq["pdf"], "page": eq["page"],
                    "gold": eq["latex"], "read": "", "status": "error",
                    "kind": "call_failed", "why": str(e), "glyph": ""}

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        rows = list(pool.map(job, gold))

    with open(os.path.join(ROOT, "eval", "live_read.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows}, f, indent=2, ensure_ascii=False)
    with open(os.path.join(ROOT, "eval", "live_read.md"), "w", encoding="utf-8") as f:
        f.write(_markdown(rows))

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"equations={len(rows)}  {counts}")
    print("wrote eval/live_read.json and eval/live_read.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
