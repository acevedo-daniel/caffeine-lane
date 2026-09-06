import assert from "node:assert/strict";
import test from "node:test";

import {
  ThemeController,
  THEME_STORAGE_KEY,
  THEME_DARK,
  THEME_LIGHT,
} from "../../static/src/js/theme-toggle.js";

const createMockStorage = (initial = {}) => {
  const store = new Map(Object.entries(initial));
  return {
    getItem(key) {
      return store.get(key) ?? null;
    },
    setItem(key, value) {
      store.set(key, String(value));
    },
    removeItem(key) {
      store.delete(key);
    },
    clear() {
      store.clear();
    },
  };
};

const createMockElement = ({ tagName = "DIV", attributes = {} } = {}) => {
  const listeners = new Map();
  const classList = new Set();
  return {
    tagName,
    attributes: new Map(Object.entries(attributes)),
    classList: {
      add: (name) => classList.add(name),
      remove: (name) => classList.delete(name),
      contains: (name) => classList.has(name),
    },
    getAttribute(name) {
      return this.attributes.get(name) ?? null;
    },
    setAttribute(name, value) {
      this.attributes.set(name, String(value));
    },
    addEventListener(name, callback) {
      listeners.set(name, callback);
    },
    emit(name, event = {}) {
      listeners.get(name)?.(event);
    },
    querySelector() {
      return null;
    },
  };
};

const createMockDocument = ({ toggles = [] } = {}) => {
  const docClassList = new Set();
  const docAttributes = new Map();
  const listeners = new Map();

  return {
    documentElement: {
      attributes: docAttributes,
      classList: {
        add: (name) => docClassList.add(name),
        remove: (name) => docClassList.delete(name),
        contains: (name) => docClassList.has(name),
      },
      getAttribute(name) {
        return docAttributes.get(name) ?? null;
      },
      setAttribute(name, value) {
        docAttributes.set(name, String(value));
      },
    },
    querySelectorAll(selector) {
      if (selector === "[data-theme-toggle]") {
        return toggles;
      }
      return [];
    },
    addEventListener(name, callback) {
      listeners.set(name, callback);
    },
    dispatchEvent() {
      return true;
    },
    emit(name, event) {
      listeners.get(name)?.(event);
    },
  };
};

const createMockWindow = ({ prefersDark = false } = {}) => {
  const listeners = new Map();
  let mediaListener = null;

  return {
    matchMedia(query) {
      return {
        matches: prefersDark,
        media: query,
        addEventListener(name, cb) {
          if (name === "change") mediaListener = cb;
        },
        removeEventListener() {},
        emitChange(matches) {
          mediaListener?.({ matches });
        },
      };
    },
    addEventListener(name, callback) {
      listeners.set(name, callback);
    },
    removeEventListener(name) {
      listeners.delete(name);
    },
    emit(name, event) {
      listeners.get(name)?.(event);
    },
  };
};

test("ThemeController uses stored theme when available", () => {
  const storage = createMockStorage({ [THEME_STORAGE_KEY]: THEME_DARK });
  const doc = createMockDocument();
  const win = createMockWindow({ prefersDark: false });

  const controller = new ThemeController({ storage, documentRef: doc, windowRef: win });
  controller.initialize();

  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_DARK);
  assert.equal(doc.documentElement.classList.contains("dark"), true);
  assert.equal(controller.getCurrentTheme(), THEME_DARK);
  assert.equal(controller.isDark(), true);
});

test("ThemeController falls back to system preference when no storage is set", () => {
  const storage = createMockStorage();
  const doc = createMockDocument();
  const win = createMockWindow({ prefersDark: true });

  const controller = new ThemeController({ storage, documentRef: doc, windowRef: win });
  controller.initialize();

  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_DARK);
  assert.equal(doc.documentElement.classList.contains("dark"), true);
  assert.equal(controller.getCurrentTheme(), THEME_DARK);
});

test("ThemeController toggle switches between dark and light and persists to storage", () => {
  const storage = createMockStorage();
  const desktopToggle = createMockElement({ tagName: "BUTTON", attributes: { "data-theme-toggle": "" } });
  const mobileToggle = createMockElement({ tagName: "BUTTON", attributes: { "data-theme-toggle": "" } });
  const doc = createMockDocument({ toggles: [desktopToggle, mobileToggle] });
  const win = createMockWindow({ prefersDark: false });

  const controller = new ThemeController({ storage, documentRef: doc, windowRef: win });
  controller.initialize();

  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_LIGHT);
  assert.equal(desktopToggle.getAttribute("aria-pressed"), "false");
  assert.equal(mobileToggle.getAttribute("aria-pressed"), "false");

  // Click desktop toggle -> switches to dark
  desktopToggle.emit("click");
  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_DARK);
  assert.equal(doc.documentElement.classList.contains("dark"), true);
  assert.equal(storage.getItem(THEME_STORAGE_KEY), THEME_DARK);
  assert.equal(desktopToggle.getAttribute("aria-pressed"), "true");
  assert.equal(mobileToggle.getAttribute("aria-pressed"), "true");

  // Click mobile toggle -> switches to light
  mobileToggle.emit("click");
  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_LIGHT);
  assert.equal(doc.documentElement.classList.contains("dark"), false);
  assert.equal(storage.getItem(THEME_STORAGE_KEY), THEME_LIGHT);
  assert.equal(desktopToggle.getAttribute("aria-pressed"), "false");
  assert.equal(mobileToggle.getAttribute("aria-pressed"), "false");
});

test("ThemeController syncs across tabs via storage event", () => {
  const storage = createMockStorage();
  const desktopToggle = createMockElement({ tagName: "BUTTON", attributes: { "data-theme-toggle": "" } });
  const doc = createMockDocument({ toggles: [desktopToggle] });
  const win = createMockWindow({ prefersDark: false });

  const controller = new ThemeController({ storage, documentRef: doc, windowRef: win });
  controller.initialize();

  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_LIGHT);

  // Storage event fired from another tab
  win.emit("storage", { key: THEME_STORAGE_KEY, newValue: THEME_DARK });
  assert.equal(doc.documentElement.getAttribute("data-theme"), THEME_DARK);
  assert.equal(doc.documentElement.classList.contains("dark"), true);
  assert.equal(desktopToggle.getAttribute("aria-pressed"), "true");
});
