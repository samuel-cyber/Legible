"""Shared test data: the demo page's true LaTeX, cosmetic variants that must be
treated as identical, and 15 injected errors that must be caught.

Kept in one module so tests/test_tokens.py and tests/test_glyphs.py (and the
eval runner) all agree on what "true" and "corrupt" mean.
"""
from __future__ import annotations

# --------------------------------------------------------------- the gold --
# The exact LaTeX of the six equations on demo/pages/fluids.tex, in reading
# order. Equation ids match the demo page (p1e1 .. p1e6).
GOLD: list[tuple[str, str]] = [
    ("p1e1", r"\frac{p}{\rho g} + \frac{v^2}{2g} + z = H"),
    ("p1e2", r"p = p_0 + \rho g h"),
    ("p1e3", r"A_1 v_1 = A_2 v_2"),
    ("p1e4", r"h_f = f \frac{L}{D} \frac{v^2}{2g}"),
    ("p1e5", r"Re = \frac{\rho v D}{\mu}"),
    ("p1e6", r"F_x = -\dot{m}(v_2 - v_1)"),
]

GOLD_BY_ID = dict(GOLD)

# ------------------------------------------------------- cosmetic variants --
# Every one of these is the same equation written a different (valid) way. The
# token lists must come out identical, so the verifier does not withhold a
# correct equation over formatting.
COSMETIC: list[tuple[str, str]] = [
    ("p1e1", r"\dfrac{p}{\rho g} + \dfrac{v^{2}}{2g} + z = H"),
    ("p1e1", r"\displaystyle \frac{p}{\rho g}+\frac{v^2}{2g}+z=H"),
    ("p1e2", r"p = p_{0} + \rho g h"),
    ("p1e2", r"p = p_0 + \rho\, g\, h"),
    ("p1e3", r"A_{1} \, v_{1} = A_{2} \, v_{2}"),
    ("p1e3", r"\mathrm{A}_1 v_1 = \mathrm{A}_2 v_2"),
    ("p1e4", r"h_f = f \tfrac{L}{D} \tfrac{v^{2}}{2g}"),
    ("p1e4", r"h_f = f\,\frac{L}{D}\,\frac{v^2}{2g}"),
    ("p1e5", r"Re = \frac{\rho v D}{\mu}"),
    ("p1e5", r"Re = \dfrac{\rho v D}{\mu}"),
    ("p1e6", r"F_x = -\dot m (v_2 - v_1)"),
    ("p1e6", r"F_{x} = -\dot{m}(v_{2} - v_{1})"),
]

# ------------------------------------------------------ 15 injected errors --
# Each corrupts exactly one thing about a gold equation, in one of the
# categories the verifier must catch: sign flip, exponent, digit, swapped
# subscript, dropped term, inverted fraction, Greek letter swap, dropped accent.
# The tests assert every one of these actually changes the token list.
CORRUPTIONS: list[tuple[str, str, str]] = [
    # 1: exponent change
    ("p1e1", r"\frac{p}{\rho g} + \frac{v^3}{2g} + z = H", "exponent"),
    # 2: dropped term
    ("p1e1", r"\frac{p}{\rho g} + \frac{v^2}{2g} = H", "dropped term"),
    # 3: dropped symbol inside a fraction
    ("p1e1", r"\frac{p}{g} + \frac{v^2}{2g} + z = H", "dropped term"),
    # 4: sign flip
    ("p1e2", r"p = p_0 - \rho g h", "sign flip"),
    # 5: digit change
    ("p1e2", r"p = p_1 + \rho g h", "digit"),
    # 6: swapped subscripts
    ("p1e3", r"A_2 v_1 = A_1 v_2", "swapped subscript"),
    # 7: changed subscript
    ("p1e3", r"A_1 v_1 = A_2 v_1", "swapped subscript"),
    # 8: inverted fraction
    ("p1e4", r"h_f = f \frac{D}{L} \frac{v^2}{2g}", "inverted fraction"),
    # 9: digit change inside a denominator
    ("p1e4", r"h_f = f \frac{L}{D} \frac{v^2}{3g}", "digit"),
    # 10: mu vs nu
    ("p1e5", r"Re = \frac{\rho v D}{\nu}", "greek swap"),
    # 11: rho vs p
    ("p1e5", r"Re = \frac{p v D}{\mu}", "greek swap"),
    # 12: rho vs sigma
    ("p1e5", r"Re = \frac{\sigma v D}{\mu}", "greek swap"),
    # 13: sign flip
    ("p1e6", r"F_x = \dot{m}(v_2 - v_1)", "sign flip"),
    # 14: dropped dot accent
    ("p1e6", r"F_x = -m(v_2 - v_1)", "dropped accent"),
    # 15: swapped subscripts inside brackets
    ("p1e6", r"F_x = -\dot{m}(v_1 - v_2)", "swapped subscript"),
    # --- added so the set covers every listed corruption scenario exactly ---
    # 16: sign flip in Bernoulli (+ -> -)
    ("p1e1", r"\frac{p}{\rho g} - \frac{v^2}{2g} + z = H", "sign flip"),
    # 17: dropped digit in a denominator (2g -> g)
    ("p1e1", r"\frac{p}{\rho g} + \frac{v^2}{g} + z = H", "dropped digit"),
    # 18: dropped symbol inside a fraction (rho g -> rho); the counterpart of
    #     case 3, which drops rho instead of g
    ("p1e1", r"\frac{p}{\rho} + \frac{v^2}{2g} + z = H", "dropped term"),
    # 19: inverted fraction p/(rho g)
    ("p1e1", r"\frac{\rho g}{p} + \frac{v^2}{2g} + z = H", "inverted fraction"),
    # 20: dropped term (h in p_0 + rho g h)
    ("p1e2", r"p = p_0 + \rho g", "dropped term"),
    # 21: spurious exponent (rho v^2 D)
    ("p1e5", r"Re = \frac{\rho v^2 D}{\mu}", "spurious exponent"),
]

assert len(CORRUPTIONS) >= 15
