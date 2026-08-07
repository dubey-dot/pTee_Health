# PTee Health — Data Flow / Process Diagram

This documents the **data framework as actually implemented** in this repo:
how a request moves from a UI action on the Assessment screen, through the
Next.js frontend, into the FastAPI backend, down to Postgres, and — for the
two flows that aren't plain CRUD — out to the browser's Web Speech API and
the Anthropic Claude API.

This file is a structural reference only. For narrative history of *how*
each piece got built (and what was verified along the way), see
[`Progress.md`](Progress.md). For how to actually run the project, see
[`README.md`](README.md).

> **Keep this updated** whenever the data flow changes — a new endpoint, a
> new table, a new external call — the same standing convention already
> applied to `README.md`/`Progress.md`.

## 1. Full-stack data flow

```mermaid
flowchart TD
    subgraph Client["Client (Browser)"]
        UI["React components<br/>assessment-screen.tsx tree<br/>(PatientSummaryCard, DoctorNotesSection,<br/>PteeAssistantPanel, FindingsList, ...)"]
        RQ["TanStack Query<br/>client-side mutations + cache"]
        Speech["Web Speech API<br/>voice -&gt; text, client-only"]
    end

    subgraph NextServer["Next.js Server"]
        Pages["Server Components<br/>page.tsx routes<br/>(/, /patients/new, /patients,<br/>/patients/:id, /assessment, /assessment/:id)"]
        ApiClient["lib/api.ts<br/>single typed HTTP client"]
    end

    subgraph FastAPI["FastAPI backend — api/v1 routers"]
        R1["patients.py"]
        R2["assessments.py"]
        R3["findings.py"]
        R4["diagnosis.py"]
        R5["tests.py"]
        R6["insights.py"]
        R7["notes.py"]
    end

    subgraph Services["Services layer (services/*.py)"]
        S1["patients"]
        S2["assessments<br/>(+ generate_diagnosis)"]
        S3["findings"]
        S4["tests"]
        S5["insights"]
        S6["notes"]
        Engine["engines/<br/>ClaudeWorkingDiagnosisEngine"]
    end

    subgraph DB["Postgres"]
        T1[("patients")]
        T2[("assessment_sessions")]
        T3[("findings")]
        T4[("logged_tests")]
        T5[("doctor_notes")]
    end

    Claude[["External: Anthropic API<br/>claude-opus-5"]]

    Speech -->|transcribed text| UI
    UI --> RQ
    Pages -->|SSR initial fetch| ApiClient
    RQ -->|client fetch/mutate| ApiClient

    ApiClient -->|HTTP JSON, camelCase| R1
    ApiClient --> R2
    ApiClient --> R3
    ApiClient --> R4
    ApiClient --> R5
    ApiClient --> R6
    ApiClient --> R7

    R1 --> S1
    R2 --> S2
    R3 --> S3
    R4 --> S2
    R5 --> S4
    R6 --> S5
    R7 --> S6

    S1 --> T1
    S2 --> T2
    S3 --> T3
    S4 --> T4
    S5 --> T2
    S6 --> T5

    S2 -.->|"POST /diagnosis/generate<br/>triggers"| Engine
    Engine -->|structured-output call| Claude
    Claude -->|"diagnosis, confidence,<br/>insight summary + tags"| Engine
    Engine -.-> S2
```

## 2. Callout: AI diagnosis generation

The one flow with a real external network dependency. One combined
structured-output call produces diagnosis text, a confidence score, and the
insight summary/tags together — not three separate calls.

```mermaid
sequenceDiagram
    participant U as Doctor (PteeAssistantPanel)
    participant FE as Frontend (generateDiagnosis mutation)
    participant API as POST /assessments/{id}/diagnosis/generate
    participant SVC as services.assessments.generate_diagnosis
    participant ENG as ClaudeWorkingDiagnosisEngine
    participant AI as Anthropic Claude Opus 5
    participant DB as assessment_sessions row

    U->>FE: Click "Generate with AI"
    FE->>API: POST /assessments/{id}/diagnosis/generate
    API->>SVC: generate_diagnosis(db, assessment_id)
    SVC->>ENG: generate(patient_summary, clinical_summary, findings)
    ENG->>AI: client.messages.parse() structured output
    AI-->>ENG: diagnosis, confidence, insight_summary, insight_tags
    ENG-->>SVC: GeneratedAssessment
    SVC->>DB: persist diagnosis/confidence/insight_*, version += 1
    SVC-->>API: updated Assessment
    API-->>FE: 200 Assessment (or 502 on any Anthropic/key failure)
    FE-->>U: diagnosis panel updates; insights query invalidated
```

## 3. Callout: Doctor's Notes voice dictation

The one flow where the browser itself does work before anything reaches the
backend — no audio is ever sent over the wire, only the transcribed text.

```mermaid
sequenceDiagram
    participant D as Doctor
    participant Mic as Mic button (DoctorNotesSection)
    participant WS as Browser Web Speech API
    participant TA as Textarea (local content state)
    participant API as POST /assessments/{id}/notes
    participant SVC as services.notes.create_note
    participant DB as doctor_notes table

    D->>Mic: Click mic, speak
    Mic->>WS: recognition.start()
    WS-->>Mic: onresult (final transcript)
    Mic->>TA: append transcript, source = "voice"
    D->>Mic: Click "Save note"
    Mic->>API: POST {content, source: "voice"}
    API->>SVC: create_note(db, assessment_id, data)
    SVC->>DB: insert row, bump assessment.version
    SVC-->>API: DoctorNote
    API-->>Mic: 201 DoctorNote
    Mic-->>D: note appears in list, textarea clears
```

Typed notes follow the same `POST /assessments/{id}/notes` path, just
without the Web Speech API step and with `source: "typed"`.

## 4. Legend / current state

- **Everything in section 1 is real and DB-backed** — there is no
  fixture/in-memory store left anywhere in the backend; all seven routers
  (`patients`, `assessments`, `findings`, `diagnosis`, `tests`, `insights`,
  `notes`) persist to Postgres via SQLAlchemy.
- **The dashed edges** (`S2 -.-> Engine`, `Engine -.-> S2`) mark the one
  conditional branch — it only fires on `POST /diagnosis/generate`, not on
  every assessment request.
- **Not in this diagram because not built yet**: RAG/vector-DB retrieval
  (the Claude call reasons only over the current session's own findings,
  not a clinical knowledge base), the Recommendation Engine ("what to test
  next"), and Treatment/Home Plan/Evaluation data flows. See `Progress.md`
  → "Pending Tasks" for the full list.
