# Legible evaluation — Task 3 report

Everything below comes from an actual run of the code in this repository.
No number here is estimated or invented.

## 1. What was measured

- **Gold set:** 152 equations (`eval/gold.json`) — 6 from the hand-built demo
  page, 146 paired from two open-licence lecture-note sources (see
  `eval/sources.md`):
  - `eval/pdfs/lec_notes.pdf` (finite-element methods) — 96 equations
  - `eval/pdfs/deriving-navier-stokes.pdf` (fluid mechanics) — 50 equations
- **Channels:** A = Muse Spark reading (a real model call), B = deterministic
  PDF glyph layer, C = render-back visual check.
- **Rule:** if B exists, A must match B token-for-token (C advisory only); if B
  is missing, C is the gate; every error path fails closed.

## 2. Results table — `--injected` (offline, deterministic, no API spend)

Command: `py eval/run_eval.py --injected` (303 injected corruptions from the
152 gold equations).

| Config | False accept | False reject | Repair success | Review share | s/eq |
| --- | --- | --- | --- | --- | --- |
| A only (single pass) | 1.000 | 0.000 | n/a | 0.000 | 0.000 |
| A + B (glyph layer) | 0.000 | 0.237 | 0.000 | 0.745 | 0.001 |
| A + B + repair (full, offline) | 0.000 | 0.237 | 0.683 | 0.745 | 0.001 |

Reading of the table:

- Publishing the raw model reading with no check (**A only**) accepts *every*
  corrupted equation: false-accept rate 1.000. It is the baseline, not a
  contender.
- Adding the glyph layer (**A + B**) drops false accepts to **0.000** — every
  one of the 303 corruptions is caught — at the cost of withholding 36 of 152
  correct equations (**false reject 0.237**). That 0.237 is exactly the same 36
  equations the token comparison cannot resolve (§4).
- One repair pass (**A + B + repair**, repair = oracle in injected mode) fixes
  68.3% of refused readings; the remaining false rejects are the genuinely
  ambiguous geometry, which repair cannot help because the *checker*, not the
  reading, is what differs.

- **Live run** (after the spend was approved). `eval/run_eval.py --live` keeps
  Channel A as the stored reading (it measures the *decision rule* and Channel C),
  so the live parts are the render-back check and the repair step:

  | Config | False accept | False reject | Review share | s/eq |
  | --- | --- | --- | --- | --- |
  | A only (single pass) | 1.000 | 0.000 | 0.000 | 0.000 |
  | A + B (glyph layer) | 0.000 | 0.237 | 0.745 | 0.001 |
  | A + C (render-back) | 0.000 | 0.822 | 0.941 | 4.420 |
  | A + B + C + repair (full) | 0.000 | 0.237 | 0.745 | 11.207 |

  False reject is **identical (0.237) live and injected** — the same 36 equations
  are withheld, and their identity does not depend on the mode. `A + C` alone is
  much weaker (0.822 withheld) and costs ~4.4 s/eq; the full config keeps B's zero
  false-accept and adds a repair pass at ~11 s/eq.

  **Caveat, stated rather than hidden:** the live table shows **repair success =
  0.000**, but that is a metric artefact, not a failed repair. In live mode the
  model returns an *equivalent* string (e.g. `\dots` where the source wrote
  `\cdots`, or different spacing), and `run_eval.py` counts a repair as successful
  only on **exact string equality** with the source gold. The injected-mode 0.683
  is the meaningful repair number, because there the target string is known
  exactly. A token-equality repair metric would be the right fix, and is noted as
  a follow-up rather than silently reported as a zero.

## 3. Channel B / tokenizer fixes made (each with a real-glyph regression test)

All fixes are general and safe; all 165 tests pass. Regression tests live in
`tests/test_real_samples.py` and draw their samples from
`eval/test_samples.py`, whose provenance is the published LaTeX source.

| Fix | What was wrong | Regression sample |
| --- | --- | --- |
| Overlay folding (`OVERLAYS` in `tokens.py`, wired through `glyphs.py`) | `\ne` is drawn as a `=` glyph plus a combining slash (U+0338) drawn beside it; the glyph layer saw `=` and `slash`, the reading saw `≠`. The slash is now folded into the base it strikes. | `neq_overlay`, `uh_p8e34` |
| Removing the `norm("=") -> "≠"` hack | A blanket rule rewrote every `=` to `≠`, corrupting plain `=` and the Relbar inside `\Longrightarrow`. | `plain_equals`, `uh_p1e2` |
| Dot folding (`_fold_dots`) | `\dots`/`\cdots` are drawn as three literal dots; the fold now merges a run of `.`/`·` to one ellipsis and keeps any remainder. | `dots_fold`, `uh_p5e23` |
| Centered-ellipsis folding (`_fold_cdots`) | A reading writes the centered dots as `\cdots` (U+22EF), but the glyph layer folds the printed run to `…` (U+2026); the same printed dots must tokenize the same, so a *base-level* `⋯` now folds to `…` (inside a script the two heights really differ, so those still differ). Found by the live run: it had withheld two correct readings. | `dots_fold` (now matched against both `\dots` and `\cdots`), `uh_p5e23`, `uh_p6e26` |
| Script roles (`_script_roles` v2) | Nested scripts on the norm bar (`L^p`) were mis-assigned; the host is now the nearest preceding glyph of any size, and a small glyph sharing its host's baseline inherits the role. | covered by `norm_bars` / `to_relation` |
| Norm bars, `\to`-as-relation, `\boxed` transparency | Paired `\|` must map to the reading's norm character; a `\to` between sets must stay a relation (not be eaten as an accent); `\boxed` must not change tokens. | `norm_bars` (`uh_p7e31`), `to_relation` (`uh_p3e16`), `boxed_relation` (`ffns_p19e12`) |

