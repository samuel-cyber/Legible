"""Render the student page and the verification report."""
from __future__ import annotations

import base64
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from assemble.mathml import to_mathml

_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(["html", "j2"]),
)


def summarize(results) -> dict:
    s = {"total": len(results), "verified": 0, "repaired": 0, "withheld": 0}
    for r in results:
        s[r.status] += 1
    return s


def _mathml_map(results) -> dict:
    out = {}
    for r in results:
        if r.latex:
            try:
                out[r.id] = to_mathml(r.latex)
            except Exception:
                out[r.id] = ""
    return out


def _data_uri(path) -> str:
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def render_student(title, blocks, results, report_href="report.html") -> str:
    by_id = {r.id: r for r in results}
    order = {r.id: i + 1 for i, r in enumerate(results)}
    return _env.get_template("student.html.j2").render(
        title=title, blocks=blocks, results=by_id, mathml=_mathml_map(results),
        summary=summarize(results), loop_index=order, report_href=report_href,
    )


def render_report(title, results) -> str:
    return _env.get_template("report.html.j2").render(
        title=title, results=results, mathml=_mathml_map(results),
        summary=summarize(results), crops={r.id: _data_uri(r.crop_png) for r in results},
    )
