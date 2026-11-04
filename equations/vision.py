"""Channel A: Muse Spark reads the equation image and writes LaTeX.

Also hosts the evidence-guided repair step: when channels disagree, the
model gets the crop, its previous reading and the exact disagreement.
"""
from __future__ import annotations

import re

from clients import meta

TRANSCRIBE_PROMPT = """You are transcribing one equation from an engineering lecture PDF.
Write exactly what is printed, as LaTeX math (no $ signs, no \\[ \\]).
Rules:
- Copy every sign, subscript, superscript, accent and fraction exactly as shown.
- Do not simplify, rearrange, correct or complete the equation.
- Use \\frac{..}{..} for stacked fractions and \\dot{..} for dot accents.
- Ignore any equation number at the right margin.
Return JSON: {"latex": "..."}"""

PAGE_TEXT_PROMPT = """This image is one page of a scanned or handwritten lecture document.
Transcribe the body text (not the equations) in reading order, top to bottom.
Skip page numbers and running headers/footers. If a word is illegible, write
[illegible] in its place rather than guessing.
Return JSON: {"text": "..."}"""

REPAIR_PROMPT = """You transcribed this equation from an engineering lecture PDF as:

    {latex}

An independent check against the PDF's own text layer found these disagreements:
{diffs}

Look at the image again, focusing only on those places. The text-layer check can
itself be wrong, so trust what is printed in the image. Write the equation exactly
as printed, as LaTeX math (no $ signs).
Return JSON: {{"latex": "...", "changed": true/false, "note": "one short sentence"}}"""


def _clean(latex: str) -> str:
    latex = latex.strip()
    latex = re.sub(r"^\\\[|\\\]$|^\$+|\$+$", "", latex).strip()
    return latex


def transcribe(crop_png: str, route: str = "meta") -> str:
    # Structured output constrains decoding to {"latex": "..."} where the API
    # supports it; ask_json falls back to prompt-plus-parse if it does not.
    data = meta.ask_json(TRANSCRIBE_PROMPT, [crop_png], route, schema=meta.LATEX_SCHEMA)
    return _clean(data["latex"])


def page_text(page_png: str, route: str = "meta") -> str:
    """Body text of a scanned/handwritten page, read by Muse Spark.

    Last resort in the body-text chain (existing OCR layer, then Tesseract,
    then this) -- used only when neither of the deterministic sources is
    available. Never used to verify an equation; equations always go through
    ``transcribe`` on their own crop.
    """
    data = meta.ask_json(PAGE_TEXT_PROMPT, [page_png], route, schema=meta.PAGE_TEXT_SCHEMA)
    return data["text"].strip()


def repair(crop_png: str, latex: str, diff_explanations: list[str], route: str = "meta") -> str:
    diffs = "\n".join(f"- {d}" for d in diff_explanations)
    data = meta.ask_json(REPAIR_PROMPT.format(latex=latex, diffs=diffs), [crop_png], route,
                         schema=meta.REPAIR_SCHEMA)
    return _clean(data["latex"])
