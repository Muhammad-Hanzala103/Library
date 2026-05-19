document.addEventListener("DOMContentLoaded", () => {
  const activeLink = document.querySelector(".nav-item.active");
  if (activeLink) {
    activeLink.setAttribute("aria-current", "page");
  }
});

