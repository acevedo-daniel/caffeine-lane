import assert from "node:assert/strict";
import test from "node:test";

import { initializeFileFields } from "../../static/src/js/file-field.js";

const createFileFieldDocument = ({ emptyLabel = "Ninguna foto seleccionada", initialFiles = [] } = {}) => {
  const listeners = new Map();
  const input = {
    files: initialFiles,
    value: initialFiles.length > 0 ? `C:\\fakepath\\${initialFiles[0].name}` : "",
    addEventListener(name, callback) {
      listeners.set(name, callback);
    },
    emit(name) {
      listeners.get(name)?.();
    },
  };
  const nameElement = {
    dataset: { emptyLabel },
    textContent: emptyLabel,
  };
  const field = {
    querySelector(selector) {
      if (selector === 'input[type="file"]') return input;
      if (selector === "[data-file-field-name]") return nameElement;
      return null;
    },
  };
  const documentRef = {
    querySelectorAll(selector) {
      if (selector === "[data-file-field]") return [field];
      return [];
    },
  };

  return { documentRef, input, nameElement };
};

test("initializeFileFields keeps the empty label and updates on file selection and reset", () => {
  const { documentRef, input, nameElement } = createFileFieldDocument();

  const initialized = initializeFileFields(documentRef);
  assert.equal(initialized.length, 1);
  assert.equal(nameElement.textContent, "Ninguna foto seleccionada");

  input.files = [{ name: "norton-es2.webp" }];
  input.value = "C:\\fakepath\\norton-es2.webp";
  input.emit("change");
  assert.equal(nameElement.textContent, "norton-es2.webp");

  input.files = [{ name: "one.jpg" }, { name: "two.png" }];
  input.emit("change");
  assert.equal(nameElement.textContent, "one.jpg, two.png");

  input.files = [];
  input.value = "";
  input.emit("change");
  assert.equal(nameElement.textContent, "Ninguna foto seleccionada");
});
