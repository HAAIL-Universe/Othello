Cycle Status: STOPPED:CONTRACT_CONFLICT
Todo Ledger:
- Planned: Harden routine step creation, capture planner/confirm network traces, rerun E2E once.
- Completed: Made step inputs robust; added planner trace + planner load failure detection; confirm waits on POST /confirm or /plan/update; ran E2E; captured evidence.
- Remaining: Diagnose why Planner load failed banner appears despite 200 responses, and why confirm POST is not observed; fix backend/UI deterministically and rerun.

Next Action: Investigate Today Planner load error path (fetchTodayBrief/plan render) and confirm POST wiring on Render; fix root cause, then rerun E2E.

diff --git a/evidence/e2e_run.md b/evidence/e2e_run.md
index 45518278..3fd145c5 100644
--- a/evidence/e2e_run.md
+++ b/evidence/e2e_run.md
@@ -1,38 +1,39 @@
-Date/Time: 2026-01-03 17:02:21 +00:00
+Date/Time: 2026-01-03 17:35:21 +00:00
 
 Commands:
-- npm install
-- npx playwright install --with-deps
 - OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e
-- OTHELLO_BASE_URL="https://othello-kk2z.onrender.com/" OTHELLO_ACCESS_CODE="******69" npm run e2e (after selector fix for Chat tab)
+- POST /api/auth/login, GET /api/today-brief, GET /api/today-plan (PowerShell Invoke-WebRequest)
 
 Env Vars:
 - OTHELLO_BASE_URL=https://othello-kk2z.onrender.com/
 - OTHELLO_ACCESS_CODE=******69
 
+Auth probe summary (manual):
+- /api/auth/login -> 200 {"auth_mode":"login_key","ok":true,"user_id":"1"}
+- /api/today-brief -> 200 {"brief":{...}}
+- /api/today-plan -> 200 {"plan":{...}}
+
 Result: FAIL
 
