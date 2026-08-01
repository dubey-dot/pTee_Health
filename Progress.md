# PTee Health — Project Progress

Single source of truth for project status. Updated after every meaningful task — entries are appended, not overwritten.

---

## Project Overview

PTee Health is an AI-powered Clinical Decision Support Platform for physiotherapists. **Phase 1** (current phase) is scoped strictly to the **Patient Intake / Assessment screen** of the clinical journey, replicated pixel-for-pixel from Lovable-generated UI reference screenshots, backed by a lightweight FastAPI service that will later be swapped for real AI/RAG/clinical services without requiring frontend changes.

Long-term vision (not yet started): an AI-powered clinical reasoning pipeline (RAG over clinical knowledge), healthcare API integrations, and full patient journey coverage (Assessment → Treatment → Home Plan → Evaluation).

## Architecture

- **Frontend**: Next.js App Router. Server Components for static layout; Client Components (`"use client"`) for anything with interactive state (panels, toggles, forms). No global state manager — each interactive component owns its local `useState`.
- **Backend**: FastAPI, mocked REST endpoints. Intended contract: the frontend consumes the backend "exactly as if it were production," so swapping mocked responses for real AI/RAG output later requires no frontend rewrite. **Not yet wired up** — see Backend APIs section.
- **Data flow today**: The Assessment screen is entirely frontend-local. Mock finding/diagnosis/insight data is hardcoded as component defaults/props; nothing is fetched from the backend yet.
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
- Python 3.13, isolated via `backend/.venv`

**Tooling**
- ESLint 9 (flat config)
- npm (frontend package manager)
- pip + venv (backend dependency management)

## Folder Structure

```
PTeeHealth/
├── PROJECT_PROGRESS.md
├── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                  # Home / hero "tap to begin" landing screen
│   │   │   ├── layout.tsx
│   │   │   ├── globals.css               # Tailwind v4 tokens (default shadcn palette — not yet swapped for Lovable's real tokens)
│   │   │   └── assessment/
│   │   │       └── page.tsx              # Patient Intake / Assessment screen route
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── top-nav.tsx
│   │   │   ├── home/
│   │   │   │   ├── hero-section.tsx       # rotating headline/badge + mic entry point (routes to /assessment)
│   │   │   │   └── quick-actions-bar.tsx  # fixed bottom pill (crop/type/draw/chat icons, visual-only)
│   │   │   ├── assessment/
│   │   │   │   ├── assessment-tabs.tsx
│   │   │   │   ├── patient-summary-card.tsx
│   │   │   │   ├── ptee-assistant-panel.tsx
│   │   │   │   ├── finding-row.tsx
│   │   │   │   ├── findings-list.tsx
│   │   │   │   ├── log-test-panel.tsx
│   │   │   │   └── insights-panel.tsx
│   │   │   └── ui/                       # shadcn primitives (button, input)
│   │   └── lib/utils.ts                  # cn() helper
│   ├── components.json                   # shadcn config
│   └── package.json
└── backend/
    ├── app/
    │   ├── __init__.py
    │   └── main.py                       # FastAPI app, CORS, /health
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

| Endpoint | Method | Status |
|---|---|---|
| `/health` | GET | Implemented — returns `{"status": "ok"}` |

No feature endpoints exist yet. Findings, diagnosis, insights, and "log a test" data are all hardcoded in frontend components — **not** served by the backend. This is the next major integration gap (see Pending Tasks).

## AI & RAG Integration Progress

None. No AI/LLM calls, no RAG pipeline, no vector database, no embeddings anywhere in the codebase. All "AI-generated" content visible in the UI (working diagnosis text, confidence percentage, insight summaries) is static placeholder data used purely to match the reference design pixel-for-pixel — not produced by any model.

## Deployment Progress

Not deployed. Verified locally only:
- Frontend: `npm run build` / `npm run dev` / `npm run start`
- Backend: `uvicorn app.main:app --reload`

Deployment plan was discussed but not executed: Vercel for the frontend (root directory `frontend`, no env vars needed yet since there's no live API integration), Render (or similar, not Vercel serverless) for the backend once real AI/RAG workloads exist, connected via `ALLOWED_ORIGINS` / `NEXT_PUBLIC_API_BASE_URL`. No CI/CD, no hosting accounts configured.

## Pending Tasks

- Build Treatment, Home Plan, and Evaluation tab content.
- Wire the Assessment screen to real backend endpoints (findings, working diagnosis, insights, log-a-test submission) instead of hardcoded frontend data.
- Swap the placeholder Tailwind palette (default shadcn neutral tokens) for the actual Lovable design tokens/hex values once provided.
- Real voice capture for mic buttons (currently visual-only toggles).
- Auth, database, and persistence layer (explicitly out of scope until a later phase per project scope).
- Deployment execution (Vercel + backend host) once there's a live integration worth deploying.

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
