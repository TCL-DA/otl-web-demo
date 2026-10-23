/* OTL Motion — hiệu ứng chỉ dùng transform/opacity (chạy trên compositor) để giữ ≥60 Hz.
   OTLM.start(cfg) gọi trong <head>: tiêm CSS ẩn trước khi vẽ (không nháy), DOM sẵn sàng thì tách chữ, gắn IntersectionObserver.
   cfg.rules: [selector, fx, opts] — fx: rise|fall|left|right|fade|zoom|pop|tilt|draw|drawY|wipe ; opts.split: 'words'|'chars'. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceQuery = window.matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : null;
  function reduced() { return !!(reduceQuery && reduceQuery.matches); }
  var M = (window.OTLM = { n: 0 });
  var activeAnimations = [];
  var FX = {
    rise: function (d) { return [{ opacity: 0, transform: "translate3d(0," + d + "px,0)" }, { opacity: 1, transform: "none" }]; },
    fall: function (d) { return [{ opacity: 0, transform: "translate3d(0," + -d + "px,0)" }, { opacity: 1, transform: "none" }]; },
    left: function (d) { return [{ opacity: 0, transform: "translate3d(" + d + "px,0,0)" }, { opacity: 1, transform: "none" }]; },
    right: function (d) { return [{ opacity: 0, transform: "translate3d(" + -d + "px,0,0)" }, { opacity: 1, transform: "none" }]; },
    fade: function () { return [{ opacity: 0 }, { opacity: 1 }]; },
    zoom: function () { return [{ opacity: 0, transform: "scale(1.12)" }, { opacity: 1, transform: "none" }]; },
    pop: function () { return [{ opacity: 0, transform: "scale(.8)" }, { opacity: 1, transform: "none" }]; },
    tilt: function (d) { return [{ opacity: 0, transform: "translate3d(0," + d + "px,0) rotate(-4deg)" }, { opacity: 1, transform: "none" }]; },
    draw: function () { return [{ transform: "scaleX(0)" }, { transform: "none" }]; },
    drawY: function () { return [{ transform: "scaleY(0)" }, { transform: "none" }]; },
    mask: function () { return [{ transform: "translate3d(0,112%,0)" }, { transform: "none" }]; },
    char: function () { return [{ opacity: 0, transform: "translate3d(0,.45em,0)" }, { opacity: 1, transform: "none" }]; },
    settle: function () { return [{ transform: "scale(1.16)" }, { transform: "none" }]; }
  };
  M.FX = FX;

  function addCss(t) { var s = document.createElement("style"); s.textContent = t; document.head.appendChild(s); }
  function qa(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  function track(a) {
    activeAnimations.push(a); M.n++;
    function remove() { var i = activeAnimations.indexOf(a); if (i > -1) activeAnimations.splice(i, 1); }
    a.addEventListener("finish", remove, { once: true });
    a.addEventListener("cancel", remove, { once: true });
    return a;
  }

  function anim(el, frames, dur, delay, ease, keep) {
    el.classList.add("m-done");
    if (reduced()) {
      var last = frames[frames.length - 1] || {};
      Object.keys(last).forEach(function (k) { el.style[k] = last[k]; });
      return { cancel: function () {} };
    }
    return track(el.animate(frames, { duration: dur, delay: delay, easing: ease, fill: keep ? "both" : "backwards" }));
  }
  M.anim = anim;

  /* tách chữ, giữ nguyên thẻ con (em, b, br) */
  function split(node, mode) {
    var kids = [];
    (function walk(n) {
      Array.prototype.slice.call(n.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(" ")); return; }
            if (mode === "words") {
              var o = document.createElement("span"); o.className = "m-w";
              var i = document.createElement("span"); i.className = "m-i"; i.textContent = w;
              o.appendChild(i); frag.appendChild(o); kids.push(i);
            } else {
              var wc = document.createElement("span"); wc.className = "m-wc";
              Array.from(w).forEach(function (ch) {
                var s = document.createElement("span"); s.className = "m-c"; s.textContent = ch;
                wc.appendChild(s); kids.push(s);
              });
              frag.appendChild(wc);
            }
          });
          n.replaceChild(frag, c);
        } else if (c.nodeType === 1 && c.tagName !== "BR") walk(c);
      });
    })(node);
    node.setAttribute("aria-label", node.textContent.replace(/\s+/g, " ").trim());
    return kids;
  }

  function counter(el, delay, dur) {
    var src = el.textContent, nums = src.match(/\d+(\.\d+)?/g);
    if (!nums) return;
    var parts = src.split(/\d+(?:\.\d+)?/), t0 = null;
    setTimeout(function () {
      function step(t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3), out = parts[0];
        nums.forEach(function (v, i) {
          var dec = (v.split(".")[1] || "").length;
          out += (parseFloat(v) * e).toFixed(dec) + parts[i + 1];
        });
        el.textContent = out;
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }, delay);
  }

  function wipe(el, o, P, delay) {
    el.classList.add("m-done");
    if (reduced()) return;
    if (getComputedStyle(el).position === "static") el.style.position = "relative";
    el.style.overflow = "hidden";
    var c = document.createElement("i");
    c.className = "m-cover";
    c.style.cssText = "position:absolute;inset:0;z-index:3;pointer-events:none;background:" + (o.bg || P.cover) +
      ";transform-origin:" + (o.from || "right") + " center";
    el.appendChild(c);
    var a = track(c.animate([{ transform: "scaleX(1)" }, { transform: "scaleX(0)" }],
      { duration: o.dur || P.dur, delay: delay, easing: o.ease || P.ease, fill: "both" }));
    a.onfinish = function () { c.remove(); };
    a.oncancel = function () { c.remove(); };
    var img = o.settle === false ? null : el.querySelector("img");   /* ảnh rất lớn: tắt phóng-lắng để đỡ vẽ lại */
    if (img) anim(img, FX.settle(), (o.dur || P.dur) * 1.6, delay, P.ease);
  }

  function play(el, k) {
    var r = el._m, o = r.o, P = M.cfg.preset;
    if (reduced()) {
      el.classList.add("m-done");
      (r.kids || []).forEach(function (c) { c.classList.add("m-done"); c.style.opacity = "1"; c.style.transform = "none"; });
      return;
    }
    var d = o.d != null ? o.d : P.d, dur = o.dur || P.dur, ease = o.ease || P.ease;
    var delay = (o.delay || 0) + k * (o.stagger != null ? o.stagger : P.stagger);
    if (r.kids) {
      el.classList.add("m-split");
      var each = o.each != null ? o.each : P.each;
      r.kids.forEach(function (c, i) { anim(c, FX[o.split === "words" ? "mask" : "char"](d), dur, delay + i * each, ease); });
      return;
    }
    if (r.fx === "wipe") return wipe(el, o, P, delay);
    if (o.origin) el.style.transformOrigin = o.origin;
    anim(el, FX[r.fx](d), dur, delay, ease);
    if (o.count) counter(el, delay, o.cdur || 1500);
  }

  function prep(cfg) {
    var waiting = [];
    function run(list) {
      list.sort(function (a, b) { return a.compareDocumentPosition(b) & 4 ? -1 : 1; });
      list.forEach(function (el, k) {
        io.unobserve(el);
        var i = waiting.indexOf(el); if (i > -1) waiting.splice(i, 1);
        play(el, k);
      });
    }
    var io = new IntersectionObserver(function (ents) {
      run(ents.filter(function (e) { return e.isIntersecting; }).map(function (e) { return e.target; }));
    }, { rootMargin: "0px 0px -5% 0px", threshold: 0 });
    cfg.rules.forEach(function (r) {
      qa(r[0]).forEach(function (el) {
        if (el._m) return;
        var o = r[2] || {};
        el._m = { fx: r[1], o: o, kids: o.split ? split(el, o.split) : null };
        waiting.push(el);
        io.observe(el);
      });
    });
    /* chốt an toàn: chạm đáy trang thì chạy hết phần tử còn chờ đang nằm trong màn hình */
    var t = 0;
    addEventListener("scroll", function () {
      if (t || !waiting.length) return;
      t = setTimeout(function () {
        t = 0;
        if (scrollY + innerHeight < root.scrollHeight - 4) return;
        run(waiting.filter(function (el) { var r = el.getBoundingClientRect(); return r.height && r.top < innerHeight && r.bottom > 0; }));
      }, 120);
    }, { passive: true });
    M.stopPrep = function () { io.disconnect(); waiting.length = 0; };
  }

  /* ---------- tương tác ---------- */
  function setImgs() {
    var I = window.IMGS || {};
    var imgs = qa("img[data-k]");
    imgs.forEach(function (i) { i.decoding = "async"; if (I[i.dataset.k]) i.src = I[i.dataset.k]; });
    /* giải mã sẵn từng ảnh lúc rảnh (mỗi lượt 1 ảnh) để cuộn nhanh không chớp trống */
    var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 60); };
    var k = 0;
    (function next() {
      if (k >= imgs.length) return;
      var im = imgs[k++];
      idle(function () {
        var p = im.decode ? im.decode() : Promise.resolve();
        p.catch(function () {}).then(next);
      }, { timeout: 500 });
    })();
  }
  M.src = function (k) { return (window.IMGS || {})[k] || ""; };

  function menu(P) {
    var b = document.querySelector(".burger"), p = document.querySelector(".mnav");
    if (!b || !p) return;
    var version = 0, panelAnim = null, itemAnims = [], inertState = [];

    function cancelAnimations() {
      if (panelAnim) { panelAnim.cancel(); panelAnim = null; }
      itemAnims.forEach(function (a) { if (a && a.cancel) a.cancel(); });
      itemAnims = [];
    }

    /* Khoá mọi nhánh nền, kể cả khi menu được đặt bên trong header; trả lại đúng trạng thái inert ban đầu. */
    function lockBackground() {
      if (inertState.length) return;
      var node = p;
      while (node && node !== document.body) {
        var parent = node.parentElement;
        if (!parent) break;
        Array.prototype.slice.call(parent.children).forEach(function (el) {
          if (el === node || inertState.some(function (x) { return x.el === el; })) return;
          inertState.push({ el: el, value: !!el.inert, had: el.hasAttribute("inert"), attr: el.getAttribute("inert") });
          el.inert = true;
          el.setAttribute("inert", "");
        });
        node = parent;
      }
    }
    function unlockBackground() {
      inertState.forEach(function (x) {
        x.el.inert = x.value;
        if (x.had) x.el.setAttribute("inert", x.attr || "");
        else x.el.removeAttribute("inert");
      });
      inertState = [];
    }
    function focusable() {
      return qa('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])', p)
        .filter(function (el) { return !el.hidden && !el.closest("[hidden],[inert]"); });
    }
    function set(open) {
      var current = ++version;
      cancelAnimations();
      b.setAttribute("aria-expanded", open);
      root.classList.toggle("m-lock", open);
      if (open) {
        p.hidden = false;
        lockBackground();
        if (!reduced()) {
          panelAnim = anim(p, FX.fade(), 260, 0, P.ease);
          var controls = qa("a,.mnav-x,.theme-t", p);
          var itemStep = controls.length > 1 ? Math.min(18, 150 / (controls.length - 1)) : 0;
          controls.forEach(function (a, i) { itemAnims.push(anim(a, FX.rise(12), 300, 30 + i * itemStep, P.ease)); });
        }
        requestAnimationFrame(function () {
          var close = p.querySelector(".mnav-x");
          if (current === version && b.getAttribute("aria-expanded") === "true" && close) close.focus();
        });
      } else {
        unlockBackground();
        b.focus();
        if (reduced()) p.hidden = true;
        else {
          var closeAnim = track(p.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 200, easing: "ease-in" }));
          panelAnim = closeAnim;
          closeAnim.onfinish = function () {
            if (current === version && b.getAttribute("aria-expanded") === "false") p.hidden = true;
            if (panelAnim === closeAnim) panelAnim = null;
          };
          closeAnim.oncancel = function () {
            if (current === version && reduced() && b.getAttribute("aria-expanded") === "false") p.hidden = true;
            if (panelAnim === closeAnim) panelAnim = null;
          };
        }
      }
    }
    b.addEventListener("click", function () { set(b.getAttribute("aria-expanded") !== "true"); });
    qa("a,.mnav-x", p).forEach(function (a) { a.addEventListener("click", function () { set(false); }); });
    document.addEventListener("keydown", function (e) {
      if (p.hidden || b.getAttribute("aria-expanded") !== "true") return;
      if (e.key === "Escape") { e.preventDefault(); set(false); return; }
      if (e.key !== "Tab") return;
      var items = focusable();
      if (!items.length) { e.preventDefault(); return; }
      var first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      else if (!p.contains(document.activeElement)) { e.preventDefault(); (e.shiftKey ? last : first).focus(); }
    });
  }

  function filters(P) {
    qa("[data-filter-group]").forEach(function (g) {
      var items = qa(g.getAttribute("data-filter-group"));
      qa("button", g).forEach(function (btn) {
        btn.addEventListener("click", function () {
          qa("button", g).forEach(function (x) { x.classList.toggle("on", x === btn); x.setAttribute("aria-pressed", x === btn); });
          var f = btn.dataset.f, k = 0;
          items.forEach(function (it) {
            var show = f === "all" || it.dataset.c === f;
            it.hidden = !show;
            if (show && !reduced()) anim(it, FX[P.filterFx || "rise"](P.d * 0.6), 480, k++ * 45, P.ease);
          });
        });
      });
    });
  }

  function galleries(P) {
    qa(".pg").forEach(function (g) {
      var main = g.querySelector(".pg-main"), img = main.querySelector("img"), buttons = qa(".pg-t button", g);
      var version = 0, activeAnim = null, overlay = null;
      function altOf(t) {
        var label = t.dataset.alt || t.getAttribute("aria-label") || "";
        return label.replace(/^Ảnh\s+\d+:\s*/, "") || img.alt;
      }
      function fit(el, value) {
        el.classList.remove("fit-contain", "fit-cover");
        if (value) el.classList.add("fit-" + value);
      }
      buttons.forEach(function (t) {
        t.setAttribute("aria-pressed", t.classList.contains("on") ? "true" : "false");
        t.addEventListener("click", function () {
          if (t.classList.contains("on") && !overlay) return;
          var current = ++version, src = M.src(t.dataset.k), alt = altOf(t), fitMode = t.dataset.fit || "";
          buttons.forEach(function (x) {
            var on = x === t;
            x.classList.toggle("on", on); x.setAttribute("aria-pressed", on ? "true" : "false");
          });
          if (activeAnim) { activeAnim.cancel(); activeAnim = null; }
          if (overlay) { overlay.remove(); overlay = null; }
          if (reduced()) {
            img.src = src; img.alt = alt; fit(img, fitMode);
            return;
          }
          var nx = img.cloneNode(); nx.removeAttribute("data-k"); nx.src = src; nx.alt = alt; fit(nx, fitMode);
          nx.style.cssText = "position:absolute;inset:0;width:100%;height:100%";
          main.appendChild(nx); overlay = nx;
          activeAnim = track(nx.animate([{ opacity: 0, transform: "scale(1.06)" }, { opacity: 1, transform: "none" }], { duration: 520, easing: P.ease }));
          function commit() {
            if (current !== version) return;
            img.src = src; img.alt = alt; fit(img, fitMode);
            nx.remove(); overlay = null; activeAnim = null;
          }
          activeAnim.onfinish = commit;
          activeAnim.oncancel = function () { if (reduced()) commit(); };
        });
      });
    });
  }

  function forms(P) {
    var errorNo = 0;
    function clearError(i) {
      i.classList.remove("m-bad"); i.removeAttribute("aria-invalid");
      if (!i._mError) return;
      i._mError.node.remove();
      if (i._mError.describedby === null) i.removeAttribute("aria-describedby");
      else i.setAttribute("aria-describedby", i._mError.describedby);
      if (i._mError.errormessage === null) i.removeAttribute("aria-errormessage");
      else i.setAttribute("aria-errormessage", i._mError.errormessage);
      delete i._mError;
    }
    function fieldName(i) {
      var label = i.id && qa("label").filter(function (x) { return x.htmlFor === i.id; })[0];
      if (!label) label = i.closest("label");
      return label ? label.textContent.replace(/\s*\*\s*$/, "").trim() : "trường này";
    }
    function messageFor(i) {
      if (i.validity && i.validity.valueMissing) return "Vui lòng nhập " + fieldName(i) + ".";
      if (i.type === "email" && i.validity && i.validity.typeMismatch) return "Vui lòng nhập địa chỉ email hợp lệ.";
      return "Vui lòng kiểm tra thông tin này.";
    }
    function showError(i) {
      clearError(i);
      var msg = document.createElement("span"), id = "otl-form-error-" + (++errorNo);
      msg.id = id; msg.className = "m-form-error"; msg.textContent = messageFor(i);
      i.insertAdjacentElement("afterend", msg);
      i._mError = {
        node: msg,
        describedby: i.getAttribute("aria-describedby"),
        errormessage: i.getAttribute("aria-errormessage")
      };
      var described = (i._mError.describedby || "").split(/\s+/).filter(Boolean);
      described.push(id);
      i.setAttribute("aria-describedby", described.join(" "));
      i.setAttribute("aria-errormessage", id);
      i.classList.add("m-bad"); i.setAttribute("aria-invalid", "true");
    }
    qa("form[data-demo]").forEach(function (f) {
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        var priorStatus = f.querySelector(".m-form-status");
        if (priorStatus) priorStatus.remove();
        qa("input, textarea, select", f).forEach(clearError);
        /* Kiểm cả định dạng email và ô trống; novalidate để tự hiển thị lỗi đồng nhất. */
        var bad = qa("input, textarea, select", f).filter(function (i) {
          return (i.required && !i.value.trim()) || !i.validity.valid;
        });
        if (bad.length) {
          bad.forEach(function (i) {
            showError(i);
            if (!reduced()) {
              track(i.animate([{ transform: "translateX(0)" }, { transform: "translateX(-8px)" }, { transform: "translateX(7px)" }, { transform: "translateX(-4px)" }, { transform: "translateX(0)" }], { duration: 420, easing: "ease-out" }));
            }
          });
          bad[0].focus();
          return;
        }
        var b = f.querySelector("button[type=submit]");
        var ok = f.dataset.ok || "Bản demo — thông tin chưa được gửi.";
        b.textContent = "Thông tin hợp lệ";
        var status = document.createElement("p");
        status.className = "m-form-status"; status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite"); status.textContent = ok;
        b.insertAdjacentElement("afterend", status);
        anim(b, FX.pop(), 520, 0, P.ease);
      });
      qa("input, textarea, select", f).forEach(function (i) {
        i.addEventListener("input", function () { clearError(i); });
        i.addEventListener("change", function () { clearError(i); });
      });
    });
  }

  function scrollFx(cfg) {
    var bar = cfg.progress && document.querySelector(cfg.progress);
    var top = document.querySelector(".totop");
    var px = (cfg.parallax || []).reduce(function (acc, p) {
      return acc.concat(qa(p[0]).map(function (el) { return { el: el, f: p[1], s: p[2] || 1 }; }));
    }, []);
    var H = 1, ticking = false;
    function measure() { H = Math.max(1, root.scrollHeight - innerHeight); }
    function frame() {
      ticking = false;
      var y = scrollY, vh = innerHeight;
      if (bar) bar.style.transform = "scaleX(" + (y / H).toFixed(4) + ")";
      if (top) top.classList.toggle("show", y > vh * 1.2);
      if (reduced()) { px.forEach(function (p) { p.el.style.transform = ""; }); return; }
      var rects = px.map(function (p) { return p.el.parentElement.getBoundingClientRect(); });
      px.forEach(function (p, i) {
        var r = rects[i];
        if (r.bottom < -80 || r.top > vh + 80) return;
        var off = (r.top + r.height / 2 - vh / 2) * p.f;
        p.el.style.transform = "translate3d(0," + off.toFixed(1) + "px,0) scale(" + p.s + ")";
      });
    }
    function req() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
    addEventListener("scroll", req, { passive: true });
    addEventListener("resize", function () { measure(); req(); });
    measure(); frame();
    if (top) top.addEventListener("click", function () { scrollTo({ top: 0, behavior: reduced() ? "auto" : "smooth" }); });
  }

  function tilt(cfg) {
    if (!cfg.tilt || !matchMedia("(hover:hover) and (pointer:fine)").matches || reduced()) return;
    qa(cfg.tilt).forEach(function (c) {
      var raf = 0, rx = 0, ry = 0;
      c.addEventListener("pointermove", function (e) {
        if (reduced()) { c.style.transform = ""; return; }
        var r = c.getBoundingClientRect();
        ry = ((e.clientX - r.left) / r.width - 0.5) * 7; rx = -((e.clientY - r.top) / r.height - 0.5) * 7;
        if (!raf) raf = requestAnimationFrame(function () { raf = 0; c.style.transform = "perspective(900px) rotateX(" + rx.toFixed(2) + "deg) rotateY(" + ry.toFixed(2) + "deg)"; });
      });
      c.addEventListener("pointerleave", function () { c.style.transform = ""; });
    });
  }

  M.start = function (cfg) {
    M.cfg = cfg;
    if (reduceQuery && !M.reduceBound) {
      M.reduceBound = true;
      reduceQuery.addEventListener("change", function (e) {
        if (!e.matches) return;
        activeAnimations.slice().forEach(function (a) { try { a.cancel(); } catch (ignore) {} });
        if (M.stopPrep) M.stopPrep();
        root.classList.remove("m-on");
        qa(".m-cover").forEach(function (c) { c.remove(); });
        (cfg.parallax || []).forEach(function (p) { qa(p[0]).forEach(function (el) { el.style.transform = ""; }); });
        cfg.rules.forEach(function (r) {
          qa(r[0]).forEach(function (el) {
            el.classList.add("m-done");
            if (el._m && el._m.kids) el._m.kids.forEach(function (c) { c.classList.add("m-done"); c.style.opacity = "1"; c.style.transform = "none"; });
            delete el._m;
          });
        });
      });
    }
    var ready = function () {
      setImgs(); menu(cfg.preset); filters(cfg.preset); galleries(cfg.preset); forms(cfg.preset); scrollFx(cfg); tilt(cfg);
      if (!reduced()) prep(cfg);
      if (cfg.after) cfg.after(M);
    };
    if (!reduced()) {
      root.classList.add("m-on");
      var css = "";
      cfg.rules.forEach(function (r) {
        var o = r[2] || {}, s = ".m-on " + r[0];
        if (o.split) css += s + ":not(.m-split){opacity:0}";
        else if (r[1] === "draw") css += s + ":not(.m-done){transform:scaleX(0)}";
        else if (r[1] === "drawY") css += s + ":not(.m-done){transform:scaleY(0)}";
        else css += s + ":not(.m-done){opacity:0}";
      });
      css += ".m-on .m-i:not(.m-done),.m-on .m-c:not(.m-done){opacity:0}";
      addCss(css);
    }
    addCss(".m-w{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.14em;margin-bottom:-.14em}" +
      ".m-i,.m-c{display:inline-block}.m-wc{display:inline-block;white-space:nowrap}.m-lock,.m-lock body{overflow:hidden}" +
      ".m-bad{outline:2px solid #d8262c!important;outline-offset:-1px}.m-form-error{display:block;color:var(--red-ink,#b91c1c);font-size:.82rem;margin-top:.38rem}.m-form-status{margin-top:.75rem}");
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready); else ready();
  };
})();
