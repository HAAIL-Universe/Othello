# Goal Handling and Updating Audit

## Scope and sources
- Repo focus: goal creation/focus, plan/step storage, plan step rendering, and step updates across UI -> API -> DB.
- Trinity sources read:
  - `build_docs/othello_manifesto.md` (contract-first, DB truth, UI lens, replayable truth).
  - `build_docs/othello_blueprint.md` (Phase 1 goals + steps + completion; API surface requirements).
  - `build_docs/othello_directive.md` (non-negotiable contract-first, DB truth, no silent failure, event history).

## Trinity constraints and clauses (relevant excerpts)
- Data integrity + contract discipline:
  - `build_docs/othello_manifesto.md`: "Contract before cleverness" and "DB is truth; JSON is not truth".
  - `build_docs/othello_directive.md`: "Contract-first, always" and "DB is the only source of truth".
- UX/interaction expectations:
  - `build_docs/othello_blueprint.md`: "Step tick-off, goal completion, goal history".
  - `build_docs/othello_directive.md`: "UI does not compute truth; it calls endpoints." and "No silent failure".
- Persistence/auditability:
  - `build_docs/othello_manifesto.md`: "Truth is replayable" and "Everything is explainable".
  - `build_docs/othello_directive.md`: "Maintain `goal_events` append-only. Do not try to \"explain\" history by overwriting rows."
- Minimal diffs / contracts:
  - `build_docs/othello_directive.md`: "Every change must declare:" and "no silent contract drift".

## Current end-to-end flow (UI -> API -> manager -> repo -> schema)

### UI state + focus handling
- State: `othelloState.activeGoalId`, `othelloState.currentDetailGoalId`, `othelloState.currentView`, `othelloState.currentMode` in `othello_ui.html` (see `othello_ui.html:2290`).
- Focus logic: `setActiveGoal` updates `activeGoalId`, updates ribbon, and updates focus view; `hideGoalDetail` clears `currentDetailGoalId` in `othello_ui.html` (see `othello_ui.html:3323` and `othello_ui.html:4269`).

### Goal detail rendering + plan steps
- `renderGoalDetail` in `othello_ui.html` renders plan steps when `goal.plan_steps` exists; otherwise falls back to `goal.plan` string (see `othello_ui.html:3956` and `othello_ui.html:4067`).
- Steps are grouped by section labels parsed from encoded descriptions (see `db/db_goal_manager.py:629` decode path).
- Activity log buttons "Add to Current Plan" and intent "Build plan" are rendered in the goal detail view (see `othello_ui.html:4037` and `othello_ui.html:3976`).

### Click delegation for plan buttons
- Activity log: `.plan-from-activity-btn` on Othello messages calls `postPlanFromText` in `othello_ui.html` (see `othello_ui.html:4347`).
- Intent list: `.intent-plan-btn` calls `postPlanFromIntent` in `othello_ui.html` (see `othello_ui.html:4348`).
- Both are delegated from the `#detail-content` container (see `othello_ui.html:4279`).

### API payload keys and routing (handle_message)
- Payload keys used from UI: `goal_id`, `active_goal_id`, `ui_action`, `current_mode`, `current_view`, `plan_text` (see `othello_ui.html:3605`).
- `api.py` `handle_message` branches:
  - `ui_action == "plan_from_text_append"`: parses steps -> `append_goal_plan` or `save_goal_plan_section` (see `api.py:1339`).
  - `ui_action == "plan_from_text"`: parses steps -> `save_goal_plan` (legacy overwrite path, still present) (see `api.py:1419`).
  - `ui_action == "plan_from_intent"`: LLM plan -> `save_goal_plan_section` (see `api.py:1479`).

### GoalManager / DbGoalManager
- `DbGoalManager.append_goal_plan` in `db/db_goal_manager.py` appends steps using `get_max_plan_step_index` (see `db/db_goal_manager.py:535`).
- `DbGoalManager.save_goal_plan` deletes all steps first (overwrite) (see `db/db_goal_manager.py:486`).
- `DbGoalManager.save_goal_plan_section` deletes only matching section prefix and appends (see `db/db_goal_manager.py:579`).
- `DbGoalManager.get_goal_with_plan` loads plan steps, decodes section prefix with `_decode_plan_step_description`, and attaches step details from `goal_events` (see `db/db_goal_manager.py:629`).

### Repository functions
- `goals_repository.create_plan_steps`, `delete_plan_steps_for_goal`,
  `delete_plan_steps_for_goal_section`, `get_max_plan_step_index` in `db/goals_repository.py` (see `db/goals_repository.py:400`).
- `goal_events_repository.list_latest_step_details` uses goal_id + step_id scoping for step detail retrieval (see `db/goal_events_repository.py:113`).

### Schema (plan_steps)
- `db/schema.sql` `plan_steps` columns:
  - `id` (PK), `goal_id` (FK), `step_index` (unique per goal),
  - `description`, `status`, `due_date`, `created_at`, `updated_at`.

