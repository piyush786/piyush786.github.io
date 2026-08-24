(() => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector("#main-navigation");
  const links = [...document.querySelectorAll(".main-nav a[href^='#']")];
  const year = document.querySelector(".site-year");
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  if (year) {
    year.textContent = String(new Date().getFullYear());
  }

  const revealElements = [...document.querySelectorAll("[data-reveal]")];
  const revealAll = () => {
    revealElements.forEach((element) => element.classList.add("is-visible"));
  };

  if (prefersReducedMotion || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -10%", threshold: 0.12 },
    );

    revealElements.forEach((element) => revealObserver.observe(element));
  }

  if (toggle && nav) {
    const setMenu = (open, { restoreFocus = false } = {}) => {
      nav.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute(
        "aria-label",
        open ? "Close navigation" : "Open navigation",
      );

      if (restoreFocus) {
        toggle.focus();
      }
    };

    toggle.addEventListener("click", () => {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });

    links.forEach((link) => {
      link.addEventListener("click", () => setMenu(false));
    });

    document.addEventListener("keydown", (event) => {
      const menuOpen = toggle.getAttribute("aria-expanded") === "true";
      if (event.key === "Escape" && menuOpen) {
        setMenu(false, { restoreFocus: true });
      }
    });

    document.addEventListener("click", (event) => {
      const menuOpen = toggle.getAttribute("aria-expanded") === "true";
      const target = event.target;
      if (
        menuOpen
        && target instanceof Node
        && !nav.contains(target)
        && !toggle.contains(target)
      ) {
        setMenu(false);
      }
    });

    const mobileNavigation = window.matchMedia("(max-width: 900px)");
    const handleViewportChange = (event) => {
      if (!event.matches) {
        setMenu(false);
      }
    };

    if (typeof mobileNavigation.addEventListener === "function") {
      mobileNavigation.addEventListener("change", handleViewportChange);
    } else {
      mobileNavigation.addListener(handleViewportChange);
    }
  }

  if ("IntersectionObserver" in window) {
    const sections = links
      .map((link) => document.querySelector(link.hash))
      .filter(Boolean);

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) {
            continue;
          }

          links.forEach((link) => {
            const active = link.hash === `#${entry.target.id}`;
            link.classList.toggle("is-active", active);
            if (active) {
              link.setAttribute("aria-current", "location");
            } else {
              link.removeAttribute("aria-current");
            }
          });
        }
      },
      { rootMargin: "-35% 0px -55%", threshold: 0 },
    );

    sections.forEach((section) => observer.observe(section));
  }
})();
