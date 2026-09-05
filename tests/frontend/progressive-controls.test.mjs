import assert from "node:assert/strict";
import test from "node:test";

import { MobileMenuController } from "../../static/src/js/base.js";
import { SearchFiltersController } from "../../static/src/js/search-filters.js";

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
