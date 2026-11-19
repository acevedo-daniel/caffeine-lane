const initializedInputs = new WeakSet();

/** Synchronize a localized filename label with the selected files of a hidden file input. */
export const syncFileFieldName = (input, nameElement) => {
  if (!input || !nameElement) return "";

  const emptyLabel =
    nameElement.dataset?.emptyLabel ||
    nameElement.getAttribute?.("data-empty-label") ||
    nameElement.textContent ||
    "";
  const files = Array.from(input.files || []);
  const selectedNames =
    input.value === ""
      ? []
      : files.map((file) => file?.name).filter(Boolean);
  const nextLabel = selectedNames.length > 0 ? selectedNames.join(", ") : emptyLabel;
  nameElement.textContent = nextLabel;
  return nextLabel;
};

/** Bind localized filename updates for every [data-file-field] wrapper in documentRef. */
export const initializeFileFields = (
  documentRef = typeof document !== "undefined" ? document : null,
) => {
  if (!documentRef?.querySelectorAll) return [];

  const fields = documentRef.querySelectorAll("[data-file-field]") || [];
  const initialized = [];

  fields.forEach((field) => {
    const input = field.querySelector?.('input[type="file"]');
    const nameElement = field.querySelector?.("[data-file-field-name]");
    if (!input || !nameElement) return;

    if (!initializedInputs.has(input)) {
      initializedInputs.add(input);
      input.addEventListener("change", () => syncFileFieldName(input, nameElement));
    }

    syncFileFieldName(input, nameElement);
    initialized.push({ field, input, nameElement });
  });

  return initialized;
};

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initializeFileFields());
  } else {
    initializeFileFields();
  }
}
