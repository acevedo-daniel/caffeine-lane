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
