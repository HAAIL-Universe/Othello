const { defineConfig } = require("@playwright/test");

const baseURL = process.env.OTHELLO_BASE_URL;

module.exports = defineConfig({
  testDir: "tests/e2e",
  testMatch: "**/*.spec.js",
  retries: 1,
  timeout: 90_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL,
    headless: true,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  reporter: [["list"]],
});
