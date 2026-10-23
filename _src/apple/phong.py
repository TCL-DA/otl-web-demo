# phong.py — 8 phong cách Apple Thành gửi 24/10/2026, mỗi phong cách gán cho một nhóm trang (Claude).
# Chạy SAU khi build xong: chỉ gắn lớp .stN lên <body>, đổi vài lớp section, chèn viên giá; giao diện nằm ở phong.css.
# Không sửa build.py / site.css của Codex. Trang chủ và trang báo giá giữ nguyên giao diện chung.
#   1 white gallery (máy gập)  → máy rang nhỏ OTL-1.2/03/06
#   2 + 3 bảo tàng ánh sáng ngày (Thành gửi 2 bản giống hệt) → trang danh mục; bản 3 thêm dải xanh băng mở đầu
#   4 tủ kính trắng (iPad Air) → OTL-12/15
#   5 tủ kính sương sớm       → thiết bị phụ trợ và 8 trang cỡ OD/AB
#   6 bê tông điện ảnh        → Công nghệ, Kiến thức, bài viết, Cửa hàng, Về OTL
#   7 tủ kính đen obsidian    → OTL-30/60 (tối → tối → sáng)
#   8 nhà hát đen             → OTL-120
# Luật OTL vẫn giữ: không gradient, không bóng, không kính mờ → thanh giá "kính" của phong cách 8 dùng nền đặc.

PHONG = {}
for _n, _ds in {
    1: ["otl-1-2", "otl-03", "otl-06"],
    2: ["roasters", "equipment", "compare"],
    3: ["solutions", "support"],
    4: ["otl-12", "otl-15"],
    5: ["destoner", "afterburner", "cyclone", "silo", "od-05", "od-15", "od-30", "od-60", "ab-15", "ab-30", "ab-60", "ab-120"],
    6: ["cong-nghe", "kien-thuc", "cua-hang", "about"],
    7: ["otl-30", "otl-60"],
    8: ["otl-120"],
}.items():
    for _d in _ds:
        PHONG[_d] = _n

# Mở sáng chỉ khi khách chưa tự chọn VÀ máy khách không để chế độ tối (máy tối thì web vẫn tự tối).
_SANG = ("<script>(function(){var s=null;try{s=localStorage.getItem('otl-theme')}catch(e){}"
         "if(!s&&!(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches))"
         "document.documentElement.dataset.theme='light'})()</script>")

def _mo_sang(h):
    i = h.find("window.OTLTheme=")
    j = h.find("</script>", i) + len("</script>") if i >= 0 else -1
    return h[:j] + _SANG + h[j:] if j > 0 else h

def _phong_so(stem):
    if stem in PHONG:
        return PHONG[stem]
    return 6 if stem.startswith("kt-") else 0

def _vien_gia(h):
    """Viên giá nổi: tên máy + năng suất + nút báo giá, dính đáy màn hình khi cuộn trang."""
    nm = _re.search(r'<span class="nm">([^<]+)</span>', h)
    facts = _re.search(r'<p class="hero-facts">([^<]+)</p>', h)
    href = _re.search(r'<a class="btn btn-f sm" href="([^"]+)"', h)
    if not (nm and href):
        return h
    span = f'<span>{facts.group(1)}</span>' if facts else ""
    pill = (f'<div class="g-buy" role="complementary" aria-label="Báo giá {nm.group(1)}"><b>{nm.group(1)}</b>{span}'
            f'<a class="btn btn-f sm" href="{href.group(1)}">Nhận báo giá</a></div>')
    return h.replace('<section class="sec bg-c cta-band">', pill + '<section class="sec bg-c cta-band">', 1)

def _toi(h, *marks):
    for m in marks:
        h = h.replace(m, m.replace('class="sec ', 'class="sec dk ', 1), 1)
    return h

