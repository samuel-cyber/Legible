# Legible

**Verified STEM accessibility.** Legible turns engineering lecture PDFs into screen-reader-accessible HTML, and refuses to publish any equation it cannot prove matches the source.

Built for the Meta Global AI Developer Hackathon (building period Oct 27 – Nov 4, 2026). All code in this repository was written during the hackathon.

## How it works

Every equation is checked by three evidence channels that fail in different ways:

| Channel | Source | Model? |
| --- | --- | --- |
| A · Vision reading | Muse Spark transcribes the equation image to LaTeX | Yes |
| B · Glyph layer | The PDF's own characters, positions and fraction bars, rebuilt into structure | No |
| C · Render-back | The reading is re-typeset and Muse Spark lists differences against the original | Yes |

A's LaTeX and B's glyph structure are reduced to the same role-tagged token form (symbol + numerator/denominator/superscript/subscript context) and diffed deterministically.

The decision rule depends on whether the glyph layer exists:

**When B is available** (born-digital page), B is the gate and C is *advisory*:

- **Verified**: A matches B exactly → published as MathML. C still runs, but if it flags a difference the finding is recorded and shown as an advisory note ("visual check flagged X; the glyph layer confirmed the reading") — it does not withhold.
- **Repaired**: A and B disagree, so Muse Spark re-reads once, told exactly where the disagreement is, and the new reading matches B.
- **Withheld**: still disagrees with B after one repair → announced as "unverified equation", never read as math — regardless of what C says.

**When B is unavailable** (scanned page / image equation), C is the gate:

- **Verified**: C finds no differences.
- **Repaired / Withheld**: as above, driven by C instead of B.
- **Withheld (fail-closed)**: C errors or returns unparseable output counts as a failure, so the equation is withheld rather than trusted.

Why: measured against real runs, C is a much weaker signal than the exact, deterministic glyph layer. Two different renderers never agree on letterforms, so C misses or invents differences. Letting an over-eager (or unavailable) C withhold a reading that provably matches the PDF's own characters only produces false rejects. When B is absent there is nothing exact to fall back on, so C is used as a gate and still fails closed.

Either way, a model error in A means withheld; a model error in C can never, on its own, cause a verification.

The variable glossary under each equation is quoted verbatim from the document's own "where ..." sentence.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env        # add your Meta Model API key
python pipeline.py demo/pages/fluids.pdf out/fluids
```

Offline test mode (no API key; readings come from a JSON file, everything else is the real pipeline):

```bash
python pipeline.py demo/pages/fluids.pdf out/fluids --replay demo/replay_fluids.json
```

Outputs `out/fluids/index.html` (the accessible page) and `out/fluids/report.html` (the verification report).

### Web app

```bash
uvicorn app.main:app --reload
```

Opens an upload UI at `http://127.0.0.1:8000`: pick a PDF, watch per-equation
progress stream in, then open the accessible page or the verification
report. See `DEPLOY.md` for deploying this to Render or Hugging Face Spaces.

## Harder page

`demo/hard/` is a second page with constructs the first one does not have:
partial derivatives, a definite integral, a summation, a radical whose radicand
is a fraction, multi-letter subscripts and an accent. It is typeset directly
with PyMuPDF, so it needs no LaTeX toolchain, yet the glyph layer, baselines
and fraction bars are real and Channel B runs on it unmodified.

```bash
py demo/hard/build.py                                              # writes hard.pdf + replay.json
py pipeline.py demo/hard/hard.pdf out/hard --replay demo/hard/replay.json
py demo/hard/report.py                                             # writes demo/hard/REPORT.md
```

Channel B verifies the integral, summation, radical, partials, accent and
nested fraction, and withholds `\binom` and `\lfloor` — macros the token
vocabulary cannot represent, so they fail closed. `demo/hard/REPORT.md` is the
generated evidence.

## Layout

```
ingest/      PDF glyphs, rules, crops (PyMuPDF)
equations/   tokens.py (shared token form + diff), glyphs.py (Channel B),
             vision.py (Channel A + repair), renderback.py (Channel C), decide.py (decision rule)
assemble/    reading-order layout, glossary, MathML, HTML templates
clients/     Meta Model API client (OpenAI-compatible)
eval/        error injection and ablation
```

