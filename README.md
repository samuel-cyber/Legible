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

## Scope

Born-digital, single-column PDFs. Scanned pages have no glyph layer, so equations on them can only be verified by the visual check; multi-column layout, charts and diagrams are roadmap.
