"""Verified LaTeX -> MathML, deterministically (no model in this step)."""
from __future__ import annotations

import html

from latex2mathml.converter import convert


def to_mathml(latex: str, display: bool = True) -> str:
    mathml = convert(latex)
    attrs = f' display="{"block" if display else "inline"}" alttext="{html.escape(latex, quote=True)}"'
    return mathml.replace("<math", "<math" + attrs, 1)
