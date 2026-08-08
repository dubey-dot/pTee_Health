# PTee Health — Project Progress

Single source of truth for project status. Updated after every meaningful task — entries are appended, not overwritten.

---

## Project Overview

PTee Health is an AI-powered Clinical Decision Support Platform for physiotherapists. **Phase 1** (current phase) is scoped strictly to the **Patient Intake / Assessment screen** of the clinical journey, replicated pixel-for-pixel from Lovable-generated UI reference screenshots, backed by a lightweight FastAPI service that will later be swapped for real AI/RAG/clinical services without requiring frontend changes.

Long-term vision (not yet started): an AI-powered clinical reasoning pipeline (RAG over clinical knowledge), healthcare API integrations, and full patient journey coverage (Assessment → Treatment → Home Plan → Evaluation).

## Architecture

- **Frontend**: Next.js App Router. Server Components for static layout; Client Components (`"use client"`) for anything with interactive state (panels, toggles, forms). No global state manager — each interactive component owns its local `useState`.
- **Backend**: FastAPI, layered `api/v1` (routers) → `services` (business logic) → `schemas` (Pydantic contracts) → `models`/`db` (SQLAlchemy 2.x ORM models, Postgres). Persistence via Alembic migrations against a local Postgres run through `docker-compose.yml`; seeded with the same demo data that used to be hardcoded in the frontend. Contract: the frontend consumes the backend "exactly as if it were production," so swapping the fixture-backed `diagnosis_service`/`insight_service` for the future RAG pipeline requires no frontend rewrite — see `BACKEND_INTEGRATION_PLAN.md`.
- **Data flow today**: The Assessment screen fetches its initial data (patient summary, assessment/diagnosis, findings, insights) server-side from FastAPI in an async Server Component, then hands off to TanStack Query on the client for interactivity — delete/relabel findings, diagnosis actions, status transitions, and "Log a test" are all real mutations against the backend's in-memory store (optimistic UI on delete/relabel, with rollback on error). No hardcoded finding/diagnosis/insight data remains in frontend components.
- **Repo layout**: `frontend/` and `backend/` as sibling directories at repo root (see Folder Structure).

## Technology Stack

**Frontend**
- Next.js 16.2.12 (App Router, Turbopack)
- React 19.2.4 / React DOM 19.2.4
- TypeScript 5
- Tailwind CSS v4 (CSS-first config, `@theme inline` tokens)
- shadcn/ui — `base-nova` preset (Base UI primitives via `@base-ui/react`, not Radix)
- lucide-react (icons)
- class-variance-authority, tailwind-merge, clsx (styling utilities)

**Backend**
- FastAPI 0.116.1
- Uvicorn 0.35.0 (`[standard]`)
- pydantic-settings 2.7.1 (env-driven config)
- SQLAlchemy 2.0.36 (ORM), Alembic 1.14.0 (migrations), psycopg 3.2.3 (Postgres driver)
- Postgres 16, run locally via `docker-compose.yml`
- pytest 8.3.4 + httpx 0.28.1 (`TestClient`) — first automated test suite in the repo, `backend/tests/`
- Python 3.13, isolated via `backend/.venv`

**Data fetching (frontend)**
- @tanstack/react-query — client-side caching, mutations, optimistic updates against the FastAPI backend

**Tooling**
- ESLint 9 (flat config)
- npm (frontend package manager)
- pip + venv (backend dependency management)
- Docker Desktop (local Postgres)

## Folder Structure

```
PTeeHealth/
├── PROJECT_PROGRESS.md
├── BACKEND_INTEGRATION_PLAN.md           # Phase 2-5 backend integration roadmap
├── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                  # Home / hero "tap to begin" landing screen
│   │   │   ├── layout.tsx
│   │   │   ├── providers.tsx             # TanStack Query client provider
│   │   │   ├── globals.css               # Tailwind v4 tokens (default shadcn palette — not yet swapped for Lovable's real tokens)
│   │   │   ├── assessment/
│   │   │   │   ├── page.tsx              # Seeded demo patient/assessment (fixed ids) — kept for backward compat
│   │   │   │   └── [assessmentId]/page.tsx  # Any assessment by id — what patient creation/selection routes into
│   │   │   └── patients/
│   │   │       ├── new/page.tsx          # New patient intake form
│   │   │       ├── page.tsx              # All patients list
│   │   │       └── [patientId]/page.tsx  # One patient's assessment history
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── top-nav.tsx           # nav links wired to /patients/new, /patients
│   │   │   ├── home/
│   │   │   │   ├── hero-section.tsx       # rotating headline/badge + mic entry point (routes to /patients/new)
│   │   │   │   └── quick-actions-bar.tsx  # fixed bottom pill (crop/type/draw/chat icons, visual-only)
│   │   │   ├── assessment/
│   │   │   │   ├── assessment-screen.tsx      # shared render, used by both /assessment routes
│   │   │   │   ├── assessment-tabs.tsx
│   │   │   │   ├── patient-summary-card.tsx
│   │   │   │   ├── doctor-notes-section.tsx   # useQuery/useMutation against /assessments/{id}/notes; mic button = client-side Web Speech API
│   │   │   │   ├── ptee-assistant-panel.tsx   # useQuery/useMutation against /assessments/{id}
│   │   │   │   ├── finding-row.tsx
│   │   │   │   ├── findings-list.tsx          # useQuery/useMutation against /assessments/{id}/findings
│   │   │   │   ├── recommended-tests-panel.tsx  # rendered inside PteeAssistantPanel — batch feed, Delete + per-test findings entry, real Completed Tests with Edit
│   │   │   │   ├── log-test-panel.tsx
│   │   │   │   └── insights-panel.tsx         # useQuery against /assessments/{id}/insights
│   │   │   ├── patients/
│   │   │   │   ├── new-patient-form.tsx       # full intake form, creates patient + first assessment
│   │   │   │   └── new-assessment-button.tsx  # starts another assessment for an existing patient
│   │   │   └── ui/                       # shadcn primitives (button, input, textarea)
│   │   └── lib/
│   │       ├── api.ts                    # typed fetch client for the FastAPI backend
│   │       ├── constants.ts              # DEFAULT_PATIENT_ID / DEFAULT_ASSESSMENT_ID — only used by the fixed /assessment demo route now
│   │       ├── use-voice-dictation.ts    # shared Web Speech API hook — used by DoctorNotesSection and each pending RecommendedTestsPanel card
│   │       └── utils.ts                  # cn() helper
│   ├── components.json                   # shadcn config
│   ├── .env.example                      # documents NEXT_PUBLIC_API_BASE_URL
│   └── package.json
└── backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                       # FastAPI app factory, CORS, /health, mounts /api/v1
    │   ├── core/
    │   │   ├── config.py                 # pydantic-settings (ALLOWED_ORIGINS, DATABASE_URL)
    │   │   └── deps.py                   # get_db() session dependency; get_current_user no-op stub (auth seam)
    │   ├── db/
    │   │   ├── base.py                   # SQLAlchemy DeclarativeBase, imports all models for Alembic autogenerate
    │   │   └── session.py                # engine, SessionLocal, get_db()
    │   ├── models/                       # SQLAlchemy ORM models, one file per table
    │   │   ├── patient.py, assessment_session.py, legacy_finding.py, legacy_test.py, doctor_note.py
    │   ├── api/v1/
    │   │   ├── router.py                 # aggregates all /api/v1 routers
    │   │   ├── patients.py
    │   │   ├── assessments.py
    │   │   ├── findings.py
    │   │   ├── diagnosis.py
    │   │   ├── tests.py                  # "log a test"
    │   │   ├── insights.py
    │   │   ├── notes.py                  # Doctor's Notes — GET/POST /assessments/{id}/notes
    │   │   └── recommendations.py        # POST /assessments/{id}/recommendations — batch, advisory, no DB writes
    │   ├── schemas/                      # Pydantic request/response models, camelCase over the wire
    │   │   ├── base.py                   # CamelModel — shared alias-generator base
    │   │   ├── patient.py
    │   │   ├── assessment.py
    │   │   ├── finding.py
    │   │   ├── test.py
    │   │   ├── insight.py
    │   │   ├── note.py                   # DoctorNote / DoctorNoteCreate, source: "typed" | "voice"
    │   │   └── recommendation.py         # RecommendedTest / TestRecommendationBatch (API-facing, camelCase)
    │   └── services/                     # business logic, DB-backed via SQLAlchemy Session
    │       ├── patients.py
    │       ├── assessments.py            # + generate_diagnosis() — calls the Claude engine, persists result
    │       ├── findings.py
    │       ├── tests.py
    │       ├── insights.py               # reads persisted insight_summary/insight_tags, or a fallback pre-generation
    │       ├── notes.py                  # list/create doctor notes, bumps assessment.version like tests.py
    │       ├── recommendations.py        # get_next_recommendation() — reads current state, no persistence
    │       └── engines/                  # AI seam — swappable behind a Protocol interface
    │           ├── base.py               # WorkingDiagnosisEngine + RecommendationEngine Protocols, all structured-output schemas
    │           ├── anthropic_client.py   # shared Anthropic client, explicit missing-key guard
    │           ├── working_diagnosis_engine.py  # ClaudeWorkingDiagnosisEngine — real claude-opus-5 structured-output call
    │           ├── recommendation_engine.py     # ClaudeRecommendationEngine — "what to test next," one at a time
    │           ├── rules.py              # load_assessment_rules() / load_recommendation_rules() — read fresh on every call
    │           ├── assessment_rules.md   # standing rules Claude must follow; edit freely, no code/restart needed
    │           └── recommendation_rules.md  # rules for the next-test recommendation (format, one-at-a-time, etc.)
    ├── alembic/
    │   ├── env.py                        # reads DATABASE_URL from Settings, targets Base.metadata
    │   ├── script.py.mako
    │   └── versions/
    │       ├── 0001_initial_schema.py    # patients, assessment_sessions, findings, logged_tests
    │       ├── 0002_seed_demo_data.py    # patient-1 / assessment-1 / 5 findings
    │       ├── 0003_add_insight_fields.py  # assessment_sessions.insight_summary / insight_tags
    │       └── 0004_add_doctor_notes.py    # doctor_notes table
    ├── alembic.ini
    ├── docker-compose.yml                # local Postgres 16, host port 5433
    ├── tests/                            # pytest + httpx.TestClient, one file per router, real Postgres test DB
    ├── pytest.ini
    ├── requirements.txt
    ├── .env.example                      # documents ALLOWED_ORIGINS, DATABASE_URL
    └── .gitignore
```

