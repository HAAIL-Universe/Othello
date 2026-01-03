const { test, expect } = require("@playwright/test");

const ROUTINE_NAME = "E2E Morning Routine " + Date.now();
const STEP_TITLES = ["Breakfast", "Shower"];

async function login(page, accessCode) {
  const loginInput = page.locator("#login-pin");
  const loginOverlay = page.locator("#login-overlay");
  const needsLogin = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
  if (needsLogin) {
    await loginInput.fill(accessCode);
    await page.locator("#login-btn").click();
  }
  await expect(page.getByRole("button", { name: "Chat" })).toBeVisible({ timeout: 20000 });
  await expect(loginOverlay).toBeHidden({ timeout: 20000 });
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

  page.on("response", (response) => {
    if (response.status() >= 500) {
      serverErrors.push(`${response.status()} ${response.url()}`);
    }
  });

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });

  page.on("pageerror", (err) => {
    consoleErrors.push(`pageerror: ${err.message}`);
  });

  await page.goto(baseURL, { waitUntil: "domcontentloaded" });
  await login(page, accessCode);

  await switchMode(page, "Routine Planner");
  await expect(page.getByRole("heading", { name: "Routine Planner" })).toBeVisible();

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
  await addStepBtn.click();
  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(1, { timeout: 15000 });
  await addStepBtn.click();
  await expect(page.locator("#routine-steps input[type=text]")).toHaveCount(2, { timeout: 15000 });

  const stepInputs = page.locator("#routine-steps input[type=text]");
  await stepInputs.nth(0).fill(STEP_TITLES[0]);
  await stepInputs.nth(1).fill(STEP_TITLES[1]);

  await page.locator("#routine-save-btn").click();
  await expect(page.locator("#routine-list")).toContainText(ROUTINE_NAME, { timeout: 20000 });

  await switchMode(page, "Today Planner");

  await page.locator("#middle-tab").click();
  await expect(page.locator("#today-planner-view")).toBeVisible();
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
  await targetCard.getByRole("button", { name: "Confirm" }).click();

  await expect
    .poll(
      async () => {
        const currentCount = await suggestionsList.count();
        if (currentCount < pendingCount) return true;
        if (selectedTitle) {
          const panelText = await page.locator("#today-plan-suggestions").textContent();
          return panelText ? !panelText.includes(selectedTitle) : false;
        }
        return false;
      },
      { timeout: 20000 }
    )
    .toBe(true);

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
});
