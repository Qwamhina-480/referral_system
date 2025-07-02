function showSection(sectionId) {
      const sections = document.querySelectorAll(".section");
      sections.forEach(sec => sec.classList.add("hidden"));
      document.getElementById(sectionId).classList.remove("hidden");
    }

    document.addEventListener("DOMContentLoaded", () => {
      showSection("home");
    });