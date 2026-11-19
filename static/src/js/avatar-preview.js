export class AvatarPreviewController {
  constructor({
    input,
    previewImg,
    errorContainer,
    documentRef = typeof document !== "undefined" ? document : null,
    maxSizeBytes = 5 * 1024 * 1024,
    allowedTypes = ["image/jpeg", "image/png", "image/webp"],
  } = {}) {
    this.input = input;
    this.previewImg = previewImg;
    this.errorContainer = errorContainer;
    this.document = documentRef;
    this.maxSizeBytes = maxSizeBytes;
    this.allowedTypes = allowedTypes;
    this.originalSrc = this.previewImg?.getAttribute?.("src") || this.previewImg?.src || "";
    this.isClearingInput = false;
  }

  initialize() {
    if (!this.input) return false;
    this.input.addEventListener("change", (event) => this.handleFileChange(event));
    return true;
  }

  getErrorMessage(datasetKey, attributeName, fallback) {
    return (
      this.errorContainer?.dataset?.[datasetKey] ||
      this.errorContainer?.getAttribute?.(attributeName) ||
      fallback
    );
  }

  clearRejectedInput() {
    if (!this.input) return;
    this.isClearingInput = true;
    try {
      try {
        this.input.value = "";
      } catch {
        // Ignore read-only value mocks in unit tests.
      }
      if (
        typeof this.input.dispatchEvent === "function" &&
        typeof Event === "function"
      ) {
        this.input.dispatchEvent(new Event("change", { bubbles: true }));
      }
    } finally {
      this.isClearingInput = false;
    }
  }

  handleFileChange(event) {
    if (this.isClearingInput) return;

    const file = event?.target?.files?.[0] || this.input?.files?.[0];
    if (!file) {
      this.resetPreview();
      return;
    }

    // Validate MIME type
    if (file.type && !this.allowedTypes.includes(file.type.toLowerCase())) {
      this.showError(
        this.getErrorMessage(
          "messageType",
          "data-message-type",
          "Images must use JPEG, PNG, or WebP format.",
        ),
      );
      this.resetPreview();
      this.clearRejectedInput();
      return;
    }

    // Validate file size (5MB limit)
    if (file.size && file.size > this.maxSizeBytes) {
      this.showError(
        this.getErrorMessage(
          "messageSize",
          "data-message-size",
          "Images must be 5 MB or smaller.",
        ),
      );
      this.resetPreview();
      this.clearRejectedInput();
      return;
    }

    this.clearError();
    this.applyPreview(file);
  }

  applyPreview(file) {
    if (!this.previewImg) return;

    if (typeof URL !== "undefined" && typeof URL.createObjectURL === "function") {
      const previewUrl = URL.createObjectURL(file);
      this.previewImg.src = previewUrl;
      this.previewImg.setAttribute?.("src", previewUrl);
      this.previewImg.classList?.add("has-custom-preview");
    }
  }

  resetPreview() {
    if (this.previewImg && this.originalSrc) {
      this.previewImg.src = this.originalSrc;
      this.previewImg.setAttribute?.("src", this.originalSrc);
      this.previewImg.classList?.remove("has-custom-preview");
    }
  }

  showError(message) {
    if (this.errorContainer) {
      this.errorContainer.textContent = message;
      this.errorContainer.removeAttribute?.("hidden");
      if (this.errorContainer.style) this.errorContainer.style.display = "block";
    }
  }

  clearError() {
    if (this.errorContainer) {
      this.errorContainer.textContent = "";
      this.errorContainer.setAttribute?.("hidden", "");
      if (this.errorContainer.style) this.errorContainer.style.display = "none";
    }
  }
}

export const initializeAvatarPreviews = (documentRef = typeof document !== "undefined" ? document : null) => {
  if (!documentRef) return [];

  const inputs = documentRef.querySelectorAll?.('[data-avatar-input="true"]') || [];
  const controllers = [];

  inputs.forEach((input) => {
    const form = input.closest?.("form");
    const previewImg = form?.querySelector?.("[data-avatar-preview-image]") || documentRef.querySelector?.("[data-avatar-preview-image]");
    const errorContainer = form?.querySelector?.("[data-avatar-error]") || documentRef.querySelector?.("[data-avatar-error]");

    const controller = new AvatarPreviewController({
      input,
      previewImg,
      errorContainer,
      documentRef,
    });
    controller.initialize();
    controllers.push(controller);
  });

  return controllers;
};

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initializeAvatarPreviews());
  } else {
    initializeAvatarPreviews();
  }
}
