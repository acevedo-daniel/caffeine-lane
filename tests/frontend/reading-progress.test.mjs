import assert from "node:assert/strict";
import test from "node:test";

import { ReadingProgressController } from "../../static/src/js/reading-progress.js";

const createFixture = ({ scrollY = 0, scrollHeight = 2000, innerHeight = 1000 } = {}) => {
  const listeners = new Map();
  const progressBar = {
    style: { width: "0%" },
  };

  const documentRef = {
    documentElement: {
      scrollTop: scrollY,
      scrollHeight,
    },
    querySelector(selector) {
      if (selector === "#reading-progress") return progressBar;
      return null;
    },
  };

  const windowRef = {
    document: documentRef,
    scrollY,
    innerHeight,
    addEventListener(name, callback) {
      listeners.set(name, callback);
    },
    emit(name) {
      listeners.get(name)?.();
    },
  };

  return { progressBar, windowRef, listeners };
};

test("reading progress initializes to zero at top of page and attaches scroll listeners", () => {
  const { progressBar, windowRef, listeners } = createFixture({ scrollY: 0 });
  const controller = new ReadingProgressController({ windowRef });
  controller.initialize();

  assert.equal(progressBar.style.width, "0%");
  assert.equal(listeners.has("scroll"), true);
  assert.equal(listeners.has("resize"), true);
});

test("reading progress calculates percentage correctly on scroll update", () => {
  const { progressBar, windowRef } = createFixture({ scrollY: 500, scrollHeight: 2000, innerHeight: 1000 });
  const controller = new ReadingProgressController({ windowRef });
  controller.initialize();

  // (500 / (2000 - 1000)) * 100 = 50%
  assert.equal(progressBar.style.width, "50%");

  // Scroll to bottom
  windowRef.scrollY = 1000;
  windowRef.emit("scroll");
  assert.equal(progressBar.style.width, "100%");
});

test("reading progress clamps to 0% if content is smaller than viewport", () => {
  const { progressBar, windowRef } = createFixture({ scrollY: 0, scrollHeight: 500, innerHeight: 1000 });
  const controller = new ReadingProgressController({ windowRef });
  controller.initialize();

  assert.equal(progressBar.style.width, "0%");
});
