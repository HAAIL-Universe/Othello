# Othello Directive

## 0) Directive Intent

This document is the **execution law** for building Othello.

It defines:

- strict boundaries (what code may and may not do)
- quality rules (contracts, events, projections, UI behaviour)
- implementation constraints (cold starts, auth, logging)
- stop conditions (when to stop and ask for human intervention)

Anything not aligned with this directive is a bug, even if it “works.”

---

## 1) Non-Negotiable Rules

### 1.1 Contract-first, always

- Every externally visible payload must have a defined schema.
- Every event payload must be validated server-side.
- No “just shove JSON into a column and parse later” for core behaviours.

### 1.2 Ledger is the source of truth

- Canonical state changes happen via **event writes**.
- Projections/read models are derived from events.
- Do not create direct “update goal row” endpoints that bypass event emission.

### 1.3 UI never computes canonical truth

The UI:

- may display and format read models
- may cache read models
- may stage user input locally until committed

The UI must not:

- invent state not represented in read models
- “fix” server truth client-side
- compute progress metrics from partial local history when server truth exists

### 1.4 No silent failure

If something fails:

- user sees it
- logs capture it
- system does not pretend it succeeded

### 1.5 Cold-start safe is mandatory

Render Free cold starts are expected behaviour. The system must:

- expose `/ready` (or equivalent) for UI gating
- provide `/warmup` path if useful
- show a visible waking UI state with retry and explanation
- never show a blank screen or infinite spinner without context

### 1.6 Minimal auth now, expandable later

- Implement a single-user login gate now.
- All non-health endpoints require auth.
- Do not hardcode secrets into frontend or repo.
- Auth implementation must be modular enough to later support multi-user.

---

## 2) Architecture Boundaries

### 2.1 Layers

Othello is split into clear layers:

1. **API Layer**
   - request parsing, auth, validation, response formatting
2. **Contract Layer**
   - schemas and versioning rules
3. **Event Layer**
   - event creation, validation, persistence
4. **Projection Layer**
   - read model updates, rebuild utilities
5. **Planning Engine**
   - deterministic planning rules + optional LLM assist
6. **UI**
   - renders read models, emits events

### 2.2 LLM Boundary

LLM usage is allowed only for:

- phrasing and coaching tone
- decomposing tasks into smaller steps
- suggesting adjustments

LLM usage is not allowed for:

- deciding canonical truth (goal status changes, outcome facts)
- storing unstructured blobs as primary truth
- bypassing event writes

If LLM is unavailable, system must still function using deterministic rules.

---

## 3) Required Interfaces (Implementation Contract)

### 3.1 Health / readiness

- `GET /health` always returns quickly and never requires auth.
- `GET /ready` returns readiness for UI gating.
- Optional: `GET /warmup` to trigger wake paths.

### 3.2 Auth

Minimum endpoints:

- `POST /v1/auth/login`
- `POST /v1/auth/logout`
- `GET /v1/auth/me`

Rules:

- use secure token/session storage
- protect all non-health endpoints
- add rate limiting / brute-force protection (even minimal)

### 3.3 Event writes

- `POST /v1/events`
- `POST /v1/events/batch`

Rules:

- server validates event envelope + payload schema
- returns event ids
- batch responses are per-event (no all-or-nothing unless explicitly chosen)

### 3.4 Read endpoints

- `GET /v1/read/today-plan`
- `GET /v1/read/goals`
- `GET /v1/read/insights`
- `GET /v1/read/history`

Rules:

- only return read models (no raw table dumping)
- consistent response shapes
- pagination if needed

---

## 4) Data & Schema Rules

### 4.1 Event envelope required fields

Every event must include:

- `event_id` (UUID)
- `event_type` (string)
- `event_version` (int)
- `occurred_at` (timestamp)
- `actor_user_id`
- `payload`

Optional but recommended:

- `correlation_id`
- `session_id`
- `meta` (client version, UI surface)

### 4.2 Projection rebuild

The system must support:

- rebuilding projections from the ledger
- validating projection consistency

Projection rebuild is the escape hatch for corruption and schema changes.

---

## 5) Reliability & Observability Requirements

### 5.1 Logs

Logs must include:

- request id
- route
- latency
- status code
- user id (where safe)
- event ids for writes
- projection update success/failure

### 5.2 Error returns

Error responses must be structured:

- `error_code`
- `message`
- `request_id`
- optional `details` (validation errors, etc.)

### 5.3 No “console-only” errors

If the user needs to act, the UI must display the error state.

---

## 6) UI Behaviour Rules

### 6.1 Cold-start UI states

UI must implement explicit states:

- `WAKING_SERVER`
- `CHECKING_AUTH`
- `LOADING_DATA`
- `READY`
- `ERROR`

### 6.2 Event-first interactions

UI actions must map to events:

- create goal -> `goal_created`
- edit goal -> `goal_updated`
- generate plan -> `plan_generation_requested` then server emits `plan_generated`
- complete task -> `task_outcome_logged`

UI should never mutate read models locally and call it “done” without an event confirmation.

### 6.3 Offline / cache policy (if any)

If you add local caching:

- it must be marked as cache
- it must resync with server
- it must not overwrite server truth silently

---

## 7) Engineering Rules for Contributions (Copilot-safe)

### 7.1 Change discipline

Any change must specify:

- what contract changed (if any)
- what event(s) are emitted
- what projection(s) are updated
- what UI read model(s) are impacted
- how to test it

### 7.2 Stop conditions (when to stop and ask)

Stop and ask for human decision if:

- a change requires altering canonical schema without a version plan
- you cannot map a UI feature to events + projections cleanly
- adding a shortcut would bypass auth or ledger
- the only way forward is to store unstructured blobs as truth
- any change risks silent data loss

### 7.3 Minimal dependencies

Avoid adding heavy frameworks to “save time” if they:

- obscure truth boundaries
- increase cold-start time
- complicate deployment

---

## 8) Definition of Done (DoD)

A feature is “done” only when:

- contract is defined and validated
- event(s) are emitted and persisted
- read model is updated and queryable
- UI consumes read model and renders correct states
- errors are visible and logged
- tests exist for core logic (at least contract validation + projection correctness)

---

## 9) Immediate Build Priorities (Order of Operations)

1. Health/ready endpoints + cold-start UI state
2. Minimal auth gate (single-user)
3. Event ledger write path (+ validation)
4. Read model for Today Plan + Goals
5. Plan generation (deterministic) + plan_generated event
6. Task outcome logging + history view
7. Insight generation loop (rule-based, then optional LLM assist)
8. Projection rebuild tooling + integrity checks

---

## 10) Tone and Behaviour

Othello’s tone should be:

- calm
- direct
- execution-focused
- evidence-driven

No “woo.” No guilt. No fake certainty.  
If something is a suggestion, it must be labeled as such.
