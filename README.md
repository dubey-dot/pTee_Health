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

**Phase 1** (UI) and **Phase 2** (backend integration) are complete for the
**Patient Intake / Assessment screen** — the only fully built screen so far.
Treatment, Home Plan, and Evaluation tabs render labels only, no content yet.

Current implementation:

- **Frontend**: Next.js 16 (App Router, Turbopack), React 19, TypeScript,
  Tailwind v4, shadcn/ui. Two routes: `/` (hero/mic entry) and `/assessment`.
  `/assessment` is an async Server Component that fetches its initial data
  (patient, assessment, findings, insights) from the backend, then hands off
  to TanStack Query on the client for interactive mutations (delete/relabel
  findings, diagnosis actions, status toggling, log-a-test).
- **Backend**: FastAPI, layered `api/v1` (routers) → `services` (business
  logic) → `schemas` (Pydantic contracts, camelCase over the wire) →
  `services/store.py` (in-memory fixture store, seeded with one demo patient
  and assessment). **No real database yet** — backend state resets on
  restart. See the Backend APIs table in `Progress.md` for the full endpoint
  list.
- **No AI/RAG yet.** Working diagnosis, confidence, and insights are served
  by the backend but are still static fixture data, not model-generated.
  `app/services/insights.py` and the diagnosis fields in
  `app/services/assessments.py` are the seams reserved for that (Phase 4).
- **No auth, no persistence, no deployment yet** (Phases 3, 5).

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Node.js | 20+ | Next.js 16 requirement |
| npm | bundled with Node | |
| Python | 3.13 | matches `backend/.venv` |
| Git | any recent | |
| PowerShell | 5.1+ (Windows) | commands below use PowerShell syntax |

Verify what you have:

```powershell
node --version
npm --version
py -3.13 --version
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
```

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

**Start the backend first** — `/assessment` fetches from it server-side on
first load and will 500 if it's not up yet. Use two separate PowerShell
windows/tabs (both commands are long-running and block the terminal).

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

## Testing

There is no automated test suite yet (no pytest, no Jest/Vitest) — "testing"
today means static checks plus the manual verification checklist below.

```powershell
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
Assessment screen. Restart both servers first for a clean baseline (fixture
data resets on backend restart).

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
- [ ] Mic button on `/` navigates to `/assessment`
- [ ] `/assessment` loads directly (not just via navigation from `/`) without a 500
- [ ] Browser devtools Network tab shows requests to `localhost:8000/api/v1/...`, not hardcoded/mocked data

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
- [ ] Restarting the backend resets all data back to the seeded Ankita Sharma fixture (expected — no persistence yet, not a bug)

**Error handling**
- [ ] Stop the backend, then load `/assessment` → should fail loudly (visible Next.js error overlay/500), not silently render stale/empty data
- [ ] With backend running but frontend pointed at the wrong `NEXT_PUBLIC_API_BASE_URL`, browser console shows a clear fetch/CORS error, not a silent failure
- [ ] Browser devtools console has **zero** uncaught errors during normal use of the checklist above

## Troubleshooting

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
