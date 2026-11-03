"""Build ground-truth equations from real lecture-note LaTeX source.

            py eval/gold_from_tex.py

For each document it:
  1. extracts the display equations from the .tex (equation, equation*,
     displaymath, \\[..\\], and *single-row* align/align*) in file order;
  2. expands only *trivial* user macros it can resolve safely (\\newcommand /
     \\def with zero or few arguments, bounded recursion);
  3. compiles nothing itself; it reads the PDF compiled from that same source
     and detects display-equation regions with ingest.pdf.find_display_equations;
  4. pairs source equations with detected regions using a reading-order
     alignment: matches must run in the same order on both sides, and a pair is
     kept only when the PDF glyph text plausibly matches the source (the same
     letters/digits). Anything ambiguous is skipped and the reason logged.

It never invents LaTeX and never invents a pairing: every kept entry's `latex`
is copied verbatim (after macro expansion) from the source, and its bbox comes
from the detected region. Existing gold entries (the demo page) are preserved.

Writes eval/gold.json (existing format) and eval/gold_report.md, and prints a
few random kept pairs for a human spot-check.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from equations.glyphs import GlyphLayerUnavailable, glyph_text  # noqa: E402
from ingest.pdf import find_display_equations, load_page  # noqa: E402

# Documents to process: (compiled PDF, LaTeX source, id slug).
DOCS = [
    ("eval/pdfs/lec_notes.pdf", "eval/sources/uh_lecture/lec_notes.tex", "uh"),
    ("eval/pdfs/deriving-navier-stokes.pdf",
     "eval/sources/ff_navierstokes/deriving-navier-stokes.tex", "ffns"),
]

GLYPH_MIN = 0.90           # letters/digits (and letters) agreement to keep a pair
LETTERS_MIN = 0.80         # letters-only agreement, as a second guard
MIN_SIG = 3                # ignore signatures with fewer than this many alphanumerics
MAX_MACRO_PASSES = 12      # bound on macro-expansion recursion

# Recognised equation-number suffix, e.g. "(3.14)" at the end of a glyph line.
_EQNUM = re.compile(r"\(\s*\d+(?:\.\d+)*\s*\)\s*$")


# --------------------------------------------------------------- .tex parse --

def _read_balanced(text: str, i: int) -> tuple[str, int]:
    """Read a balanced {...} group starting at text[i] == '{' (backslash-aware)."""
    assert text[i] == "{"
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return text[i + 1:], len(text)


def collect_macros(text: str) -> dict[str, tuple[int, str]]:
    """Return {name: (n_args, body)} for user macros declared in the preamble."""
    macros: dict[str, tuple[int, str]] = {}

    for m in re.finditer(
            r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)"
            r"\s*\{?\\([A-Za-z@]+)\}?\s*(\[\d+\])?\s*(?:\[[^\]]*\])?\s*\{",
            text):
        name = m.group(1)
        nargs = int(m.group(2)[1:-1]) if m.group(2) else 0
        body, _ = _read_balanced(text, m.end() - 1)
        macros[name] = (nargs, body)

    # \def\x#1#2{...}
    for m in re.finditer(r"\\def\s*\\([A-Za-z@]+)\s*((?:#\d)+)?\s*\{", text):
        name = m.group(1)
        nargs = len(re.findall(r"#\d", m.group(2) or ""))
        body, _ = _read_balanced(text, m.end() - 1)
        macros.setdefault(name, (nargs, body))

    return macros


def _read_macro_args(latex: str, i: int, n: int) -> tuple[list[str], int]:
    """Read n arguments of a macro call starting at index i; return (args, next)."""
    args = []
    j = i
    for _ in range(n):
        while j < len(latex) and latex[j].isspace():
            j += 1
        if j < len(latex) and latex[j] == "{":
            arg, j = _read_balanced(latex, j)
        else:
            arg = latex[j] if j < len(latex) else ""
            j += 1
        args.append(arg)
    return args, j


def expand_macros(latex: str, macros: dict[str, tuple[int, str]]) -> str:
    """Expand user macros, bounded, skipping any that would recurse to themselves."""
    out = latex
    for _ in range(MAX_MACRO_PASSES):
        changed = False
        result = []
        i = 0
        while i < len(out):
            if out[i] == "\\":
                m = re.match(r"\\([A-Za-z@]+)", out[i:])
                if m and m.group(1) in macros:
                    name = m.group(1)
                    nargs, body = macros[name]
                    body_sub = body
                    j = i + m.end()
                    if nargs:
                        args, j = _read_macro_args(out, j, nargs)
                        for k, a in enumerate(args, 1):
                            body_sub = body_sub.replace(f"#{k}", a)
                    # Would self-recurse only if the *whole command* \name appears
                    # again (a prefix like \p inside \partial must not count).
                    if re.search(r"\\" + re.escape(name) + r"(?![A-Za-z@])", body_sub):
                        result.append(out[i:j])
                        changed = True
                        i = j
                        continue
                    result.append(body_sub)
                    changed = True
                    i = j
                    continue
            result.append(out[i])
            i += 1
        out = "".join(result)
        if not changed or "\\" not in out:
            break
    return out


_ENV = re.compile(r"\\begin\{(equation\*?|displaymath|align\*?)\}(.*?)\\end\{\1\}", re.S)
_BRACKET = re.compile(r"\\\[(.*?)\\\]", re.S)


def _align_rows(body: str) -> list[str]:
    """Split an align body into rows on \\\\ and strip alignment marks."""
    rows = body.split("\\\\")
    return [r.replace("&", " ").strip() for r in rows]


def find_equations_tex(text: str) -> list[dict]:
    """Return display-equation candidates in file order with a kind label.

    Single-row align/align* blocks count as one display equation; multi-row
    blocks are returned as a single candidate flagged multi_line so the caller
    can skip them (pairing several rows is unreliable).
    """
    found: list[dict] = []

    for m in _ENV.finditer(text):
        env, body = m.group(1), m.group(2)
        if env.startswith("align"):
            rows = _align_rows(body)
            found.append({"kind": env.rstrip("*"), "latex": rows[0] if rows else body,
                          "pos": m.start(), "multi_line": len(rows) > 1, "rows": len(rows)})
        else:
            found.append({"kind": env, "latex": body, "pos": m.start(),
                          "multi_line": "\\\\" in body, "rows": 1})

    for m in _BRACKET.finditer(text):
        body = m.group(1)
        found.append({"kind": "bracket", "latex": body, "pos": m.start(),
                      "multi_line": False, "rows": 1})

    found.sort(key=lambda d: d["pos"])
    return found


_CLEAN = [
    (re.compile(r"\\label\{[^}]*\}"), ""),
    (re.compile(r"\\tag\{[^}]*\}"), ""),
    (re.compile(r"\\index\{[^}]*\}"), ""),
    (re.compile(r"\\(?:nonumber|notag|displaystyle|quad|qquad)\b"), " "),
]


def clean_latex(latex: str) -> str:
    out = latex
    for pat, rep in _CLEAN:
        out = pat.sub(rep, out)
    return " ".join(out.split())


def is_complex(latex: str) -> str | None:
    """Reason a source equation is unsafe to pair, or None if it is simple."""
    if "\\\\" in latex:
        return "multi-line / aligned"
    m = re.search(r"\\begin\{([^}]*)\}", latex)
    if m:
        return f"nested environment {m.group(1)}"
    return None


# ------------------------------------------------------------- signatures ----

def _letters_digits(s: str) -> set[str]:
    """Set of Latin letters and digits, ignoring LaTeX command names and Greek."""
    no_cmds = re.sub(r"\\[A-Za-z]+", " ", s)     # drop command names (\rho, \frac)
    no_cmds = no_cmds.replace("\\", " ")
    return set(re.findall(r"[A-Za-z0-9]", no_cmds))


def _letters_only(s: str) -> set[str]:
    return set(re.findall(r"[A-Za-z]", re.sub(r"\\[A-Za-z]+", " ", s)))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def glyph_of(pdf: str, page_no: int, bbox) -> str | None:
    """Return the trimmed glyph text for a region, or None if unavailable.

    A trailing equation number like "(3.14)" is stripped so it does not pollute
    the signature. Returns None (rather than raising) when the PDF has no usable
    glyph layer, so the caller can skip the pair cleanly.
    """
    page = load_page(pdf, page_no)
    try:
        text = glyph_text(page, tuple(bbox))
    except GlyphLayerUnavailable:
        return None
    return _EQNUM.sub("", text).strip()


# ------------------------------------------------------------------- build ---

def detected_regions(pdf: str) -> list[dict]:
    """All display-equation regions across the PDF, in page then reading order."""
    import pymupdf
    doc = pymupdf.open(pdf)
    pages = doc.page_count
    doc.close()
    out = []
    for pno in range(pages):
        page = load_page(pdf, pno)
        for bbox in find_display_equations(page):
            out.append({"page": pno, "bbox": bbox})
    return out


def align(source: list[dict], regions: list[dict]) -> tuple[list[tuple[int, int]], list[dict]]:
    """Match source equations to detected regions in reading order.

    Returns (pairs, score) where pairs is a list of (source_index, region_index)
    strictly increasing in both, chosen to maximise glyph agreement. A pair is
    only allowed when the PDF glyph text plausibly matches the source.
    """
    n, m = len(source), len(regions)
    s_sig = [_letters_digits(e["latex"]) for e in source]
    s_let = [_letters_only(e["latex"]) for e in source]
    r_sig = [r["sig"] for r in regions]
    r_let = [r["let"] for r in regions]

    score = [[0] * m for _ in range(n)]
    for i in range(n):
        if len(s_sig[i]) < MIN_SIG:
            continue
        for j in range(m):
            if len(r_sig[j]) < MIN_SIG:
                continue
            ld = _jaccard(s_sig[i], r_sig[j])
            lo = _jaccard(s_let[i], r_let[j])
            if ld >= GLYPH_MIN and lo >= LETTERS_MIN:
                score[i][j] = int(round(ld * 1000))

    # Max-weight increasing matching (each source at most one region, in order).
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        row, prev = dp[i], dp[i - 1]
        for j in range(1, m + 1):
            best = prev[j - 1]
            if score[i - 1][j - 1] and best + score[i - 1][j - 1] > best:
                best = best + score[i - 1][j - 1]
            if prev[j] > best:
                best = prev[j]
            if row[j - 1] > best:
                best = row[j - 1]
            row[j] = best

    pairs: list[tuple[int, int]] = []
    i, j = n, m
    while i > 0 and j > 0:
        sc = score[i - 1][j - 1]
        if sc and dp[i][j] == dp[i - 1][j - 1] + sc:
            pairs.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    return pairs, score


def build_doc(pdf: str, tex: str, slug: str) -> tuple[list[dict], dict]:
    with open(tex, encoding="utf-8") as f:
        text = f.read()
    macros = collect_macros(text)
    candidates = find_equations_tex(text)

    report = {"pdf": pdf, "tex": tex, "kept": [], "skipped": []}

    simple = []
    for c in candidates:
        if c["multi_line"]:
            report["skipped"].append({
                "kind": c["kind"], "reason": f"multi-line ({c['rows']} rows)",
                "latex": clean_latex(c["latex"])[:90]})
            continue
        latex = clean_latex(expand_macros(c["latex"], macros))
        if not latex:
            report["skipped"].append({"kind": c["kind"], "reason": "empty after cleanup",
                                      "latex": ""})
            continue
        reason = is_complex(latex)
        if reason:
            report["skipped"].append({"kind": c["kind"], "reason": reason, "latex": latex[:90]})
            continue
        if len(_letters_digits(latex)) < MIN_SIG:
            report["skipped"].append({"kind": c["kind"],
                                      "reason": "signature too small to verify safely",
                                      "latex": latex[:90]})
            continue
        simple.append({"kind": c["kind"], "latex": latex})

    # Detect regions and cache their glyph signatures once.
    regions = []
    for r in detected_regions(pdf):
        g = glyph_of(pdf, r["page"], r["bbox"])
        if g is None:
            continue
        regions.append({"page": r["page"], "bbox": r["bbox"], "glyph": g,
                        "sig": _letters_digits(g), "let": _letters_only(g)})

    report["counts"] = {"source_simple": len(simple), "detected": len(regions)}

    pairs, _ = align(simple, regions)
    matched_src = {i for i, _ in pairs}
    matched_reg = {j for _, j in pairs}

    kept = []
    for k, (i, j) in enumerate(pairs, 1):
        eq, reg = simple[i], regions[j]
        eq_id = f"{slug}_p{reg['page']}e{k}"
        kept.append({
            "id": eq_id, "pdf": pdf, "page": reg["page"],
            "bbox": [round(float(v), 2) for v in reg["bbox"]], "latex": eq["latex"],
        })
        report["kept"].append({"id": eq_id, "page": reg["page"], "kind": eq["kind"],
                               "latex": eq["latex"], "glyph": reg["glyph"]})

    for i, eq in enumerate(simple):
        if i not in matched_src:
            report["skipped"].append({
                "kind": eq["kind"],
                "reason": "no matching glyph region in reading order",
                "latex": eq["latex"][:90]})

    report["unmatched_regions"] = len(regions) - len(matched_reg)
    return kept, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(ROOT, "eval", "gold.json"))
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()

    with open(a.out, encoding="utf-8") as f:
        existing = json.load(f)["equations"]

    rng = random.Random(a.seed)
    generated_pdfs: set[str] = set()
    new_eqs: list[dict] = []
    reports = []
    for pdf, tex, slug in DOCS:
        paths = (os.path.join(ROOT, pdf), os.path.join(ROOT, tex))
        if not all(os.path.exists(p) for p in paths):
            print(f"! skipping {pdf}: source or PDF missing")
            continue
        kept, rep = build_doc(pdf, tex, slug)
        generated_pdfs.add(pdf)
        new_eqs.extend(kept)
        reports.append(rep)
        c = rep["counts"]
        print(f"{slug:6s} source={c['source_simple']:3d} detected={c['detected']:3d} "
              f"kept={len(kept):3d} skipped={len(rep['skipped']):3d} "
              f"unmatched-regions={rep['unmatched_regions']:3d}")

    # Regeneration is idempotent: drop any existing entry belonging to a document
    # we just rebuilt, keep everything else (the hand-kept demo entries), then add
    # the freshly generated entries (deduped on pdf+page+bbox).
    existing = [e for e in existing if e["pdf"] not in generated_pdfs]

    def key(e):
        return (e["pdf"], e["page"], tuple(round(float(v), 2) for v in e["bbox"]))

    seen = {key(e) for e in existing}
    merged = list(existing) + [e for e in new_eqs if key(e) not in seen]

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"note": (
            "Ground truth for the evaluation. Each entry ties an equation's true "
            "LaTeX to the PDF and page bbox it was read from. Entries under "
            "eval/pdfs/ were generated from the published LaTeX source by "
            "eval/gold_from_tex.py; the demo entries were transcribed with the "
            "source in demo/pages/fluids.tex."), "equations": merged}, f,
            indent=2, ensure_ascii=False)

    _write_report(reports, existing, new_eqs)
    print(f"\nwrote {a.out}: {len(existing)} existing + {len(new_eqs)} new = {len(merged)} equations")

    if new_eqs and a.sample:
        print(f"\n--- {min(a.sample, len(new_eqs))} random kept pairs (seed={a.seed}) ---")
        for e in rng.sample(new_eqs, min(a.sample, len(new_eqs))):
            g = glyph_text(load_page(os.path.join(ROOT, e["pdf"]), e["page"]), tuple(e["bbox"]))
            print(f"\n[{e['id']}]  page {e['page']}  bbox {e['bbox']}")
            print(f"  source latex: {e['latex']}")
            print(f"  glyph text  : {g}")
    return 0


def _write_report(reports, existing, new_eqs) -> None:
    lines = ["# Gold set built from LaTeX source", "",
             f"Existing (hand-kept) entries preserved: {len(existing)}  ·  "
             f"generated from source: {len(new_eqs)}", "",
             "Source equations are paired with detected PDF regions by a "
             "reading-order alignment (matching pairs must run in the same order "
             "on both sides); a pair is kept only when the PDF glyph letters and "
             "digits plausibly match the source. Everything else is skipped, "
             "fail-closed.", ""]
    for rep in reports:
        c = rep["counts"]
        lines.append(f"## {os.path.basename(rep['pdf'])}")
        lines.append("")
        lines.append(f"- Source: `{rep['tex']}`")
        lines.append(
            f"- Simple source equations: **{c['source_simple']}**  ·  "
            f"detected regions: **{c['detected']}**  ·  kept: **{len(rep['kept'])}**  ·  "
            f"unmatched regions (prose/fragments): **{rep['unmatched_regions']}**")
        lines.append("")
        if rep["kept"]:
            lines.append("| id | page | kind | LaTeX | PDF glyph text |")
            lines.append("| --- | --- | --- | --- | --- |")
            for k in rep["kept"]:
                tex = k["latex"].replace("|", "\\|")
                gl = k["glyph"].replace("|", "\\|")
                lines.append(f"| {k['id']} | {k['page']} | {k['kind']} | `{tex}` | `{gl}` |")
            lines.append("")
        if rep["skipped"]:
            lines.append(f"### Skipped ({len(rep['skipped'])})")
            lines.append("")
            lines.append("| kind | reason | LaTeX |")
            lines.append("| --- | --- | --- |")
            for s in rep["skipped"]:
                tex = (s.get("latex") or "").replace("|", "\\|")
                lines.append(f"| {s['kind']} | {s['reason']} | `{tex}` |")
            lines.append("")
    with open(os.path.join(ROOT, "eval", "gold_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
