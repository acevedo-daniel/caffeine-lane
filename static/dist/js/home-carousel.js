document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("carousel-container");
  const previous = document.getElementById("prev-btn");
  const next = document.getElementById("next-btn");
  if (!container || !previous || !next) return;

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
  previous.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", () => show(current + 1));
});
