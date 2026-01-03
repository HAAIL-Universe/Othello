const { test, expect } = require("@playwright/test");

const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
const STEP_TITLES = ["Breakfast", "Shower"];

async function recordAuthTrace(label, response, authTrace) {
  let status = "NO_RESPONSE";
  let bodyText = "";
  if (response) {
    status = response.status();
    try {
      bodyText = await response.text();
    } catch (err) {
      bodyText = `READ_ERROR: ${err.message}`;
    }
  }
  const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
  authTrace.push(`${label} ${status} ${snippet}`);
  return { status, snippet, text: bodyText };
}

async function login(page, accessCode, baseURL, testInfo, authTrace) {
  const loginInput = page.locator("#login-pin");
  const loginOverlay = page.locator("#login-overlay");
  const loginForm = page.locator("#loginForm");
  const preAuthResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
    failOnStatusCode: false,
  });
  const preAuthResult = await recordAuthTrace("auth/me pre", preAuthResponse, authTrace);
  let preAuthData = null;
  try {
    preAuthData = JSON.parse(preAuthResult.text || "");
  } catch {}
  const needsLogin = !Boolean(preAuthData && (preAuthData.authed || preAuthData.authenticated));
  if (needsLogin) {
    await loginInput.waitFor({ state: "visible", timeout: 20000 });
    const loginResponsePromise = page.waitForResponse(
      (response) => response.url().includes("/api/auth/login"),
      { timeout: 20000 }
    ).catch(() => null);
    await loginInput.fill(accessCode);
    await page.locator("#login-btn").click();
    const loginResponse = await loginResponsePromise;
    if (loginResponse) {
      await recordAuthTrace("auth/login", loginResponse, authTrace);
    } else {
      authTrace.push("auth/login NO_RESPONSE");
    }
  }

  const meResponse = await page.request.get(new URL("/api/auth/me", baseURL).toString(), {
    failOnStatusCode: false,
  });
  const meResult = await recordAuthTrace("auth/me post", meResponse, authTrace);
  let meData = null;
  try {
    meData = JSON.parse(meResult.text || "");
  } catch {}
  const isAuthed = Boolean(meData && (meData.authed || meData.authenticated));

  const capabilitiesResponse = await page.request.get(new URL("/api/capabilities", baseURL).toString(), {
    failOnStatusCode: false,
  });
  await recordAuthTrace("capabilities", capabilitiesResponse, authTrace);

  if (meResult.status !== 200 || !isAuthed) {
    await testInfo.attach("auth-debug.txt", {
      body: authTrace.join("\n"),
      contentType: "text/plain",
    });
    throw new Error(
      `Auth check failed: /api/auth/me status ${meResult.status} authed=${isAuthed}`
    );
  }

  await expect(loginOverlay).toBeHidden({ timeout: 20000 });
  const overlayCount = await loginOverlay.count();
  if (overlayCount > 0) {
    await expect(loginOverlay).toHaveCSS("pointer-events", "none", { timeout: 20000 });
  } else {
    await expect(loginForm).toHaveCount(0, { timeout: 20000 });
  }
  await expect(page.locator('button[data-view="chat"]')).toBeVisible({ timeout: 20000 });
}

async function switchMode(page, label) {
  await page.locator("#mode-toggle").click();
  await page.getByRole("option", { name: label }).click();
}

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    const screenshot = await page.screenshot({ fullPage: true });
    await testInfo.attach("screenshot", { body: screenshot, contentType: "image/png" });
    const html = await page.content();
    await testInfo.attach("page.html", { body: html, contentType: "text/html" });
  }
});

