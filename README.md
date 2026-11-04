# Legible

**Verified STEM accessibility.** Legible turns engineering lecture PDFs into screen-reader-accessible HTML, and refuses to publish any equation it cannot independently verify against the source.

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

Why: measured against real runs, C is a much weaker signal than the exact, deterministic glyph layer. Two different renderers never agree on letterforms, so C misses or invents differences. Letting an over-eager (or unavailable) C withhold a reading that is independently verified against the PDF's own characters only produces false rejects. When B is absent there is nothing exact to fall back on, so C is used as a gate and still fails closed.

Either way, a model error in A means withheld; a model error in C can never, on its own, cause a verification.

The variable glossary under each equation is quoted verbatim from the document's own "where ..." sentence.

### Ask about this equation

Every verified or repaired equation on the student page has a labelled
"Ask about this equation" box. It answers from that equation's own verified
token structure only — numerator/denominator, the exponent or subscript of
a symbol, what's inside a bracket, a slow one-part-at-a-time reading, or a
symbol's meaning from the quoted glossary — and nothing else: no model call
is made anywhere in this feature (`equations/ask.py`), and a question it
can't parse gets a fixed refusal rather than a guess. It never appears on a
withheld equation, because there's no independently-verified structure to
answer from.

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

## Trust levels

Legible reports two distinct trust levels, and the status badge always says
which one an equation got:

- **verified / repaired** — born-digital pages. The reading is independently
  verified against the PDF's own text layer (see Results above): 0% false
  accept, 23.7% false reject, measured on 152 real equations.
- **ai_read** — scanned or handwritten pages (`ingest/scan.py` detects these:
  no text layer at all, or a page dominated by one raster image even if an
  OCR layer sits on top). There are no stored characters to check against, so
  an equation here can be *read* but never *independently verified* — status
  is "ai_read", never "verified", however clean the reading looks. Channel C
  (render-back) and any OCR text inside the region are cautions only; neither
  can withhold or verify an ai_read equation. The only way to withhold here
  is Channel A itself failing or returning invalid LaTeX.

**Measured accuracy (live Muse Spark, image-only fluids demo page):** the
page was rasterized to a single embedded image with zero text layer
(`demo/scans/build.py`), run through the real pipeline end to end, and every
reading compared against the same gold LaTeX used throughout this README.
**Result: 6/6 equations read exactly correctly.**

That number came from real debugging, not a lucky first run, worth stating
honestly: the first live attempt found 0/6 usable readings — the
region-proposal model's box coordinates drifted further off the true
position the lower it looked on the page (a few points at the top, tens of
points by the bottom), because at the default render resolution a rasterized
page gives it far less to work with than the clean vector text the same
model-region code already handles well on a born-digital page. Rendering the
proposal image at a higher zoom (4.0 instead of 2.0) fixed the drift to a
few points everywhere; padding each proposed box by 15pt before snapping to
ink fixed two remaining equations that were cut off by one trailing symbol.
Both fixes are specific to the scanned path only — the born-digital region
finder is untouched and its own tests still pass unchanged.

**Measured accuracy (live Muse Spark, real handwritten notes,
`demo/scans/handwritten.pdf`):** one page, 5 equations, hand-scored against
an answer key. All 5 were found and all 5 came back as recognizable,
correct equations — no garbled or nonsense readings. Scored strictly
(matching in meaning, not just "looks close"):

| Eq | Read | Verdict |
| --- | --- | --- |
| 1 | `p/(ρg) + V^2/2g + z = H` | Right, one case substitution: v → V |
| 2 | `A_1 V_1 = A_2 V_2` | Right, same v → V substitution (both) |
| 3 | `R_e = ρvD/μ` | **Exact.** μ read correctly, *not* misread as "m" |
| 4 | `p = p_0 + ρgh` | **Exact** |
| 5 | `h_f = F(L/D)(V^2/2g)` | Right (F and brackets both accepted per the answer key), same v → V substitution |

**2 of 5 exact, 3 of 5 right with one recurring, labelled substitution, 0
wrong or unreadable.** The v → V pattern is not a model error to paper over:
checked against the actual handwriting crop, this person's cursive "v" is
tall and symmetric and genuinely reads as a capital V — the model's
transcription is a defensible reading of what is actually on the page, and
it was consistent across every occurrence rather than random. Separately,
Channel C earned its keep here: on equation 5 it flagged "the original has
10 but the re-typeset version has D" — checked against the crop, the
handwritten denominator really is ambiguous between "D" and "10", and the
model's reading (D, the contextually correct one for this formula) is
shown with that caution attached rather than asserted as certain. Neither
the v/V pattern nor the D/10 caution blocked anything, exactly as designed:
ai_read publishes its best reading and surfaces what's uncertain, never
withholding over an unproven visual check.

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
