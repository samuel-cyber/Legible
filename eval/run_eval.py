"""Ablation evaluation runner.

Compares what Legible publishes (or refuses to publish) under four
configurations, on the same set of equations, in two modes:

    --injected   replay of known (corrupted) readings. No API needed; Channel C
                 is off because it needs the model. This is the deterministic,
                 reproducible run.
    --live       real Muse Spark readings and the real visual check.

    py eval/run_eval.py --injected
    py eval/run_eval.py --live

For every config it runs two corpora through the decision rule:
  - "gold" readings: the correct LaTeX. Withholding one is a FALSE REJECT.
  - "corrupted" readings: a known mis-reading. Publishing one is a FALSE ACCEPT.

Writes eval/results.json and eval/results.md.

Honesty note (rule 4): in --injected mode the repair step is an ORACLE — it is
handed the gold LaTeX, modelling "the model, told exactly what is wrong, reads
it correctly". It is labelled as such in the output. --live uses the real
repair. No number here is invented; every cell comes from an actual run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from equations import renderback, vision  # noqa: E402
from equations.decide import WITHHELD, verify_equation  # noqa: E402
from eval.inject import build_corpus  # noqa: E402
from ingest.pdf import load_page, render_crop  # noqa: E402

PUBLISHED = ("verified", "repaired")


# --------------------------------------------------------------- configs ---

class Config:
    def __init__(self, name, use_glyphs, use_visual, use_repair, naive=False, needs_live=False):
        self.name = name
        self.use_glyphs = use_glyphs
        self.use_visual = use_visual
        self.use_repair = use_repair
        self.naive = naive
        self.needs_live = needs_live


def configs_for(mode: str) -> list[Config]:
    full_visual = mode == "live"
    out = [
        Config("A only (single pass)", use_glyphs=False, use_visual=False, use_repair=False, naive=True),
        Config("A + B (glyph layer)", use_glyphs=True, use_visual=False, use_repair=False),
    ]
    if full_visual:
        out.append(Config("A + C (render-back)", use_glyphs=False, use_visual=True, use_repair=False))
        out.append(Config("A + B + C + repair (full)", use_glyphs=True, use_visual=True, use_repair=True))
    else:
        # Channel C needs the model, so the offline full system is A + B + repair.
        out.append(Config("A + B + repair (full, offline)", use_glyphs=True,
                          use_visual=False, use_repair=True))
    return out


# ------------------------------------------------------------- evaluation --

def load_pages(gold, loader=None) -> dict:
    """Load each distinct (pdf, page) exactly once.

    Keyed by (pdf, page), not by pdf: a document has many pages, and an
    equation on page 3 must be checked against page 3's glyphs -- not whichever
    page of that document happened to be loaded first.
    """
    if loader is None:
        loader = load_page
    pages = {}
    for eq in gold:
        key = (eq["pdf"], eq["page"])
        if key not in pages:
            pages[key] = loader(os.path.join(ROOT, eq["pdf"]), eq["page"])
    return pages

def _evaluate_one(cfg, eq, reading, gold_latex, page, crop, mode):
    """Run one reading through one config; return (published_latex, status, seconds)."""
    t0 = time.perf_counter()

    if cfg.naive:
        # "A only": whatever the model read is published, unchecked.
        return reading, "verified", time.perf_counter() - t0

    def transcribe(_crop):
        return reading

    repair = None
    if cfg.use_repair:
        if mode == "injected":
            repair = lambda _c, _l, _d: gold_latex      # oracle repair
        else:
            repair = vision.repair

    compare = renderback.compare if (cfg.use_visual and mode == "live") else False
    render = renderback.render_latex if compare else None

    result = verify_equation(
        eq["id"], page, tuple(eq["bbox"]), crop,
        transcribe=transcribe, repair=repair, compare=compare, render=render,
        use_glyphs=cfg.use_glyphs, workdir=os.path.dirname(crop),
    )
    return result.latex, result.status, time.perf_counter() - t0


def run_config(cfg, gold, corpus, pages, crops, mode):
    """Return metrics for one config across the gold and corrupted corpora."""
    tot_time = 0.0
    n_runs = 0
    reviewed = 0          # runs whose status was repaired or withheld (needed review)

    # --- gold readings: failing to reproduce the true equation is a reject --
    gold_total = gold_reject = 0
    for eq in gold:
        published, status, dt = _evaluate_one(cfg, eq, eq["latex"], eq["latex"],
                                              pages[(eq["pdf"], eq["page"])],
                                              crops[eq["id"]], mode)
        tot_time += dt
        n_runs += 1
        gold_total += 1
        if published != eq["latex"]:
            gold_reject += 1
        if status in ("repaired", WITHHELD):
            reviewed += 1

    # --- corrupted readings: publishing a wrong one is a false accept ------
    corrupt_total = false_accept = caught = repaired_to_gold = 0
    for c in corpus:
        eq = next(e for e in gold if e["id"] == c.gold_id)
        published, status, dt = _evaluate_one(cfg, eq, c.read_latex, c.gold_latex,
                                              pages[(eq["pdf"], eq["page"])],
                                              crops[c.gold_id], mode)
        tot_time += dt
        n_runs += 1
        corrupt_total += 1
        if status in PUBLISHED and published != c.gold_latex:
            false_accept += 1
        if status == WITHHELD:
            caught += 1
        if status in ("repaired", WITHHELD):
            reviewed += 1
        if status == "repaired" and published == c.gold_latex:
            repaired_to_gold += 1

    denom_accept = corrupt_total or 1
    denom_reject = gold_total or 1
    # Repair success: of the readings the checks refused on the first pass,
    # how many were then repaired to the correct equation.
    attempted = caught + repaired_to_gold
    return {
        "config": cfg.name,
        "false_accept_rate": round(false_accept / denom_accept, 3),
        "false_reject_rate": round(gold_reject / denom_reject, 3),
        "repair_success_rate": round(repaired_to_gold / attempted, 3) if attempted else None,
        "review_share": round(reviewed / (corrupt_total + gold_total or 1), 3),
        "seconds_per_equation": round(tot_time / n_runs, 3) if n_runs else None,
        "counts": {
            "corrupted": corrupt_total, "false_accept": false_accept,
            "caught": caught, "repaired_to_gold": repaired_to_gold,
            "gold": gold_total, "gold_rejected": gold_reject,
        },
    }


def _corruption_counts(corpus):
    kinds: dict[str, int] = {}
    for c in corpus:
        kinds[c.kind] = kinds.get(c.kind, 0) + 1
    return kinds


def main() -> int:
    ap = argparse.ArgumentParser(description="Legible ablation evaluation")
    ap.add_argument("--injected", action="store_true", help="offline: replay corrupted readings (no API)")
    ap.add_argument("--live", action="store_true", help="use real Muse Spark readings and Channel C")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    if a.injected == a.live:
        print("choose exactly one of --injected or --live", file=sys.stderr)
        return 2
    mode = "injected" if a.injected else "live"

    with open(os.path.join(ROOT, "eval", "gold.json"), encoding="utf-8") as f:
        gold = json.load(f)["equations"]

    # Build crops and load pages once.
    workdir = tempfile.mkdtemp(prefix="legible-eval-")
    pages = load_pages(gold)
    crops = {}
    for eq in gold:
        crops[eq["id"]] = render_crop(
            os.path.join(ROOT, eq["pdf"]), eq["page"], tuple(eq["bbox"]),
            os.path.join(workdir, f"{eq['id']}.png"))

    # The corrupted corpus: one crop per (equation, corruption).
    corpus = build_corpus(gold, seed=a.seed)
    for c in corpus:
        eq = next(e for e in gold if e["id"] == c.gold_id)
        crops[c.id] = render_crop(
            os.path.join(ROOT, eq["pdf"]), eq["page"], tuple(eq["bbox"]),
            os.path.join(workdir, f"{c.id}.png"))

    print(f"mode={mode}  gold={len(gold)}  corruptions={len(corpus)}")
    print("corruption kinds:", _corruption_counts(corpus))

    rows = []
    for cfg in configs_for(mode):
        print(f"\n== {cfg.name} ==")
        row = run_config(cfg, gold, corpus, pages, crops, mode)
        rows.append(row)
        print(json.dumps(row, indent=2))

    results = {
        "mode": mode,
        "repair_model": "oracle (gold) — injected mode" if mode == "injected" else "vision.repair (live)",
        "n_gold": len(gold),
        "n_corruptions": len(corpus),
        "corruption_kinds": _corruption_counts(corpus),
        "rows": rows,
    }
    with open(os.path.join(ROOT, "eval", "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(os.path.join(ROOT, "eval", "results.md"), "w", encoding="utf-8") as f:
        f.write(_markdown(results))
    print("\nwrote eval/results.json and eval/results.md")
    return 0


def _fmt(x):
    return "n/a" if x is None else f"{x:.3f}"


def _markdown(results: dict) -> str:
    lines = [
        "# Legible evaluation",
        "",
        f"- Mode: **{results['mode']}**",
        f"- Repair step: {results['repair_model']}",
        f"- Equations: {results['n_gold']}  ·  injected corruptions: {results['n_corruptions']}",
        f"- Corruption kinds: " + ", ".join(f"{k} x{v}" for k, v in sorted(results["corruption_kinds"].items())),
        "",
        "| Config | False accept | False reject | Repair success | Review share | s/equation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in results["rows"]:
        lines.append(
            f"| {r['config']} | {_fmt(r['false_accept_rate'])} | {_fmt(r['false_reject_rate'])} | "
            f"{_fmt(r['repair_success_rate'])} | {_fmt(r['review_share'])} | {_fmt(r['seconds_per_equation'])} |"
        )
    lines += [
        "",
        "False accept = a corrupted equation was published as if correct.",
        "False reject = a correct equation was withheld.",
        "Repair success = of the readings the checks refused, the share repaired to the correct equation.",
        "Review share = share of equations that were not auto-verified (repaired or withheld).",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
