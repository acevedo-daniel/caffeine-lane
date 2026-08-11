export class SearchFiltersController {
  constructor({ toggle, panel, documentRef = document } = {}) {
    this.toggle = toggle;
    this.panel = panel;
    this.document = documentRef;
  }

  initialize() {
    if (!this.toggle || !this.panel) return false;

    const isOpen = this.toggle.getAttribute("aria-expanded") === "true";
    this.setOpen(isOpen);
    this.document.documentElement.classList.add("has-search-filter-enhancement");
    this.toggle.addEventListener("click", () => this.setOpen(!this.isOpen()));
    this.document.addEventListener("keydown", (event) => this.handleKeydown(event));
    return true;
  }

  isOpen() {
    return this.toggle.getAttribute("aria-expanded") === "true";
  }

  setOpen(isOpen, { returnFocus = false } = {}) {
    this.toggle.setAttribute("aria-expanded", String(isOpen));
    this.panel.classList.toggle("is-open", isOpen);
    if (returnFocus) this.toggle.focus();
  }

  handleKeydown(event) {
    if (event.key !== "Escape" || !this.isOpen()) return;
    event.preventDefault();
    this.setOpen(false, { returnFocus: true });
  }
}

export const initializeSearchFilters = (documentRef = document) => {
  const controller = new SearchFiltersController({
    toggle: documentRef.getElementById("filter-toggle-btn"),
    panel: documentRef.getElementById("filter-section"),
    documentRef,
  });
  controller.initialize();
  return controller;
};

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => initializeSearchFilters());
}