def _ap_phong(h, n):
    m = _re.search(r'<body(?: class="([^"]*)")?>', h)
    if m:
        cls = (m.group(1) + " " if m.group(1) else "") + f"st st{n}"
        h = h[:m.start()] + f'<body class="{cls}">' + h[m.end():]
    if n <= 6:   # phong cách nền sáng: khách mới vào thấy bản sáng; ai đã chọn tối hoặc máy để tối thì vẫn tối
        h = _mo_sang(h)
    if n in (1, 4, 5):   # sân khấu sản phẩm trắng
        h = h.replace('class="hero product-hero dk ', 'class="hero product-hero ', 1)
    if n in (1, 8):
        h = _vien_gia(h)
    if n == 7:   # màn 1 và 2 tối, phần chi tiết sáng
        h = _toi(h, '<section class="sec bg-w" id="highlights">')
        h = _re.sub(r'(id="highlights">.*?</section>\s*<section class="sec )(bg-c">)', r"\1dk \2", h, count=1, flags=_re.S)
    if n == 8:   # nhà hát đen, xen dải sáng ở sơ đồ và thông số
        h = h.replace('<div class="mini">', '<div class="mini dk">', 1)
        h = _toi(h, '<section class="sec bg-w" id="highlights">', '<section class="sec bg-c" id="gallery">',
                 '<section class="sec bg-c cta-band">')
        h = _re.sub(r'(id="highlights">.*?</section>\s*<section class="sec )(bg-c">)', r"\1dk \2", h, count=1, flags=_re.S)
    return h

# ----------------------------------------------------------------- 8 phong cách xoay theo TỪNG MỤC (24/10, lần 2)
# Mục đầu trang giữ phong cách của trang; các mục sau xoay vòng trắng → sương → tối → trắng… để trang nào cũng đủ nhiều
# phong cách. Mục có biểu mẫu / bài viết dài không bị đổi sang tối; không để hai mục tối liền nhau.
_XOAY = [1, 5, 7, 4, 6, 3, 8, 2]
_TOI = {7, 8}
_KHONG_TOI = _re.compile(r"<form|<input|<select|<textarea|g-art-b|data-request")

def _xoay(h, n):
    i0, i1 = h.find("<main"), h.find("</main>")
    if i0 < 0 or i1 < 0:
        return h, set()
    body = h[i0:i1]
    secs = list(_re.finditer(r'<section class="([^"]*)"(.*?)</section>', body, flags=_re.S))
    k = (_XOAY.index(n) + 1) if n in _XOAY else 0
    truoc_toi, dung, out, last = False, set(), [], 0
    for idx, m in enumerate(secs):
        cls, noi = m.group(1), m.group(2)
        if (idx == 0 and n) or "hero" in cls.split():
            truoc_toi = "dk" in cls.split()
            continue
        if "dk" in cls.split():      # dải tối có sẵn (Codex hoặc phong cách 7/8) → mang chất tối 7 hoặc 8
            s = 8 if n == 8 else 7
        else:
            s = None
            for _ in range(len(_XOAY)):
                c = _XOAY[k % len(_XOAY)]; k += 1
                if c in _TOI and (truoc_toi or _KHONG_TOI.search(noi)):
                    continue
                s = c
                break
        them = f" ss ss{s}" + (" dk" if s in _TOI and "dk" not in cls.split() else "")
        out.append(body[last:m.start(1)] + cls + them)
        last = m.end(1)
        dung.add(s)
        truoc_toi = s in _TOI
    out.append(body[last:])
    return h[:i0] + "".join(out) + h[i1:], dung

