"""Layout region tests (no network, no API key).

The region model is mocked: every test feeds a fixed JSON reply (or a failing
call) to ``layout.regions`` and checks the deterministic behaviour around it --
validation, snapping to glyphs, reading order, the heuristic fallback, and the
cross-check union. Nothing here needs Muse Spark.
"""
from __future__ import annotations

import logging
import os

import pytest

from ingest.pdf import Glyph, Page
from layout import regions

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_PDF = os.path.join(ROOT, "demo", "pages", "fluids.pdf")


def G(c: str, font: str = "CMMI10", x: float = 0.0, top: float = 0.0,
      w: float = 6.0, h: float = 10.0) -> Glyph:
    """A glyph with an explicit box: left=x, top=top, width w, height h."""
    return Glyph(c=c, font=font, size=h, x=x, y=top + h,
                 bbox=(x, top, x + w, top + h))


def make_page(glyphs=(), lines=(), width: float = 600.0, height: float = 800.0) -> Page:
    return Page(number=0, width=width, height=height,
                glyphs=list(glyphs), lines=[list(l) for l in lines])


def eq_glyphs(top: float, x0: float = 100.0, n: int = 4, gap: float = 20.0):
    return [G(chr(ord("a") + i), x=x0 + i * gap, top=top) for i in range(n)]


def reply(boxes):
    return {"regions": [{"x0": b[0], "y0": b[1], "x1": b[2], "y1": b[3]} for b in boxes]}


def fake_ask(data):
    def ask(prompt, images=(), schema=None):
        return data
    return ask


def failing_ask(prompt, images=(), schema=None):
    raise RuntimeError("network down")


# --------------------------------------------------------------- validation ---

def test_box_off_the_page_is_invalid():
    page = make_page([G("x", x=100, top=100)])
    assert not regions.valid_box(page, (-50.0, 100.0, 200.0, 120.0)), "left of page"
    assert not regions.valid_box(page, (100.0, -50.0, 200.0, 120.0)), "above page"
    assert not regions.valid_box(page, (100.0, 100.0, 4000.0, 120.0)), "right of page"
    assert not regions.valid_box(page, (100.0, 100.0, 200.0, 5000.0)), "below page"


def test_tiny_box_is_invalid():
    page = make_page([G("x", x=100, top=100)])
    assert not regions.valid_box(page, (100.0, 100.0, 105.0, 103.0)), "too small"


def test_sensible_box_is_valid():
    page = make_page([G("x", x=100, top=100)])
    assert regions.valid_box(page, (95.0, 95.0, 300.0, 120.0))


# ------------------------------------------------------------------ snapping ---

def test_snap_tightens_to_the_glyphs_inside():
    page = make_page(eq_glyphs(top=100.0))
    snapped = regions.snap_to_glyphs(page, (95.0, 95.0, 300.0, 140.0), pad=2.0)
    # glyphs: x = 100,120,140,160, each 6 wide, top=100 h=10 -> union (100,100,166,110)
    assert snapped == (98.0, 98.0, 168.0, 112.0)


def test_box_with_no_glyphs_has_nothing_to_snap_to():
    page = make_page(eq_glyphs(top=100.0))
    assert regions.snap_to_glyphs(page, (400.0, 400.0, 500.0, 420.0)) is None


def test_snap_ignores_glyphs_whose_centre_is_outside():
    page = make_page([G("x", x=100, top=100), G("y", x=300, top=100)])
    # Box covers only the first glyph's centre.
    snapped = regions.snap_to_glyphs(page, (95.0, 95.0, 200.0, 120.0), pad=0.0)
    assert snapped == (100.0, 100.0, 106.0, 110.0)


# ------------------------------------------------------------- reading order ---

def test_reading_order_is_rows_then_left_to_right():
    boxes = [(0.0, 100.0, 50.0, 120.0), (0.0, 200.0, 50.0, 220.0), (60.0, 100.0, 110.0, 120.0)]
    assert regions.in_reading_order(boxes) == [
        (0.0, 100.0, 50.0, 120.0),
        (60.0, 100.0, 110.0, 120.0),
        (0.0, 200.0, 50.0, 220.0),
    ]


def test_reading_order_of_nothing_is_nothing():
    assert regions.in_reading_order([]) == []


# ----------------------------------------------------------------- cross-check ---

def test_cross_check_reports_both_sides_of_a_disagreement():
    model = [(100.0, 100.0, 200.0, 120.0), (100.0, 300.0, 200.0, 320.0)]
    heuristic = [(100.0, 100.0, 200.0, 120.0), (100.0, 500.0, 200.0, 520.0)]
    extra, missed = regions.cross_check(model, heuristic)
    assert extra == [(100.0, 300.0, 200.0, 320.0)]
    assert missed == [(100.0, 500.0, 200.0, 520.0)]


def test_cross_check_agreement_is_silent():
    same = [(100.0, 100.0, 200.0, 120.0)]
    extra, missed = regions.cross_check(same, list(same))
    assert extra == [] and missed == []


# ------------------------------------------------------------- parse_regions ---

