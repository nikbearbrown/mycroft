// Reference site behaviour: the theme toggle, the mobile menu and search. No dependencies;
// works from file://.
(function () {
  "use strict";

  // Light by default. The choice is remembered in localStorage; if the browser refuses
  // storage (some do for file:// pages), the toggle still works for the current page.
  var root = document.documentElement;
  var themeButton = document.querySelector(".theme-toggle");
  function applyTheme(dark) {
    if (dark) root.dataset.theme = "dark"; else delete root.dataset.theme;
    if (themeButton) themeButton.setAttribute("aria-pressed", dark ? "true" : "false");
  }
  if (themeButton) {
    applyTheme(root.dataset.theme === "dark");
    themeButton.addEventListener("click", function () {
      var dark = root.dataset.theme !== "dark";
      applyTheme(dark);
      try { localStorage.setItem("docs-theme", dark ? "dark" : "light"); } catch (e) { /* not remembered */ }
    });
  }

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var input = document.getElementById("search-input");
  var list = document.getElementById("search-results");
  var status = document.getElementById("search-status");
  var index = window.DOCS_INDEX || [];
  if (!input || !list) return;

  var KIND_RANK = { page: 0, file: 1, section: 2, route: 3, "class": 4, "function": 5, issue: 6 };
  var active = -1;

  function score(entry, terms) {
    var title = entry.t.toLowerCase();
    var rest = ((entry.s || "") + " " + (entry.x || "")).toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      if (title === t) total += 100;
      else if (title.indexOf(t) === 0) total += 40;
      else if (title.indexOf(t) >= 0) total += 20;
      else if (rest.indexOf(t) >= 0) total += 5;
      else return 0;
    }
    return total - (KIND_RANK[entry.k] || 7);
  }

  function clear() {
    list.hidden = true;
    list.innerHTML = "";
    active = -1;
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  function run() {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { clear(); status.textContent = ""; return; }
    var terms = q.split(/\s+/);
    var hits = [];
    for (var i = 0; i < index.length; i++) {
      var s = score(index[i], terms);
      if (s > 0) hits.push([s, index[i]]);
    }
    hits.sort(function (a, b) { return b[0] - a[0]; });
    hits = hits.slice(0, 30);
    list.innerHTML = "";
    active = -1;
    if (!hits.length) {
      list.appendChild(el("li", "empty", "No matches"));
    }
    hits.forEach(function (h) {
      var e = h[1];
      var li = el("li");
      var a = el("a");
      a.href = e.u;
      a.appendChild(el("span", "kind", e.k));
      a.appendChild(document.createTextNode(e.t));
      if (e.s) a.appendChild(el("span", "where", e.s));
      li.appendChild(a);
      list.appendChild(li);
    });
    list.hidden = false;
    status.textContent = hits.length ? hits.length + " results" : "No matches";
  }

  function move(delta) {
    var links = list.querySelectorAll("a");
    if (!links.length) return;
    if (active >= 0) links[active].removeAttribute("aria-selected");
    active = (active + delta + links.length) % links.length;
    links[active].setAttribute("aria-selected", "true");
    links[active].scrollIntoView({ block: "nearest" });
  }

  input.addEventListener("input", run);
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowDown") { ev.preventDefault(); move(1); }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); move(-1); }
    else if (ev.key === "Enter") {
      var links = list.querySelectorAll("a");
      var target = links[active >= 0 ? active : 0];
      if (target) { ev.preventDefault(); window.location.href = target.href; }
    } else if (ev.key === "Escape") { clear(); input.value = ""; }
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "/" && document.activeElement !== input && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
      ev.preventDefault();
      input.focus();
    }
  });
  document.addEventListener("click", function (ev) {
    if (!ev.target.closest || !ev.target.closest(".search")) clear();
  });
})();
