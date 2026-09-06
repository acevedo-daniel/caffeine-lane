import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";

const databaseUrl = process.env.E2E_DATABASE_URL || process.env.DATABASE_URL;
const localWindowsPython = ".\\.venv\\Scripts\\python.exe";
const djangoCommand = process.env.E2E_PYTHON
  ? `"${process.env.E2E_PYTHON}" manage.py runserver 127.0.0.1:8010 --noreload`
  : process.platform === "win32" && existsSync(localWindowsPython)
    ? `"${localWindowsPython}" manage.py runserver 127.0.0.1:8010 --noreload`
    : "uv run python manage.py runserver 127.0.0.1:8010 --noreload";

export default defineConfig({
  testDir: "./scripts",
  testMatch: "capture-doc-screenshots.spec.mjs",
  timeout: 30_000,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:8010",
    browserName: "chromium",
  },
  webServer: {
    command: djangoCommand,
    url: "http://127.0.0.1:8010/healthz/",
    timeout: 30_000,
    reuseExistingServer: false,
    env: {
      ...process.env,
      DJANGO_SETTINGS_MODULE: "config.settings.local",
      ...(databaseUrl ? { DATABASE_URL: databaseUrl } : {}),
      DEBUG_TOOLBAR_ENABLED: "false",
    },
  },
});
