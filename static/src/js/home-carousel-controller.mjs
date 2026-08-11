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