## Results

Measured against a 152-equation gold set: the 6-equation demo page plus 146
equations drawn from two CC-BY lecture-note PDFs (`eval/pdfs/lec_notes.pdf`,
finite-element methods, 96 equations; `eval/pdfs/deriving-navier-stokes.pdf`,
fluid mechanics, 50 equations). Every number below comes from an actual run
of the code in this repository — full methodology in `eval/EVAL_REPORT.md`.

| | False accept | False reject |
| --- | --- | --- |
| No verification (raw reading published as-is) | 100% (303/303 injected errors published) | 0% |
| With verification (glyph-layer gate) | **0%** (0/303 injected errors published) | 23.7% (36/152 correct equations withheld) |

- **Zero false accepts**, with or without a repair pass. All 303 injected
  corruptions (sign flips, wrong exponents, swapped subscripts, dropped
  terms, Greek-letter swaps, inverted fractions, …) across all 152 gold
  equations were caught.
- **False-reject rate: 23.7%** (36/152) — the *same* 36 equations whether
  Channel A's reading is a stored string or a live Muse Spark call. Every one
  is the glyph layer hitting a genuine geometric limit (see Scope below), not
  a mistaken rejection of an ordinary equation.
- **Real Muse Spark errors, caught:** running the live model over all 152
  real crops (Channel C off, no repair) found 114 agreements and 4
  disagreements. Three are genuine reading mistakes — in each, the model
  wrote a visually similar bar (`\|` or `||`) where the PDF's own glyph was
  the norm symbol `∥`, a meaning-changing substitution, and the glyph-layer
  check withheld all three rather than publish a different symbol as the
  same one. The fourth is a region-detection artefact (a crop spanning two
  separate equations), not a reading error.
- **Repair:** one guided re-read, told exactly what disagreed, fixed 68.3% of
  the equations the first pass flagged, measured offline where the target
  reading is known exactly (an oracle repair — see `eval/EVAL_REPORT.md` for
  why the live repair-success metric reads 0%: a token-equality bug in the
  *metric*, not a failed repair).

## Scope

Born-digital PDFs with a real text layer. Scanned pages have no glyph layer,
so Channel C's visual check has to carry verification alone — a much weaker
signal, measured at 82.2% false-reject in that configuration (vs. 23.7% with
the glyph layer). Multi-column layout, charts and diagrams are roadmap.

The glyph layer (Channel B) is pure geometry — symbol size and position, no
model — so it cannot yet represent every construct. All 36 of the equations
above that are withheld despite being correct come from one of these, each
confirmed against real glyph samples (`eval/EVAL_REPORT.md` §4):

- a superscript nested inside a subscript or vice versa, e.g. `L^p(I)` as a
  subscript (17 of 36) — the dominant gap, and the one we looked hardest at
  fixing; it needs the script-role tracker to carry a real baseline per
  nesting level rather than compare each glyph only to its immediate
  neighbour, which is a bigger change than we were willing to risk this late
  without new false accepts, so it stays a documented limit
- a subscript immediately followed by a closing delimiter, which inherits the
  same ambiguity (6)
- a big operator (`\sum`, `\prod`) whose limit glyphs interleave with the
  operator symbol in raw print order (3)
- `\overline` drawn as a rule rather than a glyph (1)
- a Unicode integral glyph whose limit is visually absorbed into the symbol (1)
- `\Longrightarrow`-style long arrows drawn as two component glyphs — left
  withheld on purpose, since folding it risks silently merging an unrelated
  `=` that happens to precede an arrow (2)

That accounts for 30 of the 36. The remaining 6 are a different kind of gap —
region detection, not the token vocabulary: the equation's bounding box
captured a neighbouring line or two equations at once, so the glyph layer
read the wrong span. That is `layout/regions.py`'s territory (model-proposed
boxes unioned with the heuristic, see `eval/EVAL_REPORT.md` §8), not a
tokenizer limit.

None of these 36 produce a false accept: every one fails closed and is
withheld rather than guessed.
