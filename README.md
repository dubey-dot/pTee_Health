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
- **Real AI generation exists now**, gated behind `ANTHROPIC_API_KEY`. **PTee
  Assistant starts automatically** — there's no manual "Generate with AI"
  button. It calls `POST /assessments/{id}/diagnosis/generate` once when the
  Assessment screen loads, and again every time a test is completed (see
  below), so the confidence meter stays current as findings come in. This
  one Claude Opus 5 call (structured outputs,
  `app/services/engines/working_diagnosis_engine.py`) produces the working
  diagnosis, confidence %, and insights summary/tags together, and persists
  all of it. Without a configured key, that endpoint returns `502` with a
  clear message shown inline (with a "Retry" link) rather than a manual
  button — see Troubleshooting; every other endpoint is unaffected. No
  RAG/vector DB yet — this is a single structured-output call over the
  current patient/findings, not retrieval. Every call is also governed by
  standing rules loaded from `backend/app/services/engines/assessment_rules.md`
  — a plain-Markdown file that's read fresh on every request and sent to
  Claude as a dedicated system-prompt block Claude is instructed to follow
  before anything else. Edit that file to change what Claude must follow;
  no Python changes or backend restart needed — see `services/engines/rules.py`.
- **PTee Assistant now recommends what to test next**, its core purpose:
  "Recommended tests" (`RecommendedTestsPanel`, inside the PTee Assistant
  panel) calls `POST /assessments/{id}/recommendations` on demand
  ("Suggest tests") and returns a ranked **batch of up to 4 tests**, each
  with a Test Name, short Summary, and expandable "Why this test" — no
  per-test confidence score anywhere; only the overall assessment
  confidence above is shown, to avoid two competing numbers. For each
  test, the doctor either **deletes** the suggestion or writes/dictates
  findings directly under it (a text field + mic button, same
  Web-Speech-API pattern as Doctor's Notes) and clicks **"Mark
  complete"** — this creates a **real logged test**
  (`POST /assessments/{id}/tests`), no separate accept step. Completed
  tests appear in a **"Completed tests"** panel with a result summary and
  an **Edit** action (`PATCH /tests/{id}`) for redoing findings later.
  "Completed tests" reflects the same backend data as the older, separate
  "Log a test" panel — a test logged either way shows up in both places.
  Governed by its own rules file, `services/engines/recommendation_rules.md`,
  loaded alongside `assessment_rules.md` on every call
  (`app/services/engines/recommendation_engine.py`).
- **Doctor's Notes are real now**: the Patient Summary card's "Doctor's
  Notes" section supports both typed and voice-dictated notes, persisted
  per-assessment via `POST /assessments/{id}/notes`. Voice-to-text runs
  entirely client-side via the browser's Web Speech API (no new backend
  dependency) — the mic button transcribes into the same text field the
  doctor can review/edit before saving, and falls back to a visible inline
  message in browsers that don't support it (e.g. Firefox, Safari).
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
files are optional unless you change ports, or want the AI "Generate with
AI" button to actually work.** To set them up:

