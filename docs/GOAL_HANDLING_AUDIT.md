# Goal Handling and Updating Audit

## Scope and sources
- Repo focus: goal creation/focus, plan/step storage, plan step rendering, and step updates across UI -> API -> DB.
- Trinity sources read:
  - `build_docs/othello_manifesto.md` (contract-first, DB truth, UI lens, replayable truth).
  - `build_docs/othello_blueprint.md` (Phase 1 goals + steps + completion; API surface requirements).
  - `build_docs/othello_directive.md` (non-negotiable contract-first, DB truth, no silent failure, event history).

## Trinity constraints and clauses (relevant excerpts)
- Data integrity + contract discipline:
  - Manifesto: "Contract before cleverness" and "DB is truth; JSON is not truth."
  - Directive: "Contract-first, always" and "DB is the only source of truth."
- UX/interaction expectations:
  - Blueprint Phase 1: "Step tick-off, goal completion, goal history."
  - Directive: UI renders read models; no silent failure.
- Persistence/auditability:
  - Manifesto: "Truth is replayable" and "Everything is explainable."
  - Directive: "Maintain goal_events append-only. Do not try to explain history by overwriting rows."
- Minimal diffs / contracts:
  - Directive: "Every change must declare what contract/endpoint is affected; no silent contract drift."

## Current end-to-end flow (UI -> API -> manager -> repo -> schema)

### UI state + focus handling
- State: `othelloState.activeGoalId`, `othelloState.currentDetailGoalId`, `othelloState.currentView`, `othelloState.currentMode` in `othello_ui.html`.
- Focus logic: `setActiveGoal` updates `activeGoalId`, updates ribbon, and updates focus view; `hideGoalDetail` clears `currentDetailGoalId` in `othello_ui.html`.

### Goal detail rendering + plan steps
- `renderGoalDetail` in `othello_ui.html` renders plan steps when `goal.plan_steps` exists; otherwise falls back to `goal.plan` string.
- Steps grouped by section labels parsed from encoded descriptions (see manager decode below).
- Activity log buttons "Add to Current Plan" and intent "Build plan" are rendered in the goal detail view.

### Click delegation for plan buttons
- Activity log: `.plan-from-activity-btn` on Othello messages calls `postPlanFromText` in `othello_ui.html`.
- Intent list: `.intent-plan-btn` calls `postPlanFromIntent` in `othello_ui.html`.
- Both are delegated from the `#detail-content` container.

### API payload keys and routing (handle_message)
- Payload keys used from UI: `goal_id`, `active_goal_id`, `ui_action`, `current_mode`, `current_view`, `plan_text`.
- `api.py` `handle_message` branches:
  - `ui_action == "plan_from_text"`: parses steps -> `save_goal_plan`.
  - `ui_action == "plan_from_intent"`: LLM plan -> `save_goal_plan_section`.

### GoalManager / DbGoalManager
- `DbGoalManager.save_goal_plan` in `db/db_goal_manager.py`:
  - Calls `goals_repository.delete_plan_steps_for_goal` then inserts new steps.
- `DbGoalManager.save_goal_plan_section`:
  - Deletes by section prefix only, appends steps with incremented index.
- `DbGoalManager.get_goal_with_plan`:
  - Loads plan steps, decodes section prefix with `_decode_plan_step_description`.

### Repository functions
- `goals_repository.create_plan_steps`, `delete_plan_steps_for_goal`,
  `delete_plan_steps_for_goal_section`, `get_max_plan_step_index` in `db/goals_repository.py`.

### Schema (plan_steps)
- `db/schema.sql` `plan_steps` columns:
  - `id` (PK), `goal_id` (FK), `step_index` (unique per goal),
  - `description`, `status`, `due_date`, `created_at`, `updated_at`.

## Overwrite root cause (confirmed)
- "Add to Current Plan" uses `ui_action=plan_from_text` via `postPlanFromText` in `othello_ui.html`.
- `api.py` handles `plan_from_text` by calling `DbGoalManager.save_goal_plan`.
- `DbGoalManager.save_goal_plan` calls `goals_repository.delete_plan_steps_for_goal`, which deletes all steps for the goal.
- Result: each "Add to Current Plan" action wipes existing steps.

## Trinity alignment comparison (current behavior)
- Alignments:
  - Plan steps are stored in Postgres `plan_steps` (DB truth) and returned via `get_goal_with_plan`.
  - UI renders read model from `/api/goals/{id}`.
- Misalignments / gaps:
  - "Add to Current Plan" causes silent data loss by deleting all existing steps (violates contract-first + replayable truth).
  - UI lacks step completion toggle (Blueprint Phase 1 expects step tick-off).
  - Step detail is not persistable; no auditable elaboration path (Manifesto replayable truth).

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
4) Plan display efficiency:
   - Plan steps rendered in compact rows with checkbox + truncated label.
   - Details collapsed by default, expanded on demand.

## API contract addendum (new/updated)
- `POST /api/message` with `ui_action=plan_from_text_append`
  - Request body keys: `plan_text`, `goal_id`, `active_goal_id`, `current_mode`, `current_view`.
  - Response: `{ reply, meta: { intent: "plan_steps_added" }, goal_id, section_label }`.
- `POST /api/goals/{goal_id}/steps/{step_id}/status`
  - Request: `{ "status": "pending" | "in_progress" | "done" }`
  - Response: `{ "step": { id, goal_id, step_index, description, status, ... } }`
- `POST /api/goals/{goal_id}/steps/{step_id}/detail`
  - Request: `{ "detail": "<string>" }` (empty string clears)
  - Response: `{ "step": { goal_id, step_id, detail } }`
- `GET /api/goals/{goal_id}`
  - `plan_steps[]` now includes optional `detail` and `detail_updated_at`.
