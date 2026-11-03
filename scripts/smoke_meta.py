"""Live API smoke test for Legible.

Sends one equation crop through the three real channels and prints what each
one produced. Use it to confirm your Meta Model API credentials and that Muse
Spark returns parseable LaTeX, before running the full pipeline.

    py scripts/smoke_meta.py                       # first crop in out/fluids/crops
    py scripts/smoke_meta.py out/fluids/crops/p1e1.png
    py scripts/smoke_meta.py --route baseten       # open-weight route

It exits non-zero with a clear message on any problem: missing environment
variables, an auth failure, or JSON the model would not return in a parseable
form (after ask_json's single retry).
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

# Make the repo root importable when run as a script.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from clients import meta  # noqa: E402
from equations import renderback, vision  # noqa: E402
from equations.decide import verify_equation  # noqa: E402
from ingest.pdf import find_display_equations, load_page  # noqa: E402

DEFAULT_PDF = os.path.join(ROOT, "demo", "pages", "fluids.pdf")
DEFAULT_CROPS = os.path.join(ROOT, "out", "fluids", "crops")


def _fail(msg: str, code: int = 1):
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _pick_crop(arg: str | None) -> str:
    if arg:
        if not os.path.exists(arg):
            _fail(f"crop not found: {arg}")
        return arg
    hits = sorted(glob.glob(os.path.join(DEFAULT_CROPS, "*.png")))
    if not hits:
        _fail(
            f"no crops in {DEFAULT_CROPS}. Run first:\n"
            f"    py pipeline.py demo/pages/fluids.pdf out/fluids --replay demo/replay_fluids.json"
        )
    return hits[0]


def _page_and_bbox_for(crop: str):
    """Find which demo equation a crop belongs to, so we can run Channel B."""
    eq_id = os.path.splitext(os.path.basename(crop))[0]
    if not os.path.exists(DEFAULT_PDF):
        return None, None, eq_id
    page = load_page(DEFAULT_PDF, 0)
    boxes = find_display_equations(page)
    for i, bbox in enumerate(boxes):
        if f"p1e{i + 1}" == eq_id:
            return page, bbox, eq_id
    return page, None, eq_id


def main() -> int:
    ap = argparse.ArgumentParser(description="Live Muse Spark smoke test")
    ap.add_argument("crop", nargs="?", help="path to an equation crop PNG")
    ap.add_argument("--route", default="meta", choices=["meta", "baseten"])
    a = ap.parse_args()

    # ---- 1. environment ---------------------------------------------------
    key_var = "BASETEN_API_KEY" if a.route == "baseten" else "META_API_KEY"
    url_var = "BASETEN_BASE_URL" if a.route == "baseten" else "META_BASE_URL"
    missing = [v for v in (key_var, url_var) if not os.getenv(v)]
    if missing:
        print("Environment check:", file=sys.stderr)
        for v in (key_var, url_var):
            print(f"  {v}: {'set' if os.getenv(v) else 'MISSING'}", file=sys.stderr)
        print(
            "\nSet the missing variables in your .env file (see README / the Meta "
            "quickstart for the base URL and model id), then re-run.",
            file=sys.stderr,
        )
        return 2
    print(f"route={a.route}  model={meta.model_name(a.route)}")
    print(f"{key_var}=set  {url_var}={os.getenv(url_var)}")

    if not meta.available(a.route):
        _fail(f"meta.available() is False for route {a.route} (bad key or base URL)")

    crop = _pick_crop(a.crop)
    print(f"\ncrop: {crop}")

    # ---- 2. Channel A: transcribe ----------------------------------------
    print("\n[Channel A] transcribing ...")
    try:
        latex = vision.transcribe(crop, route=a.route)
    except meta.BadModelJSON as e:
        _fail(f"Channel A returned unparseable JSON: {e}")
    except Exception as e:  # auth, network, quota, ...
        _fail(f"Channel A call failed: {type(e).__name__}: {e}")
    print(f"  latex = {latex!r}")

    # ---- 3. Channel B: glyphs, and the whole decision rule ---------------
    page, bbox, eq_id = _page_and_bbox_for(crop)
    if page is None or bbox is None:
        print("\n[Channel B] skipped: no matching demo bbox for this crop")
        print("  (Channel B is exercised by tests/test_glyphs.py)")
    else:
        print(f"\n[Channel B] rebuilding structure for {eq_id} ...")

    print("\n[full decision rule] verify_equation with A + B + C ...")
    try:
        result = verify_equation(
            eq_id, page, bbox, crop,
            transcribe=lambda c: vision.transcribe(c, route=a.route),
            repair=lambda c, l, d: vision.repair(c, l, d, route=a.route),
            compare=lambda c, r: renderback.compare(c, r, route=a.route),
            render=renderback.render_latex,
            use_glyphs=page is not None and bbox is not None,
            workdir=os.path.dirname(crop) or ".",
        )
    except meta.BadModelJSON as e:
        _fail(f"a channel returned unparseable JSON: {e}")
    except Exception as e:
        _fail(f"verify_equation failed: {type(e).__name__}: {e}")

    print(f"  status   = {result.status}")
    print(f"  channels = {result.channels}")
    print(f"  latex    = {result.latex!r}")
    print(f"  glyphs   = {result.glyph_form!r}")
    print(f"  raw text = {result.raw_text!r}")
    print(f"  why      = {result.explanation}")
    for i, att in enumerate(result.attempts):
        print(f"  attempt {i + 1}: latex={att.latex!r}")
        for d in att.glyph_diffs:
            print(f"    B: {d}")
        for d in att.visual_diffs:
            print(f"    C: {d}")
        if att.parse_error:
            print(f"    parse: {att.parse_error}")

    print("\nOK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