test("Routine -> Build Today's Plan -> Confirm Suggestion", async ({ page }, testInfo) => {
  const baseURL = process.env.OTHELLO_BASE_URL;
  test.skip(!baseURL, "OTHELLO_BASE_URL is required");

  const accessCode = process.env.OTHELLO_ACCESS_CODE || process.env.OTHELLO_PASSWORD;
  test.skip(!accessCode, "OTHELLO_ACCESS_CODE or OTHELLO_PASSWORD is required");

  const serverErrors = [];
  const consoleErrors = [];
  const authTrace = [];
  const plannerTrace = [];

  page.on("response", (response) => {
    if (response.status() >= 500) {
      serverErrors.push(`${response.status()} ${response.url()}`);
    }
  });

  page.on("response", async (response) => {
    const url = response.url();
    const matchesPlanner = (
      url.includes("/api/today-plan")
      || url.includes("/api/today-brief")
      || url.includes("/v1/plan/draft")
      || url.includes("/api/confirm")
      || url.includes("/v1/confirm")
      || url.includes("/api/plan/update")
    );
    if (!matchesPlanner) return;
    const request = response.request();
    let path = url;
    try {
      const parsed = new URL(url);
      path = `${parsed.pathname}${parsed.search}`;
    } catch {}
    let bodyText = "";
    try {
      bodyText = await response.text();
    } catch (err) {
      bodyText = `READ_ERROR: ${err.message}`;
    }
    const snippet = bodyText.replace(/\s+/g, " ").trim().slice(0, 300);
    plannerTrace.push(`${request.method()} ${path} ${response.status()} ${snippet}`);
  });

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });

  page.on("pageerror", (err) => {
    consoleErrors.push(`pageerror: ${err.message}`);
  });

  try {
    await page.goto(baseURL, { waitUntil: "domcontentloaded" });
    await login(page, accessCode, baseURL, testInfo, authTrace);

    await switchMode(page, "Routine Planner");
    await page.locator("#middle-tab").click();
    await expect(page.locator("#routine-planner-view")).toBeVisible();

    page.once("dialog", (dialog) => dialog.accept(ROUTINE_NAME));
    await page.locator("#routine-add-btn").click();
    await page.locator("#routine-title-input").fill(ROUTINE_NAME);

    await expect(page.locator("#routine-title-input")).toHaveValue(ROUTINE_NAME, { timeout: 20000 });

    const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
    for (const day of days) {
      await page.locator("#routine-days label", { hasText: new RegExp(day, "i") })
        .locator("input[type=checkbox]")
        .check();
    }

    const timeInputs = page.locator("#routine-schedule-extra input[type=time]");
    await expect(timeInputs.first()).toBeVisible();
    await timeInputs.first().fill("06:00");

    const addStepBtn = page.locator("#routine-add-step-btn");
    const stepInputs = page.locator("#routine-steps input[type=text]");
    let stepCount = await stepInputs.count();
    while (stepCount < 2) {
      await addStepBtn.click();
      await expect(stepInputs).toHaveCount(stepCount + 1, { timeout: 15000 });
      stepCount = await stepInputs.count();
    }
    const emptyIndices = [];
    for (let i = 0; i < stepCount; i++) {
      const value = await stepInputs.nth(i).inputValue();
      if (!value.trim()) {
        emptyIndices.push(i);
      }
    }
    let targetIndices = [];
    if (emptyIndices.length >= 2) {
      targetIndices = emptyIndices.slice(0, 2);
    } else {
      targetIndices = [Math.max(0, stepCount - 2), stepCount - 1];
    }
    await stepInputs.nth(targetIndices[0]).fill(STEP_TITLES[0]);
    await stepInputs.nth(targetIndices[1]).fill(STEP_TITLES[1]);

    await page.locator("#routine-save-btn").click();
    await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });

    await switchMode(page, "Today Planner");

    await page.locator("#middle-tab").click();
    await expect(page.locator("#today-planner-view")).toBeVisible();
    const plannerFailedBanner = page.getByText("Planner load failed");
    const plannerLoadResult = await Promise.race([
      page.waitForResponse(
        (response) => response.url().includes("/api/today-plan") && response.status() === 200,
        { timeout: 20000 }
      ).then(() => "ok").catch(() => null),
      plannerFailedBanner.waitFor({ state: "visible", timeout: 20000 }).then(() => "fail").catch(() => null),
    ]);
    if (plannerLoadResult !== "ok") {
      await testInfo.attach("planner-trace.txt", {
        body: plannerTrace.join("\n"),
        contentType: "text/plain",
      });
      await testInfo.attach("console-errors.txt", {
        body: consoleErrors.join("\n"),
        contentType: "text/plain",
      });
      if (plannerLoadResult === "fail") {
        throw new Error("Planner load failed banner displayed; see planner-trace.txt");
      }
      throw new Error("Planner load did not complete; see planner-trace.txt");
    }
    await expect(page.locator("#build-plan-btn")).toBeVisible();
    await page.locator("#build-plan-btn").click();

    const suggestionsList = page.locator("#today-plan-suggestions .planner-block");
    await expect(suggestionsList.first()).toBeVisible({ timeout: 20000 });
    const pendingCount = await suggestionsList.count();

    let targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: ROUTINE_NAME });
    if (await targetCard.count() === 0) {
      targetCard = page.locator("#today-plan-suggestions .planner-block", { hasText: /routine-/i });
    }
    const targetCount = await targetCard.count();
    expect(
      targetCount,
      "Expected at least one routine-related suggestion (name match or routine- fallback)."
    ).toBeGreaterThan(0);

    targetCard = targetCard.first();
    let selectedTitle = "";
    const titleLocator = targetCard.locator(".planner-block__title");
    if (await titleLocator.count()) {
      selectedTitle = (await titleLocator.first().innerText()).trim();
    }
    if (!selectedTitle) {
      selectedTitle = ((await targetCard.textContent()) || "").trim();
    }
    const confirmResponsePromise = page.waitForResponse(
      (response) => {
        const url = response.url();
        if (response.request().method() !== "POST") return false;
        return url.includes("/confirm") || url.includes("/plan/update");
      },
      { timeout: 20000 }
    );
    await targetCard.getByRole("button", { name: "Confirm" }).click();
    const confirmResponse = await confirmResponsePromise;
    let confirmText = "";
    try {
      confirmText = await confirmResponse.text();
    } catch {}
    let confirmOk = confirmResponse.status() === 200;
    if (confirmText.includes("\"ok\":")) {
      confirmOk = confirmText.includes("\"ok\":true");
    }
    if (!confirmOk) {
      await testInfo.attach("planner-trace.txt", {
        body: plannerTrace.join("\n"),
        contentType: "text/plain",
      });
      throw new Error(`Confirm failed: ${confirmResponse.status()} ${confirmText.slice(0, 300)}`);
    }

    await page.locator("#middle-tab").click();
    await expect(page.locator("#today-planner-view")).toBeVisible();

    const todayPlanItems = page.locator("#today-plan-items");
    await expect(todayPlanItems).toBeVisible();
    const planText = selectedTitle ? await todayPlanItems.textContent() : "";
    if (selectedTitle && planText && planText.includes(selectedTitle)) {
      await expect(todayPlanItems).toContainText(selectedTitle, { timeout: 20000 });
    } else {
      await expect
        .poll(async () => todayPlanItems.locator(".planner-task").count(), { timeout: 20000 })
        .toBeGreaterThan(0);
    }

    if (consoleErrors.length) {
      await testInfo.attach("console-errors.txt", {
        body: consoleErrors.join("\n"),
        contentType: "text/plain",
      });
    }

    if (serverErrors.length) {
      await testInfo.attach("server-500s.txt", {
        body: serverErrors.join("\n"),
        contentType: "text/plain",
      });
    }

    const criticalConsoleErrors = consoleErrors.filter((entry) => (
      entry.includes("Uncaught") || entry.includes("TypeError")
    ));
    expect(criticalConsoleErrors, "Critical console errors detected during flow").toEqual([]);
    expect(serverErrors, "Server returned 500 responses during flow").toEqual([]);
  } finally {
    if (plannerTrace.length) {
      await testInfo.attach("planner-trace.txt", {
        body: plannerTrace.join("\n"),
        contentType: "text/plain",
      });
    }
  }
});
