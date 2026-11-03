# Deploying the Legible web app

`app/main.py` is the FastAPI app behind `uvicorn`. Both routes below run the
exact same code as the CLI (`pipeline.py`) — nothing in the decision rule
changes between local, CLI and deployed use.

Two defaults that matter for a public deployment:

- **Region finder stays on `heuristic`** (the default `process()` already
  uses, and `app/main.py` never overrides it). The alternative, `--regions
  model`, spends one Muse Spark call per page just to *propose* equation
  boxes — fine for an evaluation run you trigger yourself, not something a
  public upload endpoint should do on every stranger's PDF. Nothing to
  change here; just don't add a `regions=` override to the `process(...)`
  call in `app/main.py` if you're copying code around.
- **Upload size is capped at 20 MB** (`MAX_BYTES` in `app/main.py`), enforced
  while streaming to disk before anything is parsed. Raise it only if you
  also plan for the matching memory/time cost — a bigger PDF means more
  equations, each a few Muse Spark calls.

## Option A — Render (recommended; no Dockerfile needed)

1. Push this repo to GitHub (or GitLab).
2. On [render.com](https://render.com): **New → Web Service**, connect the
   repo.
3. Settings:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     (Render injects `$PORT`; don't hardcode a port number)
   - **Instance type:** the free/starter tier is enough — the app does no
     heavy local compute itself, it waits on Muse Spark's API.
4. **Environment → Add Environment Variable** (do this in the dashboard, not
   in a committed file):
   - `META_API_KEY` = your key, marked as a **secret**
   - `META_BASE_URL` = `https://api.meta.ai/v1`
   - `META_MODEL` = `muse-spark-1.3`
5. Deploy. Render builds and starts the service; the health check endpoint is
   `GET /health` (already defined in `app/main.py`) if you want to wire one up
   under **Settings → Health Check Path**.
6. Visit the service URL — it serves `app/static/index.html`, the upload UI.

No Dockerfile is used in this path; Render's native Python buildpack reads
`requirements.txt` directly.

## Option B — Hugging Face Spaces (Docker SDK)

Spaces need a `Dockerfile` (provided at the repo root) and a tiny bit of YAML
front matter identifying the Space.

1. Create a Space at [huggingface.co/new-space](https://huggingface.co/new-space),
   **SDK: Docker**, **Docker template: Blank**.
2. Push this repo's contents to the Space's git remote (Spaces work like any
   git repo: `git remote add space https://huggingface.co/spaces/<you>/<name>`,
   then push `main`).
3. At the very top of whatever file HF treats as the Space's README (it looks
   for YAML front matter in `README.md`), add:
   ```yaml
   ---
   title: Legible
   sdk: docker
   app_port: 7860
   ---
   ```
   Do this in the Space's own README, not this project's `README.md` — keep
   the two separate (e.g. copy this project's README content below the front
   matter, or keep the Space's README minimal and link back here).
4. **Settings → Variables and secrets** on the Space:
   - `META_API_KEY` → add as a **secret** (never a public variable)
   - `META_BASE_URL` → `https://api.meta.ai/v1` (variable is fine, it's not
     sensitive, but secret works too)
   - `META_MODEL` → `muse-spark-1.3`
5. The Space rebuilds the Dockerfile automatically on push. It listens on
   `7860` by default (set in the Dockerfile's `ENV PORT=7860`); the `app_port`
   in the front matter must match.
6. Open the Space — same upload UI as Render.

## Either way

- **Never commit `.env`** — it's already gitignored. The three `META_*`
  values are read from the environment at call time
  (`clients/meta.py`'s `_client()`); nothing in the code prints or logs the
  key.
- **Offline/demo mode in production:** if you ever want a deployed instance
  that answers without spending API calls (e.g. a judge-facing demo button),
  set `LEGIBLE_REPLAY_JSON` to a readings file as `app/main.py` already
  supports — `_run_job` picks it up and forces `compare=False`, exactly like
  the CLI's `--replay`. Don't set this in a deployment meant to verify real
  uploads; it's a fixed-answer fixture, not a general PDF checker.
- **Logs:** Render and HF Spaces both capture stdout; `pipeline.py`'s
  `on_event` callback in the web app only ever emits the plain-language
  status strings (see the README's wording in the progress list), never the
  API key or raw request bodies.
