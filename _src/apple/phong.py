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
        i = h.find("window.OTLTheme=")
        j = h.find("</script>", i) + len("</script>") if i >= 0 else -1
        if j > 0:
            h = h[:j] + _SANG + h[j:]
    if n == 3:   # dải xanh băng: mục đầu tiên không phải dải tối
        h = _re.sub(r'(<main[^>]*>\s*(?:<section class="[^"]*\bdk\b[^"]*".*?</section>\s*)?<section class="sec )', r"\1g-ice ",
                    h, count=1, flags=_re.S)
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

_main_phong = main
def main():
    import hashlib
    _main_phong()
    shutil.copy(HERE / "phong.css", OUT / "phong.css")
    v = hashlib.md5((HERE / "phong.css").read_bytes()).hexdigest()[:8]
    dem = {}
    for f in sorted(OUT.glob("*.html")):
        n = _phong_so(f.stem)
        if not n:
            continue
        h = f.read_text(encoding="utf-8")
        if _re.search(r'<body class="[^"]*\bst st\d', h):
            continue
        h = _ap_phong(h, n).replace("</head>", f'<link rel="stylesheet" href="phong.css?v={v}"></head>', 1)
        f.write_text(h, encoding="utf-8")
        dem[n] = dem.get(n, 0) + 1
    print("[phong] " + " ".join(f"P{k}:{dem[k]}" for k in sorted(dem)))
