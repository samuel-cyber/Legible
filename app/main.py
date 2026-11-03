"""Legible web app: upload a PDF, watch verification progress, read the result.

Run with:
    uvicorn app.main:app --reload

Endpoints
    GET  /                     the upload UI (app/static/index.html)
    POST /jobs                 upload a PDF (<= 20 MB), returns {"id": ...}
    GET  /jobs/{id}/events     Server-Sent Events of the pipeline's on_event dicts
    GET  /jobs/{id}/page       the generated accessible page (index.html)
    GET  /jobs/{id}/report     the generated verification report (report.html)

The pipeline runs in a background thread so the request returns immediately.
Events are buffered per job, so an EventSource that connects late (or
reconnects) still receives every event from the start.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import uuid
from dataclasses import dataclass, field

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse

# Make the repo root importable whether run via `uvicorn app.main:app` or directly.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pipeline import process, replay_reader  # noqa: E402

MAX_BYTES = 20 * 1024 * 1024          # 20 MB
CHUNK = 1024 * 1024
PDF_MAGIC = b"%PDF"

app = FastAPI(title="Legible", description="Verified STEM accessibility")

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


@dataclass
class Job:
    id: str
    outdir: str
    source_pdf: str
    events: list[dict] = field(default_factory=list)
    finished: bool = False
    error: str | None = None
    cond: threading.Condition = field(default_factory=threading.Condition)

    def emit(self, event: dict) -> None:
        with self.cond:
            if event.get("type") == "done":
                self.finished = True
            self.events.append(event)
            self.cond.notify_all()

    def fail(self, message: str) -> None:
        self.error = message
        self.emit({"type": "error", "message": message})

    def snapshot(self, index: int) -> tuple[list[dict], bool]:
        with self.cond:
            return self.events[index:], self.finished

    def wait_for_more(self, index: int, timeout: float = 15.0) -> None:
        with self.cond:
            if index >= len(self.events) and not self.finished:
                self.cond.wait(timeout)


JOBS: dict[str, Job] = {}
JOBS_LOCK = threading.Lock()


def _get_job(job_id: str) -> Job:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="unknown job id")
    return job


def _run_job(job: Job, use_glyphs: bool) -> None:
    """Background worker: run the pipeline and stream its events into the job.

    If LEGIBLE_REPLAY_JSON names a readings file, the job runs offline exactly
    like the CLI's --replay (Channel C off), which makes the app demoable and
    testable without an API key.
    """
    try:
        kwargs = {}
        replay = os.getenv("LEGIBLE_REPLAY_JSON")
        if replay:
            transcribe, repair = replay_reader(replay)
            kwargs.update(transcribe=transcribe, repair=repair, compare=False)
        result = process(
            job.source_pdf, job.outdir,
            use_glyphs=use_glyphs,
            on_event=job.emit,
            **kwargs,
        )
        job.emit({"type": "finished", "summary": result["summary"]})
    except Exception as e:  # no API key, bad PDF, model error, ...
        job.fail(f"{type(e).__name__}: {e}")
    finally:
        with job.cond:
            job.finished = True
            job.cond.notify_all()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/jobs")
async def create_job(file: UploadFile = File(...), use_glyphs: bool = True) -> JSONResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="please upload a .pdf file")

    job_id = uuid.uuid4().hex
    outdir = tempfile.mkdtemp(prefix=f"legible-{job_id}-")
    source_pdf = os.path.join(outdir, "source.pdf")

    # Stream to disk, refusing anything over the limit. Read the first chunk
    # first so we can check the %PDF magic before trusting the client.
    total = 0
    first = True
    with open(source_pdf, "wb") as f:
        while True:
            chunk = await file.read(CHUNK)
            if not chunk:
                break
            if first:
                if not chunk.startswith(PDF_MAGIC):
                    f.close()
                    os.remove(source_pdf)
                    raise HTTPException(status_code=400, detail="file is not a PDF")
                first = False
            total += len(chunk)
            if total > MAX_BYTES:
                f.close()
                os.remove(source_pdf)
                raise HTTPException(status_code=413, detail="PDF exceeds the 20 MB limit")
            f.write(chunk)

    if total == 0:
        os.remove(source_pdf)
        raise HTTPException(status_code=400, detail="empty upload")

    job = Job(id=job_id, outdir=outdir, source_pdf=source_pdf)
    with JOBS_LOCK:
        JOBS[job_id] = job
    threading.Thread(target=_run_job, args=(job, use_glyphs), daemon=True).start()
    return JSONResponse({"id": job_id})


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@app.get("/jobs/{job_id}/events")
def job_events(job_id: str) -> StreamingResponse:
    job = _get_job(job_id)

    def stream():
        index = 0
        while True:
            events, finished = job.snapshot(index)
            if events:
                for ev in events:
                    yield _sse(ev)
                index += len(events)
                continue
            if finished:
                break
            # Wait for more, or send a comment heartbeat to keep the link alive.
            job.wait_for_more(index, timeout=15.0)
            more, _ = job.snapshot(index)
            if not more:
                yield ": keep-alive\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/jobs/{job_id}/page")
def job_page(job_id: str) -> FileResponse:
    job = _get_job(job_id)
    path = os.path.join(job.outdir, "index.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=409, detail="page is not ready yet")
    return FileResponse(path, media_type="text/html; charset=utf-8")


@app.get("/jobs/{job_id}/report")
def job_report(job_id: str) -> FileResponse:
    job = _get_job(job_id)
    path = os.path.join(job.outdir, "report.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=409, detail="report is not ready yet")
    return FileResponse(path, media_type="text/html; charset=utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "jobs": len(JOBS)}
