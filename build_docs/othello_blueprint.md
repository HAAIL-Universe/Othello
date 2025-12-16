# Othello Blueprint

## 0) Blueprint intent

This document defines **what must exist** in Othello and how it is structured from idea → completion.  
It is the architecture truth. If code deviates, code is wrong.

Othello is built to be:

- contract-first and debuggable
- database-truth (Neon/Postgres)
- voice-first UX with transcript-as-truth
- confirmation-gated inference
- scalable without rewriting core boundaries

## 1) Product scope by phase (end-goal roadmap)

### Phase 0 — Foundation (contract + DB truth)
- Auth + user settings (timezone)
- DB schema and migration discipline
- Core contracts and versioning

### Phase 1 — Goal Operating System (v0)  ✅ current build target
Deliverable: goals + steps + completion + history driven by transcript truth.

- Voice capture → external STT → verbatim transcript
- Audio deletion after transcription (or TTL after failure)
- On-demand analysis to *suggestions only*
- Confirm suggestions into goals and steps
- Goal Focus Mode: goal-scoped conversation + analysis
- Step tick-off, goal completion, goal history

### Phase 2 — Today Plan (v1)
- Home = Today Plan + mic button
- User-initiated plan confirmation (authority rule)
- Plan candidates seeded from conversation and rollover (non-authoritative)
- Onboarding prompts (night-before; repeat on first open if unanswered)

### Phase 3 — In-app coaching nudges (v2)
- Explicit consent + influence modes (global per user)
- Policy-driven nudges inside app only (caps, quiet hours)
- Influence logs (“why I said this”) and revocation

### Phase 4 — Push notifications (v3)
- PWA push first; native later optional
- Same policy engine, just another delivery channel
- Strict limits + quiet hours + audit logs

### Phase 5 — Subscription tier + persona growth (v4)
- Subscription gating for advanced coaching modes
- Persona snapshots are structured and versioned (no prompt bloat)
- Transparency: inspectable logs + controls

### Phase 6 — Magistus interoperability (v5)
- Magistus can query Othello as an execution subsystem
- Othello remains authoritative for goals/plans/outcomes
- Mutations require Othello’s confirmation contracts

## 2) Canonical boundaries (truth disciplines)

### 2.1 Truth layers
- **Transcript truth**: messages as verbatim text.
- **Inference**: suggestions, tagged as pending.
- **Confirmed state**: goals/steps/plans/outcomes in DB.
- **Policy**: consent and influence modes constrain outputs.
- **Audit**: explainability logs and events.

### 2.2 “DB is truth” rule
No runtime reads from JSON/JSONL for authoritative state.

Allowed file usage:
- tests fixtures
- write-only debug logs (never read in runtime)

## 3) Canonical entities (conceptual)

- User (timezone, notification prefs, influence policy)
- Session (conversation container)
- Message (verbatim transcript, source voice/text)
- Suggestion (pending/accepted/rejected; provenance links to messages)
- Goal (confirmed)
- Goal Step (confirmed; ordered)
- Goal Event (append-only history: created/updated/step_done/completed/etc.)
- Plan (later phase)
- Outcome (later phase, but step completion is a basic outcome)
- Insight (derived; confirm-gated if it changes behavior)
- Consent (versioned)
- Influence Log (why/when/how a nudge was produced)

## 4) Storage model (recommended, Neon/Postgres)

### 4.1 Core tables (Phase 1 minimum)
- `users`
- `sessions`
- `messages`
- `suggestions`
- `goals`
- `goal_steps`
- `goal_events` (append-only)

### 4.2 Suggested columns (Phase 1)
**users**
- user_id (uuid pk)
- email/username (as used)
- timezone (IANA string)
- created_at_utc

**messages**
- message_id (uuid pk)
- user_id
- session_id (nullable)
- source (voice|text)
- transcript (text, verbatim)
- status (uploading|transcribing|ready|failed)
- stt_provider, stt_model (nullable)
- audio_duration_ms (nullable)
- error (nullable)
- created_at_utc

**suggestions**
- suggestion_id (uuid pk)
- user_id
- kind (goal|step|constraint|insight|plan_item)
- status (pending|accepted|rejected)
- payload_json (jsonb)
- provenance_message_ids (uuid[])
- created_at_utc
- decided_at_utc (nullable)

**goals**
- goal_id (uuid pk)
- user_id
- title
- intent (optional)
- status (active|paused|completed|archived)
- priority (optional)
- target_date (optional date)
- created_at_utc
- updated_at_utc

**goal_steps**
- step_id (uuid pk)
- goal_id
- user_id
- title
- status (todo|done|dropped)
- order_index (int)
- created_at_utc
- updated_at_utc

**goal_events**
- event_id (uuid pk)
- user_id
- goal_id (nullable for pre-goal events)
- event_type (goal_created|step_added|step_done|goal_completed|etc.)
- payload_json (jsonb)
- occurred_at_utc

### 4.3 Later tables (phases 2–5)
- plans, plan_items, outcomes
- insights + evidence refs
- consents, influence_prefs, influence_logs
- audit_events

## 5) External services

### 5.1 Speech-to-text
- Use external STT API for long-form capture.
- Audio is transient; transcript is stored.
- Support chunked upload later if needed.

### 5.2 LLM usage
LLM is allowed for:
- generating suggestions from transcripts
- phrasing/coaching tone
- task decomposition proposals

LLM is NOT allowed for:
- writing canonical truth without confirmation
- silently changing schedules or goal state
- storing unstructured blobs as primary truth

## 6) API surface (v1, contract-first)

### 6.1 Health
- `GET /health` (no auth; fast)
- `GET /ready` (UI gating)

### 6.2 Auth (single-user now, expandable)
- `POST /v1/auth/login`
- `POST /v1/auth/logout`
- `GET /v1/auth/me`

### 6.3 Messages (voice-first)
- `POST /v1/messages` (create message shell)
- `POST /v1/messages/{id}/audio` (upload audio)
- `POST /v1/messages/{id}/finalize` (enqueue STT)
- `GET /v1/messages/{id}` (status + transcript)

### 6.4 Analysis (on-demand)
- `POST /v1/analyze` (message_ids[] → suggestions created)

### 6.5 Confirmation
- `POST /v1/suggestions/{id}/accept`
- `POST /v1/suggestions/{id}/reject`

### 6.6 Goals (read models)
- `GET /v1/read/goals`
- `GET /v1/read/goals/{goal_id}`
- `POST /v1/goals/{goal_id}/steps` (manual add; still evented)
- `POST /v1/steps/{step_id}/status` (tick off)
- `POST /v1/goals/{goal_id}/complete`
- `GET /v1/read/history` (completed goals + events)

## 7) UI requirements (Phase 1)

Minimum screens:
- Login
- Chat (voice + transcript view) with Analyze button
- Suggestions Inbox (pending)
- Goals list
- Goal detail (steps + tick)
- History (completed goals)

Strict rules:
- UI renders read models.
- UI never computes canonical truth.
- If something fails, user sees it.

## 8) Acceptance criteria (Phase 1)

Phase 1 is “done” when:
- A user can record voice, receive transcript, and audio is deleted.
- On-demand analyze creates pending suggestions.
- Accepting a suggestion creates DB goals and steps.
- Steps can be ticked off; goals can be completed.
- History is readable and explainable from DB.
- Deleting all non-test JSON files does not break these flows.
