# Phase 9.5a: Today Planner Fixes

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Locate suggestion acceptance endpoint (`api.py:v1_accept_suggestion` -> `_apply_suggestion_decisions`).
- [x] Locate plan item creation (`db/plan_repository.py:insert_plan_item`).
- [x] Apply Fixes:
    - [x] `api.py`: Ensure accepted routine suggestions have status "planned".
    - [x] `core/day_planner.py`: Add title normalization to `_merge_fresh_routines` and `_flatten_plan_items`.
    - [x] `core/day_planner.py`: Ensure `_merge_fresh_routines` is idempotent and preserves status.
- [x] Verify changes.
- [x] Update Log.

## Root Cause Anchors
- **Anchor A (Status):** `api.py:_apply_suggestion_decisions` handles `kind == "plan_item"`. It calls `insert_plan_item_from_payload`. I need to check if `payload` contains `status`. If not, `insert_plan_item` defaults to "planned". But the user says it's "In_progress". This implies the payload might have `status="in_progress"` or the UI is interpreting it wrong.
- **Anchor B (Untitled):** `db/plan_repository.py:insert_plan_item` takes `item.get("title")`. If missing, it might be null. `othello_ui.html` likely renders "Untitled plan item" if title is missing.
- **Anchor C (Merge):** `core/day_planner.py:_merge_fresh_routines` (my previous code) checks `existing_ids`. I need to verify it handles title correctly and doesn't overwrite.

## Evidence
- `api.py:1718`: `item = insert_plan_item_from_payload(...)`.
- `db/plan_repository.py:130`: `item.get("status", "planned")`. Default is planned.
- `core/day_planner.py:565`: `item = { ... "name": fr["title"] ... }`. I used `name` instead of `title` in the plan item dict in `_merge_fresh_routines`. `_flatten_plan_items` might expect `title` or `label`.

## Plan
1.  **Fix `api.py`**: Explicitly set `status="planned"` in `payload` before creating plan item from suggestion.
2.  **Fix `core/day_planner.py`**:
    - In `_merge_fresh_routines`, ensure `title` is set (I used `name` previously).
    - Add a normalization step to ensure `title` is never empty.
3.  **Verify**: Run static checks and manual verification if possible.
