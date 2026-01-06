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
- [x] Phase 3: Global chat bubble + overlay shell.
- [x] Phase 4: Unify chat UI + context routing.
- [x] Phase 5: Dialogue selector.

Completed:
- [x] Phase 1: Identified `othello_ui.html` and `static/othello.js` as key files. Confirmed `switchView` handles tab switching and `sendMessage` uses `/api/message` with mode-based channel selection.
- [x] Phase 2: Removed Chat tab. Split Middle Tab into explicit Today and Goals tabs. Updated default mode to `today-planner`. Refactored badge logic.
- [x] Phase 3: Implemented Global Chat Overlay. Moved `#chat-view` and `#input-bar` into a floating sheet. Added FAB triggering. Updated `switchView` to toggle overlay for 'chat'. Refactored `updateFocusRibbon` to respect overlay state.
- [x] Phase 4: Unified chat UI context routing. Updated `effectiveChannelForView` to map `today-planner` -> `planner` and `goals` -> `companion`. Configured `toggleChatOverlay` to reload chat history based on the underlying view context.
- [x] Phase 5: Replaced Main Header branding logic. Implemented `<select id="chat-context-selector">` in the overlay header. Added `othelloState.manualChannelOverride`. Updated `effectiveChannelForView` to respect override. Configured Overlay to reset override on open/close for context-sensitivity.

## Next Action
Stop and commit. Cycle Complete.

## Full Unified Diff
(No changes to code yet)
