Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Read governance docs; gate planner/week/routine fetches; add single poller + aborts; add BOOT_DEBUG logs; run py_compile; update updatedifflog
Completed: Read directive/blueprint/manifesto; gated planner/week/routine loads; added poller/abort guards and drilldown/panel logs; ran py_compile api.py
Remaining: Manual UI verification of view gating; commit checkpoint after verification
Next Action: Manually verify Chat/Planner/Week/Routine behavior, then git status/diff/add and commit with message "Fix: Today Planner load + confirm wiring; stabilize E2E"
diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
index 4608da02..407279b4 100644
--- a/evidence/updatedifflog.md
+++ b/evidence/updatedifflog.md
@@ -1,1588 +1,4515 @@
-Cycle Status: COMPLETE
+Cycle Status: IN_PROGRESS
 Todo Ledger:
-- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
-- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
-- Remaining: None.
-
-Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
-
-diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
-index 3fd145c5..ce3666e6 100644
---- a/evidence/e2e_run.md
-+++ b/evidence/e2e_run.md
-@@ -1,39 +1,20 @@
--Date/Time: 2026-01-03 17:35:21 +00:00
-+Date/Time: 2026-01-03 17:46:11 +00:00
- 
- Commands:
- - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
--- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
- 
- Env Vars:
- - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
- - OTHELLO_ACCESS_CODE=******69
- 
--Auth probe summary (manual):
--- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
--- /api/today-brief -> 200 {"brief":{...}}
--- /api/today-plan -> 200 {"plan":{...}}
-+Planner load instrumentation:
-+- Planner load failed banner: NOT observed in passing run
-+- fetchTodayBrief failure is now non-fatal (logs only)
- 
--Result: FAIL
-+Confirm endpoint:
-+- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})
- 
--Failure (attempt #1):
--- Error: Planner load failed banner displayed; see planner-trace.txt
--- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
--
--Failure (retry #1):
--- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
--- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
--
--Planner trace highlights:
--- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
--- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
--
--Server 500s: Not captured by Playwright listener on this run.
--Critical console errors: Not captured by Playwright listener on this run.
-+Result: PASS
- 
- Artifacts:
--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
-+- None (pass run)
+Planned: Read governance docs; gate planner/week/routine fetches; add single poller + aborts; add BOOT_DEBUG logs; run py_compile; update updatedifflog
+Completed: Read directive/blueprint/manifesto; gated planner/week/routine loads; added poller/abort guards and drilldown/panel logs; ran py_compile api.py
+Remaining: Manual UI verification of view gating; commit checkpoint after verification
+Next Action: Manually verify Chat/Planner/Week/Routine behavior, then git status/diff/add and commit with message "Fix: Today Planner load + confirm wiring; stabilize E2E"
 diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
-index 16f62059..18158802 100644
+index 4608da02..530f3254 100644
 --- a/evidence/updatedifflog.md
 +++ b/evidence/updatedifflog.md
-@@ -1,487 +1,820 @@
--Cycle Status: STOPPED:CONTRACT_CONFLICT
-+Cycle Status: COMPLETE
+@@ -1,1588 +1,2504 @@
+ Cycle Status: COMPLETE
  Todo Ledger:
--- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
--- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
--- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.
-+- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
-+- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
-+- Remaining: None.
- 
--Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.
-+Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
- 
- diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
--index 45518278..3fd145c5 100644
-+index 3fd145c5..ce3666e6 100644
- --- a/evidence/e2e_run.md
- +++ b/evidence/e2e_run.md
--@@ -1,38 +1,39 @@
---Date/Time: 2026-01-03 17:02:21 +00:00
--+Date/Time: 2026-01-03 17:35:21 +00:00
-+@@ -1,39 +1,20 @@
-+-Date/Time: 2026-01-03 17:35:21 +00:00
-++Date/Time: 2026-01-03 17:46:11 +00:00
-  
-  Commands:
---- npm install
---- npx playwright install --with-deps
-  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
---- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
--+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
-+-- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
-  
-  Env Vars:
-  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
-  - OTHELLO_ACCESS_CODE=******69
-  
--+Auth probe summary (manual):
--+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
--+- /api/today-brief -> 200 {"brief":{...}}
--+- /api/today-plan -> 200 {"plan":{...}}
--+
-- Result: FAIL
-+-Auth probe summary (manual):
-+-- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
-+-- /api/today-brief -> 200 {"brief":{...}}
-+-- /api/today-plan -> 200 {"plan":{...}}
-++Planner load instrumentation:
-++- Planner load failed banner: NOT observed in passing run
-++- fetchTodayBrief failure is now non-fatal (logs only)
-+ 
-+-Result: FAIL
-++Confirm endpoint:
-++- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})
-  
---Failure 1 (initial run):
---- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
---- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
---- Artifacts:
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
-+-Failure (attempt #1):
-+-- Error: Planner load failed banner displayed; see planner-trace.txt
-+-- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
- -
---Failure 2 (rerun after selector change):
---- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
---- Secondary: login overlay still visible after 20s (retry #1)
---- Locations:
---  - tests/e2e/othello.todayplanner.routines.spec.js:19
---  - tests/e2e/othello.todayplanner.routines.spec.js:15
---- Artifacts:
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
-+-Failure (retry #1):
-+-- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
-+-- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
- -
---Server 500s: Not evaluated (test timed out before assertion stage).
---Console errors: Not evaluated; none surfaced in runner output.
--+Failure (attempt #1):
--+- Error: Planner load failed banner displayed; see planner-trace.txt
--+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
--+
--+Failure (retry #1):
--+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
--+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
--+
--+Planner trace highlights:
--+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
--+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
--+
--+Server 500s: Not captured by Playwright listener on this run.
--+Critical console errors: Not captured by Playwright listener on this run.
-+-Planner trace highlights:
-+-- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
-+-- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+-- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
+-- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
+-- Remaining: None.
+-
+-Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
+-
+-diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
+-index 3fd145c5..ce3666e6 100644
+---- a/evidence/e2e_run.md
+-+++ b/evidence/e2e_run.md
+-@@ -1,39 +1,20 @@
+--Date/Time: 2026-01-03 17:35:21 +00:00
+-+Date/Time: 2026-01-03 17:46:11 +00:00
+- 
+- Commands:
+- - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
+--- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
+- 
+- Env Vars:
+- - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
+- - OTHELLO_ACCESS_CODE=******69
+- 
+--Auth probe summary (manual):
+--- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
+--- /api/today-brief -> 200 {"brief":{...}}
+--- /api/today-plan -> 200 {"plan":{...}}
+-+Planner load instrumentation:
+-+- Planner load failed banner: NOT observed in passing run
+-+- fetchTodayBrief failure is now non-fatal (logs only)
+- 
+--Result: FAIL
+-+Confirm endpoint:
+-+- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})
+- 
+--Failure (attempt #1):
+--- Error: Planner load failed banner displayed; see planner-trace.txt
+--- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
+--
+--Failure (retry #1):
+--- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
+--- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
+--
+--Planner trace highlights:
+--- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+--- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+--
+--Server 500s: Not captured by Playwright listener on this run.
+--Critical console errors: Not captured by Playwright listener on this run.
+-+Result: PASS
+- 
+- Artifacts:
+--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+-+- None (pass run)
++Planned: Gate planner/week/routine fetches; add single poller + abort handling; add debug logging; run py_compile; update evidence
++Completed: Gated planner/week/routine loads; added poller control + aborts; added debug logs; ran py_compile api.py
++Remaining: Manual UI verification and commit checkpoint
++Next Action: Run the How to verify steps, then git status/diff/add and commit the intended files
++How to verify:
++- Open app and stay in Chat for 30s; Network should not show today-brief/today-plan/week/routines spam
++- Switch to Today Planner; it should fetch once and start polling
++- Switch back to Chat; polling stops and planner calls end
++- Open week drilldown; it should fetch once and stop on close
+ diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+-index 16f62059..18158802 100644
++index 4608da02..1cfdf574 100644
+ --- a/evidence/updatedifflog.md
+ +++ b/evidence/updatedifflog.md
+-@@ -1,487 +1,820 @@
+--Cycle Status: STOPPED:CONTRACT_CONFLICT
+-+Cycle Status: COMPLETE
++@@ -1,1588 +1,468 @@
++ Cycle Status: COMPLETE
+  Todo Ledger:
+--- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
+--- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
+--- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.
+-+- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
+-+- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
+-+- Remaining: None.
+- 
+--Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.
+-+Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
+- 
+- diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
+--index 45518278..3fd145c5 100644
+-+index 3fd145c5..ce3666e6 100644
+- --- a/evidence/e2e_run.md
+- +++ b/evidence/e2e_run.md
+--@@ -1,38 +1,39 @@
+---Date/Time: 2026-01-03 17:02:21 +00:00
+--+Date/Time: 2026-01-03 17:35:21 +00:00
+-+@@ -1,39 +1,20 @@
+-+-Date/Time: 2026-01-03 17:35:21 +00:00
+-++Date/Time: 2026-01-03 17:46:11 +00:00
++-- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
++-- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
++-- Remaining: None.
++-
++-Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
 +-
-+-Server 500s: Not captured by Playwright listener on this run.
-+-Critical console errors: Not captured by Playwright listener on this run.
-++Result: PASS
-+ 
-+ Artifacts:
-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
-++- None (pass run)
-+diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
-+index 16f62059..c737bd4c 100644
-+--- a/evidence/updatedifflog.md
-++++ b/evidence/updatedifflog.md
-+@@ -1,487 +1,9 @@
-+-Cycle Status: STOPPED:CONTRACT_CONFLICT
-++Cycle Status: COMPLETE
-+ Todo Ledger:
-+-- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
-+-- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
-+-- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.
-++- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
-++- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
-++- Remaining: None.
-+ 
-+-Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.
-++Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
-+ 
 +-diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
-+-index 45518278..3fd145c5 100644
++-index 3fd145c5..ce3666e6 100644
 +---- a/evidence/e2e_run.md
 +-+++ b/evidence/e2e_run.md
-+-@@ -1,38 +1,39 @@
-+--Date/Time: 2026-01-03 17:02:21 +00:00
-+-+Date/Time: 2026-01-03 17:35:21 +00:00
++-@@ -1,39 +1,20 @@
++--Date/Time: 2026-01-03 17:35:21 +00:00
++-+Date/Time: 2026-01-03 17:46:11 +00:00
 +- 
 +- Commands:
-+--- npm install
-+--- npx playwright install --with-deps
 +- - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
-+--- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
-+-+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
++--- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
 +- 
 +- Env Vars:
 +- - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
 +- - OTHELLO_ACCESS_CODE=******69
 +- 
-+-+Auth probe summary (manual):
-+-+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
-+-+- /api/today-brief -> 200 {"brief":{...}}
-+-+- /api/today-plan -> 200 {"plan":{...}}
-+-+
-+- Result: FAIL
++--Auth probe summary (manual):
++--- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
++--- /api/today-brief -> 200 {"brief":{...}}
++--- /api/today-plan -> 200 {"plan":{...}}
++-+Planner load instrumentation:
++-+- Planner load failed banner: NOT observed in passing run
++-+- fetchTodayBrief failure is now non-fatal (logs only)
++- 
++--Result: FAIL
++-+Confirm endpoint:
++-+- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})
 +- 
-+--Failure 1 (initial run):
-+--- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
-+--- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
-+--- Artifacts:
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++--Failure (attempt #1):
++--- Error: Planner load failed banner displayed; see planner-trace.txt
++--- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
 +--
-+--Failure 2 (rerun after selector change):
-+--- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
-+--- Secondary: login overlay still visible after 20s (retry #1)
-+--- Locations:
-+--  - tests/e2e/othello.todayplanner.routines.spec.js:19
-+--  - tests/e2e/othello.todayplanner.routines.spec.js:15
-+--- Artifacts:
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++--Failure (retry #1):
++--- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
++--- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
 +--
-+--Server 500s: Not evaluated (test timed out before assertion stage).
-+--Console errors: Not evaluated; none surfaced in runner output.
-+-+Failure (attempt #1):
-+-+- Error: Planner load failed banner displayed; see planner-trace.txt
-+-+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
-+-+
-+-+Failure (retry #1):
-+-+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
-+-+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
-+-+
-+-+Planner trace highlights:
-+-+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
-+-+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
-+-+
-+-+Server 500s: Not captured by Playwright listener on this run.
-+-+Critical console errors: Not captured by Playwright listener on this run.
++--Planner trace highlights:
++--- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++--- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++--
++--Server 500s: Not captured by Playwright listener on this run.
++--Critical console errors: Not captured by Playwright listener on this run.
++-+Result: PASS
++- 
++- Artifacts:
++--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
++--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
++--- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++-+- None (pass run)
++-diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++-index 16f62059..18158802 100644
++---- a/evidence/updatedifflog.md
++-+++ b/evidence/updatedifflog.md
++-@@ -1,487 +1,820 @@
++--Cycle Status: STOPPED:CONTRACT_CONFLICT
++-+Cycle Status: COMPLETE
++- Todo Ledger:
++--- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
++--- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
++--- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.
++-+- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
++-+- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
++-+- Remaining: None.
++- 
++--Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.
++-+Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
++- 
++- diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
++--index 45518278..3fd145c5 100644
++-+index 3fd145c5..ce3666e6 100644
++- --- a/evidence/e2e_run.md
++- +++ b/evidence/e2e_run.md
++--@@ -1,38 +1,39 @@
++---Date/Time: 2026-01-03 17:02:21 +00:00
++--+Date/Time: 2026-01-03 17:35:21 +00:00
++-+@@ -1,39 +1,20 @@
++-+-Date/Time: 2026-01-03 17:35:21 +00:00
++-++Date/Time: 2026-01-03 17:46:11 +00:00
++-  
++-  Commands:
++---- npm install
++---- npx playwright install --with-deps
++-  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
++---- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
++--+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
++-+-- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
++-  
++-  Env Vars:
++-  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
++-  - OTHELLO_ACCESS_CODE=******69
++-  
++--+Auth probe summary (manual):
++--+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
++--+- /api/today-brief -> 200 {"brief":{...}}
++--+- /api/today-plan -> 200 {"plan":{...}}
++--+
++-- Result: FAIL
++-+-Auth probe summary (manual):
++-+-- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
++-+-- /api/today-brief -> 200 {"brief":{...}}
++-+-- /api/today-plan -> 200 {"plan":{...}}
++-++Planner load instrumentation:
++-++- Planner load failed banner: NOT observed in passing run
++-++- fetchTodayBrief failure is now non-fatal (logs only)
++-+ 
++-+-Result: FAIL
++-++Confirm endpoint:
++-++- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})
++-  
++---Failure 1 (initial run):
++---- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
++---- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
++---- Artifacts:
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++-+-Failure (attempt #1):
++-+-- Error: Planner load failed banner displayed; see planner-trace.txt
++-+-- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
++- -
++---Failure 2 (rerun after selector change):
++---- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
++---- Secondary: login overlay still visible after 20s (retry #1)
++---- Locations:
++---  - tests/e2e/othello.todayplanner.routines.spec.js:19
++---  - tests/e2e/othello.todayplanner.routines.spec.js:15
++---- Artifacts:
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
++---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++-+-Failure (retry #1):
++-+-- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
++-+-- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
++- -
++---Server 500s: Not evaluated (test timed out before assertion stage).
++---Console errors: Not evaluated; none surfaced in runner output.
++--+Failure (attempt #1):
++--+- Error: Planner load failed banner displayed; see planner-trace.txt
++--+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
++--+
++--+Failure (retry #1):
++--+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
++--+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
++--+
++--+Planner trace highlights:
++--+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++--+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++--+
++--+Server 500s: Not captured by Playwright listener on this run.
++--+Critical console errors: Not captured by Playwright listener on this run.
++-+-Planner trace highlights:
++-+-- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++-+-- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++-+-
++-+-Server 500s: Not captured by Playwright listener on this run.
++-+-Critical console errors: Not captured by Playwright listener on this run.
++-++Result: PASS
++-+ 
++-+ Artifacts:
++-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
++-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
++-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++-++- None (pass run)
++-+diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++-+index 16f62059..c737bd4c 100644
++-+--- a/evidence/updatedifflog.md
++-++++ b/evidence/updatedifflog.md
++-+@@ -1,487 +1,9 @@
++-+-Cycle Status: STOPPED:CONTRACT_CONFLICT
++-++Cycle Status: COMPLETE
++-+ Todo Ledger:
++-+-- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
++-+-- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
++-+-- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.
++-++- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
++-++- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
++-++- Remaining: None.
++-+ 
++-+-Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.
++-++Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
++-+ 
++-+-diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
++-+-index 45518278..3fd145c5 100644
++-+---- a/evidence/e2e_run.md
++-+-+++ b/evidence/e2e_run.md
++-+-@@ -1,38 +1,39 @@
++-+--Date/Time: 2026-01-03 17:02:21 +00:00
++-+-+Date/Time: 2026-01-03 17:35:21 +00:00
++-+- 
++-+- Commands:
++-+--- npm install
++-+--- npx playwright install --with-deps
++-+- - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
++-+--- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
++-+-+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
++-+- 
++-+- Env Vars:
++-+- - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
++-+- - OTHELLO_ACCESS_CODE=******69
++-+- 
++-+-+Auth probe summary (manual):
++-+-+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
++-+-+- /api/today-brief -> 200 {"brief":{...}}
++-+-+- /api/today-plan -> 200 {"plan":{...}}
++-+-+
++-+- Result: FAIL
++-+- 
++-+--Failure 1 (initial run):
++-+--- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
++-+--- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
++-+--- Artifacts:
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++-+--
++-+--Failure 2 (rerun after selector change):
++-+--- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
++-+--- Secondary: login overlay still visible after 20s (retry #1)
++-+--- Locations:
++-+--  - tests/e2e/othello.todayplanner.routines.spec.js:19
++-+--  - tests/e2e/othello.todayplanner.routines.spec.js:15
++-+--- Artifacts:
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
++-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++-+--
++-+--Server 500s: Not evaluated (test timed out before assertion stage).
++-+--Console errors: Not evaluated; none surfaced in runner output.
++-+-+Failure (attempt #1):
++-+-+- Error: Planner load failed banner displayed; see planner-trace.txt
++-+-+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
++-+-+
++-+-+Failure (retry #1):
++-+-+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
++-+-+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
++-+-+
++-+-+Planner trace highlights:
++-+-+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++-+-+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
++-+-+
++-+-+Server 500s: Not captured by Playwright listener on this run.
++-+-+Critical console errors: Not captured by Playwright listener on this run.
++-+-+
++-+-+Artifacts:
++-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
++-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
++-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++-+-diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
++-+-index 5abbeab8..e7e992f5 100644
++-+---- a/tests/e2e/othello.todayplanner.routines.spec.js
++-+-+++ b/tests/e2e/othello.todayplanner.routines.spec.js
++-+-@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
++-+- const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
++-+- const STEP_TITLES = ["Breakfast", "Shower"];
++-+- 
++-+--async function login(page, accessCode) {
++-+-+async function recordAuthTrace(label, response, authTrace) {
++-+-+  let status = "NO_RESPONSE";
++-+-+  let bodyText = "";
++-+-+  if (response) {
++-+-+    status = response.status();
++-+-+    try {
++-+-+      bodyText = await response.text();
++-+-+    } catch (err) {
++-+-+      bodyText = `READ_ERROR: ${err.message}`;
++-+-+    }
++-+-+  }
++-+-+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
++-+-+  authTrace.push(`${label} ${status} ${snippet}`);
++-+-+  return { status, snippet, text: bodyText };
++-+-+}
++-+-+
++-+-+async function login(page, accessCode, baseURL, testInfo, authTrace) {
++-+-   const loginInput = page.locator("#login-pin");
++-+-   const loginOverlay = page.locator("#login-overlay");
++-+--  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
++-+-+  const loginForm = page.locator("#loginForm");
++-+-+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
++-+-+    failOnStatusCode: false,
++-+-+  });
++-+-+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
++-+-+  let preAuthData = null;
++-+-+  try {
++-+-+    preAuthData = JSON.parse(preAuthResult.text || "");
++-+-+  } catch {}
++-+-+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
++-+-   if (needsLogin) {
++-+-+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
++-+-+    const loginResponsePromise = page.waitForResponse(
++-+-+      (response) => response.url().includes("/api/auth/login"),
++-+-+      { timeout: 20000 }
++-+-+    ).catch(() => null);
++-+-     await loginInput.fill(accessCode);
++-+-     await page.locator("#login-btn").click();
++-+-+    const loginResponse = await loginResponsePromise;
++-+-+    if (loginResponse) {
++-+-+      await recordAuthTrace("auth/login", loginResponse, authTrace);
++-+-+    } else {
++-+-+      authTrace.push("auth/login NO_RESPONSE");
++-+-+    }
++-+-   }
++-+--  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
++-+-+
++-+-+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
++-+-+    failOnStatusCode: false,
++-+-+  });
++-+-+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
++-+-+  let meData = null;
++-+-+  try {
++-+-+    meData = JSON.parse(meResult.text || "");
++-+-+  } catch {}
++-+-+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
++-+-+
++-+-+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
++-+-+    failOnStatusCode: false,
++-+-+  });
++-+-+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
++-+-+
++-+-+  if (meResult.status !== 200 || !isAuthed) {
++-+-+    await testInfo.attach("auth-debug.txt", {
++-+-+      body: authTrace.join("\n"),
++-+-+      contentType: "text/plain",
++-+-+    });
++-+-+    throw new Error(
++-+-+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
++-+-+    );
++-+-+  }
++-+-+
++-+-   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
++-+-+  const overlayCount = await loginOverlay.count();
++-+-+  if (overlayCount > 0) {
++-+-+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
++-+-+  } else {
++-+-+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
++-+-+  }
++-+-+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
++-+- }
++-+- 
++-+- async function switchMode(page, label) {
++-+-@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+- 
++-+-   const serverErrors = [];
++-+-   const consoleErrors = [];
++-+-+  const authTrace = [];
++-+-+  const plannerTrace = [];
++-+- 
++-+-   page.on("response", (response) => {
++-+-     if (response.status() >= 500) {
++-+-@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+-     }
++-+-   });
++-+- 
++-+-+  page.on("response", async (response) => {
++-+-+    const url = response.url();
++-+-+    const matchesPlanner = (
++-+-+      url.includes("/api/today-plan")
++-+-+      || url.includes("/api/today-brief")
++-+-+      || url.includes("/v1/plan/draft")
++-+-+      || url.includes("/api/confirm")
++-+-+      || url.includes("/v1/confirm")
++-+-+      || url.includes("/api/plan/update")
++-+-+    );
++-+-+    if (!matchesPlanner) return;
++-+-+    const request = response.request();
++-+-+    let path = url;
++-+-+    try {
++-+-+      const parsed = new URL(url);
++-+-+      path = `${parsed.pathname}${parsed.search}`;
++-+-+    } catch {}
++-+-+    let bodyText = "";
++-+-+    try {
++-+-+      bodyText = await response.text();
++-+-+    } catch (err) {
++-+-+      bodyText = `READ_ERROR: ${err.message}`;
++-+-+    }
++-+-+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
++-+-+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
++-+-+  });
++-+-+
++-+-   page.on("console", (msg) => {
++-+-     if (msg.type() === "error") {
++-+-       consoleErrors.push(msg.text());
++-+-@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+-     consoleErrors.push(`pageerror: ${err.message}`);
++-+-   });
++-+- 
++-+--  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
++-+--  await login(page, accessCode);
++-+-+  try {
++-+-+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
++-+-+    await login(page, accessCode, baseURL, testInfo, authTrace);
++-+- 
++-+--  await switchMode(page, "Routine Planner");
++-+--  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
++-+-+    await switchMode(page, "Routine Planner");
++-+-+    await page.locator("#middle-tab").click();
++-+-+    await expect(page.locator("#routine-planner-view")).toBeVisible();
++-+- 
++-+--  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
++-+--  await page.locator("#routine-add-btn").click();
++-+--  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
++-+-+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
++-+-+    await page.locator("#routine-add-btn").click();
++-+-+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
++-+- 
++-+--  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
++-+-+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
++-+- 
++-+--  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
++-+--  for (const day of days) {
++-+--    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
++-+--      .locator("input[type=checkbox]")
++-+--      .check();
++-+--  }
++-+-+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
++-+-+    for (const day of days) {
++-+-+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
++-+-+        .locator("input[type=checkbox]")
++-+-+        .check();
++-+-+    }
++-+- 
++-+--  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
++-+--  await expect(timeInputs.first()).toBeVisible();
++-+--  await timeInputs.first().fill("06:00");
++-+-+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
++-+-+    await expect(timeInputs.first()).toBeVisible();
++-+-+    await timeInputs.first().fill("06:00");
++-+- 
++-+--  const addStepBtn = page.locator("#routine-add-step-btn");
++-+--  await addStepBtn.click();
++-+--  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
++-+--  await addStepBtn.click();
++-+--  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
++-+-+    const addStepBtn = page.locator("#routine-add-step-btn");
++-+-+    const stepInputs = page.locator("#routine-steps input[type=text]");
++-+-+    let stepCount = await stepInputs.count();
++-+-+    while (stepCount < 2) {
++-+-+      await addStepBtn.click();
++-+-+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
++-+-+      stepCount = await stepInputs.count();
++-+-+    }
++-+-+    const emptyIndices = [];
++-+-+    for (let i = 0; i < stepCount; i++) {
++-+-+      const value = await stepInputs.nth(i).inputValue();
++-+-+      if (!value.trim()) {
++-+-+        emptyIndices.push(i);
++-+-+      }
++-+-+    }
++-+-+    let targetIndices = [];
++-+-+    if (emptyIndices.length >= 2) {
++-+-+      targetIndices = emptyIndices.slice(0, 2);
++-+-+    } else {
++-+-+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
++-+-+    }
++-+-+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
++-+-+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
++-+- 
++-+--  const stepInputs = page.locator("#routine-steps input[type=text]");
++-+--  await stepInputs.nth(0).fill(STEP_TITLES[0]);
++-+--  await stepInputs.nth(1).fill(STEP_TITLES[1]);
++-+-+    await page.locator("#routine-save-btn").click();
++-+-+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
++-+- 
++-+--  await page.locator("#routine-save-btn").click();
++-+--  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
++-+-+    await switchMode(page, "Today Planner");
++-+- 
++-+--  await switchMode(page, "Today Planner");
++-+-+    await page.locator("#middle-tab").click();
++-+-+    await expect(page.locator("#today-planner-view")).toBeVisible();
++-+-+    const plannerFailedBanner = page.getByText("Planner load failed");
++-+-+    const plannerLoadResult = await Promise.race([
++-+-+      page.waitForResponse(
++-+-+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
++-+-+        { timeout: 20000 }
++-+-+      ).then(() => "ok").catch(() => null),
++-+-+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
++-+-+    ]);
++-+-+    if (plannerLoadResult !== "ok") {
++-+-+      await testInfo.attach("planner-trace.txt", {
++-+-+        body: plannerTrace.join("\n"),
++-+-+        contentType: "text/plain",
++-+-+      });
++-+-+      await testInfo.attach("console-errors.txt", {
++-+-+        body: consoleErrors.join("\n"),
++-+-+        contentType: "text/plain",
++-+-+      });
++-+-+      if (plannerLoadResult === "fail") {
++-+-+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
++-+-+      }
++-+-+      throw new Error("Planner load did not complete; see planner-trace.txt");
++-+-+    }
++-+-+    await expect(page.locator("#build-plan-btn")).toBeVisible();
++-+-+    await page.locator("#build-plan-btn").click();
++-+- 
++-+--  await page.locator("#middle-tab").click();
++-+--  await expect(page.locator("#today-planner-view")).toBeVisible();
++-+--  await expect(page.locator("#build-plan-btn")).toBeVisible();
++-+--  await page.locator("#build-plan-btn").click();
++-+-+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
++-+-+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
++-+-+    const pendingCount = await suggestionsList.count();
++-+- 
++-+--  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
++-+--  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
++-+--  const pendingCount = await suggestionsList.count();
++-+-+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
++-+-+    if (await targetCard.count() === 0) {
++-+-+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
++-+-+    }
++-+-+    const targetCount = await targetCard.count();
++-+-+    expect(
++-+-+      targetCount,
++-+-+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
++-+-+    ).toBeGreaterThan(0);
++-+- 
++-+--  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
++-+--  if (await targetCard.count() === 0) {
++-+--    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
++-+--  }
++-+--  const targetCount = await targetCard.count();
++-+--  expect(
++-+--    targetCount,
++-+--    "Expected at least one routine-related suggestion (name match or routine- fallback)."
++-+--  ).toBeGreaterThan(0);
++-+--
++-+--  targetCard = targetCard.first();
++-+--  let selectedTitle = "";
++-+--  const titleLocator = targetCard.locator(".planner-block__title");
++-+--  if (await titleLocator.count()) {
++-+--    selectedTitle = (await titleLocator.first().innerText()).trim();
++-+--  }
++-+--  if (!selectedTitle) {
++-+--    selectedTitle = ((await targetCard.textContent()) || "").trim();
++-+--  }
++-+--  await targetCard.getByRole("button", { name: "Confirm" }).click();
++-+--
++-+--  await expect
++-+--    .poll(
++-+--      async () => {
++-+--        const currentCount = await suggestionsList.count();
++-+--        if (currentCount < pendingCount) return true;
++-+--        if (selectedTitle) {
++-+--          const panelText = await page.locator("#today-plan-suggestions").textContent();
++-+--          return panelText ? !panelText.includes(selectedTitle) : false;
++-+--        }
++-+--        return false;
++-+-+    targetCard = targetCard.first();
++-+-+    let selectedTitle = "";
++-+-+    const titleLocator = targetCard.locator(".planner-block__title");
++-+-+    if (await titleLocator.count()) {
++-+-+      selectedTitle = (await titleLocator.first().innerText()).trim();
++-+-+    }
++-+-+    if (!selectedTitle) {
++-+-+      selectedTitle = ((await targetCard.textContent()) || "").trim();
++-+-+    }
++-+-+    const confirmResponsePromise = page.waitForResponse(
++-+-+      (response) => {
++-+-+        const url = response.url();
++-+-+        if (response.request().method() !== "POST") return false;
++-+-+        return url.includes("/confirm") || url.includes("/plan/update");
++-+-       },
++-+-       { timeout: 20000 }
++-+--    )
++-+--    .toBe(true);
++-+--
++-+--  const todayPlanItems = page.locator("#today-plan-items");
++-+--  await expect(todayPlanItems).toBeVisible();
++-+--  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
++-+--  if (selectedTitle && planText && planText.includes(selectedTitle)) {
++-+--    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
++-+--  } else {
++-+--    await expect
++-+--      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
++-+--      .toBeGreaterThan(0);
++-+--  }
++-+-+    );
++-+-+    await targetCard.getByRole("button", { name: "Confirm" }).click();
++-+-+    const confirmResponse = await confirmResponsePromise;
++-+-+    let confirmText = "";
++-+-+    try {
++-+-+      confirmText = await confirmResponse.text();
++-+-+    } catch {}
++-+-+    let confirmOk = confirmResponse.status() === 200;
++-+-+    if (confirmText.includes("\"ok\":")) {
++-+-+      confirmOk = confirmText.includes("\"ok\":true");
++-+-+    }
++-+-+    if (!confirmOk) {
++-+-+      await testInfo.attach("planner-trace.txt", {
++-+-+        body: plannerTrace.join("\n"),
++-+-+        contentType: "text/plain",
++-+-+      });
++-+-+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
++-+-+    }
++-+- 
++-+--  if (consoleErrors.length) {
++-+--    await testInfo.attach("console-errors.txt", {
++-+--      body: consoleErrors.join("\n"),
++-+--      contentType: "text/plain",
++-+--    });
++-+--  }
++-+-+    await page.locator("#middle-tab").click();
++-+-+    await expect(page.locator("#today-planner-view")).toBeVisible();
++-+- 
++-+--  if (serverErrors.length) {
++-+--    await testInfo.attach("server-500s.txt", {
++-+--      body: serverErrors.join("\n"),
++-+--      contentType: "text/plain",
++-+--    });
++-+--  }
++-+-+    const todayPlanItems = page.locator("#today-plan-items");
++-+-+    await expect(todayPlanItems).toBeVisible();
++-+-+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
++-+-+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
++-+-+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
++-+-+    } else {
++-+-+      await expect
++-+-+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
++-+-+        .toBeGreaterThan(0);
++-+-+    }
++-+- 
++-+--  const criticalConsoleErrors = consoleErrors.filter((entry) => (
++-+--    entry.includes("Uncaught") || entry.includes("TypeError")
++-+--  ));
++-+--  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
++-+--  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
++-+-+    if (consoleErrors.length) {
++-+-+      await testInfo.attach("console-errors.txt", {
++-+-+        body: consoleErrors.join("\n"),
++-+-+        contentType: "text/plain",
++-+-+      });
++-+-+    }
++-+-+
++-+-+    if (serverErrors.length) {
++-+-+      await testInfo.attach("server-500s.txt", {
++-+-+        body: serverErrors.join("\n"),
++-+-+        contentType: "text/plain",
++-+-+      });
++-+-+    }
++-+-+
++-+-+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
++-+-+      entry.includes("Uncaught") || entry.includes("TypeError")
++-+-+    ));
++-+-+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
++-+-+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
++-+-+  } finally {
++-+-+    if (plannerTrace.length) {
++-+-+      await testInfo.attach("planner-trace.txt", {
++-+-+        body: plannerTrace.join("\n"),
++-+-+        contentType: "text/plain",
++-+-+      });
++-+-+    }
++-+-+  }
++-+- });
++-++diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md index 3fd145c5..ce3666e6 100644 --- a/evidence/e2e_run.md +++ b/evidence/e2e_run.md @@ -1,39 +1,20 @@ -Date/Time: 2026-01-03 17:35:21 +00:00 +Date/Time: 2026-01-03 17:46:11 +00:00    Commands:  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e -- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)    Env Vars:  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/  - OTHELLO_ACCESS_CODE=******69   -Auth probe summary (manual): -- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -- /api/today-brief -> 200 {"brief":{...}} -- /api/today-plan -> 200 {"plan":{...}} +Planner load instrumentation: +- Planner load failed banner: NOT observed in passing run +- fetchTodayBrief failure is now non-fatal (logs only)   -Result: FAIL +Confirm endpoint: +- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})   -Failure (attempt #1): -- Error: Planner load failed banner displayed; see planner-trace.txt -- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 - -Failure (retry #1): -- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 - -Planner trace highlights: -- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... - -Server 500s: Not captured by Playwright listener on this run. -Critical console errors: Not captured by Playwright listener on this run. +Result: PASS    Artifacts: -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md +- None (pass run) diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md index 16f62059..1ca047b1 100644 --- a/evidence/updatedifflog.md +++ b/evidence/updatedifflog.md @@ -1,487 +1,9 @@ -Cycle Status: STOPPED:CONTRACT_CONFLICT +Cycle Status: COMPLETE  Todo Ledger: -- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once. -- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence. -- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun. +- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E. +- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed. +- Remaining: None.   -Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E. +Next Action: Optional: clean routine data on Render for slimmer suggestion lists.   -diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md -index 45518278..3fd145c5 100644 ---- a/evidence/e2e_run.md -+++ b/evidence/e2e_run.md -@@ -1,38 +1,39 @@ --Date/Time: 2026-01-03 17:02:21 +00:00 -+Date/Time: 2026-01-03 17:35:21 +00:00 -  - Commands: --- npm install --- npx playwright install --with-deps - - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e --- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab) -+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest) -  - Env Vars: - - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/ - - OTHELLO_ACCESS_CODE=******69 -  -+Auth probe summary (manual): -+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -+- /api/today-brief -> 200 {"brief":{...}} -+- /api/today-plan -> 200 {"plan":{...}} -+ - Result: FAIL -  --Failure 1 (initial run): --- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation --- Location: tests/e2e/othello.todayplanner.routines.spec.js:14 --- Artifacts: --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- --Failure 2 (rerun after selector change): --- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events --- Secondary: login overlay still visible after 20s (retry #1) --- Locations: --  - tests/e2e/othello.todayplanner.routines.spec.js:19 --  - tests/e2e/othello.todayplanner.routines.spec.js:15 --- Artifacts: --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md -- --Server 500s: Not evaluated (test timed out before assertion stage). --Console errors: Not evaluated; none surfaced in runner output. -+Failure (attempt #1): -+- Error: Planner load failed banner displayed; see planner-trace.txt -+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 -+ -+Failure (retry #1): -+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 -+ -+Planner trace highlights: -+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -+ -+Server 500s: Not captured by Playwright listener on this run. -+Critical console errors: Not captured by Playwright listener on this run. -+ -+Artifacts: -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md -diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js -index 5abbeab8..e7e992f5 100644 ---- a/tests/e2e/othello.todayplanner.routines.spec.js -+++ b/tests/e2e/othello.todayplanner.routines.spec.js -@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test"); - const ROUTINE_NAME = "E2E Morning Routine " + Date.now(); - const STEP_TITLES = ["Breakfast", "Shower"]; -  --async function login(page, accessCode) { -+async function recordAuthTrace(label, response, authTrace) { -+  let status = "NO_RESPONSE"; -+  let bodyText = ""; -+  if (response) { -+    status = response.status(); -+    try { -+      bodyText = await response.text(); -+    } catch (err) { -+      bodyText = `READ_ERROR: ${err.message}`; -+    } -+  } -+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300); -+  authTrace.push(`${label} ${status} ${snippet}`); -+  return { status, snippet, text: bodyText }; -+} -+ -+async function login(page, accessCode, baseURL, testInfo, authTrace) { -   const loginInput = page.locator("#login-pin"); -   const loginOverlay = page.locator("#login-overlay"); --  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false); -+  const loginForm = page.locator("#loginForm"); -+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace); -+  let preAuthData = null; -+  try { -+    preAuthData = JSON.parse(preAuthResult.text || ""); -+  } catch {} -+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated)); -   if (needsLogin) { -+    await loginInput.waitFor({ state: "visible", timeout: 20000 }); -+    const loginResponsePromise = page.waitForResponse( -+      (response) => response.url().includes("/api/auth/login"), -+      { timeout: 20000 } -+    ).catch(() => null); -     await loginInput.fill(accessCode); -     await page.locator("#login-btn").click(); -+    const loginResponse = await loginResponsePromise; -+    if (loginResponse) { -+      await recordAuthTrace("auth/login", loginResponse, authTrace); -+    } else { -+      authTrace.push("auth/login NO_RESPONSE"); -+    } -   } --  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 }); -+ -+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace); -+  let meData = null; -+  try { -+    meData = JSON.parse(meResult.text || ""); -+  } catch {} -+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated)); -+ -+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace); -+ -+  if (meResult.status !== 200 || !isAuthed) { -+    await testInfo.attach("auth-debug.txt", { -+      body: authTrace.join("\n"), -+      contentType: "text/plain", -+    }); -+    throw new Error( -+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}` -+    ); -+  } -+ -   await expect(loginOverlay).toBeHidden({ timeout: 20000 }); -+  const overlayCount = await loginOverlay.count(); -+  if (overlayCount > 0) { -+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 }); -+  } else { -+    await expect(loginForm).toHaveCount(0, { timeout: 20000 }); -+  } -+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 }); - } -  - async function switchMode(page, label) { -@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -  -   const serverErrors = []; -   const consoleErrors = []; -+  const authTrace = []; -+  const plannerTrace = []; -  -   page.on("response", (response) => { -     if (response.status() >= 500) { -@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -     } -   }); -  -+  page.on("response", async (response) => { -+    const url = response.url(); -+    const matchesPlanner = ( -+      url.includes("/api/today-plan") -+      || url.includes("/api/today-brief") -+      || url.includes("/v1/plan/draft") -+      || url.includes("/api/confirm") -+      || url.includes("/v1/confirm") -+      || url.includes("/api/plan/update") -+    ); -+    if (!matchesPlanner) return; -+    const request = response.request(); -+    let path = url; -+    try { -+      const parsed = new URL(url); -+      path = `${parsed.pathname}${parsed.search}`; -+    } catch {} -+    let bodyText = ""; -+    try { -+      bodyText = await response.text(); -+    } catch (err) { -+      bodyText = `READ_ERROR: ${err.message}`; -+    } -+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300); -+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`); -+  }); -+ -   page.on("console", (msg) => { -     if (msg.type() === "error") { -       consoleErrors.push(msg.text()); -@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -     consoleErrors.push(`pageerror: ${err.message}`); -   }); -  --  await page.goto(baseURL, { waitUntil: "domcontentloaded" }); --  await login(page, accessCode); -+  try { -+    await page.goto(baseURL, { waitUntil: "domcontentloaded" }); -+    await login(page, accessCode, baseURL, testInfo, authTrace); -  --  await switchMode(page, "Routine Planner"); --  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible(); -+    await switchMode(page, "Routine Planner"); -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#routine-planner-view")).toBeVisible(); -  --  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME)); --  await page.locator("#routine-add-btn").click(); --  await page.locator("#routine-title-input").fill(ROUTINE_NAME); -+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME)); -+    await page.locator("#routine-add-btn").click(); -+    await page.locator("#routine-title-input").fill(ROUTINE_NAME); -  --  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 }); -+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 }); -  --  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]; --  for (const day of days) { --    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") }) --      .locator("input[type=checkbox]") --      .check(); --  } -+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]; -+    for (const day of days) { -+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") }) -+        .locator("input[type=checkbox]") -+        .check(); -+    } -  --  const timeInputs = page.locator("#routine-schedule-extra input[type=time]"); --  await expect(timeInputs.first()).toBeVisible(); --  await timeInputs.first().fill("06:00"); -+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]"); -+    await expect(timeInputs.first()).toBeVisible(); -+    await timeInputs.first().fill("06:00"); -  --  const addStepBtn = page.locator("#routine-add-step-btn"); --  await addStepBtn.click(); --  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 }); --  await addStepBtn.click(); --  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 }); -+    const addStepBtn = page.locator("#routine-add-step-btn"); -+    const stepInputs = page.locator("#routine-steps input[type=text]"); -+    let stepCount = await stepInputs.count(); -+    while (stepCount < 2) { -+      await addStepBtn.click(); -+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 }); -+      stepCount = await stepInputs.count(); -+    } -+    const emptyIndices = []; -+    for (let i = 0; i < stepCount; i++) { -+      const value = await stepInputs.nth(i).inputValue(); -+      if (!value.trim()) { -+        emptyIndices.push(i); -+      } -+    } -+    let targetIndices = []; -+    if (emptyIndices.length >= 2) { -+      targetIndices = emptyIndices.slice(0, 2); -+    } else { -+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1]; -+    } -+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]); -+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]); -  --  const stepInputs = page.locator("#routine-steps input[type=text]"); --  await stepInputs.nth(0).fill(STEP_TITLES[0]); --  await stepInputs.nth(1).fill(STEP_TITLES[1]); -+    await page.locator("#routine-save-btn").click(); -+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 }); -  --  await page.locator("#routine-save-btn").click(); --  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 }); -+    await switchMode(page, "Today Planner"); -  --  await switchMode(page, "Today Planner"); -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#today-planner-view")).toBeVisible(); -+    const plannerFailedBanner = page.getByText("Planner load failed"); -+    const plannerLoadResult = await Promise.race([ -+      page.waitForResponse( -+        (response) => response.url().includes("/api/today-plan") && response.status() === 200, -+        { timeout: 20000 } -+      ).then(() => "ok").catch(() => null), -+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null), -+    ]); -+    if (plannerLoadResult !== "ok") { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+      await testInfo.attach("console-errors.txt", { -+        body: consoleErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+      if (plannerLoadResult === "fail") { -+        throw new Error("Planner load failed banner displayed; see planner-trace.txt"); -+      } -+      throw new Error("Planner load did not complete; see planner-trace.txt"); -+    } -+    await expect(page.locator("#build-plan-btn")).toBeVisible(); -+    await page.locator("#build-plan-btn").click(); -  --  await page.locator("#middle-tab").click(); --  await expect(page.locator("#today-planner-view")).toBeVisible(); --  await expect(page.locator("#build-plan-btn")).toBeVisible(); --  await page.locator("#build-plan-btn").click(); -+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block"); -+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 }); -+    const pendingCount = await suggestionsList.count(); -  --  const suggestionsList = page.locator("#today-plan-suggestions .planner-block"); --  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 }); --  const pendingCount = await suggestionsList.count(); -+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME }); -+    if (await targetCard.count() === 0) { -+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i }); -+    } -+    const targetCount = await targetCard.count(); -+    expect( -+      targetCount, -+      "Expected at least one routine-related suggestion (name match or routine- fallback)." -+    ).toBeGreaterThan(0); -  --  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME }); --  if (await targetCard.count() === 0) { --    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i }); --  } --  const targetCount = await targetCard.count(); --  expect( --    targetCount, --    "Expected at least one routine-related suggestion (name match or routine- fallback)." --  ).toBeGreaterThan(0); -- --  targetCard = targetCard.first(); --  let selectedTitle = ""; --  const titleLocator = targetCard.locator(".planner-block__title"); --  if (await titleLocator.count()) { --    selectedTitle = (await titleLocator.first().innerText()).trim(); --  } --  if (!selectedTitle) { --    selectedTitle = ((await targetCard.textContent()) || "").trim(); --  } --  await targetCard.getByRole("button", { name: "Confirm" }).click(); -- --  await expect --    .poll( --      async () => { --        const currentCount = await suggestionsList.count(); --        if (currentCount < pendingCount) return true; --        if (selectedTitle) { --          const panelText = await page.locator("#today-plan-suggestions").textContent(); --          return panelText ? !panelText.includes(selectedTitle) : false; --        } --        return false; -+    targetCard = targetCard.first(); -+    let selectedTitle = ""; -+    const titleLocator = targetCard.locator(".planner-block__title"); -+    if (await titleLocator.count()) { -+      selectedTitle = (await titleLocator.first().innerText()).trim(); -+    } -+    if (!selectedTitle) { -+      selectedTitle = ((await targetCard.textContent()) || "").trim(); -+    } -+    const confirmResponsePromise = page.waitForResponse( -+      (response) => { -+        const url = response.url(); -+        if (response.request().method() !== "POST") return false; -+        return url.includes("/confirm") || url.includes("/plan/update"); -       }, -       { timeout: 20000 } --    ) --    .toBe(true); -- --  const todayPlanItems = page.locator("#today-plan-items"); --  await expect(todayPlanItems).toBeVisible(); --  const planText = selectedTitle ? await todayPlanItems.textContent() : ""; --  if (selectedTitle && planText && planText.includes(selectedTitle)) { --    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 }); --  } else { --    await expect --      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 }) --      .toBeGreaterThan(0); --  } -+    ); -+    await targetCard.getByRole("button", { name: "Confirm" }).click(); -+    const confirmResponse = await confirmResponsePromise; -+    let confirmText = ""; -+    try { -+      confirmText = await confirmResponse.text(); -+    } catch {} -+    let confirmOk = confirmResponse.status() === 200; -+    if (confirmText.includes("\"ok\":")) { -+      confirmOk = confirmText.includes("\"ok\":true"); -+    } -+    if (!confirmOk) { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`); -+    } -  --  if (consoleErrors.length) { --    await testInfo.attach("console-errors.txt", { --      body: consoleErrors.join("\n"), --      contentType: "text/plain", --    }); --  } -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#today-planner-view")).toBeVisible(); -  --  if (serverErrors.length) { --    await testInfo.attach("server-500s.txt", { --      body: serverErrors.join("\n"), --      contentType: "text/plain", --    }); --  } -+    const todayPlanItems = page.locator("#today-plan-items"); -+    await expect(todayPlanItems).toBeVisible(); -+    const planText = selectedTitle ? await todayPlanItems.textContent() : ""; -+    if (selectedTitle && planText && planText.includes(selectedTitle)) { -+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 }); -+    } else { -+      await expect -+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 }) -+        .toBeGreaterThan(0); -+    } -  --  const criticalConsoleErrors = consoleErrors.filter((entry) => ( --    entry.includes("Uncaught") || entry.includes("TypeError") --  )); --  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]); --  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]); -+    if (consoleErrors.length) { -+      await testInfo.attach("console-errors.txt", { -+        body: consoleErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+ -+    if (serverErrors.length) { -+      await testInfo.attach("server-500s.txt", { -+        body: serverErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+ -+    const criticalConsoleErrors = consoleErrors.filter((entry) => ( -+      entry.includes("Uncaught") || entry.includes("TypeError") -+    )); -+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]); -+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]); -+  } finally { -+    if (plannerTrace.length) { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+  } - }); +diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md index 3fd145c5..ce3666e6 100644 --- a/evidence/e2e_run.md +++ b/evidence/e2e_run.md @@ -1,39 +1,20 @@ -Date/Time: 2026-01-03 17:35:21 +00:00 +Date/Time: 2026-01-03 17:46:11 +00:00    Commands:  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e -- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)    Env Vars:  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/  - OTHELLO_ACCESS_CODE=******69   -Auth probe summary (manual): -- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -- /api/today-brief -> 200 {"brief":{...}} -- /api/today-plan -> 200 {"plan":{...}} +Planner load instrumentation: +- Planner load failed banner: NOT observed in passing run +- fetchTodayBrief failure is now non-fatal (logs only)   -Result: FAIL +Confirm endpoint: +- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})   -Failure (attempt #1): -- Error: Planner load failed banner displayed; see planner-trace.txt -- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 - -Failure (retry #1): -- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 - -Planner trace highlights: -- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... - -Server 500s: Not captured by Playwright listener on this run. -Critical console errors: Not captured by Playwright listener on this run. +Result: PASS    Artifacts: -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md +- None (pass run) diff --git a/othello_ui.html b/othello_ui.html index 4ed3660c..f53dba97 100644 --- a/othello_ui.html +++ b/othello_ui.html @@ -3073,14 +3073,30 @@        async function fetchTodayBrief() {        const resp = await fetch("/api/today-brief", { credentials: "include" }); -      if (resp.status === 401 || resp.status === 403) { +      const status = resp.status; +      const text = await resp.text(); +      if (status === 401 || status === 403) {          const err = new Error("Unauthorized"); -        err.status = resp.status; +        err.status = status;          throw err;        } -      if (!resp.ok) throw new Error("Failed to load brief"); -      const data = await resp.json(); -      return data.brief || {}; +      if (!resp.ok) { +        const err = new Error("Failed to load brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        throw err; +      } +      let data = null; +      try { +        data = JSON.parse(text); +      } catch (parseErr) { +        const err = new Error("Failed to parse brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        err.parseError = parseErr.message; +        throw err; +      } +      return (data && data.brief) || {};      }        async function fetchTodayPlan() { @@ -3206,13 +3222,21 @@            if (!suggestion || !suggestion.id) return;            confirmBtn.disabled = true;            try { +            const confirmPayload = { reason: "confirm" }; +            if (BOOT_DEBUG) { +              console.info("[Today Planner] confirm suggestion", { +                endpoint: `/v1/suggestions/${suggestion.id}/accept`, +                method: "POST", +                payloadKeys: Object.keys(confirmPayload), +              }); +            }              await v1Request(                `/v1/suggestions/${suggestion.id}/accept`,                {                  method: "POST",                  headers: { "Content-Type": "application/json" },                  credentials: "include", -                body: JSON.stringify({ reason: "confirm" }) +                body: JSON.stringify(confirmPayload)                },                "Confirm suggestion"              ); @@ -3359,11 +3383,16 @@        });      }   -    function renderPlannerError(message, httpStatus) { +    function renderPlannerError(message, httpStatus, details) {        plannerError.style.display = "block";        let msg = message || "Could not load today's plan. Please try again later.";        if (httpStatus) msg += ` (HTTP ${httpStatus})`;        plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`; +      if (details) { +        plannerError.dataset.error = details; +      } else { +        delete plannerError.dataset.error; +      }        const retryBtn = document.getElementById("planner-retry-btn");        if (retryBtn) {          retryBtn.onclick = () => { @@ -5067,16 +5096,50 @@            };        }   +      let planStatus = null; +      let planSnippet = null; +      let planParseError = null; +      let briefStatus = null; +      let briefSnippet = null; +      let briefParseError = null; +      let planUrl = null;        try { -        const planUrl = dayViewDateYmd  +        planUrl = dayViewDateYmd               ? `/api/today-plan?plan_date=${dayViewDateYmd}`               : `/api/today-plan?ts=${Date.now()}`; -             -        const [brief, planResp] = await Promise.all([ -            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days -            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json()) -        ]); -         +        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => { +          briefStatus = err && err.status ? err.status : null; +          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null; +          briefParseError = err && err.parseError ? err.parseError : null; +          console.error("[Today Planner] fetchTodayBrief failed", { +            status: briefStatus, +            parseError: briefParseError, +            error: err && err.message, +          }); +          return {}; +        }); +        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" }); +        planStatus = planResponse.status; +        const planText = await planResponse.text(); +        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300); +        if (!planResponse.ok) { +          const err = new Error("Failed to load plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          throw err; +        } +        let planResp = null; +        try { +          planResp = JSON.parse(planText); +        } catch (parseErr) { +          planParseError = parseErr.message; +          const err = new Error("Failed to parse plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          err.parseError = planParseError; +          throw err; +        } +          const plan = planResp.plan || {};          const goalTasks = (plan.sections?.goal_tasks || []);          if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source }); @@ -5103,7 +5166,25 @@            const match = e.message.match(/HTTP (\d+)/);            if (match) httpStatus = match[1];          } -        renderPlannerError("Planner load failed", httpStatus); +        if (e && e.status) httpStatus = e.status; +        const detailParts = []; +        if (planStatus) detailParts.push(`today-plan:${planStatus}`); +        if (planParseError) detailParts.push(`plan_parse:${planParseError}`); +        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`); +        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`); +        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`); +        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`); +        if (e && e.message) detailParts.push(`error:${e.message}`); +        const detailString = detailParts.join(" | ").slice(0, 300); +        console.error("[Today Planner] loadTodayPlanner failed", { +          planUrl, +          planStatus, +          briefStatus, +          planParseError, +          briefParseError, +          error: e && e.message, +        }); +        renderPlannerError("Planner load failed", httpStatus, detailString);          if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);        }      } diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js index e7e992f5..d48e604d 100644 --- a/tests/e2e/othello.todayplanner.routines.spec.js +++ b/tests/e2e/othello.todayplanner.routines.spec.js @@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes    const consoleErrors = [];    const authTrace = [];    const plannerTrace = []; +  const postTrace = [];      page.on("response", (response) => {      if (response.status() >= 500) { @@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        || url.includes("/v1/plan/draft")        || url.includes("/api/confirm")        || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/")        || url.includes("/api/plan/update")      );      if (!matchesPlanner) return; @@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes      plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);    });   +  page.on("request", (request) => { +    const url = request.url(); +    if (request.method() !== "POST") return; +    const matches = ( +      url.includes("/api/confirm") +      || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/") +      || url.includes("/api/plan/update") +    ); +    if (!matches) return; +    let path = url; +    try { +      const parsed = new URL(url); +      path = `${parsed.pathname}${parsed.search}`; +    } catch {} +    const postData = request.postData() || ""; +    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300); +    postTrace.push(`${request.method()} ${path} ${snippet}`); +  }); +    page.on("console", (msg) => {      if (msg.type() === "error") {        consoleErrors.push(msg.text()); @@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          body: consoleErrors.join("\n"),          contentType: "text/plain",        }); +      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error"); +      if (plannerErrorDetails) { +        await testInfo.attach("planner-error.txt", { +          body: plannerErrorDetails, +          contentType: "text/plain", +        }); +      }        if (plannerLoadResult === "fail") {          throw new Error("Planner load failed banner displayed; see planner-trace.txt");        } @@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        (response) => {          const url = response.url();          if (response.request().method() !== "POST") return false; -        return url.includes("/confirm") || url.includes("/plan/update"); +        return url.includes("/v1/suggestions/") && url.includes("/accept");        },        { timeout: 20000 }      ); @@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        confirmText = await confirmResponse.text();      } catch {}      let confirmOk = confirmResponse.status() === 200; -    if (confirmText.includes("\"ok\":")) { -      confirmOk = confirmText.includes("\"ok\":true"); +    let confirmJson = null; +    try { +      confirmJson = JSON.parse(confirmText); +    } catch {} +    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) { +      confirmOk = confirmJson.ok === true;      }      if (!confirmOk) {        await testInfo.attach("planner-trace.txt", { @@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          contentType: "text/plain",        });      } +    await testInfo.attach("post-trace.txt", { +      body: postTrace.join("\n"), +      contentType: "text/plain", +    });    }  }); diff --git a/othello_ui.html b/othello_ui.html index 4ed3660c..f53dba97 100644 --- a/othello_ui.html +++ b/othello_ui.html @@ -3073,14 +3073,30 @@        async function fetchTodayBrief() {        const resp = await fetch("/api/today-brief", { credentials: "include" }); -      if (resp.status === 401 || resp.status === 403) { +      const status = resp.status; +      const text = await resp.text(); +      if (status === 401 || status === 403) {          const err = new Error("Unauthorized"); -        err.status = resp.status; +        err.status = status;          throw err;        } -      if (!resp.ok) throw new Error("Failed to load brief"); -      const data = await resp.json(); -      return data.brief || {}; +      if (!resp.ok) { +        const err = new Error("Failed to load brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        throw err; +      } +      let data = null; +      try { +        data = JSON.parse(text); +      } catch (parseErr) { +        const err = new Error("Failed to parse brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        err.parseError = parseErr.message; +        throw err; +      } +      return (data && data.brief) || {};      }        async function fetchTodayPlan() { @@ -3206,13 +3222,21 @@            if (!suggestion || !suggestion.id) return;            confirmBtn.disabled = true;            try { +            const confirmPayload = { reason: "confirm" }; +            if (BOOT_DEBUG) { +              console.info("[Today Planner] confirm suggestion", { +                endpoint: `/v1/suggestions/${suggestion.id}/accept`, +                method: "POST", +                payloadKeys: Object.keys(confirmPayload), +              }); +            }              await v1Request(                `/v1/suggestions/${suggestion.id}/accept`,                {                  method: "POST",                  headers: { "Content-Type": "application/json" },                  credentials: "include", -                body: JSON.stringify({ reason: "confirm" }) +                body: JSON.stringify(confirmPayload)                },                "Confirm suggestion"              ); @@ -3359,11 +3383,16 @@        });      }   -    function renderPlannerError(message, httpStatus) { +    function renderPlannerError(message, httpStatus, details) {        plannerError.style.display = "block";        let msg = message || "Could not load today's plan. Please try again later.";        if (httpStatus) msg += ` (HTTP ${httpStatus})`;        plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`; +      if (details) { +        plannerError.dataset.error = details; +      } else { +        delete plannerError.dataset.error; +      }        const retryBtn = document.getElementById("planner-retry-btn");        if (retryBtn) {          retryBtn.onclick = () => { @@ -5067,16 +5096,50 @@            };        }   +      let planStatus = null; +      let planSnippet = null; +      let planParseError = null; +      let briefStatus = null; +      let briefSnippet = null; +      let briefParseError = null; +      let planUrl = null;        try { -        const planUrl = dayViewDateYmd  +        planUrl = dayViewDateYmd               ? `/api/today-plan?plan_date=${dayViewDateYmd}`               : `/api/today-plan?ts=${Date.now()}`; -             -        const [brief, planResp] = await Promise.all([ -            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days -            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json()) -        ]); -         +        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => { +          briefStatus = err && err.status ? err.status : null; +          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null; +          briefParseError = err && err.parseError ? err.parseError : null; +          console.error("[Today Planner] fetchTodayBrief failed", { +            status: briefStatus, +            parseError: briefParseError, +            error: err && err.message, +          }); +          return {}; +        }); +        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" }); +        planStatus = planResponse.status; +        const planText = await planResponse.text(); +        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300); +        if (!planResponse.ok) { +          const err = new Error("Failed to load plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          throw err; +        } +        let planResp = null; +        try { +          planResp = JSON.parse(planText); +        } catch (parseErr) { +          planParseError = parseErr.message; +          const err = new Error("Failed to parse plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          err.parseError = planParseError; +          throw err; +        } +          const plan = planResp.plan || {};          const goalTasks = (plan.sections?.goal_tasks || []);          if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source }); @@ -5103,7 +5166,25 @@            const match = e.message.match(/HTTP (\d+)/);            if (match) httpStatus = match[1];          } -        renderPlannerError("Planner load failed", httpStatus); +        if (e && e.status) httpStatus = e.status; +        const detailParts = []; +        if (planStatus) detailParts.push(`today-plan:${planStatus}`); +        if (planParseError) detailParts.push(`plan_parse:${planParseError}`); +        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`); +        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`); +        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`); +        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`); +        if (e && e.message) detailParts.push(`error:${e.message}`); +        const detailString = detailParts.join(" | ").slice(0, 300); +        console.error("[Today Planner] loadTodayPlanner failed", { +          planUrl, +          planStatus, +          briefStatus, +          planParseError, +          briefParseError, +          error: e && e.message, +        }); +        renderPlannerError("Planner load failed", httpStatus, detailString);          if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);        }      } diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js index e7e992f5..d48e604d 100644 --- a/tests/e2e/othello.todayplanner.routines.spec.js +++ b/tests/e2e/othello.todayplanner.routines.spec.js @@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes    const consoleErrors = [];    const authTrace = [];    const plannerTrace = []; +  const postTrace = [];      page.on("response", (response) => {      if (response.status() >= 500) { @@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        || url.includes("/v1/plan/draft")        || url.includes("/api/confirm")        || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/")        || url.includes("/api/plan/update")      );      if (!matchesPlanner) return; @@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes      plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);    });   +  page.on("request", (request) => { +    const url = request.url(); +    if (request.method() !== "POST") return; +    const matches = ( +      url.includes("/api/confirm") +      || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/") +      || url.includes("/api/plan/update") +    ); +    if (!matches) return; +    let path = url; +    try { +      const parsed = new URL(url); +      path = `${parsed.pathname}${parsed.search}`; +    } catch {} +    const postData = request.postData() || ""; +    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300); +    postTrace.push(`${request.method()} ${path} ${snippet}`); +  }); +    page.on("console", (msg) => {      if (msg.type() === "error") {        consoleErrors.push(msg.text()); @@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          body: consoleErrors.join("\n"),          contentType: "text/plain",        }); +      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error"); +      if (plannerErrorDetails) { +        await testInfo.attach("planner-error.txt", { +          body: plannerErrorDetails, +          contentType: "text/plain", +        }); +      }        if (plannerLoadResult === "fail") {          throw new Error("Planner load failed banner displayed; see planner-trace.txt");        } @@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        (response) => {          const url = response.url();          if (response.request().method() !== "POST") return false; -        return url.includes("/confirm") || url.includes("/plan/update"); +        return url.includes("/v1/suggestions/") && url.includes("/accept");        },        { timeout: 20000 }      ); @@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        confirmText = await confirmResponse.text();      } catch {}      let confirmOk = confirmResponse.status() === 200; -    if (confirmText.includes("\"ok\":")) { -      confirmOk = confirmText.includes("\"ok\":true"); +    let confirmJson = null; +    try { +      confirmJson = JSON.parse(confirmText); +    } catch {} +    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) { +      confirmOk = confirmJson.ok === true;      }      if (!confirmOk) {        await testInfo.attach("planner-trace.txt", { @@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          contentType: "text/plain",        });      } +    await testInfo.attach("post-trace.txt", { +      body: postTrace.join("\n"), +      contentType: "text/plain", +    });    }  });
++-+diff --git a/othello_ui.html b/othello_ui.html
++-+index 4ed3660c..f53dba97 100644
++-+--- a/othello_ui.html
++-++++ b/othello_ui.html
++-+@@ -3073,14 +3073,30 @@
++-+ 
++-+     async function fetchTodayBrief() {
++-+       const resp = await fetch("/api/today-brief", { credentials: "include" });
++-+-      if (resp.status === 401 || resp.status === 403) {
++-++      const status = resp.status;
++-++      const text = await resp.text();
++-++      if (status === 401 || status === 403) {
++-+         const err = new Error("Unauthorized");
++-+-        err.status = resp.status;
++-++        err.status = status;
++-+         throw err;
++-+       }
++-+-      if (!resp.ok) throw new Error("Failed to load brief");
++-+-      const data = await resp.json();
++-+-      return data.brief || {};
++-++      if (!resp.ok) {
++-++        const err = new Error("Failed to load brief");
++-++        err.status = status;
++-++        err.bodySnippet = text.slice(0, 300);
++-++        throw err;
++-++      }
++-++      let data = null;
++-++      try {
++-++        data = JSON.parse(text);
++-++      } catch (parseErr) {
++-++        const err = new Error("Failed to parse brief");
++-++        err.status = status;
++-++        err.bodySnippet = text.slice(0, 300);
++-++        err.parseError = parseErr.message;
++-++        throw err;
++-++      }
++-++      return (data && data.brief) || {};
++-+     }
++-+ 
++-+     async function fetchTodayPlan() {
++-+@@ -3206,13 +3222,21 @@
++-+           if (!suggestion || !suggestion.id) return;
++-+           confirmBtn.disabled = true;
++-+           try {
++-++            const confirmPayload = { reason: "confirm" };
++-++            if (BOOT_DEBUG) {
++-++              console.info("[Today Planner] confirm suggestion", {
++-++                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
++-++                method: "POST",
++-++                payloadKeys: Object.keys(confirmPayload),
++-++              });
++-++            }
++-+             await v1Request(
++-+               `/v1/suggestions/${suggestion.id}/accept`,
++-+               {
++-+                 method: "POST",
++-+                 headers: { "Content-Type": "application/json" },
++-+                 credentials: "include",
++-+-                body: JSON.stringify({ reason: "confirm" })
++-++                body: JSON.stringify(confirmPayload)
++-+               },
++-+               "Confirm suggestion"
++-+             );
++-+@@ -3359,11 +3383,16 @@
++-+       });
++-+     }
++-+ 
++-+-    function renderPlannerError(message, httpStatus) {
++-++    function renderPlannerError(message, httpStatus, details) {
++-+       plannerError.style.display = "block";
++-+       let msg = message || "Could not load today's plan. Please try again later.";
++-+       if (httpStatus) msg += ` (HTTP ${httpStatus})`;
++-+       plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
++-++      if (details) {
++-++        plannerError.dataset.error = details;
++-++      } else {
++-++        delete plannerError.dataset.error;
++-++      }
++-+       const retryBtn = document.getElementById("planner-retry-btn");
++-+       if (retryBtn) {
++-+         retryBtn.onclick = () => {
++-+@@ -5067,16 +5096,50 @@
++-+           };
++-+       }
++-+ 
++-++      let planStatus = null;
++-++      let planSnippet = null;
++-++      let planParseError = null;
++-++      let briefStatus = null;
++-++      let briefSnippet = null;
++-++      let briefParseError = null;
++-++      let planUrl = null;
++-+       try {
++-+-        const planUrl = dayViewDateYmd 
++-++        planUrl = dayViewDateYmd 
++-+             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
++-+             : `/api/today-plan?ts=${Date.now()}`;
++-+-            
++-+-        const [brief, planResp] = await Promise.all([
++-+-            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days
++-+-            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json())
++-+-        ]);
++-+-        
++-++        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
++-++          briefStatus = err && err.status ? err.status : null;
++-++          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
++-++          briefParseError = err && err.parseError ? err.parseError : null;
++-++          console.error("[Today Planner] fetchTodayBrief failed", {
++-++            status: briefStatus,
++-++            parseError: briefParseError,
++-++            error: err && err.message,
++-++          });
++-++          return {};
++-++        });
++-++        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
++-++        planStatus = planResponse.status;
++-++        const planText = await planResponse.text();
++-++        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
++-++        if (!planResponse.ok) {
++-++          const err = new Error("Failed to load plan");
++-++          err.status = planStatus;
++-++          err.bodySnippet = planSnippet;
++-++          throw err;
++-++        }
++-++        let planResp = null;
++-++        try {
++-++          planResp = JSON.parse(planText);
++-++        } catch (parseErr) {
++-++          planParseError = parseErr.message;
++-++          const err = new Error("Failed to parse plan");
++-++          err.status = planStatus;
++-++          err.bodySnippet = planSnippet;
++-++          err.parseError = planParseError;
++-++          throw err;
++-++        }
++- +
++--+Artifacts:
++--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
++--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
++--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
++--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
++--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
++--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
++-+         const plan = planResp.plan || {};
++-+         const goalTasks = (plan.sections?.goal_tasks || []);
++-+         if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
++-+@@ -5103,7 +5166,25 @@
++-+           const match = e.message.match(/HTTP (\d+)/);
++-+           if (match) httpStatus = match[1];
++-+         }
++-+-        renderPlannerError("Planner load failed", httpStatus);
++-++        if (e && e.status) httpStatus = e.status;
++-++        const detailParts = [];
++-++        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
++-++        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
++-++        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
++-++        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
++-++        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
++-++        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
++-++        if (e && e.message) detailParts.push(`error:${e.message}`);
++-++        const detailString = detailParts.join(" | ").slice(0, 300);
++-++        console.error("[Today Planner] loadTodayPlanner failed", {
++-++          planUrl,
++-++          planStatus,
++-++          briefStatus,
++-++          planParseError,
++-++          briefParseError,
++-++          error: e && e.message,
++-++        });
++-++        renderPlannerError("Planner load failed", httpStatus, detailString);
++-+         if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
++-+       }
++-+     }
++- diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
++--index 5abbeab8..e7e992f5 100644
++-+index e7e992f5..d48e604d 100644
++- --- a/tests/e2e/othello.todayplanner.routines.spec.js
++- +++ b/tests/e2e/othello.todayplanner.routines.spec.js
++--@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
++-- const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
++-- const STEP_TITLES = ["Breakfast", "Shower"];
++-- 
++---async function login(page, accessCode) {
++--+async function recordAuthTrace(label, response, authTrace) {
++--+  let status = "NO_RESPONSE";
++--+  let bodyText = "";
++--+  if (response) {
++--+    status = response.status();
++--+    try {
++--+      bodyText = await response.text();
++--+    } catch (err) {
++--+      bodyText = `READ_ERROR: ${err.message}`;
++--+    }
++--+  }
++--+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
++--+  authTrace.push(`${label} ${status} ${snippet}`);
++--+  return { status, snippet, text: bodyText };
++--+}
++--+
++--+async function login(page, accessCode, baseURL, testInfo, authTrace) {
++--   const loginInput = page.locator("#login-pin");
++--   const loginOverlay = page.locator("#login-overlay");
++---  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
++--+  const loginForm = page.locator("#loginForm");
++--+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
++--+    failOnStatusCode: false,
++--+  });
++--+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
++--+  let preAuthData = null;
++--+  try {
++--+    preAuthData = JSON.parse(preAuthResult.text || "");
++--+  } catch {}
++--+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
++--   if (needsLogin) {
++--+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
++--+    const loginResponsePromise = page.waitForResponse(
++--+      (response) => response.url().includes("/api/auth/login"),
++--+      { timeout: 20000 }
++--+    ).catch(() => null);
++--     await loginInput.fill(accessCode);
++--     await page.locator("#login-btn").click();
++--+    const loginResponse = await loginResponsePromise;
++--+    if (loginResponse) {
++--+      await recordAuthTrace("auth/login", loginResponse, authTrace);
++--+    } else {
++--+      authTrace.push("auth/login NO_RESPONSE");
++--+    }
++--   }
++---  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
++--+
++--+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
++--+    failOnStatusCode: false,
++--+  });
++--+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
++--+  let meData = null;
++--+  try {
++--+    meData = JSON.parse(meResult.text || "");
++--+  } catch {}
++--+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
++--+
++--+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
++--+    failOnStatusCode: false,
++--+  });
++--+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
++--+
++--+  if (meResult.status !== 200 || !isAuthed) {
++--+    await testInfo.attach("auth-debug.txt", {
++--+      body: authTrace.join("\n"),
++--+      contentType: "text/plain",
++--+    });
++--+    throw new Error(
++--+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
++--+    );
++--+  }
++--+
++--   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
++--+  const overlayCount = await loginOverlay.count();
++--+  if (overlayCount > 0) {
++--+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
++--+  } else {
++--+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
++--+  }
++--+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
++-- }
++-- 
++-- async function switchMode(page, label) {
++--@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-- 
++--   const serverErrors = [];
++-+@@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-    const consoleErrors = [];
++--+  const authTrace = [];
++--+  const plannerTrace = [];
++-+   const authTrace = [];
++-+   const plannerTrace = [];
++-++  const postTrace = [];
++-  
++-    page.on("response", (response) => {
++-      if (response.status() >= 500) {
++--@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++--     }
++-+@@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+       || url.includes("/v1/plan/draft")
++-+       || url.includes("/api/confirm")
++-+       || url.includes("/v1/confirm")
++-++      || url.includes("/v1/suggestions/")
++-+       || url.includes("/api/plan/update")
++-+     );
++-+     if (!matchesPlanner) return;
++-+@@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+     plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
++-    });
++-  
++--+  page.on("response", async (response) => {
++--+    const url = response.url();
++--+    const matchesPlanner = (
++--+      url.includes("/api/today-plan")
++--+      || url.includes("/api/today-brief")
++--+      || url.includes("/v1/plan/draft")
++--+      || url.includes("/api/confirm")
++-++  page.on("request", (request) => {
++-++    const url = request.url();
++-++    if (request.method() !== "POST") return;
++-++    const matches = (
++-++      url.includes("/api/confirm")
++- +      || url.includes("/v1/confirm")
++-++      || url.includes("/v1/suggestions/")
++- +      || url.includes("/api/plan/update")
++- +    );
++--+    if (!matchesPlanner) return;
++--+    const request = response.request();
++-++    if (!matches) return;
++- +    let path = url;
++- +    try {
++- +      const parsed = new URL(url);
++- +      path = `${parsed.pathname}${parsed.search}`;
++- +    } catch {}
++--+    let bodyText = "";
++--+    try {
++--+      bodyText = await response.text();
++--+    } catch (err) {
++--+      bodyText = `READ_ERROR: ${err.message}`;
++--+    }
++--+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
++--+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
++-++    const postData = request.postData() || "";
++-++    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300);
++-++    postTrace.push(`${request.method()} ${path} ${snippet}`);
++- +  });
++- +
++-    page.on("console", (msg) => {
++-      if (msg.type() === "error") {
++-        consoleErrors.push(msg.text());
++--@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++--     consoleErrors.push(`pageerror: ${err.message}`);
++--   });
++-- 
++---  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
++---  await login(page, accessCode);
++--+  try {
++--+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
++--+    await login(page, accessCode, baseURL, testInfo, authTrace);
++-- 
++---  await switchMode(page, "Routine Planner");
++---  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
++--+    await switchMode(page, "Routine Planner");
++--+    await page.locator("#middle-tab").click();
++--+    await expect(page.locator("#routine-planner-view")).toBeVisible();
++-- 
++---  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
++---  await page.locator("#routine-add-btn").click();
++---  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
++--+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
++--+    await page.locator("#routine-add-btn").click();
++--+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
++-- 
++---  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
++--+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
++-- 
++---  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
++---  for (const day of days) {
++---    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
++---      .locator("input[type=checkbox]")
++---      .check();
++---  }
++--+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
++--+    for (const day of days) {
++--+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
++--+        .locator("input[type=checkbox]")
++--+        .check();
++--+    }
++-- 
++---  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
++---  await expect(timeInputs.first()).toBeVisible();
++---  await timeInputs.first().fill("06:00");
++--+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
++--+    await expect(timeInputs.first()).toBeVisible();
++--+    await timeInputs.first().fill("06:00");
++-- 
++---  const addStepBtn = page.locator("#routine-add-step-btn");
++---  await addStepBtn.click();
++---  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
++---  await addStepBtn.click();
++---  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
++--+    const addStepBtn = page.locator("#routine-add-step-btn");
++--+    const stepInputs = page.locator("#routine-steps input[type=text]");
++--+    let stepCount = await stepInputs.count();
++--+    while (stepCount < 2) {
++--+      await addStepBtn.click();
++--+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
++--+      stepCount = await stepInputs.count();
++--+    }
++--+    const emptyIndices = [];
++--+    for (let i = 0; i < stepCount; i++) {
++--+      const value = await stepInputs.nth(i).inputValue();
++--+      if (!value.trim()) {
++--+        emptyIndices.push(i);
++--+      }
++--+    }
++--+    let targetIndices = [];
++--+    if (emptyIndices.length >= 2) {
++--+      targetIndices = emptyIndices.slice(0, 2);
++--+    } else {
++--+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
++--+    }
++--+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
++--+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
++-- 
++---  const stepInputs = page.locator("#routine-steps input[type=text]");
++---  await stepInputs.nth(0).fill(STEP_TITLES[0]);
++---  await stepInputs.nth(1).fill(STEP_TITLES[1]);
++--+    await page.locator("#routine-save-btn").click();
++--+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
++-- 
++---  await page.locator("#routine-save-btn").click();
++---  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
++--+    await switchMode(page, "Today Planner");
++-- 
++---  await switchMode(page, "Today Planner");
++--+    await page.locator("#middle-tab").click();
++--+    await expect(page.locator("#today-planner-view")).toBeVisible();
++--+    const plannerFailedBanner = page.getByText("Planner load failed");
++--+    const plannerLoadResult = await Promise.race([
++--+      page.waitForResponse(
++--+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
++--+        { timeout: 20000 }
++--+      ).then(() => "ok").catch(() => null),
++--+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
++--+    ]);
++--+    if (plannerLoadResult !== "ok") {
++--+      await testInfo.attach("planner-trace.txt", {
++--+        body: plannerTrace.join("\n"),
++--+        contentType: "text/plain",
++--+      });
++--+      await testInfo.attach("console-errors.txt", {
++--+        body: consoleErrors.join("\n"),
++--+        contentType: "text/plain",
++--+      });
++--+      if (plannerLoadResult === "fail") {
++--+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
++-+@@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+         body: consoleErrors.join("\n"),
++-+         contentType: "text/plain",
++-+       });
++-++      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error");
++-++      if (plannerErrorDetails) {
++-++        await testInfo.attach("planner-error.txt", {
++-++          body: plannerErrorDetails,
++-++          contentType: "text/plain",
++-++        });
++- +      }
++--+      throw new Error("Planner load did not complete; see planner-trace.txt");
++--+    }
++--+    await expect(page.locator("#build-plan-btn")).toBeVisible();
++--+    await page.locator("#build-plan-btn").click();
++-- 
++---  await page.locator("#middle-tab").click();
++---  await expect(page.locator("#today-planner-view")).toBeVisible();
++---  await expect(page.locator("#build-plan-btn")).toBeVisible();
++---  await page.locator("#build-plan-btn").click();
++--+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
++--+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
++--+    const pendingCount = await suggestionsList.count();
++-- 
++---  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
++---  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
++---  const pendingCount = await suggestionsList.count();
++--+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
++--+    if (await targetCard.count() === 0) {
++--+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
++--+    }
++--+    const targetCount = await targetCard.count();
++--+    expect(
++--+      targetCount,
++--+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
++--+    ).toBeGreaterThan(0);
++-- 
++---  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
++---  if (await targetCard.count() === 0) {
++---    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
++---  }
++---  const targetCount = await targetCard.count();
++---  expect(
++---    targetCount,
++---    "Expected at least one routine-related suggestion (name match or routine- fallback)."
++---  ).toBeGreaterThan(0);
++---
++---  targetCard = targetCard.first();
++---  let selectedTitle = "";
++---  const titleLocator = targetCard.locator(".planner-block__title");
++---  if (await titleLocator.count()) {
++---    selectedTitle = (await titleLocator.first().innerText()).trim();
++---  }
++---  if (!selectedTitle) {
++---    selectedTitle = ((await targetCard.textContent()) || "").trim();
++---  }
++---  await targetCard.getByRole("button", { name: "Confirm" }).click();
++---
++---  await expect
++---    .poll(
++---      async () => {
++---        const currentCount = await suggestionsList.count();
++---        if (currentCount < pendingCount) return true;
++---        if (selectedTitle) {
++---          const panelText = await page.locator("#today-plan-suggestions").textContent();
++---          return panelText ? !panelText.includes(selectedTitle) : false;
++---        }
++---        return false;
++--+    targetCard = targetCard.first();
++--+    let selectedTitle = "";
++--+    const titleLocator = targetCard.locator(".planner-block__title");
++--+    if (await titleLocator.count()) {
++--+      selectedTitle = (await titleLocator.first().innerText()).trim();
++--+    }
++--+    if (!selectedTitle) {
++--+      selectedTitle = ((await targetCard.textContent()) || "").trim();
++--+    }
++--+    const confirmResponsePromise = page.waitForResponse(
++--+      (response) => {
++--+        const url = response.url();
++--+        if (response.request().method() !== "POST") return false;
++--+        return url.includes("/confirm") || url.includes("/plan/update");
++-+       if (plannerLoadResult === "fail") {
++-+         throw new Error("Planner load failed banner displayed; see planner-trace.txt");
++-+       }
++-+@@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+       (response) => {
++-+         const url = response.url();
++-+         if (response.request().method() !== "POST") return false;
++-+-        return url.includes("/confirm") || url.includes("/plan/update");
++-++        return url.includes("/v1/suggestions/") && url.includes("/accept");
++-        },
++-        { timeout: 20000 }
++---    )
++---    .toBe(true);
++---
++---  const todayPlanItems = page.locator("#today-plan-items");
++---  await expect(todayPlanItems).toBeVisible();
++---  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
++---  if (selectedTitle && planText && planText.includes(selectedTitle)) {
++---    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
++---  } else {
++---    await expect
++---      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
++---      .toBeGreaterThan(0);
++---  }
++--+    );
++--+    await targetCard.getByRole("button", { name: "Confirm" }).click();
++--+    const confirmResponse = await confirmResponsePromise;
++--+    let confirmText = "";
++-+     );
++-+@@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+       confirmText = await confirmResponse.text();
++-+     } catch {}
++-+     let confirmOk = confirmResponse.status() === 200;
++-+-    if (confirmText.includes("\"ok\":")) {
++-+-      confirmOk = confirmText.includes("\"ok\":true");
++-++    let confirmJson = null;
++- +    try {
++--+      confirmText = await confirmResponse.text();
++-++      confirmJson = JSON.parse(confirmText);
++- +    } catch {}
++--+    let confirmOk = confirmResponse.status() === 200;
++--+    if (confirmText.includes("\"ok\":")) {
++--+      confirmOk = confirmText.includes("\"ok\":true");
++--+    }
++--+    if (!confirmOk) {
++--+      await testInfo.attach("planner-trace.txt", {
++--+        body: plannerTrace.join("\n"),
++--+        contentType: "text/plain",
++--+      });
++--+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
++--+    }
++-- 
++---  if (consoleErrors.length) {
++---    await testInfo.attach("console-errors.txt", {
++---      body: consoleErrors.join("\n"),
++---      contentType: "text/plain",
++---    });
++---  }
++--+    await page.locator("#middle-tab").click();
++--+    await expect(page.locator("#today-planner-view")).toBeVisible();
++-- 
++---  if (serverErrors.length) {
++---    await testInfo.attach("server-500s.txt", {
++---      body: serverErrors.join("\n"),
++---      contentType: "text/plain",
++---    });
++---  }
++--+    const todayPlanItems = page.locator("#today-plan-items");
++--+    await expect(todayPlanItems).toBeVisible();
++--+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
++--+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
++--+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
++--+    } else {
++--+      await expect
++--+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
++--+        .toBeGreaterThan(0);
++--+    }
++-- 
++---  const criticalConsoleErrors = consoleErrors.filter((entry) => (
++---    entry.includes("Uncaught") || entry.includes("TypeError")
++---  ));
++---  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
++---  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
++--+    if (consoleErrors.length) {
++--+      await testInfo.attach("console-errors.txt", {
++--+        body: consoleErrors.join("\n"),
++--+        contentType: "text/plain",
++--+      });
++--+    }
++--+
++--+    if (serverErrors.length) {
++--+      await testInfo.attach("server-500s.txt", {
++--+        body: serverErrors.join("\n"),
++--+        contentType: "text/plain",
++--+      });
++--+    }
++--+
++--+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
++--+      entry.includes("Uncaught") || entry.includes("TypeError")
++--+    ));
++--+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
++--+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
++--+  } finally {
++--+    if (plannerTrace.length) {
++--+      await testInfo.attach("planner-trace.txt", {
++--+        body: plannerTrace.join("\n"),
++--+        contentType: "text/plain",
++--+      });
++--+    }
++--+  }
++-++    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) {
++-++      confirmOk = confirmJson.ok === true;
++-+     }
++-+     if (!confirmOk) {
++-+       await testInfo.attach("planner-trace.txt", {
++-+@@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-+         contentType: "text/plain",
++-+       });
++-+     }
++-++    await testInfo.attach("post-trace.txt", {
++-++      body: postTrace.join("\n"),
++-++      contentType: "text/plain",
++-++    });
++-+   }
++-  });
 +-+
