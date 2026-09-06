export const THEME_STORAGE_KEY = "caffeine_lane_theme";
export const THEME_DARK = "dark";
export const THEME_LIGHT = "light";

export class ThemeController {
  constructor({
    storage = typeof localStorage !== "undefined" ? localStorage : null,
    documentRef = typeof document !== "undefined" ? document : null,
    windowRef = typeof window !== "undefined" ? window : null,
  } = {}) {
    this.storage = storage;
    this.document = documentRef;
    this.window = windowRef;
    this.mediaQuery = null;
    this.boundHandleMediaChange = null;
    this.boundHandleStorage = null;
  }

  getStoredTheme() {
    if (!this.storage) return null;
    try {
      const value = this.storage.getItem(THEME_STORAGE_KEY);
      return value === THEME_DARK || value === THEME_LIGHT ? value : null;
    } catch {
      return null;
    }
  }

  getSystemTheme() {
    if (!this.window?.matchMedia) return THEME_DARK;
    return this.window.matchMedia("(prefers-color-scheme: light)").matches
      ? THEME_LIGHT
      : THEME_DARK;
  }

  getCurrentTheme() {
    return this.getStoredTheme() || THEME_DARK;
  }

  isDark() {
    return this.getCurrentTheme() === THEME_DARK;
  }

  setTheme(theme, { persist = true } = {}) {
    const isDark = theme === THEME_DARK;
    const resolvedTheme = isDark ? THEME_DARK : THEME_LIGHT;

    if (this.document?.documentElement) {
      this.document.documentElement.setAttribute("data-theme", resolvedTheme);
      if (isDark) {
        this.document.documentElement.classList.add("dark");
      } else {
        this.document.documentElement.classList.remove("dark");
      }
    }

    if (persist && this.storage) {
      try {
        this.storage.setItem(THEME_STORAGE_KEY, resolvedTheme);
      } catch {
        // Ignore storage write errors (e.g. private mode)
      }
    }

    this.updateControls(resolvedTheme);

    if (this.document?.dispatchEvent) {
      try {
        const EventConstructor = this.window?.CustomEvent || (typeof CustomEvent !== "undefined" ? CustomEvent : null);
        if (EventConstructor) {
          const event = new EventConstructor("caffeine-theme-change", {
            detail: { theme: resolvedTheme, isDark },
          });
          this.document.dispatchEvent(event);
        }
      } catch {
        // Ignore dispatch error in unsupported environments
      }
    }

    return resolvedTheme;
  }

  toggle() {
    const currentTheme = this.getCurrentTheme();
    const nextTheme = currentTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
    return this.setTheme(nextTheme, { persist: true });
  }

  updateControls(currentTheme = this.getCurrentTheme()) {
    if (!this.document?.querySelectorAll) return;
    const isDark = currentTheme === THEME_DARK;
    const toggles = this.document.querySelectorAll("[data-theme-toggle]");

    toggles.forEach((button) => {
      button.setAttribute("aria-pressed", isDark ? "true" : "false");
      const nextThemeLabel = isDark
        ? (button.getAttribute("data-label-light") || "Switch to light theme")
        : (button.getAttribute("data-label-dark") || "Switch to dark theme");
      button.setAttribute("title", nextThemeLabel);

      const stateText = button.querySelector(".theme-toggle__state-text");
      if (stateText) {
        stateText.textContent = isDark
          ? (button.getAttribute("data-text-dark") || "Oscuro")
          : (button.getAttribute("data-text-light") || "Claro");
      }
    });
  }

  initialize() {
    if (!this.document) return false;

    const currentTheme = this.getCurrentTheme();
    this.setTheme(currentTheme, { persist: false });

    const toggles = this.document.querySelectorAll("[data-theme-toggle]");
    toggles.forEach((button) => {
      button.addEventListener("click", () => {
        this.toggle();
      });
    });

    if (this.window?.matchMedia) {
      this.mediaQuery = this.window.matchMedia("(prefers-color-scheme: dark)");
      this.boundHandleMediaChange = (event) => {
        if (!this.getStoredTheme()) {
          this.setTheme(event.matches ? THEME_DARK : THEME_LIGHT, { persist: false });
        }
      };
      if (this.mediaQuery.addEventListener) {
        this.mediaQuery.addEventListener("change", this.boundHandleMediaChange);
      } else if (this.mediaQuery.addListener) {
        this.mediaQuery.addListener(this.boundHandleMediaChange);
      }
    }

    if (this.window?.addEventListener) {
      this.boundHandleStorage = (event) => {
        if (event.key === THEME_STORAGE_KEY) {
          const newTheme = event.newValue || this.getSystemTheme();
          this.setTheme(newTheme, { persist: false });
        }
      };
      this.window.addEventListener("storage", this.boundHandleStorage);
    }

    return true;
  }

  destroy() {
    if (this.mediaQuery && this.boundHandleMediaChange) {
      if (this.mediaQuery.removeEventListener) {
        this.mediaQuery.removeEventListener("change", this.boundHandleMediaChange);
      } else if (this.mediaQuery.removeListener) {
        this.mediaQuery.removeListener(this.boundHandleMediaChange);
      }
    }
    if (this.window?.removeEventListener && this.boundHandleStorage) {
      this.window.removeEventListener("storage", this.boundHandleStorage);
    }
  }
}

export const initializeThemeToggle = (options = {}) => {
  const controller = new ThemeController(options);
  controller.initialize();
  return controller;
};
