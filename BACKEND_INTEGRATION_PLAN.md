# PTee Health — Backend Integration Plan

Status: proposal / roadmap. Written 2026-08-02 against the codebase described in `Progress.md` and `Current_devlopment.md`: a pixel-matched, frontend-only Assessment screen (`/assessment`) and Home screen (`/`), plus a FastAPI skeleton with a single `/health` route. No feature endpoints, no auth, no database, no AI/RAG exist yet.

This document is the implementation roadmap for turning that static UI into a real client of a real backend, without a frontend rewrite and without over-building ahead of actual need.

---

## 1. Current Architecture Overview

**Frontend** — Next.js 16 (App Router, Turbopack), React 19, TypeScript, Tailwind v4, shadcn/ui (`base-nova`/Base UI, not Radix). Two routes: `/` (hero/mic entry) and `/assessment`. No router-level data fetching, no global state manager — every interactive component (`FindingsList`, `PteeAssistantPanel`, `LogTestPanel`, `PatientSummaryCard`, `InsightsPanel`) owns local `useState` and is seeded with hardcoded defaults or hardcoded props passed from `assessment/page.tsx`.

**Backend** — FastAPI 0.116, Uvicorn, Python 3.13, one route (`GET /health`), env-configurable CORS (`ALLOWED_ORIGINS`). No routers, no models, no DB, no auth, no config layer beyond CORS.

**Data today**: 100% frontend-local. Concretely, the shapes already implied by the UI are:

| Concept | Where it lives now | Shape (inferred from props/types) |
|---|---|---|
| Patient summary | `assessment/page.tsx` constants | `{ name, fields: {label, value}[], clinicalSummary, doctorsNotesCount }` |
| Findings | `findings-list.tsx` `INITIAL_FINDINGS` | `{ id, tag, label, selected?, detail?: {question, bullets[]} }` |
| Working diagnosis / confidence | `ptee-assistant-panel.tsx` props | `{ confidence: number, diagnosis: string, status: "reviewing"\|"completed" }` |
| Logged test (write-only today) | `log-test-panel.tsx` `LoggedTest` | `{ type: "joint"\|"muscle"\|"gait", name, result }` |
| Insights | `insights-panel.tsx` props | `{ summary: string, tags: {label, meta}[] }` |

This table is effectively the first draft of the API contract — the frontend has already told us what shape it expects.

**Gap**: none of this is served by or persisted to the backend. There's also no patient identity yet — `/assessment` isn't parameterized by a patient ID, and Treatment/Home Plan/Evaluation tabs render labels only, no content.

---

## 2. Guiding Principles

1. **Contract-first, not rewrite-first.** The existing component prop shapes above already match what a REST response should look like. Design endpoints to return those shapes (or a thin superset) so wiring is "swap hardcoded const for `useQuery` result," not a component redesign.
2. **Mock-as-production.** `Progress.md` already states the intent: the frontend should consume the backend "exactly as if it were production." That means even Phase 2's endpoints should be real FastAPI routes backed by fixtures/in-memory data, not `/health`-style stubs — swapping fixtures for a real DB or a real LLM later must not change response shapes.
3. **No premature infrastructure.** No auth, no DB, no message queue, no RAG until the phase that needs it. Each phase below adds exactly one layer of real capability.
4. **Additive extensibility.** Every endpoint is versioned (`/api/v1/...`) and scoped under a patient/assessment resource so Treatment/Home Plan/Evaluation and future AI features are new routes under the same tree, not breaking changes to existing ones.

---

## 3. Recommended Backend Architecture

Restructure `backend/app/` from a single `main.py` into a conventional layered FastAPI layout — small enough to not be over-engineering for the current feature set, but shaped so routers/services/models don't need to be invented later under time pressure:

