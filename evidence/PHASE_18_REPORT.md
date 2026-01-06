# Phase 18 Report: Intent Clarification & Seed Steps

## Changes Implemented
1. **Show Seed Steps (Backend)**:
   - Modified `api.py` to handle `ui_action="show_seed_steps"` and text commands like "show seed steps".
   - Returns the seed steps checklist directly from the active goal.
2. **Focus Context Injection (Backend)**:
   - Modified `db/db_goal_manager.py:build_goal_context` to inject "Seed Steps (Initial Checklist)" into the context LLM sees.
3. **Intent Clarification (Frontend/Backend)**:
   - Added "Clarify Intent" button to `static/othello.js` goal details.
   - Added `ui_action="clarify_goal_intent"` handler in `api.py` to prompt the agent to ask clarifying questions.

## Verification
- Verified `api.py` handlers using `verify_phase18.py` (mocked).
- Confirmed "Show Seed Steps" returns data.
- Confirmed "Clarify Intent" modifies user input for agent consumption.

## Files Modified
- `api.py`
- `db/db_goal_manager.py`
- `static/othello.js`