def test_parse_drops_malformed_and_empty_regions(caplog):
    page = make_page(eq_glyphs(top=100.0))
    data = {"regions": [
        {"x0": 95, "y0": 95, "x1": 300, "y1": 120},   # good
        {"x0": 95, "y1": 120},                        # missing keys
        {"x0": "left", "y0": 0, "x1": 5, "y1": 5},    # not numeric
        {"x0": 400, "y0": 400, "x1": 500, "y1": 420}, # no glyphs
        {"x0": 100, "y0": 100, "x1": 105, "y1": 103}, # too small
    ]}
    with caplog.at_level(logging.WARNING):
        boxes = regions.parse_regions(page, data)
    assert len(boxes) == 1
    assert any("malformed" in r.message for r in caplog.records)
    assert any("no glyphs" in r.message for r in caplog.records)
    assert any("invalid" in r.message for r in caplog.records)


def test_parse_normalizes_swapped_corners():
    page = make_page(eq_glyphs(top=100.0))
    # x0 > x1 and y0 > y1: the corners are swapped.
    boxes = regions.parse_regions(page, {"regions": [{"x0": 300, "y0": 140, "x1": 95, "y1": 95}]})
    assert len(boxes) == 1
    assert boxes[0][0] < boxes[0][2] and boxes[0][1] < boxes[0][3]


# --------------------------------------------------------------- find_regions ---

def test_heuristic_mode_uses_only_the_heuristic():
    body = [G("T", font="Times", x=50, top=100)]           # sets the left margin
    eq = eq_glyphs(top=300.0, x0=120.0)
    page = make_page(glyphs=body + eq, lines=[body, eq])
    found = regions.find_regions(page, mode="heuristic")
    assert found and all(src == "heuristic" for _, src in found)


def test_model_mode_unions_model_and_heuristic_boxes(caplog):
    body = [G("T", font="Times", x=50, top=100)]
    eq1 = eq_glyphs(top=300.0, x0=120.0)
    eq2 = eq_glyphs(top=400.0, x0=120.0)
    page = make_page(glyphs=body + eq1 + eq2, lines=[body, eq1, eq2])
    # The model sees only the first equation; the heuristic must contribute the second.
    model_box = (110.0, 290.0, 200.0, 320.0)
    with caplog.at_level(logging.WARNING):
        found = regions.find_regions(page, mode="model", ask=fake_ask(reply([model_box])),
                                     page_png="unused.png")
    sources = sorted(src for _, src in found)
    assert sources == ["heuristic", "model"], "union of both finders"
    assert any("heuristic found a region the model missed" in r.message for r in caplog.records)


def test_model_mode_logs_a_model_only_region(caplog):
    body = [G("T", font="Times", x=50, top=100)]
    eq = eq_glyphs(top=300.0, x0=120.0)
    # A glyph the heuristic cannot see (not in page.lines) but the model can snap to.
    hidden = [G("h", x=120, top=600)]
    page = make_page(glyphs=body + eq + hidden, lines=[body, eq])
    model_box = (110.0, 590.0, 140.0, 620.0)
    with caplog.at_level(logging.WARNING):
        found = regions.find_regions(page, mode="model", ask=fake_ask(reply([model_box])),
                                     page_png="unused.png")
    assert any(src == "model" for _, src in found)
    assert any("model found a region the heuristic missed" in r.message for r in caplog.records)


def test_model_mode_falls_back_when_the_call_fails():
    body = [G("T", font="Times", x=50, top=100)]
    eq = eq_glyphs(top=300.0, x0=120.0)
    page = make_page(glyphs=body + eq, lines=[body, eq])
    found = regions.find_regions(page, mode="model", ask=failing_ask, page_png="unused.png")
    assert found and all(src == "heuristic" for _, src in found)


def test_model_mode_falls_back_when_the_model_returns_nothing():
    body = [G("T", font="Times", x=50, top=100)]
    eq = eq_glyphs(top=300.0, x0=120.0)
    page = make_page(glyphs=body + eq, lines=[body, eq])
    found = regions.find_regions(page, mode="model", ask=fake_ask({"regions": []}),
                                 page_png="unused.png")
    assert found and all(src == "heuristic" for _, src in found)


def test_model_mode_without_a_page_image_or_pdf_falls_back():
    body = [G("T", font="Times", x=50, top=100)]
    eq = eq_glyphs(top=300.0, x0=120.0)
    page = make_page(glyphs=body + eq, lines=[body, eq])
    found = regions.find_regions(page, mode="model", ask=fake_ask(reply([])))
    assert found and all(src == "heuristic" for _, src in found)


def test_unknown_mode_is_rejected():
    page = make_page(eq_glyphs(top=100.0))
    with pytest.raises(ValueError):
        regions.find_regions(page, mode="magic")


def test_propose_regions_wraps_model_failure():
    page = make_page(eq_glyphs(top=100.0))
    with pytest.raises(regions.RegionProposalFailed):
        regions.propose_regions(page, "unused.png", ask=failing_ask)


# ------------------------------------------------------------------- render ---

@pytest.mark.skipif(not os.path.exists(DEMO_PDF), reason="demo pdf not built")
def test_render_page_writes_a_png(tmp_path):
    out = str(tmp_path / "page.png")
    regions.render_page(DEMO_PDF, 0, out_png=out, zoom=1.0)
    assert os.path.getsize(out) > 0
