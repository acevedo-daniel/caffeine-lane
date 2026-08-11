import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";

const databaseUrl = process.env.E2E_DATABASE_URL || process.env.DATABASE_URL;
const localWindowsPython = ".\\.venv\\Scripts\\python.exe";
const djangoCommand = process.env.E2E_PYTHON
  ? `"${process.env.E2E_PYTHON}" manage.py runserver 127.0.0.1:8000 --noreload`
  : process.platform === "win32" && existsSync(localWindowsPython)
    ? `"${localWindowsPython}" manage.py runserver 127.0.0.1:8000 --noreload`
    : "uv run python manage.py runserver 127.0.0.1:8000 --noreload";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 30_000,
  expect: { timeout: 8_000 },
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://127.0.0.1:8000",
    browserName: "chromium",
    trace: "retain-on-failure",
  },
  webServer: {
    command: djangoCommand,
    url: "http://127.0.0.1:8000/healthz/",
    timeout: 30_000,
    reuseExistingServer: !process.env.CI,
    env: {
      ...process.env,
      DJANGO_SETTINGS_MODULE: "config.settings.local",
      ...(databaseUrl ? { DATABASE_URL: databaseUrl } : {}),
      DEBUG_TOOLBAR_ENABLED: "false",
    },
  },
});
