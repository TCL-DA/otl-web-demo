/* OTL web demo — tương tác riêng của bản nhiều trang (băng chuyền, so sánh, điền sẵn model khi hỏi giá).
   Hiệu ứng xuất hiện, menu điện thoại, thư viện ảnh, biểu mẫu: motion.js (OTLM). */
(function () {
  "use strict";
  function qa(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  var reduceQuery = window.matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : null;
  function reduced() { return !!(reduceQuery && reduceQuery.matches); }
  if (reduceQuery) reduceQuery.addEventListener("change", function (e) {
    if (e.matches) qa("model-viewer").forEach(function (mv) { mv.removeAttribute("auto-rotate"); });
  });

  /* Băng chuyền: nút ‹ › cuộn đúng một thẻ, tự mờ khi chạm đầu/cuối */
  qa("[data-rail]").forEach(function (box) {
    var rail = box.querySelector(".rail"), prev = box.querySelector("[data-prev]"), next = box.querySelector("[data-next]");
    if (!rail || !prev || !next) return;
    function step() { var c = rail.querySelector(".lc"); return c ? c.getBoundingClientRect().width + 20 : 360; }
    function sync() {
      prev.disabled = rail.scrollLeft < 4;
      next.disabled = rail.scrollLeft + rail.clientWidth > rail.scrollWidth - 4;
    }
    prev.addEventListener("click", function () { rail.scrollBy({ left: -step(), behavior: reduced() ? "auto" : "smooth" }); });
    next.addEventListener("click", function () { rail.scrollBy({ left: step(), behavior: reduced() ? "auto" : "smooth" }); });
    rail.addEventListener("scroll", function () { requestAnimationFrame(sync); }, { passive: true });
    addEventListener("resize", sync);
    sync();
  });

  /* So sánh: mỗi cột một ô chọn model, đổi là thay ảnh + thông số */
  var D = window.CMP;
  if (D) {
    qa(".cmp-col").forEach(function (col) {
      var sel = col.querySelector("select");
      function fill() {
        var m = D[sel.value]; if (!m) return;
        col.querySelector("[data-f=img]").innerHTML = m.img;
        col.querySelector("[data-f=name]").textContent = m.name;
        col.querySelector("[data-f=tag]").textContent = m.tagline;
        col.querySelector("[data-f=more]").href = m.url;
        col.querySelector("[data-f=quote]").href = "quote.html?model=" + encodeURIComponent(m.name);
        qa("[data-k]", col).forEach(function (dd) { dd.textContent = m.spec[dd.dataset.k] || "—"; });
        if (window.OTLM && OTLM.anim) {
          OTLM.anim(col.querySelector("[data-f=img]"), OTLM.FX.rise(16), 520, 0, "cubic-bezier(.2,.7,.2,1)");
        }
      }
      sel.addEventListener("change", fill);
      fill();
    });
  }

  /* Nút đổi sáng/tối: lưu lựa chọn (OTLTheme trong <head>), nhãn nút theo giao diện đang dùng */
  function syncTheme() {
    var dark = document.documentElement.dataset.theme === "dark";
    qa("[data-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-label", dark ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối");
      if (b.classList.contains("theme-t")) b.textContent = dark ? "Giao diện sáng" : "Giao diện tối";
    });
  }
  qa("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () { if (window.OTLTheme) { OTLTheme.toggle(); syncTheme(); } });
  });
  if (!document.documentElement.dataset.theme) document.documentElement.dataset.theme = "dark";
  syncTheme();

  /* Nút chat nổi: mở/đóng bảng WhatsApp · Zalo · Messenger; bấm ra ngoài hoặc Esc thì đóng */
  var cb = document.querySelector(".chat-b"), cp = document.getElementById("chat-p"), zq = cp && cp.querySelector(".zqr");
  if (cb && cp) {
    var setChat = function (open) {
      cb.setAttribute("aria-expanded", open); cp.hidden = !open;
      if (!open && zq) zq.hidden = true;
      if (open && window.OTLM && OTLM.anim) OTLM.anim(cp, OTLM.FX.rise(12), 320, 0, "cubic-bezier(.2,.7,.2,1)");
    };
    cb.addEventListener("click", function (e) { e.stopPropagation(); setChat(cp.hidden); });
    document.addEventListener("click", function (e) { if (!cp.hidden && !cp.contains(e.target)) setChat(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !cp.hidden) { setChat(false); cb.focus(); } });
    /* Zalo trên MÁY TÍNH: link số cá nhân bắt đăng nhập → hiện mã QR để quét bằng điện thoại; điện thoại thì mở thẳng app */
    qa("[data-zalo]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (!zq || !matchMedia("(hover: hover) and (pointer: fine)").matches) return;
        e.preventDefault(); e.stopPropagation();
        if (cp.hidden) setChat(true);
        zq.hidden = false;
        if (window.OTLM && OTLM.anim) OTLM.anim(zq, OTLM.FX.rise(10), 300, 0, "cubic-bezier(.2,.7,.2,1)");
      });
    });
  }

  /* Video Shorts: chỉ nạp YouTube (bản không cookie) khi khách bấm — trang vẫn nhẹ */
  qa(".short button[data-yt]").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + b.dataset.yt + "?autoplay=1&playsinline=1&rel=0";
      f.title = b.getAttribute("aria-label").replace("Xem video: ", "");
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen = true;
      var box = document.createElement("div"); box.className = "yt-box"; box.appendChild(f);
      b.replaceWith(box);
    });
  });

  /* Nút Copy: chép số điện thoại / email / địa chỉ; trình duyệt cũ không có Clipboard API thì dùng ô ẩn + execCommand */
  function copyText(s) {
    if (navigator.clipboard && window.isSecureContext !== false) {
      return navigator.clipboard.writeText(s).catch(function () { return fallback(s); });
    }
    return fallback(s);
  }
  function fallback(s) {
    return new Promise(function (ok, fail) {
      var ta = document.createElement("textarea"); ta.value = s; ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:0;left:0;opacity:0"; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy") ? ok() : fail(); } catch (e) { fail(e); }
      ta.remove();
    });
  }
  qa(".copy").forEach(function (b) {
    var lab = b.querySelector("span"), t0 = lab.textContent, timer = 0;
    b.addEventListener("click", function (e) {
      e.preventDefault(); e.stopPropagation();
      copyText(b.dataset.copy).then(function () {
        clearTimeout(timer); b.classList.add("ok"); lab.textContent = "Đã chép";
        if (window.OTLM && OTLM.anim) OTLM.anim(b, OTLM.FX.pop(), 260, 0, "cubic-bezier(.2,.7,.2,1)");
        timer = setTimeout(function () { b.classList.remove("ok"); lab.textContent = t0; }, 1800);
      }, function () { lab.textContent = "Nhấn Ctrl+C"; });
    });
  });

  /* Bản xem trước yêu cầu được tạo động trong motion.js; chỉ sao chép khi khách bấm nút. */
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-request-copy]");
    if (!b) return;
    e.preventDefault();
    var status = b.parentElement && b.parentElement.querySelector(".request-copy-status");
    copyText(b._copyText || "").then(function () {
      if (status) status.textContent = "Đã sao chép nội dung yêu cầu.";
      if (window.OTLM && OTLM.anim) OTLM.anim(b, OTLM.FX.pop(), 260, 0, "cubic-bezier(.2,.7,.2,1)");
    }, function () {
      if (status) status.textContent = "Không thể sao chép tự động. Vui lòng thử lại.";
    });
  });

  /* Bộ chọn máy: tải trọng mẻ quyết định model; loại hình sử dụng chỉ giúp diễn giải kết quả. */
  var finderData = Array.isArray(window.ROASTER_FINDER) ? window.ROASTER_FINDER : [];
  qa("[data-finder]").forEach(function (box) {
    var form = box.querySelector("[data-finder-form]");
    var batch = box.querySelector("#finder-batch"), use = box.querySelector("#finder-use"), result = box.querySelector("#finder-result");
    if (!form || !batch || !use || !result) return;
    var image = result.querySelector("[data-finder-image]"), title = result.querySelector("[data-finder-title]");
    var copy = result.querySelector("[data-finder-copy]"), spec = result.querySelector("[data-finder-spec]");
    var more = result.querySelector("[data-finder-more]"), quote = result.querySelector("[data-finder-quote]");
    var status = result.querySelector("[data-finder-status]");
    if (!image || !title || !copy || !spec || !more || !quote || !status) return;
    if (!status.id) status.id = "finder-status";
    var originalDescribedby = batch.getAttribute("aria-describedby");
    var useNames = { cafe: "quán cà phê", roastery: "xưởng rang", industrial: "vận hành công nghiệp" };
    var number = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 3 });

    function clearResult() {
      result.hidden = false; batch.removeAttribute("aria-invalid");
      image.hidden = true; more.hidden = true; quote.hidden = true;
      title.textContent = "Tìm cỡ máy của bạn";
      copy.textContent = "Nhấn Tìm máy phù hợp để cập nhật gợi ý theo nhu cầu vừa nhập.";
      spec.textContent = "";
      if (originalDescribedby === null) batch.removeAttribute("aria-describedby");
      else batch.setAttribute("aria-describedby", originalDescribedby);
      status.textContent = "";
    }
    function invalid() {
      result.hidden = false; image.hidden = true; more.hidden = true; quote.hidden = true;
      title.textContent = "Kiểm tra khối lượng mẻ"; copy.textContent = ""; spec.textContent = "";
      status.textContent = "Vui lòng nhập khối lượng mẻ từ 0,5 đến 500 kg.";
      batch.setAttribute("aria-invalid", "true");
      var ids = (originalDescribedby || "").split(/\s+/).filter(Boolean);
      if (ids.indexOf(status.id) < 0) ids.push(status.id);
      batch.setAttribute("aria-describedby", ids.join(" ")); batch.focus();
    }
    function showLinks() { more.hidden = false; quote.hidden = false; }
    function custom(requested, useName) {
      image.hidden = true;
      title.textContent = "Cấu hình rang công nghiệp theo yêu cầu";
      copy.textContent = "Mẻ " + number.format(requested) + " kg cho " + useName + " cần cấu hình hệ thống riêng từ OTL.";
      spec.textContent = "Dải yêu cầu: trên 120 đến 500 kg mỗi mẻ";
      more.href = "solutions.html"; more.textContent = "Xem giải pháp công nghiệp";
      var customQuote = window.ROASTER_CUSTOM_QUOTE;
      quote.href = typeof customQuote === "string" && customQuote ? customQuote : "quote.html?model=" + encodeURIComponent("Cấu hình riêng " + requested + " kg");
      quote.textContent = "Yêu cầu cấu hình riêng"; showLinks();
      status.textContent = "Đã chuyển sang yêu cầu cấu hình riêng để OTL tư vấn.";
    }
    function recommend(model, requested, useName) {
      image.hidden = !model.img;
      if (model.img) { image.src = model.img; image.alt = model.name + " — máy rang cà phê OTL"; }
      title.textContent = model.name;
      copy.textContent = "Mẻ " + number.format(requested) + " kg cho " + useName + " nằm trong dải vận hành của " + model.name + ".";
      spec.textContent = "Dải mẻ: " + number.format(model.batchMin) + "–" + number.format(model.batchMax) + " kg" + (model.output ? " • Sản lượng: " + model.output : "");
      more.href = model.url || "roasters.html"; more.textContent = "Xem " + model.name;
      quote.href = model.quote || ("quote.html?model=" + encodeURIComponent(model.name)); quote.textContent = "Nhận báo giá " + model.name;
      showLinks(); status.textContent = "Đã tìm thấy model có dải mẻ phù hợp.";
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      /* Nhận cả dấu phẩy tiếng Việt và dấu chấm, không hiểu nhầm ký hiệu khác thành số. */
      var raw = batch.value.trim(), requested = Number(raw.replace(",", ".")), useName = useNames[use.value] || "nhu cầu đã chọn";
      if (!/^(?:\d+(?:[.,]\d*)?|[.,]\d+)$/.test(raw) || !Number.isFinite(requested) || requested < 0.5 || requested > 500) { invalid(); return; }
      batch.removeAttribute("aria-invalid"); result.hidden = false;
      if (requested > 120) custom(requested, useName);
      else {
        var matches = finderData.filter(function (m) {
          return Number(m.batchMin) <= requested && Number(m.batchMax) >= requested;
        }).sort(function (a, b) { return Number(a.batchMax) - Number(b.batchMax) || Number(a.batchMin) - Number(b.batchMin); });
        if (matches.length) recommend(matches[0], requested, useName);
        else custom(requested, useName);
      }
      if (window.OTLM && OTLM.anim) OTLM.anim(result, OTLM.FX.rise(14), 360, 0, "cubic-bezier(.2,.7,.2,1)");
      result.focus({ preventScroll: true });
      result.scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "nearest" });
    });
    batch.addEventListener("input", clearResult);
    use.addEventListener("change", clearResult);
  });

  /* Xem 3D: dùng chung một lần tải model-viewer; lỗi mạng hoặc treo đều trả nút về trạng thái thử lại. */
  var modelViewerPromise = null, modelViewerScript = null, modelViewerLoadNo = 0;
  function loadModelViewer() {
    if (customElements.get("model-viewer")) return Promise.resolve();
    if (modelViewerPromise) return modelViewerPromise;
    modelViewerPromise = new Promise(function (resolve, reject) {
      var done = false;
      if (modelViewerScript) modelViewerScript.remove();
      var s = document.createElement("script"), timer;
      modelViewerScript = s;
      s.type = "module"; s.dataset.otlModelViewer = "";
      s.src = "https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js?otl-retry=" + (++modelViewerLoadNo);
      function finish(err) {
        if (done) return;
        done = true; clearTimeout(timer); s.onload = s.onerror = null;
        if (err) { s.remove(); modelViewerScript = null; reject(err); }
        else resolve();
      }
      s.onerror = function () { finish(new Error("Không tải được thư viện 3D.")); };
      s.onload = function () {
        customElements.whenDefined("model-viewer").then(function () { finish(); }, function () { finish(new Error("Không khởi tạo được trình xem 3D.")); });
      };
      timer = setTimeout(function () { finish(new Error("Hết thời gian tải thư viện 3D.")); }, 12000);
      document.head.appendChild(s);
    }).catch(function (err) { modelViewerPromise = null; throw err; });
    return modelViewerPromise;
  }
  qa(".v3d").forEach(function (box) {
    var b = box.querySelector("button"), attempt = 0;
    var status = document.createElement("p");
    status.className = "v3d-status small"; status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite"); status.hidden = true;
    box.appendChild(status);
    function label(text) {
      if (b.firstChild && b.firstChild.nodeType === 3) b.firstChild.nodeValue = text + " ";
      else b.insertBefore(document.createTextNode(text + " "), b.firstChild);
    }
    function clearViewer() { qa("model-viewer", box).forEach(function (mv) { mv.remove(); }); box.classList.remove("on"); }
    function fail(current, message) {
      if (current !== attempt) return;
      clearViewer(); b.disabled = false; label("Thử lại 3D");
      status.textContent = message || "Không thể tải mô hình 3D. Vui lòng thử lại."; status.hidden = false;
    }
    b.addEventListener("click", function () {
      var current = ++attempt, modelTimer;
      clearViewer(); status.hidden = true; status.textContent = "Đang tải mô hình 3D…";
      b.disabled = true; label("Đang tải 3D…");
      loadModelViewer().then(function () {
        if (current !== attempt) return;
        var mv = document.createElement("model-viewer");
        mv.setAttribute("src", box.dataset.glb);
        mv.setAttribute("alt", box.dataset.name + " — mô hình 3D");
        mv.setAttribute("camera-controls", "");
        if (!reduced()) mv.setAttribute("auto-rotate", "");
        mv.setAttribute("touch-action", "pan-y");
        mv.setAttribute("environment-image", "neutral");
        mv.setAttribute("camera-orbit", "35deg 75deg auto");
        mv.addEventListener("load", function () {
          if (current !== attempt) return;
          clearTimeout(modelTimer); box.classList.add("on");
          var poster = box.querySelector("img"); if (poster) poster.remove();
          status.remove(); b.remove();
        });
        mv.addEventListener("error", function () { clearTimeout(modelTimer); fail(current, "Không thể tải mô hình 3D. Vui lòng thử lại."); });
        box.appendChild(mv);
        modelTimer = setTimeout(function () { fail(current, "Hết thời gian tải mô hình 3D. Vui lòng thử lại."); }, 30000);
      }).catch(function () { fail(current, "Không thể tải trình xem 3D. Vui lòng kiểm tra kết nối và thử lại."); });
    });
  });

  /* Hỏi giá: quote.html?model=OTL-06 → chọn sẵn model */
  var q = new URLSearchParams(location.search).get("model"), ms = document.getElementById("f-model");
  if (q && ms) qa("option", ms).forEach(function (o) { if (o.value === q) ms.value = q; });
})();
