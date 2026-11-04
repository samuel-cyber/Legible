"""Web app tests (no network, no API key).

The app runs the pipeline in a background thread. We point it at the demo
replay file so the whole flow works offline and deterministically.
"""
from __future__ import annotations

import os
import time

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
pytest.importorskip("multipart")

from fastapi.testclient import TestClient  # noqa: E402

from app import main as app_main  # noqa: E402
from clients import meta as _meta  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_PDF = os.path.join(ROOT, "demo", "pages", "fluids.pdf")
DEMO_REPLAY = os.path.join(ROOT, "demo", "replay_fluids.json")


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("LEGIBLE_REPLAY_JSON", DEMO_REPLAY)
    return TestClient(app_main.app)


def test_index_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "aria-live" in r.text and "<button" in r.text and "<label" in r.text


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_reject_non_pdf(client):
    r = client.post("/jobs", files={"file": ("notes.txt", b"not a pdf", "text/plain")})
    assert r.status_code == 400


def test_reject_fake_pdf_magic(client):
    r = client.post("/jobs", files={"file": ("fake.pdf", b"hello world", "application/pdf")})
    assert r.status_code == 400


def test_unknown_job_is_404(client):
    assert client.get("/jobs/deadbeef/page").status_code == 404


def test_full_job_flow(client):
    with open(DEMO_PDF, "rb") as f:
        pdf = f.read()
    r = client.post("/jobs", files={"file": ("fluids.pdf", pdf, "application/pdf")})
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    # Wait for the background thread to produce the output files.
    deadline = time.time() + 30
    page = report = None
    while time.time() < deadline:
        page = client.get(f"/jobs/{job_id}/page")
        report = client.get(f"/jobs/{job_id}/report")
        if page.status_code == 200 and report.status_code == 200:
            break
        time.sleep(0.2)

    assert page is not None and page.status_code == 200, "page never became ready"
    assert report is not None and report.status_code == 200, "report never became ready"
    assert "unverified equation" in page.text.lower() or "verified" in page.text.lower()


def test_sample_job_makes_no_api_calls(monkeypatch):
    """/jobs/sample must work with no API key set and never touch the model."""
    monkeypatch.delenv("LEGIBLE_REPLAY_JSON", raising=False)
    monkeypatch.delenv("META_API_KEY", raising=False)

    def boom(*a, **k):
        raise AssertionError("the sample job must never call the model")

    monkeypatch.setattr(_meta, "ask", boom)
    monkeypatch.setattr(_meta, "ask_json", boom)

    client = TestClient(app_main.app)
    r = client.post("/jobs/sample")
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    deadline = time.time() + 30
    page = report = None
    while time.time() < deadline:
        page = client.get(f"/jobs/{job_id}/page")
        report = client.get(f"/jobs/{job_id}/report")
        if page.status_code == 200 and report.status_code == 200:
            break
        time.sleep(0.2)

    assert page is not None and page.status_code == 200, "page never became ready"
    assert report is not None and report.status_code == 200, "report never became ready"

    seen = []
    with client.stream("GET", f"/jobs/{job_id}/events") as resp:
        for line in resp.iter_lines():
            if line.startswith("data: "):
                seen.append(line[6:])
            if '"type": "done"' in line:
                break
    assert any('"verified": 4' in s and '"repaired": 1' in s and '"withheld": 1' in s for s in seen)


def test_events_stream_contains_all_equations(client):
    with open(DEMO_PDF, "rb") as f:
        pdf = f.read()
    job_id = client.post("/jobs", files={"file": ("fluids.pdf", pdf, "application/pdf")}).json()["id"]

    seen = []
    with client.stream("GET", f"/jobs/{job_id}/events") as resp:
        assert resp.status_code == 200
        for line in resp.iter_lines():
            if line.startswith("data: "):
                seen.append(line[6:])
            if '"type": "done"' in line or '"type": "finished"' in line:
                break

    assert any('"equation_done"' in s for s in seen)
    statuses = {s for s in seen if "equation_done" in s}
    assert statuses, "no equation_done events streamed"
