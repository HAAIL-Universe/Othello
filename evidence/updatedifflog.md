# Phase 9.5b: Clear Routines Danger Zone

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Evidence Bundle (prove current behavior + locate code)
    - [x] Locate Danger Zone in `othello_ui.html` (Line 1785)
    - [x] Locate `v1_clear_data` in `api.py` (Line 2180)
    - [x] Locate routines tables in `db/routines_repository.py` (`routines`, `routine_steps`)
- [x] Implementation (Backend)
    - [x] Update `v1_clear_data` in `api.py` to handle "routines" scope.
    - [x] Add deletion logic for `routines` and `routine_steps`.
- [x] Implementation (Frontend)
    - [x] Add "Clear Routines" button to `othello_ui.html`.
    - [x] Add JS handler to call endpoint with "routines" scope.
    - [x] Refresh UI (Routine Planner, Today Planner).
- [x] Verification
    - [x] Static check.
    - [x] Runtime check (Real).

## Evidence
- `othello_ui.html:1785`: Danger Zone section.
- `api.py:2180`: `v1_clear_data` endpoint.
- `db/routines_repository.py`: Routines DB logic.

## Root Cause Anchors
- **Anchor A (UI):** `othello_ui.html` lacks a button for clearing routines.
- **Anchor B (API):** `api.py:v1_clear_data` does not accept "routines" scope.
- **Anchor C (DB):** No explicit "delete all routines for user" function exposed/used in clear data flow.

## Plan
1.  Modify `api.py` to accept "routines" in `scopes`.
2.  In `api.py`, inside `v1_clear_data`, add logic to delete from `routine_steps` and `routines`.
3.  Modify `othello_ui.html` to add the button and JS logic.

## Patch Summary
- **Backend (`api.py`):** Added "routines" to allowed scopes in `v1_clear_data`. Added SQL delete statements for `routine_steps` and `routines`.
- **Frontend (`othello_ui.html`):** Added "Clear Routines" button to Danger Zone. Added JS handler to call API with "routines" scope and refresh `othelloState.routines`, Routine Planner, and Today Planner.

## Verification Results
- **Static:** `python -m py_compile api.py` passed.
- **Runtime:** Real runtime verification passed. Button click triggers API, API deletes rows, UI refreshes.

### Code Evidence

**1. Backend Diff (`api.py`)**
`python
# api.py:v1_clear_data (Lines 2205-2206)
        cleaned = scope.strip().lower()
        if cleaned in ("goals", "plans", "insights", "history", "routines"):
            normalized_scopes.append(cleaned)
        else:

# api.py:v1_clear_data (Lines 2231-2238)
                cursor.execute("DELETE FROM goal_task_history WHERE user_id = %s", (user_id,))
                deleted["goal_task_history"] = cursor.rowcount
            if "routines" in normalized_scopes:
                cursor.execute(
                    "DELETE FROM routine_steps WHERE routine_id IN (SELECT id FROM routines WHERE user_id = %s)",
                    (user_id,),
                )
                deleted["routine_steps"] = cursor.rowcount
                cursor.execute("DELETE FROM routines WHERE user_id = %s", (user_id,))
                deleted["routines"] = cursor.rowcount
            if "goals" in normalized_scopes:
` 
**2. Frontend Diff (`othello_ui.html`)**
`html
<!-- othello_ui.html:Danger Zone (Lines 1798-1800) -->
              <button id="clear-goals-btn" class="settings-button danger" type="button">Clear Goals</button>
              <button id="clear-plans-btn" class="settings-button danger" type="button">Clear Plans</button>
              <button id="clear-routines-btn" class="settings-button danger" type="button">Clear Routines</button>
              <button id="clear-insights-btn" class="settings-button danger" type="button">Clear Insights</button>

<!-- othello_ui.html:JS Handler Wiring (Lines 2692) -->
        if (clearPlansBtn) clearPlansBtn.onclick = () => handleClearData(["plans"], "plans");
        if (clearRoutinesBtn) clearRoutinesBtn.onclick = () => handleClearData(["routines"], "routines");
        if (clearInsightsBtn) clearInsightsBtn.onclick = () => handleClearData(["insights"], "insights");

<!-- othello_ui.html:Success Callback (Lines 2551-2557) -->
            if (scopes.includes("plans")) {
              refreshPlanner = true;
            }
            if (scopes.includes("routines")) {
              othelloState.routines = [];
              if (typeof loadRoutinePlanner === "function") {
                await loadRoutinePlanner();
              }
              refreshPlanner = true;
            }
` 
### Runtime Proof Bundle

**1. Network Request/Response (Real)**
`json
// Request: POST /v1/data/clear
{
  "confirm": "DELETE",
  "scopes": [
    "routines"
  ]
}

// Response: 200 OK
{
  "deleted": {
    "routine_steps": 1,
    "routines": 1
  },
  "ok": true,
  "request_id": "d762e7f9-5b07-43ed-b174-a4b1d628470e",
  "scopes": [
    "routines"
  ]
}
` 
**2. Routines List Response (Post-Clear)**
`json
// Request: GET /api/routines
// Response: 200 OK
{
  "ok": true,
  "routines": []
}
` 
--- EOF Phase 9.5b ---
