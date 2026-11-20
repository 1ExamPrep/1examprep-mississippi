/* River Steel motion and filters. Every word of content is in the HTML; this only animates and filters it. */
(function () {
  var d = document, root = d.documentElement;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("js");

  d.addEventListener("DOMContentLoaded", function () {
    /* reveal on scroll, with a small stagger for cards in the same row */
    var els = [].slice.call(d.querySelectorAll(".reveal"));
    if (!("IntersectionObserver" in window) || reduce) {
      els.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        var i = 0;
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.style.transitionDelay = Math.min(i++ * 60, 360) + "ms";
            en.target.classList.add("in");
            io.unobserve(en.target);
          }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      els.forEach(function (el) { io.observe(el); });
    }

    /* count-up numbers */
    var nums = [].slice.call(d.querySelectorAll("[data-count]"));
    function fmt(n, el) { return (el.dataset.prefix || "") + Math.round(n).toLocaleString("en-US") + (el.dataset.suffix || ""); }
    function run(el) {
      var end = +el.dataset.count, t0 = null, dur = 1400;
      function tick(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(end * e, el);
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }
    if (!reduce && "IntersectionObserver" in window) {
      var co = new IntersectionObserver(function (en) {
        en.forEach(function (x) { if (x.isIntersecting) { run(x.target); co.unobserve(x.target); } });
      }, { threshold: 0.6 });
      nums.forEach(function (n) { co.observe(n); });
    }

    /* header shrink, hero parallax, timeline progress */
    var top = d.querySelector("[data-shrink]");
    var hero = d.querySelector("[data-parallax]");
    var tl = d.querySelector("[data-timeline]");
    var ticking = false;
    function onScroll() {
      var y = window.scrollY;
      if (top) top.classList.toggle("small", y > 40);
      if (hero && !reduce && y < 1000) hero.style.transform = "translate3d(0," + (y * 0.25).toFixed(1) + "px,0)";
      if (tl) {
        var r = tl.getBoundingClientRect(), vh = window.innerHeight;
        var p = Math.max(0, Math.min(1, (vh * 0.75 - r.top) / r.height));
        tl.style.setProperty("--p", p.toFixed(3));
      }
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
    }, { passive: true });
    onScroll();

    /* duplicate marquee track for a seamless loop */
    var mt = d.querySelector(".m-track");
    if (mt) mt.innerHTML += mt.innerHTML;

    /* license finder on the home page */
    var input = d.getElementById("finder");
    if (input) {
      var cards = [].slice.call(d.querySelectorAll(".ccard"));
      var groups = [].slice.call(d.querySelectorAll("[data-group]"));
      var none = d.querySelector(".no-match");
      var q0 = new URLSearchParams(location.search).get("q");
      if (q0) input.value = q0;
      var filter = function () {
        var q = input.value.trim().toLowerCase(), shown = 0;
        cards.forEach(function (c) {
          var hit = !q || c.dataset.name.indexOf(q) > -1;
          c.classList.toggle("hide", !hit);
          if (hit) { shown++; c.classList.add("in"); }
        });
        groups.forEach(function (g) { g.classList.toggle("hide", !g.querySelector(".ccard:not(.hide)")); });
        if (none) none.hidden = shown > 0;
      };
      input.addEventListener("input", filter);
      input.form.addEventListener("submit", function (ev) {
        ev.preventDefault(); filter();
        var t = d.getElementById("find-your-license"); if (t) t.scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
      });
      if (q0) filter();
    }

    /* contact form: the iframe and its script are added here so the served HTML has no iframe or body script */
    var fe = d.querySelector(".form-embed");
    if (fe) {
      var id = fe.dataset.formId;
      var fr = d.createElement("iframe");
      fr.src = "https://app.1examprep.com/widget/form/" + id;
      fr.id = "inline-" + id;
      fr.title = fe.dataset.formName;
      fr.style.cssText = "width:100%;height:" + fe.dataset.height + "px;border:none;border-radius:8px";
      var attrs = {
        "data-layout": "{'id':'INLINE'}", "data-trigger-type": "alwaysShow", "data-trigger-value": "",
        "data-activation-type": "alwaysActivated", "data-activation-value": "",
        "data-deactivation-type": "neverDeactivate", "data-deactivation-value": "",
        "data-form-name": fe.dataset.formName, "data-height": fe.dataset.height,
        "data-layout-iframe-id": "inline-" + id, "data-form-id": id,
        "data-cookie-consent": "true", "data-cookie-consent-provider": "auto"
      };
      Object.keys(attrs).forEach(function (k) { fr.setAttribute(k, attrs[k]); });
      fr.addEventListener("load", function () { fe.classList.add("loaded"); });
      fe.appendChild(fr);
      var sc = d.createElement("script");
      sc.src = "https://app.1examprep.com/js/form_embed.js";
      sc.async = true;
      d.body.appendChild(sc);
    }

    /* package-type chips on license pages */
    var chips = [].slice.call(d.querySelectorAll(".chip"));
    chips.forEach(function (ch) {
      ch.addEventListener("click", function () {
        var f = ch.dataset.filter;
        chips.forEach(function (c) { c.classList.toggle("on", c === ch); });
        d.querySelectorAll(".pcard").forEach(function (p) {
          var hit = f === "all" || p.dataset.type === f;
          p.classList.toggle("hide", !hit);
          if (hit) p.classList.add("in");
        });
        d.querySelectorAll(".grid").forEach(function (g) {
          var sec = g.closest(".sec");
          if (sec && !sec.querySelector(".chips")) sec.hidden = !g.querySelector(".pcard:not(.hide)");
        });
      });
    });
  });
})();
