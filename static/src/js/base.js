export class MobileMenuController {
  constructor({ button, menu, documentRef = document } = {}) {
    this.button = button;
    this.menu = menu;
    this.document = documentRef;
  }

  initialize() {
    if (!this.button || !this.menu) return false;

    this.close();
    this.document.documentElement.classList.add("has-mobile-menu");
    this.button.addEventListener("click", () => this.toggle());
    this.document.addEventListener("keydown", (event) => this.handleKeydown(event));
    return true;
  }

  toggle() {
    if (this.button.getAttribute("aria-expanded") === "true") this.close();
    else this.open();
  }

  open() {
    this.button.setAttribute("aria-expanded", "true");
    this.menu.classList.add("is-open");
  }

  close({ returnFocus = false } = {}) {
    this.button.setAttribute("aria-expanded", "false");
    this.menu.classList.remove("is-open");
    if (returnFocus) this.button.focus();
  }

  handleKeydown(event) {
    if (event.key !== "Escape" || this.button.getAttribute("aria-expanded") !== "true") return;
    event.preventDefault();
    this.close({ returnFocus: true });
  }
}

export const initializeMobileMenu = (documentRef = document) => {
  const controller = new MobileMenuController({
    button: documentRef.querySelector("[data-mobile-menu-button]"),
    menu: documentRef.querySelector("[data-mobile-menu-panel]"),
    documentRef,
  });
  controller.initialize();
  return controller;
};

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => initializeMobileMenu());
}
