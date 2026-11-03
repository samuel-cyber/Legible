# Evaluation sources

Real engineering / applied-mathematics lecture notes whose LaTeX **source** is
published under an open licence. Each PDF in `eval/pdfs/` is compiled from the
listed source with `tectonic` (a self-contained `pdflatex`-compatible engine), so
the PDF and the source match exactly. No gold LaTeX is typed by hand or produced
by a model.

| Local source | Compiled PDF | Upstream repository | Licence | Domain |
| --- | --- | --- | --- | --- |
| `eval/sources/uh_lecture/lec_notes.tex` | `eval/pdfs/lec_notes.pdf` | https://github.com/uh-comp-methods2/lectures | CC-BY-4.0 | Finite element methods (applied maths / engineering) |
| `eval/sources/ff_navierstokes/deriving-navier-stokes.tex` | `eval/pdfs/deriving-navier-stokes.pdf` | https://github.com/fairyflies9/Fluid-Dynamics-and-IBM-Theory | CC-BY-4.0 | Fluid mechanics (conservation laws to Navier--Stokes) |

## Provenance and local modifications

Everything under `eval/sources/<doc>/` is the unmodified upstream source **except**
the two edits listed here. Edits are recorded so the PDF can be trusted as a
faithful rendering of the source; none of them touch an equation.

1. `eval/sources/uh_lecture/lec_notes.tex`
   - The upstream preamble loads a private style file `tweakslo.sty` when present
     and otherwise declares its theorem environments inline with **`theorem`
     duplicated**, which is a latent upstream bug ("Command `\theorem` already
     defined"). The repository's real `tweakslo.sty` and `refs.bib` were
     downloaded alongside the source and are used, so the document is
     self-contained. The only change is to load `tweakslo.sty` unconditionally.
   - No equation, label, or body text was changed.

2. `eval/sources/ff_navierstokes/ib-tutorials.sty`
   - The shared beamer style guards its pdfLaTeX-only microtype ligature
     disabling with `\ifdefined\pdfnoligatures`, but left the `\DisableLigatures`
     call itself unguarded. It was moved inside the guard so the deck compiles
     under XeTeX as well. Only f-ligatures and straight typewriter quotes differ;
     every equation and heading is unchanged.

## Licence texts

Both repositories ship a machine-readable licence recognised by GitHub:
CC-BY-4.0 (Creative Commons Attribution 4.0 International). Attribution is to the
original authors (Lauri Oksanen for the finite-element notes; Laura A. Miller for
the fluid-dynamics deck). This evaluation uses the sources solely to build a
ground-truth set and does not redistribute them beyond this working tree.
