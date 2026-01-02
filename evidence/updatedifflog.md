# Update Diff Log - Phase 3.1.2 Suggestion Correctness

## Summary
Implemented correctness fixes for the suggestion pipeline. Introduced strict read-only guards using local-day semantics, a retry-safe "applying" status for dual-write scenarios, and rigorous operation validation.

## Files Changed
- `api.py`: Added `_get_local_today`, updated `generate`/`apply`/`reject` with strict date parsing and local-day checks. Implemented 2-phase commit logic in `apply_proposal` using `applying` status. Added strict op validation.
- `othello_ui.html`: Updated `applySuggestion` and `rejectSuggestion` to handle 409 Conflict (applying status).

## Anchors

### A) Read-only Guard (Local Day)
[api.py:4658](api.py#L4658) - `def _get_local_today(user_id: str) -> date:`
[api.py:4861](api.py#L4861) - `if plan_date != local_today:` (READ_ONLY_MODE check)

### B) Retry-safe Apply (Applying Status)
[api.py:4835](api.py#L4835) - `SELECT ... FOR UPDATE` (Locking)
[api.py:4843](api.py#L4843) - `if status == "applying":` (Conflict check)
[api.py:4904](api.py#L4904) - `UPDATE suggestions SET status = 'applying'` (Mark applying)
[api.py:4962](api.py#L4962) - `UPDATE suggestions SET status = 'accepted'` (Finalize)

### C) Op Validation (Strict)
[api.py:4866](api.py#L4866) - `allowed_ops = {"set_status", "reschedule"}`
[api.py:4880](api.py#L4880) - `if not op_type or op_type not in allowed_ops:`

### D) Dedupe Race Reduction
[api.py:4761](api.py#L4761) - `SELECT ... FOR UPDATE` (Lock pending for dedupe)

### E) UI 409 Handling
[othello_ui.html:4816](othello_ui.html#L4816) - `if (res.status === 409) {` (applySuggestion)
[othello_ui.html:4846](othello_ui.html#L4846) - `if (res.status === 409) {` (rejectSuggestion)

## Verification Notes
- **Static Check**: `python -m py_compile api.py core/day_planner.py db/plan_repository.py` passed.
- **Read-only**: Verified `READ_ONLY_MODE` checks against `_get_local_today`.
- **Applying Status**: Verified `status='applying'` transition and 409 Conflict handling.
- **Validation**: Verified strict checks for op types, item existence, and status enums.
- **Environment Limitation**: Dual-write remains (DB transaction for suggestion vs separate DB calls for plan updates), but is now retry-safe via the `applying` status. If the process crashes during Phase 2, the suggestion stays `applying` (requires manual cleanup or timeout logic in future).
