# Othello Blueprint

## 0) Blueprint Intent

This document defines **what must exist** in Othello and how it is structured.

It is a build map for an implementation that is:

- contract-first
- event-ledger driven
- projection/read-model backed
- cold-start safe on Render Free
- minimal-auth gated for single-user early builds
- expandable without rewriting core logic

This is the “architecture truth” for Othello. If code deviates, code is wrong.

---

## 1) System Model

### 1.1 Entities (conceptual, not necessarily DB tables)

- **User**: initially a single-user deployment; designed to become multi-user.
- **Goal**: long-lived intent (“ship Othello,” “stream weekly,” “build WQT V2”).
- **Routine**: repeatable sequence (“morning reset,” “evening shutdown”).
- **Task**: smallest executable action; always attached to a plan or routine.
- **Plan**: a time-bounded hypothesis (Today Plan, Next 3 Days, etc.).
- **Outcome**: what actually happened for a task instance.
- **Insight**: a derived conclusion from repeated outcomes.
- **Constraint**: time window, energy level, available tools, “workday vs rest day,” etc.

### 1.2 Canonical Data Discipline

- **Events** are the only source of truth.
- **Read models** are derived views for UI and API.
- **Contracts** define the shape of every event and read model.

---

## 2) Contract Layer

### 2.1 Contract Versioning

- All external API payloads are versioned (e.g., `v1`).
- Contract changes require:
  - explicit version bump (major/minor rules)
  - migration logic for projections if needed
  - compatibility plan for old clients (even if “old client” is just yesterday)

### 2.2 Canonical Schemas (minimum set)

The system accepts flexible input (chat, forms, quick actions), but internally it stores only canonical shapes.

#### A) Goal

Fields (canonical):

- `goal_id` (UUID)
- `title` (string)
- `intent` (string: why this exists)
- `status` (`active|paused|completed|archived`)
- `priority` (`low|med|high|critical`)
- `created_at`, `updated_at`
- `tags` (string[])
- `success_definition` (string)
- `constraints` (optional object)
- `target_date` (optional date)
- `owner_user_id` (UUID; single-user for now but always present)

#### B) Routine

- `routine_id` (UUID)
- `title`
- `schedule` (e.g., days-of-week or trigger rules)
- `steps` (ordered list of routine step definitions)
- `default_duration_minutes` (optional)
- `status`
- `tags`
- timestamps

#### C) Plan (Today Plan)

- `plan_id` (UUID)
- `plan_date` (YYYY-MM-DD)
- `generated_at`
- `mode` (`workday|restday|custom`)
- `time_budget_minutes` (optional)
- `tasks` (ordered list of task instances)
- `assumptions` (list of planning assumptions)
- `generation_reason` (what triggered generation)
- `inputs_snapshot` (summary of constraints used)

#### D) Task Instance

- `task_id` (UUID)
- `plan_id` (UUID)
- `title`
- `description` (optional)
- `source` (`goal|routine|ad_hoc|system`)
- `linked_goal_id` (optional)
- `linked_routine_id` (optional)
- `estimate_minutes` (optional int)
- `difficulty` (`easy|medium|hard`)
- `order_index` (int)
- `created_at`

#### E) Outcome (task execution record)

- `task_id` (UUID)
- `plan_id` (UUID)
- `status` (`done|partial|skipped|blocked`)
- `completed_at` (timestamp)
- `duration_minutes` (optional)
- `block_reason` (optional string)
- `notes` (optional string)
- `confidence` (optional 0–1)
- `evidence` (optional; minimal, not essay)
- `created_at`

#### F) Insight

- `insight_id` (UUID)
- `created_at`
- `type` (e.g., `friction_pattern|time_pattern|context_switch|overcommit|undercommit`)
- `statement` (one sentence)
- `evidence_refs` (links to event ids / plan ids / outcome ids)
- `recommended_adjustment` (one actionable change)
- `severity` (`low|med|high`)
- `tags`

---

## 3) Event Ledger

### 3.1 Event Envelope (required for every event)

- `event_id` (UUID)
- `event_type` (string)
- `event_version` (int)
- `occurred_at` (timestamp)
- `actor_user_id` (UUID)
- `session_id` (optional)
- `correlation_id` (optional; ties multiple events together)
- `payload` (schema by event_type)
- `meta` (optional: client_version, ui_surface, etc.)

### 3.2 Core Event Types (minimum viable set)

**Identity / Access**
- `user_authenticated`
- `user_logged_out`

**Goals**
- `goal_created`
- `goal_updated`
- `goal_status_changed`
- `goal_deleted` (prefer soft delete; if used, must still be evented)

**Routines**
- `routine_created`
- `routine_updated`
- `routine_status_changed`
- `routine_step_completed` (optional early; may be treated as task outcomes)

**Planning**
- `plan_generation_requested`
- `plan_generated`
- `plan_regenerated` (if you re-run generation for same day)
- `plan_archived`

**Execution**
- `task_outcome_logged`
- `task_reordered` (optional; if UI supports reorder)
- `task_edited` (optional; changes should be evented)

**Reflection / Insights**
- `reflection_logged`
- `insight_generated`
- `adjustment_applied` (explicitly record “we changed the plan logic because…”)

### 3.3 Ledger Storage Requirements

- Append-only storage
- Strong ordering by `occurred_at`
- Query by:
  - time range
  - event_type
  - correlation_id / session_id
  - user_id