```
backend/
├── app/
│   ├── main.py                 # app factory, CORS, router registration
│   ├── core/
│   │   ├── config.py           # pydantic-settings: ALLOWED_ORIGINS, DATABASE_URL, etc.
│   │   └── deps.py             # shared FastAPI dependencies (auth, db session)
│   ├── api/
│   │   └── v1/
│   │       ├── router.py       # aggregates sub-routers under /api/v1
│   │       ├── patients.py
│   │       ├── assessments.py
│   │       ├── findings.py
│   │       ├── diagnosis.py
│   │       ├── tests.py        # "log a test"
│   │       └── insights.py
│   ├── schemas/                # Pydantic request/response models (the real contract)
│   │   ├── patient.py
│   │   ├── assessment.py
│   │   ├── finding.py
│   │   └── insight.py
│   ├── models/                 # ORM models (added in Phase 2, once persistence lands)
│   ├── services/                # business logic, kept out of route handlers
│   │   ├── diagnosis_service.py   # later: calls the RAG/LLM layer
│   │   └── insight_service.py
│   └── db/
│       └── session.py          # SQLAlchemy engine/session (Phase 2+)
├── requirements.txt
└── .env.example
```

**Why this shape:**
- `schemas/` separated from `models/` from day one avoids the common FastAPI trap of leaking ORM objects into API responses once a DB is added in Phase 2 — no breaking response-shape changes later.
- `services/` gives the future RAG/diagnosis pipeline (Phase 4) a seam to plug into (`diagnosis_service.generate()`), so the route handler in `diagnosis.py` never needs to change when the implementation behind it goes from "return fixture" to "call vector DB + LLM."
- `api/v1/` versioning costs nothing now and avoids a painful migration if the contract needs to change after the frontend is already live against it.

**Database recommendation**: PostgreSQL, accessed via SQLAlchemy 2.x + Alembic for migrations. Postgres over something lighter (SQLite/Mongo) because: relational data (patients → assessments → findings → tests) fits relational modeling well, `pgvector` gives a low-friction path to the vector DB requirement in Phase 4 without introducing a second datastore, and it's what Render (already the planned backend host per `Progress.md`) supports as a managed add-on.

---

## 4. Frontend ↔ Backend Communication

**Transport**: plain REST/JSON over `fetch`, no GraphQL — the data shapes are simple and mostly resource-scoped (patient → assessment → findings), which is exactly what REST models well, and it avoids adding a schema/codegen layer to a two-person-scale project.

**API client**: introduce a thin `frontend/src/lib/api.ts` wrapping `fetch` with the base URL from `NEXT_PUBLIC_API_BASE_URL` (already named as a planned env var in `Progress.md`), shared error handling, and typed request/response helpers per resource. This is the one new piece of frontend infrastructure this plan requires before any endpoint gets wired up.

**State/data-fetching library**: adopt **TanStack Query (React Query)**. Rationale — the app has no global state manager today and doesn't need one (Redux/Zustand would be overkill for what's still page-local data), but it does need request caching, revalidation-after-mutation (e.g., re-fetch findings after `POST /tests`), and loading/error states that `useState` + raw `fetch` would otherwise hand-roll per component. This is the smallest addition that solves those problems without imposing a global store.

**Data flow (example — Findings list)**:
```
FindingsList (client component)
   └─ useQuery(["findings", assessmentId]) ──GET /api/v1/assessments/{id}/findings──▶ FastAPI
   └─ useMutation(deleteFinding) ──DELETE /api/v1/findings/{id}──▶ FastAPI
        └─ onSuccess: invalidateQueries(["findings", assessmentId])
```
Optimistic UI (e.g., instant row removal on delete) stays exactly as it is today — React Query's `onMutate` slot lets the existing local `setFindings` pattern be reused, backed by a rollback on error instead of being replaced.

**Server vs. client components**: preserve the current split. `assessment/page.tsx` becomes an `async` Server Component that does the *initial* fetch (patient summary, assessment, findings) server-side — better first paint, no loading spinner flash for the primary content — and passes results as `initialData` into React Query on the client, which then owns subsequent interactivity/mutations. Purely interactive panels (`LogTestPanel`, per-row voice toggle) stay client-only as today.

---

## 5. What's Fetched On-Demand vs. Cached vs. Persisted

