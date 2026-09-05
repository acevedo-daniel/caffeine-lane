export class SearchFiltersController {
  constructor({ toggle, panel, clearBtn, input, documentRef = typeof document !== "undefined" ? document : null } = {}) {
    this.toggle = toggle;
    this.panel = panel;
    this.clearBtn = clearBtn ?? documentRef?.getElementById?.("search-clear-btn");
    this.input = input ?? documentRef?.getElementById?.("id_q");
    this.document = documentRef;
  }

  initialize() {
    this.initFilterDrawer();
    this.initClearButton();
    return true;
  }

  initFilterDrawer() {
    if (!this.toggle || !this.panel) return;

    const isOpen = this.toggle.getAttribute("aria-expanded") === "true";
    this.setOpen(isOpen);
    this.document?.documentElement?.classList?.add("has-search-filter-enhancement");
    this.toggle.addEventListener("click", () => this.setOpen(!this.isOpen()));
    this.document?.addEventListener("keydown", (event) => this.handleKeydown(event));
  }

  initClearButton() {
    if (!this.clearBtn || !this.input) return;

    const updateVisibility = () => {
      const hasValue = Boolean(this.input.value && this.input.value.trim().length > 0);
      if (hasValue) {
        this.clearBtn.removeAttribute("hidden");
        this.clearBtn.style.display = "";
      } else {
        this.clearBtn.setAttribute("hidden", "");
        this.clearBtn.style.display = "none";
      }
    };

    this.input.addEventListener("input", updateVisibility);

    this.clearBtn.addEventListener("click", () => {
      this.input.value = "";
      updateVisibility();
      this.input.focus();
    });

    updateVisibility();
  }

  isOpen() {
    return this.toggle?.getAttribute("aria-expanded") === "true";
  }

  setOpen(isOpen, { returnFocus = false } = {}) {
    if (!this.toggle || !this.panel) return;
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

export const initializeSearchFilters = (documentRef = typeof document !== "undefined" ? document : null) => {
  if (!documentRef) return null;
  const controller = new SearchFiltersController({
    toggle: documentRef.getElementById("filter-toggle-btn"),
    panel: documentRef.getElementById("filter-section"),
    clearBtn: documentRef.getElementById("search-clear-btn"),
    input: documentRef.getElementById("id_q"),
    documentRef,
  });
  controller.initialize();
  return controller;
};

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initializeSearchFilters());
  } else {
    initializeSearchFilters();
  }
}
