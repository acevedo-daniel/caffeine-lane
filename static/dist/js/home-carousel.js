import { HomeCarouselController } from "./home-carousel-controller.mjs";

const AUTOPLAY_DELAY_MS = 7000;
const SWIPE_THRESHOLD_PX = 40;

document.addEventListener("DOMContentLoaded", () => {
  const hero = document.querySelector("[aria-roledescription='carousel']");
  const track = document.getElementById("carousel-container");
  if (!hero || !track) return;

  const slides = [...track.querySelectorAll(".carousel-slide")];
  if (!slides.length) return;

  const previousButton = hero.querySelector("[data-carousel-previous]");
  const nextButton = hero.querySelector("[data-carousel-next]");
  const indexElement = hero.querySelector("[data-carousel-index]");
  const controller = new HomeCarouselController({ track, slides, indexElement });
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let autoplayTimer;
  let hovering = false;
  let focusWithin = false;
  let touchStartX = null;

  const hasMultipleSlides = slides.length > 1;
  const pauseAutoplay = () => {
    window.clearTimeout(autoplayTimer);
    autoplayTimer = undefined;
  };
  const canAutoplay = () => (
    hasMultipleSlides
    && !hovering
    && !focusWithin
    && !document.hidden
    && !reducedMotion.matches
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

  hero.addEventListener("mouseenter", () => {
    hovering = true;
    pauseAutoplay();
  });
  hero.addEventListener("mouseleave", () => {
    hovering = false;
    scheduleAutoplay();
  });
  hero.addEventListener("focusin", () => {
    focusWithin = true;
    pauseAutoplay();
  });
  hero.addEventListener("focusout", (event) => {
    if (hero.contains(event.relatedTarget)) return;
    focusWithin = false;
    scheduleAutoplay();
  });
  document.addEventListener("visibilitychange", scheduleAutoplay);
  reducedMotion.addEventListener("change", scheduleAutoplay);

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