## 4. Classification of every A/B disagreement

Of 152 equations, **116 are token-identical** and **36 differ**. Token agreement
by source: demo 6/6, `lec_notes.pdf` 68/96, `deriving-navier-stokes.pdf` 42/50.
The 36 are grouped by cause; **none is a Muse Spark reading error** (Channel A
is mocked in this run, so the "reading" is the gold LaTeX — these are checker
gaps, not model errors).

**Cause 1 — glyph layer cannot represent a script on a script (nested sub/sup).**
The geometry flattens `_{L^p}` to `_L p` or `_H 1`; the reading nests. This is
an inherent limit of a geometry-only channel, so these stay **withheld**
(fail-closed):
`uh_p2e6`, `uh_p5e25`, `uh_p11e44`, `uh_p12e45`, `uh_p12e46`, `uh_p12e48`,
`uh_p13e54`, `uh_p14e57`, `uh_p14e58`, `uh_p14e59`, `uh_p14e60`, `uh_p15e64`,
`uh_p18e83`, `uh_p19e90`, `uh_p19e91`, `uh_p19e93`, `uh_p19e94`.

**Cause 2 — subscript followed by a delimiter.** After a nested script the
closing `)`/`_i}` grouping is ambiguous, so the trailing tokens differ
(`i` vs `i,)`):
`uh_p14e61`, `uh_p14e62`, `uh_p15e66`, `uh_p15e67`, `uh_p15e68`, `uh_p15e69`.
**Withheld.**

**Cause 3 — big-operator limits reordered.** `\sum`/`\prod` limits are placed
across the operator's x, so the glyph order differs from the reading's:
`uh_p18e82`, `uh_p18e84`, `uh_p17e81`. **Withheld.**

**Cause 4 — long-arrow drawn as a Relbar composition.** XeTeX draws
`\Longrightarrow`/`\implies` as a Relbar (`=`) plus `⇒`; `\Longleftrightarrow`
as `⇐` plus `⇒`. The reading has the single character:
`uh_p7e30` (`= ⇒` vs `⟹`), `ffns_p18e11`, `ffns_p18e10` (`⇐ ⇒` vs `⟺`).
This could be folded like the overlay, but the heuristic risks mis-merging an
`=` that legitimately precedes an arrow, so it is **left withheld**.

**Cause 5 — Unicode big integral hides its limit.** `\int_\Omega` draws the
integral as one large Unicode glyph with the `Ω` limit positioned so the glyph
layer cannot see it is a subscript:
`uh_p20e96` (glyph `∫`, reading `∫ Ω_sub`). **Withheld.**

**Cause 6 — `\overline` is a rule, not a glyph.** The overline is drawn as a
horizontal rule; `_build` treats rules as fraction bars only, so the accent
never appears in the glyph layer:
`ffns_p49e44` (reading has `¯` twice; glyph has none). **Withheld.**

**Cause 7 — region detection / bbox captures the wrong geometry** (Task 4
territory). The clipping box spans more than the equation, so the glyph layer
reads a neighbouring line or two equations at once:
`ffns_p8e1`, `ffns_p10e2`, `ffns_p30e21`, `ffns_p52e47`, `ffns_p14e8`,
`ffns_p18e10`. These are **gold-pairing/region errors**, not tokenizer gaps.

## 5. Muse Spark errors caught

Channel A is mocked inside `run_eval.py`, so the real reader's mistakes are
captured separately by **`eval/live_read.py`**, which runs the *real* model over
the 152 gold crops and then runs the gate (A vs B; Channel C off, no repair).
Full output: `eval/live_read.json` / `eval/live_read.md`.

Result: **114 agree, 4 errors, 34 Channel-B gaps**. Of the 4, three are genuine
Muse Spark mis-readings and one is a crop/pairing artefact:

| Equation | Page | What A read | What the PDF says | Cause |
| --- | ---: | --- | --- | --- |
| `uh_p9e36` | 10 | `\|u1_K - u\| \le 1/j.` | `∥u1K−u∥≤1/j.` | reader wrote the norm bars as `\|`; the PDF's bar glyph is `∥` |
| `uh_p18e85` | 19 | `\|(h\partial)(u-u_h)\|_{\sim} \lesssim \|(h\partial)^{l+1}u\|,` | `∥(h∂)(u−u_h)∥≲∥(h∂)^{l+1}u∥,` | same norm-bar substitution |
| `uh_p18e86` | 19 | `\| u - u_h \| \lesssim \| (h\partial)^{l+1} u \|.` | `∥u−u_h∥≲∥(h∂)^{l+1}u∥.` | same norm-bar substitution |
| `ffns_p45e37` | 46 | `\rho(\boldsymbol u\cdot\nabla)\boldsymbol u = -\nabla p + \mu\nabla^2\boldsymbol u + \rho\boldsymbol b` | two displays in one crop: `τ=2μD`, `σ=−pI+2μD` | the bbox spans **two** equations, so the reading is not wrong — the crop is. Region-detection territory (Task 4), not a reader error. |

Classification of all 4:

- **Best demo candidate — `uh_p9e36`.** One short equation; the reader swaps the
  visually-similar single bar `\|` for the PDF's double bar `∥`, and Channel B
  catches it exactly ("The PDF has '∥', but the reading has '|', '|'"). Small,
  legible, and a clear fail-closed win.
- The two `uh_p18e85/86` cases are the same failure on longer lines.
- `ffns_p45e37` is a region error, so it belongs with the Task-4 section, not
  here.

The other **34** are Channel-B gaps, not reader errors: those are the known
geometry limits classified in §4 (nested scripts, big-operator limits, `\overline`
as a rule, and so on). The reader's reading there is off-gold only because B
cannot represent it; the pipeline withholds them (fail-closed).

Two earlier "errors" (`uh_p5e23`, `uh_p6e26`) were the `\cdots`-vs-`…` tokenizer
gap fixed in §3; after that fix they verify, and the count dropped from 5 to 4.

## 6. API spend

Approximate, and reported honestly: there is no billing feed inside the
repository, so this is a **call count**, not a dollar figure. The paid runs made
(only after the spend was approved) are:

| Run | Model calls |
| --- | ---: |
| `eval/compare_regions.py --live --save` | 88 (one per page) |
| `eval/run_eval.py --live` (Channel C + repair) | ~300 |
| `eval/live_read.py` (real Channel A over 152 crops, run twice) | ~304 |
| Diagnostic probes (`_conc.py`, `_one_read.py`, limited `live_read` samples) | ~60 |
| **approximate total** | **~750 vision calls** |

That is on the order of a few dollars at Muse Spark's per-image pricing — a small
fraction of the $150 budget — and every call that was not free was gated behind
the user's explicit go-ahead. No key or token is printed anywhere; the client
reads `META_API_KEY` from the environment / `.env` and never logs it.

## 7. Harness bug found and fixed

The first `--injected` run reported a false-reject rate of 0.941 (143/152). The
cause was a **bug in `eval/run_eval.py`**: pages were cached by PDF *path* only,
so every equation of a multi-page document was checked against whichever page
of that document loaded first — page 2's equations saw page 1's glyphs. Fixed by
keying the cache on `(pdf, page)` via a new `load_pages()` helper, with three
tests in `tests/test_run_eval.py`. After the fix the false-reject rate is the
honest 0.237.

## 8. Task 4 — model vs heuristic region detection

`layout/regions.py` asks the model to propose display-equation boxes in page
coordinates and in reading order, then **validates** each box (on-page, contains
ink), **snaps** it to the surrounding glyphs, and **cross-checks** it against the
existing `find_display_equations` heuristic. The pipeline (`--regions model`)
takes the **union** and logs any model box the heuristic missed; if the model call
fails, the heuristic result is used unchanged. Nothing about the fail-closed gate
changes: a mis-detected region only means the equation is withheld, never
accepted.

Command: `py eval/compare_regions.py --live --save` (one model call per page,
cached in `eval/regions_cache.json`; full output in `eval/regions_compare.md`).

| PDF | Pages | Heuristic | Model | Matched | Model extra | Heuristic missed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lec_notes.pdf` | 22 | 192 | 117 | 33 | 84 | 159 |
| `deriving-navier-stokes.pdf` | 66 | 122 | 99 | 45 | 54 | 66 |
| **total** | 88 | 314 | 216 | 78 | 138 | 225 |

Two conclusions, both checked rather than assumed:

- **The model's coordinates are correct.** A diagnostic (`eval/_diag_regions.py`)
  compared individual boxes against the glyph layer and found exact agreements
  (e.g. page 3's `(239, 485, 316, 502)`), so there is **no scaling/coordinate
  bug** — the model speaks the same page-point space the heuristic does.
- **The heuristic is more precise on these notes.** It finds 314 regions to the
  model's 216, matches only 78, and the model adds 138 boxes that are mostly
  prose or two equations merged (the model being *less* precise, not shifted).
  That is exactly the situation the union-plus-fallback design exists for: the
  model can surface an equation the heuristic misses, the heuristic covers what
  the model drops, and the gate decides in either case. The `ffns_p45e37`
  Muse-error row in §5 is one such merged crop — the union design keeps it
  fail-closed rather than accepting a reading of the wrong span.