## Overwrite root cause (confirmed)
- "Add to Current Plan" previously used `ui_action=plan_from_text` via `postPlanFromText` in `othello_ui.html` (now `plan_from_text_append`, see `othello_ui.html:3605`).
- `api.py` handles legacy `plan_from_text` by calling `DbGoalManager.save_goal_plan` (see `api.py:1419`).
- `DbGoalManager.save_goal_plan` calls `goals_repository.delete_plan_steps_for_goal`, which deletes all steps for the goal (see `db/db_goal_manager.py:510`).
- Result: each "Add to Current Plan" action wiped existing steps before the append path was added.

## Step detail save bug (root cause)
- API endpoint `POST /api/goals/{goal_id}/steps/{step_id}/detail` validates by step_id membership in `get_plan_steps_for_goal` (see `db/db_goal_manager.py:730`).
- UI originally only sent `step_id` (from DOM) with no `step_index` fallback (see `othello_ui.html:4282` in the click handler).
- If the UI posts a non-PK identifier (e.g., step_index used as step_id in older data shapes), the API rejects with "Step not found or does not belong to this goal" (`api.py:2800`).

## Step identity lifecycle note
- `save_goal_plan` deletes all plan_steps for a goal before inserting new ones (see `db/db_goal_manager.py:510`), which produces new step IDs.
- `save_goal_plan_section` deletes steps by section prefix (see `db/db_goal_manager.py:600`), which also recreates step IDs for that section.
- Step details are stored in `goal_events` keyed by step_id, so regenerated steps will not show older detail entries unless the steps are updated in place.

## Trinity alignment comparison (current behavior)
- Compliant:
  - Plan steps are stored in Postgres `plan_steps` (DB truth) and returned via `get_goal_with_plan`.
  - UI renders read model from `/api/goals/{id}`.
  - Step completion + step detail are persisted via API endpoints and goal_events.
- Needs decision:
  - Legacy `ui_action=plan_from_text` still deletes all steps if called directly; UI now uses `plan_from_text_append`, but the overwrite endpoint remains available for other clients.

## Proposed/implemented change set (minimal, contract-driven)
1) Add plan append action (no overwrite):
   - New `ui_action=plan_from_text_append` routed in `api.py`.
   - `DbGoalManager.append_goal_plan` appends steps using `get_max_plan_step_index`.
   - Default section label added for readability; existing plan steps preserved.
2) Step completion toggle:
   - UI adds checkbox per step and uses existing `POST /api/goals/{goal_id}/steps/{step_id}/status`.
   - Refreshes goal detail after status update for persistence visibility.
3) Step detail storage + UI:
   - New endpoint `POST /api/goals/{goal_id}/steps/{step_id}/detail`.
   - Details stored as append-only `goal_events` with `event_type=step_detail`, keyed by `step_id`.
   - `get_goal_with_plan` attaches latest detail to `plan_steps` for read model.
   - Added `step_index` fallback for detail updates, API warning when legacy shape is used, and debug logging (see `api.py:2848`, `api.py:2896`, `db/db_goal_manager.py:730`, `othello_ui.html:3700`, `othello_ui.html:4282`).
4) Plan display efficiency:
   - Plan steps rendered in compact rows with checkbox + truncated label.
   - Details collapsed by default, expanded on demand.

## Change-to-Trinity mapping (explicit)
- `plan_from_text_append` + `append_goal_plan`:
  - Aligns with "Contract before cleverness" by preserving step records and keeping mutations explicit.
  - Aligns with "DB is truth; JSON is not truth" because steps are persisted in `plan_steps`.
  - Addresses "No silent failure" by returning explicit errors on validation and save failures.
- Step completion toggle (`/api/goals/{goal_id}/steps/{step_id}/status` UI):
  - Aligns with "Step tick-off, goal completion, goal history".
  - Aligns with "UI does not compute truth; it calls endpoints."
- Step detail storage via `goal_events`:
  - Aligns with "Maintain `goal_events` append-only. Do not try to \"explain\" history by overwriting rows."
  - Aligns with "Truth is replayable" and "Everything is explainable" by keeping detail changes as events.
- Compact plan display:
  - Aligns with "UI does not compute truth; it calls endpoints." (read-model only).
  - No schema changes; no contract drift.

## API contract addendum (new/updated)
- `POST /api/message` with `ui_action=plan_from_text_append`
  - Request body keys: `plan_text`, `goal_id`, `active_goal_id`, `current_mode`, `current_view`.
  - Response: `{ reply, meta: { intent: "plan_steps_added" }, goal_id, section_label }`.
- `POST /api/goals/{goal_id}/steps/{step_id}/status`
  - Request: `{ "status": "pending" | "in_progress" | "done" }`
  - Response: `{ "step": { id, goal_id, step_index, description, status, ... } }`
- `POST /api/goals/{goal_id}/steps/{step_id}/detail`
  - Request: `{ "detail": "<string>", "step_index": <int> }` (empty string clears; step_index is optional fallback)
  - Response: `{ "step": { goal_id, step_id, detail } }`
- `GET /api/goals/{goal_id}`
  - `plan_steps[]` now includes optional `detail` and `detail_updated_at`.

## Manual verification checklist
- Focus a goal -> add details to a step -> Save -> refresh -> details persist.
- Toggle completion -> refresh -> status persists.
- Build plan for multiple intents -> sections append (no overwrite).
- Verify logs: API info log includes request_id, user_id, goal_id, step_id, step_index, matched flag.
