document.addEventListener("DOMContentLoaded", function() {
  var htmlElement = document.getElementsByTagName("html")[0];
  var currentTheme = localStorage.getItem("theme");
  var themeButton = document.getElementById("themeButton");

  if (!currentTheme) {
    currentTheme = "light";
  }

  themeButton.checked = currentTheme === "dark";

  function toggleTheme() {
    var newTheme = htmlElement.getAttribute("data-bs-theme") === "light" ? "dark" : "light";
    htmlElement.setAttribute("data-bs-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  }

  themeButton.addEventListener("click", toggleTheme);
});
