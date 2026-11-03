"""Channel C: render the reading back to an image and ask for visible differences.

Spotting differences between two images is a different task from
transcribing one, so its mistakes correlate less with Channel A's. Because two
renderers never agree on letterforms, the prompt is explicit that the fonts
differ and that only a *different character* counts as a difference, and it asks
the model to quote the exact characters it compared.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from clients import meta

COMPARE_PROMPT = """Image 1 is an equation cropped from a lecture PDF.
Image 2 is the same equation re-typeset from a transcription of it.

The two images deliberately use DIFFERENT fonts and renderers, so the glyph
shapes, stroke weights, sizes, italics, slant, kerning, spacing and color will
NOT match exactly. None of that is a difference.

Report a difference ONLY when a symbol is a genuinely DIFFERENT CHARACTER, for
example:
- a letter case change: a lowercase 'x' vs an uppercase 'X', 'g' vs 'G'
- an italic character vs a roman one that changes which symbol it is (e.g. 'l'
  vs '1', 'v' vs Greek 'ν', 'O' vs '0')
- a different Greek letter or a swapped sign, digit, subscript or superscript
- a missing or extra symbol, fraction, bracket or accent

Do NOT report a difference for font choice, size, spacing, slant or italics
alone when it is the same character. Ignore any equation number in image 1.

For each real difference, QUOTE the exact characters you compared, as
"Image 1 has X but image 2 has Y".
Return JSON: {"differences": ["...", "..."]}  (an empty list if the characters are identical)"""


class RenderError(ValueError):
    pass


def _fontsize_for(crop_png: str | None, lo: int = 14, hi: int = 64) -> int:
    """Pick a font size that makes the render roughly the height of the crop.

    Comparing two images is easier when they are at a similar scale, so we match
    the crop's height (the crop is rendered at 4x zoom, i.e. 200 dpi here).
    """
    if not crop_png:
        return 28
    try:
        img = mpimg.imread(crop_png)
        crop_h = img.shape[0]
    except Exception:
        return 28
    size = round((crop_h / 200.0) * 72.0 / 1.7)
    return max(lo, min(hi, size))


def render_latex(latex: str, out_png: str, crop_png: str | None = None,
                 fontsize: int | None = None) -> str:
    """Render LaTeX with matplotlib mathtext (no TeX install needed).

    ``crop_png`` is only used to match the render's size to the original crop.
    """
    if fontsize is None:
        fontsize = _fontsize_for(crop_png)
    fig = plt.figure(figsize=(0.01, 0.01))
    try:
        fig.text(0, 0, f"${latex}$", fontsize=fontsize)
        fig.savefig(out_png, dpi=200, bbox_inches="tight", pad_inches=0.2, facecolor="white")
    except Exception as e:  # mathtext rejects some commands
        raise RenderError(str(e)) from e
    finally:
        plt.close(fig)
    return out_png


def compare(crop_png: str, rendered_png: str, route: str = "meta") -> list[str]:
    # Structured output constrains decoding to {"differences": [...]}; ask_json
    # falls back to prompt-plus-parse if the endpoint does not support it.
    data = meta.ask_json(COMPARE_PROMPT, [crop_png, rendered_png], route,
                         schema=meta.COMPARE_SCHEMA)
    return [d for d in data.get("differences", []) if str(d).strip()]
