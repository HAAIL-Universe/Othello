# Othello Directive

## 0) Directive intent

This document is the execution law for building Othello.  
Anything not aligned with this directive is a bug, even if it “works.”

This directive is written to be LLM/collaborator-safe: it defines strict boundaries, stop conditions, and pass/fail acceptance criteria.

---

## 1) Non-negotiable rules

### 1.1 Contract-first, always
- Every externally visible payload has a defined schema.
- Every event/suggestion payload is validated server-side.
- No “shove JSON into a file and parse later” for core behavior.

### 1.2 DB is the only source of truth
- Canonical state lives in Postgres (Neon).
- Filesystem JSON/JSONL may exist only as:
  - test fixtures
  - write-only debug logs (never read by runtime)

Acceptance test: the app still runs for Phase 1 even if all non-test JSON files are deleted.

### 1.3 Transcript truth vs suggestions vs confirmed state
- Transcript is verbatim evidence.
- Suggestions are optional and pending.
- Confirmed state changes require explicit user confirmation.

### 1.4 No silent failure
If something fails:
- the user sees it (UI)
- logs capture it (server)
- state is not silently “pretended”

### 1.5 Voice pipeline is transient-audio by default
- Audio is used only to produce transcript.
- Delete audio after transcription success.
- If transcription fails, keep audio only for a short TTL to allow retries, then delete.

### 1.6 No unbounded prompt accumulation
Personalization must not be implemented by appending permanent text to a system prompt.

Use:
- structured user profile snapshots in DB
- bounded retrieval/injection per request

### 1.7 Consent governs coaching
- Nudges/influence strategies require explicit, granular consent.
- Influence modes are global per user (initially).
- All strategy usage must be inspectable via logs later phases.

### 1.8 Time handling
- Store all timestamps in UTC.
- User must set explicit IANA timezone at setup.
- Interpret day boundaries and scheduling in user-local time.

---

## 2) Architecture boundaries

### 2.1 Layers
1) API Layer: auth, validation, response formatting  
2) Persistence Layer: DB access helpers/DAO  
3) Transcript Layer: STT pipeline + message state  
4) Suggestion Layer: analysis and suggestion creation (no truth writes)  
5) Confirmation Layer: transform suggestion → DB truth  
6) Read Models: query endpoints for UI  
7) UI: renders read models; triggers actions

### 2.2 LLM boundary
LLM is allowed only for:
- generating suggestions from transcripts
- phrasing/coaching tone
- decomposing tasks into steps as suggestions

LLM is not allowed for:
- writing canonical truth directly
- deciding outcomes as facts
- mutating goal state without confirmation

If the LLM is unavailable, Phase 1 still works (manual goal/step entry remains possible).

---

## 3) Required interfaces (Phase 1)

### 3.1 Health/readiness
- `GET /health` fast, no auth.
- `GET /ready` for UI gating.

### 3.2 Auth (minimal, expandable)
- `POST /v1/auth/login`
- `POST /v1/auth/logout`
- `GET /v1/auth/me`

### 3.3 Voice + messages
- create message shell
- upload audio
- finalize/enqueue STT
- poll message status + transcript

### 3.4 Analysis (on-demand)
- analyze selected message IDs only
- create suggestions only

### 3.5 Confirmation
- accept/reject suggestions
- acceptance creates DB truth (goals/steps)
- rejection logs decision, does not mutate truth

### 3.6 Goals + steps + history
- read goals
- read goal detail
- tick steps
- complete goal
- read completed history and events

---

## 4) Data & schema rules

### 4.1 Multi-user discipline (even if single-user today)
Every row that belongs to a user must include `user_id`.

### 4.2 Event history
Maintain `goal_events` append-only. Do not try to “explain” history by overwriting rows.

### 4.3 Migration discipline
- schema changes are versioned
- projections/read endpoints have stable response shapes
- no silent contract drift

---

## 5) Reliability & observability

### 5.1 Logs
Logs must include:
- request_id
- route
- latency
- status
- user_id (where safe)
- message_id / suggestion_id / goal_id where applicable

### 5.2 Errors
Error responses must be structured:
- error_code
- message
- request_id
- details (optional validation errors)

UI must surface actionable failures.

---

## 6) UI behavior rules (Phase 1)

- UI does not compute truth; it calls endpoints.
- UI shows explicit states for:
  - transcription in progress
  - analysis in progress
  - pending suggestions
  - acceptance/rejection success/failure
- No infinite spinner with no explanation.

---

## 7) Engineering contribution rules (Copilot-safe)

Every change must declare:
- what contract/endpoint is affected
- what DB tables are affected
- how to verify the change

Stop and ask for human decision if:
- a schema change is needed without migration plan
- a feature requires unbounded prompt accumulation
- the only way forward is reading/writing JSON as truth
- a proposed shortcut risks silent data loss

---

## 8) Definition of Done (Phase 1)

Phase 1 is done only when:
- Voice transcript capture works end-to-end.
- Audio is deleted after transcription success.
- On-demand analysis creates pending suggestions.
- Accepting suggestions creates goals/steps in DB.
- Steps can be ticked; goals can be completed.
- History is readable from DB.
- Deleting non-test JSON files does not break Phase 1 flows.
