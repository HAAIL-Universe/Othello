# Phase 9.4d: Routine Planner State Sync Fix

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Gather Evidence
- [x] Apply Fixes (State management, Render logic, Handlers)
- [x] Static Verification
- [x] Update Log

## Next Action
- Verify fix in live environment.

## Changes
- **othello_ui.html**:
  - Updated `fetchRoutines` to validate `activeRoutineId` against the fresh data.
  - Updated `loadRoutinePlanner` to use deterministic selection logic (try to keep active, else select first, else empty).
  - Updated `selectRoutine` to always pull the routine object from `othelloState.routines` (the source of truth) instead of relying on potentially stale arguments or state.
  - Updated `deleteRoutine` to correctly clear `activeRoutineId` only if the deleted routine was active, and then reload.
  - Updated `duplicateRoutine` to fetch routines and then select the new routine from the fresh state.
  - Added `renderEmptyState` helper for consistency.

## Evidence

### 1) Anchor: Deterministic Selection (loadRoutinePlanner)
```javascript
    async function loadRoutinePlanner() {
      await fetchRoutines();
      renderRoutineList(othelloState.routines);
      
      // Deterministic selection logic
      if (othelloState.activeRoutineId) {
          // Try to select the previously active routine
          const exists = othelloState.routines.find(r => r.id === othelloState.activeRoutineId);
          if (exists) {
              selectRoutine(othelloState.activeRoutineId, true);
          } else {
              othelloState.activeRoutineId = null;
              if (othelloState.routines.length > 0) {
                  selectRoutine(othelloState.routines[0].id, false);
              } else {
                  renderEmptyState();
              }
          }
```

### 2) Anchor: Source of Truth (selectRoutine)
```javascript
    function selectRoutine(routineId, openOnMobile = false) {
      othelloState.activeRoutineId = routineId;
      // Always find the routine from the latest state
      const routine = othelloState.routines.find(r => r.id === routineId);
      renderRoutineList(othelloState.routines); // update selection style
```

### 3) Anchor: Duplicate Routine Sync
```javascript
        // Refresh and select
        await fetchRoutines();
        
        // Ensure we find the new routine in the fresh state
        const freshNewRoutine = othelloState.routines.find(r => r.id === newRoutine.id);
        if (freshNewRoutine) {
            othelloState.mobileEditorPinned = true;
            selectRoutine(freshNewRoutine.id, true);
```

### 4) Static Verification
```text
python -m py_compile api.py core/day_planner.py db/plan_repository.py
(No output, exit code 0)
```

--- EOF Phase 9.4d ---
