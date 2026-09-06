import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";

import { chromium } from "@playwright/test";

const baseUrl = (process.env.SCREENSHOT_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);
const outputDirectory = resolve("docs/screenshots");
const viewport = { width: 1440, height: 960 };

async function waitForPage(page) {
  await page.waitForLoadState("networkidle");
  await page.evaluate(async () => {
    await document.fonts.ready;
  });
}

async function visit(page, path, { theme = "dark", focus, offsetY = 0, scrollY } = {}) {
  await page.goto(`${baseUrl}${path}`, { waitUntil: "networkidle" });
  await page.evaluate((selectedTheme) => {
    localStorage.setItem("caffeine_lane_theme", selectedTheme);
    document.documentElement.dataset.theme = selectedTheme;
  }, theme);
  await page.reload({ waitUntil: "networkidle" });
  await waitForPage(page);

  if (focus) {
    await page.locator(focus).scrollIntoViewIfNeeded();
    if (offsetY) {
      await page.evaluate((offset) => window.scrollBy({ top: offset }), offsetY);
    }
    await page.waitForTimeout(150);
  } else if (scrollY) {
    await page.evaluate((position) => window.scrollTo({ top: position }), scrollY);
    await page.waitForTimeout(150);
  }
}

async function capture(page, filename) {
  await page.screenshot({
    path: resolve(outputDirectory, filename),
    animations: "disabled",
  });
}

await mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport,
  colorScheme: "light",
  deviceScaleFactor: 1,
  locale: "es-AR",
  reducedMotion: "reduce",
});
const page = await context.newPage();

try {
  await visit(page, "/");
  await capture(page, "public-landing.png");

  await visit(page, "/posts/cafe-racer-de-garaje/", {
    focus: ".build-specs-inspector",
    offsetY: 135,
  });
  await capture(page, "post-detail.png");

  await visit(page, "/posts/search/?q=moto", { scrollY: 270 });
  await capture(page, "search-results.png");

  await visit(page, "/posts/cafe-racer-de-garaje/", {
    focus: ".post-detail__section--comments",
  });
  await capture(page, "discussion-thread.png");
} finally {
  await browser.close();
}

console.log(`Captured documentation screenshots from ${baseUrl}.`);
