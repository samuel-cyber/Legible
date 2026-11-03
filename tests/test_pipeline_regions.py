"""Pipeline layout wiring (no network, no API key).

Exercises ``pipeline.process`` with each region mode using the demo replay file
(nothing here reaches Muse Spark). The model region proposal is monkeypatched in
the model-mode tests so the run is guaranteed offline.
"""
from __future__ import annotations

import os

import pytest

import pipeline
from ingest.pdf import find_display_equations, load_page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_PDF = os.path.join(ROOT, "demo", "pages", "fluids.pdf")
DEMO_REPLAY = os.path.join(ROOT, "demo", "replay_fluids.json")

pytestmark = pytest.mark.skipif(
    not (os.path.exists(DEMO_PDF) and os.path.exists(DEMO_REPLAY)),
    reason="demo pdf/replay not built",
)


def _run(tmp_path, regions, events=None):
    transcribe, repair = pipeline.replay_reader(DEMO_REPLAY)
    return pipeline.process(
        DEMO_PDF, str(tmp_path), transcribe=transcribe, repair=repair,
        compare=False, regions=regions, on_event=(events.append if events is not None else (lambda e: None)),
    )


def test_heuristic_mode_runs_offline(tmp_path):
    events = []
    out = _run(tmp_path, "heuristic", events)
    assert out["summary"]["verified"] + out["summary"]["repaired"] + out["summary"]["withheld"] > 0
    page_events = [e for e in events if e["type"] == "page"]
    assert page_events and page_events[0]["regions"] == "heuristic"
    assert page_events[0]["sources"] and all(s == "heuristic" for s in page_events[0]["sources"])


def test_model_mode_wires_through_without_network(monkeypatch, tmp_path):
    page = load_page(DEMO_PDF, 0)
    first = find_display_equations(page)[0]

    def fake_propose(_page, _page_png, ask=None):
        return [first]

    # Patch the proposal itself: find_regions still runs its own cross-check and
    # the run can never touch the network.
    monkeypatch.setattr(pipeline.region_finder, "propose_regions", fake_propose)
    events = []
    out = _run(tmp_path, "model", events)

    page_events = [e for e in events if e["type"] == "page"]
    assert page_events and page_events[0]["regions"] == "model"
    sources = page_events[0]["sources"]
    assert "model" in sources, "the model box should be used"
    assert "heuristic" in sources, "the heuristic should top up the regions the model missed"
    # Every equation still gets a verdict; a region never decides by itself.
    assert out["summary"]["verified"] + out["summary"]["repaired"] + out["summary"]["withheld"] == len(sources)


def test_model_failure_falls_back_to_heuristic_through_the_pipeline(monkeypatch, tmp_path):
    def boom(_page, _page_png, ask=None):
        raise pipeline.region_finder.RegionProposalFailed("model down")

    monkeypatch.setattr(pipeline.region_finder, "propose_regions", boom)
    events = []
    _run(tmp_path, "model", events)
    page_events = [e for e in events if e["type"] == "page"]
    assert page_events[0]["regions"] == "model", "the mode is still reported"
    assert page_events[0]["sources"] and all(s == "heuristic" for s in page_events[0]["sources"])


def test_unknown_region_mode_is_rejected(tmp_path):
    transcribe, repair = pipeline.replay_reader(DEMO_REPLAY)
    with pytest.raises(ValueError):
        pipeline.process(DEMO_PDF, str(tmp_path), transcribe=transcribe, repair=repair,
                         compare=False, regions="magic")
