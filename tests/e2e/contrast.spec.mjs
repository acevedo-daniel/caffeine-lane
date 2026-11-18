import { expect, test } from "@playwright/test";

const ROUTES = [
  "/",
  "/home/",
  "/posts/category/builds/",
  "/posts/cafe-racer-de-garaje/",
  "/posts/search/?q=moto",
  "/posts/search/?q=zzqxv",
  "/about/",
  "/contact/",
  "/accounts/login/",
  "/accounts/register/",
  "/accounts/password-reset/",
  "/404/",
];

const THEMES = ["light", "dark"];

test.describe("WCAG AA text contrast", () => {
  for (const theme of THEMES) {
    for (const route of ROUTES) {
      test(`${route} (${theme})`, async ({ page }) => {
        await page.setViewportSize({ width: 1440, height: 900 });
        await page.addInitScript((selectedTheme) => {
          localStorage.setItem("caffeine_lane_theme", selectedTheme);
        }, theme);

        await page.goto(route);
        await page.evaluate(() => document.fonts.ready);

        const failures = await page.evaluate(() => {
          const canvas = document.createElement("canvas");
          canvas.width = 1;
          canvas.height = 1;
          const ctx = canvas.getContext("2d", { willReadFrequently: true });

          function parseColor(colorStr) {
            if (!colorStr || colorStr === "transparent" || colorStr === "none") {
              return [0, 0, 0, 0];
            }
            ctx.clearRect(0, 0, 1, 1);
            ctx.fillStyle = "#000000";
            ctx.fillStyle = colorStr;
            ctx.fillRect(0, 0, 1, 1);
            const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
            return [r, g, b, a / 255];
          }

          function srgbToLinear(channel) {
            const s = channel / 255;
            return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
          }

          function relativeLuminance([r, g, b]) {
            return (
              0.2126 * srgbToLinear(r) +
              0.7152 * srgbToLinear(g) +
              0.0722 * srgbToLinear(b)
            );
          }

          function contrastRatio(rgb1, rgb2) {
            const l1 = relativeLuminance(rgb1);
            const l2 = relativeLuminance(rgb2);
            const lighter = Math.max(l1, l2);
            const darker = Math.min(l1, l2);
            return (lighter + 0.05) / (darker + 0.05);
          }

          function describeElement(el) {
            const tag = el.tagName.toLowerCase();
            if (el.id) {
              return `${tag}#${el.id}`;
            }
            if (el.classList.length > 0) {
              return `${tag}.${Array.from(el.classList).slice(0, 3).join(".")}`;
            }
            const parent = el.parentElement;
            if (parent) {
              const pTag = parent.tagName.toLowerCase();
              const pDesc = parent.id
                ? `${pTag}#${parent.id}`
                : parent.classList.length > 0
                  ? `${pTag}.${Array.from(parent.classList).slice(0, 2).join(".")}`
                  : pTag;
              return `${pDesc} > ${tag}`;
            }
            return tag;
          }

          function shouldSkipElement(el, textNode) {
            const ignoredTags = new Set([
              "SCRIPT",
              "STYLE",
              "NOSCRIPT",
              "TEMPLATE",
              "TITLE",
              "TEXTAREA",
              "OPTION",
              "OPTGROUP",
            ]);
            if (ignoredTags.has(el.tagName) || el.closest("select")) {
              return true;
            }

            let cur = el;
            while (cur && cur.nodeType === 1) {
              if (cur.matches('[aria-hidden="true"], .sr-only, [inert]')) {
                return true;
              }
              const cs = getComputedStyle(cur);
              if (
                cs.display === "none" ||
                cs.visibility === "hidden" ||
                parseFloat(cs.opacity) === 0
              ) {
                return true;
              }
              cur = cur.parentElement;
            }

            const range = document.createRange();
            range.selectNodeContents(textNode);
            const textRect = range.getBoundingClientRect();
            if (textRect.width === 0 || textRect.height === 0) {
              return true;
            }

            const elRect = el.getBoundingClientRect();
            const elStyle = getComputedStyle(el);
            if (
              elStyle.display !== "contents" &&
              (elRect.width === 0 || elRect.height === 0)
            ) {
              return true;
            }
            if (
              (elRect.width <= 1 && elRect.height <= 1 && elStyle.overflow === "hidden") ||
              elStyle.clip === "rect(0px, 0px, 0px, 0px)" ||
              elStyle.clipPath === "inset(50%)"
            ) {
              return true;
            }
            return false;
          }

          function resolveColors(el) {
            const bgLayers = [];
            let fgOpacity = 1;
            let cur = el;

            while (cur && cur.nodeType === 1) {
              const cs = getComputedStyle(cur);
              if (/url\(/i.test(cs.backgroundImage)) {
                return null;
              }
              const bgColor = parseColor(cs.backgroundColor);
              if (bgColor[3] > 0) {
                bgLayers.push(bgColor);
                if (bgColor[3] >= 0.999) {
                  break;
                }
              }
              fgOpacity *= parseFloat(cs.opacity);
              cur = cur.parentElement;
            }

            let bg = [255, 255, 255];
            for (let i = bgLayers.length - 1; i >= 0; i--) {
              const [r, g, b, a] = bgLayers[i];
              bg = [
                r * a + bg[0] * (1 - a),
                g * a + bg[1] * (1 - a),
                b * a + bg[2] * (1 - a),
              ];
            }

            const elStyle = getComputedStyle(el);
            const [fr, fg, fb, fa] = parseColor(elStyle.color);
            const effectiveAlpha = fa * fgOpacity;
            const fgRgb = [
              fr * effectiveAlpha + bg[0] * (1 - effectiveAlpha),
              fg * effectiveAlpha + bg[1] * (1 - effectiveAlpha),
              fb * effectiveAlpha + bg[2] * (1 - effectiveAlpha),
            ];

            return { fgRgb, bgRgb: bg, elStyle };
          }

          const seen = new Set();
          const issues = [];
          const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
          );

          let node;
          while ((node = walker.nextNode())) {
            const rawText = node.nodeValue ? node.nodeValue.trim() : "";
            if (!rawText) {
              continue;
            }
            const el = node.parentElement;
            if (!el || seen.has(el)) {
              continue;
            }
            if (shouldSkipElement(el, node)) {
              continue;
            }

            const resolved = resolveColors(el);
            if (!resolved) {
              continue;
            }
            seen.add(el);

            const { fgRgb, bgRgb, elStyle } = resolved;
            const fontSize = parseFloat(elStyle.fontSize);
            const fontWeight = parseFloat(elStyle.fontWeight);
            const isLarge =
              fontSize >= 24 || (fontWeight >= 700 && fontSize >= 18.66);
            const required = isLarge ? 3 : 4.5;
            const ratio = contrastRatio(fgRgb, bgRgb);

            if (ratio < required) {
              const snippet = rawText.replace(/\s+/g, " ").slice(0, 60);
              issues.push(
                `${describeElement(el)} · ${ratio.toFixed(2)} (req ${required}) · ${snippet}`,
              );
            }
          }

          return issues;
        });

        expect(
          failures,
          `${route} (${theme}) contrast failures:\n${failures.join("\n")}`,
        ).toEqual([]);
      });
    }
  }
});
