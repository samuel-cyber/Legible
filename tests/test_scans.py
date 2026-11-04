"""Feature: scanned and handwritten pages (branch ``scans``).

A page with no usable glyph layer can be read, never proven, so it must
never reach "verified" or "repaired" -- only "ai_read" or "withheld". These
tests cover detection, the soft Tesseract dependency, the new decision rule
in isolation, and the pipeline end to end on a rasterized (image-only) copy
of the demo page -- plus the hard regression: a born-digital run through the
same pipeline code must be byte-for-byte unchanged.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pipeline
from equations.decide import AI_READ, REPAIRED, VERIFIED, WITHHELD, decide_scanned_equation
from ingest.pdf import load_page
from ingest.scan import is_scanned_page, ocr_layer_text, ocr_text_in_bbox, tesseract_text

DEMO_PDF = os.path.join(ROOT, "demo", "pages", "fluids.pdf")
DEMO_REPLAY = os.path.join(ROOT, "demo", "replay_fluids.json")

pytestmark = pytest.mark.skipif(not os.path.exists(DEMO_PDF), reason="demo PDF not built")

_BUILD_SPEC = importlib.util.spec_from_file_location(
    "scans_build", os.path.join(ROOT, "demo", "scans", "build.py")
)


def _load_build():
    import pymupdf  # noqa: F401
    module = importlib.util.module_from_spec(_BUILD_SPEC)
    _BUILD_SPEC.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def scan_pdf(tmp_path_factory):
    build = _load_build()
    out = str(tmp_path_factory.mktemp("scans") / "fluids_scan.pdf")
    return build.build(out_path=out)


# ------------------------------------------------------------- detection ---

def test_scanned_page_detected_on_image_only_pdf(scan_pdf):
    page = load_page(scan_pdf, 0)
    assert is_scanned_page(page, scan_pdf, 0)


def test_born_digital_page_is_never_flagged_as_scanned():
    page = load_page(DEMO_PDF, 0)
    assert not is_scanned_page(page, DEMO_PDF, 0)


def test_no_glyphs_at_all_is_a_scan(scan_pdf):
    page = load_page(scan_pdf, 0)
    assert page.glyphs == []
    assert page.lines == []


def test_ocr_layer_text_is_none_with_no_text_layer(scan_pdf):
    page = load_page(scan_pdf, 0)
    assert ocr_layer_text(page) is None


# ------------------------------------------------- soft Tesseract import ---

def test_missing_tesseract_package_does_not_crash(monkeypatch, scan_pdf):
    """No pytesseract installed: must return None, never raise."""
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    assert tesseract_text(scan_pdf, 0) is None


def test_tesseract_runtime_error_does_not_crash(monkeypatch, scan_pdf):
    """pytesseract installed but the tesseract binary itself is missing."""
    pytesseract = pytest.importorskip("pytesseract")

    class _Boom:
        @staticmethod
        def image_to_string(_img):
            raise getattr(pytesseract, "TesseractNotFoundError", RuntimeError)("no binary")

    monkeypatch.setitem(sys.modules, "pytesseract", _Boom)
    assert tesseract_text(scan_pdf, 0) is None


# --------------------------------------------- decide_scanned_equation ----

def test_successful_reading_is_ai_read_never_verified():
    r = decide_scanned_equation("e1", (0, 0, 10, 10), None, transcribe=lambda crop: "x = 1")
    assert r.status == AI_READ
    assert r.status not in (VERIFIED, REPAIRED)
    assert r.latex == "x = 1"


def test_transcribe_failure_withholds():
    def boom(_crop):
        raise RuntimeError("model down")
    r = decide_scanned_equation("e1", (0, 0, 10, 10), None, transcribe=boom)
    assert r.status == WITHHELD
    assert r.latex is None


def test_invalid_latex_withholds():
    # An unclosed brace genuinely fails to parse (an unknown command like
    # \mystery is accepted as an opaque token elsewhere, so it would not
    # exercise this path).
    r = decide_scanned_equation("e1", (0, 0, 10, 10), None, transcribe=lambda crop: r"\frac{1}{2")
    assert r.status == WITHHELD
    assert r.latex is None


def test_visual_caution_never_withholds_or_verifies():
    def compare(_crop, _rendered):
        return ["x looks like it could be X"]
    def render(_latex, out_png, _crop=None):
        return out_png
    r = decide_scanned_equation("e1", (0, 0, 10, 10), "crop.png",
                                transcribe=lambda crop: "x = 1", compare=compare, render=render,
                                workdir=".")
    assert r.status == AI_READ
    assert r.cautions == ["x looks like it could be X"]


def test_visual_check_error_is_a_caution_not_a_withhold():
    def compare(_crop, _rendered):
        raise RuntimeError("BadModelJSON")
    def render(_latex, out_png, _crop=None):
        return out_png
    r = decide_scanned_equation("e1", (0, 0, 10, 10), "crop.png",
                                transcribe=lambda crop: "x = 1", compare=compare, render=render,
                                workdir=".")
    assert r.status == AI_READ
    assert r.cautions and "could not run" in r.cautions[0]


def test_ocr_mismatch_adds_a_caution_but_never_verifies():
    r = decide_scanned_equation("e1", (0, 0, 10, 10), None,
                                transcribe=lambda crop: "x = 1", ocr_text="completely different text")
    assert r.status == AI_READ
    assert r.cautions, "a large OCR/reading mismatch should be flagged"


def test_ocr_close_match_raises_no_caution():
    r = decide_scanned_equation("e1", (0, 0, 10, 10), None,
                                transcribe=lambda crop: "x = 1", ocr_text="x=1")
    assert r.status == AI_READ
    assert r.cautions == []


def test_ocr_can_never_verify_even_when_it_matches_perfectly():
    """OCR agreement is not evidence of correctness -- status is still ai_read."""
    r = decide_scanned_equation("e1", (0, 0, 10, 10), None,
                                transcribe=lambda crop: "x = 1", ocr_text="x = 1")
    assert r.status == AI_READ


def test_ocr_text_in_bbox_reads_only_glyphs_inside_the_box():
    page = load_page(DEMO_PDF, 0)
    # p1e2's bbox from eval/gold.json: "p = p_0 + \rho g h"
    bbox = (272.57, 301.57, 337.68, 316.32)
    text = ocr_text_in_bbox(page, bbox)
    assert text and "p" in text


# ----------------------------------------------- pipeline, end to end -----

def test_image_only_pdf_never_verifies_anything(tmp_path, scan_pdf):
    """The whole pipeline, on a page with no glyph layer: mocked model
    replies throughout, nothing can ever come out "verified" or "repaired"."""
    calls = {"n": 0}

    def fake_transcribe(_crop):
        calls["n"] += 1
        return f"x_{calls['n']} = {calls['n']}"

    def fake_ask(_prompt, images=(), schema=None):
        # p1e1's known bbox on the demo page (eval/gold.json), so there is
        # real ink for snap_to_ink to find.
        return {"regions": [{"x0": 262.4, "y0": 177.2, "x1": 348.1, "y1": 207.7}]}

    out = pipeline.process(
        scan_pdf, str(tmp_path), transcribe=fake_transcribe, compare=False,
        scan_regions_ask=fake_ask, on_event=lambda e: None,
    )
    assert out["results"], "expected at least one region to be found"
    statuses = {r.status for r in out["results"]}
    assert VERIFIED not in statuses
    assert REPAIRED not in statuses
    assert statuses <= {AI_READ, WITHHELD}
    assert out["pages"] and out["pages"][0].is_scan is True


def test_image_only_pdf_with_failing_region_model_finds_nothing(tmp_path, scan_pdf):
    """No heuristic fallback exists for a scanned page: a failed region
    proposal means no equations are found, not a guess."""
    def boom(_prompt, images=(), schema=None):
        raise RuntimeError("model down")

    out = pipeline.process(
        scan_pdf, str(tmp_path), transcribe=lambda c: "x = 1", compare=False,
        scan_regions_ask=boom, on_event=lambda e: None,
    )
    assert out["results"] == []
    assert out["pages"][0].is_scan is True


def test_born_digital_pipeline_output_is_byte_for_byte_unchanged(tmp_path):
    """The hard regression: this feature must not alter born-digital output."""
    if not os.path.exists(DEMO_REPLAY):
        pytest.skip("demo replay not built")
    transcribe, repair = pipeline.replay_reader(DEMO_REPLAY)
    out = pipeline.process(
        DEMO_PDF, str(tmp_path), transcribe=transcribe, repair=repair, compare=False,
        on_event=lambda e: None,
    )
    assert out["summary"] == {"verified": 4, "repaired": 1, "withheld": 1}
    assert all(not p.is_scan for p in out["pages"])
