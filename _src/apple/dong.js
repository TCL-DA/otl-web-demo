/* dong.js — thêm 8 kiểu chuyển động cho bộ OTLM (motion.js của Codex), Claude 24/10/2026.
   Chỉ transform/opacity: trình duyệt chạy trên GPU, luồng chính rảnh → giữ nhịp 120 Hz.
   Nạp ngay sau OTLM.start() trong <head>, trước khi trang dựng xong (lúc đó motion.js mới bắt đầu chạy hiệu ứng). */
(function () {
  "use strict";
  var M = window.OTLM;
  if (!M || !M.FX) return;
  var P = "perspective(900px) ";
  var X = {
    rise3d: function (d) { return [{ opacity: 0, transform: P + "translate3d(0," + d + "px,0) rotateX(12deg)" }, { opacity: 1, transform: "none" }]; },
    swing: function (d) { return [{ opacity: 0, transform: P + "translate3d(0," + d + "px,0) rotateY(-10deg)" }, { opacity: 1, transform: "none" }]; },
    unfold: function () { return [{ opacity: 0, transform: "scaleY(.86)" }, { opacity: 1, transform: "none" }]; },
    rollL: function (d) { return [{ opacity: 0, transform: "translate3d(" + -d + "px,0,0) rotate(-3deg)" }, { opacity: 1, transform: "none" }]; },
    drop: function (d) { return [{ opacity: 0, transform: "translate3d(0," + -d + "px,0) scale(.92)" }, { opacity: 1, transform: "none" }]; },
    zoomOut: function () { return [{ opacity: 0, transform: "scale(.9)" }, { opacity: 1, transform: "none" }]; },
    lift: function (d) { return [{ opacity: 0, transform: "translate3d(0," + d + "px,0) scale(.96)" }, { opacity: 1, transform: "none" }]; },
    skew: function (d) { return [{ opacity: 0, transform: "translate3d(0," + d + "px,0) skewY(3deg)" }, { opacity: 1, transform: "none" }]; }
  };
  Object.keys(X).forEach(function (k) { if (!M.FX[k]) M.FX[k] = X[k]; });
})();