| Data | Persisted (DB) | Cache strategy | Notes |
|---|---|---|---|
| Patient record | Yes | React Query, `staleTime` ~5min | Rarely changes mid-session |
| Assessment (status, confidence, diagnosis) | Yes | React Query, invalidate on any mutation to findings/diagnosis | Drives the confidence meter + banner state |
| Findings list | Yes | React Query, invalidate on add/delete/relabel | Optimistic updates on delete/relabel |
| Logged tests | Yes (append-only) | Not cached client-side beyond the mutation response; refetch findings/insights after save | Write-heavy, read-rarely from this screen |
| Insights | Derived/generated, cached server-side (see below) | React Query, invalidate when findings or tests change | Expensive to (re)compute once real AI is behind it — cache server-side per assessment version, not just recomputed per request |
| Auth session/token | N/A (Phase 5) | httpOnly cookie or short-lived JWT in memory, not localStorage | See Auth section |
| Static reference data (test-type list, tag taxonomy) | Yes, but changes rarely | Long `staleTime` / could ship as static JSON initially | Not worth a DB round-trip on every page load |

General rule: anything the clinician is actively editing (findings, diagnosis, test log) is fetched per-assessment and invalidated on mutation; anything AI-generated and non-trivial to compute (insights, future RAG-grounded diagnosis text) should be cached server-side keyed by assessment state version, so re-opening a completed assessment doesn't re-trigger an LLM call.

---

## 6. Proposed API Endpoint Structure

All under `/api/v1`. Resource-nested where there's a real containment relationship (findings belong to an assessment), flat where a resource is addressed directly (finding delete/update by its own id, matching what `FindingsList` already does).

```
Auth (Phase 5)
POST   /auth/login
POST   /auth/logout
GET    /auth/me

Patients
GET    /patients                          list (search/filter, "New" vs "Existing")
POST   /patients                          create
GET    /patients/{patient_id}             detail — feeds PatientSummaryCard
PATCH  /patients/{patient_id}

Assessments  (an assessment belongs to a patient; Assessment/Treatment/Home Plan/Evaluation tabs
              are sub-resources or sub-documents of one assessment, not separate top-level records)
GET    /patients/{patient_id}/assessments
POST   /patients/{patient_id}/assessments          create new assessment (mic-button entry flow)
GET    /assessments/{assessment_id}                feeds AssessmentTabs status + PteeAssistantPanel
PATCH  /assessments/{assessment_id}                status transitions (reviewing → completed), diagnosis action

Findings
GET    /assessments/{assessment_id}/findings
POST   /assessments/{assessment_id}/findings       add finding (manual or voice-derived)
PATCH  /findings/{finding_id}                      relabel ("Type finding instead")
DELETE /findings/{finding_id}

Diagnosis
GET    /assessments/{assessment_id}/diagnosis      { diagnosis, confidence, status }
PATCH  /assessments/{assessment_id}/diagnosis      agree / update / fully-change actions

Tests ("Log a test")
GET    /assessments/{assessment_id}/tests
POST   /assessments/{assessment_id}/tests          { type, name, result }

Insights
GET    /assessments/{assessment_id}/insights       { summary, tags[] } — server-cached, see §5

Voice (Phase 3, stubbed behind a real route earlier if useful)
POST   /assessments/{assessment_id}/voice/findings  audio in → finding(s) out
POST   /assessments/{assessment_id}/voice/notes     audio in → doctor's note text out

Treatment / Home Plan / Evaluation (Phase 3+, currently unbuilt tabs)
GET/POST /assessments/{assessment_id}/treatment-plan
GET/POST /assessments/{assessment_id}/home-plan
GET/POST /assessments/{assessment_id}/evaluation

Health
GET    /health                             already implemented, keep as-is (unversioned, for infra checks)
```

This maps 1:1 onto existing components — no endpoint invents a data shape the frontend doesn't already imply.

---

## 7. Data Flow Diagram

