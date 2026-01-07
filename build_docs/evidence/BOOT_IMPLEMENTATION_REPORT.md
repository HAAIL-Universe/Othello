# Othello Boot Sequence Fix Implementation Report

## Summary
This update fixes the issue where the waking overlay remains indefinitely even after the server is reachable, and ensures downstream boot failures (auth/data/planner) are surfaced as in-app errors, not as "still waking". Boot instrumentation is added for easier debugging.

## Files Modified
- `othello_ui.html`

## Root Cause
- The UI only cleared the waking overlay after all downstream boot steps (including planner load) succeeded, so any failure in those steps kept the overlay visible, misleading users into thinking the server was still waking.
- No detailed boot instrumentation was present, making debugging difficult.

## Fix (Boot State Machine Changes)
- **Health Poll URL**: Confirmed to use only relative, same-origin paths (`/api/health/db`). No hardcoded localhost/127.0.0.1/BASE_URL in production path.
- **BOOT_DEBUG Instrumentation**: Added a `BOOT_DEBUG` flag (enable with `?bootdebug=1`) to log all boot step transitions, health responses, and errors.
- **Readiness Condition**: Now only considers the server ready if `response.ok === true` and `data.status === "ok"`. JSON parse errors are handled and logged.
- **Timeout/AbortController**: Health poll uses a 4s timeout and aborts if the server is unresponsive.
- **Single Poll Loop**: Prevents duplicate health poll loops from running.
- **Overlay Decoupling**: Overlay is hidden immediately after the server is reachable, regardless of downstream planner/auth/data errors.
- **Planner Error Handling**: If planner endpoints fail, an in-app error banner is shown with HTTP code and a Retry button (which only retries planner load). The overlay stays hidden.

## How to Verify on Render
1. Deploy the changes.
2. Open DevTools > Network tab. Observe `/api/health/db` is polled with a relative path.
3. Add `?bootdebug=1` to the URL to see detailed boot logs in the console.
4. Simulate a planner endpoint failure (e.g., break `/api/today-plan`). The overlay should clear as soon as `/api/health/db` returns `{status: "ok"}`. Any planner error should show as a banner with a Retry button, not as "Waking server...".
5. Retry button should only retry planner load, not the full boot.

---

For further debugging, use `?bootdebug=1` in the URL to see all boot state transitions and error payloads in the browser console.