# ----------------------------------------------------------------- hiệu ứng: nối thêm luật vào bộ motion.js của Codex
# Chỉ transform/opacity (chạy trên GPU, giữ 120 Hz). Không gắn vào dải cuộn ngang (.rail, .shorts, .strip, .pg-t):
# thẻ nằm ngoài màn hình theo chiều ngang không bao giờ "thấy" → sẽ kẹt ẩn.
MOTION["rules"] = [
    [".product-hero .sub", "rise", {"split": "words", "each": 34, "dur": 900}],
    [".cta-band .h-xl", "rise", {"split": "words", "each": 40}],
    [".g-art-h .h-xl", "rise", {"split": "words", "each": 30}],
    [".g-var", "swing", {"d": 40, "dur": 1000, "stagger": 140}],   # đứng trước .rv để thẻ phiên bản có kiểu riêng
] + MOTION["rules"] + [
    [".g-var-im", "lift", {"d": 30, "dur": 1100, "delay": 120}],
    [".g-draw", "unfold", {"dur": 900, "origin": "top center"}],
    [".g-ticks li", "rollL", {"d": 28, "stagger": 60}],
    [".g-grid3>*", "rise3d", {"d": 34, "stagger": 90}],
    [".g-grid4>*", "rise3d", {"d": 30, "stagger": 70}],
    [".g-photos .g-ph", "zoomOut", {"stagger": 45, "dur": 900}],
    [".g-sizes .g-pill", "drop", {"d": 14, "stagger": 40, "dur": 600}],
    [".specs dt", "left", {"d": -18, "stagger": 22, "dur": 650}],
    [".specs dd", "left", {"d": 18, "stagger": 22, "dur": 650}],
    [".know li", "rollL", {"d": 22, "stagger": 50}],
    [".g-art-b>p", "rise", {"d": 14, "dur": 650, "stagger": 40}],
    [".g-art-b>:is(h2,h3,ul)", "skew", {"d": 18, "dur": 750}],
    [".g-art-im", "zoomOut", {"dur": 1000}],
    [".g-art-cover", "unfold", {"dur": 1100, "origin": "top center"}],
    [".duo>*", "rise3d", {"d": 30, "stagger": 110}],
    [".foot .cols>div", "rise", {"d": 18, "stagger": 70, "dur": 700}],
    [".foot .note", "fade", {"dur": 900}],
    [".g-buy", "pop", {"dur": 700}],
]   # mỗi luật 1 bộ chọn, KHÔNG dùng dấu phẩy: motion.js ghép ".m-on " vào đầu cả chuỗi

# cuối mỗi bài: 3 bài khác + dải mời tư vấn (nội dung có thật, để bài cũng có nhiều mục mang phong cách)
_page_bai_phong = page_bai
def page_bai(b):
    h = _page_bai_phong(b)
    i = BAI.index(b)
    khac = [BAI[(i + j) % len(BAI)] for j in (1, 2, 3)]
    them = (f'<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Bài viết khác.</h2>'
            f'<div class="g-grid3">{"".join(_bai_card(x) for x in khac)}</div>'
            f'<p class="rv" style="margin-top:30px"><a class="lnk" href="kien-thuc.html">Tất cả bài viết</a></p></div></section>'
            f'<section class="sec bg-w cta-band"><div class="wrap"><h2 class="h-xl rv">Cần tư vấn chọn máy rang?</h2>'
            f'<p class="lead measure rv" style="margin-top:14px">Kể cho OTL về loại hạt, sản lượng và mặt bằng xưởng, chúng tôi đề xuất cấu hình phù hợp.</p>'
            f'<div class="btns rv"><a class="btn btn-f" href="quote.html">Nhận báo giá</a><a class="btn btn-o" href="support.html">Liên hệ hỗ trợ</a></div>'
            f'</div></section>')
    return h.replace("</main>", them + "</main>", 1)

_main_phong = main
def main():
    import hashlib
    _main_phong()
    v = {}
    for f in ("phong.css", "dong.js"):
        shutil.copy(HERE / f, OUT / f)
        v[f] = hashlib.md5((HERE / f).read_bytes()).hexdigest()[:8]
    # dong.js phải nạp TRƯỚC khi trang dựng xong (bộ motion.js chạy hiệu ứng lúc DOMContentLoaded)
    tai = (f'<link rel="stylesheet" href="phong.css?v={v["phong.css"]}">'
           f'<script src="dong.js?v={v["dong.js"]}"></script></head>')
    dem, dung_het = {}, {}
    for f in sorted(OUT.glob("*.html")):
        h = f.read_text(encoding="utf-8")
        if "dong.js?v=" in h:
            continue
        n = _phong_so(f.stem)
        if n:
            h = _ap_phong(h, n)
            dem[n] = dem.get(n, 0) + 1
        else:   # trang chủ, báo giá: không có phong cách riêng nhưng mở sáng để các mục xoay phong cách hiện rõ
            h = _mo_sang(h)
        h, dung = _xoay(h, n)
        dung_het[f.stem] = len(dung | ({n} if n else set()))
        f.write_text(h.replace("</head>", tai, 1), encoding="utf-8")
    print("[phong] " + " ".join(f"P{k}:{dem[k]}" for k in sorted(dem))
          + f" | so phong cach moi trang: min {min(dung_het.values())}, tb {sum(dung_het.values()) / len(dung_het):.1f}")
