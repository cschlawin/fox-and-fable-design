/**
 * Fox & Fable — homepage behaviour
 * Vanilla JS, no dependencies. Loaded from 'self' only (see CSP).
 *  1. Progressive-enhancement flag (.no-js → .js)
 *  2. Mobile navigation toggle
 *  3. Consultation form: client-side validation + "preview only" note (mock-up: never submits, never uploads)
 *  4. Gallery: category filters + accessible <dialog> lightbox
 *
 * Security notes:
 *  - User input is only ever written to the page with textContent, never innerHTML.
 *  - Client-side validation improves UX only; it is NOT a security control.
 *    A real backend must re-validate, rate-limit, and spam-filter every submission.
 */
(function () {
  "use strict";

  // 1. Progressive enhancement ------------------------------------------------
  document.documentElement.classList.replace("no-js", "js");

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initForm();
    initGallery();
    var year = document.getElementById("year");
    if (year) year.textContent = String(new Date().getFullYear());
  });

  // 2. Mobile navigation -------------------------------------------------------
  function initNav() {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("primary-nav");
    if (!toggle || !nav) return;
    var label = toggle.querySelector(".visually-hidden");

    function setOpen(open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      if (label) label.textContent = open ? "Close menu" : "Menu";
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    // Close after choosing a link, on Escape, or when resizing to desktop.
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
    window.matchMedia("(min-width: 1100px)").addEventListener("change", function (mq) {
      if (mq.matches) setOpen(false);
    });
  }

  // 3. Consultation form -------------------------------------------------------
  var EMAIL_RE = /^[^\s@<>()[\]\\,;:"]+@[^\s@<>()[\]\\,;:"]+\.[A-Za-z]{2,}$/;
  var PHONE_RE = /^[0-9+().\-\s]{7,20}$/;
  // Strip control characters (except newline/tab in the message) and trim.
  function clean(value, allowNewlines) {
    var re = allowNewlines ? /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g : /[\u0000-\u001F\u007F]/g;
    return String(value).replace(re, "").trim();
  }

  var RULES = {
    name:     { required: "Please tell us your name.", max: 80 },
    email:    { required: "Please add an email so we can reply.", max: 254,
                test: function (v) { return EMAIL_RE.test(v); }, invalid: "That email doesn't look quite right. Try name@example.com." },
    phone:    { max: 20, test: function (v) { return v === "" || (PHONE_RE.test(v) && v.replace(/\D/g, "").length >= 7); },
                invalid: "Please use digits, spaces, or + ( ) - only, at least 7 digits." },
    city:     { required: "Which city is the project in?", max: 60 },
    room:     { required: "Please choose a room type." },
    project:  { required: "Please choose a project type." },
    budget:   { required: "Please choose a budget range." },
    timeline: { required: "Please choose a timeline." },
    message:  { max: 2000, multiline: true }
  };

  function initForm() {
    var form = document.getElementById("consult-form");
    if (!form) return;
    var status = document.getElementById("form-status");
    var message = form.elements.message;
    var counter = document.getElementById("message-count");

    if (message && counter) {
      message.addEventListener("input", function () {
        counter.textContent = message.value.length + " / " + RULES.message.max + " characters";
      });
    }

    // Re-validate a field as the visitor fixes it (only after it was flagged).
    form.addEventListener("input", function (e) {
      var field = e.target;
      if (field.getAttribute("aria-invalid") === "true") validateField(form, field.name);
    });
    form.addEventListener("change", function (e) {
      if (e.target.getAttribute("aria-invalid") === "true") validateField(form, e.target.name);
    });

    var files = initUpload(form);

    form.addEventListener("submit", function (e) {
      e.preventDefault(); // Mock-up: nothing is ever sent or uploaded (the CSP also sets form-action 'none').

      // Honeypot: real people never see this field. Silently "succeed" for bots.
      if (form.elements.website && form.elements.website.value !== "") {
        form.reset();
        return;
      }

      var firstInvalid = null;
      var errors = 0;
      Object.keys(RULES).forEach(function (name) {
        if (!validateField(form, name)) {
          errors++;
          if (!firstInvalid) firstInvalid = form.elements[name];
        }
      });
      if (files && !files.validate()) {
        errors++;
        if (!firstInvalid) firstInvalid = files.input;
      }

      status.className = "form-status";
      status.replaceChildren();

      if (errors) {
        status.classList.add("is-error");
        status.textContent = errors === 1
          ? "One field needs a quick look before we can continue."
          : errors + " fields need a quick look before we can continue.";
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      // Preview note. Built with DOM nodes + textContent (never innerHTML). The form is NOT reset,
      // so the visitor keeps what they typed and can copy it into an email.
      var firstName = clean(form.elements.name.value).split(/\s+/)[0];
      var heading = document.createElement("strong");
      heading.textContent = "Thank you, " + firstName + ".";
      var body = document.createElement("span");
      body.append("This form is a preview, and nothing was sent" + (files && files.count() ? " or uploaded" : "") +
        ". Please email us at ");
      var mail = document.createElement("a");
      mail.href = "mailto:hello@foxandfable.com";
      mail.textContent = "hello@foxandfable.com";
      body.append(mail, " to start a project.");
      status.classList.add("is-success");
      status.append(heading, body);
      status.setAttribute("tabindex", "-1");
      status.focus();
    });
  }

  // "Share your space" upload (mock-up). Only the names, sizes and types of the chosen files are looked at
  // to list them; files are never read, uploaded or sent anywhere (the input has no name attribute).
  var UPLOAD = {
    maxFiles: 10,
    maxBytes: 10 * 1024 * 1024,
    exts: ["jpg", "jpeg", "png", "webp", "heic", "heif", "pdf"]
  };
  function formatSize(bytes) {
    return bytes >= 1048576 ? (bytes / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(bytes / 1024)) + " KB";
  }
  function initUpload(form) {
    var input = document.getElementById("files");
    var list = document.getElementById("files-list");
    var error = document.getElementById("files-error");
    if (!input || !list || !error) return null;
    var zone = input.closest(".upload-zone");
    var selected = [];
    var canEdit = typeof DataTransfer === "function";
    try { if (canEdit) new DataTransfer(); } catch (err) { canEdit = false; }

    function setError(msg) {
      error.textContent = msg;
      if (msg) { input.setAttribute("aria-invalid", "true"); zone.classList.add("is-invalid"); }
      else { input.removeAttribute("aria-invalid"); zone.classList.remove("is-invalid"); }
    }
    function sync() {
      if (!canEdit) return;
      var dt = new DataTransfer();
      selected.forEach(function (f) { dt.items.add(f); });
      input.files = dt.files;
    }
    function render() {
      list.replaceChildren();
      selected.forEach(function (f, i) {
        var li = document.createElement("li");
        var name = document.createElement("span");
        name.className = "file-name";
        name.textContent = f.name;
        name.title = f.name;
        var size = document.createElement("span");
        size.className = "file-size";
        size.textContent = formatSize(f.size);
        li.append(name, size);
        if (canEdit) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "file-remove";
          btn.textContent = "Remove";
          btn.setAttribute("aria-label", "Remove " + f.name);
          btn.addEventListener("click", function () {
            selected.splice(i, 1);
            sync(); render(); setError("");
            input.focus();
          });
          li.append(btn);
        }
        list.append(li);
      });
      list.hidden = selected.length === 0;
    }
    function ok(f) {
      var ext = (f.name.split(".").pop() || "").toLowerCase();
      return UPLOAD.exts.indexOf(ext) !== -1;
    }

    input.addEventListener("change", function () {
      var incoming = Array.prototype.slice.call(input.files || []);
      var notes = [];
      var base = canEdit ? selected.slice() : [];
      incoming.forEach(function (f) {
        if (!ok(f)) { notes.push(f.name + " isn't a JPG, PNG, HEIC, WebP or PDF."); return; }
        if (f.size > UPLOAD.maxBytes) { notes.push(f.name + " is " + formatSize(f.size) + "; please keep each file under 10 MB."); return; }
        var dup = base.some(function (g) { return g.name === f.name && g.size === f.size && g.lastModified === f.lastModified; });
        if (dup) return;
        if (base.length >= UPLOAD.maxFiles) { notes.push("You can share up to " + UPLOAD.maxFiles + " files, so some were left out."); return; }
        base.push(f);
      });
      selected = base;
      sync(); render();
      // Keep only the first "up to 10" note.
      setError(notes.filter(function (n, i) { return notes.indexOf(n) === i; }).join(" "));
    });

    ["dragenter", "dragover"].forEach(function (t) { input.addEventListener(t, function () { zone.classList.add("is-dragover"); }); });
    ["dragleave", "drop"].forEach(function (t) { input.addEventListener(t, function () { zone.classList.remove("is-dragover"); }); });

    return {
      input: input,
      count: function () { return selected.length; },
      validate: function () {
        var bad = selected.filter(function (f) { return !ok(f) || f.size > UPLOAD.maxBytes; });
        if (bad.length || selected.length > UPLOAD.maxFiles) {
          setError("Please remove files that aren't images or PDFs, are over 10 MB, or go past the 10-file limit.");
          return false;
        }
        return true;
      }
    };
  }

  function validateField(form, name) {
    var field = form.elements[name];
    var rule = RULES[name];
    if (!field || !rule) return true;

    var value = clean(field.value, rule.multiline);
    var msg = "";
    if (rule.required && value === "") msg = rule.required;
    else if (rule.max && value.length > rule.max) msg = "Please keep this under " + rule.max + " characters.";
    else if (rule.test && value !== "" && !rule.test(value)) msg = rule.invalid;

    var error = document.getElementById(name + "-error");
    if (msg) {
      field.setAttribute("aria-invalid", "true");
      if (error) error.textContent = msg;
      return false;
    }
    field.removeAttribute("aria-invalid");
    if (error) error.textContent = "";
    return true;
  }

  // 4. Gallery -----------------------------------------------------------------
  // Markup contract (gallery.html): each project is
  //   <figure class="gallery-item" data-category="playhouses|bunk-rooms|closets|bedrooms|living-spaces|commercial"> (space-separated for more than one)
  //     <a class="gallery-link" href="full-size image"><img alt="..."></a>
  //     <div class="gallery-set" hidden><a href="photo-2" data-alt="..." data-width data-height></a>…</div>  (optional)
  //     <figcaption>...</figcaption>
  //   </figure>
  // Without JS the links simply open the full image; with JS they open the lightbox.
  function initGallery() {
    var grid = document.getElementById("gallery-grid");
    if (!grid) return;
    var items = Array.prototype.slice.call(grid.querySelectorAll(".gallery-item"));
    var buttons = Array.prototype.slice.call(document.querySelectorAll(".filter-btn"));
    var status = document.getElementById("gallery-status");

    // Filters
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var filter = btn.getAttribute("data-filter");
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        var shown = 0;
        items.forEach(function (item) {
          var cats = (item.getAttribute("data-category") || "").split(/\s+/);
          var match = filter === "all" || cats.indexOf(filter) !== -1;
          item.hidden = !match;
          if (match) shown++;
        });
        if (status) status.textContent = "Showing " + shown + " of " + items.length + " projects (" + btn.textContent + ").";
      });
    });

    // Lightbox
    var dialog = document.getElementById("lightbox");
    if (!dialog || typeof dialog.showModal !== "function") return; // fall back to plain links
    var img = document.getElementById("lightbox-img");
    var caption = document.getElementById("lightbox-caption");
    var count = document.getElementById("lightbox-count");
    var current = -1;
    var trigger = null;

    // Only photo items take part in the lightbox; video items (no .gallery-link) play inline.
    function visibleItems() {
      return items.filter(function (item) { return !item.hidden && item.querySelector(".gallery-link"); });
    }

    // Only allow same-origin image URLs into the lightbox (defence in depth).
    function safeSrc(href) {
      try {
        var url = new URL(href, window.location.href);
        if (url.origin !== window.location.origin && url.protocol !== "file:") return null;
        return url.href;
      } catch (e) { return null; }
    }

    // A project can carry extra photos: <div class="gallery-set" hidden><a href data-alt data-width data-height data-label></div>.
    function slideFrom(a) {
      return { href: a.getAttribute("href"), alt: a.getAttribute("data-alt") || "", w: a.getAttribute("data-width"), h: a.getAttribute("data-height"), label: a.getAttribute("data-label") || "" };
    }
    function slidesFor(item) {
      var link = item.querySelector(".gallery-link");
      var thumb = item.querySelector("img");
      // The card shows a small pre-resized thumbnail; the link carries the full image's own size.
      var slides = [{ href: link.getAttribute("href"), alt: thumb ? thumb.alt : "",
        w: link.getAttribute("data-width") || (thumb ? thumb.getAttribute("width") : null),
        h: link.getAttribute("data-height") || (thumb ? thumb.getAttribute("height") : null), label: "" }];
      Array.prototype.forEach.call(item.querySelectorAll(".gallery-set a"), function (a) { slides.push(slideFrom(a)); });
      return slides;
    }

    var activeItem = null, slides = [], slide = 0, setOnly = false;
    function render() {
      var s = slides[slide];
      var src = s && safeSrc(s.href);
      if (!src) return;
      img.src = src;
      img.alt = s.alt;
      if (s.w && s.h) { img.setAttribute("width", s.w); img.setAttribute("height", s.h); }
      var cap = activeItem.querySelector("figcaption .gallery-meta") || activeItem.querySelector("figcaption");
      caption.textContent = cap ? cap.textContent.replace(/\s+/g, " ").trim() : "";
      var text = slides.length > 1 || setOnly
        ? (slide + 1) + " / " + slides.length
        : (current + 1) + " / " + visibleItems().length;
      count.textContent = s.label ? text + " · " + s.label : text;
    }

    function show(index) {
      var list = visibleItems();
      if (!list.length) return;
      current = (index + list.length) % list.length;
      activeItem = list[current];
      slides = slidesFor(activeItem);
      slide = 0;
      setOnly = false;
      render();
    }

    // Within a multi-photo set, ← / → cycle through its photos; otherwise they move between projects.
    function step(dir) {
      if (!activeItem) return;
      if (slides.length > 1) { slide = (slide + dir + slides.length) % slides.length; render(); }
      else if (!setOnly) show(current + dir);
    }

    grid.addEventListener("click", function (e) {
      var btn = e.target.closest(".before-btn");
      if (btn) {
        var set = document.getElementById(btn.getAttribute("data-before-set"));
        if (!set) return;
        trigger = btn;
        activeItem = btn.closest(".gallery-item");
        slides = Array.prototype.map.call(set.querySelectorAll("a"), slideFrom);
        slide = 0;
        setOnly = true;
        render();
        dialog.showModal();
        return;
      }
      var link = e.target.closest(".gallery-link");
      if (!link) return;
      e.preventDefault();
      trigger = link;
      show(visibleItems().indexOf(link.closest(".gallery-item")));
      dialog.showModal();
    });

    dialog.addEventListener("click", function (e) {
      var action = e.target.closest("[data-lightbox]");
      if (action) {
        var a = action.getAttribute("data-lightbox");
        if (a === "close") dialog.close();
        else step(a === "next" ? 1 : -1);
      } else if (e.target === dialog) {
        dialog.close(); // click on the backdrop
      }
    });

    dialog.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
    });

    // Esc is handled natively by <dialog>; always return focus to the thumbnail.
    dialog.addEventListener("close", function () {
      if (trigger) trigger.focus();
    });
  }
})();
