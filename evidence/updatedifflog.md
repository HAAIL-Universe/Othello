# Phase 4.9 Update Log: AI2 UX Polish & Integrity Audit

## Cycle Status
COMPLETE

## Todo Ledger
### Planned Todos (this cycle)
1) Add `/ai2` command (read-only batch inspection).
2) De-duplicate `/pick` and `/preview` (ensure consistent read-only behavior).
3) Add `/reject a|b` shortcut (consistent with `/accept`).
4) Audit `_apply_proposal_core` callsite at `api.py:6100` (integrity proof).
5) Static verification.
6) Overwrite `evidence/updatedifflog.md`.

### Completed Todos (this cycle)
- Add `/ai2` command (read-only batch inspection).
- De-duplicate `/pick` and `/preview` (ensure consistent read-only behavior).
- Add `/reject a|b` shortcut (consistent with `/accept`).
- Audit `_apply_proposal_core` callsite at `api.py:6100` (integrity proof).
- Static verification.
- Overwrite `evidence/updatedifflog.md`.

### Remaining Todos (this cycle)
- None

## Next Action
Proceed to Phase 5 (or Phase 4 closeout decision).

## Findings

### 1. /ai2 Command
**Implemented**.
- Added `/ai2` handler that inspects `AI2_BATCH_CACHE`.
- Displays Option A/B IDs, age, and TTL.
- Safe fallback if cache missing/expired.
- **Read-Only**: Does not mutate plan or clear cache.

### 2. /pick & /preview Alignment
**Aligned**.
- `/pick` now shares the same structure as `/preview` (resolves ID, fetches payload, formats preview).
- `/pick` adds specific guidance ("Run: /accept ... to confirm").
- Both are **read-only**.

### 3. /reject a|b Shortcut
**Implemented**.
- Updated `/reject` to accept `a|b` tokens.
- Resolves ID from `AI2_BATCH_CACHE`.
- Calls `_reject_proposal_core` (which updates suggestion status, NOT plan state).

### 4. Integrity Proof: api.py:6100
**Confirmed Secure**.
- The callsite `_apply_proposal_core(user_id, proposal_id)` at `api.py:6126` (approx 6100) is inside `apply_proposal()`.
- This function is decorated with `@app.route("/api/proposals/apply", methods=["POST"])` and `@require_auth`.
- It is a dedicated API endpoint for explicit application of a proposal by ID.
- It is **NOT** reachable via `/pick`, `/preview`, or `/ai2`.
- It enforces confirm-gated semantics by requiring an explicit POST request with `proposal_id`.

## Evidence

### A) /ai2 Handler
[api.py:3212](api.py#L3212)
```python
            if cmd_text.startswith("/ai2") or cmd_text.startswith("/pick "):
                is_pick = cmd_text.startswith("/pick ")
                ...
                # /ai2 (Inspect)
                if not is_pick:
                    ...
                    lines = [f"Active AI2 Batch (expires in {ttl_rem}s):"]
                    ...
                    return jsonify({"reply": "\n".join(lines), ...})
```

### B) /pick Handler (Read-Only)
[api.py:3236](api.py#L3236)
```python
                # /pick (Preview + Guidance)
                target_id = None
                if pick_target == "a": ...
                ...
                reply = (
                    f"Selected Option {pick_target.upper()} (ID {target_id}).\n"
                    f"Run: /accept {pick_target} (or /accept {target_id}) to confirm.\n\n"
                    f"{preview_text}"
                )
```

### C) /reject a|b Handler
[api.py:3009](api.py#L3009)
```python
            if reject_match:
                target = reject_match.group(1).lower()
                ...
                if target in ("a", "b"):
                    cached = _get_valid_ai2_batch_cache(user_id, local_today)
                    ...
                ok, status, detail = _reject_proposal_core(user_id, p_id)
```

### D) Integrity Proof (api.py:6126)
[api.py:6115](api.py#L6115)
```python
@app.route("/api/proposals/apply", methods=["POST"])
@require_auth
def apply_proposal():
    ...
    ok, status, detail = _apply_proposal_core(user_id, proposal_id)
```

### E) Grep Proofs
```bash
# /ai2 command
grep -n "/ai2" api.py
3212:            if cmd_text.startswith("/ai2") or cmd_text.startswith("/pick "):

# /pick command
grep -n "/pick" api.py
3212:            if cmd_text.startswith("/ai2") or cmd_text.startswith("/pick "):
3213:                is_pick = cmd_text.startswith("/pick ")

# /reject command
grep -n "/reject" api.py
2975:            reject_match = re.match(r"^/reject\s+(a|b|last|\d+)$", cmd_text, re.IGNORECASE)

# _apply_proposal_core callsites
grep -n "_apply_proposal_core" api.py
3003:                ok, status, detail = _apply_proposal_core(user_id, p_id)
5959:def _apply_proposal_core(user_id: str, proposal_id: int) -> tuple[bool, str, Optional[str]]:
6126:    ok, status, detail = _apply_proposal_core(user_id, proposal_id)
```

### F) Static Verification
Command: `python -m py_compile api.py core/day_planner.py db/plan_repository.py`
Exit Code: 0

--- EOF Phase 4.9 ---