-Failure 1 (initial run):
-- Assertion: expect(locator).toBeVisible for getByRole('button', { name: 'Chat' }) strict mode violation
-- Location: tests/e2e/othello.todayplanner.routines.spec.js:14
-- Artifacts:
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
-
-Failure 2 (rerun after selector change):
-- Timeout: locator.click on #mode-toggle; login overlay intercepts pointer events
-- Secondary: login overlay still visible after 20s (retry #1)
-- Locations:
-  - tests/e2e/othello.todayplanner.routines.spec.js:19
-  - tests/e2e/othello.todayplanner.routines.spec.js:15
-- Artifacts:
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
-  - test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
-
-Server 500s: Not evaluated (test timed out before assertion stage).
-Console errors: Not evaluated; none surfaced in runner output.
+Failure (attempt #1):
+- Error: Planner load failed banner displayed; see planner-trace.txt
+- Location: tests/e2e/othello.todayplanner.routines.spec.js:229
+
+Failure (retry #1):
+- Error: waitForResponse timeout waiting for POST /confirm or /plan/update
+- Location: tests/e2e/othello.todayplanner.routines.spec.js:259
+
+Planner trace highlights:
+- GET /api/today-plan?ts=1767461627203 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+- GET /api/today-plan?ts=1767461630717 200 {"plan":{"_plan_source":"db","behavior_profile":{"momentum":{},"routine_stats":{},"section_density":{},"skip_rate_by_kind":{},"throughput_by_effort":{"heavy":0,"light":0,"medium":0}},"capacity_model":{"heavy":1,"light":2,"medium":1},"date":"2026-01-03"...
+
+Server 500s: Not captured by Playwright listener on this run.
+Critical console errors: Not captured by Playwright listener on this run.
+
+Artifacts:
+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/test-failed-1.png
+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/trace.zip
+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion/error-context.md
+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/test-failed-1.png
+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/trace.zip
+- test-results/othello.todayplanner.routi-261c6-s-Plan---Confirm-Suggestion-retry1/error-context.md
diff --git a/tests/e2e/othello.todayplanner.routines.spec.js b/tests/e2e/othello.todayplanner.routines.spec.js
index 5abbeab8..e7e992f5 100644
--- a/tests/e2e/othello.todayplanner.routines.spec.js
+++ b/tests/e2e/othello.todayplanner.routines.spec.js
@@ -3,16 +3,84 @@ const { test, expect } = require("@playwright/test");
 const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
 const STEP_TITLES = ["Breakfast", "Shower"];
 
-async function login(page, accessCode) {
+async function recordAuthTrace(label, response, authTrace) {
+  let status = "NO_RESPONSE";
+  let bodyText = "";
+  if (response) {
+    status = response.status();
+    try {
+      bodyText = await response.text();
+    } catch (err) {
+      bodyText = `READ_ERROR: ${err.message}`;
+    }
+  }
+  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
+  authTrace.push(`${label} ${status} ${snippet}`);
+  return { status, snippet, text: bodyText };
+}
+
+async function login(page, accessCode, baseURL, testInfo, authTrace) {
   const loginInput = page.locator("#login-pin");
   const loginOverlay = page.locator("#login-overlay");
-  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
+  const loginForm = page.locator("#loginForm");
+  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
+    failOnStatusCode: false,
+  });
+  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
+  let preAuthData = null;
+  try {
+    preAuthData = JSON.parse(preAuthResult.text || "");
+  } catch {}
+  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
   if (needsLogin) {
+    await loginInput.waitFor({ state: "visible", timeout: 20000 });
+    const loginResponsePromise = page.waitForResponse(
+      (response) => response.url().includes("/api/auth/login"),
+      { timeout: 20000 }
+    ).catch(() => null);
     await loginInput.fill(accessCode);
     await page.locator("#login-btn").click();
+    const loginResponse = await loginResponsePromise;
+    if (loginResponse) {
+      await recordAuthTrace("auth/login", loginResponse, authTrace);
+    } else {
+      authTrace.push("auth/login NO_RESPONSE");
+    }
   }
-  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
+
+  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
+    failOnStatusCode: false,
+  });
+  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
+  let meData = null;
+  try {
+    meData = JSON.parse(meResult.text || "");
+  } catch {}
+  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));
+
+  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
+    failOnStatusCode: false,
+  });
+  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);
+
+  if (meResult.status !== 200 || !isAuthed) {
+    await testInfo.attach("auth-debug.txt", {
+      body: authTrace.join("\n"),
+      contentType: "text/plain",
+    });
+    throw new Error(
+      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
+    );
+  }
+
   await expect(loginOverlay).toBeHidden({ timeout: 20000 });
+  const overlayCount = await loginOverlay.count();
+  if (overlayCount > 0) {
+    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
+  } else {
+    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
+  }
+  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
 }
 
 async function switchMode(page, label) {
@@ -38,6 +106,8 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
 
   const serverErrors = [];
   const consoleErrors = [];
+  const authTrace = [];
+  const plannerTrace = [];
 
   page.on("response", (response) => {
     if (response.status() >= 500) {
@@ -45,6 +115,33 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
     }
   });
 
+  page.on("response", async (response) => {
+    const url = response.url();
+    const matchesPlanner = (
+      url.includes("/api/today-plan")
+      || url.includes("/api/today-brief")
+      || url.includes("/v1/plan/draft")
+      || url.includes("/api/confirm")
+      || url.includes("/v1/confirm")
+      || url.includes("/api/plan/update")
+    );
+    if (!matchesPlanner) return;
+    const request = response.request();
+    let path = url;
+    try {
+      const parsed = new URL(url);
+      path = `${parsed.pathname}${parsed.search}`;
+    } catch {}
+    let bodyText = "";
+    try {
+      bodyText = await response.text();
+    } catch (err) {
+      bodyText = `READ_ERROR: ${err.message}`;
+    }
+    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
+    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
+  });
+
   page.on("console", (msg) => {
     if (msg.type() === "error") {
       consoleErrors.push(msg.text());
@@ -55,117 +152,175 @@ test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, tes
     consoleErrors.push(`pageerror: ${err.message}`);
   });
 
-  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
-  await login(page, accessCode);
+  try {
+    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
+    await login(page, accessCode, baseURL, testInfo, authTrace);
 
-  await switchMode(page, "Routine Planner");
-  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();
+    await switchMode(page, "Routine Planner");
+    await page.locator("#middle-tab").click();
+    await expect(page.locator("#routine-planner-view")).toBeVisible();
 
-  page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
-  await page.locator("#routine-add-btn").click();
-  await page.locator("#routine-title-input").fill(ROUTINE_NAME);
+    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
+    await page.locator("#routine-add-btn").click();
+    await page.locator("#routine-title-input").fill(ROUTINE_NAME);
 
-  await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
+    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });
 
-  const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
-  for (const day of days) {
-    await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
-      .locator("input[type=checkbox]")
-      .check();
-  }
+    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
+    for (const day of days) {
+      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
+        .locator("input[type=checkbox]")
+        .check();
+    }
 
-  const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
-  await expect(timeInputs.first()).toBeVisible();
-  await timeInputs.first().fill("06:00");
+    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
+    await expect(timeInputs.first()).toBeVisible();
+    await timeInputs.first().fill("06:00");
 
-  const addStepBtn = page.locator("#routine-add-step-btn");
-  await addStepBtn.click();
-  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
-  await addStepBtn.click();
-  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });
+    const addStepBtn = page.locator("#routine-add-step-btn");
+    const stepInputs = page.locator("#routine-steps input[type=text]");
+    let stepCount = await stepInputs.count();
+    while (stepCount < 2) {
+      await addStepBtn.click();
+      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
+      stepCount = await stepInputs.count();
+    }
+    const emptyIndices = [];
+    for (let i = 0; i < stepCount; i++) {
+      const value = await stepInputs.nth(i).inputValue();
+      if (!value.trim()) {
+        emptyIndices.push(i);
+      }
+    }
+    let targetIndices = [];
+    if (emptyIndices.length >= 2) {
+      targetIndices = emptyIndices.slice(0, 2);
+    } else {
+      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
+    }
+    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
+    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);
 
