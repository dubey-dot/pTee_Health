# PTee Health — Project Progress

Single source of truth for project status. Updated after every meaningful task — entries are appended, not overwritten.

---

## Project Overview

PTee Health is an AI-powered Clinical Decision Support Platform for physiotherapists. **Phase 1** (current phase) is scoped strictly to the **Patient Intake / Assessment screen** of the clinical journey, replicated pixel-for-pixel from Lovable-generated UI reference screenshots, backed by a lightweight FastAPI service that will later be swapped for real AI/RAG/clinical services without requiring frontend changes.

Long-term vision (not yet started): an AI-powered clinical reasoning pipeline (RAG over clinical knowledge), healthcare API integrations, and full patient journey coverage (Assessment → Treatment → Home Plan → Evaluation).

## Architecture

- **Frontend**: Next.js App Router. Server Components for static layout; Client Components (`"use client"`) for anything with interactive state (panels, toggles, forms). No global state manager — each interactive component owns its local `useState`.
- **Backend**: FastAPI, layered `api/v1` (routers) → `services` (business logic) → `schemas` (Pydantic contracts) → `services/store.py` (in-memory fixture "database," seeded with the same demo data that used to be hardcoded in the frontend). Contract: the frontend consumes the backend "exactly as if it were production," so swapping the fixture store for a real database and the fixture-backed `diagnosis_service`/`insight_service` for the future RAG pipeline requires no frontend rewrite — see `BACKEND_INTEGRATION_PLAN.md`.
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
- Python 3.13, isolated via `backend/.venv`

**Data fetching (frontend)**
- @tanstack/react-query — client-side caching, mutations, optimistic updates against the FastAPI backend

