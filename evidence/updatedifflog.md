# evidence/updatedifflog.md (OVERWRITE)

Cycle Status: COMPLETE
Todo Ledger:
- Planned: Fix "local day" time-semantics inconsistencies in api.py.
- Completed: Updated `/api/today-plan` and `/api/today-brief` to default to `local_today`. Updated `_apply_proposal_core` to use `local_today` for plan loading.
- Remaining: None.
Next Action: Await user confirmation.

Root-Cause Anchors:
- `api.py:5361`: `get_today_plan` handler used implicit default.
- `api.py:5428`: `get_today_brief` handler used implicit default.
- `api.py:6167`: `_apply_proposal_core` called `get_today_plan` without explicit date.

Patch Summary:
- **Explicit Local Day:** `/api/today-plan` and `/api/today-brief` now explicitly compute `_get_local_today(user_id)` when `plan_date` is not provided, ensuring Europe/London consistency.
- **Proposal Safety:** `_apply_proposal_core` now passes `plan_date=local_today` to `get_today_plan`, preventing server-time drift during proposal application.
- **Logging:** Added info log when `today-plan` defaults to `local_today`.

Verification Results (static -> runtime -> behavioral -> contract):
- Static: `python -m py_compile api.py ...` passed.
- Runtime:
    - `GET /api/today-plan` (no date) -> Returns plan for 2026-01-03 (local today).
    - `GET /api/today-plan?plan_date=2026-01-04` -> Returns plan for 2026-01-04.
    - `GET /api/today-brief` -> Returns brief successfully.
- Behavioral: Confirmed endpoints function correctly with auth and return expected data.
- Contract: All "today" paths now use `_get_local_today(user_id)` unless plan_date is explicitly provided.

--- EOF Phase 9.5e ---
