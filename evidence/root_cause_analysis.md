# Phase 1: Root Cause Anchoring

## Frontend (static/othello.js)
- **Routine Card Logic**: `buildRoutineReadyPanel` is called when `meta.intent === "routine_ready"`.
- **Focus State**: `othelloState.activeGoalId` tracks the focused goal.
- **Message Rendering**: `addMessage` creates the DOM elements. It adds `.msg-row` and `.bubble`.
- **API Call**: `sendMessage` sends `active_goal_id` (and `goal_id`) to `/api/message`.

## Backend (api.py)
- **Routine Trigger**: `routine_ready` is set in two places:
    1.  Pending suggestion completion (lines 4700+).
    2.  New extraction via `ConversationParser` (lines 4746+).
- **Focus Context**: The `chat` endpoint receives `active_goal_id` (or `goal_id`) in the JSON payload.

## CSS (static/othello.css)
- **Message Styles**: `.msg-row.user .bubble` and `.msg-row.bot .bubble` define the look.

## Root Cause
- **Issue A (Highlighting)**: No CSS class is applied to messages when a goal is focused.
- **Issue B (Routine Trigger)**: `api.py` checks for pending routine suggestions and runs the parser *regardless* of whether a goal is focused. The parser fix handled negative intent, but `api.py` still needs to be aware of "goal focus" to suppress routine suggestions unless explicitly requested.

## Plan
1.  **Backend Fix**: In `api.py`, wrap the routine logic. If `active_goal_id` is present, ONLY allow routine logic if the user input explicitly asks for it (positive intent).
2.  **Frontend Fix**: In `othello.js`, update `addMessage` to check `othelloState.activeGoalId` and add `.msg--focus-attached`.
3.  **CSS Fix**: Add `.msg--focus-attached .bubble` styles to `othello.css`.
