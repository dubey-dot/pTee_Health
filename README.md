# PTee Health

AI-powered Clinical Decision Support Platform for physiotherapists.

> This README covers local setup, running, and testing. For architecture and
> project-status detail, see [`Progress.md`](Progress.md) (standing source of
> truth, updated after every meaningful task) and
> [`BACKEND_INTEGRATION_PLAN.md`](BACKEND_INTEGRATION_PLAN.md) (backend
> integration roadmap, Phases 2-5).
>
> **Keep this file updated** whenever a new feature, script, endpoint, or
> setup step is added — it should always reflect how to actually run the
> project today.

## Project Overview

**Phase 1** (UI), **Phase 2** (backend integration), and a persistence
migration (Postgres) are complete for the **Patient Intake / Assessment
screen**. Multi-patient support now exists too — patients aren't hardcoded
to a single demo record anymore. Treatment, Home Plan, and Evaluation tabs
still render labels only, no content yet.

Current implementation:

- **Frontend**: Next.js 16 (App Router, Turbopack), React 19, TypeScript,
  Tailwind v4, shadcn/ui. Routes: `/` (hero/mic entry), `/patients/new`
  (intake form — creates a patient + their first assessment), `/patients`
  (list of all patients), `/patients/[patientId]` (that patient's
  assessments), `/assessment` (the original seeded demo patient, kept for
  backward compatibility), and `/assessment/[assessmentId]` (any assessment
  by id — what the intake flow and patient list route into).
  `/assessment` is an async Server Component that fetches its initial data
  (patient, assessment, findings, insights) from the backend, then hands off
  to TanStack Query on the client for interactive mutations (delete/relabel
  findings, diagnosis actions, status toggling, log-a-test).
- **Backend**: FastAPI, layered `api/v1` (routers) → `services` (business
  logic) → `schemas` (Pydantic contracts, camelCase over the wire) →
  `models`/`db` (SQLAlchemy 2.x, **Postgres-backed** — persistence via
  `docker-compose.yml` + Alembic migrations). Data now survives a backend
  restart. Seeded with one demo patient (`patient-1`, Ankita Sharma) and one
  demo assessment (`assessment-1`) via an Alembic data migration. See the
  Backend APIs table in `Progress.md` for the full endpoint list.
- **No AI/RAG yet.** Working diagnosis, confidence, and insights are served
  by the backend but are still static fixture data, not model-generated.
  `app/services/insights.py` and the diagnosis fields in
  `app/services/assessments.py` are the seams reserved for that (a later
  phase — see `BACKEND_INTEGRATION_PLAN.md`).
- **No auth, no deployment yet.**
- **Automated tests exist now**: `backend/tests/` (pytest + `httpx.TestClient`,
  runs against a real Postgres test database) — see Testing below.

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Node.js | 20+ | Next.js 16 requirement |
| npm | bundled with Node | |
| Python | 3.13 | matches `backend/.venv` |
| Docker Desktop | any recent | runs the local Postgres database via `docker-compose.yml` |
| Git | any recent | |
| PowerShell | 5.1+ (Windows) | commands below use PowerShell syntax |

Verify what you have:

```powershell
node --version
npm --version
py -3.13 --version
docker --version
git --version
```

## Local Setup (one-time)

Run these once after cloning, or whenever `requirements.txt` /
`package.json` change.

```powershell
# 1. Backend: create venv + install dependencies
Set-Location backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Set-Location ..

# 2. Frontend: install dependencies
Set-Location frontend
npm install
Set-Location ..

# 3. Database: start Postgres (Docker Desktop must be running first)
Set-Location backend
docker compose up -d
Set-Location ..
```

### Database migrations (one-time, and whenever new migrations are added)

With Postgres running (step 3 above):

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m alembic upgrade head
Set-Location ..
```

This creates the schema and seeds the same demo patient/assessment data that
used to be hardcoded in `store.py` — behavior-neutral for local dev. Data
now **persists** across backend restarts (a real change from earlier: the
old in-memory fixture store reset every restart, Postgres doesn't).

### Environment files

Both apps have sane defaults for local dev (backend allows
`http://localhost:3000`; frontend calls `http://localhost:8000`), so **env
files are optional unless you change ports**. To set them up anyway:

```powershell
# Backend — controls ALLOWED_ORIGINS (CORS)
Copy-Item backend\.env.example backend\.env

# Frontend — controls NEXT_PUBLIC_API_BASE_URL
Copy-Item frontend\.env.example frontend\.env.local
```

> **Windows gotcha:** if you (re)create `backend\.env` yourself instead of
> copying the example, don't use `Out-File -Encoding utf8` or `>` /
> `Set-Content` from PowerShell — they write a UTF-8 **BOM**, which breaks
> `pydantic-settings` parsing (`Extra inputs are not permitted` on
> `allowed_origins`). Copy the example file, or use
> `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::ASCII)`
> if you must write it by hand.

## Running Locally

**Start Postgres, then the backend, then the frontend** — `/assessment`
fetches from the backend server-side on first load (500s if it's not up),
and the backend now needs Postgres reachable to start meaningfully (it'll
still boot with Postgres down, but every route will fail). Use two separate
PowerShell windows/tabs for the two long-running dev servers.

**Database** (from the repo root, if not already running from setup):

```powershell
Set-Location backend
docker compose up -d
Set-Location ..
```

**Terminal 1 — backend** (from the repo root):

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Leave this running. You should see `Application startup complete.` and
`Uvicorn running on http://127.0.0.1:8000`.

**Terminal 2 — frontend** (from the repo root):

```powershell
Set-Location frontend
npm run dev
```

Leave this running. Then open **http://localhost:3000** (home) or
**http://localhost:3000/assessment** directly.

### Stopping

`Ctrl+C` in each terminal. If a port is stuck afterward (see
Troubleshooting), free it explicitly:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 3000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Postgres keeps running in the background (Docker) even after you stop the
app servers — that's fine, leave it running between sessions, or:

```powershell
Set-Location backend
docker compose stop   # stops the container, keeps data
# docker compose down    # stops + removes the container (data volume survives)
Set-Location ..
```

## Testing

**Backend automated tests exist now** (`backend/tests/`, pytest +
`httpx.TestClient`) — the frontend still has no automated test suite (no
Jest/Vitest), so frontend "testing" remains static checks plus the manual
checklist below.

```powershell
# Backend: automated test suite (needs Postgres running — see Local Setup)
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -v
Set-Location ..

# Frontend: lint (ESLint flat config)
Set-Location frontend
npm run lint

# Frontend: production build (also runs the TypeScript compiler)
npm run build
Set-Location ..

# Backend: confirm the app imports cleanly and every route registers
Set-Location backend
.\.venv\Scripts\python.exe -c "from app.main import app; print([r.path for r in app.routes])"
Set-Location ..
```

The pytest suite creates its own `ptee_health_test` database automatically
on the same Postgres server (doesn't touch your dev data in `ptee_health`),
and each test runs inside a transaction that's rolled back afterward — safe
to run repeatedly, no manual cleanup needed.

### Backend API smoke test (curl)

With the backend running (Terminal 1 above), from any PowerShell window:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/api/v1/patients/patient-1
curl.exe http://localhost:8000/api/v1/assessments/assessment-1
curl.exe http://localhost:8000/api/v1/assessments/assessment-1/findings
curl.exe http://localhost:8000/api/v1/assessments/assessment-1/insights
```

Or use the interactive Swagger UI at **http://localhost:8000/docs** to try
every endpoint (including PATCH/POST/DELETE mutations) by hand.

## Manual Verification Checklist

Run through this after any change that touches data flow, routing, or the
Assessment screen. To reset to a clean baseline, re-run the seed migration
(`docker compose down -v` to wipe the volume, then `docker compose up -d` +
`alembic upgrade head` again) — a plain backend restart no longer resets
data, since it's Postgres-backed now.

**Backend / API connectivity**
- [ ] `GET /health` → `200 {"status":"ok"}`
- [ ] `GET /api/v1/patients/patient-1` → 200, returns Ankita Sharma with all 9 summary fields populated
- [ ] `GET /api/v1/assessments/assessment-1` → 200, `status: "completed"`, `confidence: 64`
- [ ] `GET /api/v1/assessments/assessment-1/findings` → 200, 5 findings, first one (`pelvis-shift`) has a non-null `detail`
- [ ] `GET /api/v1/assessments/assessment-1/insights` → 200, non-empty `summary` and `tags`
- [ ] A GET for a nonexistent ID (e.g. `/api/v1/patients/does-not-exist`) → 404, not a 500
- [ ] `/docs` (Swagger UI) loads and lists all routers: patients, assessments, findings, diagnosis, tests, insights

**Frontend routing**
- [ ] `/` loads, hero headline rotates between two variants every ~4s
- [ ] Mic button on `/` navigates to `/patients/new` (the intake form — not `/assessment` directly anymore)
- [ ] `/assessment` (the original seeded demo, no id) still loads directly without a 500 — kept for backward compatibility
- [ ] Browser devtools Network tab shows requests to `localhost:8000/api/v1/...`, not hardcoded/mocked data

**Multi-patient flow**
- [ ] `/patients/new`: filling in just a name and submitting creates a patient and routes to `/assessment/{new-id}` — every other field is optional
- [ ] The new assessment screen shows the just-entered patient fields, 0 findings, `status: "reviewing"`, 0% confidence ("Low") — a genuinely fresh assessment, not the demo data
- [ ] `/patients` lists both the new patient and the original seeded "Ankita Sharma" — creating a patient never affects the demo one
- [ ] Clicking a patient on `/patients` goes to `/patients/{id}`, listing their assessment(s); "+ New assessment" there creates another assessment for the *same* patient and routes to it
- [ ] TopNav's "New Patients" / "Existing Patients" links go to `/patients/new` / `/patients` respectively (previously inert/wrong)

**UI functionality — Assessment screen**
- [ ] Patient Summary card shows "Ankita Sharma" and all fields; collapse/expand toggle works
- [ ] PTee Assistant panel shows confidence meter (64%, "Good") and diagnosis text
- [ ] Clicking a diagnosis action (Agree / Update / Fully change) highlights it and persists after reload
- [ ] "Reopen diagnosis" / "Complete" toggles the status pill correctly and persists after reload
- [ ] Deleting a finding (trash icon) removes it immediately **and it stays gone after a page reload** (proves the mutation hit the backend, not just local state)
- [ ] "Type finding instead" relabel: edited text persists after reload
- [ ] "Log a test" panel: Save is disabled until a test name is entered; saving closes the panel and does not error
- [ ] Insights panel expand/collapse works; content matches `/api/v1/assessments/assessment-1/insights`

**Data flow / state management**
- [ ] Editing a finding in one browser tab and reloading a second tab shows the same change (proves shared backend state, not per-tab local state)
- [ ] Restarting the backend (`Ctrl+C` + re-run `uvicorn`) **keeps** all prior edits — data now persists in Postgres, this is the opposite of the old fixture-store behavior and confirms the DB is actually being used
- [ ] `docker compose down -v` + `docker compose up -d` + `alembic upgrade head` restores the clean seeded baseline (Ankita Sharma, 5 findings)

**Error handling**
- [ ] Stop the backend, then load `/assessment` → should fail loudly (visible Next.js error overlay/500), not silently render stale/empty data
- [ ] With backend running but frontend pointed at the wrong `NEXT_PUBLIC_API_BASE_URL`, browser console shows a clear fetch/CORS error, not a silent failure
- [ ] Browser devtools console has **zero** uncaught errors during normal use of the checklist above

## Troubleshooting

**Backend fails to start / every route 500s with a connection error**
Postgres isn't running. `docker compose up -d` from `backend/` (Docker
Desktop must be open first — it does not auto-start). Confirm with
`docker ps` — you should see `ptee_health_postgres` as `Up`/`healthy`.

**`docker compose up -d` fails to bind port 5433, or Postgres data looks wrong**
`docker-compose.yml` publishes Postgres on host port **5433**, not 5432,
specifically to avoid clashing with a native Postgres install. If you have
something else already on 5433, change the port mapping in
`backend/docker-compose.yml` and update `DATABASE_URL` (env var or
`backend/.env`) to match.

**`alembic upgrade head` fails with a connection error**
Same root cause as above — Postgres isn't reachable yet. Also confirm
`DATABASE_URL` (default: `postgresql+psycopg://ptee:ptee@localhost:5433/ptee_health`,
matching `docker-compose.yml`'s defaults) hasn't been overridden to point
somewhere stale in your shell environment or `backend/.env`.

**`pytest` fails with a connection/database error**
Same prerequisite — Postgres must be running (`docker compose up -d`). The
test suite creates its own `ptee_health_test` database on first run; if
that database gets into a bad state, drop it manually
(`docker exec -it ptee_health_postgres psql -U ptee -d postgres -c 'DROP DATABASE ptee_health_test;'`)
and re-run — it'll be recreated automatically.

**`Activate.ps1 cannot be loaded because running scripts is disabled`**
Don't activate the venv — call its `python.exe` directly instead, as shown
throughout this README (`.\.venv\Scripts\python.exe -m ...`). This sidesteps
PowerShell's script execution policy entirely.

**Backend: `[Errno 10048] error while attempting to bind on address ... only one usage of each socket address`**
Something is already listening on port 8000 — often a previous `uvicorn`
process that didn't shut down cleanly. Find and stop it:
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object OwningProcess
Stop-Process -Id <OwningProcess> -Force
```
If `Stop-Process` can't find that PID (rare orphaned-socket state), just run
the backend on a different port (`--port 8010`) and set
`NEXT_PUBLIC_API_BASE_URL` to match — don't spend time fighting a phantom
listener.

**Page shows stale/placeholder content that doesn't match the source**
(e.g. `/` renders a bare `PTee Health` line instead of the hero section, and
the Next.js dev indicator badge shows "N — 1 Issue" in the bottom-left
corner) — the `npm run dev` process serving that tab has been running since
before the relevant files changed and Turbopack's HMR didn't fully
reconcile. Stop it and start a fresh one:
```powershell
Get-NetTCPConnection -LocalPort 3000 -State Listen | Select-Object OwningProcess
Stop-Process -Id <OwningProcess> -Force
Set-Location frontend
npm run dev
```
Then hard-refresh the browser tab. If restarting doesn't fix it, also clear
Turbopack's cache: `Remove-Item frontend\.next -Recurse -Force` before
restarting.

**Frontend: `Another next dev server is already running` / port 3000 busy**
Same idea — a previous `npm run dev` is still holding the port:
```powershell
Get-NetTCPConnection -LocalPort 3000 -State Listen | Select-Object OwningProcess
Stop-Process -Id <OwningProcess> -Force
```

**Browser console shows a CORS error** (`No 'Access-Control-Allow-Origin' header`)
The frontend's origin isn't in the backend's `ALLOWED_ORIGINS`. Either run
the frontend on port 3000 (the default the backend already allows), or set
`ALLOWED_ORIGINS` to include your actual frontend origin before starting the
backend:
```powershell
$env:ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:3010"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**`/assessment` fails with `API GET /patients/patient-1 failed: 404`**
The backend that's actually answering requests is running old code (e.g. a
stale process from before a backend restructure) or isn't up at all. Confirm
`GET http://localhost:8000/api/v1/patients/patient-1` succeeds via curl
first, independent of the frontend.

**Changed `frontend/.env.local` but the app still uses the old value**
Next.js only reads env files at dev-server startup. Stop (`Ctrl+C`) and
restart `npm run dev`.

**Backend `.env` values seem to be ignored / `Extra inputs are not permitted` error on startup**
See the Windows BOM gotcha under Environment files above — recreate the file
via `Copy-Item` rather than PowerShell redirection.

**`npm audit` reports vulnerabilities**
3 high-severity transitive-dependency vulnerabilities are a known, tracked
issue (see `Progress.md` → Known Issues) — not caused by your local setup.
