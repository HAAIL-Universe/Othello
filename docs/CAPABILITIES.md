# Othello Capabilities (runtime inventory)
Source of truth: `core/capabilities_registry.py` (this doc is a snapshot).
## UI screens (current)
- Chat: message thread, mic button (browser SpeechRecognition), focus ribbon actions.
- Goals: list goals, open goal detail overlay, plan/step controls (subject to Phase-1 gating).
- Today Planner: brief + routines + goal tasks view.
- Routine Planner: placeholder view (no backend calls).
- Insights: list/apply/dismiss insight cards.
- Settings: dev reset (if enabled) and archive goal confirmation.
## Capabilities (test-oriented)
### Capabilities checklist
- How to trigger: Chat "what can you do", "help", "/help", "capabilities" or `GET /v1/capabilities`.
- Expected behavior: Deterministic list of capabilities from registry.
- Primary endpoint(s): `GET /v1/capabilities -> {version, generated_at, capabilities[]}`; `POST /api/message` (help patterns) -> `{reply, meta.intent=capabilities_help}`.
- How to verify: Call `/v1/capabilities`, then send "what can you do" in chat.
- Notes / limitations: Chat shortcut bypasses the LLM.
### Service health and readiness probes
- How to trigger: Call health endpoints from any client.
- Expected behavior: Health returns ok; readiness reports LLM config state; DB health checks connectivity.
- Primary endpoint(s): `GET /api/health -> {ok:true}`; `GET /ready -> {ok, ready, reason?}`; `GET /api/health/db -> {status, message, database}`; `GET /v1/health`; `GET /v1/ready`.
- How to verify: `curl /api/health` and `curl /ready` (DB check requires DATABASE_URL).
- Notes / limitations: `/ready` requires OPENAI_API_KEY to show ready.
### Session auth (login/me/logout)
- How to trigger: Login overlay or `POST /api/auth/login`.
- Expected behavior: Session cookie set; `/me` reports authed state.
- Primary endpoint(s): `POST /api/auth/login` body `{password|access_code|code|pin}` -> `{ok, auth_mode, user_id}`; `GET /api/auth/me -> {ok, authed, user_id}`; `POST /api/auth/logout -> {ok:true}`; v1 auth wrappers mirror these.
- How to verify: Log in, then `GET /api/auth/me` returns `authed:true`.
- Notes / limitations: Requires OTHELLO_* auth env and cookie support.
### Chat + goal-intent suggestions
- How to trigger: Chat view send message (text or mic -> SpeechRecognition).
- Expected behavior: Returns LLM reply; may include goal-intent suggestions; supports "list my goals" and "goal <id>" shortcuts.
- Primary endpoint(s): `POST /api/message` body `{message, goal_id?, active_goal_id?, current_mode?, current_view?, client_message_id?, ui_action?}` -> `{reply, meta?, agent_status?}`; `POST /api/suggestions/dismiss` body `{type, source_client_message_id} -> {ok:true}`.
- How to verify: Send a message; observe reply and suggestion panel (if any).
- Notes / limitations: Mic uses browser STT; no audio upload or server-side STT in this repo.
### Goal read + focus/unfocus
- How to trigger: Goals tab, "list my goals", "goal 1", or focus ribbon.
- Expected behavior: Lists goals, loads detail with steps, sets/clears active goal.
- Primary endpoint(s): `GET /api/goals -> {goals}`; `GET /api/goals/<goal_id> -> {goal}`; `GET /api/goals/active-with-next-actions -> {goals}`; `POST /api/goals/unfocus -> {ok, request_id}`.
- How to verify: Open Goals tab; open a goal detail; send "goal 1".
- Notes / limitations: Focus set via `/api/message` shortcut.
### Goal creation/notes/archive (legacy writes)
- How to trigger: Goal intent panel Save/Add or archive button (Phase-1 disabled).
- Expected behavior: Creates goals, adds notes, archives goals.
- Primary endpoint(s): `POST /api/goals` body `{title, description?, source_client_message_id?}` -> `{ok, created, goal_id}`; `POST /api/goals/<goal_id>/notes` body `{text}` -> `{ok, goal_id}`; `POST /api/goals/<goal_id>/archive -> {ok, status:'archived'}`.
- How to verify: Create a goal via `POST /api/goals`, then `GET /api/goals`.
- Notes / limitations: Blocked when OTHELLO_PHASE1 or OTHELLO_PHASE=phase1.
### Goal plan/step updates (legacy writes)
- How to trigger: Goal detail step toggles or plan generation (Phase-1 disabled).
- Expected behavior: Updates step status/detail or generates plan steps via LLM.
- Primary endpoint(s): `POST /api/goals/<goal_id>/steps/<step_id>/status` body `{status}` -> `{step}`; `POST /api/goals/<goal_id>/steps/<step_id>/detail` body `{detail, step_index?}` -> `{step}`; `POST /api/goals/<goal_id>/plan` body `{instruction?}` -> `{goal}`.
- How to verify: POST a step status update and re-fetch goal detail.
- Notes / limitations: Blocked in Phase-1; `/plan` requires LLM.
### Plan suggestions from text/intent (confirm-gated)
- How to trigger: Goal detail planner actions (plan_from_text_append/plan_from_intent).
- Expected behavior: Creates pending goal_plan suggestion; confirmation required.
- Primary endpoint(s): `POST /api/message` with `ui_action=plan_from_text_append` + `plan_text`; `POST /api/message` with `ui_action=plan_from_intent` + `{intent_index, intent_text}`; confirm via `POST /api/confirm` or `POST /v1/confirm`.
- How to verify: Submit plan text, then confirm via `/api/confirm`.
- Notes / limitations: Creates suggestions only; no auto-write.
### Suggestions pipeline (v1 analyze + confirm)
- How to trigger: `POST /v1/analyze` with message_ids.
- Expected behavior: Creates pending suggestions; listable and confirmable via v1 endpoints.
- Primary endpoint(s): `POST /v1/analyze` body `{message_ids:[int], llm_error_code?}` -> `{suggestions, analyzed_message_ids}`; `GET /v1/suggestions` -> `{suggestions}`; `POST /v1/confirm` body `{decisions:[{suggestion_id, action}]}` -> `{results}`.
- How to verify: Create a message via `/v1/messages`, then POST `/v1/analyze`.
- Notes / limitations: UI is not wired to `/v1/analyze`.
### Messages + sessions (v1)
- How to trigger: API client posts transcripts to `/v1/messages`.
- Expected behavior: Creates message/session records and supports status/transcript updates.
- Primary endpoint(s): `POST /v1/sessions -> {session_id}`; `POST /v1/messages` body `{transcript|text, source?, session_id?}` -> `{message}`; `GET /v1/sessions/<session_id>/messages`; `GET/PATCH /v1/messages/<message_id>`; `POST /v1/messages/<message_id>/finalize` body `{transcript}`.
- How to verify: POST `/v1/messages`, then GET `/v1/messages/<id>`.
- Notes / limitations: No audio upload/STT endpoints in this repo.
### History + goal task log read
- How to trigger: API read of goal events or task history.
- Expected behavior: Returns recent goal events or task history slice.
- Primary endpoint(s): `GET /v1/read/history?limit=100 -> {events}`; `GET /api/goal-tasks/history?status?&start_date?&end_date?&days? -> {goal_tasks}`.
- How to verify: GET `/v1/read/history?limit=10`.
- Notes / limitations: Goal task history is API-only; UI does not call it.
### Today plan + brief
- How to trigger: Mode switch -> Today Planner view.
- Expected behavior: Returns plan sections and brief; supports update/rebuild.
- Primary endpoint(s): `GET /api/today-plan?mood?&fatigue?&time_pressure? -> {plan}`; `GET /api/today-brief?mood?&fatigue?&time_pressure? -> {brief}`; `POST /api/plan/update` body `{item_id, status, ...}`; `POST /api/plan/rebuild` body `{mood_context?}`.
- How to verify: Open Today Planner view and confirm brief + sections render.
- Notes / limitations: Not part of Phase-1 scope.
### Insights inbox
- How to trigger: Insights tab in UI.
- Expected behavior: Lists pending insights; apply/dismiss updates status and counts.
- Primary endpoint(s): `GET /api/insights/summary -> {pending_counts}`; `GET /api/insights/list?status=pending -> {insights}`; `POST /api/insights/apply` body `{id}` -> `{ok, applied_count}`; `POST /api/insights/dismiss` body `{id}` -> `{ok}`.
- How to verify: Open Insights tab; apply/dismiss if any entries exist.
- Notes / limitations: Insight creation depends on LLM/DB; apply may create goals/plan items.
### Admin reset (dev only)
- How to trigger: Settings -> Dev reset (requires OTHELLO_ENABLE_DEV_RESET=true).
- Expected behavior: Wipes DB tables and returns truncated table list.
- Primary endpoint(s): `GET /api/admin/capabilities -> {dev_reset_enabled}`; `POST /api/admin/reset` body `{confirm:'RESET'} -> {ok, tables}`.
- How to verify: Call `/api/admin/capabilities`, then POST `/api/admin/reset` with confirm=RESET.
- Notes / limitations: Destructive; dev only.
## Phase-1 confirmation flow (code-based)
- Implemented: v1 messages + analyze + suggestions + confirm; confirm applies goal/goal_plan suggestions via DB.
- Implemented: chat goal-intent suggestions with explicit user confirmation in UI (Save/Add).
- Missing: audio upload + server-side STT endpoints (`/v1/messages/{id}/audio`), and UI wiring for `/v1/analyze`.
- Gated: legacy /api goal/step writes are blocked when Phase-1 flags are enabled.
