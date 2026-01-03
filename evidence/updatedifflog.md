# Phase 9.4e: Routine Planner Optimistic UI Sync

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Gather Evidence
- [x] Apply Fixes (Optimistic updates for Create/Delete/Duplicate)
- [x] Static Verification
- [x] Update Log

## Root Cause Anchors
- `othello_ui.html:addStepInline`: Currently awaits `fetchRoutines` before updating UI, causing lag.
- `othello_ui.html:deleteRoutine`: Awaits `loadRoutinePlanner` (fetch) before updating UI.
- `othello_ui.html:duplicateRoutine`: Awaits `fetchRoutines` before selecting new routine.

## Planned Changes
1. **addStepInline**: Parse response, push step to `othelloState.routines`, call `renderRoutineEditor`, then reconcile.
2. **deleteRoutine**: Filter out routine from `othelloState.routines`, update selection/UI, then reconcile.
3. **duplicateRoutine**: Push new routine to `othelloState.routines`, update UI, then reconcile.
4. **Defensive Rendering**: Ensure `renderRoutineEditor` handles null steps.

## Evidence

### 1) Anchor: Optimistic Step Create
```javascript
          // Optimistic update
          const routine = othelloState.routines.find(r => r.id === routineId);
          if (routine && data.step) {
              if (!routine.steps) routine.steps = [];
              routine.steps.push(data.step);
              renderRoutineEditor(routine);
          }
```

### 2) Anchor: Optimistic Delete
```javascript
          // Optimistic remove
          const wasActive = (othelloState.activeRoutineId === id);
          othelloState.routines = othelloState.routines.filter(r => r.id !== id);
          if (wasActive) { ... select next ... }
          renderRoutineList(othelloState.routines);
```

### 3) Anchor: Optimistic Duplicate
```javascript
        // Optimistic insert (without steps initially)
        othelloState.routines.push(newRoutine);
        renderRoutineList(othelloState.routines);
```

## Next Action
- Verify fix in live environment.
