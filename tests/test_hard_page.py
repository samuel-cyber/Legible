"""Task 5: the harder page must exercise Channel B exactly as advertised.

The page is typeset with PyMuPDF (no LaTeX toolchain) but has a real glyph
layer: exact baselines, sizes and drawn fraction bars. Channel B is unmodified,
so these tests pin down which constructs it reproduces and which it withholds.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_BUILD_SPEC = importlib.util.spec_from_file_location(
    "hard_build", os.path.join(ROOT, "demo", "hard", "build.py")
)


def _load_build():
    pytest.importorskip("matplotlib")
    pytest.importorskip("fontTools")
    import pymupdf  # noqa: F401
    module = importlib.util.module_from_spec(_BUILD_SPEC)
    _BUILD_SPEC.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def build():
    return _load_build()


@pytest.fixture(scope="module")
def placed(build):
    return build.build()


@pytest.fixture(scope="module")
def page(build):
    from ingest.pdf import load_page
    return load_page(build.HARD_PDF, 0)


def test_page_has_eight_equations(page, build):
    from ingest.pdf import find_display_equations
    assert len(find_display_equations(page)) == len(build.EQ_SPECS) == 8


def _specs():
    """EQ_SPECS is a module constant; read it without triggering a build."""
    module = _load_build()
    return module.EQ_SPECS


@pytest.mark.parametrize("eqid", [s["id"] for s in _specs() if s["expected"] == "match"])
def test_handled_constructs_match(eqid, placed, page):
    from equations.glyphs import glyph_tokens
    from equations.tokens import diff, latex_to_tokens

    spec = next(s for s in placed if s["id"] == eqid)
    assert not diff(latex_to_tokens(spec["latex"]), glyph_tokens(page, spec["bbox"])), \
        f"{eqid} should be reproduced token-for-token"


@pytest.mark.parametrize("eqid", [s["id"] for s in _specs() if s["expected"] == "withhold"])
def test_unrepresentable_constructs_withheld(eqid, placed, page):
    from equations.glyphs import glyph_tokens
    from equations.tokens import diff, latex_to_tokens

    spec = next(s for s in placed if s["id"] == eqid)
    assert diff(latex_to_tokens(spec["latex"]), glyph_tokens(page, spec["bbox"])), \
        f"{eqid} is outside the token vocabulary and must not verify"


def test_construct_inventory_is_covered():
    kinds = " ".join(f"{s['heading']} {s['construct']}" for s in _specs()).lower()
    for needle in ("partial", "integral", "summation", "radical", "accent", "binomial", "floor"):
        assert needle in kinds, f"harder page is meant to exercise {needle!r}"