```
┌─────────────────────────┐        REST/JSON (fetch + React Query)       ┌──────────────────────────┐
│  Next.js Frontend        │ ───────────────────────────────────────────▶ │  FastAPI Backend          │
│  (Server + Client comps) │ ◀─────────────────────────────────────────── │  /api/v1/*                │
└─────────────────────────┘                                               └──────────────────────────┘
        │  initial SSR fetch                                                       │
        │  (patient, assessment, findings)                                         │  services/
        ▼                                                                          ▼
┌─────────────────────────┐                                               ┌──────────────────────────┐
│  React Query cache       │                                               │  diagnosis_service        │
│  (client-side, per       │                                               │  insight_service           │
│   assessmentId key)      │                                               │  (Phase 4: calls RAG/LLM) │
└─────────────────────────┘                                               └──────────────────────────┘
                                                                                     │
                                                                                     ▼
                                                                            ┌──────────────────────────┐
                                                                            │  PostgreSQL (+pgvector)   │
                                                                            │  patients, assessments,   │
                                                                            │  findings, tests           │
                                                                            └──────────────────────────┘
                                                                                     ▲
                                                                            ┌──────────────────────────┐
                                                                            │  Phase 4+: RAG pipeline,   │
                                                                            │  healthcare API adapters   │
                                                                            │  (called from services/,   │
                                                                            │   never from routes)       │
                                                                            └──────────────────────────┘
```

The key architectural point: routes never call the RAG pipeline or a healthcare API directly — they call a `service`, and the service decides whether that means "read a fixture," "query Postgres," or "call the LLM." That indirection is what lets Phase 4 land without touching `api/v1/*.py` or any frontend code.

---

## 8. Feature Modules — How Each Should Interact with the Backend

- **Auth**: out of scope until Phase 5, but every route from Phase 2 onward should already accept an (initially optional/no-op) `current_user` dependency in `core/deps.py`, so adding real auth later is "make the dependency enforce" rather than "thread a new parameter through every handler."
- **Patient records**: CRUD via `patients.py`. `PatientSummaryCard`'s free-text `fields` array is convenient for the UI but a poor DB shape — model patient fields as real typed columns (name, age, gender, occupation, chief_complaint, etc.) server-side, and have the API response assemble the `{label, value}[]` array for the frontend. Keeps the DB schema meaningful (queryable, validated) while the frontend contract stays unchanged.
- **Assessments**: the container for one clinical encounter's Assessment/Treatment/Home Plan/Evaluation state. `AssessmentTabs`' active/inert tab styling should eventually be driven by which sub-resources exist/are complete on the assessment, not hardcoded tab logic.
- **Clinical reasoning (diagnosis + confidence)**: `diagnosis_service.py` is the seam. Phase 2: returns a fixture. Phase 4: calls the RAG pipeline grounded on findings + patient history, returns the same `{diagnosis, confidence, status}` shape. Route and frontend are untouched by that swap.
- **Treatment plans / Home Plan / Evaluation**: currently unbuilt UI. Recommend building their backend routes (even fixture-backed) in Phase 3 alongside the frontend screens, following the same pattern as Assessment, rather than designing them speculatively now.
- **Insights**: same seam pattern as diagnosis — `insight_service.py` abstracted from day one so Phase 4 can swap "static tag list" for "RAG-derived insight" without a contract change.

---

## 9. Future Integration Points (No Major Refactor Required)

