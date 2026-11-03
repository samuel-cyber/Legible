# Legible evaluation

- Mode: **live**
- Repair step: vision.repair (live)
- Equations: 152  ·  injected corruptions: 303
- Corruption kinds: digit x54, dropped accent x1, dropped term x33, exponent x51, greek swap x27, inverted fraction x21, sign flip x66, swapped subscript x50

| Config | False accept | False reject | Repair success | Review share | s/equation |
| --- | --- | --- | --- | --- | --- |
| A only (single pass) | 1.000 | 0.000 | n/a | 0.000 | 0.000 |
| A + B (glyph layer) | 0.000 | 0.237 | 0.000 | 0.745 | 0.001 |
| A + C (render-back) | 0.000 | 0.822 | 0.000 | 0.941 | 4.420 |
| A + B + C + repair (full) | 0.000 | 0.237 | 0.000 | 0.745 | 11.207 |

False accept = a corrupted equation was published as if correct.
False reject = a correct equation was withheld.
Repair success = of the readings the checks refused, the share repaired to the correct equation.
Review share = share of equations that were not auto-verified (repaired or withheld).