-  const stepInputs = page.locator("#routine-steps input[type=text]");
-  await stepInputs.nth(0).fill(STEP_TITLES[0]);
-  await stepInputs.nth(1).fill(STEP_TITLES[1]);
+    await page.locator("#routine-save-btn").click();
+    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
 
-  await page.locator("#routine-save-btn").click();
-  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });
+    await switchMode(page, "Today Planner");
 
-  await switchMode(page, "Today Planner");
+    await page.locator("#middle-tab").click();
+    await expect(page.locator("#today-planner-view")).toBeVisible();
+    const plannerFailedBanner = page.getByText("Planner load failed");
+    const plannerLoadResult = await Promise.race([
+      page.waitForResponse(
+        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
+        { timeout: 20000 }
+      ).then(() => "ok").catch(() => null),
+      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
+    ]);
+    if (plannerLoadResult !== "ok") {
+      await testInfo.attach("planner-trace.txt", {
+        body: plannerTrace.join("\n"),
+        contentType: "text/plain",
+      });
+      await testInfo.attach("console-errors.txt", {
+        body: consoleErrors.join("\n"),
+        contentType: "text/plain",
+      });
+      if (plannerLoadResult === "fail") {
+        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
+      }
+      throw new Error("Planner load did not complete; see planner-trace.txt");
+    }
+    await expect(page.locator("#build-plan-btn")).toBeVisible();
+    await page.locator("#build-plan-btn").click();
 
-  await page.locator("#middle-tab").click();
-  await expect(page.locator("#today-planner-view")).toBeVisible();
-  await expect(page.locator("#build-plan-btn")).toBeVisible();
-  await page.locator("#build-plan-btn").click();
+    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
+    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
+    const pendingCount = await suggestionsList.count();
 
-  const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
-  await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
-  const pendingCount = await suggestionsList.count();
+    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
+    if (await targetCard.count() === 0) {
+      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
+    }
+    const targetCount = await targetCard.count();
+    expect(
+      targetCount,
+      "Expected at least one routine-related suggestion (name match or routine- fallback)."
+    ).toBeGreaterThan(0);
 
