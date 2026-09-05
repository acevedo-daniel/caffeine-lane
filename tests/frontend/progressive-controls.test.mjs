import assert from "node:assert/strict";
import test from "node:test";

import { MobileMenuController } from "../../static/src/js/base.js";
import { SearchFiltersController } from "../../static/src/js/search-filters.js";
import { AvatarPreviewController } from "../../static/src/js/avatar-preview.js";

const createElement = ({ attributes = {} } = {}) => {
  const listeners = new Map();
  const classNames = new Set();
  return {
    attributes: new Map(Object.entries(attributes)),
    classList: {
      add: (name) => classNames.add(name),
      remove: (name) => classNames.delete(name),
      toggle: (name, force) => {
        if (force) classNames.add(name);
        else classNames.delete(name);
      },
      contains: (name) => classNames.has(name),
    },
    focusCount: 0,
    getAttribute(name) { return this.attributes.get(name) ?? null; },
    setAttribute(name, value) { this.attributes.set(name, value); },
    addEventListener(name, callback) { listeners.set(name, callback); },
    emit(name, event = {}) { listeners.get(name)?.(event); },
    focus() { this.focusCount += 1; },
  };
};

const createDocument = () => {
  const classNames = new Set();
  const listeners = new Map();
  return {
    documentElement: { classList: { add: (name) => classNames.add(name) } },
    classNames,
    addEventListener(name, callback) { listeners.set(name, callback); },
    emit(name, event) { listeners.get(name)?.(event); },
  };
};

test("the mobile menu becomes collapsible only after JavaScript initializes", () => {
  const documentRef = createDocument();
  const button = createElement({ attributes: { "aria-expanded": "false" } });
  const menu = createElement();
  const controller = new MobileMenuController({ button, menu, documentRef });

  assert.equal(controller.initialize(), true);
  assert.equal(documentRef.classNames.has("has-mobile-menu"), true);
  assert.equal(menu.classList.contains("is-open"), false);

  button.emit("click");
  assert.equal(button.getAttribute("aria-expanded"), "true");
  assert.equal(menu.classList.contains("is-open"), true);

  const escapeEvent = { key: "Escape", preventDefault() {} };
  documentRef.emit("keydown", escapeEvent);
  assert.equal(button.getAttribute("aria-expanded"), "false");
  assert.equal(menu.classList.contains("is-open"), false);
  assert.equal(button.focusCount, 1);
});

test("search filters preserve the server-selected open state and close with Escape", () => {
  const documentRef = createDocument();
  const toggle = createElement({ attributes: { "aria-expanded": "true" } });
  const panel = createElement();
  const controller = new SearchFiltersController({ toggle, panel, documentRef });

  assert.equal(controller.initialize(), true);
  assert.equal(documentRef.classNames.has("has-search-filter-enhancement"), true);
  assert.equal(panel.classList.contains("is-open"), true);

  const escapeEvent = { key: "Escape", preventDefault() {} };
  documentRef.emit("keydown", escapeEvent);
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(panel.classList.contains("is-open"), false);
  assert.equal(toggle.focusCount, 1);
});

test("search instant clear button clears input and updates visibility", () => {
  const documentRef = createDocument();
  const input = {
    value: "CB750",
    focusCount: 0,
    listeners: new Map(),
    addEventListener(name, cb) { this.listeners.set(name, cb); },
    emit(name) { this.listeners.get(name)?.(); },
    focus() { this.focusCount += 1; },
  };
  const clearBtn = {
    hidden: false,
    style: { display: "" },
    listeners: new Map(),
    setAttribute(name) { if (name === "hidden") this.hidden = true; },
    removeAttribute(name) { if (name === "hidden") this.hidden = false; },
    addEventListener(name, cb) { this.listeners.set(name, cb); },
    emit(name) { this.listeners.get(name)?.(); },
  };

  const controller = new SearchFiltersController({ clearBtn, input, documentRef });
  controller.initialize();

  assert.equal(clearBtn.hidden, false);

  // Click clear button
  clearBtn.emit("click");
  assert.equal(input.value, "");
  assert.equal(clearBtn.hidden, true);
  assert.equal(input.focusCount, 1);

  // Type again
  input.value = "BMW";
  input.emit("input");
  assert.equal(clearBtn.hidden, false);
});

test("avatar preview updates preview src on valid image selection", () => {
  const listeners = new Map();
  const input = {
    files: [{ name: "avatar.webp", type: "image/webp", size: 1024 * 50 }],
    addEventListener(name, cb) { listeners.set(name, cb); },
    emit(name, event) { listeners.get(name)?.(event); },
  };
  const classNames = new Set();
  const previewImg = {
    src: "/static/images/default-avatar.svg",
    classList: {
      add: (cls) => classNames.add(cls),
      remove: (cls) => classNames.delete(cls),
      contains: (cls) => classNames.has(cls),
    },
    setAttribute(name, val) { if (name === "src") this.src = val; },
    getAttribute(name) { if (name === "src") return this.src; return null; },
  };
  const errorContainer = {
    textContent: "",
    hidden: true,
    style: { display: "none" },
    setAttribute(name) { if (name === "hidden") this.hidden = true; },
    removeAttribute(name) { if (name === "hidden") this.hidden = false; },
  };

  // Mock URL.createObjectURL
  globalThis.URL = globalThis.URL || {};
  globalThis.URL.createObjectURL = (file) => `blob:http://localhost/${file.name}`;

  const controller = new AvatarPreviewController({ input, previewImg, errorContainer });
  controller.initialize();

  input.emit("change", { target: input });

  assert.equal(previewImg.src, "blob:http://localhost/avatar.webp");
  assert.equal(previewImg.classList.contains("has-custom-preview"), true);
  assert.equal(errorContainer.textContent, "");
});

test("avatar preview rejects files exceeding 5MB and unsupported formats", () => {
  const listeners = new Map();
  const input = {
    files: [{ name: "huge.png", type: "image/png", size: 6 * 1024 * 1024 }],
    addEventListener(name, cb) { listeners.set(name, cb); },
    emit(name, event) { listeners.get(name)?.(event); },
  };
  const previewImg = {
    src: "/static/images/default-avatar.svg",
    classList: { add() {}, remove() {}, contains: () => false },
    setAttribute(name, val) { if (name === "src") this.src = val; },
    getAttribute(name) { if (name === "src") return this.src; return null; },
  };
  const errorContainer = {
    textContent: "",
    hidden: true,
    style: { display: "none" },
    setAttribute(name) { if (name === "hidden") this.hidden = true; },
    removeAttribute(name) { if (name === "hidden") this.hidden = false; },
  };

  const controller = new AvatarPreviewController({ input, previewImg, errorContainer });
  controller.initialize();

  // Test oversize
  input.emit("change", { target: input });
  assert.equal(errorContainer.textContent, "Images must be 5 MB or smaller.");

  // Test unsupported format
  input.files = [{ name: "doc.pdf", type: "application/pdf", size: 1024 }];
  input.emit("change", { target: input });
  assert.equal(errorContainer.textContent, "Images must use JPEG, PNG, or WebP format.");
});