## Features Implemented

- **Project scaffold**: Next.js + Tailwind + shadcn/ui frontend; FastAPI backend skeleton with env-configurable CORS (`ALLOWED_ORIGINS`).
- **Home / hero screen** (`/`), pixel-matched from Lovable reference screenshots:
  - Shared `TopNav` with "New Patients" now pointing at `/` (was `/assessment`)
  - Rotating headline + achievement badge (`hero-section.tsx`) cycling every 4s between two mock variants ("decisions" / 12+ years of know-how and "tracking" / 50,000+ sessions reasoned through), matching both reference screenshot states
  - Large circular mic button that routes to `/assessment` via `next/link` — the "tap to begin assessment" entry point
  - "Start here" instruction copy
  - Fixed bottom quick-actions pill (`quick-actions-bar.tsx`) with crop/type/draw/chat icon buttons, visual-only (no backing behavior yet, consistent with other visual-only affordances already in the Assessment screen)
- **Patient Intake / Assessment screen** (`/assessment`), pixel-matched from Lovable reference screenshots:
  - Top nav (logo, New Patients/Existing Patients/Dashboard, search, notifications, AI icon, avatar)
  - Assessment/Treatment/Home Plan/Evaluation tab strip + "Senior review" pill
  - Collapsible Patient Summary card (patient fields, clinical summary, Doctor's Notes — real per-assessment notes now, typed or voice-dictated, not static placeholder text)
  - PTee Assistant panel: confidence meter, Cancel/Working-diagnosis/Complete↔Completed toggle, diagnosis Agree/Update/Fully-change block, and the green Reopen-diagnosis/Go-to-treatment-plan banner in the completed state
  - Findings list: 5 mock findings, per-row delete, per-row mic toggle (visual only), expandable question+bullet detail (populated for one reference row), and a "Type finding instead" manual override that replaces the AI-suggested label inline
  - Log a Test panel: Joint/Muscle/Gait type selector, test name + optional result fields, disabled-until-valid Save button
  - Insights panel: collapsible, AI-summary text, tagged finding with a "recorded" count badge

## UI Screens Completed

| Screen | Status |
|---|---|
| Patient Intake / Assessment tab (`/assessment`, seeded demo patient) | ✅ Built, pixel-matched |
| Any assessment by id (`/assessment/[assessmentId]`) | ✅ Built — shares rendering with `/assessment` via `components/assessment/assessment-screen.tsx` |
| Landing / "tap to begin assessment" mic screen (`/`) | ✅ Built, pixel-matched. Mic button now routes to `/patients/new`, not directly to `/assessment` |
| New patient intake form (`/patients/new`) | ✅ Built — full form (name, age, gender, occupation/sport, chief complaint, duration, pain score, aggravating/relieving factors, previous injuries); only name required. Creates the patient + their first assessment, routes to `/assessment/{id}` |
| Patients list (`/patients`) | ✅ Built — lists all patients with chief complaint, links to `/patients/{id}` |
| Patient detail / assessment history (`/patients/[patientId]`) | ✅ Built — lists that patient's assessments, "+ New assessment" starts another one |
| Treatment tab | ❌ Not built (tab label renders, no content; "Go to treatment plan" button is inert) |
| Home Plan tab | ❌ Not built |
| Evaluation tab | ❌ Not built |

## Backend APIs Implemented

All under `/api/v1`, Postgres-backed via SQLAlchemy + Alembic (data now survives a backend restart — the in-memory fixture store from Phase 2 has been fully removed). Seeded via Alembic migration with one demo patient (`patient-1`, Ankita Sharma) and one demo assessment (`assessment-1`) matching the data that used to be hardcoded in the frontend.

| Endpoint | Method | Status |
|---|---|---|
| `/health` | GET | Implemented — returns `{"status": "ok"}` |
| `/api/v1/patients` | GET, POST | Implemented |
| `/api/v1/patients/{patient_id}` | GET, PATCH | Implemented |
| `/api/v1/patients/{patient_id}/assessments` | GET, POST | Implemented |
| `/api/v1/assessments/{assessment_id}` | GET, PATCH | Implemented — status transitions (reviewing/completed) |
| `/api/v1/assessments/{assessment_id}/findings` | GET, POST | Implemented |
| `/api/v1/findings/{finding_id}` | PATCH, DELETE | Implemented — relabel, delete |
| `/api/v1/assessments/{assessment_id}/diagnosis` | GET, PATCH | Implemented — agree/update/fully-change actions |
| `/api/v1/assessments/{assessment_id}/diagnosis/generate` | POST | Implemented — real Claude Opus 5 call, generates + persists diagnosis, confidence, and insights together. `502` (not `500`) on any Anthropic failure, including a missing `ANTHROPIC_API_KEY` |
| `/api/v1/assessments/{assessment_id}/tests` | GET, POST | Implemented — "Log a test"; also the backing data for "Completed tests" in the recommendations panel |
| `/api/v1/tests/{test_id}` | PATCH | Implemented — edit a logged test's `result` only (name/type immutable); bumps `assessment.version` like any other test/finding write |
| `/api/v1/assessments/{assessment_id}/insights` | GET | Implemented — reads persisted `insight_summary`/`insight_tags` if `/diagnosis/generate` has run; otherwise a "nothing generated yet" fallback (not the old fixture text) |
| `/api/v1/assessments/{assessment_id}/notes` | GET, POST | Implemented — Doctor's Notes, one row per note, `source: "typed"\|"voice"`, ordered oldest-first |
| `/api/v1/assessments/{assessment_id}/recommendations` | POST | Implemented — real Claude Opus 5 call recommends a ranked batch of up to 4 tests, each with `testName`/`testType`/`summary`/`whyRecommended` — **no per-test confidence** (removed, see Change Log; only the overall diagnosis confidence is shown anywhere). Advisory only, writes nothing to the DB itself — completing a test calls the real `POST .../tests` endpoint instead. `502` on any Anthropic failure, same convention as `/diagnosis/generate` |

The Assessment screen now fetches all of the above from the backend instead of hardcoded frontend data — the gap called out below in earlier entries is closed. The `POST /patients`, `GET /patients`, `POST /patients/{id}/assessments`, and `GET /patients/{id}/assessments` endpoints were already implemented but unused by the frontend until now — `lib/api.ts` gained `createPatient`/`listPatients`/`createAssessment`/`listAssessmentsForPatient` wrappers to actually call them (see New patient intake / Patients list / Patient detail screens above). Not yet implemented: auth (`get_current_user` is a wired-in no-op stub), and Treatment/Home Plan/Evaluation endpoints (their tabs still render no content). Voice now has two real integrations sharing one hook (`lib/use-voice-dictation.ts`) — Doctor's Notes dictation and per-test findings dictation in the Recommended Tests panel — both entirely client-side via the Web Speech API (browser transcribes to text, backend never sees audio). Still no backend voice/audio-upload endpoint of any kind, and the findings-checklist rows' mic buttons remain visual-only.

## AI & RAG Integration Progress

**Real LLM calls now exist** — no RAG/vector DB/embeddings yet, but the working-diagnosis/confidence/insights seam is no longer a fixture.

- **Provider/model**: Anthropic Claude Opus 5 (`claude-opus-5`), official `anthropic` Python SDK, structured outputs (`client.messages.parse(output_format=...)` — the response *is* the validated Pydantic model, no free-text parsing).
- **Where it lives**: `backend/app/services/engines/` — `base.py` (both the `WorkingDiagnosisEngine` and `RecommendationEngine` Protocols + all structured-output schemas), `anthropic_client.py` (shared client, explicit missing-key guard), `working_diagnosis_engine.py` (`ClaudeWorkingDiagnosisEngine`), `recommendation_engine.py` (`ClaudeRecommendationEngine`), `rules.py` + two rules files (centralized rules seam, see below).
- **Centralized rules system, now populated with real content**: `assessment_rules.md` (role/scope, the 70%-confidence policy, Foundational Assessments taxonomy, mechanical relationships, general communication style) and `recommendation_rules.md` (the recommendation-batch spec — up to 4 ranked tests per call, exact format, manual-assessment handling) are sent to Claude as their own cached system-prompt blocks, each with a preamble instructing Claude to follow it before anything else. Both are read fresh on every request — deliberately not cached at the Python level — so editing either `.md` takes effect on the very next call with no code change and no backend restart. A missing file raises `RuntimeError`, already caught by the existing `502` handling (no endpoint code needed changing to add this).
- **Two engines now, sharing the rules seam**: `ClaudeWorkingDiagnosisEngine` (diagnosis + confidence + insights, one combined call) and `ClaudeRecommendationEngine` (a ranked batch of up to 4 tests to consider next — PTee Assistant's core recommendation behavior; no per-test confidence, only the diagnosis engine's confidence is shown anywhere). The recommendation engine loads *both* rules files (assessment rules + recommendation rules), the diagnosis engine loads only the first.
- **Diagnosis generation is automatic, not a button**: `PteeAssistantPanel` calls `POST /assessments/{id}/diagnosis/generate` once on mount and again whenever a test is completed (via `RecommendedTestsPanel`'s `onTestCompleted` or `FindingsList`'s `onTestLogged` callbacks) — there is no manual "Generate with AI" trigger anymore. A single request still generates diagnosis + confidence + insight summary/tags together (cheaper and more internally consistent than separate round trips reasoning over the same findings).
- **Recommendation batch is advisory, but completing a test is real**: `POST /assessments/{id}/recommendations` reads current findings/logged tests/doctor's notes fresh each call and returns a ranked batch — it never writes to the database itself. Deleting a suggestion is client-side only. Writing findings under a suggestion and clicking "Mark complete" calls the real `POST /assessments/{id}/tests`, creating an actual logged test — no separate "accept" step, no `RecommendationLog` table needed (the old PDF-derived plan flagged that entity as tentative). The next batch naturally sees newly-logged tests and won't repeat them.
- **Persistence**: `assessment_sessions` gained `insight_summary`/`insight_tags` columns (migration `0003`) so a generated insight survives past the single request — `services/insights.py` reads them, falling back to a "nothing generated yet" placeholder (not fake AI-sounding text) until generation has run at least once.
- **Failure handling**: any Anthropic failure (missing/invalid key, network, rate limit) returns `502` with a specific message — never a raw `500` — and leaves the assessment's existing diagnosis/confidence/insights untouched; verified via a real end-to-end browser test with no API key configured (the actual out-of-the-box state for a fresh clone).
- **Requires `ANTHROPIC_API_KEY`** (`backend/.env`) to actually generate anything; every other endpoint in the app is unaffected by its absence.
- **Testable without a real key**: both `services/assessments.py::generate_diagnosis` and `services/recommendations.py::get_recommendations` take an optional `engine` parameter for dependency injection — `backend/tests/test_diagnosis_generate.py` and `test_recommendations.py` mock it, no network calls in the test suite.
- **Not built yet**: RAG/retrieval over clinical knowledge, a vector database, and the Confidence Engine as a separate component (confidence is currently produced inline by `ClaudeWorkingDiagnosisEngine`, not a standalone engine as the PDF-derived plan originally described) — the Recommendation Engine itself (the "what to test next" half of that plan's engine trio) is now real, reasoning over today's flat `Finding`/`LoggedTest`/`DoctorNote` data rather than the plan's richer structured-findings model, which is still not built.

## Deployment Progress

Not deployed. Verified locally only:
- Frontend: `npm run build` / `npm run dev` / `npm run start`
- Backend: `uvicorn app.main:app --reload` against a local Postgres (`docker compose up -d` + `alembic upgrade head`)

Deployment plan was discussed but not executed: Vercel for the frontend (root directory `frontend`, no env vars needed yet since there's no live API integration), Render (or similar, not Vercel serverless) for the backend once real AI/RAG workloads exist, connected via `ALLOWED_ORIGINS` / `NEXT_PUBLIC_API_BASE_URL`. No CI/CD, no hosting accounts configured.

## Pending Tasks

- Build Treatment, Home Plan, and Evaluation tab content (frontend UI + backend routes, per `BACKEND_INTEGRATION_PLAN.md` Phase 3).
- Swap the placeholder Tailwind palette (default shadcn neutral tokens) for the actual Lovable design tokens/hex values once provided.
- Real voice capture for the *other* mic buttons (findings rows, Log a Test — still visual-only toggles); Doctor's Notes is the first one that's real (client-side Web Speech API, see Change Log). No backend `/voice/*` endpoint exists or is needed for that pattern — transcription happens in the browser, only the resulting text is sent to the backend.
- Real auth, multi-clinician / senior-review workflow — `get_current_user` is currently a wired-in no-op.
- RAG pipeline behind `diagnosis_service`/`insight_service` — a single Claude Opus 5 structured-output call now generates diagnosis/confidence/insights (see "AI & RAG Integration Progress" above), but it reasons only over the current session's own findings, not retrieval over a clinical knowledge base/vector DB. That retrieval layer is still not built.
- Recommendation Engine ("what to test next") — **now built**, real Claude call, a ranked batch of up to 4 tests per call (see "AI & RAG Integration Progress" above); still reasons over today's flat findings/tests/notes data rather than the richer structured-findings model the PDF-derived plan describes (Foundational Assessments' full 3-plane taxonomy isn't captured as structured data yet, only referenced in the rules text — see `assessment_rules.md` § Foundational Assessments' "current implementation gap" note).
- No "add to plan" action beyond the Completed Tests list itself — completing a recommended test now creates a real logged test (see Change Log), but there's no further downstream step (e.g. a Treatment plan hand-off) that does anything with that data yet.
- Deployment execution (Vercel + backend host) once there's a live integration worth deploying — the local Postgres setup (`docker-compose.yml`) is dev-only; production DB hosting is unaddressed.
- Frontend automated test suite (still none — Jest/Vitest not evaluated yet); backend now has one (`backend/tests/`, pytest).
- Richer data model per the PDF-derived backend Plan of Action (structured demographics, per-visit Intake Form, joint/muscle findings, Recommendation/Working-Diagnosis/Confidence engines, session lifecycle, treatment handoff, email/WhatsApp logging) — persistence migration (Phase 1) is the only phase done; remaining phases not yet started.
- No "delete patient" / edit-patient-details UI yet — patients created via `/patients/new` can't currently be renamed or removed from the app itself (only via direct API calls).
- `/patients` has no search/filter/pagination — fine at current (near-zero) patient counts, will need it once real usage starts.

## Known Issues

- `npm audit` reports 3 high-severity vulnerabilities in transitive dependencies (not investigated or patched).
- Row-level "info" and "play" icons are only functional/populated for one mock finding ("Pelvis Shift Right/Left"); other rows render the icons but they're inert — no reference content exists for them yet.
- In `next dev` under a headless-Chromium test-automation harness, the HMR WebSocket handshake can fail (`ERR_INVALID_HTTP_RESPONSE`), which silently prevented React hydration in that harness (confirmed via testing against the production build, where it worked correctly). Not reproduced in a normal browser session; flagged in case a similar environment issue (proxy/VPN/AV intercepting localhost WebSockets) shows up for a real user.
- The git remote named `origin` (`https://github.com/suyashalok/PTeeHealth.git`) is unreachable ("repository not found"). The actual working remote is `https://github.com/dubey-dot/pTee_Health.git`, which the local `main` branch was pushed to directly (without updating `origin`, since git identity/remote config changes are intentionally left to the user rather than automated).

## Future Enhancements

- RAG-based clinical reasoning pipeline (vector DB + retrieval over clinical knowledge to ground the "working diagnosis" and "insights" content).
- Healthcare API integrations (not yet identified/selected).
- Real-time voice capture and transcription feeding the PTee Assistant's findings/diagnosis suggestions.
- Full patient journey: Treatment planning, Home Plan generation, Evaluation/outcomes tracking.
- Authentication and multi-clinician / senior-review workflow (the "Senior review" pill currently exists as UI only).

---

## Change Log

_(Ordered chronologically. Each entry is appended, never edited or removed, when a meaningful task completes.)_

- **2026-08-02** — Scaffolded project: Next.js 16 + TypeScript + Tailwind v4 + shadcn/ui (`base-nova` preset) in `frontend/`; FastAPI skeleton with env-configurable CORS (`ALLOWED_ORIGINS`) and a `/health` endpoint in `backend/`. Verified both build/run cleanly.
- **2026-08-02** — Documented and verified the local dev workflow (backend venv activation, frontend `npm run dev`, troubleshooting common errors) and produced a deployment plan (Vercel for frontend, Render — not Vercel serverless — for backend) with required env vars identified (`ALLOWED_ORIGINS`, future `NEXT_PUBLIC_API_BASE_URL`).
- **2026-08-02** — Built the "Log a Test" panel (Joint/Muscle/Gait selector, test name/result fields, disabled-until-valid Save) and the collapsible "Insights" panel, pixel-matched from Lovable reference screenshots.
- **2026-08-02** — Built the full Patient Intake / Assessment screen at `/assessment`: shared top nav, Assessment tab strip, collapsible Patient Summary card, and the PTee Assistant panel (confidence meter, Cancel/Working-diagnosis/Complete↔Completed states, diagnosis Agree/Update/Fully-change block, Reopen-diagnosis/Go-to-treatment-plan banner) with a findings list supporting per-row detail expansion, manual "Type finding instead" override, and deletion. Verified via headless-browser screenshot testing against both dev and production builds.
- **2026-08-02** — Published the initial commit (`"PTee health Assessment"`) to `https://github.com/dubey-dot/pTee_Health.git`, re-authored as `dubey-dot <dubey@pteehealth.com>`, pushed directly to the URL without modifying git config or the existing (unreachable) `origin` remote.
- **2026-08-02** — Added this document (`PROJECT_PROGRESS.md`) as the standing source of truth for project status, to be updated after every meaningful task going forward.
- **2026-08-02** — Built the Home / hero landing screen at `/` (`hero-section.tsx`, `quick-actions-bar.tsx`), pixel-matched from Lovable reference screenshots: rotating headline word + achievement badge (mock data, 4s interval), circular mic button routing to `/assessment`, and a fixed bottom quick-actions pill. Re-pointed the shared `TopNav`'s "New Patients" link from `/assessment` to `/` so the mic screen is now the entry point into the New Patient flow. Verified via `npm run build` and headless-browser screenshots (desktop 1280px, mobile 390px, both rotation states).
- **2026-08-02** — Authored `BACKEND_INTEGRATION_PLAN.md`: the Phase 2-5 roadmap for replacing hardcoded frontend data with a real FastAPI-backed integration — layered backend architecture (`api/v1`/`schemas`/`services`), REST endpoint design, TanStack Query-based frontend data flow, cache/persistence strategy, and the service-layer seams reserved for the future RAG pipeline and healthcare API integrations.
- **2026-08-02** — Implemented Phase 2 (fixture-backed backend + Assessment screen wiring) end-to-end:
  - Restructured `backend/app` from a single `main.py` into `core/` (settings, auth stub), `schemas/` (Pydantic models with a shared `CamelModel` base so JSON responses match the frontend's camelCase types), `services/` (business logic over an in-memory fixture store seeded with the existing demo patient/assessment/findings data), and `api/v1/` (routers for patients, assessments, findings, diagnosis, tests, insights).
  - Added `pydantic-settings` for env-driven CORS config; `get_current_user` wired in as a no-op dependency across all `/api/v1` routes as the Phase 5 auth seam.
  - Added TanStack Query (`@tanstack/react-query`) to the frontend, a typed `lib/api.ts` fetch client, and `lib/constants.ts` for the (temporary, pre-patient-routing) default patient/assessment IDs.
  - Converted `assessment/page.tsx` to an async Server Component that fetches patient/assessment/findings/insights from FastAPI, passed down as React Query `initialData`. `PteeAssistantPanel`, `FindingsList`, and `InsightsPanel` now read live backend state and issue real mutations (delete/relabel findings with optimistic updates + rollback, diagnosis agree/update/fully-change, status reviewing↔completed, log-a-test submission) instead of owning hardcoded local state.
  - Verified: `npm run lint` and `npm run build` clean; backend endpoints round-tripped via curl (including PATCH/DELETE/POST mutations and assessment version bumping); full browser verification via a headless-Chromium Playwright script confirmed the rendered page is pixel-identical to the pre-integration version, and that deleting a finding removes it and the removal survives a page reload (proving the mutation persists server-side, not just in local UI state) with zero console errors.
- **2026-08-04** — A PDF spec (`Data Flow.pdf`) proposing the full target data model and backend orchestration flow (structured demographics, per-visit Intake Form, joint/muscle/clinical findings, Recommendation/Working-Diagnosis/Confidence engines, session lifecycle, treatment handoff, email/WhatsApp logging) was analyzed and turned into a detailed Plan of Action (backend folder structure, DB schema, API design, phased build sequence, risks/open questions) — confirmed scope with the user: rule-based engine stubs (no LLM yet), no voice capture yet, backend-first with frontend UI changes deferred, and Cancel soft-closes a session without ever deleting the patient record (overriding the PDF's literal "Patient details deleted" wording, flagged and confirmed rather than assumed).
- **2026-08-04** — Implemented Phase 1 of that plan (Persistence Migration) end-to-end:
  - Replaced the in-memory `services/store.py` fixture with Postgres 16 (via `docker-compose.yml`, host port 5433 to avoid clashing with any native Postgres) + SQLAlchemy 2.x models (`app/models/`) + Alembic migrations (`app/db/`, `alembic/`). The former `assessments` fixture table is now `assessment_sessions` in the DB (API path `/assessments/...` unchanged) — a deliberate rename to give later phases (which FK everything to a session) a stable anchor from day one.
  - Two migrations: `0001_initial_schema` (patients, assessment_sessions, findings, logged_tests) and `0002_seed_demo_data` (reproduces patient-1/assessment-1/5 findings exactly, so upgrading a fresh DB is behavior-neutral for local dev).
  - Rewrote all four services (`patients`, `assessments`, `findings`, `tests`) plus `insights` to be DB-backed via SQLAlchemy `Session`, injected into every route via a new `get_db()` FastAPI dependency; `core/config.py` gained `database_url` and now actually loads `backend/.env` (previously `Settings` had no `env_file` configured despite `.env.example` implying it did — fixed as part of this work).
  - Added the repo's first-ever automated test suite: `backend/tests/` (pytest + `httpx.TestClient`, 30 tests covering all 17 `/api/v1` routes' happy paths and 404 cases), running against a real dedicated `ptee_health_test` Postgres database (not mocks, not SQLite) with per-test transaction rollback for isolation.
  - Verified: all 30 pytest tests pass; `alembic upgrade head` on a fresh DB reproduces the old fixture's exact JSON responses byte-for-byte (confirmed via curl diff against the pre-migration output); `npm run build` clean; a production frontend build/start pointed at the new Postgres-backed backend confirmed server-side rendering still pulls live data correctly (patient name, findings, insights all present in the SSR HTML).
- **2026-08-04** — Added multi-patient support to the frontend (backend needed no changes — `POST /patients`, `GET /patients`, `POST /patients/{id}/assessments`, and `GET /patients/{id}/assessments` already existed from Phase 2 but the frontend never called them):
  - `lib/api.ts` gained `createPatient`, `listPatients`, `createAssessment`, `listAssessmentsForPatient` wrappers and a `PatientCreateInput` type.
  - New screens: `/patients/new` (full intake form — name required, age/gender/occupation-sport/chief complaint/duration/pain score/aggravating/relieving/previous injuries all optional — creates the patient then their first assessment, routes to the new assessment), `/patients` (list all patients, links to each), `/patients/[patientId]` (that patient's assessment history + a "+ New assessment" button for follow-ups).
  - New dynamic route `/assessment/[assessmentId]` renders any assessment by id; extracted the shared rendering into `components/assessment/assessment-screen.tsx` so the original fixed `/assessment` route (still shows the seeded Ankita Sharma demo, kept for backward compatibility) and the new dynamic route don't duplicate markup.
  - Re-pointed the Home screen's mic button and `TopNav`'s "New Patients"/"Existing Patients" links (previously inert/pointed at `/`) to the new intake form and patient list respectively.
  - Verified: `npm run lint` and `npm run build` clean (7 routes registered correctly); full headless-browser Playwright run driving the real flow end-to-end — Home → mic → intake form → filled all 10 fields → submit → routed to a brand-new `/assessment/{id}` showing the just-entered patient data with a genuinely empty assessment (0 findings, `status: "reviewing"`, 0% confidence) → confirmed both the new patient and the original demo patient appear on `/patients` → confirmed the original `/assessment` demo route still renders unchanged. Zero console errors, zero failed network requests throughout.
- **2026-08-05** — Implemented real LLM-backed generation for working diagnosis, confidence, and insights (the PTee Assistant panel content shown in the UI was previously always static fixture text):
  - Designed the integration around the existing `services/insights.py`/`services/assessments.py` seam rather than a new subsystem: added `backend/app/services/engines/` — `base.py` (a `WorkingDiagnosisEngine` `Protocol` plus `GeneratedAssessment`/`GeneratedInsightTag` Pydantic schemas), `anthropic_client.py` (a cached `anthropic.Anthropic` client factory), and `working_diagnosis_engine.py` (`ClaudeWorkingDiagnosisEngine`, the real implementation).
  - One combined `client.messages.parse()` structured-output call to `claude-opus-5` (per the `claude-api` skill's model mandate) generates diagnosis text, a 0–100 confidence score, and an insight summary + tags together from the assessment's patient summary, clinical summary, and logged findings — rather than three separate calls reasoning over the same data.
  - New `POST /assessments/{id}/diagnosis/generate` endpoint (`api/v1/diagnosis.py`) triggers generation and persists the result; `assessment_sessions` gained `insight_summary`/`insight_tags` columns (migration `0003_add_insight_fields`) so a generated result survives past the single request. `services/insights.py` was rewritten to read those persisted columns, falling back to a "nothing generated yet" placeholder (replacing the old always-present "Biceps Femoris..." fixture text) until generation has run at least once for that session.
  - `services/assessments.py::generate_diagnosis` takes an optional `engine` parameter for dependency injection, so `backend/tests/test_diagnosis_generate.py` (6 new tests) exercises the full service+endpoint logic with a fake engine — no real network calls in the test suite (36 backend tests pass total).
  - Frontend: `lib/api.ts` gained `generateDiagnosis()`; `PteeAssistantPanel` gained a "Generate with AI" button (next to "Working diagnosis") wired to a `useMutation` that updates the assessment and invalidates the insights query on success, and an inline error message on failure.
  - **Bug found and fixed via live manual testing** (curl against the running backend with no `ANTHROPIC_API_KEY` set): the Anthropic SDK raises a bare `TypeError` at request-build time when no key is configured, not an `anthropic.APIStatusError`/`APIConnectionError` — the endpoint's except clause didn't catch it, so the failure surfaced as an unhandled `500` instead of a clear error. Fixed with an explicit upfront key check in `get_anthropic_client()` raising `RuntimeError`, caught alongside the real Anthropic exception types in the endpoint; re-verified via curl (`502` with an actionable message) and added a regression test (`test_generate_diagnosis_endpoint_502_when_api_key_missing`).
  - Verified: 36 pytest tests pass (real Postgres test DB, no mocked-out client at the HTTP layer — mocking happens at the service's `engine` parameter); `npm run lint`/`npm run build` clean; full headless-browser Playwright run against the live app with no `ANTHROPIC_API_KEY` configured (the actual out-of-the-box state in this environment) confirmed the "Generate with AI" button shows a loading state, the request returns `502`, the inline error message renders, the button re-enables, and the assessment's prior diagnosis/confidence are left untouched — the complete failure/degradation path, end to end. **Not verified**: the success path (an actual generated diagnosis from a real Claude API call) — no `ANTHROPIC_API_KEY` is available in this environment; the request/response contract was validated instead via the mocked-engine pytest suite plus a live schema-validation smoke check of the Anthropic call shape.
  - README.md updated in the same turn: Project Overview, Environment files (documenting `ANTHROPIC_API_KEY`), Manual Verification Checklist (new "AI generation" section), and Troubleshooting (the 502/missing-key scenario).
- **2026-08-05** — Made the Doctor's Notes section on the Patient Summary card real (previously static placeholder text, no way to actually add a note):
  - Backend: new `doctor_notes` table (migration `0004_add_doctor_notes`) — one row per note, FK'd to `assessment_sessions` (per-consultation, matching the `Finding`/`LoggedTest` pattern rather than being patient-wide), `content`, `source` (`"typed"` or `"voice"`), `created_at`. New `app/schemas/note.py`, `app/services/notes.py` (list/create, bumps `assessment.version` like `tests.py` does), and `app/api/v1/notes.py` — `GET`/`POST /assessments/{id}/notes`, `404` if the assessment doesn't exist.
  - Frontend: new `components/assessment/doctor-notes-section.tsx` (replacing the static block inside `patient-summary-card.tsx`, which now takes `assessmentId`/`initialNotes` instead of the old `doctorsNotesCount` prop) — a textarea + mic button + "Save note" button, backed by `useQuery`/`useMutation` against the new endpoint. Notes render as a list above the input with a relative timestamp and a "· dictated" tag for voice-sourced ones.
  - Voice-to-text runs entirely client-side via the browser's Web Speech API (`window.SpeechRecognition`/`webkitSpeechRecognition`, locally typed since it's not in TypeScript's DOM lib) — no backend change needed for this, since the browser does the transcription and only the resulting text is ever sent over the wire. Feature support is checked lazily at click time (not via a mount-detection `useEffect`, which the project's stricter `eslint-plugin-react-hooks` rule flags as a same-render-cycle `setState`-in-effect anti-pattern) — unsupported browsers get a visible inline fallback message instead of a silent failure or a disabled-on-first-render button that could itself cause a hydration mismatch.
  - `PatientSummary.doctorsNotesCount` (a static integer column on `patients` that was never actually incremented by anything) is left in place on the backend for now — untouched, unused — since removing it would mean touching the patient model/schema/migrations for a field this feature doesn't need to touch; the frontend simply no longer reads it, using the real per-assessment note count instead.
  - **Bug found and fixed via Playwright verification** (not via manual testing this time — the first browser run surfaced a React hydration-mismatch console error): each note's relative timestamp was formatted with `date.toLocaleString(undefined, {...})`, and an unspecified locale resolves differently between Node's ICU (server-side render) and the test browser's default locale (client-side render) — e.g. `"5 Aug, 3:13"` server-side vs. `"5 Aug, 3:13 am"` client-side — producing a real (if cosmetic) hydration mismatch on every page load with notes present. Fixed by pinning the locale explicitly to `"en-US"` instead of leaving it `undefined`; re-verified via Playwright with zero console errors.
  - Verified: 42 backend pytest tests pass (36 prior + 6 new `test_notes.py` cases — create/list, ordering, `assessment.version` bump, `404` on a nonexistent assessment, both `source` values); `npm run lint`/`npm run build` clean; full headless-browser Playwright run against the live app — saved a typed note, confirmed a `201` response, the note appearing in the list, the header count incrementing, the textarea clearing, and the note still present after a full page reload (proving real backend persistence, not local state); clicking the mic button in headless Chromium (which has no working speech backend) didn't throw or break the page. **Not verified**: actual microphone dictation end-to-end (headless browser automation has no real audio input/speech service) — that requires a manual check in a real Chrome/Edge session with mic permission granted, called out explicitly in the README's Manual Verification Checklist rather than claimed as tested.
  - README.md updated in the same turn: Project Overview, a new curl example under "Testing POST endpoints," the `/docs` router list, and a new "Doctor's Notes" Manual Verification Checklist section.
- **2026-08-07** — Configured a real `ANTHROPIC_API_KEY` end-to-end and exercised the AI generation success path for the first time in this project (previously only the failure/missing-key path had ever been verified live). Along the way, root-caused a real environment bug: on Windows, killing the top-level `uvicorn --reload` process does **not** kill the actual worker subprocess it spawns via `multiprocessing` — that child survives orphaned, keeps holding the port, and keeps serving requests with whatever `.env` it loaded at its own startup. Every prior "restart the backend" in this session had silently been restarting the *reloader* while an older orphaned *worker* (with a stale cached API key) kept answering all requests — confirmed via `Get-CimInstance Win32_Process` parent/child inspection, not guesswork. Fixed by killing the actual worker PID directly. `POST /assessments/assessment-1/diagnosis/generate` and `GET .../insights` were verified against the real API, returning genuine generated clinical reasoning for the first time.
- **2026-08-07** — Made the New Patient intake form's free-text fields (Chief complaint, Aggravating factors, Relieving factors, Previous injuries) multi-line: added `frontend/src/components/ui/textarea.tsx` (Base UI has no `Textarea` primitive, so this mirrors `input.tsx`'s styling over a plain `<textarea>`, matching the precedent already set in `doctor-notes-section.tsx`), converted those four fields to full-width 3-row `Textarea`s while leaving genuinely short fields (Age, Gender, Occupation/Sport, Duration, Pain score) as single-line inputs. Verified via `npm run lint`/`npm run build` and a headless-browser screenshot showing multi-paragraph text wrapping correctly with zero console errors.
- **2026-08-07** — Added a centralized, editable-without-code rules system for the Claude integration: `backend/app/services/engines/assessment_rules.md` (a placeholder Markdown template — Scope & Boundaries, Clinical Reasoning Principles, Confidence Scoring Rules, Red Flags & Escalation, Tone & Communication Style, Prohibited Behaviors — no real clinical content yet, intentionally left for the user to fill in) and `services/engines/rules.py` (`load_assessment_rules()`, reads the file fresh on every call, deliberately uncached so edits take effect on the next request with no restart). `working_diagnosis_engine.py` now sends the rules as their own cached system-prompt block ahead of the existing task-instruction block, with an explicit `RULES_PREAMBLE` telling Claude to follow them before anything else; a missing file raises `RuntimeError`, which the existing `502` handling in `api/v1/diagnosis.py` already catches — no endpoint code changed. Added `tests/test_rules.py` (load success/missing-file) and `tests/test_working_diagnosis_engine.py` (proves the rules content actually reaches the system prompt sent to Claude, via a fake Anthropic client — the first test in this suite to assert on prompt construction directly rather than only the service/HTTP layer). Verified: 45 backend pytest tests pass (42 prior + 3 new); re-ran the real end-to-end `/diagnosis/generate` call against the live Anthropic API afterward to confirm the response flow is byte-for-byte unchanged from the user's perspective, per the "don't change existing functionality" requirement.
- **2026-08-07** — Populated `assessment_rules.md` with real content from a user-authored clinical spec (previously a placeholder) — Role & Scope (MSK-first, AI is not the decision-maker), the 70%-confidence policy (must explain the pathway to 70% rather than just report a low number), the Foundational Assessments taxonomy (Pelvis/Ribcage/Neck/Spine across 3 planes), Mechanical Relationships, and General Communication & Output Style. The same source material also specified a full "AI Assessment Recommendation Engine" spec (one test at a time, exact Test Type/Name/Expected/Actual format, reasoning rules, manual-assessment handling) — since no `RecommendationEngine` existed in `base.py` yet, this was captured faithfully in a new, separate `recommendation_rules.md`, explicitly flagged as **not yet wired into any engine** rather than silently mixed into the live file. (That engine was built the same day — see the next entry.) Found via verification, not asked to fix: `GeneratedAssessment.reasoning` — where the confidence-building pathway the new rules require would need to live — is generated by Claude but never persisted or surfaced anywhere in the app; flagged to the user as a real gap between the rule and actual product behavior.
- **2026-08-07** — Built the Recommendation Engine — PTee Assistant's core purpose per the user's spec: recommend the single next test the clinician should perform, with an info button explaining what it is and why. This is the engine `recommendation_rules.md` was written for one entry earlier, now actually wired in:
  - Backend: `RecommendedTest`/`TestRecommendation` schemas + a `RecommendationEngine` Protocol added to `services/engines/base.py`; `services/engines/recommendation_engine.py` (`ClaudeRecommendationEngine`) sends **both** rules files as separate cached system-prompt blocks (assessment rules + recommendation rules) ahead of its own task instructions — `rules.py` was generalized from one file/one preamble to two of each. New `POST /assessments/{id}/recommendations/next` (`api/v1/recommendations.py` → `services/recommendations.py`) reads current findings (including each one's `selected` status), logged tests, and doctor's notes fresh on every call and asks Claude for exactly one recommended test, or `hasRecommendation: false` with a reason if none would meaningfully help. **Deliberately advisory only** — never writes to the database or bumps `assessment.version`; the doctor logs the actually-performed test through the existing findings/tests endpoints, and because those are included in the next call's context, Claude naturally avoids re-recommending an already-logged test without needing a dedicated recommendation-history table.
  - Frontend: `RecommendedTestCard` (`components/assessment/recommended-test-card.tsx`), mounted at the top of `FindingsList` above the existing findings — shows Test Type badge, Test Name, EXPECTED and WATCH FOR bullet lists, and an **(i) info button** that expands to show "What it is" (`purpose`) and "Why now" (`reasoning`). Generated on demand via a "Suggest next test" button (confirmed with the user: one test at a time per the user's own Rule 1, manually triggered like "Generate with AI" rather than automatic, to avoid a surprise Claude call on every render).
  - Two design decisions confirmed with the user before building (both went with the recommended option): show one test at a time — not a list — resolving a direct conflict between `recommendation_rules.md` Rule 1 ("never display multiple simultaneously") and the request's own reference screenshot showing a multi-item list; and manual-button trigger over automatic regeneration.
  - Added `tests/test_recommendation_engine.py` (proves both rules files reach the system prompt, 3 cached blocks) and `tests/test_recommendations.py` (service persists nothing / doesn't bump version, `404`, `502` on missing key and on Anthropic failure) — mirrors the `test_diagnosis_generate.py` pattern. A cosmetic `PytestCollectionWarning` (pytest mistaking the `TestRecommendation` Pydantic model for a test class purely because of its name) was filtered in `pytest.ini`, matching the existing filter for pydantic's alias-generator warning.
  - Verified: 55 backend pytest tests pass (45 prior + 10 new); `npm run lint`/`npm run build` clean; re-ran the real end-to-end call against the live Anthropic API — returned a genuinely well-reasoned recommendation ("Right Single Leg Squat" with quantified expected/actual ROM values tied to the patient's specific finding pattern); full headless-browser Playwright run confirmed the card renders correctly, the (i) button toggles the info panel, and there were zero console errors. Environment note: the backend needed a clean process restart (killed the entire reloader chain by PID, not just the top-level command) before the new router was picked up — WatchFiles didn't auto-reload for this batch of new files the way it has for single-file edits earlier in this session; not fully root-caused, but the "kill everything, verify via `Get-CimInstance`, restart clean" recipe from the earlier API-key debugging session resolved it immediately.
  - README.md updated in the same turn: Project Overview, a new curl example, the `/docs` router list, a new "Recommended next test" Manual Verification Checklist section, and a Troubleshooting entry covering both rules files' missing-file case.
- **2026-08-07** — Redesigned the Recommended Test feature from the entry above, same day, per explicit follow-up feedback: relocated it to render **inside** the PTee Assistant panel (between the diagnosis block and the findings checklist) instead of as its own card above `FindingsList`, and simplified the displayed shape from 4 fields behind a toggle down to exactly 3 always-visible fields.
  - Schema simplified in `services/engines/base.py` and `schemas/recommendation.py`: `RecommendedTest` is now just `testName` / `whyRecommended` / `expectedResult` — dropped the `testType` badge and the separate `actualBehaviour` ("watch for") list, and merged the old `purpose` + `reasoning` fields into one concise `whyRecommended` note. No (i) button/toggle needed anymore since everything is shown directly.
  - `recommendation_rules.md` Rule 3 (format) and Rule 4 (reasoning) were merged into a single updated Rule 3 describing the new 3-field shape, with the old Rules 5/6 renumbered down to 4/5 — kept the rules file in sync with what Claude is actually asked to produce, rather than leaving it describing a format the engine no longer outputs. Also fixed a stale note in both rules files' headers still saying `recommendation_rules.md` was "not yet wired into any engine," left over from the entry above before the engine existed.
  - Frontend: `RecommendedTestCard` rewritten (no more `useState`-driven info toggle) and moved from `FindingsList` into `PteeAssistantPanel`, rendered right after the diagnosis/reopen-banner block.
  - One assumption made and flagged rather than silently guessed: the request used "Recommended Tests" (plural) and "for each recommended test," which could have meant reverting the previous turn's confirmed "one at a time" decision — read instead as generic/plural phrasing for the feature name, since nothing in the request explicitly asked to show multiple simultaneously and it directly followed a confirmed decision the turn before. Kept one-at-a-time.
  - Verified: updated `tests/test_recommendation_engine.py` and `tests/test_recommendations.py` for the new field names, all 55 backend tests still pass; `npm run lint`/`npm run build` clean; re-ran the live Anthropic API call end-to-end and confirmed the new 3-field shape (`testName`/`whyRecommended`/`expectedResult`) comes back correctly; full headless-browser Playwright run confirmed the section now renders inside the same card as "PTee Assistant" (checked via DOM ancestor query, not just visual inspection) with zero console errors. Same environment quirk as the entry above recurred (two full reloader chains ended up running simultaneously, one serving stale responses with the old field names) — resolved with the same "enumerate every uvicorn-related PID via `Get-CimInstance`, kill all of them, start exactly one clean instance" recipe.
  - README.md updated in the same turn: Project Overview wording, the Manual Verification Checklist's "Recommended next test" section (new placement-check item, dropped the now-inapplicable (i)-button checklist item).
- **2026-08-08** — Redesigned Recommended Tests a third time, this time reversing the "one at a time" decision from two entries above: now a **reviewable batch feed** (up to 4 ranked tests, each independently confidence-scored) with Accept/Reject/Undo and a Selected Tests staging panel, matching a reference screenshot + spec the user provided. Three follow-up questions were asked and confirmed before building (all "recommended" options): manual "Suggest tests" button (not automatic generation), Accept as client-side-only staging (no backend write — a further "add to plan" step is implied by the wording but not yet built), and Reject-removes/Undo-restores (not a visible-but-greyed-out state). The "one vs. many" question itself wasn't asked — the user's reference screenshot showing 4 simultaneous cards settled it unambiguously.
  - Backend: `RecommendedTest` gained a `confidence` field (0–100, independent per-test — explicitly *not* the same number as the overall working-diagnosis confidence, called out in both the schema docstring and the prompt to avoid Claude conflating the two) and a `summary` field (short always-visible line distinct from the fuller `why_recommended`, which is now only shown when a card is expanded); dropped `expected_result` entirely since neither the new screenshot nor spec called for it. Root schema renamed `TestRecommendation` → `TestRecommendationBatch` (`tests: list[RecommendedTest]`, empty when nothing further is recommended) — `has_recommendation`/single-`test` shape retired. Endpoint renamed `POST /assessments/{id}/recommendations/next` → `POST /assessments/{id}/recommendations` (only ever called from this one place in the frontend, so renaming now was low-risk). `recommendation_rules.md` Rule 1 rewritten from "ONE at a time, never simultaneous" to "batch of up to 4, ranked, each independently confidence-scored"; Rule 3's format table gained the Confidence column and Summary field; Rule 5's "one at a time" restatement removed.
  - Frontend: `recommended-test-card.tsx` deleted, replaced by `recommended-tests-panel.tsx` (`RecommendedTestsPanel`) — manages the batch as local `{test, status: pending|accepted|rejected}[]` state (Accept/Reject are pure `useState`, no backend call), an expand/collapse `Set` for "Why this test," and a `lastRejected` index driving the Undo banner. Confidence renders as a color-coded bar + percentage + label (green ≥70% "High," amber ≥45% "Medium," red <45% "Low," thresholds picked to match the reference screenshot's example values of 82/65/88/41%). "Selected tests" panel lists accepted tests with their confidence, count badge, and the exact placeholder copy from the reference screenshot when empty.
  - Verified: updated `test_recommendation_engine.py`/`test_recommendations.py` for the batch shape, all 55 backend tests pass; `pytest.ini`'s cosmetic-warning filter updated for the renamed `TestRecommendationBatch` class; `npm run lint`/`npm run build` clean; re-ran the live Anthropic API call and got 4 genuinely well-differentiated, ranked, clinically coherent tests (88/84/80/76% confidence, each targeting a distinct differential); full headless-browser Playwright run exercised the whole loop — fetch batch → expand reasoning → Accept one → Reject another → Undo the reject — confirmed the counter, Undo banner, and Selected Tests panel all update correctly, with zero console errors throughout.
  - **Known limitation, by design (confirmed via the Accept-behavior question above)**: Accept/Reject/Selected-tests state lives only in React state — a page reload loses it entirely, and there's currently no "add to plan" action that does anything with the Selected Tests list beyond displaying it. This matches what was asked ("client-side staging only... for final review before adding them to the plan"), but the actual "adding to the plan" step doesn't exist yet — flagged here rather than silently implied as done.
  - README.md updated in the same turn: Project Overview, the curl example, and the Manual Verification Checklist's "Recommended tests" section rewritten for the batch/Accept-Reject-Undo/Selected-Tests flow.
- **2026-08-08** — Fourth pass on this feature area, same day: removed the manual "Generate with AI" trigger (PTee Assistant now starts automatically), replaced Accept/Reject/Undo with Delete + real per-test findings entry, dropped per-test confidence entirely, and renamed Selected → Completed Tests with a real Edit capability. Two follow-up questions were asked and confirmed (both "recommended" options): diagnosis generation auto-runs on page load *and* after every completed test (not load-only), and completing a recommended test persists as a real logged test (not client-side staging).
  - Backend: `RecommendedTest.confidence` removed entirely (not hidden — actually stopped generating it, avoiding the same "generated-then-discarded" waste flagged earlier this session for `GeneratedAssessment.reasoning`); gained `test_type: "joint"|"muscle"|"gait"` instead, matching `LoggedTest`'s existing taxonomy exactly, since completing a recommendation now creates a real `LoggedTest` through the same endpoint and needs a valid type to do it. New `PATCH /tests/{id}` (`schemas/test.py::LoggedTestUpdate`, `services/tests.py::update_test`) — result-only edit, mirrors the existing `PATCH /findings/{id}` pattern exactly. `recommendation_engine.py`'s prompt and `recommendation_rules.md` Rule 1/Rule 3 rewritten to drop confidence-scoring instructions and document the Test Type field instead.
  - Frontend: `RecommendedTestsPanel` rewritten again — pending cards now show Test Name/Summary/"Why this test" plus a **Delete** button and a **FINDINGS** textarea+mic section (reusing the Doctor's Notes dictation pattern) ending in a **"Mark complete"** button; completing calls `api.createTest` for real. **"Completed tests"** is no longer separate ephemeral state — it's a `useQuery(["tests", assessmentId])` over the real backend list, shared with the pre-existing separate "Log a test" panel (`FindingsList`'s `testMutation` now also invalidates that same query key, so a test logged either way shows up in both places). Each completed row has an **Edit** link revealing an inline textarea that calls the new `PATCH /tests/{id}`.
  - Extracted `lib/use-voice-dictation.ts` — the Web Speech API glue that lived inline in `doctor-notes-section.tsx` is now a shared hook, used there and once per pending recommendation card (multiple simultaneous instances). `doctor-notes-section.tsx` refactored to use it too, net negative diff with identical behavior — worth doing now that a second real usage exists, not attempted the first time this pattern was written since duplicating it once wasn't yet worth the abstraction.
  - `PteeAssistantPanel`: the "Generate with AI" button is gone; a `useRef`-guarded `useEffect` fires `generateMutation.mutate()` once per mount, and `onTestCompleted`/`onTestLogged` callbacks (passed to `RecommendedTestsPanel`/`FindingsList`) fire it again after any test is completed or logged. The confidence meter shows an "Analyzing…" spinner in place of the percentage while a generation is in flight; a failed auto-generation shows the same inline error as before plus a small "Retry" link (there's no other way to re-trigger it without reloading the page).
  - **Real behavior change worth knowing, not just a code diff**: every assessment page load now fires a real Claude API call automatically (previously opt-in via the button). Flagged explicitly in README Troubleshooting, including that the seeded demo assessment's fixture diagnosis gets overwritten by a real generated one the first time `/assessment` is visited after this change.
  - Verified: 57 backend pytest tests pass (55 prior + 2 new for `PATCH /tests/{id}`); `npm run lint`/`npm run build` clean; live end-to-end confirmed the new batch response has no `confidence` field and correct `testType` values; full headless-browser Playwright run confirmed all of — auto-generation fires on mount with zero manual buttons present, zero confidence badges anywhere on recommendation cards, deleting a card removes it locally, completing a card creates a real test **and** re-triggers a second `/diagnosis/generate` call, and editing a completed test's result persists — with zero console errors throughout.
  - README.md updated in the same turn: Project Overview (both bullets rewritten), a new `PATCH /tests/{id}` curl example, the "AI generation" and "Recommended tests" Manual Verification Checklist sections rewritten for the new flow, and a new Troubleshooting entry about the auto-trigger's API-cost implication.
