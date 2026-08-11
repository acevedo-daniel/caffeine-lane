export class CommentReplyController {
  constructor({ documentRef = document } = {}) {
    this.document = documentRef;
    this.entries = [];
    this.activeEntry = null;
  }

  initialize() {
    const buttons = this.document.querySelectorAll("[data-reply-open]");

    buttons.forEach((button) => {
      const formId = button.getAttribute("aria-controls");
      const form = formId ? this.document.getElementById(formId) : null;
      if (!form) return;

      const entry = {
        button,
        form,
        textarea: form.querySelector("textarea"),
        cancelButton: form.querySelector("[data-reply-cancel]"),
      };
      this.entries.push(entry);
      this.close(entry);

      button.addEventListener("click", () => this.toggle(entry));
      entry.cancelButton?.addEventListener("click", () => this.close(entry, { returnFocus: true }));
    });

    if (!this.entries.length) return;

    this.document.documentElement.classList.add("has-reply-enhancement");
    this.document.addEventListener("keydown", (event) => this.handleKeydown(event));
  }

  toggle(entry) {
    if (this.activeEntry === entry) {
      this.close(entry, { returnFocus: true });
      return;
    }
    this.open(entry);
  }

  open(entry) {
    this.entries.forEach((candidate) => {
      if (candidate !== entry) this.close(candidate);
    });

    entry.form.hidden = false;
    entry.button.setAttribute("aria-expanded", "true");
    this.activeEntry = entry;
    entry.textarea?.focus();
  }

  close(entry, { returnFocus = false } = {}) {
    entry.form.hidden = true;
    entry.button.setAttribute("aria-expanded", "false");
    if (this.activeEntry === entry) this.activeEntry = null;
    if (returnFocus) entry.button.focus();
  }

  handleKeydown(event) {
    if (event.key !== "Escape" || !this.activeEntry) return;
    event.preventDefault();
    this.close(this.activeEntry, { returnFocus: true });
  }
}

export const initializeCommentReplies = (documentRef = document) => {
  const controller = new CommentReplyController({ documentRef });
  controller.initialize();
  return controller;
};

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => initializeCommentReplies());
}
