document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("carousel-container");
  const previousButtons = document.querySelectorAll("[data-carousel-previous]");
  const nextButtons = document.querySelectorAll("[data-carousel-next]");

  if (!container || !previousButtons.length || !nextButtons.length) return;

  const slides = container.querySelectorAll(".carousel-slide");

  if (slides.length <= 1) return;

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

  previousButtons.forEach((button) => {
    button.addEventListener("click", () => show(current - 1));
  });

  nextButtons.forEach((button) => {
    button.addEventListener("click", () => show(current + 1));
  });

  show(0);

  setInterval(() => {
    show(current + 1);
  }, 5000);
});
