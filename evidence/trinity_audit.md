# Trinity Audit

## Found Docs
- build_docs/othello_blueprint.md
- build_docs/othello_manifesto.md
- build_docs/othello_directive.md

## Current State
- Branch: main
- HEAD: 8dd692dd4f5eed4c07c8c7139074e6521152e3d7

## Normalized Doc Outline

### Phases and Deliverables (Blueprint)
- Phase 0 - Foundation: auth + user settings (timezone), DB schema and migration discipline, core contracts.
- Phase 1 - Goal OS v0: voice capture -> transcript; audio deletion after transcription; on-demand analysis -> suggestions only; confirm suggestions into goals/steps; goal focus mode; step tick-off; goal completion; goal history.
- Phase 2 - Today Plan v1: Today Plan home + mic; user-initiated plan confirmation; plan candidates from conversation + rollover; onboarding prompts (night-before).
- Phase 2.5 - Ship-ready beta: auth and session security (secure cookies), multi-user isolation, beta gate, production hygiene, confirm-gated writes; acceptance criteria listed.
- Phase 3 - In-app coaching nudges: consent, influence modes, caps, logs.
- Phase 4 - Push notifications: PWA push, same policy engine.
- Phase 5 - Subscription tier + persona growth: subscription gating, structured persona snapshots.
- Phase 6 - Magistus interoperability: external read access with confirm-gated mutations.

### Acceptance Criteria (Blueprint + Directive)
- Phase 1 done only when voice transcript capture works end-to-end, audio is deleted after transcription success, on-demand analysis creates pending suggestions, accepting suggestions creates goals/steps, steps can be ticked, goals completed, history readable from DB, and deleting non-test JSON does not break Phase 1 flows.
- Phase 2.5 done when auth gating, strict user scoping, beta gate, and clear-data behavior are verified.

### Non-negotiables (Manifesto + Directive)
- Contract-first, DB truth only, transcript truth vs suggestions vs confirmed state, confirm-gated writes.
- UI renders read models only; no client-side truth fixes.
- No silent failure; structured errors; logs required.
- Consent governs coaching; time is stored UTC and interpreted in user-local time.

## Codebase Scan

