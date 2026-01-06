# Cycle Status: IN_PROGRESS (UX Re-architecture)

## Scope + Constraints
- **Docs Found**: `contracts/EXECUTOR_CONTRACT.md`, `othello_ui.html`, `static/othello.js`.
- **Constraints**: 
    - No changes to `/api/message` endpoint contract.
    - No DB schema modifications.
    - Preserving `goal-intent` "?" marker logic and "create goal from message" flow.
    - Minimal diff, targeting `othello_ui.html`, `static/othello.js`, and `static/othello.css`.

## Todo Ledger
Planned:
- [x] Phase 1: Discover + Anchor (Identify UI entry points and message pipelines).
- [x] Phase 2: Navigation restructure (Planner-first home, remove Chat tab).
- [ ] Phase 3: Global chat bubble + overlay shell.
- [ ] Phase 4: Unify chat UI + context routing.
- [ ] Phase 5: Dialogue selector.

Completed:
- [x] Phase 1: Identified `othello_ui.html` and `static/othello.js` as key files. Confirmed `switchView` handles tab switching and `sendMessage` uses `/api/message` with mode-based channel selection.
- [x] Phase 2: Removed "Chat" tab from `othello_ui.html`. Updated `othello.js` default state to `today-planner`, changed `loadMode` default to `today`, and updated `setMode` fallback to prefer Planner/Goals over Chat.

## Next Action
Start Phase 3: Global chat bubble + overlay shell.

## Full Unified Diff
(Diffs included in git commits)