-+-+Artifacts:
-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+++Planned: Gate planner/week/routine fetches; add single poller + abort handling; add debug logging; run py_compile; update evidence
+++Completed: Gated planner/week/routine loads; added poller control + aborts; added debug logs; ran py_compile api.py
+++Remaining: Manual UI verification and commit checkpoint
+++Next Action: Run the How to verify steps, then git status/diff/add and commit the intended files
+++How to verify:
+++- Open app and stay in Chat for 30s; Network should not show today-brief/today-plan/week/routines spam
+++- Switch to Today Planner; it should fetch once and start polling
+++- Switch back to Chat; polling stops and planner calls end
+++- Open week drilldown; it should fetch once and stop on close
++ diff --git a/othello_ui.html b/othello_ui.html
++-index 4ed3660c..f53dba97 100644
+++index f53dba97..827acd1b 100644
++ --- a/othello_ui.html
++ +++ b/othello_ui.html
++-@@ -3073,14 +3073,30 @@
+++@@ -3071,8 +3071,8 @@
+++       return formatDateYYYYMMDD(d);
+++     }
+   
+-  Commands:
+---- npm install
+---- npx playwright install --with-deps
+-  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
+---- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
+--+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
+-+-- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
++-     async function fetchTodayBrief() {
++-       const resp = await fetch("/api/today-brief", { credentials: "include" });
++--      if (resp.status === 401 || resp.status === 403) {
++-+      const status = resp.status;
++-+      const text = await resp.text();
++-+      if (status === 401 || status === 403) {
++-         const err = new Error("Unauthorized");
++--        err.status = resp.status;
++-+        err.status = status;
++-         throw err;
+++-    async function fetchTodayBrief() {
+++-      const resp = await fetch("/api/today-brief", { credentials: "include" });
++++    async function fetchTodayBrief(signal) {
++++      const resp = await fetch("/api/today-brief", { credentials: "include", signal });
+++       const status = resp.status;
+++       const text = await resp.text();
+++       if (status === 401 || status === 403) {
+++@@ -3148,14 +3148,18 @@
+++       }
+++       return payload;
+++     }
+++-    async function fetchV1TodayPlan() {
+++-      const payload = await v1Request("/v1/read/today", { cache: "no-store", credentials: "include" }, "Today plan");
++++    async function fetchV1TodayPlan(signal) {
++++      const payload = await v1Request(
++++        "/v1/read/today",
++++        { cache: "no-store", credentials: "include", signal },
++++        "Today plan"
++++      );
+++       return payload?.data?.plan || {};
+++     }
+++-    async function fetchPlanItemSuggestions() {
++++    async function fetchPlanItemSuggestions(signal) {
+++       const payload = await v1Request(
+++         "/v1/suggestions?status=pending&kind=plan_item&limit=20",
+++-        { credentials: "include" },
++++        { credentials: "include", signal },
+++         "Plan suggestions"
+++       );
+++       return Array.isArray(payload?.data?.suggestions) ? payload.data.suggestions : [];
+++@@ -3291,13 +3295,22 @@
+++       }
+++       return { payload: { include_rollover: true }, note: "No recent chat message found; drafting from rollover only." };
+++     }
+++-    async function loadTodayPlanPanel() {
++++    async function loadTodayPlanPanel(signal) {
++++      if (othelloState.currentView !== "today-planner") return;
++++      if (document.hidden) return;
+++       if (!todayPlanItems || !todayPlanSuggestions) return;
+++       clearTodayPlanError();
++++      let panelSignal = signal;
++++      if (!panelSignal) {
++++        abortPlannerRequests("panel-reload");
++++        plannerAbort = new AbortController();
++++        panelSignal = plannerAbort.signal;
++++      }
+++       try {
+++-        const plan = await fetchV1TodayPlan();
++++        const plan = await fetchV1TodayPlan(panelSignal);
+++         renderTodayPlanItems(plan);
+++       } catch (e) {
++++        if (isAbortError(e)) return;
+++         if (e && (e.status === 401 || e.status === 403)) {
+++           await handleUnauthorized('today-plan-read');
+++           return;
+++@@ -3305,9 +3318,10 @@
+++         setTodayPlanError(e && e.message ? e.message : "Failed to load today plan.", e && e.requestId ? e.requestId : null);
++        }
++--      if (!resp.ok) throw new Error("Failed to load brief");
++--      const data = await resp.json();
++--      return data.brief || {};
++-+      if (!resp.ok) {
++-+        const err = new Error("Failed to load brief");
++-+        err.status = status;
++-+        err.bodySnippet = text.slice(0, 300);
++-+        throw err;
+++       try {
+++-        const suggestions = await fetchPlanItemSuggestions();
++++        const suggestions = await fetchPlanItemSuggestions(panelSignal);
+++         renderPlanSuggestions(suggestions);
+++       } catch (e) {
++++        if (isAbortError(e)) return;
+++         if (e && (e.status === 401 || e.status === 403)) {
+++           await handleUnauthorized('today-plan-suggestions');
+++           return;
+++@@ -4564,6 +4578,66 @@
+++     const weekViewCache = {}; 
+++     let isWeekViewActive = false;
+++     let dayViewDateYmd = null; // null means "today/live"
++++    let plannerPollId = null;
++++    let plannerAbort = null;
++++    let weekAbort = null;
++++    let routinesAbort = null;
++++    let activeWeekDrilldownYmd = null;
++++    let plannerListenersBound = false;
++++    const PLANNER_POLL_MS = 60000;
++++
++++    function isAbortError(err) {
++++      return err && (err.name === "AbortError" || err.code === 20);
++++    }
++++
++++    function logPlannerDebug(message, payload) {
++++      if (!BOOT_DEBUG) return;
++++      if (payload) {
++++        console.log(message, payload);
++++      } else {
++++        console.log(message);
++ +      }
++-+      let data = null;
++-+      try {
++-+        data = JSON.parse(text);
++-+      } catch (parseErr) {
++-+        const err = new Error("Failed to parse brief");
++-+        err.status = status;
++-+        err.bodySnippet = text.slice(0, 300);
++-+        err.parseError = parseErr.message;
++-+        throw err;
++++    }
++++
++++    function abortPlannerRequests(reason) {
++++      if (!plannerAbort) return;
++++      plannerAbort.abort();
++++      plannerAbort = null;
++++      logPlannerDebug("[Today Planner] aborted in-flight request", { reason });
++++    }
++++
++++    function abortWeekRequests(reason) {
++++      if (!weekAbort) return;
++++      weekAbort.abort();
++++      weekAbort = null;
++++      logPlannerDebug("[Week View] aborted in-flight request", { reason });
++++    }
++++
++++    function abortRoutineRequests(reason) {
++++      if (!routinesAbort) return;
++++      routinesAbort.abort();
++++      routinesAbort = null;
++++      logPlannerDebug("[Routine Planner] aborted in-flight request", { reason });
++++    }
++++
++++    function stopPlannerPolling(reason) {
++++      if (plannerPollId) {
++++        clearInterval(plannerPollId);
++++        plannerPollId = null;
++++        logPlannerDebug("[Today Planner] polling stopped", { reason });
++ +      }
++-+      return (data && data.brief) || {};
++-     }
++++    }
++++
++++    function startPlannerPolling() {
++++      stopPlannerPolling("restart");
++++      if (!PLANNER_POLL_MS || PLANNER_POLL_MS < 1000) return;
++++      plannerPollId = setInterval(() => {
++++        if (document.hidden) return;
++++        if (othelloState.currentView !== "today-planner") return;
++++        loadTodayPlanner();
++++      }, PLANNER_POLL_MS);
++++      logPlannerDebug("[Today Planner] polling started", { intervalMs: PLANNER_POLL_MS });
++++    }
+   
+-  Env Vars:
+-  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
+-  - OTHELLO_ACCESS_CODE=******69
++-     async function fetchTodayPlan() {
++-@@ -3206,13 +3222,21 @@
++-           if (!suggestion || !suggestion.id) return;
++-           confirmBtn.disabled = true;
++-           try {
++-+            const confirmPayload = { reason: "confirm" };
++-+            if (BOOT_DEBUG) {
++-+              console.info("[Today Planner] confirm suggestion", {
++-+                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
++-+                method: "POST",
++-+                payloadKeys: Object.keys(confirmPayload),
++-+              });
++-+            }
++-             await v1Request(
++-               `/v1/suggestions/${suggestion.id}/accept`,
++-               {
++-                 method: "POST",
++-                 headers: { "Content-Type": "application/json" },
++-                 credentials: "include",
++--                body: JSON.stringify({ reason: "confirm" })
++-+                body: JSON.stringify(confirmPayload)
++-               },
++-               "Confirm suggestion"
++-             );
++-@@ -3359,11 +3383,16 @@
++-       });
+++     function getWeekStartYmd(refDate = new Date()) {
+++       // Monday-start, local time
+++@@ -4641,12 +4715,18 @@
+++         return { completed, inProgress, overdue, snoozed, tomorrow };
++      }
+   
+--+Auth probe summary (manual):
+--+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
+--+- /api/today-brief -> 200 {"brief":{...}}
+--+- /api/today-plan -> 200 {"plan":{...}}
+--+
+-- Result: FAIL
+-+-Auth probe summary (manual):
+-+-- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
+-+-- /api/today-brief -> 200 {"brief":{...}}
+-+-- /api/today-plan -> 200 {"plan":{...}}
+-++Planner load instrumentation:
+-++- Planner load failed banner: NOT observed in passing run
+-++- fetchTodayBrief failure is now non-fatal (logs only)
++--    function renderPlannerError(message, httpStatus) {
++-+    function renderPlannerError(message, httpStatus, details) {
++-       plannerError.style.display = "block";
++-       let msg = message || "Could not load today's plan. Please try again later.";
++-       if (httpStatus) msg += ` (HTTP ${httpStatus})`;
++-       plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
++-+      if (details) {
++-+        plannerError.dataset.error = details;
++-+      } else {
++-+        delete plannerError.dataset.error;
++-+      }
++-       const retryBtn = document.getElementById("planner-retry-btn");
++-       if (retryBtn) {
++-         retryBtn.onclick = () => {
++-@@ -5067,16 +5096,50 @@
++-           };
+++-    async function fetchPlanForDate(ymd) {
++++    async function fetchPlanForDate(ymd, options = {}) {
++++      const { signal, source } = options;
++++      if (othelloState.currentView !== "today-planner") return null;
++++      if (!isWeekViewActive && source !== "drilldown") return null;
+++       if (weekViewCache[ymd]) return weekViewCache[ymd];
+++       
+++       try {
+++         // Use peek=1 to prevent generation/mutation of plans during week view browsing
+++-        const resp = await fetch(`/api/today-plan?plan_date=${ymd}&peek=1`, { cache: "no-store", credentials: "include" });
++++        const resp = await fetch(
++++          `/api/today-plan?plan_date=${ymd}&peek=1`,
++++          { cache: "no-store", credentials: "include", signal }
++++        );
+++         if (!resp.ok) throw new Error("Failed to fetch");
+++         const data = await resp.json();
+++         const plan = data.plan || {};
+++@@ -4655,19 +4735,34 @@
+++         weekViewCache[ymd] = { plan, counts, fetchedAt: Date.now() };
+++         return weekViewCache[ymd];
+++       } catch (e) {
++++        if (isAbortError(e)) {
++++          logPlannerDebug("[Week View] fetch aborted", { ymd });
++++          return null;
++++        }
+++         console.error(`Failed to fetch plan for ${ymd}`, e);
+++         return null;
++        }
+++     }
++  
++-+      let planStatus = null;
++-+      let planSnippet = null;
++-+      let planParseError = null;
++-+      let briefStatus = null;
++-+      let briefSnippet = null;
++-+      let briefParseError = null;
++-+      let planUrl = null;
++-       try {
++--        const planUrl = dayViewDateYmd 
++-+        planUrl = dayViewDateYmd 
++-             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
++-             : `/api/today-plan?ts=${Date.now()}`;
++--            
++--        const [brief, planResp] = await Promise.all([
++--            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days
++--            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json())
++--        ]);
+++     async function loadWeekView() {
++++        if (othelloState.currentView !== "today-planner") return;
++++        if (!isWeekViewActive) return;
++++        if (document.hidden) return;
++++        
+++         const container = document.getElementById("week-view-content");
+++-        if (!container) return;
++++        const weekView = document.getElementById("planner-week-view");
++++        if (!container || (weekView && weekView.style.display === "none")) return;
+++         container.innerHTML = '<div style="padding:1rem; text-align:center; color:var(--text-soft);">Loading week...</div>';
+++         
++++        abortWeekRequests("week-view-reload");
++++        weekAbort = new AbortController();
++++        const { signal } = weekAbort;
++++        logPlannerDebug("[Week View] loadWeekView invoked", { view: othelloState.currentView });
++++        
+++         const days = getWeekDays();
+++-        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd)));
++++        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd, { signal })));
+++         
++++        if (signal.aborted) return;
+++         container.innerHTML = '';
+++         
+++         results.forEach((res, idx) => {
+++@@ -4738,12 +4833,26 @@
+++         return items;
+++     }
+ + 
+-+-Result: FAIL
+-++Confirm endpoint:
+-++- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})
+++-    async function openWeekDrilldown(ymd) {
+++-        const res = await fetchPlanForDate(ymd);
+++-        if (!res) return;
++ -        
++-+        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
++-+          briefStatus = err && err.status ? err.status : null;
++-+          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
++-+          briefParseError = err && err.parseError ? err.parseError : null;
++-+          console.error("[Today Planner] fetchTodayBrief failed", {
++-+            status: briefStatus,
++-+            parseError: briefParseError,
++-+            error: err && err.message,
++-+          });
++-+          return {};
++-+        });
++-+        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
++-+        planStatus = planResponse.status;
++-+        const planText = await planResponse.text();
++-+        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
++-+        if (!planResponse.ok) {
++-+          const err = new Error("Failed to load plan");
++-+          err.status = planStatus;
++-+          err.bodySnippet = planSnippet;
++-+          throw err;
++-+        }
++-+        let planResp = null;
++-+        try {
++-+          planResp = JSON.parse(planText);
++-+        } catch (parseErr) {
++-+          planParseError = parseErr.message;
++-+          const err = new Error("Failed to parse plan");
++-+          err.status = planStatus;
++-+          err.bodySnippet = planSnippet;
++-+          err.parseError = planParseError;
++-+          throw err;
++-+        }
++++    function closeWeekDrilldown() {
+++         const existing = document.getElementById("planner-week-drilldown");
+++         if (existing) existing.remove();
++++        activeWeekDrilldownYmd = null;
++++    }
++ +
++-         const plan = planResp.plan || {};
++-         const goalTasks = (plan.sections?.goal_tasks || []);
++-         if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
++-@@ -5103,7 +5166,25 @@
++-           const match = e.message.match(/HTTP (\d+)/);
++-           if (match) httpStatus = match[1];
++++    async function openWeekDrilldown(ymd) {
++++        if (othelloState.currentView !== "today-planner") return;
++++        if (activeWeekDrilldownYmd === ymd && document.getElementById("planner-week-drilldown")) return;
++++        activeWeekDrilldownYmd = ymd;
++++        
++++        abortWeekRequests("week-drilldown");
++++        weekAbort = new AbortController();
++++        const res = await fetchPlanForDate(ymd, { signal: weekAbort.signal, source: "drilldown" });
++++        if (!res) {
++++            activeWeekDrilldownYmd = null;
++++            return;
++++        }
++++        
++++        closeWeekDrilldown();
+++         
+++         const modal = document.createElement("div");
+++         modal.id = "planner-week-drilldown";
+++@@ -4754,7 +4863,7 @@
+++         modal.style.display = "flex";
+++         modal.style.alignItems = "center";
+++         modal.style.justifyContent = "center";
+++-        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
++++        modal.onclick = (e) => { if (e.target === modal) closeWeekDrilldown(); };
+++         
+++         const card = document.createElement("div");
+++         card.className = "planner-card";
+++@@ -4777,7 +4886,7 @@
+++                     <div class="planner-section__title" style="font-size:1.1rem;">${dateStr}</div>
+++                     <div style="font-size:0.85rem; color:var(--text-soft); margin-top:0.2rem;">${summary}</div>
+++                 </div>
+++-                <button class="icon-button" style="border:none; background:transparent;" onclick="document.getElementById('planner-week-drilldown').remove()">ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢</button>
++++                <button class="icon-button" style="border:none; background:transparent;" onclick="closeWeekDrilldown()">ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢</button>
+++             </div>
+++             <div style="flex:1; overflow-y:auto; padding-right:0.5rem;" id="drilldown-list"></div>
+++             <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid var(--border); text-align:center;">
+++@@ -4864,8 +4973,8 @@
+++ 
+++     function openDayViewForDate(ymd) {
+++         dayViewDateYmd = ymd;
+++-        const modal = document.getElementById("planner-week-drilldown");
+++-        if (modal) modal.remove();
++++        closeWeekDrilldown();
++++        abortWeekRequests("day-view-open");
+++         
+++         isWeekViewActive = false;
+++         document.getElementById("planner-week-view").style.display = "none";
+++@@ -4883,6 +4992,7 @@
+++     }
+++ 
+++     function toggleWeekView() {
++++        if (othelloState.currentView !== "today-planner") return;
+++         const weekView = document.getElementById("planner-week-view");
+++         const dayView = document.getElementById("planner-day-view");
+++         const btn = document.getElementById("week-view-toggle");
+++@@ -4898,14 +5008,25 @@
+++             weekView.style.display = "none";
+++             dayView.style.display = "block";
+++             btn.textContent = "Week View";
++++            closeWeekDrilldown();
++++            abortWeekRequests("week-view-close");
++          }
++--        renderPlannerError("Planner load failed", httpStatus);
++-+        if (e && e.status) httpStatus = e.status;
++-+        const detailParts = [];
++-+        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
++-+        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
++-+        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
++-+        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
++-+        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
++-+        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
++-+        if (e && e.message) detailParts.push(`error:${e.message}`);
++-+        const detailString = detailParts.join(" | ").slice(0, 300);
++-+        console.error("[Today Planner] loadTodayPlanner failed", {
++-+          planUrl,
++-+          planStatus,
++-+          briefStatus,
++-+          planParseError,
++-+          briefParseError,
++-+          error: e && e.message,
++-+        });
++-+        renderPlannerError("Planner load failed", httpStatus, detailString);
++-         if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
++-       }
++      }
 +-diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
-+-index 5abbeab8..e7e992f5 100644
++-index e7e992f5..d48e604d 100644
 +---- a/tests/e2e/othello.todayplanner.routines.spec.js
 +-+++ b/tests/e2e/othello.todayplanner.routines.spec.js
-+-@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
-+- const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
-+- const STEP_TITLES = ["Breakfast", "Shower"];
-+- 
-+--async function login(page, accessCode) {
-+-+async function recordAuthTrace(label, response, authTrace) {
-+-+  let status = "NO_RESPONSE";
-+-+  let bodyText = "";
-+-+  if (response) {
-+-+    status = response.status();
-+-+    try {
-+-+      bodyText = await response.text();
-+-+    } catch (err) {
-+-+      bodyText = `READ_ERROR: ${err.message}`;
-+-+    }
-+-+  }
-+-+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
-+-+  authTrace.push(`${label} ${status} ${snippet}`);
-+-+  return { status, snippet, text: bodyText };
-+-+}
-+-+
-+-+async function login(page, accessCode, baseURL, testInfo, authTrace) {
-+-   const loginInput = page.locator("#login-pin");
-+-   const loginOverlay = page.locator("#login-overlay");
-+--  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
-+-+  const loginForm = page.locator("#loginForm");
-+-+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
-+-+    failOnStatusCode: false,
-+-+  });
-+-+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
-+-+  let preAuthData = null;
-+-+  try {
-+-+    preAuthData = JSON.parse(preAuthResult.text || "");
-+-+  } catch {}
-+-+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
-+-   if (needsLogin) {
-+-+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
-+-+    const loginResponsePromise = page.waitForResponse(
-+-+      (response) => response.url().includes("/api/auth/login"),
-+-+      { timeout: 20000 }
-+-+    ).catch(() => null);
-+-     await loginInput.fill(accessCode);
-+-     await page.locator("#login-btn").click();
-+-+    const loginResponse = await loginResponsePromise;
-+-+    if (loginResponse) {
-+-+      await recordAuthTrace("auth/login", loginResponse, authTrace);
-+-+    } else {
-+-+      authTrace.push("auth/login NO_RESPONSE");
-+-+    }
-+-   }
-+--  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
-+-+
-+-+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
-+-+    failOnStatusCode: false,
-+-+  });
-+-+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
-+-+  let meData = null;
-+-+  try {
-+-+    meData = JSON.parse(meResult.text || "");
-+-+  } catch {}
-+-+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
-+-+
-+-+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
-+-+    failOnStatusCode: false,
-+-+  });
-+-+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
-+-+
-+-+  if (meResult.status !== 200 || !isAuthed) {
-+-+    await testInfo.attach("auth-debug.txt", {
-+-+      body: authTrace.join("\n"),
-+-+      contentType: "text/plain",
-+-+    });
-+-+    throw new Error(
-+-+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
-+-+    );
-+-+  }
-+-+
-+-   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
-+-+  const overlayCount = await loginOverlay.count();
-+-+  if (overlayCount > 0) {
-+-+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
-+-+  } else {
-+-+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
-+-+  }
-+-+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
-+- }
-+- 
-+- async function switchMode(page, label) {
-+-@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+- 
-+-   const serverErrors = [];
++-@@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
 +-   const consoleErrors = [];
-+-+  const authTrace = [];
-+-+  const plannerTrace = [];
-+- 
++-   const authTrace = [];
++-   const plannerTrace = [];
++-+  const postTrace = [];
+++     
+++-    // Initialize toggle
+++-    document.addEventListener("DOMContentLoaded", () => {
++++    function bindPlannerListeners() {
++++        if (plannerListenersBound) return;
++++        plannerListenersBound = true;
+++         const btn = document.getElementById("week-view-toggle");
+++         if (btn) btn.onclick = toggleWeekView;
+++-    });
++++        
++++        const toggle = document.getElementById("suggestions-toggle");
++++        if (toggle) toggle.onclick = toggleSuggestions;
++++        
++++        const genBtn = document.getElementById("generate-suggestions-btn");
++++        if (genBtn) genBtn.onclick = generateSuggestions;
++++    }
++++    
++++    document.addEventListener("DOMContentLoaded", bindPlannerListeners);
+   
+---Failure 1 (initial run):
+---- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
+---- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
+---- Artifacts:
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+-+-Failure (attempt #1):
+-+-- Error: Planner load failed banner displayed; see planner-trace.txt
+-+-- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
+- -
+---Failure 2 (rerun after selector change):
+---- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
+---- Secondary: login overlay still visible after 20s (retry #1)
+---- Locations:
+---  - tests/e2e/othello.todayplanner.routines.spec.js:19
+---  - tests/e2e/othello.todayplanner.routines.spec.js:15
+---- Artifacts:
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+---  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+-+-Failure (retry #1):
+-+-- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
+-+-- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
+- -
+---Server 500s: Not evaluated (test timed out before assertion stage).
+---Console errors: Not evaluated; none surfaced in runner output.
+--+Failure (attempt #1):
+--+- Error: Planner load failed banner displayed; see planner-trace.txt
+--+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
+--+
+--+Failure (retry #1):
+--+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
+--+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
+--+
+--+Planner trace highlights:
+--+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+--+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
 +-   page.on("response", (response) => {
 +-     if (response.status() >= 500) {
-+-@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+-     }
++-@@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-       || url.includes("/v1/plan/draft")
++-       || url.includes("/api/confirm")
++-       || url.includes("/v1/confirm")
++-+      || url.includes("/v1/suggestions/")
++-       || url.includes("/api/plan/update")
++-     );
++-     if (!matchesPlanner) return;
++-@@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-     plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
 +-   });
-+- 
-+-+  page.on("response", async (response) => {
-+-+    const url = response.url();
-+-+    const matchesPlanner = (
-+-+      url.includes("/api/today-plan")
-+-+      || url.includes("/api/today-brief")
-+-+      || url.includes("/v1/plan/draft")
-+-+      || url.includes("/api/confirm")
+++     // --- Suggestions Logic ---
+++     
+++@@ -5035,21 +5156,23 @@
+++         }
+++     }
++  
++-+  page.on("request", (request) => {
++-+    const url = request.url();
++-+    if (request.method() !== "POST") return;
++-+    const matches = (
++-+      url.includes("/api/confirm")
 +-+      || url.includes("/v1/confirm")
++-+      || url.includes("/v1/suggestions/")
 +-+      || url.includes("/api/plan/update")
 +-+    );
-+-+    if (!matchesPlanner) return;
-+-+    const request = response.request();
++-+    if (!matches) return;
 +-+    let path = url;
 +-+    try {
 +-+      const parsed = new URL(url);
 +-+      path = `${parsed.pathname}${parsed.search}`;
 +-+    } catch {}
-+-+    let bodyText = "";
-+-+    try {
-+-+      bodyText = await response.text();
-+-+    } catch (err) {
-+-+      bodyText = `READ_ERROR: ${err.message}`;
-+-+    }
-+-+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
-+-+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
++-+    const postData = request.postData() || "";
++-+    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300);
++-+    postTrace.push(`${request.method()} ${path} ${snippet}`);
 +-+  });
-+-+
+ -+
+--+Server 500s: Not captured by Playwright listener on this run.
+--+Critical console errors: Not captured by Playwright listener on this run.
+-+-Planner trace highlights:
+-+-- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+-+-- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
 +-   page.on("console", (msg) => {
 +-     if (msg.type() === "error") {
 +-       consoleErrors.push(msg.text());
-+-@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+-     consoleErrors.push(`pageerror: ${err.message}`);
-+-   });
-+- 
-+--  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
-+--  await login(page, accessCode);
-+-+  try {
-+-+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
-+-+    await login(page, accessCode, baseURL, testInfo, authTrace);
-+- 
-+--  await switchMode(page, "Routine Planner");
-+--  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
-+-+    await switchMode(page, "Routine Planner");
-+-+    await page.locator("#middle-tab").click();
-+-+    await expect(page.locator("#routine-planner-view")).toBeVisible();
-+- 
-+--  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
-+--  await page.locator("#routine-add-btn").click();
-+--  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
-+-+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
-+-+    await page.locator("#routine-add-btn").click();
-+-+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
-+- 
-+--  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
-+-+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
-+- 
-+--  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
-+--  for (const day of days) {
-+--    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
-+--      .locator("input[type=checkbox]")
-+--      .check();
-+--  }
-+-+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
-+-+    for (const day of days) {
-+-+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
-+-+        .locator("input[type=checkbox]")
-+-+        .check();
-+-+    }
-+- 
-+--  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
-+--  await expect(timeInputs.first()).toBeVisible();
-+--  await timeInputs.first().fill("06:00");
-+-+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
-+-+    await expect(timeInputs.first()).toBeVisible();
-+-+    await timeInputs.first().fill("06:00");
-+- 
-+--  const addStepBtn = page.locator("#routine-add-step-btn");
-+--  await addStepBtn.click();
-+--  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
-+--  await addStepBtn.click();
-+--  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
-+-+    const addStepBtn = page.locator("#routine-add-step-btn");
-+-+    const stepInputs = page.locator("#routine-steps input[type=text]");
-+-+    let stepCount = await stepInputs.count();
-+-+    while (stepCount < 2) {
-+-+      await addStepBtn.click();
-+-+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
-+-+      stepCount = await stepInputs.count();
-+-+    }
-+-+    const emptyIndices = [];
-+-+    for (let i = 0; i < stepCount; i++) {
-+-+      const value = await stepInputs.nth(i).inputValue();
-+-+      if (!value.trim()) {
-+-+        emptyIndices.push(i);
-+-+      }
-+-+    }
-+-+    let targetIndices = [];
-+-+    if (emptyIndices.length >= 2) {
-+-+      targetIndices = emptyIndices.slice(0, 2);
-+-+    } else {
-+-+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
-+-+    }
-+-+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
-+-+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
-+- 
-+--  const stepInputs = page.locator("#routine-steps input[type=text]");
-+--  await stepInputs.nth(0).fill(STEP_TITLES[0]);
-+--  await stepInputs.nth(1).fill(STEP_TITLES[1]);
-+-+    await page.locator("#routine-save-btn").click();
-+-+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
-+- 
-+--  await page.locator("#routine-save-btn").click();
-+--  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
-+-+    await switchMode(page, "Today Planner");
-+- 
-+--  await switchMode(page, "Today Planner");
-+-+    await page.locator("#middle-tab").click();
-+-+    await expect(page.locator("#today-planner-view")).toBeVisible();
-+-+    const plannerFailedBanner = page.getByText("Planner load failed");
-+-+    const plannerLoadResult = await Promise.race([
-+-+      page.waitForResponse(
-+-+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
-+-+        { timeout: 20000 }
-+-+      ).then(() => "ok").catch(() => null),
-+-+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
-+-+    ]);
-+-+    if (plannerLoadResult !== "ok") {
-+-+      await testInfo.attach("planner-trace.txt", {
-+-+        body: plannerTrace.join("\n"),
-+-+        contentType: "text/plain",
-+-+      });
-+-+      await testInfo.attach("console-errors.txt", {
-+-+        body: consoleErrors.join("\n"),
-+-+        contentType: "text/plain",
-+-+      });
-+-+      if (plannerLoadResult === "fail") {
-+-+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
-+-+      }
-+-+      throw new Error("Planner load did not complete; see planner-trace.txt");
-+-+    }
-+-+    await expect(page.locator("#build-plan-btn")).toBeVisible();
-+-+    await page.locator("#build-plan-btn").click();
-+- 
-+--  await page.locator("#middle-tab").click();
-+--  await expect(page.locator("#today-planner-view")).toBeVisible();
-+--  await expect(page.locator("#build-plan-btn")).toBeVisible();
-+--  await page.locator("#build-plan-btn").click();
-+-+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
-+-+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
-+-+    const pendingCount = await suggestionsList.count();
-+- 
-+--  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
-+--  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
-+--  const pendingCount = await suggestionsList.count();
-+-+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
-+-+    if (await targetCard.count() === 0) {
-+-+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
-+-+    }
-+-+    const targetCount = await targetCard.count();
-+-+    expect(
-+-+      targetCount,
-+-+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
-+-+    ).toBeGreaterThan(0);
-+- 
-+--  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
-+--  if (await targetCard.count() === 0) {
-+--    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
-+--  }
-+--  const targetCount = await targetCard.count();
-+--  expect(
-+--    targetCount,
-+--    "Expected at least one routine-related suggestion (name match or routine- fallback)."
-+--  ).toBeGreaterThan(0);
-+--
-+--  targetCard = targetCard.first();
-+--  let selectedTitle = "";
-+--  const titleLocator = targetCard.locator(".planner-block__title");
-+--  if (await titleLocator.count()) {
-+--    selectedTitle = (await titleLocator.first().innerText()).trim();
-+--  }
-+--  if (!selectedTitle) {
-+--    selectedTitle = ((await targetCard.textContent()) || "").trim();
-+--  }
-+--  await targetCard.getByRole("button", { name: "Confirm" }).click();
-+--
-+--  await expect
-+--    .poll(
-+--      async () => {
-+--        const currentCount = await suggestionsList.count();
-+--        if (currentCount < pendingCount) return true;
-+--        if (selectedTitle) {
-+--          const panelText = await page.locator("#today-plan-suggestions").textContent();
-+--          return panelText ? !panelText.includes(selectedTitle) : false;
-+--        }
-+--        return false;
-+-+    targetCard = targetCard.first();
-+-+    let selectedTitle = "";
-+-+    const titleLocator = targetCard.locator(".planner-block__title");
-+-+    if (await titleLocator.count()) {
-+-+      selectedTitle = (await titleLocator.first().innerText()).trim();
-+-+    }
-+-+    if (!selectedTitle) {
-+-+      selectedTitle = ((await targetCard.textContent()) || "").trim();
-+-+    }
-+-+    const confirmResponsePromise = page.waitForResponse(
-+-+      (response) => {
-+-+        const url = response.url();
-+-+        if (response.request().method() !== "POST") return false;
-+-+        return url.includes("/confirm") || url.includes("/plan/update");
++-@@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-         body: consoleErrors.join("\n"),
++-         contentType: "text/plain",
++-       });
++-+      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error");
++-+      if (plannerErrorDetails) {
++-+        await testInfo.attach("planner-error.txt", {
++-+          body: plannerErrorDetails,
++-+          contentType: "text/plain",
++-+        });
+++-    // Initialize suggestions
+++-    document.addEventListener("DOMContentLoaded", () => {
+++-        const toggle = document.getElementById("suggestions-toggle");
+++-        if (toggle) toggle.onclick = toggleSuggestions;
+++-        
+++-        const genBtn = document.getElementById("generate-suggestions-btn");
+++-        if (genBtn) genBtn.onclick = generateSuggestions;
+++-    });
+ +-
+-+-Server 500s: Not captured by Playwright listener on this run.
+-+-Critical console errors: Not captured by Playwright listener on this run.
+-++Result: PASS
+-+ 
+-+ Artifacts:
+-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+-+-- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+-++- None (pass run)
+-+diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+-+index 16f62059..c737bd4c 100644
+-+--- a/evidence/updatedifflog.md
+-++++ b/evidence/updatedifflog.md
+-+@@ -1,487 +1,9 @@
+-+-Cycle Status: STOPPED:CONTRACT_CONFLICT
+-++Cycle Status: COMPLETE
+-+ Todo Ledger:
+-+-- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
+-+-- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
+-+-- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.
+-++- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E.
+-++- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed.
+-++- Remaining: None.
+-+ 
+-+-Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.
+-++Next Action: Optional: clean routine data on Render for slimmer suggestion lists.
+++     async function loadTodayPlanner() {
++++      if (othelloState.currentView !== "today-planner") {
++++        logPlannerDebug("[Today Planner] load skipped", { view: othelloState.currentView });
++++        return;
++++      }
++++      if (document.hidden) {
++++        logPlannerDebug("[Today Planner] load skipped (hidden)", { view: othelloState.currentView });
++++        return;
++ +      }
++-       if (plannerLoadResult === "fail") {
++-         throw new Error("Planner load failed banner displayed; see planner-trace.txt");
+++       if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner invoked", {
+++         view: othelloState.currentView,
+++         ts: new Date().toISOString(),
+++         dayViewDateYmd
+++       });
++++      abortPlannerRequests("planner-reload");
++++      plannerAbort = new AbortController();
++++      const { signal } = plannerAbort;
+++       clearPlannerError();
+++       plannerHeadline.textContent = "Loading...";
+++       plannerEnergy.textContent = "";
+++@@ -5107,7 +5230,8 @@
+++         planUrl = dayViewDateYmd 
+++             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
+++             : `/api/today-plan?ts=${Date.now()}`;
+++-        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
++++        const brief = dayViewDateYmd ? {} : await fetchTodayBrief(signal).catch((err) => {
++++          if (isAbortError(err)) throw err;
+++           briefStatus = err && err.status ? err.status : null;
+++           briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
+++           briefParseError = err && err.parseError ? err.parseError : null;
+++@@ -5118,7 +5242,7 @@
+++           });
+++           return {};
+++         });
+++-        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
++++        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include", signal });
+++         planStatus = planResponse.status;
+++         const planText = await planResponse.text();
+++         planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
+++@@ -5153,8 +5277,12 @@
+++         renderPlannerSections(plan, goalTasks);
+++         const currentItem = renderCurrentFocus(plan);
+++         renderNextAction(plan, currentItem ? [currentItem.item_id || currentItem.id] : []);
+++-        await loadTodayPlanPanel();
++++        await loadTodayPlanPanel(signal);
+++       } catch (e) {
++++        if (isAbortError(e)) {
++++          logPlannerDebug("[Today Planner] load aborted", { view: othelloState.currentView });
++++          return;
++++        }
+++         let httpStatus = null;
+++         if (e && (e.status === 401 || e.status === 403)) {
+++           await handleUnauthorized('today-planner');
+++@@ -5403,11 +5531,22 @@
+++         if (focusRibbon) focusRibbon.classList.remove("visible");
++        }
++-@@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-       (response) => {
++-         const url = response.url();
++-         if (response.request().method() !== "POST") return false;
++--        return url.includes("/confirm") || url.includes("/plan/update");
++-+        return url.includes("/v1/suggestions/") && url.includes("/accept");
 +-       },
 +-       { timeout: 20000 }
-+--    )
-+--    .toBe(true);
-+--
-+--  const todayPlanItems = page.locator("#today-plan-items");
-+--  await expect(todayPlanItems).toBeVisible();
-+--  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
-+--  if (selectedTitle && planText && planText.includes(selectedTitle)) {
-+--    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
-+--  } else {
-+--    await expect
-+--      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
-+--      .toBeGreaterThan(0);
-+--  }
-+-+    );
-+-+    await targetCard.getByRole("button", { name: "Confirm" }).click();
-+-+    const confirmResponse = await confirmResponsePromise;
-+-+    let confirmText = "";
++-     );
++-@@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-       confirmText = await confirmResponse.text();
++-     } catch {}
++-     let confirmOk = confirmResponse.status() === 200;
++--    if (confirmText.includes("\"ok\":")) {
++--      confirmOk = confirmText.includes("\"ok\":true");
++-+    let confirmJson = null;
 +-+    try {
-+-+      confirmText = await confirmResponse.text();
++-+      confirmJson = JSON.parse(confirmText);
 +-+    } catch {}
-+-+    let confirmOk = confirmResponse.status() === 200;
-+-+    if (confirmText.includes("\"ok\":")) {
-+-+      confirmOk = confirmText.includes("\"ok\":true");
-+-+    }
-+-+    if (!confirmOk) {
-+-+      await testInfo.attach("planner-trace.txt", {
-+-+        body: plannerTrace.join("\n"),
-+-+        contentType: "text/plain",
-+-+      });
-+-+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
-+-+    }
-+- 
-+--  if (consoleErrors.length) {
-+--    await testInfo.attach("console-errors.txt", {
-+--      body: consoleErrors.join("\n"),
-+--      contentType: "text/plain",
-+--    });
-+--  }
-+-+    await page.locator("#middle-tab").click();
-+-+    await expect(page.locator("#today-planner-view")).toBeVisible();
-+- 
-+--  if (serverErrors.length) {
-+--    await testInfo.attach("server-500s.txt", {
-+--      body: serverErrors.join("\n"),
-+--      contentType: "text/plain",
-+--    });
-+--  }
-+-+    const todayPlanItems = page.locator("#today-plan-items");
-+-+    await expect(todayPlanItems).toBeVisible();
-+-+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
-+-+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
-+-+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
-+-+    } else {
-+-+      await expect
-+-+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
-+-+        .toBeGreaterThan(0);
-+-+    }
-+- 
-+--  const criticalConsoleErrors = consoleErrors.filter((entry) => (
-+--    entry.includes("Uncaught") || entry.includes("TypeError")
-+--  ));
-+--  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
-+--  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
-+-+    if (consoleErrors.length) {
-+-+      await testInfo.attach("console-errors.txt", {
-+-+        body: consoleErrors.join("\n"),
-+-+        contentType: "text/plain",
-+-+      });
-+-+    }
-+-+
-+-+    if (serverErrors.length) {
-+-+      await testInfo.attach("server-500s.txt", {
-+-+        body: serverErrors.join("\n"),
-+-+        contentType: "text/plain",
-+-+      });
-+-+    }
-+-+
-+-+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
-+-+      entry.includes("Uncaught") || entry.includes("TypeError")
-+-+    ));
-+-+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
-+-+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
-+-+  } finally {
-+-+    if (plannerTrace.length) {
-+-+      await testInfo.attach("planner-trace.txt", {
-+-+        body: plannerTrace.join("\n"),
-+-+        contentType: "text/plain",
-+-+      });
-+-+    }
-+-+  }
++-+    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) {
++-+      confirmOk = confirmJson.ok === true;
++-     }
++-     if (!confirmOk) {
++-       await testInfo.attach("planner-trace.txt", {
++-@@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
++-         contentType: "text/plain",
+ + 
+-+-diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
+-+-index 45518278..3fd145c5 100644
+-+---- a/evidence/e2e_run.md
+-+-+++ b/evidence/e2e_run.md
+-+-@@ -1,38 +1,39 @@
+-+--Date/Time: 2026-01-03 17:02:21 +00:00
+-+-+Date/Time: 2026-01-03 17:35:21 +00:00
+-+- 
+-+- Commands:
+-+--- npm install
+-+--- npx playwright install --with-deps
+-+- - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
+-+--- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
+-+-+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
+-+- 
+-+- Env Vars:
+-+- - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
+-+- - OTHELLO_ACCESS_CODE=******69
+-+- 
+-+-+Auth probe summary (manual):
+-+-+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
+-+-+- /api/today-brief -> 200 {"brief":{...}}
+-+-+- /api/today-plan -> 200 {"plan":{...}}
+-+-+
+-+- Result: FAIL
+-+- 
+-+--Failure 1 (initial run):
+-+--- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
+-+--- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
+-+--- Artifacts:
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+-+--
+-+--Failure 2 (rerun after selector change):
+-+--- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
+-+--- Secondary: login overlay still visible after 20s (retry #1)
+-+--- Locations:
+-+--  - tests/e2e/othello.todayplanner.routines.spec.js:19
+-+--  - tests/e2e/othello.todayplanner.routines.spec.js:15
+-+--- Artifacts:
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+-+--  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+-+--
+-+--Server 500s: Not evaluated (test timed out before assertion stage).
+-+--Console errors: Not evaluated; none surfaced in runner output.
+-+-+Failure (attempt #1):
+-+-+- Error: Planner load failed banner displayed; see planner-trace.txt
+-+-+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
+-+-+
+-+-+Failure (retry #1):
+-+-+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
+-+-+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
+-+-+
+-+-+Planner trace highlights:
+-+-+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+-+-+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+-+-+
+-+-+Server 500s: Not captured by Playwright listener on this run.
+-+-+Critical console errors: Not captured by Playwright listener on this run.
+-+-+
+-+-+Artifacts:
+-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+-+-+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+-+-diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
+-+-index 5abbeab8..e7e992f5 100644
+-+---- a/tests/e2e/othello.todayplanner.routines.spec.js
+-+-+++ b/tests/e2e/othello.todayplanner.routines.spec.js
+-+-@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
+-+- const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
+-+- const STEP_TITLES = ["Breakfast", "Shower"];
+-+- 
+-+--async function login(page, accessCode) {
+-+-+async function recordAuthTrace(label, response, authTrace) {
+-+-+  let status = "NO_RESPONSE";
+-+-+  let bodyText = "";
+-+-+  if (response) {
+-+-+    status = response.status();
+-+-+    try {
+-+-+      bodyText = await response.text();
+-+-+    } catch (err) {
+-+-+      bodyText = `READ_ERROR: ${err.message}`;
+-+-+    }
+-+-+  }
+-+-+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
+-+-+  authTrace.push(`${label} ${status} ${snippet}`);
+-+-+  return { status, snippet, text: bodyText };
+-+-+}
+-+-+
+-+-+async function login(page, accessCode, baseURL, testInfo, authTrace) {
+-+-   const loginInput = page.locator("#login-pin");
+-+-   const loginOverlay = page.locator("#login-overlay");
+-+--  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
+-+-+  const loginForm = page.locator("#loginForm");
+-+-+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
+-+-+    failOnStatusCode: false,
+-+-+  });
+-+-+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
+-+-+  let preAuthData = null;
+-+-+  try {
+-+-+    preAuthData = JSON.parse(preAuthResult.text || "");
+-+-+  } catch {}
+-+-+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
+-+-   if (needsLogin) {
+-+-+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
+-+-+    const loginResponsePromise = page.waitForResponse(
+-+-+      (response) => response.url().includes("/api/auth/login"),
+-+-+      { timeout: 20000 }
+-+-+    ).catch(() => null);
+-+-     await loginInput.fill(accessCode);
+-+-     await page.locator("#login-btn").click();
+-+-+    const loginResponse = await loginResponsePromise;
+-+-+    if (loginResponse) {
+-+-+      await recordAuthTrace("auth/login", loginResponse, authTrace);
+-+-+    } else {
+-+-+      authTrace.push("auth/login NO_RESPONSE");
+-+-+    }
+-+-   }
+-+--  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
+-+-+
+-+-+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
+-+-+    failOnStatusCode: false,
+-+-+  });
+-+-+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
+-+-+  let meData = null;
+-+-+  try {
+-+-+    meData = JSON.parse(meResult.text || "");
+-+-+  } catch {}
+-+-+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
+-+-+
+-+-+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
+-+-+    failOnStatusCode: false,
+-+-+  });
+-+-+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
+-+-+
+-+-+  if (meResult.status !== 200 || !isAuthed) {
+-+-+    await testInfo.attach("auth-debug.txt", {
+-+-+      body: authTrace.join("\n"),
+-+-+      contentType: "text/plain",
+-+-+    });
+-+-+    throw new Error(
+-+-+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
+-+-+    );
+-+-+  }
+-+-+
+-+-   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
+-+-+  const overlayCount = await loginOverlay.count();
+-+-+  if (overlayCount > 0) {
+-+-+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
+-+-+  } else {
+-+-+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
+-+-+  }
+-+-+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
+-+- }
+-+- 
+-+- async function switchMode(page, label) {
+-+-@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+- 
+-+-   const serverErrors = [];
+-+-   const consoleErrors = [];
+-+-+  const authTrace = [];
+-+-+  const plannerTrace = [];
+-+- 
+-+-   page.on("response", (response) => {
+-+-     if (response.status() >= 500) {
+-+-@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+-     }
+-+-   });
+-+- 
+-+-+  page.on("response", async (response) => {
+-+-+    const url = response.url();
+-+-+    const matchesPlanner = (
+-+-+      url.includes("/api/today-plan")
+-+-+      || url.includes("/api/today-brief")
+-+-+      || url.includes("/v1/plan/draft")
+-+-+      || url.includes("/api/confirm")
+-+-+      || url.includes("/v1/confirm")
+-+-+      || url.includes("/api/plan/update")
+-+-+    );
+-+-+    if (!matchesPlanner) return;
+-+-+    const request = response.request();
+-+-+    let path = url;
+-+-+    try {
+-+-+      const parsed = new URL(url);
+-+-+      path = `${parsed.pathname}${parsed.search}`;
+-+-+    } catch {}
+-+-+    let bodyText = "";
+-+-+    try {
+-+-+      bodyText = await response.text();
+-+-+    } catch (err) {
+-+-+      bodyText = `READ_ERROR: ${err.message}`;
+-+-+    }
+-+-+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
+-+-+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
+-+-+  });
+-+-+
+-+-   page.on("console", (msg) => {
+-+-     if (msg.type() === "error") {
+-+-       consoleErrors.push(msg.text());
+-+-@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+-     consoleErrors.push(`pageerror: ${err.message}`);
+-+-   });
+-+- 
+-+--  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
+-+--  await login(page, accessCode);
+-+-+  try {
+-+-+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
+-+-+    await login(page, accessCode, baseURL, testInfo, authTrace);
+-+- 
+-+--  await switchMode(page, "Routine Planner");
+-+--  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
+-+-+    await switchMode(page, "Routine Planner");
+-+-+    await page.locator("#middle-tab").click();
+-+-+    await expect(page.locator("#routine-planner-view")).toBeVisible();
+-+- 
+-+--  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
+-+--  await page.locator("#routine-add-btn").click();
+-+--  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
+-+-+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
+-+-+    await page.locator("#routine-add-btn").click();
+-+-+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
+-+- 
+-+--  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
+-+-+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
+-+- 
+-+--  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
+-+--  for (const day of days) {
+-+--    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
+-+--      .locator("input[type=checkbox]")
+-+--      .check();
+-+--  }
+-+-+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
+-+-+    for (const day of days) {
+-+-+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
+-+-+        .locator("input[type=checkbox]")
+-+-+        .check();
+-+-+    }
+-+- 
+-+--  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
+-+--  await expect(timeInputs.first()).toBeVisible();
+-+--  await timeInputs.first().fill("06:00");
+-+-+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
+-+-+    await expect(timeInputs.first()).toBeVisible();
+-+-+    await timeInputs.first().fill("06:00");
+-+- 
+-+--  const addStepBtn = page.locator("#routine-add-step-btn");
+-+--  await addStepBtn.click();
+-+--  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
+-+--  await addStepBtn.click();
+-+--  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
+-+-+    const addStepBtn = page.locator("#routine-add-step-btn");
+-+-+    const stepInputs = page.locator("#routine-steps input[type=text]");
+-+-+    let stepCount = await stepInputs.count();
+-+-+    while (stepCount < 2) {
+-+-+      await addStepBtn.click();
+-+-+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
+-+-+      stepCount = await stepInputs.count();
+-+-+    }
+-+-+    const emptyIndices = [];
+-+-+    for (let i = 0; i < stepCount; i++) {
+-+-+      const value = await stepInputs.nth(i).inputValue();
+-+-+      if (!value.trim()) {
+-+-+        emptyIndices.push(i);
+-+-+      }
+-+-+    }
+-+-+    let targetIndices = [];
+-+-+    if (emptyIndices.length >= 2) {
+-+-+      targetIndices = emptyIndices.slice(0, 2);
+-+-+    } else {
+-+-+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
+-+-+    }
+-+-+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
+-+-+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
+-+- 
+-+--  const stepInputs = page.locator("#routine-steps input[type=text]");
+-+--  await stepInputs.nth(0).fill(STEP_TITLES[0]);
+-+--  await stepInputs.nth(1).fill(STEP_TITLES[1]);
+-+-+    await page.locator("#routine-save-btn").click();
+-+-+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
+-+- 
+-+--  await page.locator("#routine-save-btn").click();
+-+--  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
+-+-+    await switchMode(page, "Today Planner");
+-+- 
+-+--  await switchMode(page, "Today Planner");
+-+-+    await page.locator("#middle-tab").click();
+-+-+    await expect(page.locator("#today-planner-view")).toBeVisible();
+-+-+    const plannerFailedBanner = page.getByText("Planner load failed");
+-+-+    const plannerLoadResult = await Promise.race([
+-+-+      page.waitForResponse(
+-+-+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
+-+-+        { timeout: 20000 }
+-+-+      ).then(() => "ok").catch(() => null),
+-+-+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
+-+-+    ]);
+-+-+    if (plannerLoadResult !== "ok") {
+-+-+      await testInfo.attach("planner-trace.txt", {
+-+-+        body: plannerTrace.join("\n"),
+-+-+        contentType: "text/plain",
+-+-+      });
+-+-+      await testInfo.attach("console-errors.txt", {
+-+-+        body: consoleErrors.join("\n"),
+-+-+        contentType: "text/plain",
+-+-+      });
+-+-+      if (plannerLoadResult === "fail") {
+-+-+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
+-+-+      }
+-+-+      throw new Error("Planner load did not complete; see planner-trace.txt");
+-+-+    }
+-+-+    await expect(page.locator("#build-plan-btn")).toBeVisible();
+-+-+    await page.locator("#build-plan-btn").click();
+-+- 
+-+--  await page.locator("#middle-tab").click();
+-+--  await expect(page.locator("#today-planner-view")).toBeVisible();
+-+--  await expect(page.locator("#build-plan-btn")).toBeVisible();
+-+--  await page.locator("#build-plan-btn").click();
+-+-+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
+-+-+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
+-+-+    const pendingCount = await suggestionsList.count();
+-+- 
+-+--  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
+-+--  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
+-+--  const pendingCount = await suggestionsList.count();
+-+-+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
+-+-+    if (await targetCard.count() === 0) {
+-+-+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
+-+-+    }
+-+-+    const targetCount = await targetCard.count();
+-+-+    expect(
+-+-+      targetCount,
+-+-+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
+-+-+    ).toBeGreaterThan(0);
+-+- 
+-+--  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
+-+--  if (await targetCard.count() === 0) {
+-+--    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
+-+--  }
+-+--  const targetCount = await targetCard.count();
+-+--  expect(
+-+--    targetCount,
+-+--    "Expected at least one routine-related suggestion (name match or routine- fallback)."
+-+--  ).toBeGreaterThan(0);
+-+--
+-+--  targetCard = targetCard.first();
+-+--  let selectedTitle = "";
+-+--  const titleLocator = targetCard.locator(".planner-block__title");
+-+--  if (await titleLocator.count()) {
+-+--    selectedTitle = (await titleLocator.first().innerText()).trim();
+-+--  }
+-+--  if (!selectedTitle) {
+-+--    selectedTitle = ((await targetCard.textContent()) || "").trim();
+-+--  }
+-+--  await targetCard.getByRole("button", { name: "Confirm" }).click();
+-+--
+-+--  await expect
+-+--    .poll(
+-+--      async () => {
+-+--        const currentCount = await suggestionsList.count();
+-+--        if (currentCount < pendingCount) return true;
+-+--        if (selectedTitle) {
+-+--          const panelText = await page.locator("#today-plan-suggestions").textContent();
+-+--          return panelText ? !panelText.includes(selectedTitle) : false;
+-+--        }
+-+--        return false;
+-+-+    targetCard = targetCard.first();
+-+-+    let selectedTitle = "";
+-+-+    const titleLocator = targetCard.locator(".planner-block__title");
+-+-+    if (await titleLocator.count()) {
+-+-+      selectedTitle = (await titleLocator.first().innerText()).trim();
+-+-+    }
+-+-+    if (!selectedTitle) {
+-+-+      selectedTitle = ((await targetCard.textContent()) || "").trim();
+-+-+    }
+-+-+    const confirmResponsePromise = page.waitForResponse(
+-+-+      (response) => {
+-+-+        const url = response.url();
+-+-+        if (response.request().method() !== "POST") return false;
+-+-+        return url.includes("/confirm") || url.includes("/plan/update");
+-+-       },
+-+-       { timeout: 20000 }
+-+--    )
+-+--    .toBe(true);
+-+--
+-+--  const todayPlanItems = page.locator("#today-plan-items");
+-+--  await expect(todayPlanItems).toBeVisible();
+-+--  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
+-+--  if (selectedTitle && planText && planText.includes(selectedTitle)) {
+-+--    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
+-+--  } else {
+-+--    await expect
+-+--      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
+-+--      .toBeGreaterThan(0);
+-+--  }
+-+-+    );
+-+-+    await targetCard.getByRole("button", { name: "Confirm" }).click();
+-+-+    const confirmResponse = await confirmResponsePromise;
+-+-+    let confirmText = "";
+-+-+    try {
+-+-+      confirmText = await confirmResponse.text();
+-+-+    } catch {}
+-+-+    let confirmOk = confirmResponse.status() === 200;
+-+-+    if (confirmText.includes("\"ok\":")) {
+-+-+      confirmOk = confirmText.includes("\"ok\":true");
+-+-+    }
+-+-+    if (!confirmOk) {
+-+-+      await testInfo.attach("planner-trace.txt", {
+-+-+        body: plannerTrace.join("\n"),
+-+-+        contentType: "text/plain",
+-+-+      });
+-+-+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
+-+-+    }
+-+- 
+-+--  if (consoleErrors.length) {
+-+--    await testInfo.attach("console-errors.txt", {
+-+--      body: consoleErrors.join("\n"),
+-+--      contentType: "text/plain",
+-+--    });
+-+--  }
+-+-+    await page.locator("#middle-tab").click();
+-+-+    await expect(page.locator("#today-planner-view")).toBeVisible();
+-+- 
+-+--  if (serverErrors.length) {
+-+--    await testInfo.attach("server-500s.txt", {
+-+--      body: serverErrors.join("\n"),
+-+--      contentType: "text/plain",
+-+--    });
+-+--  }
+-+-+    const todayPlanItems = page.locator("#today-plan-items");
+-+-+    await expect(todayPlanItems).toBeVisible();
+-+-+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
+-+-+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
+-+-+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
+-+-+    } else {
+-+-+      await expect
+-+-+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
+-+-+        .toBeGreaterThan(0);
+-+-+    }
+-+- 
+-+--  const criticalConsoleErrors = consoleErrors.filter((entry) => (
+-+--    entry.includes("Uncaught") || entry.includes("TypeError")
+-+--  ));
+-+--  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
+-+--  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
+-+-+    if (consoleErrors.length) {
+-+-+      await testInfo.attach("console-errors.txt", {
+-+-+        body: consoleErrors.join("\n"),
+-+-+        contentType: "text/plain",
+-+-+      });
+-+-+    }
+-+-+
+-+-+    if (serverErrors.length) {
+-+-+      await testInfo.attach("server-500s.txt", {
+-+-+        body: serverErrors.join("\n"),
+-+-+        contentType: "text/plain",
+-+-+      });
+-+-+    }
+-+-+
+-+-+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
+-+-+      entry.includes("Uncaught") || entry.includes("TypeError")
+-+-+    ));
+-+-+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
+-+-+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
+-+-+  } finally {
+-+-+    if (plannerTrace.length) {
+-+-+      await testInfo.attach("planner-trace.txt", {
+-+-+        body: plannerTrace.join("\n"),
+-+-+        contentType: "text/plain",
+-+-+      });
+-+-+    }
+-+-+  }
+-+- });
+-++diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md index 3fd145c5..ce3666e6 100644 --- a/evidence/e2e_run.md +++ b/evidence/e2e_run.md @@ -1,39 +1,20 @@ -Date/Time: 2026-01-03 17:35:21 +00:00 +Date/Time: 2026-01-03 17:46:11 +00:00    Commands:  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e -- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)    Env Vars:  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/  - OTHELLO_ACCESS_CODE=******69   -Auth probe summary (manual): -- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -- /api/today-brief -> 200 {"brief":{...}} -- /api/today-plan -> 200 {"plan":{...}} +Planner load instrumentation: +- Planner load failed banner: NOT observed in passing run +- fetchTodayBrief failure is now non-fatal (logs only)   -Result: FAIL +Confirm endpoint: +- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})   -Failure (attempt #1): -- Error: Planner load failed banner displayed; see planner-trace.txt -- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 - -Failure (retry #1): -- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 - -Planner trace highlights: -- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... - -Server 500s: Not captured by Playwright listener on this run. -Critical console errors: Not captured by Playwright listener on this run. +Result: PASS    Artifacts: -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md +- None (pass run) diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md index 16f62059..1ca047b1 100644 --- a/evidence/updatedifflog.md +++ b/evidence/updatedifflog.md @@ -1,487 +1,9 @@ -Cycle Status: STOPPED:CONTRACT_CONFLICT +Cycle Status: COMPLETE  Todo Ledger: -- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once. -- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence. -- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun. +- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E. +- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed. +- Remaining: None.   -Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E. +Next Action: Optional: clean routine data on Render for slimmer suggestion lists.   -diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md -index 45518278..3fd145c5 100644 ---- a/evidence/e2e_run.md -+++ b/evidence/e2e_run.md -@@ -1,38 +1,39 @@ --Date/Time: 2026-01-03 17:02:21 +00:00 -+Date/Time: 2026-01-03 17:35:21 +00:00 -  - Commands: --- npm install --- npx playwright install --with-deps - - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e --- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab) -+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest) -  - Env Vars: - - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/ - - OTHELLO_ACCESS_CODE=******69 -  -+Auth probe summary (manual): -+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -+- /api/today-brief -> 200 {"brief":{...}} -+- /api/today-plan -> 200 {"plan":{...}} -+ - Result: FAIL -  --Failure 1 (initial run): --- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation --- Location: tests/e2e/othello.todayplanner.routines.spec.js:14 --- Artifacts: --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- --Failure 2 (rerun after selector change): --- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events --- Secondary: login overlay still visible after 20s (retry #1) --- Locations: --  - tests/e2e/othello.todayplanner.routines.spec.js:19 --  - tests/e2e/othello.todayplanner.routines.spec.js:15 --- Artifacts: --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md -- --Server 500s: Not evaluated (test timed out before assertion stage). --Console errors: Not evaluated; none surfaced in runner output. -+Failure (attempt #1): -+- Error: Planner load failed banner displayed; see planner-trace.txt -+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 -+ -+Failure (retry #1): -+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 -+ -+Planner trace highlights: -+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -+ -+Server 500s: Not captured by Playwright listener on this run. -+Critical console errors: Not captured by Playwright listener on this run. -+ -+Artifacts: -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md -diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js -index 5abbeab8..e7e992f5 100644 ---- a/tests/e2e/othello.todayplanner.routines.spec.js -+++ b/tests/e2e/othello.todayplanner.routines.spec.js -@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test"); - const ROUTINE_NAME = "E2E Morning Routine " + Date.now(); - const STEP_TITLES = ["Breakfast", "Shower"]; -  --async function login(page, accessCode) { -+async function recordAuthTrace(label, response, authTrace) { -+  let status = "NO_RESPONSE"; -+  let bodyText = ""; -+  if (response) { -+    status = response.status(); -+    try { -+      bodyText = await response.text(); -+    } catch (err) { -+      bodyText = `READ_ERROR: ${err.message}`; -+    } -+  } -+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300); -+  authTrace.push(`${label} ${status} ${snippet}`); -+  return { status, snippet, text: bodyText }; -+} -+ -+async function login(page, accessCode, baseURL, testInfo, authTrace) { -   const loginInput = page.locator("#login-pin"); -   const loginOverlay = page.locator("#login-overlay"); --  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false); -+  const loginForm = page.locator("#loginForm"); -+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace); -+  let preAuthData = null; -+  try { -+    preAuthData = JSON.parse(preAuthResult.text || ""); -+  } catch {} -+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated)); -   if (needsLogin) { -+    await loginInput.waitFor({ state: "visible", timeout: 20000 }); -+    const loginResponsePromise = page.waitForResponse( -+      (response) => response.url().includes("/api/auth/login"), -+      { timeout: 20000 } -+    ).catch(() => null); -     await loginInput.fill(accessCode); -     await page.locator("#login-btn").click(); -+    const loginResponse = await loginResponsePromise; -+    if (loginResponse) { -+      await recordAuthTrace("auth/login", loginResponse, authTrace); -+    } else { -+      authTrace.push("auth/login NO_RESPONSE"); -+    } -   } --  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 }); -+ -+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace); -+  let meData = null; -+  try { -+    meData = JSON.parse(meResult.text || ""); -+  } catch {} -+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated)); -+ -+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace); -+ -+  if (meResult.status !== 200 || !isAuthed) { -+    await testInfo.attach("auth-debug.txt", { -+      body: authTrace.join("\n"), -+      contentType: "text/plain", -+    }); -+    throw new Error( -+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}` -+    ); -+  } -+ -   await expect(loginOverlay).toBeHidden({ timeout: 20000 }); -+  const overlayCount = await loginOverlay.count(); -+  if (overlayCount > 0) { -+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 }); -+  } else { -+    await expect(loginForm).toHaveCount(0, { timeout: 20000 }); -+  } -+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 }); - } -  - async function switchMode(page, label) { -@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -  -   const serverErrors = []; -   const consoleErrors = []; -+  const authTrace = []; -+  const plannerTrace = []; -  -   page.on("response", (response) => { -     if (response.status() >= 500) { -@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -     } -   }); -  -+  page.on("response", async (response) => { -+    const url = response.url(); -+    const matchesPlanner = ( -+      url.includes("/api/today-plan") -+      || url.includes("/api/today-brief") -+      || url.includes("/v1/plan/draft") -+      || url.includes("/api/confirm") -+      || url.includes("/v1/confirm") -+      || url.includes("/api/plan/update") -+    ); -+    if (!matchesPlanner) return; -+    const request = response.request(); -+    let path = url; -+    try { -+      const parsed = new URL(url); -+      path = `${parsed.pathname}${parsed.search}`; -+    } catch {} -+    let bodyText = ""; -+    try { -+      bodyText = await response.text(); -+    } catch (err) { -+      bodyText = `READ_ERROR: ${err.message}`; -+    } -+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300); -+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`); -+  }); -+ -   page.on("console", (msg) => { -     if (msg.type() === "error") { -       consoleErrors.push(msg.text()); -@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -     consoleErrors.push(`pageerror: ${err.message}`); -   }); -  --  await page.goto(baseURL, { waitUntil: "domcontentloaded" }); --  await login(page, accessCode); -+  try { -+    await page.goto(baseURL, { waitUntil: "domcontentloaded" }); -+    await login(page, accessCode, baseURL, testInfo, authTrace); -  --  await switchMode(page, "Routine Planner"); --  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible(); -+    await switchMode(page, "Routine Planner"); -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#routine-planner-view")).toBeVisible(); -  --  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME)); --  await page.locator("#routine-add-btn").click(); --  await page.locator("#routine-title-input").fill(ROUTINE_NAME); -+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME)); -+    await page.locator("#routine-add-btn").click(); -+    await page.locator("#routine-title-input").fill(ROUTINE_NAME); -  --  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 }); -+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 }); -  --  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]; --  for (const day of days) { --    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") }) --      .locator("input[type=checkbox]") --      .check(); --  } -+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]; -+    for (const day of days) { -+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") }) -+        .locator("input[type=checkbox]") -+        .check(); -+    } -  --  const timeInputs = page.locator("#routine-schedule-extra input[type=time]"); --  await expect(timeInputs.first()).toBeVisible(); --  await timeInputs.first().fill("06:00"); -+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]"); -+    await expect(timeInputs.first()).toBeVisible(); -+    await timeInputs.first().fill("06:00"); -  --  const addStepBtn = page.locator("#routine-add-step-btn"); --  await addStepBtn.click(); --  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 }); --  await addStepBtn.click(); --  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 }); -+    const addStepBtn = page.locator("#routine-add-step-btn"); -+    const stepInputs = page.locator("#routine-steps input[type=text]"); -+    let stepCount = await stepInputs.count(); -+    while (stepCount < 2) { -+      await addStepBtn.click(); -+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 }); -+      stepCount = await stepInputs.count(); -+    } -+    const emptyIndices = []; -+    for (let i = 0; i < stepCount; i++) { -+      const value = await stepInputs.nth(i).inputValue(); -+      if (!value.trim()) { -+        emptyIndices.push(i); -+      } -+    } -+    let targetIndices = []; -+    if (emptyIndices.length >= 2) { -+      targetIndices = emptyIndices.slice(0, 2); -+    } else { -+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1]; -+    } -+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]); -+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]); -  --  const stepInputs = page.locator("#routine-steps input[type=text]"); --  await stepInputs.nth(0).fill(STEP_TITLES[0]); --  await stepInputs.nth(1).fill(STEP_TITLES[1]); -+    await page.locator("#routine-save-btn").click(); -+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 }); -  --  await page.locator("#routine-save-btn").click(); --  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 }); -+    await switchMode(page, "Today Planner"); -  --  await switchMode(page, "Today Planner"); -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#today-planner-view")).toBeVisible(); -+    const plannerFailedBanner = page.getByText("Planner load failed"); -+    const plannerLoadResult = await Promise.race([ -+      page.waitForResponse( -+        (response) => response.url().includes("/api/today-plan") && response.status() === 200, -+        { timeout: 20000 } -+      ).then(() => "ok").catch(() => null), -+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null), -+    ]); -+    if (plannerLoadResult !== "ok") { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+      await testInfo.attach("console-errors.txt", { -+        body: consoleErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+      if (plannerLoadResult === "fail") { -+        throw new Error("Planner load failed banner displayed; see planner-trace.txt"); -+      } -+      throw new Error("Planner load did not complete; see planner-trace.txt"); -+    } -+    await expect(page.locator("#build-plan-btn")).toBeVisible(); -+    await page.locator("#build-plan-btn").click(); -  --  await page.locator("#middle-tab").click(); --  await expect(page.locator("#today-planner-view")).toBeVisible(); --  await expect(page.locator("#build-plan-btn")).toBeVisible(); --  await page.locator("#build-plan-btn").click(); -+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block"); -+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 }); -+    const pendingCount = await suggestionsList.count(); -  --  const suggestionsList = page.locator("#today-plan-suggestions .planner-block"); --  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 }); --  const pendingCount = await suggestionsList.count(); -+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME }); -+    if (await targetCard.count() === 0) { -+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i }); -+    } -+    const targetCount = await targetCard.count(); -+    expect( -+      targetCount, -+      "Expected at least one routine-related suggestion (name match or routine- fallback)." -+    ).toBeGreaterThan(0); -  --  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME }); --  if (await targetCard.count() === 0) { --    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i }); --  } --  const targetCount = await targetCard.count(); --  expect( --    targetCount, --    "Expected at least one routine-related suggestion (name match or routine- fallback)." --  ).toBeGreaterThan(0); -- --  targetCard = targetCard.first(); --  let selectedTitle = ""; --  const titleLocator = targetCard.locator(".planner-block__title"); --  if (await titleLocator.count()) { --    selectedTitle = (await titleLocator.first().innerText()).trim(); --  } --  if (!selectedTitle) { --    selectedTitle = ((await targetCard.textContent()) || "").trim(); --  } --  await targetCard.getByRole("button", { name: "Confirm" }).click(); -- --  await expect --    .poll( --      async () => { --        const currentCount = await suggestionsList.count(); --        if (currentCount < pendingCount) return true; --        if (selectedTitle) { --          const panelText = await page.locator("#today-plan-suggestions").textContent(); --          return panelText ? !panelText.includes(selectedTitle) : false; --        } --        return false; -+    targetCard = targetCard.first(); -+    let selectedTitle = ""; -+    const titleLocator = targetCard.locator(".planner-block__title"); -+    if (await titleLocator.count()) { -+      selectedTitle = (await titleLocator.first().innerText()).trim(); -+    } -+    if (!selectedTitle) { -+      selectedTitle = ((await targetCard.textContent()) || "").trim(); -+    } -+    const confirmResponsePromise = page.waitForResponse( -+      (response) => { -+        const url = response.url(); -+        if (response.request().method() !== "POST") return false; -+        return url.includes("/confirm") || url.includes("/plan/update"); -       }, -       { timeout: 20000 } --    ) --    .toBe(true); -- --  const todayPlanItems = page.locator("#today-plan-items"); --  await expect(todayPlanItems).toBeVisible(); --  const planText = selectedTitle ? await todayPlanItems.textContent() : ""; --  if (selectedTitle && planText && planText.includes(selectedTitle)) { --    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 }); --  } else { --    await expect --      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 }) --      .toBeGreaterThan(0); --  } -+    ); -+    await targetCard.getByRole("button", { name: "Confirm" }).click(); -+    const confirmResponse = await confirmResponsePromise; -+    let confirmText = ""; -+    try { -+      confirmText = await confirmResponse.text(); -+    } catch {} -+    let confirmOk = confirmResponse.status() === 200; -+    if (confirmText.includes("\"ok\":")) { -+      confirmOk = confirmText.includes("\"ok\":true"); -+    } -+    if (!confirmOk) { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`); -+    } -  --  if (consoleErrors.length) { --    await testInfo.attach("console-errors.txt", { --      body: consoleErrors.join("\n"), --      contentType: "text/plain", --    }); --  } -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#today-planner-view")).toBeVisible(); -  --  if (serverErrors.length) { --    await testInfo.attach("server-500s.txt", { --      body: serverErrors.join("\n"), --      contentType: "text/plain", --    }); --  } -+    const todayPlanItems = page.locator("#today-plan-items"); -+    await expect(todayPlanItems).toBeVisible(); -+    const planText = selectedTitle ? await todayPlanItems.textContent() : ""; -+    if (selectedTitle && planText && planText.includes(selectedTitle)) { -+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 }); -+    } else { -+      await expect -+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 }) -+        .toBeGreaterThan(0); -+    } -  --  const criticalConsoleErrors = consoleErrors.filter((entry) => ( --    entry.includes("Uncaught") || entry.includes("TypeError") --  )); --  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]); --  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]); -+    if (consoleErrors.length) { -+      await testInfo.attach("console-errors.txt", { -+        body: consoleErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+ -+    if (serverErrors.length) { -+      await testInfo.attach("server-500s.txt", { -+        body: serverErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+ -+    const criticalConsoleErrors = consoleErrors.filter((entry) => ( -+      entry.includes("Uncaught") || entry.includes("TypeError") -+    )); -+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]); -+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]); -+  } finally { -+    if (plannerTrace.length) { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+  } - }); +diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md index 3fd145c5..ce3666e6 100644 --- a/evidence/e2e_run.md +++ b/evidence/e2e_run.md @@ -1,39 +1,20 @@ -Date/Time: 2026-01-03 17:35:21 +00:00 +Date/Time: 2026-01-03 17:46:11 +00:00    Commands:  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e -- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)    Env Vars:  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/  - OTHELLO_ACCESS_CODE=******69   -Auth probe summary (manual): -- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -- /api/today-brief -> 200 {"brief":{...}} -- /api/today-plan -> 200 {"plan":{...}} +Planner load instrumentation: +- Planner load failed banner: NOT observed in passing run +- fetchTodayBrief failure is now non-fatal (logs only)   -Result: FAIL +Confirm endpoint: +- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})   -Failure (attempt #1): -- Error: Planner load failed banner displayed; see planner-trace.txt -- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 - -Failure (retry #1): -- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 - -Planner trace highlights: -- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... - -Server 500s: Not captured by Playwright listener on this run. -Critical console errors: Not captured by Playwright listener on this run. +Result: PASS    Artifacts: -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md +- None (pass run) diff --git a/othello_ui.html b/othello_ui.html index 4ed3660c..f53dba97 100644 --- a/othello_ui.html +++ b/othello_ui.html @@ -3073,14 +3073,30 @@        async function fetchTodayBrief() {        const resp = await fetch("/api/today-brief", { credentials: "include" }); -      if (resp.status === 401 || resp.status === 403) { +      const status = resp.status; +      const text = await resp.text(); +      if (status === 401 || status === 403) {          const err = new Error("Unauthorized"); -        err.status = resp.status; +        err.status = status;          throw err;        } -      if (!resp.ok) throw new Error("Failed to load brief"); -      const data = await resp.json(); -      return data.brief || {}; +      if (!resp.ok) { +        const err = new Error("Failed to load brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        throw err; +      } +      let data = null; +      try { +        data = JSON.parse(text); +      } catch (parseErr) { +        const err = new Error("Failed to parse brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        err.parseError = parseErr.message; +        throw err; +      } +      return (data && data.brief) || {};      }        async function fetchTodayPlan() { @@ -3206,13 +3222,21 @@            if (!suggestion || !suggestion.id) return;            confirmBtn.disabled = true;            try { +            const confirmPayload = { reason: "confirm" }; +            if (BOOT_DEBUG) { +              console.info("[Today Planner] confirm suggestion", { +                endpoint: `/v1/suggestions/${suggestion.id}/accept`, +                method: "POST", +                payloadKeys: Object.keys(confirmPayload), +              }); +            }              await v1Request(                `/v1/suggestions/${suggestion.id}/accept`,                {                  method: "POST",                  headers: { "Content-Type": "application/json" },                  credentials: "include", -                body: JSON.stringify({ reason: "confirm" }) +                body: JSON.stringify(confirmPayload)                },                "Confirm suggestion"              ); @@ -3359,11 +3383,16 @@        });      }   -    function renderPlannerError(message, httpStatus) { +    function renderPlannerError(message, httpStatus, details) {        plannerError.style.display = "block";        let msg = message || "Could not load today's plan. Please try again later.";        if (httpStatus) msg += ` (HTTP ${httpStatus})`;        plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`; +      if (details) { +        plannerError.dataset.error = details; +      } else { +        delete plannerError.dataset.error; +      }        const retryBtn = document.getElementById("planner-retry-btn");        if (retryBtn) {          retryBtn.onclick = () => { @@ -5067,16 +5096,50 @@            };        }   +      let planStatus = null; +      let planSnippet = null; +      let planParseError = null; +      let briefStatus = null; +      let briefSnippet = null; +      let briefParseError = null; +      let planUrl = null;        try { -        const planUrl = dayViewDateYmd  +        planUrl = dayViewDateYmd               ? `/api/today-plan?plan_date=${dayViewDateYmd}`               : `/api/today-plan?ts=${Date.now()}`; -             -        const [brief, planResp] = await Promise.all([ -            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days -            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json()) -        ]); -         +        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => { +          briefStatus = err && err.status ? err.status : null; +          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null; +          briefParseError = err && err.parseError ? err.parseError : null; +          console.error("[Today Planner] fetchTodayBrief failed", { +            status: briefStatus, +            parseError: briefParseError, +            error: err && err.message, +          }); +          return {}; +        }); +        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" }); +        planStatus = planResponse.status; +        const planText = await planResponse.text(); +        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300); +        if (!planResponse.ok) { +          const err = new Error("Failed to load plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          throw err; +        } +        let planResp = null; +        try { +          planResp = JSON.parse(planText); +        } catch (parseErr) { +          planParseError = parseErr.message; +          const err = new Error("Failed to parse plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          err.parseError = planParseError; +          throw err; +        } +          const plan = planResp.plan || {};          const goalTasks = (plan.sections?.goal_tasks || []);          if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source }); @@ -5103,7 +5166,25 @@            const match = e.message.match(/HTTP (\d+)/);            if (match) httpStatus = match[1];          } -        renderPlannerError("Planner load failed", httpStatus); +        if (e && e.status) httpStatus = e.status; +        const detailParts = []; +        if (planStatus) detailParts.push(`today-plan:${planStatus}`); +        if (planParseError) detailParts.push(`plan_parse:${planParseError}`); +        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`); +        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`); +        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`); +        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`); +        if (e && e.message) detailParts.push(`error:${e.message}`); +        const detailString = detailParts.join(" | ").slice(0, 300); +        console.error("[Today Planner] loadTodayPlanner failed", { +          planUrl, +          planStatus, +          briefStatus, +          planParseError, +          briefParseError, +          error: e && e.message, +        }); +        renderPlannerError("Planner load failed", httpStatus, detailString);          if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);        }      } diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js index e7e992f5..d48e604d 100644 --- a/tests/e2e/othello.todayplanner.routines.spec.js +++ b/tests/e2e/othello.todayplanner.routines.spec.js @@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes    const consoleErrors = [];    const authTrace = [];    const plannerTrace = []; +  const postTrace = [];      page.on("response", (response) => {      if (response.status() >= 500) { @@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        || url.includes("/v1/plan/draft")        || url.includes("/api/confirm")        || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/")        || url.includes("/api/plan/update")      );      if (!matchesPlanner) return; @@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes      plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);    });   +  page.on("request", (request) => { +    const url = request.url(); +    if (request.method() !== "POST") return; +    const matches = ( +      url.includes("/api/confirm") +      || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/") +      || url.includes("/api/plan/update") +    ); +    if (!matches) return; +    let path = url; +    try { +      const parsed = new URL(url); +      path = `${parsed.pathname}${parsed.search}`; +    } catch {} +    const postData = request.postData() || ""; +    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300); +    postTrace.push(`${request.method()} ${path} ${snippet}`); +  }); +    page.on("console", (msg) => {      if (msg.type() === "error") {        consoleErrors.push(msg.text()); @@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          body: consoleErrors.join("\n"),          contentType: "text/plain",        }); +      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error"); +      if (plannerErrorDetails) { +        await testInfo.attach("planner-error.txt", { +          body: plannerErrorDetails, +          contentType: "text/plain", +        }); +      }        if (plannerLoadResult === "fail") {          throw new Error("Planner load failed banner displayed; see planner-trace.txt");        } @@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        (response) => {          const url = response.url();          if (response.request().method() !== "POST") return false; -        return url.includes("/confirm") || url.includes("/plan/update"); +        return url.includes("/v1/suggestions/") && url.includes("/accept");        },        { timeout: 20000 }      ); @@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        confirmText = await confirmResponse.text();      } catch {}      let confirmOk = confirmResponse.status() === 200; -    if (confirmText.includes("\"ok\":")) { -      confirmOk = confirmText.includes("\"ok\":true"); +    let confirmJson = null; +    try { +      confirmJson = JSON.parse(confirmText); +    } catch {} +    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) { +      confirmOk = confirmJson.ok === true;      }      if (!confirmOk) {        await testInfo.attach("planner-trace.txt", { @@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          contentType: "text/plain",        });      } +    await testInfo.attach("post-trace.txt", { +      body: postTrace.join("\n"), +      contentType: "text/plain", +    });    }  }); diff --git a/othello_ui.html b/othello_ui.html index 4ed3660c..f53dba97 100644 --- a/othello_ui.html +++ b/othello_ui.html @@ -3073,14 +3073,30 @@        async function fetchTodayBrief() {        const resp = await fetch("/api/today-brief", { credentials: "include" }); -      if (resp.status === 401 || resp.status === 403) { +      const status = resp.status; +      const text = await resp.text(); +      if (status === 401 || status === 403) {          const err = new Error("Unauthorized"); -        err.status = resp.status; +        err.status = status;          throw err;        } -      if (!resp.ok) throw new Error("Failed to load brief"); -      const data = await resp.json(); -      return data.brief || {}; +      if (!resp.ok) { +        const err = new Error("Failed to load brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        throw err; +      } +      let data = null; +      try { +        data = JSON.parse(text); +      } catch (parseErr) { +        const err = new Error("Failed to parse brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        err.parseError = parseErr.message; +        throw err; +      } +      return (data && data.brief) || {};      }        async function fetchTodayPlan() { @@ -3206,13 +3222,21 @@            if (!suggestion || !suggestion.id) return;            confirmBtn.disabled = true;            try { +            const confirmPayload = { reason: "confirm" }; +            if (BOOT_DEBUG) { +              console.info("[Today Planner] confirm suggestion", { +                endpoint: `/v1/suggestions/${suggestion.id}/accept`, +                method: "POST", +                payloadKeys: Object.keys(confirmPayload), +              }); +            }              await v1Request(                `/v1/suggestions/${suggestion.id}/accept`,                {                  method: "POST",                  headers: { "Content-Type": "application/json" },                  credentials: "include", -                body: JSON.stringify({ reason: "confirm" }) +                body: JSON.stringify(confirmPayload)                },                "Confirm suggestion"              ); @@ -3359,11 +3383,16 @@        });      }   -    function renderPlannerError(message, httpStatus) { +    function renderPlannerError(message, httpStatus, details) {        plannerError.style.display = "block";        let msg = message || "Could not load today's plan. Please try again later.";        if (httpStatus) msg += ` (HTTP ${httpStatus})`;        plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`; +      if (details) { +        plannerError.dataset.error = details; +      } else { +        delete plannerError.dataset.error; +      }        const retryBtn = document.getElementById("planner-retry-btn");        if (retryBtn) {          retryBtn.onclick = () => { @@ -5067,16 +5096,50 @@            };        }   +      let planStatus = null; +      let planSnippet = null; +      let planParseError = null; +      let briefStatus = null; +      let briefSnippet = null; +      let briefParseError = null; +      let planUrl = null;        try { -        const planUrl = dayViewDateYmd  +        planUrl = dayViewDateYmd               ? `/api/today-plan?plan_date=${dayViewDateYmd}`               : `/api/today-plan?ts=${Date.now()}`; -             -        const [brief, planResp] = await Promise.all([ -            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days -            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json()) -        ]); -         +        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => { +          briefStatus = err && err.status ? err.status : null; +          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null; +          briefParseError = err && err.parseError ? err.parseError : null; +          console.error("[Today Planner] fetchTodayBrief failed", { +            status: briefStatus, +            parseError: briefParseError, +            error: err && err.message, +          }); +          return {}; +        }); +        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" }); +        planStatus = planResponse.status; +        const planText = await planResponse.text(); +        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300); +        if (!planResponse.ok) { +          const err = new Error("Failed to load plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          throw err; +        } +        let planResp = null; +        try { +          planResp = JSON.parse(planText); +        } catch (parseErr) { +          planParseError = parseErr.message; +          const err = new Error("Failed to parse plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          err.parseError = planParseError; +          throw err; +        } +          const plan = planResp.plan || {};          const goalTasks = (plan.sections?.goal_tasks || []);          if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source }); @@ -5103,7 +5166,25 @@            const match = e.message.match(/HTTP (\d+)/);            if (match) httpStatus = match[1];          } -        renderPlannerError("Planner load failed", httpStatus); +        if (e && e.status) httpStatus = e.status; +        const detailParts = []; +        if (planStatus) detailParts.push(`today-plan:${planStatus}`); +        if (planParseError) detailParts.push(`plan_parse:${planParseError}`); +        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`); +        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`); +        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`); +        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`); +        if (e && e.message) detailParts.push(`error:${e.message}`); +        const detailString = detailParts.join(" | ").slice(0, 300); +        console.error("[Today Planner] loadTodayPlanner failed", { +          planUrl, +          planStatus, +          briefStatus, +          planParseError, +          briefParseError, +          error: e && e.message, +        }); +        renderPlannerError("Planner load failed", httpStatus, detailString);          if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);        }      } diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js index e7e992f5..d48e604d 100644 --- a/tests/e2e/othello.todayplanner.routines.spec.js +++ b/tests/e2e/othello.todayplanner.routines.spec.js @@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes    const consoleErrors = [];    const authTrace = [];    const plannerTrace = []; +  const postTrace = [];      page.on("response", (response) => {      if (response.status() >= 500) { @@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        || url.includes("/v1/plan/draft")        || url.includes("/api/confirm")        || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/")        || url.includes("/api/plan/update")      );      if (!matchesPlanner) return; @@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes      plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);    });   +  page.on("request", (request) => { +    const url = request.url(); +    if (request.method() !== "POST") return; +    const matches = ( +      url.includes("/api/confirm") +      || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/") +      || url.includes("/api/plan/update") +    ); +    if (!matches) return; +    let path = url; +    try { +      const parsed = new URL(url); +      path = `${parsed.pathname}${parsed.search}`; +    } catch {} +    const postData = request.postData() || ""; +    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300); +    postTrace.push(`${request.method()} ${path} ${snippet}`); +  }); +    page.on("console", (msg) => {      if (msg.type() === "error") {        consoleErrors.push(msg.text()); @@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          body: consoleErrors.join("\n"),          contentType: "text/plain",        }); +      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error"); +      if (plannerErrorDetails) { +        await testInfo.attach("planner-error.txt", { +          body: plannerErrorDetails, +          contentType: "text/plain", +        }); +      }        if (plannerLoadResult === "fail") {          throw new Error("Planner load failed banner displayed; see planner-trace.txt");        } @@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        (response) => {          const url = response.url();          if (response.request().method() !== "POST") return false; -        return url.includes("/confirm") || url.includes("/plan/update"); +        return url.includes("/v1/suggestions/") && url.includes("/accept");        },        { timeout: 20000 }      ); @@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        confirmText = await confirmResponse.text();      } catch {}      let confirmOk = confirmResponse.status() === 200; -    if (confirmText.includes("\"ok\":")) { -      confirmOk = confirmText.includes("\"ok\":true"); +    let confirmJson = null; +    try { +      confirmJson = JSON.parse(confirmText); +    } catch {} +    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) { +      confirmOk = confirmJson.ok === true;      }      if (!confirmOk) {        await testInfo.attach("planner-trace.txt", { @@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          contentType: "text/plain",        });      } +    await testInfo.attach("post-trace.txt", { +      body: postTrace.join("\n"), +      contentType: "text/plain", +    });    }  });
+-+diff --git a/othello_ui.html b/othello_ui.html
+-+index 4ed3660c..f53dba97 100644
+-+--- a/othello_ui.html
+-++++ b/othello_ui.html
+-+@@ -3073,14 +3073,30 @@
++++      if (viewName !== "today-planner") {
++++        stopPlannerPolling("view-change");
++++        abortPlannerRequests("view-change");
++++        abortWeekRequests("view-change");
++++        closeWeekDrilldown();
++++      }
++++      if (viewName !== "routine-planner") {
++++        abortRoutineRequests("view-change");
++++      }
++++
+++       // Load view-specific data
+++       if (viewName === "goals") {
+++         renderGoalsList();
+++       } else if (viewName === "today-planner") {
+++         loadTodayPlanner();
++++        startPlannerPolling();
+++       } else if (viewName === "insights") {
+++         loadInsightsInbox();
+++       } else if (viewName === "routine-planner") {
+++@@ -5423,6 +5562,19 @@
++        });
++      }
++-+    await testInfo.attach("post-trace.txt", {
++-+      body: postTrace.join("\n"),
++-+      contentType: "text/plain",
+ + 
+-+     async function fetchTodayBrief() {
+-+       const resp = await fetch("/api/today-brief", { credentials: "include" });
+-+-      if (resp.status === 401 || resp.status === 403) {
+-++      const status = resp.status;
+-++      const text = await resp.text();
+-++      if (status === 401 || status === 403) {
+-+         const err = new Error("Unauthorized");
+-+-        err.status = resp.status;
+-++        err.status = status;
+-+         throw err;
+-+       }
+-+-      if (!resp.ok) throw new Error("Failed to load brief");
+-+-      const data = await resp.json();
+-+-      return data.brief || {};
+-++      if (!resp.ok) {
+-++        const err = new Error("Failed to load brief");
+-++        err.status = status;
+-++        err.bodySnippet = text.slice(0, 300);
+-++        throw err;
++++    document.addEventListener("visibilitychange", () => {
++++      if (document.hidden) {
++++        stopPlannerPolling("hidden");
++++        abortPlannerRequests("hidden");
++++        abortWeekRequests("hidden");
++++        abortRoutineRequests("hidden");
++++        return;
+ ++      }
+-++      let data = null;
+-++      try {
+-++        data = JSON.parse(text);
+-++      } catch (parseErr) {
+-++        const err = new Error("Failed to parse brief");
+-++        err.status = status;
+-++        err.bodySnippet = text.slice(0, 300);
+-++        err.parseError = parseErr.message;
+-++        throw err;
++++      if (othelloState.currentView === "today-planner") {
++++        startPlannerPolling();
+ ++      }
+-++      return (data && data.brief) || {};
++ +    });
++-   }
 +- });
-++diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md index 3fd145c5..ce3666e6 100644 --- a/evidence/e2e_run.md +++ b/evidence/e2e_run.md @@ -1,39 +1,20 @@ -Date/Time: 2026-01-03 17:35:21 +00:00 +Date/Time: 2026-01-03 17:46:11 +00:00    Commands:  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e -- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)    Env Vars:  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/  - OTHELLO_ACCESS_CODE=******69   -Auth probe summary (manual): -- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -- /api/today-brief -> 200 {"brief":{...}} -- /api/today-plan -> 200 {"plan":{...}} +Planner load instrumentation: +- Planner load failed banner: NOT observed in passing run +- fetchTodayBrief failure is now non-fatal (logs only)   -Result: FAIL +Confirm endpoint: +- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})   -Failure (attempt #1): -- Error: Planner load failed banner displayed; see planner-trace.txt -- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 - -Failure (retry #1): -- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 - -Planner trace highlights: -- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... - -Server 500s: Not captured by Playwright listener on this run. -Critical console errors: Not captured by Playwright listener on this run. +Result: PASS    Artifacts: -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md +- None (pass run) diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md index 16f62059..1ca047b1 100644 --- a/evidence/updatedifflog.md +++ b/evidence/updatedifflog.md @@ -1,487 +1,9 @@ -Cycle Status: STOPPED:CONTRACT_CONFLICT +Cycle Status: COMPLETE  Todo Ledger: -- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once. -- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence. -- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun. +- Planned: Instrument Today Planner errors and confirm wiring, make confirm wait deterministic, rerun E2E. +- Completed: Added planner failure instrumentation, made brief failures non-fatal, logged confirm endpoint, updated E2E confirm/post tracing, E2E passed. +- Remaining: None.   -Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E. +Next Action: Optional: clean routine data on Render for slimmer suggestion lists.   -diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md -index 45518278..3fd145c5 100644 ---- a/evidence/e2e_run.md -+++ b/evidence/e2e_run.md -@@ -1,38 +1,39 @@ --Date/Time: 2026-01-03 17:02:21 +00:00 -+Date/Time: 2026-01-03 17:35:21 +00:00 -  - Commands: --- npm install --- npx playwright install --with-deps - - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e --- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab) -+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest) -  - Env Vars: - - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/ - - OTHELLO_ACCESS_CODE=******69 -  -+Auth probe summary (manual): -+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -+- /api/today-brief -> 200 {"brief":{...}} -+- /api/today-plan -> 200 {"plan":{...}} -+ - Result: FAIL -  --Failure 1 (initial run): --- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation --- Location: tests/e2e/othello.todayplanner.routines.spec.js:14 --- Artifacts: --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- --Failure 2 (rerun after selector change): --- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events --- Secondary: login overlay still visible after 20s (retry #1) --- Locations: --  - tests/e2e/othello.todayplanner.routines.spec.js:19 --  - tests/e2e/othello.todayplanner.routines.spec.js:15 --- Artifacts: --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip --  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md -- --Server 500s: Not evaluated (test timed out before assertion stage). --Console errors: Not evaluated; none surfaced in runner output. -+Failure (attempt #1): -+- Error: Planner load failed banner displayed; see planner-trace.txt -+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 -+ -+Failure (retry #1): -+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 -+ -+Planner trace highlights: -+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -+ -+Server 500s: Not captured by Playwright listener on this run. -+Critical console errors: Not captured by Playwright listener on this run. -+ -+Artifacts: -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md -diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js -index 5abbeab8..e7e992f5 100644 ---- a/tests/e2e/othello.todayplanner.routines.spec.js -+++ b/tests/e2e/othello.todayplanner.routines.spec.js -@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test"); - const ROUTINE_NAME = "E2E Morning Routine " + Date.now(); - const STEP_TITLES = ["Breakfast", "Shower"]; -  --async function login(page, accessCode) { -+async function recordAuthTrace(label, response, authTrace) { -+  let status = "NO_RESPONSE"; -+  let bodyText = ""; -+  if (response) { -+    status = response.status(); -+    try { -+      bodyText = await response.text(); -+    } catch (err) { -+      bodyText = `READ_ERROR: ${err.message}`; -+    } -+  } -+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300); -+  authTrace.push(`${label} ${status} ${snippet}`); -+  return { status, snippet, text: bodyText }; -+} -+ -+async function login(page, accessCode, baseURL, testInfo, authTrace) { -   const loginInput = page.locator("#login-pin"); -   const loginOverlay = page.locator("#login-overlay"); --  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false); -+  const loginForm = page.locator("#loginForm"); -+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace); -+  let preAuthData = null; -+  try { -+    preAuthData = JSON.parse(preAuthResult.text || ""); -+  } catch {} -+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated)); -   if (needsLogin) { -+    await loginInput.waitFor({ state: "visible", timeout: 20000 }); -+    const loginResponsePromise = page.waitForResponse( -+      (response) => response.url().includes("/api/auth/login"), -+      { timeout: 20000 } -+    ).catch(() => null); -     await loginInput.fill(accessCode); -     await page.locator("#login-btn").click(); -+    const loginResponse = await loginResponsePromise; -+    if (loginResponse) { -+      await recordAuthTrace("auth/login", loginResponse, authTrace); -+    } else { -+      authTrace.push("auth/login NO_RESPONSE"); -+    } -   } --  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 }); -+ -+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace); -+  let meData = null; -+  try { -+    meData = JSON.parse(meResult.text || ""); -+  } catch {} -+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated)); -+ -+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), { -+    failOnStatusCode: false, -+  }); -+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace); -+ -+  if (meResult.status !== 200 || !isAuthed) { -+    await testInfo.attach("auth-debug.txt", { -+      body: authTrace.join("\n"), -+      contentType: "text/plain", -+    }); -+    throw new Error( -+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}` -+    ); -+  } -+ -   await expect(loginOverlay).toBeHidden({ timeout: 20000 }); -+  const overlayCount = await loginOverlay.count(); -+  if (overlayCount > 0) { -+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 }); -+  } else { -+    await expect(loginForm).toHaveCount(0, { timeout: 20000 }); -+  } -+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 }); - } -  - async function switchMode(page, label) { -@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -  -   const serverErrors = []; -   const consoleErrors = []; -+  const authTrace = []; -+  const plannerTrace = []; -  -   page.on("response", (response) => { -     if (response.status() >= 500) { -@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -     } -   }); -  -+  page.on("response", async (response) => { -+    const url = response.url(); -+    const matchesPlanner = ( -+      url.includes("/api/today-plan") -+      || url.includes("/api/today-brief") -+      || url.includes("/v1/plan/draft") -+      || url.includes("/api/confirm") -+      || url.includes("/v1/confirm") -+      || url.includes("/api/plan/update") -+    ); -+    if (!matchesPlanner) return; -+    const request = response.request(); -+    let path = url; -+    try { -+      const parsed = new URL(url); -+      path = `${parsed.pathname}${parsed.search}`; -+    } catch {} -+    let bodyText = ""; -+    try { -+      bodyText = await response.text(); -+    } catch (err) { -+      bodyText = `READ_ERROR: ${err.message}`; -+    } -+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300); -+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`); -+  }); -+ -   page.on("console", (msg) => { -     if (msg.type() === "error") { -       consoleErrors.push(msg.text()); -@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes -     consoleErrors.push(`pageerror: ${err.message}`); -   }); -  --  await page.goto(baseURL, { waitUntil: "domcontentloaded" }); --  await login(page, accessCode); -+  try { -+    await page.goto(baseURL, { waitUntil: "domcontentloaded" }); -+    await login(page, accessCode, baseURL, testInfo, authTrace); -  --  await switchMode(page, "Routine Planner"); --  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible(); -+    await switchMode(page, "Routine Planner"); -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#routine-planner-view")).toBeVisible(); -  --  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME)); --  await page.locator("#routine-add-btn").click(); --  await page.locator("#routine-title-input").fill(ROUTINE_NAME); -+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME)); -+    await page.locator("#routine-add-btn").click(); -+    await page.locator("#routine-title-input").fill(ROUTINE_NAME); -  --  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 }); -+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 }); -  --  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]; --  for (const day of days) { --    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") }) --      .locator("input[type=checkbox]") --      .check(); --  } -+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]; -+    for (const day of days) { -+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") }) -+        .locator("input[type=checkbox]") -+        .check(); -+    } -  --  const timeInputs = page.locator("#routine-schedule-extra input[type=time]"); --  await expect(timeInputs.first()).toBeVisible(); --  await timeInputs.first().fill("06:00"); -+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]"); -+    await expect(timeInputs.first()).toBeVisible(); -+    await timeInputs.first().fill("06:00"); -  --  const addStepBtn = page.locator("#routine-add-step-btn"); --  await addStepBtn.click(); --  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 }); --  await addStepBtn.click(); --  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 }); -+    const addStepBtn = page.locator("#routine-add-step-btn"); -+    const stepInputs = page.locator("#routine-steps input[type=text]"); -+    let stepCount = await stepInputs.count(); -+    while (stepCount < 2) { -+      await addStepBtn.click(); -+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 }); -+      stepCount = await stepInputs.count(); -+    } -+    const emptyIndices = []; -+    for (let i = 0; i < stepCount; i++) { -+      const value = await stepInputs.nth(i).inputValue(); -+      if (!value.trim()) { -+        emptyIndices.push(i); -+      } -+    } -+    let targetIndices = []; -+    if (emptyIndices.length >= 2) { -+      targetIndices = emptyIndices.slice(0, 2); -+    } else { -+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1]; -+    } -+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]); -+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]); -  --  const stepInputs = page.locator("#routine-steps input[type=text]"); --  await stepInputs.nth(0).fill(STEP_TITLES[0]); --  await stepInputs.nth(1).fill(STEP_TITLES[1]); -+    await page.locator("#routine-save-btn").click(); -+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 }); -  --  await page.locator("#routine-save-btn").click(); --  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 }); -+    await switchMode(page, "Today Planner"); -  --  await switchMode(page, "Today Planner"); -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#today-planner-view")).toBeVisible(); -+    const plannerFailedBanner = page.getByText("Planner load failed"); -+    const plannerLoadResult = await Promise.race([ -+      page.waitForResponse( -+        (response) => response.url().includes("/api/today-plan") && response.status() === 200, -+        { timeout: 20000 } -+      ).then(() => "ok").catch(() => null), -+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null), -+    ]); -+    if (plannerLoadResult !== "ok") { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+      await testInfo.attach("console-errors.txt", { -+        body: consoleErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+      if (plannerLoadResult === "fail") { -+        throw new Error("Planner load failed banner displayed; see planner-trace.txt"); -+      } -+      throw new Error("Planner load did not complete; see planner-trace.txt"); -+    } -+    await expect(page.locator("#build-plan-btn")).toBeVisible(); -+    await page.locator("#build-plan-btn").click(); -  --  await page.locator("#middle-tab").click(); --  await expect(page.locator("#today-planner-view")).toBeVisible(); --  await expect(page.locator("#build-plan-btn")).toBeVisible(); --  await page.locator("#build-plan-btn").click(); -+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block"); -+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 }); -+    const pendingCount = await suggestionsList.count(); -  --  const suggestionsList = page.locator("#today-plan-suggestions .planner-block"); --  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 }); --  const pendingCount = await suggestionsList.count(); -+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME }); -+    if (await targetCard.count() === 0) { -+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i }); -+    } -+    const targetCount = await targetCard.count(); -+    expect( -+      targetCount, -+      "Expected at least one routine-related suggestion (name match or routine- fallback)." -+    ).toBeGreaterThan(0); -  --  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME }); --  if (await targetCard.count() === 0) { --    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i }); --  } --  const targetCount = await targetCard.count(); --  expect( --    targetCount, --    "Expected at least one routine-related suggestion (name match or routine- fallback)." --  ).toBeGreaterThan(0); -- --  targetCard = targetCard.first(); --  let selectedTitle = ""; --  const titleLocator = targetCard.locator(".planner-block__title"); --  if (await titleLocator.count()) { --    selectedTitle = (await titleLocator.first().innerText()).trim(); --  } --  if (!selectedTitle) { --    selectedTitle = ((await targetCard.textContent()) || "").trim(); --  } --  await targetCard.getByRole("button", { name: "Confirm" }).click(); -- --  await expect --    .poll( --      async () => { --        const currentCount = await suggestionsList.count(); --        if (currentCount < pendingCount) return true; --        if (selectedTitle) { --          const panelText = await page.locator("#today-plan-suggestions").textContent(); --          return panelText ? !panelText.includes(selectedTitle) : false; --        } --        return false; -+    targetCard = targetCard.first(); -+    let selectedTitle = ""; -+    const titleLocator = targetCard.locator(".planner-block__title"); -+    if (await titleLocator.count()) { -+      selectedTitle = (await titleLocator.first().innerText()).trim(); -+    } -+    if (!selectedTitle) { -+      selectedTitle = ((await targetCard.textContent()) || "").trim(); -+    } -+    const confirmResponsePromise = page.waitForResponse( -+      (response) => { -+        const url = response.url(); -+        if (response.request().method() !== "POST") return false; -+        return url.includes("/confirm") || url.includes("/plan/update"); -       }, -       { timeout: 20000 } --    ) --    .toBe(true); -- --  const todayPlanItems = page.locator("#today-plan-items"); --  await expect(todayPlanItems).toBeVisible(); --  const planText = selectedTitle ? await todayPlanItems.textContent() : ""; --  if (selectedTitle && planText && planText.includes(selectedTitle)) { --    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 }); --  } else { --    await expect --      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 }) --      .toBeGreaterThan(0); --  } -+    ); -+    await targetCard.getByRole("button", { name: "Confirm" }).click(); -+    const confirmResponse = await confirmResponsePromise; -+    let confirmText = ""; -+    try { -+      confirmText = await confirmResponse.text(); -+    } catch {} -+    let confirmOk = confirmResponse.status() === 200; -+    if (confirmText.includes("\"ok\":")) { -+      confirmOk = confirmText.includes("\"ok\":true"); -+    } -+    if (!confirmOk) { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`); -+    } -  --  if (consoleErrors.length) { --    await testInfo.attach("console-errors.txt", { --      body: consoleErrors.join("\n"), --      contentType: "text/plain", --    }); --  } -+    await page.locator("#middle-tab").click(); -+    await expect(page.locator("#today-planner-view")).toBeVisible(); -  --  if (serverErrors.length) { --    await testInfo.attach("server-500s.txt", { --      body: serverErrors.join("\n"), --      contentType: "text/plain", --    }); --  } -+    const todayPlanItems = page.locator("#today-plan-items"); -+    await expect(todayPlanItems).toBeVisible(); -+    const planText = selectedTitle ? await todayPlanItems.textContent() : ""; -+    if (selectedTitle && planText && planText.includes(selectedTitle)) { -+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 }); -+    } else { -+      await expect -+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 }) -+        .toBeGreaterThan(0); -+    } -  --  const criticalConsoleErrors = consoleErrors.filter((entry) => ( --    entry.includes("Uncaught") || entry.includes("TypeError") --  )); --  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]); --  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]); -+    if (consoleErrors.length) { -+      await testInfo.attach("console-errors.txt", { -+        body: consoleErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+ -+    if (serverErrors.length) { -+      await testInfo.attach("server-500s.txt", { -+        body: serverErrors.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+ -+    const criticalConsoleErrors = consoleErrors.filter((entry) => ( -+      entry.includes("Uncaught") || entry.includes("TypeError") -+    )); -+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]); -+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]); -+  } finally { -+    if (plannerTrace.length) { -+      await testInfo.attach("planner-trace.txt", { -+        body: plannerTrace.join("\n"), -+        contentType: "text/plain", -+      }); -+    } -+  } - }); +diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md index 3fd145c5..ce3666e6 100644 --- a/evidence/e2e_run.md +++ b/evidence/e2e_run.md @@ -1,39 +1,20 @@ -Date/Time: 2026-01-03 17:35:21 +00:00 +Date/Time: 2026-01-03 17:46:11 +00:00    Commands:  - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e -- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)    Env Vars:  - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/  - OTHELLO_ACCESS_CODE=******69   -Auth probe summary (manual): -- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"} -- /api/today-brief -> 200 {"brief":{...}} -- /api/today-plan -> 200 {"plan":{...}} +Planner load instrumentation: +- Planner load failed banner: NOT observed in passing run +- fetchTodayBrief failure is now non-fatal (logs only)   -Result: FAIL +Confirm endpoint: +- POST /v1/suggestions/{id}/accept (payload: {"reason":"confirm"})   -Failure (attempt #1): -- Error: Planner load failed banner displayed; see planner-trace.txt -- Location: tests/e2e/othello.todayplanner.routines.spec.js:229 - -Failure (retry #1): -- Error: waitForResponse timeout waiting for POST /confirm or /plan/update -- Location: tests/e2e/othello.todayplanner.routines.spec.js:259 - -Planner trace highlights: -- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... -- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"... - -Server 500s: Not captured by Playwright listener on this run. -Critical console errors: Not captured by Playwright listener on this run. +Result: PASS    Artifacts: -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip -- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md +- None (pass run) diff --git a/othello_ui.html b/othello_ui.html index 4ed3660c..f53dba97 100644 --- a/othello_ui.html +++ b/othello_ui.html @@ -3073,14 +3073,30 @@        async function fetchTodayBrief() {        const resp = await fetch("/api/today-brief", { credentials: "include" }); -      if (resp.status === 401 || resp.status === 403) { +      const status = resp.status; +      const text = await resp.text(); +      if (status === 401 || status === 403) {          const err = new Error("Unauthorized"); -        err.status = resp.status; +        err.status = status;          throw err;        } -      if (!resp.ok) throw new Error("Failed to load brief"); -      const data = await resp.json(); -      return data.brief || {}; +      if (!resp.ok) { +        const err = new Error("Failed to load brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        throw err; +      } +      let data = null; +      try { +        data = JSON.parse(text); +      } catch (parseErr) { +        const err = new Error("Failed to parse brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        err.parseError = parseErr.message; +        throw err; +      } +      return (data && data.brief) || {};      }        async function fetchTodayPlan() { @@ -3206,13 +3222,21 @@            if (!suggestion || !suggestion.id) return;            confirmBtn.disabled = true;            try { +            const confirmPayload = { reason: "confirm" }; +            if (BOOT_DEBUG) { +              console.info("[Today Planner] confirm suggestion", { +                endpoint: `/v1/suggestions/${suggestion.id}/accept`, +                method: "POST", +                payloadKeys: Object.keys(confirmPayload), +              }); +            }              await v1Request(                `/v1/suggestions/${suggestion.id}/accept`,                {                  method: "POST",                  headers: { "Content-Type": "application/json" },                  credentials: "include", -                body: JSON.stringify({ reason: "confirm" }) +                body: JSON.stringify(confirmPayload)                },                "Confirm suggestion"              ); @@ -3359,11 +3383,16 @@        });      }   -    function renderPlannerError(message, httpStatus) { +    function renderPlannerError(message, httpStatus, details) {        plannerError.style.display = "block";        let msg = message || "Could not load today's plan. Please try again later.";        if (httpStatus) msg += ` (HTTP ${httpStatus})`;        plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`; +      if (details) { +        plannerError.dataset.error = details; +      } else { +        delete plannerError.dataset.error; +      }        const retryBtn = document.getElementById("planner-retry-btn");        if (retryBtn) {          retryBtn.onclick = () => { @@ -5067,16 +5096,50 @@            };        }   +      let planStatus = null; +      let planSnippet = null; +      let planParseError = null; +      let briefStatus = null; +      let briefSnippet = null; +      let briefParseError = null; +      let planUrl = null;        try { -        const planUrl = dayViewDateYmd  +        planUrl = dayViewDateYmd               ? `/api/today-plan?plan_date=${dayViewDateYmd}`               : `/api/today-plan?ts=${Date.now()}`; -             -        const [brief, planResp] = await Promise.all([ -            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days -            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json()) -        ]); -         +        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => { +          briefStatus = err && err.status ? err.status : null; +          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null; +          briefParseError = err && err.parseError ? err.parseError : null; +          console.error("[Today Planner] fetchTodayBrief failed", { +            status: briefStatus, +            parseError: briefParseError, +            error: err && err.message, +          }); +          return {}; +        }); +        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" }); +        planStatus = planResponse.status; +        const planText = await planResponse.text(); +        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300); +        if (!planResponse.ok) { +          const err = new Error("Failed to load plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          throw err; +        } +        let planResp = null; +        try { +          planResp = JSON.parse(planText); +        } catch (parseErr) { +          planParseError = parseErr.message; +          const err = new Error("Failed to parse plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          err.parseError = planParseError; +          throw err; +        } +          const plan = planResp.plan || {};          const goalTasks = (plan.sections?.goal_tasks || []);          if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source }); @@ -5103,7 +5166,25 @@            const match = e.message.match(/HTTP (\d+)/);            if (match) httpStatus = match[1];          } -        renderPlannerError("Planner load failed", httpStatus); +        if (e && e.status) httpStatus = e.status; +        const detailParts = []; +        if (planStatus) detailParts.push(`today-plan:${planStatus}`); +        if (planParseError) detailParts.push(`plan_parse:${planParseError}`); +        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`); +        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`); +        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`); +        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`); +        if (e && e.message) detailParts.push(`error:${e.message}`); +        const detailString = detailParts.join(" | ").slice(0, 300); +        console.error("[Today Planner] loadTodayPlanner failed", { +          planUrl, +          planStatus, +          briefStatus, +          planParseError, +          briefParseError, +          error: e && e.message, +        }); +        renderPlannerError("Planner load failed", httpStatus, detailString);          if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);        }      } diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js index e7e992f5..d48e604d 100644 --- a/tests/e2e/othello.todayplanner.routines.spec.js +++ b/tests/e2e/othello.todayplanner.routines.spec.js @@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes    const consoleErrors = [];    const authTrace = [];    const plannerTrace = []; +  const postTrace = [];      page.on("response", (response) => {      if (response.status() >= 500) { @@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        || url.includes("/v1/plan/draft")        || url.includes("/api/confirm")        || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/")        || url.includes("/api/plan/update")      );      if (!matchesPlanner) return; @@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes      plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);    });   +  page.on("request", (request) => { +    const url = request.url(); +    if (request.method() !== "POST") return; +    const matches = ( +      url.includes("/api/confirm") +      || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/") +      || url.includes("/api/plan/update") +    ); +    if (!matches) return; +    let path = url; +    try { +      const parsed = new URL(url); +      path = `${parsed.pathname}${parsed.search}`; +    } catch {} +    const postData = request.postData() || ""; +    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300); +    postTrace.push(`${request.method()} ${path} ${snippet}`); +  }); +    page.on("console", (msg) => {      if (msg.type() === "error") {        consoleErrors.push(msg.text()); @@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          body: consoleErrors.join("\n"),          contentType: "text/plain",        }); +      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error"); +      if (plannerErrorDetails) { +        await testInfo.attach("planner-error.txt", { +          body: plannerErrorDetails, +          contentType: "text/plain", +        }); +      }        if (plannerLoadResult === "fail") {          throw new Error("Planner load failed banner displayed; see planner-trace.txt");        } @@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        (response) => {          const url = response.url();          if (response.request().method() !== "POST") return false; -        return url.includes("/confirm") || url.includes("/plan/update"); +        return url.includes("/v1/suggestions/") && url.includes("/accept");        },        { timeout: 20000 }      ); @@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        confirmText = await confirmResponse.text();      } catch {}      let confirmOk = confirmResponse.status() === 200; -    if (confirmText.includes("\"ok\":")) { -      confirmOk = confirmText.includes("\"ok\":true"); +    let confirmJson = null; +    try { +      confirmJson = JSON.parse(confirmText); +    } catch {} +    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) { +      confirmOk = confirmJson.ok === true;      }      if (!confirmOk) {        await testInfo.attach("planner-trace.txt", { @@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          contentType: "text/plain",        });      } +    await testInfo.attach("post-trace.txt", { +      body: postTrace.join("\n"), +      contentType: "text/plain", +    });    }  }); diff --git a/othello_ui.html b/othello_ui.html index 4ed3660c..f53dba97 100644 --- a/othello_ui.html +++ b/othello_ui.html @@ -3073,14 +3073,30 @@        async function fetchTodayBrief() {        const resp = await fetch("/api/today-brief", { credentials: "include" }); -      if (resp.status === 401 || resp.status === 403) { +      const status = resp.status; +      const text = await resp.text(); +      if (status === 401 || status === 403) {          const err = new Error("Unauthorized"); -        err.status = resp.status; +        err.status = status;          throw err;        } -      if (!resp.ok) throw new Error("Failed to load brief"); -      const data = await resp.json(); -      return data.brief || {}; +      if (!resp.ok) { +        const err = new Error("Failed to load brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        throw err; +      } +      let data = null; +      try { +        data = JSON.parse(text); +      } catch (parseErr) { +        const err = new Error("Failed to parse brief"); +        err.status = status; +        err.bodySnippet = text.slice(0, 300); +        err.parseError = parseErr.message; +        throw err; +      } +      return (data && data.brief) || {};      }        async function fetchTodayPlan() { @@ -3206,13 +3222,21 @@            if (!suggestion || !suggestion.id) return;            confirmBtn.disabled = true;            try { +            const confirmPayload = { reason: "confirm" }; +            if (BOOT_DEBUG) { +              console.info("[Today Planner] confirm suggestion", { +                endpoint: `/v1/suggestions/${suggestion.id}/accept`, +                method: "POST", +                payloadKeys: Object.keys(confirmPayload), +              }); +            }              await v1Request(                `/v1/suggestions/${suggestion.id}/accept`,                {                  method: "POST",                  headers: { "Content-Type": "application/json" },                  credentials: "include", -                body: JSON.stringify({ reason: "confirm" }) +                body: JSON.stringify(confirmPayload)                },                "Confirm suggestion"              ); @@ -3359,11 +3383,16 @@        });      }   -    function renderPlannerError(message, httpStatus) { +    function renderPlannerError(message, httpStatus, details) {        plannerError.style.display = "block";        let msg = message || "Could not load today's plan. Please try again later.";        if (httpStatus) msg += ` (HTTP ${httpStatus})`;        plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`; +      if (details) { +        plannerError.dataset.error = details; +      } else { +        delete plannerError.dataset.error; +      }        const retryBtn = document.getElementById("planner-retry-btn");        if (retryBtn) {          retryBtn.onclick = () => { @@ -5067,16 +5096,50 @@            };        }   +      let planStatus = null; +      let planSnippet = null; +      let planParseError = null; +      let briefStatus = null; +      let briefSnippet = null; +      let briefParseError = null; +      let planUrl = null;        try { -        const planUrl = dayViewDateYmd  +        planUrl = dayViewDateYmd               ? `/api/today-plan?plan_date=${dayViewDateYmd}`               : `/api/today-plan?ts=${Date.now()}`; -             -        const [brief, planResp] = await Promise.all([ -            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days -            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json()) -        ]); -         +        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => { +          briefStatus = err && err.status ? err.status : null; +          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null; +          briefParseError = err && err.parseError ? err.parseError : null; +          console.error("[Today Planner] fetchTodayBrief failed", { +            status: briefStatus, +            parseError: briefParseError, +            error: err && err.message, +          }); +          return {}; +        }); +        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" }); +        planStatus = planResponse.status; +        const planText = await planResponse.text(); +        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300); +        if (!planResponse.ok) { +          const err = new Error("Failed to load plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          throw err; +        } +        let planResp = null; +        try { +          planResp = JSON.parse(planText); +        } catch (parseErr) { +          planParseError = parseErr.message; +          const err = new Error("Failed to parse plan"); +          err.status = planStatus; +          err.bodySnippet = planSnippet; +          err.parseError = planParseError; +          throw err; +        } +          const plan = planResp.plan || {};          const goalTasks = (plan.sections?.goal_tasks || []);          if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source }); @@ -5103,7 +5166,25 @@            const match = e.message.match(/HTTP (\d+)/);            if (match) httpStatus = match[1];          } -        renderPlannerError("Planner load failed", httpStatus); +        if (e && e.status) httpStatus = e.status; +        const detailParts = []; +        if (planStatus) detailParts.push(`today-plan:${planStatus}`); +        if (planParseError) detailParts.push(`plan_parse:${planParseError}`); +        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`); +        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`); +        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`); +        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`); +        if (e && e.message) detailParts.push(`error:${e.message}`); +        const detailString = detailParts.join(" | ").slice(0, 300); +        console.error("[Today Planner] loadTodayPlanner failed", { +          planUrl, +          planStatus, +          briefStatus, +          planParseError, +          briefParseError, +          error: e && e.message, +        }); +        renderPlannerError("Planner load failed", httpStatus, detailString);          if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);        }      } diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js index e7e992f5..d48e604d 100644 --- a/tests/e2e/othello.todayplanner.routines.spec.js +++ b/tests/e2e/othello.todayplanner.routines.spec.js @@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes    const consoleErrors = [];    const authTrace = [];    const plannerTrace = []; +  const postTrace = [];      page.on("response", (response) => {      if (response.status() >= 500) { @@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        || url.includes("/v1/plan/draft")        || url.includes("/api/confirm")        || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/")        || url.includes("/api/plan/update")      );      if (!matchesPlanner) return; @@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes      plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);    });   +  page.on("request", (request) => { +    const url = request.url(); +    if (request.method() !== "POST") return; +    const matches = ( +      url.includes("/api/confirm") +      || url.includes("/v1/confirm") +      || url.includes("/v1/suggestions/") +      || url.includes("/api/plan/update") +    ); +    if (!matches) return; +    let path = url; +    try { +      const parsed = new URL(url); +      path = `${parsed.pathname}${parsed.search}`; +    } catch {} +    const postData = request.postData() || ""; +    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300); +    postTrace.push(`${request.method()} ${path} ${snippet}`); +  }); +    page.on("console", (msg) => {      if (msg.type() === "error") {        consoleErrors.push(msg.text()); @@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          body: consoleErrors.join("\n"),          contentType: "text/plain",        }); +      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error"); +      if (plannerErrorDetails) { +        await testInfo.attach("planner-error.txt", { +          body: plannerErrorDetails, +          contentType: "text/plain", +        }); +      }        if (plannerLoadResult === "fail") {          throw new Error("Planner load failed banner displayed; see planner-trace.txt");        } @@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        (response) => {          const url = response.url();          if (response.request().method() !== "POST") return false; -        return url.includes("/confirm") || url.includes("/plan/update"); +        return url.includes("/v1/suggestions/") && url.includes("/accept");        },        { timeout: 20000 }      ); @@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes        confirmText = await confirmResponse.text();      } catch {}      let confirmOk = confirmResponse.status() === 200; -    if (confirmText.includes("\"ok\":")) { -      confirmOk = confirmText.includes("\"ok\":true"); +    let confirmJson = null; +    try { +      confirmJson = JSON.parse(confirmText); +    } catch {} +    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) { +      confirmOk = confirmJson.ok === true;      }      if (!confirmOk) {        await testInfo.attach("planner-trace.txt", { @@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes          contentType: "text/plain",        });      } +    await testInfo.attach("post-trace.txt", { +      body: postTrace.join("\n"), +      contentType: "text/plain", +    });    }  });
-+diff --git a/othello_ui.html b/othello_ui.html
-+index 4ed3660c..f53dba97 100644
-+--- a/othello_ui.html
-++++ b/othello_ui.html
-+@@ -3073,14 +3073,30 @@
-+ 
-+     async function fetchTodayBrief() {
-+       const resp = await fetch("/api/today-brief", { credentials: "include" });
-+-      if (resp.status === 401 || resp.status === 403) {
-++      const status = resp.status;
-++      const text = await resp.text();
-++      if (status === 401 || status === 403) {
-+         const err = new Error("Unauthorized");
-+-        err.status = resp.status;
-++        err.status = status;
-+         throw err;
++-
++++
+++     // ===== MODE SWITCHER =====
+++     function persistMode(mode) {
+++       try {
+++@@ -5651,6 +5803,11 @@
+ +     }
+ + 
+-+     async function fetchTodayPlan() {
+-+@@ -3206,13 +3222,21 @@
+-+           if (!suggestion || !suggestion.id) return;
+-+           confirmBtn.disabled = true;
+-+           try {
+-++            const confirmPayload = { reason: "confirm" };
+-++            if (BOOT_DEBUG) {
+-++              console.info("[Today Planner] confirm suggestion", {
+-++                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
+-++                method: "POST",
+-++                payloadKeys: Object.keys(confirmPayload),
+-++              });
+-++            }
+-+             await v1Request(
+-+               `/v1/suggestions/${suggestion.id}/accept`,
+-+               {
+-+                 method: "POST",
+-+                 headers: { "Content-Type": "application/json" },
+-+                 credentials: "include",
+-+-                body: JSON.stringify({ reason: "confirm" })
+-++                body: JSON.stringify(confirmPayload)
+-+               },
+-+               "Confirm suggestion"
+-+             );
+-+@@ -3359,11 +3383,16 @@
+-+       });
+++     function resetAuthBoundary(reason) {
++++      stopPlannerPolling("auth-reset");
++++      abortPlannerRequests("auth-reset");
++++      abortWeekRequests("auth-reset");
++++      abortRoutineRequests("auth-reset");
++++      closeWeekDrilldown();
+++       if (connectRetryTimeout) {
+++         clearTimeout(connectRetryTimeout);
+++         connectRetryTimeout = null;
+++@@ -7553,13 +7710,17 @@
+ +     }
+ + 
+-+-    function renderPlannerError(message, httpStatus) {
+-++    function renderPlannerError(message, httpStatus, details) {
+-+       plannerError.style.display = "block";
+-+       let msg = message || "Could not load today's plan. Please try again later.";
+-+       if (httpStatus) msg += ` (HTTP ${httpStatus})`;
+-+       plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
+-++      if (details) {
+-++        plannerError.dataset.error = details;
+-++      } else {
+-++        delete plannerError.dataset.error;
+-++      }
+-+       const retryBtn = document.getElementById("planner-retry-btn");
+-+       if (retryBtn) {
+-+         retryBtn.onclick = () => {
+-+@@ -5067,16 +5096,50 @@
+-+           };
+++     async function fetchRoutines() {
++++      if (othelloState.currentView !== "routine-planner") return;
++++      if (document.hidden) return;
+++       const listEl = document.getElementById("routine-list");
+++       // Only show loader if we don't have data yet to avoid flicker on refresh
+++       if (listEl && othelloState.routines.length === 0) {
+++          listEl.innerHTML = '<div class="routine-loader">Loading routines...</div>';
+ +       }
+-+ 
+-++      let planStatus = null;
+-++      let planSnippet = null;
+-++      let planParseError = null;
+-++      let briefStatus = null;
+-++      let briefSnippet = null;
+-++      let briefParseError = null;
+-++      let planUrl = null;
+ +       try {
+-+-        const planUrl = dayViewDateYmd 
+-++        planUrl = dayViewDateYmd 
+-+             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
+-+             : `/api/today-plan?ts=${Date.now()}`;
+-+-            
+-+-        const [brief, planResp] = await Promise.all([
+-+-            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days
+-+-            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json())
+-+-        ]);
+-+-        
+-++        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
+-++          briefStatus = err && err.status ? err.status : null;
+-++          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
+-++          briefParseError = err && err.parseError ? err.parseError : null;
+-++          console.error("[Today Planner] fetchTodayBrief failed", {
+-++            status: briefStatus,
+-++            parseError: briefParseError,
+-++            error: err && err.message,
+-++          });
+-++          return {};
+-++        });
+-++        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
+-++        planStatus = planResponse.status;
+-++        const planText = await planResponse.text();
+-++        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
+-++        if (!planResponse.ok) {
+-++          const err = new Error("Failed to load plan");
+-++          err.status = planStatus;
+-++          err.bodySnippet = planSnippet;
+-++          throw err;
+-++        }
+-++        let planResp = null;
+-++        try {
+-++          planResp = JSON.parse(planText);
+-++        } catch (parseErr) {
+-++          planParseError = parseErr.message;
+-++          const err = new Error("Failed to parse plan");
+-++          err.status = planStatus;
+-++          err.bodySnippet = planSnippet;
+-++          err.parseError = planParseError;
+-++          throw err;
+-++        }
+- +
+--+Artifacts:
+--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
+-+         const plan = planResp.plan || {};
+-+         const goalTasks = (plan.sections?.goal_tasks || []);
+-+         if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
+-+@@ -5103,7 +5166,25 @@
+-+           const match = e.message.match(/HTTP (\d+)/);
+-+           if (match) httpStatus = match[1];
+++-        const resp = await fetch(ROUTINES_API, { credentials: "include" });
++++        abortRoutineRequests("routines-reload");
++++        routinesAbort = new AbortController();
++++        const resp = await fetch(ROUTINES_API, { credentials: "include", signal: routinesAbort.signal });
+++         if (!resp.ok) throw new Error("Failed to fetch routines");
+++         const data = await resp.json();
+++         if (data.ok) {
+++@@ -7574,6 +7735,10 @@
+++           }
+ +         }
+-+-        renderPlannerError("Planner load failed", httpStatus);
+-++        if (e && e.status) httpStatus = e.status;
+-++        const detailParts = [];
+-++        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
+-++        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
+-++        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
+-++        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
+-++        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
+-++        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
+-++        if (e && e.message) detailParts.push(`error:${e.message}`);
+-++        const detailString = detailParts.join(" | ").slice(0, 300);
+-++        console.error("[Today Planner] loadTodayPlanner failed", {
+-++          planUrl,
+-++          planStatus,
+-++          briefStatus,
+-++          planParseError,
+-++          briefParseError,
+-++          error: e && e.message,
+-++        });
+-++        renderPlannerError("Planner load failed", httpStatus, detailString);
+-+         if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
+-+       }
+-+     }
+- diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
+--index 5abbeab8..e7e992f5 100644
+-+index e7e992f5..d48e604d 100644
+- --- a/tests/e2e/othello.todayplanner.routines.spec.js
+- +++ b/tests/e2e/othello.todayplanner.routines.spec.js
+--@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
+-- const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
+-- const STEP_TITLES = ["Breakfast", "Shower"];
+-- 
+---async function login(page, accessCode) {
+--+async function recordAuthTrace(label, response, authTrace) {
+--+  let status = "NO_RESPONSE";
+--+  let bodyText = "";
+--+  if (response) {
+--+    status = response.status();
+--+    try {
+--+      bodyText = await response.text();
+--+    } catch (err) {
+--+      bodyText = `READ_ERROR: ${err.message}`;
+--+    }
+--+  }
+--+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
+--+  authTrace.push(`${label} ${status} ${snippet}`);
+--+  return { status, snippet, text: bodyText };
+--+}
+--+
+--+async function login(page, accessCode, baseURL, testInfo, authTrace) {
+--   const loginInput = page.locator("#login-pin");
+--   const loginOverlay = page.locator("#login-overlay");
+---  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
+--+  const loginForm = page.locator("#loginForm");
+--+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
+--+    failOnStatusCode: false,
+--+  });
+--+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
+--+  let preAuthData = null;
+--+  try {
+--+    preAuthData = JSON.parse(preAuthResult.text || "");
+--+  } catch {}
+--+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
+--   if (needsLogin) {
+--+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
+--+    const loginResponsePromise = page.waitForResponse(
+--+      (response) => response.url().includes("/api/auth/login"),
+--+      { timeout: 20000 }
+--+    ).catch(() => null);
+--     await loginInput.fill(accessCode);
+--     await page.locator("#login-btn").click();
+--+    const loginResponse = await loginResponsePromise;
+--+    if (loginResponse) {
+--+      await recordAuthTrace("auth/login", loginResponse, authTrace);
+--+    } else {
+--+      authTrace.push("auth/login NO_RESPONSE");
+--+    }
+--   }
+---  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
+--+
+--+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
+--+    failOnStatusCode: false,
+--+  });
+--+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
+--+  let meData = null;
+--+  try {
+--+    meData = JSON.parse(meResult.text || "");
+--+  } catch {}
+--+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
+--+
+--+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
+--+    failOnStatusCode: false,
+--+  });
+--+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
+--+
+--+  if (meResult.status !== 200 || !isAuthed) {
+--+    await testInfo.attach("auth-debug.txt", {
+--+      body: authTrace.join("\n"),
+--+      contentType: "text/plain",
+--+    });
+--+    throw new Error(
+--+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
+--+    );
+--+  }
+--+
+--   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
+--+  const overlayCount = await loginOverlay.count();
+--+  if (overlayCount > 0) {
+--+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
+--+  } else {
+--+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
+--+  }
+--+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
+-- }
+-- 
+-- async function switchMode(page, label) {
+--@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-- 
+--   const serverErrors = [];
+-+@@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-    const consoleErrors = [];
+--+  const authTrace = [];
+--+  const plannerTrace = [];
+-+   const authTrace = [];
+-+   const plannerTrace = [];
+-++  const postTrace = [];
+-  
+-    page.on("response", (response) => {
+-      if (response.status() >= 500) {
+--@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+--     }
+-+@@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+       || url.includes("/v1/plan/draft")
+-+       || url.includes("/api/confirm")
+-+       || url.includes("/v1/confirm")
+-++      || url.includes("/v1/suggestions/")
+-+       || url.includes("/api/plan/update")
+-+     );
+-+     if (!matchesPlanner) return;
+-+@@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+     plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
+-    });
+-  
+--+  page.on("response", async (response) => {
+--+    const url = response.url();
+--+    const matchesPlanner = (
+--+      url.includes("/api/today-plan")
+--+      || url.includes("/api/today-brief")
+--+      || url.includes("/v1/plan/draft")
+--+      || url.includes("/api/confirm")
+-++  page.on("request", (request) => {
+-++    const url = request.url();
+-++    if (request.method() !== "POST") return;
+-++    const matches = (
+-++      url.includes("/api/confirm")
+- +      || url.includes("/v1/confirm")
+-++      || url.includes("/v1/suggestions/")
+- +      || url.includes("/api/plan/update")
+- +    );
+--+    if (!matchesPlanner) return;
+--+    const request = response.request();
+-++    if (!matches) return;
+- +    let path = url;
+- +    try {
+- +      const parsed = new URL(url);
+- +      path = `${parsed.pathname}${parsed.search}`;
+- +    } catch {}
+--+    let bodyText = "";
+--+    try {
+--+      bodyText = await response.text();
+--+    } catch (err) {
+--+      bodyText = `READ_ERROR: ${err.message}`;
+--+    }
+--+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
+--+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
+-++    const postData = request.postData() || "";
+-++    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300);
+-++    postTrace.push(`${request.method()} ${path} ${snippet}`);
+- +  });
+- +
+-    page.on("console", (msg) => {
+-      if (msg.type() === "error") {
+-        consoleErrors.push(msg.text());
+--@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+--     consoleErrors.push(`pageerror: ${err.message}`);
+--   });
+-- 
+---  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
+---  await login(page, accessCode);
+--+  try {
+--+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
+--+    await login(page, accessCode, baseURL, testInfo, authTrace);
+-- 
+---  await switchMode(page, "Routine Planner");
+---  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
+--+    await switchMode(page, "Routine Planner");
+--+    await page.locator("#middle-tab").click();
+--+    await expect(page.locator("#routine-planner-view")).toBeVisible();
+-- 
+---  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
+---  await page.locator("#routine-add-btn").click();
+---  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
+--+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
+--+    await page.locator("#routine-add-btn").click();
+--+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
+-- 
+---  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
+--+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
+-- 
+---  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
+---  for (const day of days) {
+---    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
+---      .locator("input[type=checkbox]")
+---      .check();
+---  }
+--+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
+--+    for (const day of days) {
+--+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
+--+        .locator("input[type=checkbox]")
+--+        .check();
+--+    }
+-- 
+---  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
+---  await expect(timeInputs.first()).toBeVisible();
+---  await timeInputs.first().fill("06:00");
+--+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
+--+    await expect(timeInputs.first()).toBeVisible();
+--+    await timeInputs.first().fill("06:00");
+-- 
+---  const addStepBtn = page.locator("#routine-add-step-btn");
+---  await addStepBtn.click();
+---  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
+---  await addStepBtn.click();
+---  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
+--+    const addStepBtn = page.locator("#routine-add-step-btn");
+--+    const stepInputs = page.locator("#routine-steps input[type=text]");
+--+    let stepCount = await stepInputs.count();
+--+    while (stepCount < 2) {
+--+      await addStepBtn.click();
+--+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
+--+      stepCount = await stepInputs.count();
+--+    }
+--+    const emptyIndices = [];
+--+    for (let i = 0; i < stepCount; i++) {
+--+      const value = await stepInputs.nth(i).inputValue();
+--+      if (!value.trim()) {
+--+        emptyIndices.push(i);
+--+      }
+--+    }
+--+    let targetIndices = [];
+--+    if (emptyIndices.length >= 2) {
+--+      targetIndices = emptyIndices.slice(0, 2);
+--+    } else {
+--+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
+--+    }
+--+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
+--+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
+-- 
+---  const stepInputs = page.locator("#routine-steps input[type=text]");
+---  await stepInputs.nth(0).fill(STEP_TITLES[0]);
+---  await stepInputs.nth(1).fill(STEP_TITLES[1]);
+--+    await page.locator("#routine-save-btn").click();
+--+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
+-- 
+---  await page.locator("#routine-save-btn").click();
+---  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
+--+    await switchMode(page, "Today Planner");
+-- 
+---  await switchMode(page, "Today Planner");
+--+    await page.locator("#middle-tab").click();
+--+    await expect(page.locator("#today-planner-view")).toBeVisible();
+--+    const plannerFailedBanner = page.getByText("Planner load failed");
+--+    const plannerLoadResult = await Promise.race([
+--+      page.waitForResponse(
+--+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
+--+        { timeout: 20000 }
+--+      ).then(() => "ok").catch(() => null),
+--+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
+--+    ]);
+--+    if (plannerLoadResult !== "ok") {
+--+      await testInfo.attach("planner-trace.txt", {
+--+        body: plannerTrace.join("\n"),
+--+        contentType: "text/plain",
+--+      });
+--+      await testInfo.attach("console-errors.txt", {
+--+        body: consoleErrors.join("\n"),
+--+        contentType: "text/plain",
+--+      });
+--+      if (plannerLoadResult === "fail") {
+--+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
+-+@@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+         body: consoleErrors.join("\n"),
+-+         contentType: "text/plain",
+-+       });
+-++      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error");
+-++      if (plannerErrorDetails) {
+-++        await testInfo.attach("planner-error.txt", {
+-++          body: plannerErrorDetails,
+-++          contentType: "text/plain",
+-++        });
+- +      }
+--+      throw new Error("Planner load did not complete; see planner-trace.txt");
+--+    }
+--+    await expect(page.locator("#build-plan-btn")).toBeVisible();
+--+    await page.locator("#build-plan-btn").click();
+-- 
+---  await page.locator("#middle-tab").click();
+---  await expect(page.locator("#today-planner-view")).toBeVisible();
+---  await expect(page.locator("#build-plan-btn")).toBeVisible();
+---  await page.locator("#build-plan-btn").click();
+--+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
+--+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
+--+    const pendingCount = await suggestionsList.count();
+-- 
+---  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
+---  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
+---  const pendingCount = await suggestionsList.count();
+--+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
+--+    if (await targetCard.count() === 0) {
+--+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
+--+    }
+--+    const targetCount = await targetCard.count();
+--+    expect(
+--+      targetCount,
+--+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
+--+    ).toBeGreaterThan(0);
+-- 
+---  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
+---  if (await targetCard.count() === 0) {
+---    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
+---  }
+---  const targetCount = await targetCard.count();
+---  expect(
+---    targetCount,
+---    "Expected at least one routine-related suggestion (name match or routine- fallback)."
+---  ).toBeGreaterThan(0);
+---
+---  targetCard = targetCard.first();
+---  let selectedTitle = "";
+---  const titleLocator = targetCard.locator(".planner-block__title");
+---  if (await titleLocator.count()) {
+---    selectedTitle = (await titleLocator.first().innerText()).trim();
+---  }
+---  if (!selectedTitle) {
+---    selectedTitle = ((await targetCard.textContent()) || "").trim();
+---  }
+---  await targetCard.getByRole("button", { name: "Confirm" }).click();
+---
+---  await expect
+---    .poll(
+---      async () => {
+---        const currentCount = await suggestionsList.count();
+---        if (currentCount < pendingCount) return true;
+---        if (selectedTitle) {
+---          const panelText = await page.locator("#today-plan-suggestions").textContent();
+---          return panelText ? !panelText.includes(selectedTitle) : false;
+---        }
+---        return false;
+--+    targetCard = targetCard.first();
+--+    let selectedTitle = "";
+--+    const titleLocator = targetCard.locator(".planner-block__title");
+--+    if (await titleLocator.count()) {
+--+      selectedTitle = (await titleLocator.first().innerText()).trim();
+--+    }
+--+    if (!selectedTitle) {
+--+      selectedTitle = ((await targetCard.textContent()) || "").trim();
+--+    }
+--+    const confirmResponsePromise = page.waitForResponse(
+--+      (response) => {
+--+        const url = response.url();
+--+        if (response.request().method() !== "POST") return false;
+--+        return url.includes("/confirm") || url.includes("/plan/update");
+-+       if (plannerLoadResult === "fail") {
+-+         throw new Error("Planner load failed banner displayed; see planner-trace.txt");
+-+       }
+-+@@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+       (response) => {
+-+         const url = response.url();
+-+         if (response.request().method() !== "POST") return false;
+-+-        return url.includes("/confirm") || url.includes("/plan/update");
+-++        return url.includes("/v1/suggestions/") && url.includes("/accept");
+-        },
+-        { timeout: 20000 }
+---    )
+---    .toBe(true);
+---
+---  const todayPlanItems = page.locator("#today-plan-items");
+---  await expect(todayPlanItems).toBeVisible();
+---  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
+---  if (selectedTitle && planText && planText.includes(selectedTitle)) {
+---    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
+---  } else {
+---    await expect
+---      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
+---      .toBeGreaterThan(0);
+---  }
+--+    );
+--+    await targetCard.getByRole("button", { name: "Confirm" }).click();
+--+    const confirmResponse = await confirmResponsePromise;
+--+    let confirmText = "";
+-+     );
+-+@@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+       confirmText = await confirmResponse.text();
+-+     } catch {}
+-+     let confirmOk = confirmResponse.status() === 200;
+-+-    if (confirmText.includes("\"ok\":")) {
+-+-      confirmOk = confirmText.includes("\"ok\":true");
+-++    let confirmJson = null;
+- +    try {
+--+      confirmText = await confirmResponse.text();
+-++      confirmJson = JSON.parse(confirmText);
+- +    } catch {}
+--+    let confirmOk = confirmResponse.status() === 200;
+--+    if (confirmText.includes("\"ok\":")) {
+--+      confirmOk = confirmText.includes("\"ok\":true");
+--+    }
+--+    if (!confirmOk) {
+--+      await testInfo.attach("planner-trace.txt", {
+--+        body: plannerTrace.join("\n"),
+--+        contentType: "text/plain",
+--+      });
+--+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
+--+    }
+-- 
+---  if (consoleErrors.length) {
+---    await testInfo.attach("console-errors.txt", {
+---      body: consoleErrors.join("\n"),
+---      contentType: "text/plain",
+---    });
+---  }
+--+    await page.locator("#middle-tab").click();
+--+    await expect(page.locator("#today-planner-view")).toBeVisible();
+-- 
+---  if (serverErrors.length) {
+---    await testInfo.attach("server-500s.txt", {
+---      body: serverErrors.join("\n"),
+---      contentType: "text/plain",
+---    });
+---  }
+--+    const todayPlanItems = page.locator("#today-plan-items");
+--+    await expect(todayPlanItems).toBeVisible();
+--+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
+--+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
+--+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
+--+    } else {
+--+      await expect
+--+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
+--+        .toBeGreaterThan(0);
+--+    }
+-- 
+---  const criticalConsoleErrors = consoleErrors.filter((entry) => (
+---    entry.includes("Uncaught") || entry.includes("TypeError")
+---  ));
+---  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
+---  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
+--+    if (consoleErrors.length) {
+--+      await testInfo.attach("console-errors.txt", {
+--+        body: consoleErrors.join("\n"),
+--+        contentType: "text/plain",
+--+      });
+--+    }
+--+
+--+    if (serverErrors.length) {
+--+      await testInfo.attach("server-500s.txt", {
+--+        body: serverErrors.join("\n"),
+--+        contentType: "text/plain",
+--+      });
+--+    }
+--+
+--+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
+--+      entry.includes("Uncaught") || entry.includes("TypeError")
+--+    ));
+--+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
+--+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
+--+  } finally {
+--+    if (plannerTrace.length) {
+--+      await testInfo.attach("planner-trace.txt", {
+--+        body: plannerTrace.join("\n"),
+--+        contentType: "text/plain",
+--+      });
+--+    }
+--+  }
+-++    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) {
+-++      confirmOk = confirmJson.ok === true;
+-+     }
+-+     if (!confirmOk) {
+-+       await testInfo.attach("planner-trace.txt", {
+-+@@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-+         contentType: "text/plain",
+-+       });
+++       } catch (err) {
++++        if (isAbortError(err)) {
++++          logPlannerDebug("[Routine Planner] fetch aborted", { reason: "routines-reload" });
++++          return;
++++        }
+++         console.error("fetchRoutines error:", err);
+++         showToast("Failed to load routines", "error");
+++         if (listEl && othelloState.routines.length === 0) {
+++@@ -7583,6 +7748,8 @@
+ +     }
+-++    await testInfo.attach("post-trace.txt", {
+-++      body: postTrace.join("\n"),
+-++      contentType: "text/plain",
+-++    });
+-+   }
+-  });
+-+
+++ 
+++     async function loadRoutinePlanner() {
++++      if (othelloState.currentView !== "routine-planner") return;
++++      if (document.hidden) return;
+++       await fetchRoutines();
+++       renderRoutineList(othelloState.routines);
+++       
+ diff --git a/othello_ui.html b/othello_ui.html
+-index 4ed3660c..f53dba97 100644
++index f53dba97..827acd1b 100644
+ --- a/othello_ui.html
+ +++ b/othello_ui.html
+-@@ -3073,14 +3073,30 @@
++@@ -3071,8 +3071,8 @@
++       return formatDateYYYYMMDD(d);
++     }
+  
+-     async function fetchTodayBrief() {
+-       const resp = await fetch("/api/today-brief", { credentials: "include" });
+--      if (resp.status === 401 || resp.status === 403) {
+-+      const status = resp.status;
+-+      const text = await resp.text();
+-+      if (status === 401 || status === 403) {
+-         const err = new Error("Unauthorized");
+--        err.status = resp.status;
+-+        err.status = status;
+-         throw err;
++-    async function fetchTodayBrief() {
++-      const resp = await fetch("/api/today-brief", { credentials: "include" });
+++    async function fetchTodayBrief(signal) {
+++      const resp = await fetch("/api/today-brief", { credentials: "include", signal });
++       const status = resp.status;
++       const text = await resp.text();
++       if (status === 401 || status === 403) {
++@@ -3148,14 +3148,18 @@
 +       }
-+-      if (!resp.ok) throw new Error("Failed to load brief");
-+-      const data = await resp.json();
-+-      return data.brief || {};
-++      if (!resp.ok) {
-++        const err = new Error("Failed to load brief");
-++        err.status = status;
-++        err.bodySnippet = text.slice(0, 300);
-++        throw err;
-++      }
-++      let data = null;
-++      try {
-++        data = JSON.parse(text);
-++      } catch (parseErr) {
-++        const err = new Error("Failed to parse brief");
-++        err.status = status;
-++        err.bodySnippet = text.slice(0, 300);
-++        err.parseError = parseErr.message;
-++        throw err;
-++      }
-++      return (data && data.brief) || {};
++       return payload;
 +     }
-+ 
-+     async function fetchTodayPlan() {
-+@@ -3206,13 +3222,21 @@
-+           if (!suggestion || !suggestion.id) return;
-+           confirmBtn.disabled = true;
-+           try {
-++            const confirmPayload = { reason: "confirm" };
-++            if (BOOT_DEBUG) {
-++              console.info("[Today Planner] confirm suggestion", {
-++                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
-++                method: "POST",
-++                payloadKeys: Object.keys(confirmPayload),
-++              });
-++            }
-+             await v1Request(
-+               `/v1/suggestions/${suggestion.id}/accept`,
-+               {
-+                 method: "POST",
-+                 headers: { "Content-Type": "application/json" },
-+                 credentials: "include",
-+-                body: JSON.stringify({ reason: "confirm" })
-++                body: JSON.stringify(confirmPayload)
-+               },
-+               "Confirm suggestion"
-+             );
-+@@ -3359,11 +3383,16 @@
-+       });
++-    async function fetchV1TodayPlan() {
++-      const payload = await v1Request("/v1/read/today", { cache: "no-store", credentials: "include" }, "Today plan");
+++    async function fetchV1TodayPlan(signal) {
+++      const payload = await v1Request(
+++        "/v1/read/today",
+++        { cache: "no-store", credentials: "include", signal },
+++        "Today plan"
+++      );
++       return payload?.data?.plan || {};
 +     }
-+ 
-+-    function renderPlannerError(message, httpStatus) {
-++    function renderPlannerError(message, httpStatus, details) {
-+       plannerError.style.display = "block";
-+       let msg = message || "Could not load today's plan. Please try again later.";
-+       if (httpStatus) msg += ` (HTTP ${httpStatus})`;
-+       plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
-++      if (details) {
-++        plannerError.dataset.error = details;
++-    async function fetchPlanItemSuggestions() {
+++    async function fetchPlanItemSuggestions(signal) {
++       const payload = await v1Request(
++         "/v1/suggestions?status=pending&kind=plan_item&limit=20",
++-        { credentials: "include" },
+++        { credentials: "include", signal },
++         "Plan suggestions"
++       );
++       return Array.isArray(payload?.data?.suggestions) ? payload.data.suggestions : [];
++@@ -3291,13 +3295,22 @@
+        }
+--      if (!resp.ok) throw new Error("Failed to load brief");
+--      const data = await resp.json();
+--      return data.brief || {};
+-+      if (!resp.ok) {
+-+        const err = new Error("Failed to load brief");
+-+        err.status = status;
+-+        err.bodySnippet = text.slice(0, 300);
+-+        throw err;
++       return { payload: { include_rollover: true }, note: "No recent chat message found; drafting from rollover only." };
++     }
++-    async function loadTodayPlanPanel() {
+++    async function loadTodayPlanPanel(signal) {
+++      if (othelloState.currentView !== "today-planner") return;
+++      if (document.hidden) return;
++       if (!todayPlanItems || !todayPlanSuggestions) return;
++       clearTodayPlanError();
+++      let panelSignal = signal;
+++      if (!panelSignal) {
+++        abortPlannerRequests("panel-reload");
+++        plannerAbort = new AbortController();
+++        panelSignal = plannerAbort.signal;
+ +      }
+-+      let data = null;
+-+      try {
+-+        data = JSON.parse(text);
+-+      } catch (parseErr) {
+-+        const err = new Error("Failed to parse brief");
+-+        err.status = status;
+-+        err.bodySnippet = text.slice(0, 300);
+-+        err.parseError = parseErr.message;
+-+        throw err;
++       try {
++-        const plan = await fetchV1TodayPlan();
+++        const plan = await fetchV1TodayPlan(panelSignal);
++         renderTodayPlanItems(plan);
++       } catch (e) {
+++        if (isAbortError(e)) return;
++         if (e && (e.status === 401 || e.status === 403)) {
++           await handleUnauthorized('today-plan-read');
++           return;
++@@ -3305,9 +3318,10 @@
++         setTodayPlanError(e && e.message ? e.message : "Failed to load today plan.", e && e.requestId ? e.requestId : null);
++       }
++       try {
++-        const suggestions = await fetchPlanItemSuggestions();
+++        const suggestions = await fetchPlanItemSuggestions(panelSignal);
++         renderPlanSuggestions(suggestions);
++       } catch (e) {
+++        if (isAbortError(e)) return;
++         if (e && (e.status === 401 || e.status === 403)) {
++           await handleUnauthorized('today-plan-suggestions');
++           return;
++@@ -4564,6 +4578,66 @@
++     const weekViewCache = {}; 
++     let isWeekViewActive = false;
++     let dayViewDateYmd = null; // null means "today/live"
+++    let plannerPollId = null;
+++    let plannerAbort = null;
+++    let weekAbort = null;
+++    let routinesAbort = null;
+++    let activeWeekDrilldownYmd = null;
+++    let plannerListenersBound = false;
+++    const PLANNER_POLL_MS = 60000;
+++
+++    function isAbortError(err) {
+++      return err && (err.name === "AbortError" || err.code === 20);
+++    }
+++
+++    function logPlannerDebug(message, payload) {
+++      if (!BOOT_DEBUG) return;
+++      if (payload) {
+++        console.log(message, payload);
 ++      } else {
-++        delete plannerError.dataset.error;
+++        console.log(message);
+ +      }
+-+      return (data && data.brief) || {};
+-     }
+++    }
+++
+++    function abortPlannerRequests(reason) {
+++      if (!plannerAbort) return;
+++      plannerAbort.abort();
+++      plannerAbort = null;
+++      logPlannerDebug("[Today Planner] aborted in-flight request", { reason });
+++    }
+++
+++    function abortWeekRequests(reason) {
+++      if (!weekAbort) return;
+++      weekAbort.abort();
+++      weekAbort = null;
+++      logPlannerDebug("[Week View] aborted in-flight request", { reason });
+++    }
+++
+++    function abortRoutineRequests(reason) {
+++      if (!routinesAbort) return;
+++      routinesAbort.abort();
+++      routinesAbort = null;
+++      logPlannerDebug("[Routine Planner] aborted in-flight request", { reason });
+++    }
+++
+++    function stopPlannerPolling(reason) {
+++      if (plannerPollId) {
+++        clearInterval(plannerPollId);
+++        plannerPollId = null;
+++        logPlannerDebug("[Today Planner] polling stopped", { reason });
 ++      }
-+       const retryBtn = document.getElementById("planner-retry-btn");
-+       if (retryBtn) {
-+         retryBtn.onclick = () => {
-+@@ -5067,16 +5096,50 @@
-+           };
-+       }
-+ 
-++      let planStatus = null;
-++      let planSnippet = null;
-++      let planParseError = null;
-++      let briefStatus = null;
-++      let briefSnippet = null;
-++      let briefParseError = null;
-++      let planUrl = null;
+++    }
+++
+++    function startPlannerPolling() {
+++      stopPlannerPolling("restart");
+++      if (!PLANNER_POLL_MS || PLANNER_POLL_MS < 1000) return;
+++      plannerPollId = setInterval(() => {
+++        if (document.hidden) return;
+++        if (othelloState.currentView !== "today-planner") return;
+++        loadTodayPlanner();
+++      }, PLANNER_POLL_MS);
+++      logPlannerDebug("[Today Planner] polling started", { intervalMs: PLANNER_POLL_MS });
+++    }
+  
+-     async function fetchTodayPlan() {
+-@@ -3206,13 +3222,21 @@
+-           if (!suggestion || !suggestion.id) return;
+-           confirmBtn.disabled = true;
+-           try {
+-+            const confirmPayload = { reason: "confirm" };
+-+            if (BOOT_DEBUG) {
+-+              console.info("[Today Planner] confirm suggestion", {
+-+                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
+-+                method: "POST",
+-+                payloadKeys: Object.keys(confirmPayload),
+-+              });
+-+            }
+-             await v1Request(
+-               `/v1/suggestions/${suggestion.id}/accept`,
+-               {
+-                 method: "POST",
+-                 headers: { "Content-Type": "application/json" },
+-                 credentials: "include",
+--                body: JSON.stringify({ reason: "confirm" })
+-+                body: JSON.stringify(confirmPayload)
+-               },
+-               "Confirm suggestion"
+-             );
+-@@ -3359,11 +3383,16 @@
+-       });
++     function getWeekStartYmd(refDate = new Date()) {
++       // Monday-start, local time
++@@ -4641,12 +4715,18 @@
++         return { completed, inProgress, overdue, snoozed, tomorrow };
+      }
+  
+--    function renderPlannerError(message, httpStatus) {
+-+    function renderPlannerError(message, httpStatus, details) {
+-       plannerError.style.display = "block";
+-       let msg = message || "Could not load today's plan. Please try again later.";
+-       if (httpStatus) msg += ` (HTTP ${httpStatus})`;
+-       plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
+-+      if (details) {
+-+        plannerError.dataset.error = details;
+-+      } else {
+-+        delete plannerError.dataset.error;
+-+      }
+-       const retryBtn = document.getElementById("planner-retry-btn");
+-       if (retryBtn) {
+-         retryBtn.onclick = () => {
+-@@ -5067,16 +5096,50 @@
+-           };
++-    async function fetchPlanForDate(ymd) {
+++    async function fetchPlanForDate(ymd, options = {}) {
+++      const { signal, source } = options;
+++      if (othelloState.currentView !== "today-planner") return null;
+++      if (!isWeekViewActive && source !== "drilldown") return null;
++       if (weekViewCache[ymd]) return weekViewCache[ymd];
++       
 +       try {
-+-        const planUrl = dayViewDateYmd 
-++        planUrl = dayViewDateYmd 
-+             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
-+             : `/api/today-plan?ts=${Date.now()}`;
-+-            
-+-        const [brief, planResp] = await Promise.all([
-+-            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days
-+-            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json())
-+-        ]);
-+-        
-++        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
-++          briefStatus = err && err.status ? err.status : null;
-++          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
-++          briefParseError = err && err.parseError ? err.parseError : null;
-++          console.error("[Today Planner] fetchTodayBrief failed", {
-++            status: briefStatus,
-++            parseError: briefParseError,
-++            error: err && err.message,
-++          });
-++          return {};
-++        });
-++        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
-++        planStatus = planResponse.status;
-++        const planText = await planResponse.text();
-++        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
-++        if (!planResponse.ok) {
-++          const err = new Error("Failed to load plan");
-++          err.status = planStatus;
-++          err.bodySnippet = planSnippet;
-++          throw err;
-++        }
-++        let planResp = null;
-++        try {
-++          planResp = JSON.parse(planText);
-++        } catch (parseErr) {
-++          planParseError = parseErr.message;
-++          const err = new Error("Failed to parse plan");
-++          err.status = planStatus;
-++          err.bodySnippet = planSnippet;
-++          err.parseError = planParseError;
-++          throw err;
++         // Use peek=1 to prevent generation/mutation of plans during week view browsing
++-        const resp = await fetch(`/api/today-plan?plan_date=${ymd}&peek=1`, { cache: "no-store", credentials: "include" });
+++        const resp = await fetch(
+++          `/api/today-plan?plan_date=${ymd}&peek=1`,
+++          { cache: "no-store", credentials: "include", signal }
+++        );
++         if (!resp.ok) throw new Error("Failed to fetch");
++         const data = await resp.json();
++         const plan = data.plan || {};
++@@ -4655,19 +4735,34 @@
++         weekViewCache[ymd] = { plan, counts, fetchedAt: Date.now() };
++         return weekViewCache[ymd];
++       } catch (e) {
+++        if (isAbortError(e)) {
+++          logPlannerDebug("[Week View] fetch aborted", { ymd });
+++          return null;
 ++        }
++         console.error(`Failed to fetch plan for ${ymd}`, e);
++         return null;
+        }
++     }
+  
+-+      let planStatus = null;
+-+      let planSnippet = null;
+-+      let planParseError = null;
+-+      let briefStatus = null;
+-+      let briefSnippet = null;
+-+      let briefParseError = null;
+-+      let planUrl = null;
+-       try {
+--        const planUrl = dayViewDateYmd 
+-+        planUrl = dayViewDateYmd 
+-             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
+-             : `/api/today-plan?ts=${Date.now()}`;
+--            
+--        const [brief, planResp] = await Promise.all([
+--            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days
+--            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json())
+--        ]);
++     async function loadWeekView() {
+++        if (othelloState.currentView !== "today-planner") return;
+++        if (!isWeekViewActive) return;
+++        if (document.hidden) return;
+++        
++         const container = document.getElementById("week-view-content");
++-        if (!container) return;
+++        const weekView = document.getElementById("planner-week-view");
+++        if (!container || (weekView && weekView.style.display === "none")) return;
++         container.innerHTML = '<div style="padding:1rem; text-align:center; color:var(--text-soft);">Loading week...</div>';
++         
+++        abortWeekRequests("week-view-reload");
+++        weekAbort = new AbortController();
+++        const { signal } = weekAbort;
+++        logPlannerDebug("[Week View] loadWeekView invoked", { view: othelloState.currentView });
+++        
++         const days = getWeekDays();
++-        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd)));
+++        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd, { signal })));
++         
+++        if (signal.aborted) return;
++         container.innerHTML = '';
++         
++         results.forEach((res, idx) => {
++@@ -4738,12 +4833,26 @@
++         return items;
++     }
++ 
++-    async function openWeekDrilldown(ymd) {
++-        const res = await fetchPlanForDate(ymd);
++-        if (!res) return;
+ -        
+-+        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
+-+          briefStatus = err && err.status ? err.status : null;
+-+          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
+-+          briefParseError = err && err.parseError ? err.parseError : null;
+-+          console.error("[Today Planner] fetchTodayBrief failed", {
+-+            status: briefStatus,
+-+            parseError: briefParseError,
+-+            error: err && err.message,
+-+          });
+-+          return {};
+-+        });
+-+        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
+-+        planStatus = planResponse.status;
+-+        const planText = await planResponse.text();
+-+        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
+-+        if (!planResponse.ok) {
+-+          const err = new Error("Failed to load plan");
+-+          err.status = planStatus;
+-+          err.bodySnippet = planSnippet;
+-+          throw err;
+-+        }
+-+        let planResp = null;
+-+        try {
+-+          planResp = JSON.parse(planText);
+-+        } catch (parseErr) {
+-+          planParseError = parseErr.message;
+-+          const err = new Error("Failed to parse plan");
+-+          err.status = planStatus;
+-+          err.bodySnippet = planSnippet;
+-+          err.parseError = planParseError;
+-+          throw err;
+-+        }
+++    function closeWeekDrilldown() {
++         const existing = document.getElementById("planner-week-drilldown");
++         if (existing) existing.remove();
+++        activeWeekDrilldownYmd = null;
+++    }
  +
--+Artifacts:
--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
--+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
-+         const plan = planResp.plan || {};
-+         const goalTasks = (plan.sections?.goal_tasks || []);
-+         if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
-+@@ -5103,7 +5166,25 @@
-+           const match = e.message.match(/HTTP (\d+)/);
-+           if (match) httpStatus = match[1];
+-         const plan = planResp.plan || {};
+-         const goalTasks = (plan.sections?.goal_tasks || []);
+-         if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
+-@@ -5103,7 +5166,25 @@
+-           const match = e.message.match(/HTTP (\d+)/);
+-           if (match) httpStatus = match[1];
+++    async function openWeekDrilldown(ymd) {
+++        if (othelloState.currentView !== "today-planner") return;
+++        if (activeWeekDrilldownYmd === ymd && document.getElementById("planner-week-drilldown")) return;
+++        activeWeekDrilldownYmd = ymd;
+++        
+++        abortWeekRequests("week-drilldown");
+++        weekAbort = new AbortController();
+++        const res = await fetchPlanForDate(ymd, { signal: weekAbort.signal, source: "drilldown" });
+++        if (!res) {
+++            activeWeekDrilldownYmd = null;
+++            return;
+++        }
+++        
+++        closeWeekDrilldown();
++         
++         const modal = document.createElement("div");
++         modal.id = "planner-week-drilldown";
++@@ -4754,7 +4863,7 @@
++         modal.style.display = "flex";
++         modal.style.alignItems = "center";
++         modal.style.justifyContent = "center";
++-        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
+++        modal.onclick = (e) => { if (e.target === modal) closeWeekDrilldown(); };
++         
++         const card = document.createElement("div");
++         card.className = "planner-card";
++@@ -4777,7 +4886,7 @@
++                     <div class="planner-section__title" style="font-size:1.1rem;">${dateStr}</div>
++                     <div style="font-size:0.85rem; color:var(--text-soft); margin-top:0.2rem;">${summary}</div>
++                 </div>
++-                <button class="icon-button" style="border:none; background:transparent;" onclick="document.getElementById('planner-week-drilldown').remove()">ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¢</button>
+++                <button class="icon-button" style="border:none; background:transparent;" onclick="closeWeekDrilldown()">ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¢</button>
++             </div>
++             <div style="flex:1; overflow-y:auto; padding-right:0.5rem;" id="drilldown-list"></div>
++             <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid var(--border); text-align:center;">
++@@ -4864,8 +4973,8 @@
++ 
++     function openDayViewForDate(ymd) {
++         dayViewDateYmd = ymd;
++-        const modal = document.getElementById("planner-week-drilldown");
++-        if (modal) modal.remove();
+++        closeWeekDrilldown();
+++        abortWeekRequests("day-view-open");
++         
++         isWeekViewActive = false;
++         document.getElementById("planner-week-view").style.display = "none";
++@@ -4883,6 +4992,7 @@
++     }
++ 
++     function toggleWeekView() {
+++        if (othelloState.currentView !== "today-planner") return;
++         const weekView = document.getElementById("planner-week-view");
++         const dayView = document.getElementById("planner-day-view");
++         const btn = document.getElementById("week-view-toggle");
++@@ -4898,14 +5008,25 @@
++             weekView.style.display = "none";
++             dayView.style.display = "block";
++             btn.textContent = "Week View";
+++            closeWeekDrilldown();
+++            abortWeekRequests("week-view-close");
+          }
+--        renderPlannerError("Planner load failed", httpStatus);
+-+        if (e && e.status) httpStatus = e.status;
+-+        const detailParts = [];
+-+        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
+-+        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
+-+        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
+-+        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
+-+        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
+-+        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
+-+        if (e && e.message) detailParts.push(`error:${e.message}`);
+-+        const detailString = detailParts.join(" | ").slice(0, 300);
+-+        console.error("[Today Planner] loadTodayPlanner failed", {
+-+          planUrl,
+-+          planStatus,
+-+          briefStatus,
+-+          planParseError,
+-+          briefParseError,
+-+          error: e && e.message,
+-+        });
+-+        renderPlannerError("Planner load failed", httpStatus, detailString);
+-         if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
+-       }
+      }
+-diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
+-index e7e992f5..d48e604d 100644
+---- a/tests/e2e/othello.todayplanner.routines.spec.js
+-+++ b/tests/e2e/othello.todayplanner.routines.spec.js
+-@@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-   const consoleErrors = [];
+-   const authTrace = [];
+-   const plannerTrace = [];
+-+  const postTrace = [];
++     
++-    // Initialize toggle
++-    document.addEventListener("DOMContentLoaded", () => {
+++    function bindPlannerListeners() {
+++        if (plannerListenersBound) return;
+++        plannerListenersBound = true;
++         const btn = document.getElementById("week-view-toggle");
++         if (btn) btn.onclick = toggleWeekView;
++-    });
+++        
+++        const toggle = document.getElementById("suggestions-toggle");
+++        if (toggle) toggle.onclick = toggleSuggestions;
+++        
+++        const genBtn = document.getElementById("generate-suggestions-btn");
+++        if (genBtn) genBtn.onclick = generateSuggestions;
+++    }
+++    
+++    document.addEventListener("DOMContentLoaded", bindPlannerListeners);
+  
+-   page.on("response", (response) => {
+-     if (response.status() >= 500) {
+-@@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-       || url.includes("/v1/plan/draft")
+-       || url.includes("/api/confirm")
+-       || url.includes("/v1/confirm")
+-+      || url.includes("/v1/suggestions/")
+-       || url.includes("/api/plan/update")
+-     );
+-     if (!matchesPlanner) return;
+-@@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-     plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
+-   });
++     // --- Suggestions Logic ---
++     
++@@ -5035,21 +5156,23 @@
 +         }
-+-        renderPlannerError("Planner load failed", httpStatus);
-++        if (e && e.status) httpStatus = e.status;
-++        const detailParts = [];
-++        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
-++        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
-++        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
-++        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
-++        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
-++        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
-++        if (e && e.message) detailParts.push(`error:${e.message}`);
-++        const detailString = detailParts.join(" | ").slice(0, 300);
-++        console.error("[Today Planner] loadTodayPlanner failed", {
-++          planUrl,
-++          planStatus,
-++          briefStatus,
-++          planParseError,
-++          briefParseError,
-++          error: e && e.message,
-++        });
-++        renderPlannerError("Planner load failed", httpStatus, detailString);
-+         if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
-+       }
 +     }
- diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
--index 5abbeab8..e7e992f5 100644
-+index e7e992f5..d48e604d 100644
- --- a/tests/e2e/othello.todayplanner.routines.spec.js
- +++ b/tests/e2e/othello.todayplanner.routines.spec.js
--@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
-- const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
-- const STEP_TITLES = ["Breakfast", "Shower"];
-- 
---async function login(page, accessCode) {
--+async function recordAuthTrace(label, response, authTrace) {
--+  let status = "NO_RESPONSE";
--+  let bodyText = "";
--+  if (response) {
--+    status = response.status();
+  
+-+  page.on("request", (request) => {
+-+    const url = request.url();
+-+    if (request.method() !== "POST") return;
+-+    const matches = (
+-+      url.includes("/api/confirm")
+-+      || url.includes("/v1/confirm")
+-+      || url.includes("/v1/suggestions/")
+-+      || url.includes("/api/plan/update")
+-+    );
+-+    if (!matches) return;
+-+    let path = url;
 -+    try {
--+      bodyText = await response.text();
--+    } catch (err) {
--+      bodyText = `READ_ERROR: ${err.message}`;
--+    }
--+  }
--+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
--+  authTrace.push(`${label} ${status} ${snippet}`);
--+  return { status, snippet, text: bodyText };
--+}
--+
--+async function login(page, accessCode, baseURL, testInfo, authTrace) {
--   const loginInput = page.locator("#login-pin");
--   const loginOverlay = page.locator("#login-overlay");
---  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
--+  const loginForm = page.locator("#loginForm");
--+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
--+    failOnStatusCode: false,
--+  });
--+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
--+  let preAuthData = null;
--+  try {
--+    preAuthData = JSON.parse(preAuthResult.text || "");
--+  } catch {}
--+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
--   if (needsLogin) {
--+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
--+    const loginResponsePromise = page.waitForResponse(
--+      (response) => response.url().includes("/api/auth/login"),
--+      { timeout: 20000 }
--+    ).catch(() => null);
--     await loginInput.fill(accessCode);
--     await page.locator("#login-btn").click();
--+    const loginResponse = await loginResponsePromise;
--+    if (loginResponse) {
--+      await recordAuthTrace("auth/login", loginResponse, authTrace);
--+    } else {
--+      authTrace.push("auth/login NO_RESPONSE");
--+    }
--   }
---  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
--+
--+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
--+    failOnStatusCode: false,
+-+      const parsed = new URL(url);
+-+      path = `${parsed.pathname}${parsed.search}`;
+-+    } catch {}
+-+    const postData = request.postData() || "";
+-+    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300);
+-+    postTrace.push(`${request.method()} ${path} ${snippet}`);
 -+  });
--+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
--+  let meData = null;
--+  try {
--+    meData = JSON.parse(meResult.text || "");
--+  } catch {}
--+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
--+
--+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
--+    failOnStatusCode: false,
--+  });
--+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
--+
--+  if (meResult.status !== 200 || !isAuthed) {
--+    await testInfo.attach("auth-debug.txt", {
--+      body: authTrace.join("\n"),
--+      contentType: "text/plain",
--+    });
--+    throw new Error(
--+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
--+    );
--+  }
 -+
--   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
--+  const overlayCount = await loginOverlay.count();
--+  if (overlayCount > 0) {
--+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
--+  } else {
--+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
--+  }
--+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
-- }
-- 
-- async function switchMode(page, label) {
--@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-- 
--   const serverErrors = [];
-+@@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-    const consoleErrors = [];
--+  const authTrace = [];
--+  const plannerTrace = [];
-+   const authTrace = [];
-+   const plannerTrace = [];
-++  const postTrace = [];
-  
-    page.on("response", (response) => {
-      if (response.status() >= 500) {
--@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
--     }
-+@@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+       || url.includes("/v1/plan/draft")
-+       || url.includes("/api/confirm")
-+       || url.includes("/v1/confirm")
-++      || url.includes("/v1/suggestions/")
-+       || url.includes("/api/plan/update")
-+     );
-+     if (!matchesPlanner) return;
-+@@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+     plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
-    });
-  
--+  page.on("response", async (response) => {
--+    const url = response.url();
--+    const matchesPlanner = (
--+      url.includes("/api/today-plan")
--+      || url.includes("/api/today-brief")
--+      || url.includes("/v1/plan/draft")
--+      || url.includes("/api/confirm")
-++  page.on("request", (request) => {
-++    const url = request.url();
-++    if (request.method() !== "POST") return;
-++    const matches = (
-++      url.includes("/api/confirm")
- +      || url.includes("/v1/confirm")
-++      || url.includes("/v1/suggestions/")
- +      || url.includes("/api/plan/update")
- +    );
--+    if (!matchesPlanner) return;
--+    const request = response.request();
-++    if (!matches) return;
- +    let path = url;
- +    try {
- +      const parsed = new URL(url);
- +      path = `${parsed.pathname}${parsed.search}`;
- +    } catch {}
--+    let bodyText = "";
--+    try {
--+      bodyText = await response.text();
--+    } catch (err) {
--+      bodyText = `READ_ERROR: ${err.message}`;
--+    }
--+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
--+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
-++    const postData = request.postData() || "";
-++    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300);
-++    postTrace.push(`${request.method()} ${path} ${snippet}`);
- +  });
- +
-    page.on("console", (msg) => {
-      if (msg.type() === "error") {
-        consoleErrors.push(msg.text());
--@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
--     consoleErrors.push(`pageerror: ${err.message}`);
--   });
-- 
---  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
---  await login(page, accessCode);
--+  try {
--+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
--+    await login(page, accessCode, baseURL, testInfo, authTrace);
-- 
---  await switchMode(page, "Routine Planner");
---  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
--+    await switchMode(page, "Routine Planner");
--+    await page.locator("#middle-tab").click();
--+    await expect(page.locator("#routine-planner-view")).toBeVisible();
-- 
---  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
---  await page.locator("#routine-add-btn").click();
---  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
--+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
--+    await page.locator("#routine-add-btn").click();
--+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
-- 
---  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
--+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
-- 
---  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
---  for (const day of days) {
---    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
---      .locator("input[type=checkbox]")
---      .check();
---  }
--+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
--+    for (const day of days) {
--+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
--+        .locator("input[type=checkbox]")
--+        .check();
--+    }
-- 
---  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
---  await expect(timeInputs.first()).toBeVisible();
---  await timeInputs.first().fill("06:00");
--+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
--+    await expect(timeInputs.first()).toBeVisible();
--+    await timeInputs.first().fill("06:00");
-- 
---  const addStepBtn = page.locator("#routine-add-step-btn");
---  await addStepBtn.click();
---  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
---  await addStepBtn.click();
---  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
--+    const addStepBtn = page.locator("#routine-add-step-btn");
--+    const stepInputs = page.locator("#routine-steps input[type=text]");
--+    let stepCount = await stepInputs.count();
--+    while (stepCount < 2) {
--+      await addStepBtn.click();
--+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
--+      stepCount = await stepInputs.count();
--+    }
--+    const emptyIndices = [];
--+    for (let i = 0; i < stepCount; i++) {
--+      const value = await stepInputs.nth(i).inputValue();
--+      if (!value.trim()) {
--+        emptyIndices.push(i);
--+      }
--+    }
--+    let targetIndices = [];
--+    if (emptyIndices.length >= 2) {
--+      targetIndices = emptyIndices.slice(0, 2);
--+    } else {
--+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
--+    }
--+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
--+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
-- 
---  const stepInputs = page.locator("#routine-steps input[type=text]");
---  await stepInputs.nth(0).fill(STEP_TITLES[0]);
---  await stepInputs.nth(1).fill(STEP_TITLES[1]);
--+    await page.locator("#routine-save-btn").click();
--+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
-- 
---  await page.locator("#routine-save-btn").click();
---  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
--+    await switchMode(page, "Today Planner");
-- 
---  await switchMode(page, "Today Planner");
--+    await page.locator("#middle-tab").click();
--+    await expect(page.locator("#today-planner-view")).toBeVisible();
--+    const plannerFailedBanner = page.getByText("Planner load failed");
--+    const plannerLoadResult = await Promise.race([
--+      page.waitForResponse(
--+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
--+        { timeout: 20000 }
--+      ).then(() => "ok").catch(() => null),
--+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
--+    ]);
--+    if (plannerLoadResult !== "ok") {
--+      await testInfo.attach("planner-trace.txt", {
--+        body: plannerTrace.join("\n"),
--+        contentType: "text/plain",
--+      });
--+      await testInfo.attach("console-errors.txt", {
--+        body: consoleErrors.join("\n"),
--+        contentType: "text/plain",
--+      });
--+      if (plannerLoadResult === "fail") {
--+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
-+@@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+         body: consoleErrors.join("\n"),
-+         contentType: "text/plain",
-+       });
-++      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error");
-++      if (plannerErrorDetails) {
-++        await testInfo.attach("planner-error.txt", {
-++          body: plannerErrorDetails,
-++          contentType: "text/plain",
-++        });
+-   page.on("console", (msg) => {
+-     if (msg.type() === "error") {
+-       consoleErrors.push(msg.text());
+-@@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-         body: consoleErrors.join("\n"),
+-         contentType: "text/plain",
+-       });
+-+      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error");
+-+      if (plannerErrorDetails) {
+-+        await testInfo.attach("planner-error.txt", {
+-+          body: plannerErrorDetails,
+-+          contentType: "text/plain",
+-+        });
++-    // Initialize suggestions
++-    document.addEventListener("DOMContentLoaded", () => {
++-        const toggle = document.getElementById("suggestions-toggle");
++-        if (toggle) toggle.onclick = toggleSuggestions;
++-        
++-        const genBtn = document.getElementById("generate-suggestions-btn");
++-        if (genBtn) genBtn.onclick = generateSuggestions;
++-    });
++-
++     async function loadTodayPlanner() {
+++      if (othelloState.currentView !== "today-planner") {
+++        logPlannerDebug("[Today Planner] load skipped", { view: othelloState.currentView });
+++        return;
+++      }
+++      if (document.hidden) {
+++        logPlannerDebug("[Today Planner] load skipped (hidden)", { view: othelloState.currentView });
+++        return;
  +      }
--+      throw new Error("Planner load did not complete; see planner-trace.txt");
--+    }
--+    await expect(page.locator("#build-plan-btn")).toBeVisible();
--+    await page.locator("#build-plan-btn").click();
-- 
---  await page.locator("#middle-tab").click();
---  await expect(page.locator("#today-planner-view")).toBeVisible();
---  await expect(page.locator("#build-plan-btn")).toBeVisible();
---  await page.locator("#build-plan-btn").click();
--+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
--+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
--+    const pendingCount = await suggestionsList.count();
-- 
---  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
---  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
---  const pendingCount = await suggestionsList.count();
--+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
--+    if (await targetCard.count() === 0) {
--+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
--+    }
--+    const targetCount = await targetCard.count();
--+    expect(
--+      targetCount,
--+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
--+    ).toBeGreaterThan(0);
-- 
---  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
---  if (await targetCard.count() === 0) {
---    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
---  }
---  const targetCount = await targetCard.count();
---  expect(
---    targetCount,
---    "Expected at least one routine-related suggestion (name match or routine- fallback)."
---  ).toBeGreaterThan(0);
---
---  targetCard = targetCard.first();
---  let selectedTitle = "";
---  const titleLocator = targetCard.locator(".planner-block__title");
---  if (await titleLocator.count()) {
---    selectedTitle = (await titleLocator.first().innerText()).trim();
---  }
---  if (!selectedTitle) {
---    selectedTitle = ((await targetCard.textContent()) || "").trim();
---  }
---  await targetCard.getByRole("button", { name: "Confirm" }).click();
---
---  await expect
---    .poll(
---      async () => {
---        const currentCount = await suggestionsList.count();
---        if (currentCount < pendingCount) return true;
---        if (selectedTitle) {
---          const panelText = await page.locator("#today-plan-suggestions").textContent();
---          return panelText ? !panelText.includes(selectedTitle) : false;
---        }
---        return false;
--+    targetCard = targetCard.first();
--+    let selectedTitle = "";
--+    const titleLocator = targetCard.locator(".planner-block__title");
--+    if (await titleLocator.count()) {
--+      selectedTitle = (await titleLocator.first().innerText()).trim();
--+    }
--+    if (!selectedTitle) {
--+      selectedTitle = ((await targetCard.textContent()) || "").trim();
--+    }
--+    const confirmResponsePromise = page.waitForResponse(
--+      (response) => {
--+        const url = response.url();
--+        if (response.request().method() !== "POST") return false;
--+        return url.includes("/confirm") || url.includes("/plan/update");
-+       if (plannerLoadResult === "fail") {
-+         throw new Error("Planner load failed banner displayed; see planner-trace.txt");
-+       }
-+@@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+       (response) => {
-+         const url = response.url();
-+         if (response.request().method() !== "POST") return false;
-+-        return url.includes("/confirm") || url.includes("/plan/update");
-++        return url.includes("/v1/suggestions/") && url.includes("/accept");
-        },
-        { timeout: 20000 }
---    )
---    .toBe(true);
---
---  const todayPlanItems = page.locator("#today-plan-items");
---  await expect(todayPlanItems).toBeVisible();
---  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
---  if (selectedTitle && planText && planText.includes(selectedTitle)) {
---    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
---  } else {
---    await expect
---      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
---      .toBeGreaterThan(0);
---  }
--+    );
--+    await targetCard.getByRole("button", { name: "Confirm" }).click();
--+    const confirmResponse = await confirmResponsePromise;
--+    let confirmText = "";
-+     );
-+@@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+       confirmText = await confirmResponse.text();
-+     } catch {}
-+     let confirmOk = confirmResponse.status() === 200;
-+-    if (confirmText.includes("\"ok\":")) {
-+-      confirmOk = confirmText.includes("\"ok\":true");
-++    let confirmJson = null;
- +    try {
--+      confirmText = await confirmResponse.text();
-++      confirmJson = JSON.parse(confirmText);
- +    } catch {}
--+    let confirmOk = confirmResponse.status() === 200;
--+    if (confirmText.includes("\"ok\":")) {
--+      confirmOk = confirmText.includes("\"ok\":true");
--+    }
--+    if (!confirmOk) {
--+      await testInfo.attach("planner-trace.txt", {
--+        body: plannerTrace.join("\n"),
--+        contentType: "text/plain",
--+      });
--+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
--+    }
-- 
---  if (consoleErrors.length) {
---    await testInfo.attach("console-errors.txt", {
---      body: consoleErrors.join("\n"),
---      contentType: "text/plain",
---    });
---  }
--+    await page.locator("#middle-tab").click();
--+    await expect(page.locator("#today-planner-view")).toBeVisible();
-- 
---  if (serverErrors.length) {
---    await testInfo.attach("server-500s.txt", {
---      body: serverErrors.join("\n"),
---      contentType: "text/plain",
---    });
---  }
--+    const todayPlanItems = page.locator("#today-plan-items");
--+    await expect(todayPlanItems).toBeVisible();
--+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
--+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
--+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
--+    } else {
--+      await expect
--+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
--+        .toBeGreaterThan(0);
--+    }
-- 
---  const criticalConsoleErrors = consoleErrors.filter((entry) => (
---    entry.includes("Uncaught") || entry.includes("TypeError")
---  ));
---  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
---  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
--+    if (consoleErrors.length) {
--+      await testInfo.attach("console-errors.txt", {
--+        body: consoleErrors.join("\n"),
--+        contentType: "text/plain",
--+      });
--+    }
--+
--+    if (serverErrors.length) {
--+      await testInfo.attach("server-500s.txt", {
--+        body: serverErrors.join("\n"),
--+        contentType: "text/plain",
--+      });
--+    }
--+
--+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
--+      entry.includes("Uncaught") || entry.includes("TypeError")
--+    ));
--+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
--+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
--+  } finally {
--+    if (plannerTrace.length) {
--+      await testInfo.attach("planner-trace.txt", {
--+        body: plannerTrace.join("\n"),
--+        contentType: "text/plain",
--+      });
--+    }
--+  }
-++    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) {
-++      confirmOk = confirmJson.ok === true;
-+     }
-+     if (!confirmOk) {
-+       await testInfo.attach("planner-trace.txt", {
-+@@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-+         contentType: "text/plain",
+-       if (plannerLoadResult === "fail") {
+-         throw new Error("Planner load failed banner displayed; see planner-trace.txt");
++       if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner invoked", {
++         view: othelloState.currentView,
++         ts: new Date().toISOString(),
++         dayViewDateYmd
 +       });
+++      abortPlannerRequests("planner-reload");
+++      plannerAbort = new AbortController();
+++      const { signal } = plannerAbort;
++       clearPlannerError();
++       plannerHeadline.textContent = "Loading...";
++       plannerEnergy.textContent = "";
++@@ -5107,7 +5230,8 @@
++         planUrl = dayViewDateYmd 
++             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
++             : `/api/today-plan?ts=${Date.now()}`;
++-        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
+++        const brief = dayViewDateYmd ? {} : await fetchTodayBrief(signal).catch((err) => {
+++          if (isAbortError(err)) throw err;
++           briefStatus = err && err.status ? err.status : null;
++           briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
++           briefParseError = err && err.parseError ? err.parseError : null;
++@@ -5118,7 +5242,7 @@
++           });
++           return {};
++         });
++-        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
+++        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include", signal });
++         planStatus = planResponse.status;
++         const planText = await planResponse.text();
++         planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
++@@ -5153,8 +5277,12 @@
++         renderPlannerSections(plan, goalTasks);
++         const currentItem = renderCurrentFocus(plan);
++         renderNextAction(plan, currentItem ? [currentItem.item_id || currentItem.id] : []);
++-        await loadTodayPlanPanel();
+++        await loadTodayPlanPanel(signal);
++       } catch (e) {
+++        if (isAbortError(e)) {
+++          logPlannerDebug("[Today Planner] load aborted", { view: othelloState.currentView });
+++          return;
+++        }
++         let httpStatus = null;
++         if (e && (e.status === 401 || e.status === 403)) {
++           await handleUnauthorized('today-planner');
++@@ -5403,11 +5531,22 @@
++         if (focusRibbon) focusRibbon.classList.remove("visible");
+        }
+-@@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-       (response) => {
+-         const url = response.url();
+-         if (response.request().method() !== "POST") return false;
+--        return url.includes("/confirm") || url.includes("/plan/update");
+-+        return url.includes("/v1/suggestions/") && url.includes("/accept");
+-       },
+-       { timeout: 20000 }
+-     );
+-@@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-       confirmText = await confirmResponse.text();
+-     } catch {}
+-     let confirmOk = confirmResponse.status() === 200;
+--    if (confirmText.includes("\"ok\":")) {
+--      confirmOk = confirmText.includes("\"ok\":true");
+-+    let confirmJson = null;
+-+    try {
+-+      confirmJson = JSON.parse(confirmText);
+-+    } catch {}
+-+    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) {
+-+      confirmOk = confirmJson.ok === true;
+-     }
+-     if (!confirmOk) {
+-       await testInfo.attach("planner-trace.txt", {
+-@@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
+-         contentType: "text/plain",
++ 
+++      if (viewName !== "today-planner") {
+++        stopPlannerPolling("view-change");
+++        abortPlannerRequests("view-change");
+++        abortWeekRequests("view-change");
+++        closeWeekDrilldown();
+++      }
+++      if (viewName !== "routine-planner") {
+++        abortRoutineRequests("view-change");
+++      }
+++
++       // Load view-specific data
++       if (viewName === "goals") {
++         renderGoalsList();
++       } else if (viewName === "today-planner") {
++         loadTodayPlanner();
+++        startPlannerPolling();
++       } else if (viewName === "insights") {
++         loadInsightsInbox();
++       } else if (viewName === "routine-planner") {
++@@ -5423,6 +5562,19 @@
+        });
+      }
+-+    await testInfo.attach("post-trace.txt", {
+-+      body: postTrace.join("\n"),
+-+      contentType: "text/plain",
++ 
+++    document.addEventListener("visibilitychange", () => {
+++      if (document.hidden) {
+++        stopPlannerPolling("hidden");
+++        abortPlannerRequests("hidden");
+++        abortWeekRequests("hidden");
+++        abortRoutineRequests("hidden");
+++        return;
+++      }
+++      if (othelloState.currentView === "today-planner") {
+++        startPlannerPolling();
+++      }
+ +    });
+-   }
+- });
+-
+++
++     // ===== MODE SWITCHER =====
++     function persistMode(mode) {
++       try {
++@@ -5651,6 +5803,11 @@
 +     }
-++    await testInfo.attach("post-trace.txt", {
-++      body: postTrace.join("\n"),
-++      contentType: "text/plain",
-++    });
-+   }
-  });
-+
++ 
++     function resetAuthBoundary(reason) {
+++      stopPlannerPolling("auth-reset");
+++      abortPlannerRequests("auth-reset");
+++      abortWeekRequests("auth-reset");
+++      abortRoutineRequests("auth-reset");
+++      closeWeekDrilldown();
++       if (connectRetryTimeout) {
++         clearTimeout(connectRetryTimeout);
++         connectRetryTimeout = null;
++@@ -7553,13 +7710,17 @@
++     }
++ 
++     async function fetchRoutines() {
+++      if (othelloState.currentView !== "routine-planner") return;
+++      if (document.hidden) return;
++       const listEl = document.getElementById("routine-list");
++       // Only show loader if we don't have data yet to avoid flicker on refresh
++       if (listEl && othelloState.routines.length === 0) {
++          listEl.innerHTML = '<div class="routine-loader">Loading routines...</div>';
++       }
++       try {
++-        const resp = await fetch(ROUTINES_API, { credentials: "include" });
+++        abortRoutineRequests("routines-reload");
+++        routinesAbort = new AbortController();
+++        const resp = await fetch(ROUTINES_API, { credentials: "include", signal: routinesAbort.signal });
++         if (!resp.ok) throw new Error("Failed to fetch routines");
++         const data = await resp.json();
++         if (data.ok) {
++@@ -7574,6 +7735,10 @@
++           }
++         }
++       } catch (err) {
+++        if (isAbortError(err)) {
+++          logPlannerDebug("[Routine Planner] fetch aborted", { reason: "routines-reload" });
+++          return;
+++        }
++         console.error("fetchRoutines error:", err);
++         showToast("Failed to load routines", "error");
++         if (listEl && othelloState.routines.length === 0) {
++@@ -7583,6 +7748,8 @@
++     }
++ 
++     async function loadRoutinePlanner() {
+++      if (othelloState.currentView !== "routine-planner") return;
+++      if (document.hidden) return;
++       await fetchRoutines();
++       renderRoutineList(othelloState.routines);
++       
 diff --git a/othello_ui.html b/othello_ui.html
-index 4ed3660c..f53dba97 100644
+index f53dba97..03a46986 100644
 --- a/othello_ui.html
 +++ b/othello_ui.html
-@@ -3073,14 +3073,30 @@
+@@ -3071,8 +3071,8 @@
+       return formatDateYYYYMMDD(d);
+     }
  
-     async function fetchTodayBrief() {
-       const resp = await fetch("/api/today-brief", { credentials: "include" });
--      if (resp.status === 401 || resp.status === 403) {
-+      const status = resp.status;
-+      const text = await resp.text();
-+      if (status === 401 || status === 403) {
-         const err = new Error("Unauthorized");
--        err.status = resp.status;
-+        err.status = status;
-         throw err;
+-    async function fetchTodayBrief() {
+-      const resp = await fetch("/api/today-brief", { credentials: "include" });
++    async function fetchTodayBrief(signal) {
++      const resp = await fetch("/api/today-brief", { credentials: "include", signal });
+       const status = resp.status;
+       const text = await resp.text();
+       if (status === 401 || status === 403) {
+@@ -3148,14 +3148,18 @@
+       }
+       return payload;
+     }
+-    async function fetchV1TodayPlan() {
+-      const payload = await v1Request("/v1/read/today", { cache: "no-store", credentials: "include" }, "Today plan");
++    async function fetchV1TodayPlan(signal) {
++      const payload = await v1Request(
++        "/v1/read/today",
++        { cache: "no-store", credentials: "include", signal },
++        "Today plan"
++      );
+       return payload?.data?.plan || {};
+     }
+-    async function fetchPlanItemSuggestions() {
++    async function fetchPlanItemSuggestions(signal) {
+       const payload = await v1Request(
+         "/v1/suggestions?status=pending&kind=plan_item&limit=20",
+-        { credentials: "include" },
++        { credentials: "include", signal },
+         "Plan suggestions"
+       );
+       return Array.isArray(payload?.data?.suggestions) ? payload.data.suggestions : [];
+@@ -3291,13 +3295,23 @@
+       }
+       return { payload: { include_rollover: true }, note: "No recent chat message found; drafting from rollover only." };
+     }
+-    async function loadTodayPlanPanel() {
++    async function loadTodayPlanPanel(signal) {
++      if (othelloState.currentView !== "today-planner") return;
++      if (document.hidden) return;
+       if (!todayPlanItems || !todayPlanSuggestions) return;
++      logPlannerDebug("[Today Planner] loadTodayPlanPanel");
+       clearTodayPlanError();
++      let panelSignal = signal;
++      if (!panelSignal) {
++        abortPlannerRequests("panel-reload");
++        plannerAbort = new AbortController();
++        panelSignal = plannerAbort.signal;
++      }
+       try {
+-        const plan = await fetchV1TodayPlan();
++        const plan = await fetchV1TodayPlan(panelSignal);
+         renderTodayPlanItems(plan);
+       } catch (e) {
++        if (isAbortError(e)) return;
+         if (e && (e.status === 401 || e.status === 403)) {
+           await handleUnauthorized('today-plan-read');
+           return;
+@@ -3305,9 +3319,10 @@
+         setTodayPlanError(e && e.message ? e.message : "Failed to load today plan.", e && e.requestId ? e.requestId : null);
        }
--      if (!resp.ok) throw new Error("Failed to load brief");
--      const data = await resp.json();
--      return data.brief || {};
-+      if (!resp.ok) {
-+        const err = new Error("Failed to load brief");
-+        err.status = status;
-+        err.bodySnippet = text.slice(0, 300);
-+        throw err;
+       try {
+-        const suggestions = await fetchPlanItemSuggestions();
++        const suggestions = await fetchPlanItemSuggestions(panelSignal);
+         renderPlanSuggestions(suggestions);
+       } catch (e) {
++        if (isAbortError(e)) return;
+         if (e && (e.status === 401 || e.status === 403)) {
+           await handleUnauthorized('today-plan-suggestions');
+           return;
+@@ -4564,6 +4579,66 @@
+     const weekViewCache = {}; 
+     let isWeekViewActive = false;
+     let dayViewDateYmd = null; // null means "today/live"
++    let plannerPollId = null;
++    let plannerAbort = null;
++    let weekAbort = null;
++    let routinesAbort = null;
++    let activeWeekDrilldownYmd = null;
++    let plannerListenersBound = false;
++    const PLANNER_POLL_MS = 60000;
++
++    function isAbortError(err) {
++      return err && (err.name === "AbortError" || err.code === 20);
++    }
++
++    function logPlannerDebug(message, payload) {
++      if (!BOOT_DEBUG) return;
++      if (payload) {
++        console.log(message, payload);
++      } else {
++        console.log(message);
 +      }
-+      let data = null;
-+      try {
-+        data = JSON.parse(text);
-+      } catch (parseErr) {
-+        const err = new Error("Failed to parse brief");
-+        err.status = status;
-+        err.bodySnippet = text.slice(0, 300);
-+        err.parseError = parseErr.message;
-+        throw err;
++    }
++
++    function abortPlannerRequests(reason) {
++      if (!plannerAbort) return;
++      plannerAbort.abort();
++      plannerAbort = null;
++      logPlannerDebug("[Today Planner] aborted in-flight request", { reason });
++    }
++
++    function abortWeekRequests(reason) {
++      if (!weekAbort) return;
++      weekAbort.abort();
++      weekAbort = null;
++      logPlannerDebug("[Week View] aborted in-flight request", { reason });
++    }
++
++    function abortRoutineRequests(reason) {
++      if (!routinesAbort) return;
++      routinesAbort.abort();
++      routinesAbort = null;
++      logPlannerDebug("[Routine Planner] aborted in-flight request", { reason });
++    }
++
++    function stopPlannerPolling(reason) {
++      if (plannerPollId) {
++        clearInterval(plannerPollId);
++        plannerPollId = null;
++        logPlannerDebug("[Today Planner] polling stopped", { reason });
 +      }
-+      return (data && data.brief) || {};
-     }
++    }
++
++    function startPlannerPolling() {
++      stopPlannerPolling("restart");
++      if (!PLANNER_POLL_MS || PLANNER_POLL_MS < 1000) return;
++      plannerPollId = setInterval(() => {
++        if (document.hidden) return;
++        if (othelloState.currentView !== "today-planner") return;
++        loadTodayPlanner();
++      }, PLANNER_POLL_MS);
++      logPlannerDebug("[Today Planner] polling started", { intervalMs: PLANNER_POLL_MS });
++    }
  
-     async function fetchTodayPlan() {
-@@ -3206,13 +3222,21 @@
-           if (!suggestion || !suggestion.id) return;
-           confirmBtn.disabled = true;
-           try {
-+            const confirmPayload = { reason: "confirm" };
-+            if (BOOT_DEBUG) {
-+              console.info("[Today Planner] confirm suggestion", {
-+                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
-+                method: "POST",
-+                payloadKeys: Object.keys(confirmPayload),
-+              });
-+            }
-             await v1Request(
-               `/v1/suggestions/${suggestion.id}/accept`,
-               {
-                 method: "POST",
-                 headers: { "Content-Type": "application/json" },
-                 credentials: "include",
--                body: JSON.stringify({ reason: "confirm" })
-+                body: JSON.stringify(confirmPayload)
-               },
-               "Confirm suggestion"
-             );
-@@ -3359,11 +3383,16 @@
-       });
+     function getWeekStartYmd(refDate = new Date()) {
+       // Monday-start, local time
+@@ -4641,12 +4716,18 @@
+         return { completed, inProgress, overdue, snoozed, tomorrow };
      }
  
--    function renderPlannerError(message, httpStatus) {
-+    function renderPlannerError(message, httpStatus, details) {
-       plannerError.style.display = "block";
-       let msg = message || "Could not load today's plan. Please try again later.";
-       if (httpStatus) msg += ` (HTTP ${httpStatus})`;
-       plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
-+      if (details) {
-+        plannerError.dataset.error = details;
-+      } else {
-+        delete plannerError.dataset.error;
-+      }
-       const retryBtn = document.getElementById("planner-retry-btn");
-       if (retryBtn) {
-         retryBtn.onclick = () => {
-@@ -5067,16 +5096,50 @@
-           };
+-    async function fetchPlanForDate(ymd) {
++    async function fetchPlanForDate(ymd, options = {}) {
++      const { signal, source } = options;
++      if (othelloState.currentView !== "today-planner") return null;
++      if (!isWeekViewActive && source !== "drilldown") return null;
+       if (weekViewCache[ymd]) return weekViewCache[ymd];
+       
+       try {
+         // Use peek=1 to prevent generation/mutation of plans during week view browsing
+-        const resp = await fetch(`/api/today-plan?plan_date=${ymd}&peek=1`, { cache: "no-store", credentials: "include" });
++        const resp = await fetch(
++          `/api/today-plan?plan_date=${ymd}&peek=1`,
++          { cache: "no-store", credentials: "include", signal }
++        );
+         if (!resp.ok) throw new Error("Failed to fetch");
+         const data = await resp.json();
+         const plan = data.plan || {};
+@@ -4655,19 +4736,34 @@
+         weekViewCache[ymd] = { plan, counts, fetchedAt: Date.now() };
+         return weekViewCache[ymd];
+       } catch (e) {
++        if (isAbortError(e)) {
++          logPlannerDebug("[Week View] fetch aborted", { ymd });
++          return null;
++        }
+         console.error(`Failed to fetch plan for ${ymd}`, e);
+         return null;
        }
+     }
  
-+      let planStatus = null;
-+      let planSnippet = null;
-+      let planParseError = null;
-+      let briefStatus = null;
-+      let briefSnippet = null;
-+      let briefParseError = null;
-+      let planUrl = null;
-       try {
--        const planUrl = dayViewDateYmd 
-+        planUrl = dayViewDateYmd 
-             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
-             : `/api/today-plan?ts=${Date.now()}`;
--            
--        const [brief, planResp] = await Promise.all([
--            dayViewDateYmd ? Promise.resolve({}) : fetchTodayBrief(), // No brief for past days
--            fetch(planUrl, { cache: "no-store", credentials: "include" }).then(r => r.json())
--        ]);
+     async function loadWeekView() {
++        if (othelloState.currentView !== "today-planner") return;
++        if (!isWeekViewActive) return;
++        if (document.hidden) return;
++        
+         const container = document.getElementById("week-view-content");
+-        if (!container) return;
++        const weekView = document.getElementById("planner-week-view");
++        if (!container || (weekView && weekView.style.display === "none")) return;
+         container.innerHTML = '<div style="padding:1rem; text-align:center; color:var(--text-soft);">Loading week...</div>';
+         
++        abortWeekRequests("week-view-reload");
++        weekAbort = new AbortController();
++        const { signal } = weekAbort;
++        logPlannerDebug("[Week View] loadWeekView invoked", { view: othelloState.currentView });
++        
+         const days = getWeekDays();
+-        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd)));
++        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd, { signal })));
+         
++        if (signal.aborted) return;
+         container.innerHTML = '';
+         
+         results.forEach((res, idx) => {
+@@ -4738,12 +4834,28 @@
+         return items;
+     }
+ 
+-    async function openWeekDrilldown(ymd) {
+-        const res = await fetchPlanForDate(ymd);
+-        if (!res) return;
 -        
-+        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
-+          briefStatus = err && err.status ? err.status : null;
-+          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
-+          briefParseError = err && err.parseError ? err.parseError : null;
-+          console.error("[Today Planner] fetchTodayBrief failed", {
-+            status: briefStatus,
-+            parseError: briefParseError,
-+            error: err && err.message,
-+          });
-+          return {};
-+        });
-+        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
-+        planStatus = planResponse.status;
-+        const planText = await planResponse.text();
-+        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
-+        if (!planResponse.ok) {
-+          const err = new Error("Failed to load plan");
-+          err.status = planStatus;
-+          err.bodySnippet = planSnippet;
-+          throw err;
-+        }
-+        let planResp = null;
-+        try {
-+          planResp = JSON.parse(planText);
-+        } catch (parseErr) {
-+          planParseError = parseErr.message;
-+          const err = new Error("Failed to parse plan");
-+          err.status = planStatus;
-+          err.bodySnippet = planSnippet;
-+          err.parseError = planParseError;
-+          throw err;
-+        }
++    function closeWeekDrilldown() {
+         const existing = document.getElementById("planner-week-drilldown");
+         if (existing) existing.remove();
++        activeWeekDrilldownYmd = null;
++        logPlannerDebug("[Week View] drilldown closed");
++    }
 +
-         const plan = planResp.plan || {};
-         const goalTasks = (plan.sections?.goal_tasks || []);
-         if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
-@@ -5103,7 +5166,25 @@
-           const match = e.message.match(/HTTP (\d+)/);
-           if (match) httpStatus = match[1];
++    async function openWeekDrilldown(ymd) {
++        if (othelloState.currentView !== "today-planner") return;
++        if (activeWeekDrilldownYmd === ymd && document.getElementById("planner-week-drilldown")) return;
++        activeWeekDrilldownYmd = ymd;
++        logPlannerDebug("[Week View] drilldown open", { ymd });
++        
++        abortWeekRequests("week-drilldown");
++        weekAbort = new AbortController();
++        const res = await fetchPlanForDate(ymd, { signal: weekAbort.signal, source: "drilldown" });
++        if (!res) {
++            activeWeekDrilldownYmd = null;
++            return;
++        }
++        
++        closeWeekDrilldown();
+         
+         const modal = document.createElement("div");
+         modal.id = "planner-week-drilldown";
+@@ -4754,7 +4866,7 @@
+         modal.style.display = "flex";
+         modal.style.alignItems = "center";
+         modal.style.justifyContent = "center";
+-        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
++        modal.onclick = (e) => { if (e.target === modal) closeWeekDrilldown(); };
+         
+         const card = document.createElement("div");
+         card.className = "planner-card";
+@@ -4777,7 +4889,7 @@
+                     <div class="planner-section__title" style="font-size:1.1rem;">${dateStr}</div>
+                     <div style="font-size:0.85rem; color:var(--text-soft); margin-top:0.2rem;">${summary}</div>
+                 </div>
+-                <button class="icon-button" style="border:none; background:transparent;" onclick="document.getElementById('planner-week-drilldown').remove()">Ã¢Å“â€¢</button>
++                <button class="icon-button" style="border:none; background:transparent;" onclick="closeWeekDrilldown()">Ã¢Å“â€¢</button>
+             </div>
+             <div style="flex:1; overflow-y:auto; padding-right:0.5rem;" id="drilldown-list"></div>
+             <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid var(--border); text-align:center;">
+@@ -4864,8 +4976,8 @@
+ 
+     function openDayViewForDate(ymd) {
+         dayViewDateYmd = ymd;
+-        const modal = document.getElementById("planner-week-drilldown");
+-        if (modal) modal.remove();
++        closeWeekDrilldown();
++        abortWeekRequests("day-view-open");
+         
+         isWeekViewActive = false;
+         document.getElementById("planner-week-view").style.display = "none";
+@@ -4883,6 +4995,7 @@
+     }
+ 
+     function toggleWeekView() {
++        if (othelloState.currentView !== "today-planner") return;
+         const weekView = document.getElementById("planner-week-view");
+         const dayView = document.getElementById("planner-day-view");
+         const btn = document.getElementById("week-view-toggle");
+@@ -4898,14 +5011,25 @@
+             weekView.style.display = "none";
+             dayView.style.display = "block";
+             btn.textContent = "Week View";
++            closeWeekDrilldown();
++            abortWeekRequests("week-view-close");
          }
--        renderPlannerError("Planner load failed", httpStatus);
-+        if (e && e.status) httpStatus = e.status;
-+        const detailParts = [];
-+        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
-+        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
-+        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
-+        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
-+        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
-+        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
-+        if (e && e.message) detailParts.push(`error:${e.message}`);
-+        const detailString = detailParts.join(" | ").slice(0, 300);
-+        console.error("[Today Planner] loadTodayPlanner failed", {
-+          planUrl,
-+          planStatus,
-+          briefStatus,
-+          planParseError,
-+          briefParseError,
-+          error: e && e.message,
-+        });
-+        renderPlannerError("Planner load failed", httpStatus, detailString);
-         if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
-       }
      }
-diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
-index e7e992f5..d48e604d 100644
---- a/tests/e2e/othello.todayplanner.routines.spec.js
-+++ b/tests/e2e/othello.todayplanner.routines.spec.js
-@@ -108,6 +108,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-   const consoleErrors = [];
-   const authTrace = [];
-   const plannerTrace = [];
-+  const postTrace = [];
+     
+-    // Initialize toggle
+-    document.addEventListener("DOMContentLoaded", () => {
++    function bindPlannerListeners() {
++        if (plannerListenersBound) return;
++        plannerListenersBound = true;
+         const btn = document.getElementById("week-view-toggle");
+         if (btn) btn.onclick = toggleWeekView;
+-    });
++        
++        const toggle = document.getElementById("suggestions-toggle");
++        if (toggle) toggle.onclick = toggleSuggestions;
++        
++        const genBtn = document.getElementById("generate-suggestions-btn");
++        if (genBtn) genBtn.onclick = generateSuggestions;
++    }
++    
++    document.addEventListener("DOMContentLoaded", bindPlannerListeners);
  
-   page.on("response", (response) => {
-     if (response.status() >= 500) {
-@@ -123,6 +124,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-       || url.includes("/v1/plan/draft")
-       || url.includes("/api/confirm")
-       || url.includes("/v1/confirm")
-+      || url.includes("/v1/suggestions/")
-       || url.includes("/api/plan/update")
-     );
-     if (!matchesPlanner) return;
-@@ -142,6 +144,26 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-     plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
-   });
+     // --- Suggestions Logic ---
+     
+@@ -5035,21 +5159,23 @@
+         }
+     }
  
-+  page.on("request", (request) => {
-+    const url = request.url();
-+    if (request.method() !== "POST") return;
-+    const matches = (
-+      url.includes("/api/confirm")
-+      || url.includes("/v1/confirm")
-+      || url.includes("/v1/suggestions/")
-+      || url.includes("/api/plan/update")
-+    );
-+    if (!matches) return;
-+    let path = url;
-+    try {
-+      const parsed = new URL(url);
-+      path = `${parsed.pathname}${parsed.search}`;
-+    } catch {}
-+    const postData = request.postData() || "";
-+    const snippet = postData.replace(/\s+/g, " ").trim().slice(0, 300);
-+    postTrace.push(`${request.method()} ${path} ${snippet}`);
-+  });
-+
-   page.on("console", (msg) => {
-     if (msg.type() === "error") {
-       consoleErrors.push(msg.text());
-@@ -225,6 +247,13 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-         body: consoleErrors.join("\n"),
-         contentType: "text/plain",
-       });
-+      const plannerErrorDetails = await page.locator("#planner-error").getAttribute("data-error");
-+      if (plannerErrorDetails) {
-+        await testInfo.attach("planner-error.txt", {
-+          body: plannerErrorDetails,
-+          contentType: "text/plain",
-+        });
+-    // Initialize suggestions
+-    document.addEventListener("DOMContentLoaded", () => {
+-        const toggle = document.getElementById("suggestions-toggle");
+-        if (toggle) toggle.onclick = toggleSuggestions;
+-        
+-        const genBtn = document.getElementById("generate-suggestions-btn");
+-        if (genBtn) genBtn.onclick = generateSuggestions;
+-    });
+-
+     async function loadTodayPlanner() {
++      if (othelloState.currentView !== "today-planner") {
++        logPlannerDebug("[Today Planner] load skipped", { view: othelloState.currentView });
++        return;
++      }
++      if (document.hidden) {
++        logPlannerDebug("[Today Planner] load skipped (hidden)", { view: othelloState.currentView });
++        return;
 +      }
-       if (plannerLoadResult === "fail") {
-         throw new Error("Planner load failed banner displayed; see planner-trace.txt");
+       if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner invoked", {
+         view: othelloState.currentView,
+         ts: new Date().toISOString(),
+         dayViewDateYmd
+       });
++      abortPlannerRequests("planner-reload");
++      plannerAbort = new AbortController();
++      const { signal } = plannerAbort;
+       clearPlannerError();
+       plannerHeadline.textContent = "Loading...";
+       plannerEnergy.textContent = "";
+@@ -5107,7 +5233,8 @@
+         planUrl = dayViewDateYmd 
+             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
+             : `/api/today-plan?ts=${Date.now()}`;
+-        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
++        const brief = dayViewDateYmd ? {} : await fetchTodayBrief(signal).catch((err) => {
++          if (isAbortError(err)) throw err;
+           briefStatus = err && err.status ? err.status : null;
+           briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
+           briefParseError = err && err.parseError ? err.parseError : null;
+@@ -5118,7 +5245,7 @@
+           });
+           return {};
+         });
+-        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
++        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include", signal });
+         planStatus = planResponse.status;
+         const planText = await planResponse.text();
+         planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
+@@ -5153,8 +5280,12 @@
+         renderPlannerSections(plan, goalTasks);
+         const currentItem = renderCurrentFocus(plan);
+         renderNextAction(plan, currentItem ? [currentItem.item_id || currentItem.id] : []);
+-        await loadTodayPlanPanel();
++        await loadTodayPlanPanel(signal);
+       } catch (e) {
++        if (isAbortError(e)) {
++          logPlannerDebug("[Today Planner] load aborted", { view: othelloState.currentView });
++          return;
++        }
+         let httpStatus = null;
+         if (e && (e.status === 401 || e.status === 403)) {
+           await handleUnauthorized('today-planner');
+@@ -5403,11 +5534,22 @@
+         if (focusRibbon) focusRibbon.classList.remove("visible");
        }
-@@ -260,7 +289,7 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-       (response) => {
-         const url = response.url();
-         if (response.request().method() !== "POST") return false;
--        return url.includes("/confirm") || url.includes("/plan/update");
-+        return url.includes("/v1/suggestions/") && url.includes("/accept");
-       },
-       { timeout: 20000 }
-     );
-@@ -271,8 +300,12 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-       confirmText = await confirmResponse.text();
-     } catch {}
-     let confirmOk = confirmResponse.status() === 200;
--    if (confirmText.includes("\"ok\":")) {
--      confirmOk = confirmText.includes("\"ok\":true");
-+    let confirmJson = null;
-+    try {
-+      confirmJson = JSON.parse(confirmText);
-+    } catch {}
-+    if (confirmJson && Object.prototype.hasOwnProperty.call(confirmJson, "ok")) {
-+      confirmOk = confirmJson.ok === true;
-     }
-     if (!confirmOk) {
-       await testInfo.attach("planner-trace.txt", {
-@@ -322,5 +355,9 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
-         contentType: "text/plain",
+ 
++      if (viewName !== "today-planner") {
++        stopPlannerPolling("view-change");
++        abortPlannerRequests("view-change");
++        abortWeekRequests("view-change");
++        closeWeekDrilldown();
++      }
++      if (viewName !== "routine-planner") {
++        abortRoutineRequests("view-change");
++      }
++
+       // Load view-specific data
+       if (viewName === "goals") {
+         renderGoalsList();
+       } else if (viewName === "today-planner") {
+         loadTodayPlanner();
++        startPlannerPolling();
+       } else if (viewName === "insights") {
+         loadInsightsInbox();
+       } else if (viewName === "routine-planner") {
+@@ -5423,6 +5565,19 @@
        });
      }
-+    await testInfo.attach("post-trace.txt", {
-+      body: postTrace.join("\n"),
-+      contentType: "text/plain",
+ 
++    document.addEventListener("visibilitychange", () => {
++      if (document.hidden) {
++        stopPlannerPolling("hidden");
++        abortPlannerRequests("hidden");
++        abortWeekRequests("hidden");
++        abortRoutineRequests("hidden");
++        return;
++      }
++      if (othelloState.currentView === "today-planner") {
++        startPlannerPolling();
++      }
 +    });
-   }
- });
-
++
+     // ===== MODE SWITCHER =====
+     function persistMode(mode) {
+       try {
+@@ -5651,6 +5806,11 @@
+     }
+ 
+     function resetAuthBoundary(reason) {
++      stopPlannerPolling("auth-reset");
++      abortPlannerRequests("auth-reset");
++      abortWeekRequests("auth-reset");
++      abortRoutineRequests("auth-reset");
++      closeWeekDrilldown();
+       if (connectRetryTimeout) {
+         clearTimeout(connectRetryTimeout);
+         connectRetryTimeout = null;
+@@ -7553,13 +7713,17 @@
+     }
+ 
+     async function fetchRoutines() {
++      if (othelloState.currentView !== "routine-planner") return;
++      if (document.hidden) return;
+       const listEl = document.getElementById("routine-list");
+       // Only show loader if we don't have data yet to avoid flicker on refresh
+       if (listEl && othelloState.routines.length === 0) {
+          listEl.innerHTML = '<div class="routine-loader">Loading routines...</div>';
+       }
+       try {
+-        const resp = await fetch(ROUTINES_API, { credentials: "include" });
++        abortRoutineRequests("routines-reload");
++        routinesAbort = new AbortController();
++        const resp = await fetch(ROUTINES_API, { credentials: "include", signal: routinesAbort.signal });
+         if (!resp.ok) throw new Error("Failed to fetch routines");
+         const data = await resp.json();
+         if (data.ok) {
+@@ -7574,6 +7738,10 @@
+           }
+         }
+       } catch (err) {
++        if (isAbortError(err)) {
++          logPlannerDebug("[Routine Planner] fetch aborted", { reason: "routines-reload" });
++          return;
++        }
+         console.error("fetchRoutines error:", err);
+         showToast("Failed to load routines", "error");
+         if (listEl && othelloState.routines.length === 0) {
+@@ -7583,6 +7751,8 @@
+     }
+ 
+     async function loadRoutinePlanner() {
++      if (othelloState.currentView !== "routine-planner") return;
++      if (document.hidden) return;
+       await fetchRoutines();
+       renderRoutineList(othelloState.routines);
+       
diff --git a/othello_ui.html b/othello_ui.html
index f53dba97..03a46986 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -3071,8 +3071,8 @@
       return formatDateYYYYMMDD(d);
     }
 
-    async function fetchTodayBrief() {
-      const resp = await fetch("/api/today-brief", { credentials: "include" });
+    async function fetchTodayBrief(signal) {
+      const resp = await fetch("/api/today-brief", { credentials: "include", signal });
       const status = resp.status;
       const text = await resp.text();
       if (status === 401 || status === 403) {
@@ -3148,14 +3148,18 @@
       }
       return payload;
     }
-    async function fetchV1TodayPlan() {
-      const payload = await v1Request("/v1/read/today", { cache: "no-store", credentials: "include" }, "Today plan");
+    async function fetchV1TodayPlan(signal) {
+      const payload = await v1Request(
+        "/v1/read/today",
+        { cache: "no-store", credentials: "include", signal },
+        "Today plan"
+      );
       return payload?.data?.plan || {};
     }
-    async function fetchPlanItemSuggestions() {
+    async function fetchPlanItemSuggestions(signal) {
       const payload = await v1Request(
         "/v1/suggestions?status=pending&kind=plan_item&limit=20",
-        { credentials: "include" },
+        { credentials: "include", signal },
         "Plan suggestions"
       );
       return Array.isArray(payload?.data?.suggestions) ? payload.data.suggestions : [];
@@ -3291,13 +3295,23 @@
       }
       return { payload: { include_rollover: true }, note: "No recent chat message found; drafting from rollover only." };
     }
-    async function loadTodayPlanPanel() {
+    async function loadTodayPlanPanel(signal) {
+      if (othelloState.currentView !== "today-planner") return;
+      if (document.hidden) return;
       if (!todayPlanItems || !todayPlanSuggestions) return;
+      logPlannerDebug("[Today Planner] loadTodayPlanPanel");
       clearTodayPlanError();
+      let panelSignal = signal;
+      if (!panelSignal) {
+        abortPlannerRequests("panel-reload");
+        plannerAbort = new AbortController();
+        panelSignal = plannerAbort.signal;
+      }
       try {
-        const plan = await fetchV1TodayPlan();
+        const plan = await fetchV1TodayPlan(panelSignal);
         renderTodayPlanItems(plan);
       } catch (e) {
+        if (isAbortError(e)) return;
         if (e && (e.status === 401 || e.status === 403)) {
           await handleUnauthorized('today-plan-read');
           return;
@@ -3305,9 +3319,10 @@
         setTodayPlanError(e && e.message ? e.message : "Failed to load today plan.", e && e.requestId ? e.requestId : null);
       }
       try {
-        const suggestions = await fetchPlanItemSuggestions();
+        const suggestions = await fetchPlanItemSuggestions(panelSignal);
         renderPlanSuggestions(suggestions);
       } catch (e) {
+        if (isAbortError(e)) return;
         if (e && (e.status === 401 || e.status === 403)) {
           await handleUnauthorized('today-plan-suggestions');
           return;
@@ -4564,6 +4579,66 @@
     const weekViewCache = {}; 
     let isWeekViewActive = false;
     let dayViewDateYmd = null; // null means "today/live"
+    let plannerPollId = null;
+    let plannerAbort = null;
+    let weekAbort = null;
+    let routinesAbort = null;
+    let activeWeekDrilldownYmd = null;
+    let plannerListenersBound = false;
+    const PLANNER_POLL_MS = 60000;
+
+    function isAbortError(err) {
+      return err && (err.name === "AbortError" || err.code === 20);
+    }
+
+    function logPlannerDebug(message, payload) {
+      if (!BOOT_DEBUG) return;
+      if (payload) {
+        console.log(message, payload);
+      } else {
+        console.log(message);
+      }
+    }
+
+    function abortPlannerRequests(reason) {
+      if (!plannerAbort) return;
+      plannerAbort.abort();
+      plannerAbort = null;
+      logPlannerDebug("[Today Planner] aborted in-flight request", { reason });
+    }
+
+    function abortWeekRequests(reason) {
+      if (!weekAbort) return;
+      weekAbort.abort();
+      weekAbort = null;
+      logPlannerDebug("[Week View] aborted in-flight request", { reason });
+    }
+
+    function abortRoutineRequests(reason) {
+      if (!routinesAbort) return;
+      routinesAbort.abort();
+      routinesAbort = null;
+      logPlannerDebug("[Routine Planner] aborted in-flight request", { reason });
+    }
+
+    function stopPlannerPolling(reason) {
+      if (plannerPollId) {
+        clearInterval(plannerPollId);
+        plannerPollId = null;
+        logPlannerDebug("[Today Planner] polling stopped", { reason });
+      }
+    }
+
+    function startPlannerPolling() {
+      stopPlannerPolling("restart");
+      if (!PLANNER_POLL_MS || PLANNER_POLL_MS < 1000) return;
+      plannerPollId = setInterval(() => {
+        if (document.hidden) return;
+        if (othelloState.currentView !== "today-planner") return;
+        loadTodayPlanner();
+      }, PLANNER_POLL_MS);
+      logPlannerDebug("[Today Planner] polling started", { intervalMs: PLANNER_POLL_MS });
+    }
 
     function getWeekStartYmd(refDate = new Date()) {
       // Monday-start, local time
@@ -4641,12 +4716,18 @@
         return { completed, inProgress, overdue, snoozed, tomorrow };
     }
 
-    async function fetchPlanForDate(ymd) {
+    async function fetchPlanForDate(ymd, options = {}) {
+      const { signal, source } = options;
+      if (othelloState.currentView !== "today-planner") return null;
+      if (!isWeekViewActive && source !== "drilldown") return null;
       if (weekViewCache[ymd]) return weekViewCache[ymd];
       
       try {
         // Use peek=1 to prevent generation/mutation of plans during week view browsing
-        const resp = await fetch(`/api/today-plan?plan_date=${ymd}&peek=1`, { cache: "no-store", credentials: "include" });
+        const resp = await fetch(
+          `/api/today-plan?plan_date=${ymd}&peek=1`,
+          { cache: "no-store", credentials: "include", signal }
+        );
         if (!resp.ok) throw new Error("Failed to fetch");
         const data = await resp.json();
         const plan = data.plan || {};
@@ -4655,19 +4736,34 @@
         weekViewCache[ymd] = { plan, counts, fetchedAt: Date.now() };
         return weekViewCache[ymd];
       } catch (e) {
+        if (isAbortError(e)) {
+          logPlannerDebug("[Week View] fetch aborted", { ymd });
+          return null;
+        }
         console.error(`Failed to fetch plan for ${ymd}`, e);
         return null;
       }
     }
 
     async function loadWeekView() {
+        if (othelloState.currentView !== "today-planner") return;
+        if (!isWeekViewActive) return;
+        if (document.hidden) return;
+        
         const container = document.getElementById("week-view-content");
-        if (!container) return;
+        const weekView = document.getElementById("planner-week-view");
+        if (!container || (weekView && weekView.style.display === "none")) return;
         container.innerHTML = '<div style="padding:1rem; text-align:center; color:var(--text-soft);">Loading week...</div>';
         
+        abortWeekRequests("week-view-reload");
+        weekAbort = new AbortController();
+        const { signal } = weekAbort;
+        logPlannerDebug("[Week View] loadWeekView invoked", { view: othelloState.currentView });
+        
         const days = getWeekDays();
-        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd)));
+        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd, { signal })));
         
+        if (signal.aborted) return;
         container.innerHTML = '';
         
         results.forEach((res, idx) => {
@@ -4738,12 +4834,28 @@
         return items;
     }
 
-    async function openWeekDrilldown(ymd) {
-        const res = await fetchPlanForDate(ymd);
-        if (!res) return;
-        
+    function closeWeekDrilldown() {
         const existing = document.getElementById("planner-week-drilldown");
         if (existing) existing.remove();
+        activeWeekDrilldownYmd = null;
+        logPlannerDebug("[Week View] drilldown closed");
+    }
+
+    async function openWeekDrilldown(ymd) {
+        if (othelloState.currentView !== "today-planner") return;
+        if (activeWeekDrilldownYmd === ymd && document.getElementById("planner-week-drilldown")) return;
+        activeWeekDrilldownYmd = ymd;
+        logPlannerDebug("[Week View] drilldown open", { ymd });
+        
+        abortWeekRequests("week-drilldown");
+        weekAbort = new AbortController();
+        const res = await fetchPlanForDate(ymd, { signal: weekAbort.signal, source: "drilldown" });
+        if (!res) {
+            activeWeekDrilldownYmd = null;
+            return;
+        }
+        
+        closeWeekDrilldown();
         
         const modal = document.createElement("div");
         modal.id = "planner-week-drilldown";
@@ -4754,7 +4866,7 @@
         modal.style.display = "flex";
         modal.style.alignItems = "center";
         modal.style.justifyContent = "center";
-        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
+        modal.onclick = (e) => { if (e.target === modal) closeWeekDrilldown(); };
         
         const card = document.createElement("div");
         card.className = "planner-card";
@@ -4777,7 +4889,7 @@
                     <div class="planner-section__title" style="font-size:1.1rem;">${dateStr}</div>
                     <div style="font-size:0.85rem; color:var(--text-soft); margin-top:0.2rem;">${summary}</div>
                 </div>
-                <button class="icon-button" style="border:none; background:transparent;" onclick="document.getElementById('planner-week-drilldown').remove()">âœ•</button>
+                <button class="icon-button" style="border:none; background:transparent;" onclick="closeWeekDrilldown()">âœ•</button>
             </div>
             <div style="flex:1; overflow-y:auto; padding-right:0.5rem;" id="drilldown-list"></div>
             <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid var(--border); text-align:center;">
@@ -4864,8 +4976,8 @@
 
     function openDayViewForDate(ymd) {
         dayViewDateYmd = ymd;
-        const modal = document.getElementById("planner-week-drilldown");
-        if (modal) modal.remove();
+        closeWeekDrilldown();
+        abortWeekRequests("day-view-open");
         
         isWeekViewActive = false;
         document.getElementById("planner-week-view").style.display = "none";
@@ -4883,6 +4995,7 @@
     }
 
     function toggleWeekView() {
+        if (othelloState.currentView !== "today-planner") return;
         const weekView = document.getElementById("planner-week-view");
         const dayView = document.getElementById("planner-day-view");
         const btn = document.getElementById("week-view-toggle");
@@ -4898,14 +5011,25 @@
             weekView.style.display = "none";
             dayView.style.display = "block";
             btn.textContent = "Week View";
+            closeWeekDrilldown();
+            abortWeekRequests("week-view-close");
         }
     }
     
-    // Initialize toggle
-    document.addEventListener("DOMContentLoaded", () => {
+    function bindPlannerListeners() {
+        if (plannerListenersBound) return;
+        plannerListenersBound = true;
         const btn = document.getElementById("week-view-toggle");
         if (btn) btn.onclick = toggleWeekView;
-    });
+        
+        const toggle = document.getElementById("suggestions-toggle");
+        if (toggle) toggle.onclick = toggleSuggestions;
+        
+        const genBtn = document.getElementById("generate-suggestions-btn");
+        if (genBtn) genBtn.onclick = generateSuggestions;
+    }
+    
+    document.addEventListener("DOMContentLoaded", bindPlannerListeners);
 
     // --- Suggestions Logic ---
     
@@ -5035,21 +5159,23 @@
         }
     }
 
-    // Initialize suggestions
-    document.addEventListener("DOMContentLoaded", () => {
-        const toggle = document.getElementById("suggestions-toggle");
-        if (toggle) toggle.onclick = toggleSuggestions;
-        
-        const genBtn = document.getElementById("generate-suggestions-btn");
-        if (genBtn) genBtn.onclick = generateSuggestions;
-    });
-
     async function loadTodayPlanner() {
+      if (othelloState.currentView !== "today-planner") {
+        logPlannerDebug("[Today Planner] load skipped", { view: othelloState.currentView });
+        return;
+      }
+      if (document.hidden) {
+        logPlannerDebug("[Today Planner] load skipped (hidden)", { view: othelloState.currentView });
+        return;
+      }
       if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner invoked", {
         view: othelloState.currentView,
         ts: new Date().toISOString(),
         dayViewDateYmd
       });
+      abortPlannerRequests("planner-reload");
+      plannerAbort = new AbortController();
+      const { signal } = plannerAbort;
       clearPlannerError();
       plannerHeadline.textContent = "Loading...";
       plannerEnergy.textContent = "";
@@ -5107,7 +5233,8 @@
         planUrl = dayViewDateYmd 
             ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
             : `/api/today-plan?ts=${Date.now()}`;
-        const brief = dayViewDateYmd ? {} : await fetchTodayBrief().catch((err) => {
+        const brief = dayViewDateYmd ? {} : await fetchTodayBrief(signal).catch((err) => {
+          if (isAbortError(err)) throw err;
           briefStatus = err && err.status ? err.status : null;
           briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
           briefParseError = err && err.parseError ? err.parseError : null;
@@ -5118,7 +5245,7 @@
           });
           return {};
         });
-        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include" });
+        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include", signal });
         planStatus = planResponse.status;
         const planText = await planResponse.text();
         planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
@@ -5153,8 +5280,12 @@
         renderPlannerSections(plan, goalTasks);
         const currentItem = renderCurrentFocus(plan);
         renderNextAction(plan, currentItem ? [currentItem.item_id || currentItem.id] : []);
-        await loadTodayPlanPanel();
+        await loadTodayPlanPanel(signal);
       } catch (e) {
+        if (isAbortError(e)) {
+          logPlannerDebug("[Today Planner] load aborted", { view: othelloState.currentView });
+          return;
+        }
         let httpStatus = null;
         if (e && (e.status === 401 || e.status === 403)) {
           await handleUnauthorized('today-planner');
@@ -5403,11 +5534,22 @@
         if (focusRibbon) focusRibbon.classList.remove("visible");
       }
 
+      if (viewName !== "today-planner") {
+        stopPlannerPolling("view-change");
+        abortPlannerRequests("view-change");
+        abortWeekRequests("view-change");
+        closeWeekDrilldown();
+      }
+      if (viewName !== "routine-planner") {
+        abortRoutineRequests("view-change");
+      }
+
       // Load view-specific data
       if (viewName === "goals") {
         renderGoalsList();
       } else if (viewName === "today-planner") {
         loadTodayPlanner();
+        startPlannerPolling();
       } else if (viewName === "insights") {
         loadInsightsInbox();
       } else if (viewName === "routine-planner") {
@@ -5423,6 +5565,19 @@
       });
     }
 
+    document.addEventListener("visibilitychange", () => {
+      if (document.hidden) {
+        stopPlannerPolling("hidden");
+        abortPlannerRequests("hidden");
+        abortWeekRequests("hidden");
+        abortRoutineRequests("hidden");
+        return;
+      }
+      if (othelloState.currentView === "today-planner") {
+        startPlannerPolling();
+      }
+    });
+
     // ===== MODE SWITCHER =====
     function persistMode(mode) {
       try {
@@ -5651,6 +5806,11 @@
     }
 
     function resetAuthBoundary(reason) {
+      stopPlannerPolling("auth-reset");
+      abortPlannerRequests("auth-reset");
+      abortWeekRequests("auth-reset");
+      abortRoutineRequests("auth-reset");
+      closeWeekDrilldown();
       if (connectRetryTimeout) {
         clearTimeout(connectRetryTimeout);
         connectRetryTimeout = null;
@@ -7553,13 +7713,17 @@
     }
 
     async function fetchRoutines() {
+      if (othelloState.currentView !== "routine-planner") return;
+      if (document.hidden) return;
       const listEl = document.getElementById("routine-list");
       // Only show loader if we don't have data yet to avoid flicker on refresh
       if (listEl && othelloState.routines.length === 0) {
          listEl.innerHTML = '<div class="routine-loader">Loading routines...</div>';
       }
       try {
-        const resp = await fetch(ROUTINES_API, { credentials: "include" });
+        abortRoutineRequests("routines-reload");
+        routinesAbort = new AbortController();
+        const resp = await fetch(ROUTINES_API, { credentials: "include", signal: routinesAbort.signal });
         if (!resp.ok) throw new Error("Failed to fetch routines");
         const data = await resp.json();
         if (data.ok) {
@@ -7574,6 +7738,10 @@
           }
         }
       } catch (err) {
+        if (isAbortError(err)) {
+          logPlannerDebug("[Routine Planner] fetch aborted", { reason: "routines-reload" });
+          return;
+        }
         console.error("fetchRoutines error:", err);
         showToast("Failed to load routines", "error");
         if (listEl && othelloState.routines.length === 0) {
@@ -7583,6 +7751,8 @@
     }
 
     async function loadRoutinePlanner() {
+      if (othelloState.currentView !== "routine-planner") return;
+      if (document.hidden) return;
       await fetchRoutines();
       renderRoutineList(othelloState.routines);
       
