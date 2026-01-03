# evidence/updatedifflog.md (OVERWRITE)

Cycle Status: COMPLETE
Todo Ledger:
- Planned: Tighten "Clear Routines" scope to protect history and user items.
- Completed: Implemented date-scoped deletion (today+) and strict type checking.
- Remaining: None.
Next Action: Await user confirmation.

Root-Cause Anchors:
- `api.py:2245`: `v1_clear_data` routine deletion logic.
Patch Summary:
- **Scope Tightening:** Added `plan_date >= local_today` constraint to `plan_items` deletion.
- **Predicate Tightening:** Removed `section='routines'` (unsafe). Added `type='routine_step'`.
- **Logic:** `DELETE FROM plan_items WHERE (type='routine' OR type='routine_step' OR source_kind='routine') AND plan_id IN (plans WHERE date >= local_today)`.
- **Backfill:** Added backfill logic to tag legacy routine items with `source_kind='routine'` before deletion.
- **Writer Paths:** Updated `core/day_planner.py` to ensure `source_kind='routine'` is set on creation.

Verification Results (static -> runtime -> behavioral -> contract):
- Static: `python -m py_compile api.py` (Implicitly checked via script execution).
- Runtime: `verify_safety_tightening_v2.py` executed successfully against DB.
- Behavioral: Confirmed that "Clear Routines" removes today's routine items but leaves user tasks in the same section alone.
- Contract:
    - **Historical Preservation:** Yesterday's routine items were NOT deleted.
    - **User Data Safety:** User-authored task in "routines" section was NOT deleted.
    - **Future Cleanup:** Tomorrow's routine items WERE deleted.
    - **Backfill:** Legacy routine items were correctly backfilled and deleted.

--- EOF Phase 9.5d ---
