# Phase 9.5: Today Planner Integration

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Gather Evidence
- [x] Apply Fixes (Backend: routines_for_today, Frontend: render routines)
- [x] Static Verification
- [x] Update Log

## Root Cause Anchors
- `api.py:get_today_plan`: Calls `day_planner.get_today_plan`.
- `core/day_planner.py:get_today_plan`: Calls `self.routines` which loads from JSON or DB.
- `core/day_planner.py:260`: `source_routines` logic in `_generate_plan` (or similar) filters by day tag.
- `othello_ui.html:renderPlannerSections`: Renders `plan.sections.routines`.

## Planned Changes
1.  **Backend (`core/day_planner.py`)**:
    *   Modify `get_today_plan` (or `_generate_plan`) to ensure it fetches *fresh* enabled routines from `routines_repository` if in DB-only mode, filtering by today's day tag.
    *   Currently `_generate_plan` (lines 250+) seems to have logic for this (`if _PHASE1_DB_ONLY`). I need to verify if `get_today_plan` calls `_generate_plan` correctly or if it relies on cached plans that might be stale.
    *   The issue might be that `get_today_plan` loads from cache/DB plan row first. If a new routine is added, the existing plan row won't have it.
    *   I will add logic to `get_today_plan` to *merge* missing routines into the plan if they are enabled and scheduled for today.

2.  **Frontend (`othello_ui.html`)**:
    *   `renderPlannerSections` already renders `plan.sections.routines`. If the backend sends them, they should appear.
    *   I will verify if `routines_for_today` is needed or if I can just inject them into `sections.routines`. The user request mentions `routines_for_today`, but `renderPlannerSections` uses `sections.routines`. I'll stick to `sections.routines` to minimize frontend changes if possible, or map `routines_for_today` to it.

## Evidence
- `core/day_planner.py:263`: `if _PHASE1_DB_ONLY:` block fetches from `routines_repository`.
- `core/day_planner.py:508`: `if not plan:` block generates new plan. If plan exists, it returns it. This is why new routines don't show up—the plan is cached.

## Next Action
- Verify fix in live environment.