```powershell
# Backend — controls ALLOWED_ORIGINS (CORS), DATABASE_URL, ANTHROPIC_API_KEY
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

**AI generation (optional but recommended):** open `backend\.env` and set
`ANTHROPIC_API_KEY=` to a real key from `https://platform.claude.com`.
Without it, everything else in the app works normally — only the
"Generate with AI" button on the Assessment screen fails, with a visible
`502` error in the UI rather than a crash. Restart the backend after
changing `.env` (it's only read at process startup).

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
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app --port 8000
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

Or use the interactive Swagger UI at **http://localhost:8000/docs** — click
"Try it out" on any route and it builds a valid request body for you. This
is the easiest way to test POST/PATCH/DELETE endpoints, since (see below)
sending a JSON body via `curl.exe` from PowerShell has a real gotcha.

### Testing POST endpoints (curl)

> **PowerShell + `curl.exe` + JSON body gotcha:** PowerShell 5.1 mangles
> embedded double quotes when it forwards a string argument to a *native*
> executable like `curl.exe` — a plain `-d '{"name":"x"}'` will reach the
> server as corrupted JSON (`Expecting property name enclosed in double
> quotes`), even though the same string looks fine when you print it.
> Prefix the command with the `--%` **stop-parsing token** so PowerShell
> passes everything after it through completely literally, and
> double-escape the inner quotes (`\"`) the way you would in cmd.exe:
> ```powershell
> curl.exe --% -X POST <url> -H "Content-Type: application/json" -d "{\"key\":\"value\"}"
> ```
> (This isn't a project bug — it's how PowerShell 5.1 talks to any native
> `.exe`. `Invoke-RestMethod`/`Invoke-WebRequest` don't have this problem,
> but they're not `curl.exe`, which is what these examples standardize on.)

**Create a patient** — only `name` is required, every other field is optional
(matches the intake form on `/patients/new`):

```powershell
curl.exe --% -X POST http://localhost:8000/api/v1/patients -H "Content-Type: application/json" -d "{\"name\":\"Test Patient\",\"age\":30,\"gender\":\"Female\",\"chiefComplaint\":\"Lower back pain\"}"
```

Copy the `"id"` from the response (e.g. `patient-6ee61b2a`) for the next step.

**Create an assessment for that patient** — no request body:

```powershell
curl.exe --% -X POST http://localhost:8000/api/v1/patients/patient-6ee61b2a/assessments
```

Copy the `"id"` from *this* response (e.g. `assessment-837ac696`) for the
next two steps.

**Log a finding against that assessment:**

```powershell
curl.exe --% -X POST http://localhost:8000/api/v1/assessments/assessment-837ac696/findings -H "Content-Type: application/json" -d "{\"tag\":\"JOINT\",\"label\":\"Hip Flexion Test\"}"
```

**Log a test against that assessment** — `type` must be `joint`, `muscle`, or `gait`:

```powershell
curl.exe --% -X POST http://localhost:8000/api/v1/assessments/assessment-837ac696/tests -H "Content-Type: application/json" -d "{\"type\":\"joint\",\"name\":\"Single leg bridge\",\"result\":\"Weak on right\"}"
```

**Edit a logged test's result** — copy the `"id"` from the response above (e.g. `test-a1b2c3d4`); only `result` can be changed, not the type/name:

```powershell
curl.exe --% -X PATCH http://localhost:8000/api/v1/tests/test-a1b2c3d4 -H "Content-Type: application/json" -d "{\"result\":\"Redone — now symmetric\"}"
```

**Add a doctor's note against that assessment** — `source` is optional
(`"typed"` or `"voice"`, defaults to `"typed"`; the frontend sets `"voice"`
itself when the note came from the mic button):

```powershell
curl.exe --% -X POST http://localhost:8000/api/v1/assessments/assessment-837ac696/notes -H "Content-Type: application/json" -d "{\"content\":\"Patient reports improved ROM since last visit.\"}"
```

**Get a batch of recommended tests for that assessment** — no request body,
returns up to 4 ranked tests; requires `ANTHROPIC_API_KEY` like
`/diagnosis/generate` does:

```powershell
curl.exe --% -X POST http://localhost:8000/api/v1/assessments/assessment-837ac696/recommendations
```

**What to check on each response:**
- Status `201`, and the JSON body echoes back what you sent plus a
  generated `id` and any FK field (`patientId`/`assessmentId`) filled in.
- Missing a required field → `422` with a body like
  `{"detail":[{"type":"missing","loc":["body","name"],...}]}` — this is
  correct behavior, not a bug.
- POSTing to a nonexistent parent (e.g. a patient id that doesn't exist) →
  `404 {"detail":"Patient not found"}`, not a `500`.

**Automated coverage:** every one of these POST endpoints already has
passing tests in `backend/tests/` — see `test_patients.py::test_create_patient`,
`test_assessments.py::test_create_assessment`, `test_findings.py::test_create_finding`,
`test_tests.py::test_create_test`, and `test_notes.py::test_create_note_typed`.
Running `pytest` (see Testing above)
re-verifies all of this automatically without leaving data behind (each
test rolls back). The curl walkthrough above is for manual/exploratory
testing and *does* leave real rows in your dev database — there's no
`DELETE /patients` endpoint yet to clean them up (see Known Issues in
`Progress.md`), so expect test patients created this way to stick around
until you reset via `docker compose down -v` (see Stopping above).

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
- [ ] `GET /api/v1/assessments/assessment-1/insights` → 200, non-empty `summary` (`tags` is `[]` until `/diagnosis/generate` has been run at least once — expected, not a bug)
- [ ] A GET for a nonexistent ID (e.g. `/api/v1/patients/does-not-exist`) → 404, not a 500
- [ ] `/docs` (Swagger UI) loads and lists all routers: patients, assessments, findings, diagnosis, tests, insights, notes, recommendations

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

**AI generation (automatic — no "Generate with AI" button)**
- [ ] Loading `/assessment/{id}` fires `POST /diagnosis/generate` automatically (check the Network tab) — the CONFIDENCE meter briefly shows "Analyzing…" with a spinner instead of the percentage while it's in flight
- [ ] Without `ANTHROPIC_API_KEY` set: a visible red error message appears with an inline **"Retry"** link (not a full button); existing diagnosis/confidence/insights are **unchanged**, not cleared; clicking Retry re-attempts
- [ ] `POST /api/v1/assessments/assessment-1/diagnosis/generate` with no key configured → `502`, body contains `"ANTHROPIC_API_KEY is not configured"` — not a `500`
- [ ] With a real key configured: the auto-triggered call updates the diagnosis text, confidence meter, and Insights panel content together (one call generates all three); `GET /assessments/assessment-1/insights` afterward returns the newly generated `tags`, no longer `[]`
- [ ] Completing a recommended test, or logging a test via the separate "Log a test" panel, **re-triggers** `POST /diagnosis/generate` automatically — confirm a second request fires and the confidence meter updates again without any manual action
- [ ] Renaming/deleting `backend/app/services/engines/assessment_rules.md` and calling `/diagnosis/generate` → `502`, body contains `"Assessment rules file not found"` — not a `500` (restore the file afterward)

**Doctor's Notes**
- [ ] Patient Summary card's "Doctor's Notes" header count starts at the real note count (`0` on a fresh assessment), not a hardcoded number
- [ ] Typing a note and clicking "Save note" adds it to the list immediately, clears the textarea, and increments the count — **and it's still there after a page reload** (proves it's persisted via `POST /assessments/{id}/notes`, not local state)
- [ ] Clicking the mic button in a browser that supports the Web Speech API (Chrome/Edge desktop, with mic permission granted) starts listening (button turns solid/shows a stop icon), transcribes speech into the same textarea, and stops on click again or on its own after a pause
- [ ] Clicking the mic button in a browser/environment where the Web Speech API is unavailable (e.g. headless automation, Firefox, Safari) shows the inline "Voice input isn't supported in this browser" message instead of throwing — verified via headless-browser Playwright testing, since real microphone dictation can't be exercised outside a real browser session with mic access
- [ ] A note saved via the mic shows a "· dictated" tag next to its timestamp in the list; a typed note doesn't

**Recommended tests**
- [ ] The "Recommended tests" section renders inside the PTee Assistant card itself — between the diagnosis block and the findings checklist — not as a separate card above/outside it
- [ ] Clicking "Suggest tests" shows a spinner, then up to 4 ranked test cards — Test Name, short Summary, "Why this test" toggle — with **no confidence score anywhere on the cards**; only the top-of-panel CONFIDENCE meter shows a number
- [ ] Clicking "Why this test" expands the fuller reasoning inline; clicking again collapses it
- [ ] Each pending card has a **Delete** (trash icon) button and a **FINDINGS** text field + mic button; typing/dictating text and clicking "Mark complete" removes the card from the pending list and adds it to "Completed tests" below — confirmed via `GET /assessments/assessment-1/tests` showing a new row with the typed result
- [ ] Marking a test complete also **re-triggers automatic diagnosis generation** (see AI generation checks above)
- [ ] Clicking Delete on a pending card just removes it locally — no backend call, confirmed via the Network tab
- [ ] Clicking "Reset review" fetches a brand-new batch, discarding all current pending cards (completed tests are unaffected — they're real backend data, not part of the batch)
- [ ] "Completed tests" shows the real result text for each test, plus an **Edit** link that reveals an inline textarea; saving calls `PATCH /tests/{id}` and the new text persists after a page reload
- [ ] A test logged via the separate "Log a test" panel (not from a recommendation) also appears in "Completed tests" — both flows write to the same underlying test data
- [ ] `POST /api/v1/assessments/assessment-1/recommendations` with no key configured → `502`, same failure convention as `/diagnosis/generate`
- [ ] `PATCH /api/v1/tests/{id}` with a nonexistent id → `404`, not `500`
- [ ] Fetching a batch does not change the assessment's `version` or anything else in `GET /assessments/{id}` — purely advisory; completing/editing a test *does* bump the version (same as any other findings/tests write)
- [ ] Diagnosis Agree/Update/Fully-change buttons and the generate button don't interfere with each other — both write to the same `Assessment`, and the UI reflects whichever ran last

**Error handling**
- [ ] Stop the backend, then load `/assessment` → should fail loudly (visible Next.js error overlay/500), not silently render stale/empty data
- [ ] With backend running but frontend pointed at the wrong `NEXT_PUBLIC_API_BASE_URL`, browser console shows a clear fetch/CORS error, not a silent failure
- [ ] Browser devtools console has **zero** uncaught errors during normal use of the checklist above

## Troubleshooting

**PTee Assistant shows a red error / `POST .../diagnosis/generate` returns `502`**
Almost always `ANTHROPIC_API_KEY` isn't set. Check the exact error text
returned in the response body (or the red text under the confidence meter,
with a "Retry" link) — `"ANTHROPIC_API_KEY is not configured"` means the
key is missing entirely (set it in `backend/.env`, see Environment files
above, then restart the backend); any other message is a real upstream
failure (bad key, network, rate limit, Anthropic outage) surfaced as-is
from the `anthropic` SDK. Diagnosis generation and test recommendations
are the *only* things in the app that depend on an external service —
everything else keeps working normally regardless.

**Every assessment page load now makes a real Claude API call — expect it, don't chase it as a bug**
Diagnosis generation is automatic (no more manual "Generate with AI"
button) — it fires once whenever `/assessment/{id}` mounts, and again
every time a test is completed. This means simply opening or refreshing
an assessment screen during development will call the real Anthropic API
if `ANTHROPIC_API_KEY` is set, consuming quota each time — including on
the demo `/assessment` route, which will overwrite its seeded fixture
diagnosis ("Load-related right anterior knee pain," 64%) with a freshly
generated one the first time it's viewed after this change. If you want
to avoid burning API calls while doing unrelated frontend work, unset
`ANTHROPIC_API_KEY` locally (you'll just see the inline error/Retry state
instead, which is also useful for testing that path).

**`"Assessment rules file not found"` / `"Recommendation rules file not found"` in a `502` response**
`backend/app/services/engines/assessment_rules.md` or `recommendation_rules.md`
is missing — every "Generate with AI" and "Suggest next test" call loads
both fresh and fails loudly rather than silently skipping the rules (see
`services/engines/rules.py`). Restore the file (git checkout, or recreate
it) and retry; no restart needed since both are read fresh on every call.

**`curl.exe -d '{"key":"value"}'` from PowerShell returns `Expecting property name enclosed in double quotes`**
PowerShell 5.1 mangles embedded double quotes when forwarding an argument to
a native `.exe`. See "Testing POST endpoints (curl)" above for the `--%`
stop-parsing-token workaround — or just use the Swagger UI at `/docs`
instead, which sidesteps this entirely.

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

**Backend: uvicorn keeps printing `Reloading...` / `CancelledError` / `KeyboardInterrupt` in a loop and never settles**
Not a crash — each cycle still ends with `Application startup complete`; the
traceback is just uvicorn's normal (harmless) teardown of the *previous*
worker process each time `--reload` fires. The real problem is *why* it keeps
firing: by default `--reload` watches the entire working directory, including
`.venv/Lib/site-packages` — and since this project lives under OneDrive,
background sync continuously touches file timestamps inside `.venv`
(including the `anthropic` SDK's own source files), which WatchFiles reads as
changes and reloads on. Fixed by scoping the watch to `app/` only
(`--reload-dir app`, already reflected in the run commands above). If it's
still noisy, quit OneDrive syncing for this folder or move the project
outside OneDrive entirely.

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
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app --port 8000
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