- **RAG pipeline**: lives entirely behind `diagnosis_service` / `insight_service`. Vector DB is `pgvector` on the same Postgres instance (no second datastore to provision/secure/monitor for a project this size); embeddings generated on finding/note write, retrieval happens inside the service layer at diagnosis/insight generation time.
- **Vector database**: if retrieval volume or embedding-model requirements later outgrow `pgvector` (e.g., need for a managed ANN index at scale), the service-layer indirection means swapping in Pinecone/Weaviate/etc. only touches `services/`, not routes or frontend.
- **Healthcare API integrations** (none selected yet per `Progress.md`): add as `services/integrations/<provider>.py` adapters called from the relevant service (e.g., an EHR lookup called from `patients.py`'s service layer), never called directly from routes or the frontend. Each adapter owns its own auth/retry/rate-limit handling.
- **Voice capture**: mic buttons are currently visual-only toggles. When real capture lands, the frontend records audio client-side and `POST`s it (or a stream) to `/voice/findings` or `/voice/notes`; the backend owns transcription + NLP extraction. No change to how `FindingRow`/`PatientSummaryCard` render results — they already just take a `label`/text string.

---

## 10. Phased Implementation Plan

**Phase 2 — Backend skeleton → real fixture-backed API** (foundation for everything else)
- Restructure `backend/app/` per §3 (routers/schemas/services, no DB yet).
- Implement all Phase-2-relevant endpoints from §6 (patients, assessments, findings, diagnosis, tests, insights) backed by in-memory/fixture data mirroring today's hardcoded frontend constants.
- Add `frontend/src/lib/api.ts` + React Query provider.
- Wire `/assessment` to fetch from these endpoints instead of hardcoded defaults; preserve all existing interactions (delete, relabel, log test, diagnosis actions) as mutations against the fixture API.
- Outcome: frontend behavior is pixel- and behavior-identical to today, but every value now round-trips through FastAPI. This is the milestone `Current_devlopment.md` calls out as the next major gap.

**Phase 3 — Persistence + remaining screens**
- Add Postgres + SQLAlchemy + Alembic; migrate fixtures into real tables/models.
- Build Treatment, Home Plan, Evaluation tab content (frontend) + their routes (backend), following the Assessment pattern.
- "Go to treatment plan" / tab navigation becomes real routing, not inert buttons.

**Phase 4 — Voice, RAG, AI**
- Implement voice capture + `/voice/*` endpoints (transcription).
- Stand up the RAG pipeline (embeddings + `pgvector` retrieval) behind `diagnosis_service`/`insight_service`; swap fixture responses for LLM-generated, retrieval-grounded ones.
- No frontend or route-signature changes required if §7's service-boundary discipline was followed in Phase 2–3.

**Phase 5 — Auth, multi-clinician, healthcare integrations, deployment**
- Real auth (session/JWT), enforce the `current_user` dependency stubbed in Phase 2.
- Multi-clinician / senior-review workflow backing the existing "Senior review" pill.
- First healthcare API integration(s), once a provider is selected.
- Execute the deployment plan already sketched in `Progress.md`: Vercel (frontend), Render + managed Postgres (backend), `ALLOWED_ORIGINS` / `NEXT_PUBLIC_API_BASE_URL` wired between them; add CI/CD.

Each phase ships a working app — nothing here requires a big-bang cutover, and Phase 2 alone closes the single biggest gap called out in both `Progress.md` and `Current_devlopment.md`.

---

## 11. Risks, Assumptions, Recommendations

**Assumptions**
- Single-clinician, single-tenant usage until Phase 5 — no multi-tenancy modeling needed before then.
- Postgres is an acceptable operational dependency (a managed instance on Render); if there's a strong preference for a different DB or a serverless/edge deployment target, that changes §3/§9 and should be confirmed before Phase 3 starts.
- No healthcare API vendor is selected yet — §9's adapter pattern is designed to defer that decision safely, not to predict which vendor.

**Risks**
- **Contract drift risk is low but not zero**: because endpoint shapes are derived directly from existing component props, the main risk is scope creep during Phase 2 (e.g., "while we're at it, let's redesign findings") that would desync frontend and backend mid-phase. Recommendation: freeze the response shapes in §1/§6 before starting Phase 2 implementation.
- **Insights/diagnosis caching correctness**: caching AI-generated content server-side (§5) is only safe if cache keys correctly capture "assessment state version" — a bug here could show stale diagnosis text after new findings are added. Needs a concrete versioning strategy (e.g., a monotonic `updated_at`/version column on the assessment) designed during Phase 2, even though it isn't exercised until Phase 4.
- **`npm audit`'s 3 unpatched high-severity transitive vulnerabilities** (noted in `Current_devlopment.md`) should be triaged before Phase 5 deployment, not left indefinitely.
- **Git remote situation** (`origin` unreachable, pushes going to `dubey-dot/pTee_Health.git` directly) is a process risk for a growing team, independent of this plan — worth resolving before more contributors touch the repo.

**Recommendations**
- Do Phase 2 exactly as scoped — resist adding auth or a DB to it. The fixture-backed API is what unblocks frontend integration fastest and de-risks the contract before persistence adds migration concerns.
- Adopt the `services/` seam (§3, §8) even though Phase 2 doesn't need it — retrofitting it after routes call fixtures directly is exactly the kind of refactor this plan is designed to avoid.
- Decide the real Lovable design tokens (also flagged as pending in both source docs) independently of this plan — it's unrelated to backend integration and shouldn't block Phase 2.
