// Small progressive enhancements; the site works fully without JavaScript.
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // ---- theme toggle (remembers choice; otherwise follows the OS setting)
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var dark = root.dataset.theme
        ? root.dataset.theme === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.dataset.theme = dark ? "light" : "dark";
      store("theme", root.dataset.theme);
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
  var pubs = Array.prototype.slice.call(document.querySelectorAll(".pubs[reversed] .pub"));
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

  // ---- biography tabs (short / extended)
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    var select = function (tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
    };
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var n = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
        if (n === null) return;
        var next = tabs[(n + tabs.length) % tabs.length];
        select(next); next.focus();
      });
    });
  });

  // ---- copy biography text
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.querySelector(btn.dataset.copy);
      if (!panel) return;
      var paras = panel.id ? panel.querySelectorAll("p:not(.panel-note)") : [panel];
      var text = Array.prototype.map.call(paras, function (p) { return p.textContent.trim(); }).join("\n\n");
      var done = function () { var o = btn.textContent; btn.textContent = "Copied"; setTimeout(function () { btn.textContent = o; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done);
    });
  });

  // ---- enquiry forms: compose an e-mail (no server, nothing sent to third parties)
  document.querySelectorAll("form.enquiry").forEach(function (form) {
    var params = new URLSearchParams(window.location.search);
    var topic = params.get("topic");
    var select = form.querySelector("select[name=interest]");
    var setTopic = function (v) {
      if (!select || !v) return;
      Array.prototype.forEach.call(select.options, function (o) { if (o.dataset.key === v) select.value = o.value; });
    };
    if (topic) setTopic(topic);
    // entry-point links on the collaborate page preselect the matching interest
    document.querySelectorAll("[data-interest]").forEach(function (a) {
      a.addEventListener("click", function () {
        if (!select) return;
        setTopic(a.dataset.interest);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = form.elements, ok = true;
      ["name", "email", "message"].forEach(function (n) {
        var field = f[n].closest(".field");
        var bad = !f[n].value.trim() || (n === "email" && !/^\S+@\S+\.\S+$/.test(f[n].value));
        field.classList.toggle("invalid", bad);
        if (bad && ok) { f[n].focus(); ok = false; }
      });
      if (!ok) return;
      var kind = form.dataset.kind === "collaboration" ? "Collaboration enquiry" : "Enquiry";
      var subject = kind + ": " + f.interest.value;
      var body = "Name: " + f.name.value.trim() + "\n" +
        "Organisation: " + (f.organisation.value.trim() || "-") + "\n" +
        "E-mail: " + f.email.value.trim() + "\n" +
        "Area of interest: " + f.interest.value + "\n\n" + f.message.value.trim() + "\n";
      window.location.href = "mailto:" + form.dataset.to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    });
  });
})();
