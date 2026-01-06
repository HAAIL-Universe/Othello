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
- [ ] Phase 2: Navigation restructure (Planner-first home, remove Chat tab).
- [ ] Phase 3: Global chat bubble + overlay shell.
- [ ] Phase 4: Unify chat UI + context routing.
- [ ] Phase 5: Dialogue selector.

Completed:
- [x] Phase 1: Identified `othello_ui.html` and `static/othello.js` as key files. Confirmed `switchView` handles tab switching and `sendMessage` uses `/api/message` with mode-based channel selection.

## Next Action
Stop and commit Phase 1.

## Full Unified Diff
(No changes to code yet)