- Never drop events silently
- Every write returns persisted `event_id`

---

## 4) Read Models (Projections)

Read models exist to make the UI fast and deterministic.

### 4.1 Required Read Models

**A) Today Plan View**
- `GET /v1/read/today-plan?date=YYYY-MM-DD`
- Returns `Plan` + derived summary:
  - total tasks
  - estimated time
  - completed count
  - blocked count
  - streak metrics (optional)
  - “top 1–3 focus” (derived)

**B) Goals List View**
- active goals with progress signals derived from outcomes:
  - tasks completed related to goal in last 7/30 days
  - last activity
  - next recommended action (derived)

**C) Insights Summary View**
- recent insights (last N days)
- grouped by type
- each includes evidence refs and recommended adjustment

**D) History Timeline View**
- plans by date
- per-day completion ratio
- key blockers and notes

### 4.2 Projection Update Strategy

Option 1 (recommended initially): synchronous projection updates at write-time  
- event write -> update projections -> return

Option 2: asynchronous worker  
- safer for scale, more complex; can be added later

Either way, projections must be:

- reproducible from ledger + config
- versioned if schema changes
- validated by tests

---

## 5) Planning Engine

### 5.1 Planning Inputs (canonical)

- active goals
- active routines
- constraints:
  - `time_budget_minutes`
  - `day_type` (workday/restday)
  - `energy_level` (low/med/high)
  - hard constraints (appointments)
- recent outcomes (last X days)
- recent insights + applied adjustments

### 5.2 Planning Outputs

- a single Today Plan (ordered tasks)
- task sizing rules:
  - prefer tasks <= 20 minutes where possible
  - include 1 “anchor task” (main focus)
  - include 1 “maintenance task” (small win)
  - include 1 “admin/cleanup task” if needed
- explicit assumptions list (to keep planning explainable)

### 5.3 AI Usage Boundary

LLM may help:
- rephrase tasks
- suggest decompositions
- suggest adjustments

But the final plan must be representable as canonical schema and recorded as `plan_generated` event.

If LLM is unavailable:
- fall back to deterministic heuristics (rule-based planning)

---

## 6) API Surface (v1)

### 6.1 Health & Cold Start

- `GET /health` -> { status, time, version }
- `GET /warmup` -> triggers cold-start wake path; returns progress state
- `GET /ready` -> returns ready boolean for UI gating

### 6.2 Auth (minimal now, expandable later)

- `POST /v1/auth/login` (single-user secret/password)
- `POST /v1/auth/logout`
- `GET /v1/auth/me`

Rules:
- All read/write endpoints require auth.
- Auth must not be embedded as “security by obscurity.”
- Token/session must be stored safely (httpOnly cookie preferred for web).

### 6.3 Event Write Endpoints

- `POST /v1/events` -> append one event (server validates schema)
- `POST /v1/events/batch` -> append multiple (atomic per-event responses)

### 6.4 Read Model Endpoints

- `GET /v1/read/today-plan`
- `GET /v1/read/goals`
- `GET /v1/read/insights`
- `GET /v1/read/history`

---

## 7) UI Requirements (contract consumer)

### 7.1 Core Screens

- Login / Gate
- Today Planner
- Goals
- Insights
- History
- Chat (optional; but must emit structured events behind the scenes)

### 7.2 Cold Start UX

The UI must handle Render Free cold starts explicitly:

- On load:
  - ping `/ready`
  - if not ready: show “Waking server…” with retry + explanation
  - once ready: proceed to auth check and load models

No infinite spinner. No blank screen.

### 7.3 Truth Boundaries

- UI renders read models.
- UI emits events (never writes directly to tables/projections).
- Any local caching must be clearly marked as cache and resynced.

---

## 8) Observability & Reliability

### 8.1 Logging

- Every API request: request_id, user_id (if available), route, latency, status.
- Every event write: event_id, event_type, schema version.
- Every projection update: projection name, duration, success/failure.

### 8.2 Error Policy

- No silent failures.
- If event write fails, UI shows explicit error and does not pretend success.
- If projection fails but event write succeeded:
  - return warning and trigger repair path
  - UI may degrade gracefully but must inform.

### 8.3 Repair / Rebuild Projections

- Endpoint or admin-only function:
  - rebuild projections from ledger
- Must be safe and repeatable.

---

## 9) Data Storage & Migration

### 9.1 Database

- Postgres (Neon-compatible).
- At minimum:
  - `events` table (ledger)
  - projection tables (read models)
  - `users` (even if single-user)

### 9.2 Migration Discipline

- Schema migrations are versioned.
- Contract changes tracked.
- Projection migrations can be done by:
  - backfilling from ledger
  - or rebuild projections

---

## 10) Security & Privacy

- Minimal personal data stored.
- No secrets in frontend code.
- Rate limit auth endpoints.
- Store tokens safely.
- Add audit events for auth and sensitive actions.

---

## 11) Acceptance Criteria (Definition of “Othello v1 MVP”)

Othello is “v1 MVP complete” when:

- Render deploy loads with explicit cold-start UI.
- Login gate works (single-user).
- You can:
  - create/update a goal (evented)
  - generate a Today Plan (evented)
  - log outcomes for tasks (evented)
  - view Today Plan / Goals / Insights / History via read models
- Projections are reproducible from ledger.
- No silent failures; errors are visible and logged.
