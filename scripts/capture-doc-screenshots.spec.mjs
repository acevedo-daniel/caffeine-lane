import { test } from "@playwright/test";

test("capture the README documentation screenshots", async () => {
  process.env.SCREENSHOT_BASE_URL = "http://127.0.0.1:8010";
  await import("./capture-doc-screenshots.mjs");
});
