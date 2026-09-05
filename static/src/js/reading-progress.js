export class ReadingProgressController {
  constructor({
    progressBarSelector = "#reading-progress",
    contentSelector = ".post-detail__body",
    windowRef = typeof window !== "undefined" ? window : null,
  } = {}) {
    this.window = windowRef;
    this.progressBar = this.window?.document.querySelector(progressBarSelector);
    this.content = this.window?.document.querySelector(contentSelector);
  }

  initialize() {
    if (!this.window || !this.progressBar) return;

    const update = () => this.update();
    this.window.addEventListener("scroll", update, { passive: true });
    this.window.addEventListener("resize", update, { passive: true });
    this.update();
  }

  update() {
    if (!this.window || !this.progressBar) return;

    const docElem = this.window.document.documentElement;
    const scrollTop = this.window.scrollY || docElem.scrollTop || 0;
    const scrollHeight = docElem.scrollHeight - this.window.innerHeight;

    if (scrollHeight <= 0) {
      this.progressBar.style.width = "0%";
      return;
    }

    const progress = Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100));
    this.progressBar.style.width = `${progress}%`;
  }
}

export const initializeReadingProgress = () => {
  const controller = new ReadingProgressController();
  controller.initialize();
  return controller;
};

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initializeReadingProgress());
  } else {
    initializeReadingProgress();
  }
}
