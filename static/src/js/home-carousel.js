document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("carousel-container");
  const previous = document.querySelectorAll("[data-carousel-previous]");
  const next = document.querySelectorAll("[data-carousel-next]");
  if (!container || !previous.length || !next.length) return;

  const slides = container.querySelectorAll(".carousel-slide");
  let current = 0;
  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === current;
      slide.setAttribute("aria-hidden", String(!isActive));
      slide.inert = !isActive;
    });
    container.style.transform = `translateX(-${current * 100}%)`;
  };
  show(current);
  previous.forEach((button) => {
    button.addEventListener("click", () => show(current - 1));
  });
  next.forEach((button) => {
    button.addEventListener("click", () => show(current + 1));
  });
});
