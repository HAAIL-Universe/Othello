# Phase 9.4f: Routine Planner Crash Fix & Optimistic Sync

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Gather Evidence
- [x] Apply Fixes (Crash fix, Optimistic addStepInline)
- [x] Static Verification
- [x] Update Log

## Root Cause Anchors
- `othello_ui.html:7910`: `document.getElementById("routine-add-step-btn").parentNode` throws if button is missing (which happens after first render).
- `othello_ui.html:addStepInline`: Needs optimistic update pattern.

## Planned Changes
1.  **Static HTML**: Add `id="routine-steps-header"` to the steps header container.
2.  **renderRoutineEditor**: Use `getElementById("routine-steps-header")` instead of fragile parent lookup. Ensure "Add Step" button is re-created with ID or handled correctly.
3.  **addStepInline**: Implement optimistic update and safe render sequence.

## Evidence

### 1) Anchor: Safe Header Lookup
```javascript
      // Steps Header
      const stepsHeader = document.getElementById("routine-steps-header");
      if (stepsHeader) {
          stepsHeader.innerHTML = "";
          // ...
          // Add Step Button (Header)
          const addStepBtn = document.createElement("button");
          addStepBtn.id = "routine-add-step-btn"; // Ensure ID is present for fallback
```

### 2) Anchor: Optimistic Step Create
```javascript
          // Optimistic update
          const routine = othelloState.routines.find(r => r.id === routineId);
          if (routine && data.step) {
              // ... push step ...
              selectRoutine(routineId, true);
          }
```

## Next Action
- Verify fix in live environment.
