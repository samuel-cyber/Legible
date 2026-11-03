"""Real glyph samples for regression tests.

Each sample is a page region, its bounding box, and the LaTeX that pdfLaTeX
actually set there. The regions come from the open-licence lecture notes listed
in ``eval/sources.md`` and compiled to ``eval/pdfs/*.pdf`` with tectonic, so the
glyph geometry is exactly what a real TeX engine produced -- not a fixture.

The LaTeX strings are read straight out of the paired ``eval/gold.json`` entry
(built by ``gold_from_tex.py`` from the published source), so a sample can only
exist if the source really contains it.

``SAMPLES`` are cases a fix made match; ``KNOWN_MISMATCHES`` are cases whose
glyph geometry still differs and that therefore must stay withheld. The PDFs
are committed (they are small, ~200 KB each) so these tests run without a TeX
toolchain.
"""
from __future__ import annotations

from dataclasses import dataclass

# The PDFs that must be present for these samples to run. Committed with the
# repository; see eval/sources.md for their upstream origins and licence.
PDFS = ["eval/pdfs/lec_notes.pdf", "eval/pdfs/deriving-navier-stokes.pdf"]


@dataclass(frozen=True)
class Sample:
    name: str
    pdf: str
    page: int
    bbox: tuple[float, float, float, float]
    latex: str
    why: str


# Fixes that made these match their real LaTeX, token for token.
SAMPLES = [
    Sample(
        name="neq_overlay",
        pdf="eval/pdfs/lec_notes.pdf",
        page=8,
        bbox=(227.44, 505.52, 327.98, 521.47),
        latex=r"\{x \in I \mid u(x) \ne 0\}.",
        why="the slash overlay (U+0338) must fold into the '=' it strikes, "
            "giving the same ne a transcription produces",
    ),
    Sample(
        name="dots_fold",
        pdf="eval/pdfs/lec_notes.pdf",
        page=5,
        bbox=(204.37, 264.26, 351.05, 281.16),
        latex=r"0 = x_0 < x_1 < \dots < x_n = 1,",
        why="three literal dot glyphs must fold to one ellipsis matching \\dots",
    ),
    Sample(
        name="plain_equals",
        pdf="eval/pdfs/lec_notes.pdf",
        page=1,
        bbox=(134.11, 460.32, 421.28, 476.28),
        latex=r"(u + v)(x) = u(x) + v(x), (cu)(x) = cu(x), x \in I.",
        why="a genuine '=' with no overlay must stay '=' (not be rewritten to "
            "'ne' by the overlay rule), and the two '=' in one line must both "
            "survive the per-glyph pass",
    ),
    Sample(
        name="norm_bars",
        pdf="eval/pdfs/lec_notes.pdf",
        page=7,
        bbox=(140.06, 656.97, 415.35, 673.87),
        latex=r"\|Au-Av\|_Y = \|A(u-v)\|_Y \le C \|u-v\|_X < C \delta = \epsilon.",
        why="the paired \\| norm bars must map to the same character the reading "
            "uses (four pairs on one line, with scripts and relations between "
            "them), so a straight-bar glyph is never mistaken for a relation",
    ),
    Sample(
        name="to_relation",
        pdf="eval/pdfs/lec_notes.pdf",
        page=3,
        bbox=(187.40, 617.03, 368.02, 634.74),
        latex=r"a(u, v) = (u', v'), a : \mathcal V \times \mathcal V \to \mathbb R,",
        why="an arrow used between sets is a relation, not an accent: the glyph "
            "layer must not eat it as a decoration on the preceding letter",
    ),
    Sample(
        name="boxed_relation",
        pdf="eval/pdfs/deriving-navier-stokes.pdf",
        page=19,
        bbox=(192.33, 124.43, 264.59, 140.34),
        latex=r"\boxed{\bm{t}_p(\bm{n})=-p\bm{n}}.",
        why="\\boxed is decorative: its frame must not change the tokens, so a "
            "boxed equation verifies exactly like the bare one inside it",
    ),
]


# Geometry that is genuinely ambiguous and must stay withheld (fail-closed):
# the glyph layer cannot recover the reading's structure, so the equation is
# reported for review instead of being accepted.
KNOWN_MISMATCHES = [
    Sample(
        name="superscript_norm",
        pdf="eval/pdfs/lec_notes.pdf",
        page=2,
        bbox=(203.01, 295.86, 352.40, 338.62),
        latex=r"\|u\|_{L^p(I)} = \left( \int_I |u(x)|^p dx \right)^{\frac1p}.",
        why="the superscript p sits on the norm rule's baseline, so its host is "
            "ambiguous and the glyph layer cannot tell ^p from _p",
    ),
    Sample(
        name="packing_infty",
        pdf="eval/pdfs/lec_notes.pdf",
        page=12,
        bbox=(223.48, 296.13, 331.93, 313.24),
        latex=r"\|u\|_{L^\infty(I)} \lesssim \|u\|_{H^1(I)}.",
        why="the local level baseline is set by the line's packing rules, not by "
            "the host glyph, so a raised ^\\infty is misclassified",
    ),
]