**Tooling**
- ESLint 9 (flat config)
- npm (frontend package manager)
- pip + venv (backend dependency management)

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
│   │   │   └── assessment/
│   │   │       └── page.tsx              # Patient Intake / Assessment screen route — async Server Component, fetches from FastAPI
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── top-nav.tsx
│   │   │   ├── home/
│   │   │   │   ├── hero-section.tsx       # rotating headline/badge + mic entry point (routes to /assessment)
│   │   │   │   └── quick-actions-bar.tsx  # fixed bottom pill (crop/type/draw/chat icons, visual-only)
│   │   │   ├── assessment/
│   │   │   │   ├── assessment-tabs.tsx
│   │   │   │   ├── patient-summary-card.tsx
│   │   │   │   ├── ptee-assistant-panel.tsx   # useQuery/useMutation against /assessments/{id}
│   │   │   │   ├── finding-row.tsx
│   │   │   │   ├── findings-list.tsx          # useQuery/useMutation against /assessments/{id}/findings
│   │   │   │   ├── log-test-panel.tsx
│   │   │   │   └── insights-panel.tsx         # useQuery against /assessments/{id}/insights
│   │   │   └── ui/                       # shadcn primitives (button, input)
│   │   └── lib/
│   │       ├── api.ts                    # typed fetch client for the FastAPI backend
│   │       ├── constants.ts              # DEFAULT_PATIENT_ID / DEFAULT_ASSESSMENT_ID (stand-in until patient routing exists)
│   │       └── utils.ts                  # cn() helper
│   ├── components.json                   # shadcn config
│   ├── .env.example                      # documents NEXT_PUBLIC_API_BASE_URL
│   └── package.json
└── backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                       # FastAPI app factory, CORS, /health, mounts /api/v1
    │   ├── core/
    │   │   ├── config.py                 # pydantic-settings (ALLOWED_ORIGINS)
    │   │   └── deps.py                   # get_current_user no-op stub (Phase 5 auth seam)
    │   ├── api/v1/
    │   │   ├── router.py                 # aggregates all /api/v1 routers
    │   │   ├── patients.py
    │   │   ├── assessments.py
    │   │   ├── findings.py
    │   │   ├── diagnosis.py
    │   │   ├── tests.py                  # "log a test"
    │   │   └── insights.py
    │   ├── schemas/                      # Pydantic request/response models, camelCase over the wire
    │   │   ├── base.py                   # CamelModel — shared alias-generator base
    │   │   ├── patient.py
    │   │   ├── assessment.py
    │   │   ├── finding.py
    │   │   ├── test.py
    │   │   └── insight.py
    │   └── services/                     # business logic + fixture store
    │       ├── store.py                  # in-memory fixture "database," seeded with demo patient/assessment
    │       ├── patients.py
    │       ├── assessments.py
    │       ├── findings.py
    │       ├── tests.py
    │       └── insights.py               # Phase 4 RAG seam
    ├── requirements.txt
    ├── .env.example                      # documents ALLOWED_ORIGINS
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
  - Collapsible Patient Summary card (patient fields, clinical summary, doctor's notes)
  - PTee Assistant panel: confidence meter, Cancel/Working-diagnosis/Complete↔Completed toggle, diagnosis Agree/Update/Fully-change block, and the green Reopen-diagnosis/Go-to-treatment-plan banner in the completed state
  - Findings list: 5 mock findings, per-row delete, per-row mic toggle (visual only), expandable question+bullet detail (populated for one reference row), and a "Type finding instead" manual override that replaces the AI-suggested label inline
  - Log a Test panel: Joint/Muscle/Gait type selector, test name + optional result fields, disabled-until-valid Save button
  - Insights panel: collapsible, AI-summary text, tagged finding with a "recorded" count badge

## UI Screens Completed

| Screen | Status |
|---|---|
| Patient Intake / Assessment tab (`/assessment`) | ✅ Built, pixel-matched |
| Landing / "tap to begin assessment" mic screen (`/`) | ✅ Built, pixel-matched |
| Treatment tab | ❌ Not built (tab label renders, no content; "Go to treatment plan" button is inert) |
| Home Plan tab | ❌ Not built |
| Evaluation tab | ❌ Not built |

## Backend APIs Implemented

All under `/api/v1`, fixture/in-memory-backed (no real database yet — see `BACKEND_INTEGRATION_PLAN.md` Phase 3). Seeded with one demo patient (`patient-1`, Ankita Sharma) and one demo assessment (`assessment-1`) matching the data that used to be hardcoded in the frontend.

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
| `/api/v1/assessments/{assessment_id}/tests` | GET, POST | Implemented — "Log a test" |
| `/api/v1/assessments/{assessment_id}/insights` | GET | Implemented (fixture summary/tags; Phase 4 RAG seam) |

The Assessment screen now fetches all of the above from the backend instead of hardcoded frontend data — the gap called out below in earlier entries is closed. Not yet implemented: auth (`get_current_user` is a wired-in no-op stub), voice endpoints, and Treatment/Home Plan/Evaluation endpoints (their tabs still render no content).

## AI & RAG Integration Progress

None. No AI/LLM calls, no RAG pipeline, no vector database, no embeddings anywhere in the codebase. Working diagnosis text, confidence percentage, and insight summaries are now served by the backend (`diagnosis`/`insights` fields on the `Assessment` fixture record and `insight_service.get_insights`) rather than hardcoded in frontend components, but the values themselves are still static fixture data, not produced by any model. `app/services/insights.py` and the diagnosis fields on `app/services/assessments.py` are the seams `BACKEND_INTEGRATION_PLAN.md` Phase 4 swaps for real RAG-backed generation, without changing the API contract.

## Deployment Progress

Not deployed. Verified locally only:
- Frontend: `npm run build` / `npm run dev` / `npm run start`
- Backend: `uvicorn app.main:app --reload`

Deployment plan was discussed but not executed: Vercel for the frontend (root directory `frontend`, no env vars needed yet since there's no live API integration), Render (or similar, not Vercel serverless) for the backend once real AI/RAG workloads exist, connected via `ALLOWED_ORIGINS` / `NEXT_PUBLIC_API_BASE_URL`. No CI/CD, no hosting accounts configured.

## Pending Tasks

- Build Treatment, Home Plan, and Evaluation tab content (frontend UI + backend routes, per `BACKEND_INTEGRATION_PLAN.md` Phase 3).
- Swap the placeholder Tailwind palette (default shadcn neutral tokens) for the actual Lovable design tokens/hex values once provided.
- Real voice capture for mic buttons (currently visual-only toggles); backend `/voice/*` endpoints (Phase 4).
- Real database (Postgres via SQLAlchemy/Alembic) to replace the in-memory fixture store in `backend/app/services/store.py` (Phase 3) — current data does not survive a backend restart.
- Real auth, multi-clinician / senior-review workflow (Phase 5) — `get_current_user` is currently a wired-in no-op.
- RAG pipeline behind `diagnosis_service`/`insight_service` (Phase 4).
- Deployment execution (Vercel + backend host) once there's a live integration worth deploying.
- Patient selection / routing UI — the Assessment screen currently always points at the one seeded demo patient/assessment (`DEFAULT_PATIENT_ID`/`DEFAULT_ASSESSMENT_ID` in `frontend/src/lib/constants.ts`); becomes a route param once patient list/creation UI exists.

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
