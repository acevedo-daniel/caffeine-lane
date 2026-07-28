document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("filter-toggle-btn");
  const section = document.getElementById("filter-section");
  if (toggle && section) {
    toggle.addEventListener("click", () => section.classList.toggle("hidden"));
  }
});
