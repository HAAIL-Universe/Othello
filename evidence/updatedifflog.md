# Update Diff Log - Phase 3.1.1 Suggestion Hardening

## Summary
Hardened the confirm-gated suggestion pipeline to ensure safety, determinism, and idempotency. Added server-side read-only guards, transactional application logic, operation validation, and proposal deduplication.

## Files Changed
- `api.py`: Added `get_connection` usage for transactions, `hashlib` for dedupe, and validation logic in `generate`/`apply`/`reject`.
- `othello_ui.html`: Updated `applySuggestion` to handle "Already decided" responses gracefully.

## Anchors

### A) Server-side Read-only Guard
In `generate_proposals`, `apply_proposal`, and `reject_proposal`:
```python
    # 1. Read-only Guard
    if plan_date != date.today():
        return api_error("READ_ONLY_MODE", "Cannot generate proposals for past/future dates", 403)
```

### B) Transactional Apply & Idempotency
In `apply_proposal`:
```python
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                # 1. Lock & Check
                cursor.execute(
                    "SELECT id, status, payload FROM suggestions WHERE id = %s AND user_id = %s FOR UPDATE",
                    (proposal_id, user_id)
                )
                # ...
                if status != "pending":
                    return jsonify({"ok": True, "status": status, "message": "Already decided"})
                
                # ... validation ...
                # ... apply ops (external commits) ...
                
                # 5. Mark Accepted
                cursor.execute("UPDATE suggestions SET status = 'accepted' ...")
                conn.commit()
        except Exception as e:
            conn.rollback()
            # ...
```

### C) Op Allowlist & Validation
```python
                allowed_ops = {"set_status", "reschedule"}
                # ...
                for op in ops:
                    if op.get("op") not in allowed_ops:
                        return api_error("INVALID_OP", ...)
                    if op.get("item_id") not in plan_item_ids:
                        return api_error("INVALID_OP", ...)
```

### D) Deduplication
In `generate_proposals`:
```python
    def _compute_hash(p_payload):
        canonical = {"plan_date": ..., "ops": ...}
        s = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    # ... check against existing hashes ...
    if p_hash in existing_hashes:
        continue
```

## Verification Notes
- **Static Check**: `python -m py_compile api.py core/day_planner.py db/plan_repository.py` passed.
- **Transaction**: Verified `FOR UPDATE` lock usage in `apply_proposal` and `reject_proposal`.
- **Read-only**: Verified `READ_ONLY_MODE` checks in all 3 endpoints.
- **Validation**: Verified allowlist checks for `set_status` and `reschedule`.
- **Environment Limitation**: Plan updates (via `day_planner`) commit independently of the suggestion transaction. This is a known dual-write risk accepted under "No refactors" constraint, mitigated by rolling back the suggestion status if plan update fails.
