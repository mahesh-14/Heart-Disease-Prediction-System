document.addEventListener("DOMContentLoaded", function () {
  const navbarToggle = document.getElementById("navbar-toggle");
  const navbarLinks = document.querySelector(".nav-links");
  const overlay = document.getElementById("overlay");

  navbarToggle.addEventListener("click", function () {
    navbarLinks.classList.toggle("active");
    navbarToggle.classList.toggle("active");
    overlay.style.display =
      overlay.style.display === "block" ? "none" : "block";
  });
  const inputs = document.querySelectorAll(
    '.input-form input[type="text"]'
  );
  inputs.forEach((input, index) => {
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const nextIndex = index + 1;
        if (nextIndex < inputs.length) {
          inputs[nextIndex].focus();
        }
      }
    });
  });
});
