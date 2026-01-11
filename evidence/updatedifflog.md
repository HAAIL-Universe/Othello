Cycle Status: IN PROGRESS

Todo Ledger:
- Planned: restore pingpong "second iteration" (baseline overlay + triple-tap exit + init hook).
- Completed: re-added `static/pingpong_mode.js` and `static/pingpong_mode.css`; reintroduced `initPingPongEasterEgg` in `static/othello.js`.
- Remaining: confirm whether to keep the existing pingpong asset includes in `othello_ui.html` (currently present).

Next Action: proceed with verification or adjust per updated direction.

Diff Summary (excluding evidence/updatedifflog.md):
- `static/pingpong_mode.js`: start/stop kit light during pingpong; slide paddles from bubble positions to play positions over 1s; add 3s countdown before spawn; spawn ball from kit light position; toggle `pp-parked-boost`; hit detection uses cloned `.bubble` bounds.
- `static/pingpong_mode.js`: clamp paddles with asymmetric padding (user: left -4px/right 16px; Othello: left 16px/right -4px).
- `static/othello.css`: hide horizontal overflow on parked duet bottom pane to prevent scroll bar.
- `static/othello.js`: auto-collapse all message bubbles on park (not just user rows).
- `static/othello.js`: mark new bot rows as `parked-exempt` when parked so they stay visible.
- `static/othello.js`: re-run focus peek logic on unpark to restore user bubble visibility when not crowded.
- `static/othello.css`: prevent parked transform for `.msg-row.parked-exempt`.
- `static/pingpong_mode.css`: halve paddle width (`min(260px, 35vw)`); move top paddle down (`top: 40px`); apply rainbow gradient/animation to countdown text; increase countdown size; add history exit text style.
- `static/othello.js`: add `initPingPongEasterEgg()` + DOMContentLoaded hook.
- `othello_ui.html`: pingpong assets already included.
- `static/othello.css`: parked translate set to 100%; boost set to 110% when `#chat-view.pp-parked-boost` is active.
