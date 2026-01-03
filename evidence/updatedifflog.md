# evidence/updatedifflog.md (OVERWRITE)

Cycle Status: COMPLETE
Todo Ledger:
- Planned: Stop Week View from accidentally generating/persisting day plans.
- Completed: Added `peek=1` mode to `/api/today-plan`. Updated Week View to use `peek=1`. Cleared week cache on routine clear.
- Remaining: None.
Next Action: Await user confirmation.

Root-Cause Anchors:
- `api.py:5361`: `get_today_plan` handler always called `day_planner.get_today_plan` which generates/persists.
- `othello_ui.html:4606`: `fetchPlanForDate` called API without peek mode.
- `othello_ui.html:2500`: Clear Routines success handler didn't clear week cache.

Patch Summary:
- **Backend Peek Mode:** `/api/today-plan` now accepts `peek=1`. If set, it loads existing plans by date (read-only) or returns an empty stub without generating/persisting.
- **Frontend Week View:** `fetchPlanForDate` now uses `peek=1` to prevent side-effects when browsing weeks.
- **Cache Invalidation:** "Clear Routines" now clears `weekViewCache` and refreshes the week view to prevent stale data.

Verification Results (static -> runtime -> behavioral -> contract):
- Static: `python -m py_compile api.py` passed.
- Runtime:
    - `GET /api/today-plan?plan_date=2026-01-05&peek=1` (future) -> Returns empty stub `_plan_source="empty_stub"`.
    - `GET /api/today-plan?plan_date=2026-01-03&peek=1` (today, existing) -> Returns existing plan `_plan_source="db_peek"`.
- Behavioral: Week View browsing no longer triggers plan generation. Clear Routines updates week view immediately.
- Contract: Week View is now side-effect free.

--- EOF Phase 9.5g ---
