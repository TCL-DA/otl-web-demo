/* OTL web demo — tương tác riêng của bản nhiều trang (băng chuyền, so sánh, điền sẵn model khi hỏi giá).
   Hiệu ứng xuất hiện, menu điện thoại, thư viện ảnh, biểu mẫu: motion.js (OTLM). */
(function () {
  "use strict";
  function qa(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  /* Băng chuyền: nút ‹ › cuộn đúng một thẻ, tự mờ khi chạm đầu/cuối */
  qa("[data-rail]").forEach(function (box) {
    var rail = box.querySelector(".rail"), prev = box.querySelector("[data-prev]"), next = box.querySelector("[data-next]");
    if (!rail || !prev || !next) return;
    function step() { var c = rail.querySelector(".lc"); return c ? c.getBoundingClientRect().width + 20 : 360; }
    function sync() {
      prev.disabled = rail.scrollLeft < 4;
      next.disabled = rail.scrollLeft + rail.clientWidth > rail.scrollWidth - 4;
    }
    prev.addEventListener("click", function () { rail.scrollBy({ left: -step(), behavior: "smooth" }); });
    next.addEventListener("click", function () { rail.scrollBy({ left: step(), behavior: "smooth" }); });
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
      b.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
      if (b.classList.contains("theme-t")) b.textContent = dark ? "Light mode" : "Dark mode";
    });
  }
  qa("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () { if (window.OTLTheme) { OTLTheme.toggle(); syncTheme(); } });
  });
  if (window.matchMedia) {
    var mq = matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", function () { setTimeout(syncTheme, 0); });
  }
  syncTheme();

  /* Nút chat nổi: mở/đóng bảng WhatsApp · Zalo · Messenger; bấm ra ngoài hoặc Esc thì đóng */
  var cb = document.querySelector(".chat-b"), cp = document.getElementById("chat-p");
  if (cb && cp) {
    var setChat = function (open) {
      cb.setAttribute("aria-expanded", open); cp.hidden = !open;
      if (open && window.OTLM && OTLM.anim) OTLM.anim(cp, OTLM.FX.rise(12), 320, 0, "cubic-bezier(.2,.7,.2,1)");
    };
    cb.addEventListener("click", function (e) { e.stopPropagation(); setChat(cp.hidden); });
    document.addEventListener("click", function (e) { if (!cp.hidden && !cp.contains(e.target)) setChat(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !cp.hidden) { setChat(false); cb.focus(); } });
  }

  /* Video Shorts: chỉ nạp YouTube (bản không cookie) khi khách bấm — trang vẫn nhẹ */
  qa(".short button[data-yt]").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + b.dataset.yt + "?autoplay=1&playsinline=1&rel=0";
      f.title = b.getAttribute("aria-label").replace("Play video: ", "");
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen = true;
      var box = document.createElement("div"); box.className = "yt-box"; box.appendChild(f);
      b.replaceWith(box);
    });
  });

  /* Hỏi giá: quote.html?model=OTL-06 → chọn sẵn model */
  var q = new URLSearchParams(location.search).get("model"), ms = document.getElementById("f-model");
  if (q && ms) qa("option", ms).forEach(function (o) { if (o.value === q) ms.value = q; });
})();
