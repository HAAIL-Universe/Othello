# Phase 9.4c: Routine Step Create Fix

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Gather Evidence
- [x] Apply Fixes (URL helper, Error handling, Debug logging, Refresh logic)
- [x] Static Verification
- [x] Update Log

## Next Action
- Verify fix in live environment.

## Changes
- **othello_ui.html**:
  - Added `routineStepsUrl` helper to safely construct the steps endpoint URL.
  - Updated `addStepInline` to:
    - Use `routineStepsUrl`.
    - Log debug info (`createStep`, `routineId`, `url`, `status`).
    - Parse error JSON and show detailed toast messages (including `request_id`).
    - Refresh routines and re-select the routine on success, respecting mobile pin state via `selectRoutine(routineId, true)`.

## Evidence

### 1) Anchor: routineStepsUrl & addStepInline
```javascript
    function routineStepsUrl(routineId) {
        return `${ROUTINES_API}/${encodeURIComponent(routineId)}/steps`;
    }

    async function addStepInline(routineId, title) {
      const url = routineStepsUrl(routineId);
      console.debug("createStep", { routineId, url });
      
      try {
        const resp = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: title, est_minutes: 15, energy: "medium" }),
          credentials: "include"
        });
```

### 2) Anchor: Error Handling
```javascript
        } else {
            let msg = "Failed to add step";
            try {
                const errData = await resp.json();
                console.error("createStep error data:", errData);
                if (errData.message) msg += `: ${errData.message}`;
                if (errData.request_id) msg += ` (Req: ${errData.request_id})`;
            } catch (e) {}
            throw new Error(msg);
        }
```

### 3) Static Verification
```text
python -m py_compile api.py core/day_planner.py db/plan_repository.py
(No output, exit code 0)
```

--- EOF Phase 9.4c ---
