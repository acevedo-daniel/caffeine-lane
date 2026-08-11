export const normalizeSlideIndex = (index, count) => {
  if (!count) return 0;
  return ((index % count) + count) % count;
};

export const formatSlideIndex = (index) => String(index + 1).padStart(2, "0");

export class HomeCarouselController {
  constructor({ track, slides, indexElement }) {
    this.track = track;
    this.slides = [...slides];
    this.indexElement = indexElement;
    this.current = 0;
  }

  goTo(index) {
    this.current = normalizeSlideIndex(index, this.slides.length);
    this.track.style.transform = `translateX(-${this.current * 100}%)`;

    this.slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === this.current;
      slide.setAttribute("aria-hidden", String(!isActive));
      slide.inert = !isActive;
    });

    if (this.indexElement) this.indexElement.textContent = formatSlideIndex(this.current);
    return this.current;
  }

  next() {
    return this.goTo(this.current + 1);
  }

  previous() {
    return this.goTo(this.current - 1);
  }
}

const AUTOPLAY_DELAY_MS = 7000;
const SWIPE_THRESHOLD_PX = 40;

if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded", () => {
  const hero = document.querySelector("[aria-roledescription='carousel']");
  const track = document.getElementById("carousel-container");
  if (!hero || !track) return;

  const slides = [...track.querySelectorAll(".carousel-slide")];
  if (!slides.length) return;

  const previousButton = hero.querySelector("[data-carousel-previous]");
  const nextButton = hero.querySelector("[data-carousel-next]");
  const indexElement = hero.querySelector("[data-carousel-index]");
  const controller = new HomeCarouselController({ track, slides, indexElement });
  let autoplayTimer;
  let hovering = false;
  let focusWithin = false;
  let touchStartX = null;

  const hasMultipleSlides = slides.length > 1;
  const prefersReducedMotion = window.matchMedia?.(
    "(prefers-reduced-motion: reduce)",
  ).matches ?? false;
  const pauseAutoplay = () => {
    window.clearTimeout(autoplayTimer);
    autoplayTimer = undefined;
  };
  const canAutoplay = () => (
    hasMultipleSlides
    && !prefersReducedMotion
    && !hovering
    && !focusWithin
    && !document.hidden
  );
  const scheduleAutoplay = () => {
    pauseAutoplay();
    if (!canAutoplay()) return;
    autoplayTimer = window.setTimeout(() => {
      controller.next();
      scheduleAutoplay();
    }, AUTOPLAY_DELAY_MS);
  };
  const navigate = (direction) => {
    if (direction === "next") controller.next();
    else controller.previous();
    scheduleAutoplay();
  };

  controller.goTo(0);
  track.dataset.carouselInitialized = "true";

  if (!hasMultipleSlides) return;

  previousButton?.addEventListener("click", () => navigate("previous"));
  nextButton?.addEventListener("click", () => navigate("next"));

  // Let the editorial panel and its controls remain usable while the carousel
  // continues its rhythm. Only pausing over the photograph preserves the
  // requested reading time without making autoplay appear inactive whenever
  // the pointer rests on the Hero.
  hero.querySelectorAll(".home-hero__media").forEach((media) => {
    media.addEventListener("mouseenter", () => {
      hovering = true;
      pauseAutoplay();
    });
    media.addEventListener("mouseleave", () => {
      hovering = false;
      scheduleAutoplay();
    });
  });
  hero.addEventListener("focusin", (event) => {
    // Pointer clicks also focus buttons. Pause for keyboard-visible focus so a
    // mouse click can restart autoplay while keyboard users retain control.
    if (!event.target.matches(":focus-visible")) return;
    focusWithin = true;
    pauseAutoplay();
  });
  hero.addEventListener("pointerdown", () => {
    if (!focusWithin) return;
    focusWithin = false;
    scheduleAutoplay();
  });
  hero.addEventListener("focusout", (event) => {
    if (hero.contains(event.relatedTarget)) return;
    focusWithin = false;
    scheduleAutoplay();
  });
  document.addEventListener("visibilitychange", scheduleAutoplay);

  track.addEventListener("pointerdown", (event) => {
    if (event.pointerType === "touch") touchStartX = event.clientX;
  });
  track.addEventListener("pointerup", (event) => {
    if (touchStartX === null || event.pointerType !== "touch") return;
    const distance = event.clientX - touchStartX;
    touchStartX = null;
    if (Math.abs(distance) < SWIPE_THRESHOLD_PX) return;
    navigate(distance < 0 ? "next" : "previous");
  });
  track.addEventListener("pointercancel", () => { touchStartX = null; });

  scheduleAutoplay();
});
