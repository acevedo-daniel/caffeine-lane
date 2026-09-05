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

    if (this.document.querySelectorAll) {
      this.document.querySelectorAll("[data-mobile-menu-close]").forEach((closeTrigger) => {
        closeTrigger.addEventListener("click", () => this.close({ returnFocus: true }));
      });
    }

    return true;
  }

  toggle() {
    if (this.button.getAttribute("aria-expanded") === "true") this.close();
    else this.open();
  }

  open() {
    this.button.setAttribute("aria-expanded", "true");
    this.menu.classList.add("is-open");

    if (this.menu.querySelectorAll) {
      const focusable = this.menu.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        setTimeout(() => focusable[0]?.focus?.(), 50);
      }
    }
  }

  close({ returnFocus = false } = {}) {
    this.button.setAttribute("aria-expanded", "false");
    this.menu.classList.remove("is-open");
    if (returnFocus) this.button.focus();
  }

  handleKeydown(event) {
    if (this.button.getAttribute("aria-expanded") !== "true") return;

    if (event.key === "Escape") {
      event.preventDefault();
      this.close({ returnFocus: true });
      return;
    }

    if (event.key === "Tab" && this.menu.querySelectorAll) {
      const focusable = Array.from(
        this.menu.querySelectorAll(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      ).filter((el) => !el.hidden && (el.offsetParent !== null || el.offsetWidth > 0));

      if (focusable.length > 0) {
        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (event.shiftKey && this.document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && this.document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }
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

export const dismissFlashMessage = (messageElement) => {
  if (!messageElement) return;
  messageElement.classList?.add("is-dismissing");
  setTimeout(() => {
    const container = messageElement.parentElement;
    messageElement.remove?.();
    if (
      container &&
      container.classList?.contains?.("flash-messages") &&
      container.children?.length === 0
    ) {
      container.remove?.();
    }
  }, 200);
};

const initializedFlashDocuments = new WeakSet();

export const initializeFlashMessages = (documentRef = document) => {
  if (!documentRef?.addEventListener || initializedFlashDocuments.has(documentRef)) return;
  initializedFlashDocuments.add(documentRef);

  documentRef.addEventListener("click", (event) => {
    const target = event.target?.nodeType === 3 ? event.target.parentElement : event.target;
    const button = target?.closest?.("[data-dismiss-message]");
    if (!button) return;
    const message = button.closest?.(".flash-message");
    if (message) {
      dismissFlashMessage(message);
    }
  });
};

export const initializeSearchShortcut = (documentRef = document) => {
  if (!documentRef.addEventListener) return;
  documentRef.addEventListener("keydown", (event) => {
    if (
      event.key === "/" &&
      !["INPUT", "TEXTAREA", "SELECT"].includes(documentRef.activeElement?.tagName) &&
      !documentRef.activeElement?.isContentEditable
    ) {
      const searchTrigger = documentRef.querySelector(".site-header__search-trigger");
      if (searchTrigger) {
        event.preventDefault();
        searchTrigger.click();
      }
    }
  });
};

const initializeBase = () => {
  initializeMobileMenu();
  initializeFlashMessages();
  initializeSearchShortcut();
};

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeBase);
  } else {
    initializeBase();
  }
}
