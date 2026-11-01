// Small progressive enhancements; the site works fully without JavaScript.
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");

  // ---- theme toggle (remembers choice; otherwise follows the OS setting)
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var dark = root.dataset.theme
        ? root.dataset.theme === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.dataset.theme = dark ? "light" : "dark";
      localStorage.setItem("theme", root.dataset.theme);
    });
  }

  // ---- mobile menu
  var navBtn = document.querySelector(".nav-toggle");
  var navLinks = document.getElementById("nav-links");
  if (navBtn && navLinks) {
    navBtn.addEventListener("click", function () {
      var open = navLinks.classList.toggle("open");
      navBtn.setAttribute("aria-expanded", String(open));
    });
    navLinks.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        navLinks.classList.remove("open");
        navBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  // ---- header border once scrolled
  var header = document.querySelector(".site-header");
  var onScroll = function () { header && header.classList.toggle("scrolled", window.scrollY > 8); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---- publication numbering + filters
  var pubs = Array.prototype.slice.call(document.querySelectorAll(".pub"));
  var numberPubs = function () {
    var visible = pubs.filter(function (p) { return !p.hidden; });
    visible.forEach(function (p, i) { p.dataset.n = visible.length - i; });
  };
  numberPubs();
  document.querySelectorAll(".filter").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.dataset.filter;
      document.querySelectorAll(".filter").forEach(function (b) {
        var on = b === btn;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-pressed", String(on));
      });
      pubs.forEach(function (p) { p.hidden = f !== "all" && p.dataset.type !== f; });
      numberPubs();
    });
  });

  if (!("IntersectionObserver" in window)) return;

  // ---- highlight current section in nav
  var navMap = {};
  document.querySelectorAll('.nav-links a[href*="#"]').forEach(function (a) {
    navMap[a.getAttribute("href").split("#")[1]] = a;
  });
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var link = navMap[e.target.id];
      if (link && e.isIntersecting) {
        Object.keys(navMap).forEach(function (k) { navMap[k].classList.remove("active"); });
        link.classList.add("active");
      }
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  document.querySelectorAll("section[id]").forEach(function (s) { spy.observe(s); });

})();