### System Map (evidence)
- Backend entrypoint: api.py (Flask app, v1 blueprint registration, root route serves UI via send_file).
- Core planning engine: core/day_planner.py and core/othello_engine.py.
- DB layer: db/database.py, db/schema.sql, db/*_repository.py (goals, suggestions, messages, plans, routines).
- UI entrypoint: othello_ui.html (single-page app with Today Planner, Goals, Insights, Routine Planner).
- Phase markers: api.py Phase-1 DB-only mode flags and write blocks; core/day_planner.py Phase 9.5 merge logic markers.

### Implemented Capability Inventory (evidence-backed)
- Auth/session: /api/auth/login, /api/auth/me, /api/auth/logout plus v1 wrappers (api.py auth_login/auth_me/auth_logout and v1_auth_*). Session cookie config in api.py app.config.
- Health/readiness: /api/health, /ready, /api/health/db plus v1 /health and /ready (api.py health_check, ready_check, health_check_db, v1_health_check, v1_ready_check).
- Messages + sessions (v1): /v1/sessions, /v1/messages, /v1/messages/{id}, /v1/messages/{id}/finalize (api.py v1_create_session, v1_messages, v1_get_message, v1_finalize_message).
- Suggestions + confirmation: /v1/analyze, /v1/suggestions, /v1/confirm, /api/confirm (api.py v1_analyze, v1_list_suggestions, v1_confirm, api_confirm; _apply_suggestion_decisions).
- Goals: /api/goals, /api/goals/{id}, /api/goals/unfocus, /api/goals/{id}/steps/{step_id}/status, /api/goals/{id}/notes, /api/goals/{id}/archive (api.py route handlers).
- Routines: /api/routines CRUD and routine steps (api.py routines routes).
- Today Plan: /api/today-plan, /api/today-brief, /api/plan/update, /api/plan/rebuild; v1 /read/today and /plan/draft (api.py get_today_plan, get_today_brief, plan_update, plan_rebuild, v1_read_today, v1_plan_draft; core/day_planner.py; db/schema.sql plan tables).
- UI: Today Planner view, routine planner, goals, insights, mic button using SpeechRecognition (othello_ui.html sections around mic button and today planner, calls to /api/today-plan and /v1 endpoints).

## Phase Mapping (Evidence-Backed)

### Phase 0 - Foundation
- Auth + user settings (timezone): PARTIAL. Auth endpoints in api.py; users.timezone in db/schema.sql; plan timezone helpers in api.py and db/plan_repository.py, but no explicit timezone setup UI.
- DB schema and migration discipline: PARTIAL. db/schema.sql exists; no migration tooling in repo.
- Core contracts and versioning: PARTIAL. v1 envelope helpers exist in api.py; no explicit contract versioning file.

### Phase 1 - Goal OS v0
- Voice capture -> transcript: PARTIAL. UI uses browser SpeechRecognition and sends text; server accepts transcripts via /v1/messages (api.py v1_messages). No server-side audio pipeline.
- Audio deletion after transcription: NOT STARTED. No /v1/messages/{id}/audio or audio TTL/delete handling in api.py.
- On-demand analysis -> suggestions only: PARTIAL. /v1/analyze exists (api.py v1_analyze) but is heuristic and UI is not wired to it.
- Confirm suggestions -> goals/steps: PARTIAL. /api/confirm and /v1/confirm apply suggestions (api.py _apply_suggestion_decisions), but legacy /api goal writes still exist and are phase-blocked by env flags.
- Goal focus mode: PARTIAL. Active goal focus endpoints exist (/api/goals/active-with-next-actions, /api/goals/unfocus) and UI has focus ribbon; confirm flow is mixed between /api/message and /api/goals.
- Step tick-off + goal completion + history: PARTIAL. Step status endpoint exists (/api/goals/{id}/steps/{step_id}/status) and history read is available (/v1/read/history); explicit goal completion endpoint is not evident.
- Deleting non-test JSON does not break runtime: NOT VERIFIED.

### Phase 2 - Today Plan v1
- Home = Today Plan + mic: PARTIAL. Today Planner view and mic button exist in UI; /api/today-plan and /api/today-brief exist in api.py.
- User-initiated plan confirmation: PARTIAL. /v1/plan/draft + /v1/confirm create plan-item suggestions, but /api/today-plan still renders blended plans and UI primarily reads /api/today-plan.
- Plan candidates from conversation + rollover: PARTIAL. /v1/plan/draft supports message_ids and include_rollover (api.py v1_plan_draft).
- Onboarding prompts (night-before): NOT STARTED. No prompt workflow detected in UI or API.

### Phase 2.5 - Ship-ready Beta
- Auth/session security (OAuth, server-side session cookie): PARTIAL. Session cookie config exists; auth is access-code based, not OAuth; cookie secure flag depends on runtime.
- Multi-user isolation: PARTIAL. user_id fields exist in schema and queries use session user_id; no explicit RLS or allowlist enforcement visible.
- Beta gate (150 user cap/allowlist): NOT STARTED. No allowlist/cap logic found.
- Production hygiene: PARTIAL. /api/health and /api/health/db exist; no migrations tooling visible.
- Confirm-gated write integrity: PARTIAL. Confirm flow exists, but legacy endpoints still present and gated only by env flags.

### Phase 3 - Coaching Nudges
- NOT STARTED. No consent management, influence modes, or logs found.

### Phase 4 - Push Notifications
- NOT STARTED. No push/PWA delivery layer found.

### Phase 5 - Subscription + Persona
- NOT STARTED. No subscription gating or persona snapshot storage found.

### Phase 6 - Magistus Interop
- NOT STARTED. No external integration surface beyond current API.

## Risks / Drift
- Voice pipeline drift: directive expects audio upload + deletion TTL; current UI uses browser STT with no server audio handling.
- Phase 2.5 gate drift: allowlist/cap and OAuth are not present; risk if beta expansion starts without guardrails.
- Contract mismatch: v1 endpoints exist, but UI still relies on /api/today-plan for planner and only partially uses v1 flows.
- DB truth vs JSON: data/ JSON files exist; phase flags disable JSON fallbacks, but enforcement depends on env configuration.

## Recommended Next Phase
1) Complete Phase 1 voice pipeline and confirmation loop.
   - Acceptance: /v1/messages/{id}/audio upload exists; transcription results in transcript; audio deleted after success or TTL; /v1/analyze + /v1/confirm wired end-to-end in UI.
   - Evidence bundle if UI bugs: console errors, network trace (request/response), and repro steps.
2) Harden Phase 2.5 ship-ready security and gating.
   - Acceptance: server-side allowlist or hard cap enforced; auth uses secure cookies with rotation on login; /v1/auth/me gates UI; no cross-user data reads in tests.
3) Align Today Plan workflow with confirmation semantics.
   - Acceptance: plan creation is user-initiated and confirm-gated; /v1/plan/draft + /v1/confirm flow becomes the primary path; UI uses /v1/read/today for read model.