-  let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
-  if (await targetCard.count() === 0) {
-    targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
-  }
-  const targetCount = await targetCard.count();
-  expect(
-    targetCount,
-    "Expected at least one routine-related suggestion (name match or routine- fallback)."
-  ).toBeGreaterThan(0);
-
-  targetCard = targetCard.first();
-  let selectedTitle = "";
-  const titleLocator = targetCard.locator(".planner-block__title");
-  if (await titleLocator.count()) {
-    selectedTitle = (await titleLocator.first().innerText()).trim();
-  }
-  if (!selectedTitle) {
-    selectedTitle = ((await targetCard.textContent()) || "").trim();
-  }
-  await targetCard.getByRole("button", { name: "Confirm" }).click();
-
-  await expect
-    .poll(
-      async () => {
-        const currentCount = await suggestionsList.count();
-        if (currentCount < pendingCount) return true;
-        if (selectedTitle) {
-          const panelText = await page.locator("#today-plan-suggestions").textContent();
-          return panelText ? !panelText.includes(selectedTitle) : false;
-        }
-        return false;
+    targetCard = targetCard.first();
+    let selectedTitle = "";
+    const titleLocator = targetCard.locator(".planner-block__title");
+    if (await titleLocator.count()) {
+      selectedTitle = (await titleLocator.first().innerText()).trim();
+    }
+    if (!selectedTitle) {
+      selectedTitle = ((await targetCard.textContent()) || "").trim();
+    }
+    const confirmResponsePromise = page.waitForResponse(
+      (response) => {
+        const url = response.url();
+        if (response.request().method() !== "POST") return false;
+        return url.includes("/confirm") || url.includes("/plan/update");
       },
       { timeout: 20000 }
-    )
-    .toBe(true);
-
-  const todayPlanItems = page.locator("#today-plan-items");
-  await expect(todayPlanItems).toBeVisible();
-  const planText = selectedTitle ? await todayPlanItems.textContent() : "";
-  if (selectedTitle && planText && planText.includes(selectedTitle)) {
-    await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
-  } else {
-    await expect
-      .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
-      .toBeGreaterThan(0);
-  }
+    );
+    await targetCard.getByRole("button", { name: "Confirm" }).click();
+    const confirmResponse = await confirmResponsePromise;
+    let confirmText = "";
+    try {
+      confirmText = await confirmResponse.text();
+    } catch {}
+    let confirmOk = confirmResponse.status() === 200;
+    if (confirmText.includes("\"ok\":")) {
+      confirmOk = confirmText.includes("\"ok\":true");
+    }
+    if (!confirmOk) {
+      await testInfo.attach("planner-trace.txt", {
+        body: plannerTrace.join("\n"),
+        contentType: "text/plain",
+      });
+      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
+    }
 
-  if (consoleErrors.length) {
-    await testInfo.attach("console-errors.txt", {
-      body: consoleErrors.join("\n"),
-      contentType: "text/plain",
-    });
-  }
+    await page.locator("#middle-tab").click();
+    await expect(page.locator("#today-planner-view")).toBeVisible();
 
-  if (serverErrors.length) {
-    await testInfo.attach("server-500s.txt", {
-      body: serverErrors.join("\n"),
-      contentType: "text/plain",
-    });
-  }
+    const todayPlanItems = page.locator("#today-plan-items");
+    await expect(todayPlanItems).toBeVisible();
+    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
+    if (selectedTitle && planText && planText.includes(selectedTitle)) {
+      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
+    } else {
+      await expect
+        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
+        .toBeGreaterThan(0);
+    }
 
-  const criticalConsoleErrors = consoleErrors.filter((entry) => (
-    entry.includes("Uncaught") || entry.includes("TypeError")
-  ));
-  expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
-  expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
+    if (consoleErrors.length) {
+      await testInfo.attach("console-errors.txt", {
+        body: consoleErrors.join("\n"),
+        contentType: "text/plain",
+      });
+    }
+
+    if (serverErrors.length) {
+      await testInfo.attach("server-500s.txt", {
+        body: serverErrors.join("\n"),
+        contentType: "text/plain",
+      });
+    }
+
+    const criticalConsoleErrors = consoleErrors.filter((entry) => (
+      entry.includes("Uncaught") || entry.includes("TypeError")
+    ));
+    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
+    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
+  } finally {
+    if (plannerTrace.length) {
+      await testInfo.attach("planner-trace.txt", {
+        body: plannerTrace.join("\n"),
+        contentType: "text/plain",
+      });
+    }
+  }
 });
