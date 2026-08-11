import assert from "node:assert/strict";
import test from "node:test";

import { CommentReplyController } from "../../static/src/js/comment-replies.js";

const createElement = ({ attributes = {}, query = {} } = {}) => {
  const listeners = new Map();
  return {
    attributes: new Map(Object.entries(attributes)),
    focusCount: 0,
    hidden: false,
    querySelector(selector) { return query[selector] ?? null; },
    getAttribute(name) { return this.attributes.get(name) ?? null; },
    setAttribute(name, value) { this.attributes.set(name, value); },
    addEventListener(name, callback) { listeners.set(name, callback); },
    emit(name, event = {}) { listeners.get(name)?.(event); },
    focus() { this.focusCount += 1; },
  };
};

const createFixture = (count = 2) => {
  const classNames = new Set();
  const entries = Array.from({ length: count }, (_, index) => {
    const textarea = createElement();
    const cancelButton = createElement();
    const form = createElement({ query: { textarea, "[data-reply-cancel]": cancelButton } });
    const button = createElement({ attributes: { "aria-controls": `reply-${index}`, "aria-expanded": "false" } });
    return { button, form, textarea, cancelButton };
  });
  const documentListeners = new Map();
  const documentRef = {
    documentElement: { classList: { add: (name) => classNames.add(name) } },
    querySelectorAll: () => entries.map(({ button }) => button),
    getElementById: (id) => entries.find((_, index) => id === `reply-${index}`)?.form ?? null,
    addEventListener: (name, callback) => documentListeners.set(name, callback),
    emit: (name, event) => documentListeners.get(name)?.(event),
  };
  return { classNames, documentRef, entries };
};

test("reply enhancement closes forms initially and opens one composer at a time", () => {
  const { classNames, documentRef, entries } = createFixture();
  const controller = new CommentReplyController({ documentRef });
  controller.initialize();

  assert.equal(classNames.has("has-reply-enhancement"), true);
  assert.equal(entries[0].form.hidden, true);
  assert.equal(entries[1].form.hidden, true);

  entries[0].button.emit("click");
  assert.equal(entries[0].form.hidden, false);
  assert.equal(entries[0].textarea.focusCount, 1);
  assert.equal(entries[0].button.getAttribute("aria-expanded"), "true");

  entries[1].button.emit("click");
  assert.equal(entries[0].form.hidden, true);
  assert.equal(entries[1].form.hidden, false);
  assert.equal(entries[1].textarea.focusCount, 1);
});

test("cancel and Escape close the active reply and restore focus to its trigger", () => {
  const { documentRef, entries } = createFixture();
  const controller = new CommentReplyController({ documentRef });
  controller.initialize();

  entries[0].button.emit("click");
  entries[0].cancelButton.emit("click");
  assert.equal(entries[0].form.hidden, true);
  assert.equal(entries[0].button.focusCount, 1);

  entries[1].button.emit("click");
  const escapeEvent = { key: "Escape", prevented: false, preventDefault() { this.prevented = true; } };
  documentRef.emit("keydown", escapeEvent);
  assert.equal(entries[1].form.hidden, true);
  assert.equal(entries[1].button.focusCount, 1);
  assert.equal(escapeEvent.prevented, true);
});
