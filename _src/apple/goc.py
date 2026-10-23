# goc.py — NỘI DUNG GIỐNG WEB GỐC (otlpro.com/vi) trên khung Apple. Claude, 24/10/2026.
#
# Chạy bằng exec() trong không gian tên của build.py (ngay trước main), nên dùng thẳng img/im_tag/nav/page_*...
# Nguyên tắc để KHÔNG đè phần Codex đang làm trong build.py / site.css / site.js:
#   - chỉ BỔ SUNG: sửa dữ liệu (intro, tính năng, ứng dụng, ảnh) trước khi dựng trang, chèn thêm mục vào HTML đã dựng,
#     thêm trang mới; không viết lại hàm của build.py (bọc lại: gọi hàm gốc rồi chèn);
#   - giao diện riêng ở goc.css (tự gắn vào <head>), không cần JS mới.
# Nguồn: du_lieu/otlpro_vi.json (cào 29 trang /vi ngày 24/10/2026, script trong báo cáo), ảnh trong kho
# F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro (anh-goc = a<số>, anh-goc-vi = ảnh bổ sung).
import json as _json, re as _re

_GOC = _json.load(open(HERE / "du_lieu" / "otlpro_vi.json", encoding="utf-8"))
for _k, _fn in _json.load(open(HERE / "du_lieu" / "anh_vi_map.json", encoding="utf-8")).items():
    EXTRA[_k] = BASE / "anh-goc-vi" / _fn
for _k, _fn in (("shop1", "shop1.webp"), ("shop2", "shop2.webp"), ("shop3", "shop3.jpg")):
    EXTRA[_k] = BASE / "anh-goc-vi" / _fn

_JUNK = ("Trang web này sử dụng cookie", "Chất lượng", "Máy rang cà phê hiện đại và tiên tiến.", "DỊCH VỤ", "HỖ TRỢ",
         "QUAY LẠI TRANG SẢN PHẨM", "otlpro.com@gmail.com", "+84936198938", "© 2024")
_LABELS = {"giới thiệu", "tổng quan", "thông số kỹ thuật", "thông số", "các tính năng chính", "ứng dụng", "những lợi ích",
           "lợi ích chính", "vật liệu", "đặc trưng", "giải thích sơ đồ hệ thống"}

def _parse(path):
    """Trang gốc → danh sách mục [{t: tiêu đề, p: [đoạn], li: [ý], img: [khoá ảnh], g: [(nhóm, [ý])]}] theo đúng thứ tự."""
    secs = [dict(t="", p=[], li=[], img=[], g=[])]
    for bl in _GOC["https://www.otlpro.com" + path]["blocks"]:
        cur = secs[-1]
        if bl["t"] == "a":
            continue
        if bl["t"] == "img":
            if bl.get("key") and bl["key"] not in cur["img"]:
                cur["img"].append(bl["key"])
            continue
        x = bl["x"].strip()
        if not x or any(x.startswith(j) for j in _JUNK) or (bl["t"] == "li" and "\n" in x):
            continue
        key = x.rstrip(":").strip().lower()
        if key in _LABELS or (bl["t"] in ("h1", "h2", "h3", "h4") and len(x) < 70 and not x.endswith(".")):
            secs.append(dict(t=x.rstrip(":").strip(), p=[], li=[], img=[], g=[], tag=bl["t"]))
        elif bl["t"] == "li":
            (cur["g"][-1][1] if cur["g"] else cur["li"]).append(x)
        elif x.endswith(":") and cur["t"].lower().startswith("đặc trưng"):
            cur["g"].append((x.rstrip(":"), []))
        else:
            cur["p"].append(x)
    return secs

def _sec(secs, *names):
    return [s for s in secs if s["t"].lower() in names]

def _kv(li):
    """'Nhãn: giá trị' → (nhãn, giá trị); không có dấu ':' → (câu, '')."""
    a, _, b = li.partition(":")
    return (a.strip(), b.strip().rstrip(".")) if b else (li.rstrip("."), "")

# ======================================================================= máy rang: văn bản + ảnh đúng trang gốc
_RANG = {"otl-1-2": "/vi/may-rang-ca-phe-olt-1kg", "otl-03": "/vi/may-rang-ca-phe-olt-3kg", "otl-06": "/vi/may-rang-ca-phe-olt-6kg",
         "otl-12": "/vi/may-rang-ca-phe-olt-12kg", "otl-15": "/vi/may-rang-ca-phe-otl-15kg",
         "otl-30": "/vi/may-rang-ca-phe-cong-nghiep-otl-30kg", "otl-60": "/vi/may-rang-ca-phe-cong-nghiep-otl-60kg",
         "otl-120": "/vi/may-rang-ca-phe-otl-120kg"}
GOC_RANG = {}
for _r in ROASTERS:
    _s = _parse(_RANG[_r["slug"]])
    _info = dict(variants=[], benefits=[], schema=[], apps=[])
    _gt = _sec(_s, "giới thiệu", "tổng quan")
    if _gt and _gt[0]["p"]:
        _r["intro"] = _gt[0]["p"][0]
    _ft = _sec(_s, "các tính năng chính", "đặc trưng")
    if _ft:
        if _ft[0]["g"]:   # OTL-60/120: nhóm đặc trưng, mỗi nhóm vài ý
            _r["features"] = [(g, " ".join(i.rstrip(".") + "." for i in items)) for g, items in _ft[0]["g"]]
        elif _ft[0]["li"]:
            _r["features"] = [_kv(x) for x in _ft[0]["li"]]
    _ud = _sec(_s, "ứng dụng")
    if _ud and _ud[0]["li"]:
        _r["uses"] = [x.rstrip(".") for x in _ud[0]["li"]]
    _lb = _sec(_s, "những lợi ích")
    if _lb:
        _info["benefits"] = [x.rstrip(".") for x in _lb[0]["li"]]
    _sd = _sec(_s, "giải thích sơ đồ hệ thống")
    if _sd:
        _info["schema"] = [_kv(x) for x in _sd[0]["li"]]
    # phiên bản V1/V2: nhãn "OTL-xx-V1/V2" + hai bảng thông số; ảnh dựng = cặp ảnh ngay trước nhãn, bản vẽ = ảnh trong bảng 1
    _names = []
    for s in _s:
        for x in [s["t"]] + s["p"]:
            if _re.fullmatch(r"OTL-\d+-? ?V\d", x.replace(" ", "")) and x not in _names:
                _names.append(x.replace(" ", ""))
    _tskt = [s for s in _s if s["t"].lower().startswith("thông số")]
    if len(_names) == 2 and len(_tskt) == 2:
        _renders = []
        for s in _s:   # cặp ảnh 2 tấm gần nhất đứng trước bảng thông số thứ nhất
            if s is _tskt[0]:
                break
            if len(s["img"]) == 2:
                _renders = s["img"]
        _draws = _tskt[0]["img"] if len(_tskt[0]["img"]) == 2 else []
        for n in range(2):
            _info["variants"].append(dict(name=_names[n], specs=[_kv(x) for x in _tskt[n]["li"]],
                                          render=_renders[n] if _renders else None, draw=_draws[n] if _draws else None))
    # thư viện ảnh = toàn bộ ảnh cuối trang gốc (+ ảnh đã chọn trước đó, không trùng)
    _all = [k for s in _s for k in s["img"]]
    _last = max((s["img"] for s in _s), key=len)
    _old = [k for k, _ in _r["gallery"]]
    _keys = list(dict.fromkeys(_old + [k for k in _last if k not in {v.get("render") for v in _info["variants"]}]))
    _r["gallery"] = [(k, f'{_r["name"]} — ảnh {i + 1}') for i, k in enumerate(_keys)]
    GOC_RANG[_r["slug"]] = _info

# ======================================================================= thiết bị: trang riêng từng cỡ (giống web gốc)
_CO = [  # slug, đường dẫn gốc, tên, ảnh chính (ảnh trên trang danh mục gốc), nhóm, số liệu nổi bật
    ("od-05", "/vi/may-tach-da-ca-phe-otl-0d-05", "Máy tách đá OD-05", "a178", "destoner",
     [("5–10", "kg", "mỗi mẻ"), ("0,75", "kW", "công suất tiêu thụ"), ("220", "V", "50/60 Hz"), ("V1 · V2", "", "hai phiên bản")]),
    ("od-15", "/vi/may-tach-da-ca-phe-otl-0d-15", "Máy tách đá OD-15", "a178", "destoner",
     [("15–20", "kg", "mỗi mẻ"), ("1,5", "kW", "công suất tiêu thụ"), ("220", "V", "1 pha, 50/60 Hz"), ("V1 · V2", "", "hai phiên bản")]),
    ("od-30", "/vi/may-tach-da-ca-phe-otl-od-30", "Máy tách đá OD-30", "a179", "destoner",
     [("30–40", "kg", "mỗi mẻ"), ("2,2", "kW", "công suất tiêu thụ"), ("380", "V", "3 pha, 50/60 Hz"), ("V1 · V2", "", "hai phiên bản")]),
    ("od-60", "/vi/may-tach-da-ca-phe-otl-od-60", "Máy tách đá OD-60", "a157", "destoner",
     [("60–80", "kg", "mỗi mẻ"), ("4", "kW", "công suất tiêu thụ"), ("380", "V", "3 pha, 50/60 Hz"), ("Inox", "", "thép không gỉ thực phẩm")]),
    ("ab-15", "/vi/xu-ly-khoi-otl-ab-15", "Máy đốt khói AB-15", "a180", "afterburner",
     [("3–15", "kg", "máy rang phục vụ"), ("12–40", "kW", "công suất đốt"), ("2", "", "cấp đầu đốt Ecoflam"), ("Delta", "", "điều khiển nhiệt")]),
    ("ab-30", "/vi/xu-ly-khoi-otl-ab-30", "Máy đốt khói AB-30", "a181", "afterburner",
     [("15–30", "kg", "máy rang phục vụ"), ("20–70", "kW", "công suất đốt"), ("2", "", "cấp đầu đốt Ecoflam"), ("Delta", "", "điều khiển nhiệt")]),
    ("ab-60", "/vi/xu-ly-khoi-otl-ab-60-", "Máy đốt khói AB-60", "a182", "afterburner",
     [("60", "kg", "máy rang tối đa"), ("600", "°C", "nhiệt độ hoạt động"), ("Ø250", "mm", "cổng vào"), ("Ø310", "mm", "cổng ra")]),
    ("ab-120", "/vi/xu-ly-khoi-otl-ab-120", "Máy đốt khói AB-120", "a182", "afterburner",
     [("60+", "kg", "máy rang phục vụ"), ("12–70", "kW", "công suất đốt"), ("2", "", "cấp đầu đốt Ecoflam"), ("Delta", "", "điều khiển nhiệt")]),
]
# Sửa có chủ đích so với trang gốc (ghi trong README): OD-30 trang /vi ghi "3 pha - 220V" — brochure ghi 3 pha 380 V → theo brochure;
# AB-120 trang gốc chép nhầm nguyên khối AB-60 (60 kg, 1452 × 700 × 934) → chỉ lấy khối thông số riêng của AB-120.
_SUA = {"od-30": [("Điện áp: 3 pha - 220V / 50-60Hz", "Điện áp: 3 pha 380 V / 50–60 Hz")]}
_SHARED = ["a186", "a187", "a188", "a189", "a190", "a191", "a192", "a193", "a194", "a195", "a196", "a197", "a198", "a199", "a200", "a201"]
GOC_CO = []
for _slug, _path, _name, _hero, _grp, _stats in _CO:
    _s = _parse(_path)
    _tskt = [s for s in _s if s["t"].lower().startswith("thông số")]
    if _slug == "ab-120":
        _tskt = _tskt[-1:]
    _li = [x for s in _tskt for x in s["li"]]
    for a, b in _SUA.get(_slug, []):
        _li = [b if x == a else x for x in _li]
    _vl = _sec(_s, "vật liệu")
    _specs = [_kv(x) for x in _li] + ([("Vật liệu", _vl[0]["li"][0].rstrip("."))] if _vl and _vl[0]["li"] else [])
    _ft = _sec(_s, "các tính năng chính", "lợi ích chính")
    _feats = [_kv(x) for x in _ft[0]["li"]] if _ft else []
    _lb = _sec(_s, "những lợi ích")
    if _lb and len(_feats) < 4:
        _feats += [(x.rstrip("."), "") for x in _lb[0]["li"]]
    _intro = next((p for s in _s for p in s["p"] if len(p) > 60), "")
    _imgs = [k for s in _s for k in s["img"]]
    # ảnh dùng chung cả dòng (web gốc: OD dùng chung 16 ảnh; AB-30 chỉ có 1 ảnh → thêm ảnh dựng cùng dòng AB)
    _gal = list(dict.fromkeys(_imgs + (_SHARED if _grp == "destoner" else ["a26", "a27", "a98", "a99", "a180", "a181", "a182"])))
    _e = dict(slug=_slug, name=_name, short=_name.split()[-1], kind="Thiết bị", hero=_hero, mode="r",
              series=("Máy tách đá sau rang" if _grp == "destoner" else "Xử lý khói và mùi"),
              tagline=("Tách đá và tạp chất nặng khỏi cà phê rang." if _grp == "destoner" else "Xử lý khí thải, khói đen từ máy rang."),
              lead=_name + ".", intro=_intro, stats=_stats, specs=_specs, features=_feats[:6] or [("Thiết kế và sản xuất tại Việt Nam", "")],
              gallery=[(k, f"{_name} — ảnh {i + 1}") for i, k in enumerate(_gal)], grp=_grp)
    if _slug == "od-30":
        _e["model3d"] = ("3d/od-30-v1.glb", "3d/od-30-v1_poster.jpg", "OD-30 V1", "1,9 MB")
    GOC_CO.append(_e)
    MODE_OF.setdefault(_hero, "r")

# bảng "Theo cỡ máy" trên trang tổng: cập nhật theo trang gốc (OD-60 60–80 kg, 4 kW; AB-15 3–15 kg, 12–40 kW; AB-30 20–70 kW)
for _e in EQUIP:
    if _e["slug"] == "destoner" and _e.get("table"):
        _e["table"] = (_e["table"][0], [("OD-05", "5–10 kg/mẻ", "0,75 kW", "1 pha 220 V"), ("OD-15", "15–20 kg/mẻ", "1,5 kW", "1 pha 220 V"),
                                        ("OD-30", "30–40 kg/mẻ", "2,2 kW", "3 pha 380 V"), ("OD-60", "60–80 kg/mẻ", "4 kW", "3 pha 380 V")])
        _e["stats"] = [("5–80", "kg", "mỗi mẻ, OD-05 đến OD-60"), ("0,75–4", "kW", "công suất tiêu thụ"), ("4", "", "cỡ máy"),
                       ("Inox", "", "thép không gỉ thực phẩm")]
    if _e["slug"] == "afterburner" and _e.get("table"):
        _e["table"] = (("Model", "Dùng cho máy rang", "Công suất đốt / kết nối", "Kích thước D × R × C"),
                       [("AB-15", "3–15 kg", "12–40 kW", "Theo yêu cầu"), ("AB-30", "15–30 kg", "20–70 kW", "Theo yêu cầu"),
                        ("AB-60", "Tới 60 kg", "Vào Ø250 · ra Ø310 mm", "1452 × 700 × 934 mm"), ("AB-120", "Từ 60 kg", "12–70 kW", "Theo yêu cầu")])

# ======================================================================= khung: CSS riêng, menu, chân trang
_head_goc = head
def head(title, desc, gallery_keys=()):
    import hashlib
    v = hashlib.md5((HERE / "goc.css").read_bytes()).hexdigest()[:8]
    return _head_goc(title, desc, gallery_keys).replace("</head>", f'<link rel="stylesheet" href="goc.css?v={v}"></head>', 1)

_NEW_TOP = [("cong-nghe.html", "Công nghệ", "cong-nghe"), ("kien-thuc.html", "Kiến thức", "kien-thuc"), ("cua-hang.html", "Cửa hàng", "cua-hang")]
_nav_goc = nav
def nav(active="", dk=False):
    h = _nav_goc(active if active not in {k for _, _, k in _NEW_TOP} else "", dk)
    items = "".join(f'<li><a class="top{" on" if k == active else ""}" href="{u}">{t}</a></li>' for u, t, k in _NEW_TOP)
    # "So sánh" vẫn nằm trong menu Máy rang → nhường chỗ trên thanh chính cho 3 mục mới của web gốc
    h2 = _re.sub(r'<li><a class="top[^"]*" href="compare\.html">So sánh</a></li>', items, h, count=1)
    if h2 == h:   # Codex đổi menu → chèn trước "Hỗ trợ"
        h2 = _re.sub(r'(<li><a class="top[^"]*" href="support\.html")', items.replace("</li>", "</li>", 1) + r"\1", h, count=1)
    mob = "".join(f'<a href="{u}">{t}</a>' for u, t, _ in _NEW_TOP)
    return h2.replace('<a href="support.html">Hỗ trợ</a>', mob + '<a href="support.html">Hỗ trợ</a>', 1)

_foot_goc = foot
def foot():
    return _foot_goc().replace('<li><a href="about.html#lo-trinh">Lộ trình</a></li>',
                               '<li><a href="about.html#lo-trinh">Lộ trình</a></li><li><a href="cong-nghe.html">Công nghệ</a></li>'
                               '<li><a href="kien-thuc.html">Kiến thức</a></li><li><a href="cua-hang.html">Cửa hàng</a></li>', 1)

def _chen(h, marker, block, before=True):
    """Chèn block trước/sau mốc; mốc không còn (Codex đổi khung) thì chèn trước </main> và báo."""
    i = h.find(marker)
    if i < 0:
        print("  [goc] khong thay moc", marker[:50], "-> chen truoc </main>")
        return h.replace("</main>", block + "</main>", 1)
    if not before:
        i = h.find("</section>", i) + len("</section>")
    return h[:i] + block + h[i:]

def _dl(rows):
    return "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in rows)

# ======================================================================= trang máy rang: phiên bản, lợi ích, sơ đồ
_page_model_goc = page_model
def page_model(i):
    r = ROASTERS[i]; info = GOC_RANG.get(r["slug"], {})
    h = _page_model_goc(i)
    add = ""
    if info.get("variants"):
        cards = ""
        for v in info["variants"]:
            pic = im_tag(v["render"], "r", v["name"]) if v["render"] else ""
            drw = (f'<figure class="g-draw">{im_tag(v["draw"], "p", "Bản vẽ kích thước " + v["name"])}<figcaption class="cap">Bản vẽ kích thước {v["name"]}</figcaption></figure>'
                   if v["draw"] else "")
            cards += f'''<article class="g-var rv"><div class="g-var-im">{pic}</div><h3>{v["name"]}</h3><dl class="specs">{_dl(v["specs"])}</dl>{drw}</article>'''
        add += f'''<section class="sec bg-w" id="phien-ban"><div class="wrap">
<p class="eyebrow rv">Hai phiên bản</p><h2 class="h-l rv" style="margin-top:6px">{r["name"]} có hai phiên bản.</h2>
<p class="lead rv" style="margin-top:12px;max-width:760px">Cùng năng suất, khác bố trí và kích thước. Chọn phiên bản phù hợp mặt bằng xưởng của bạn.</p>
<div class="g-vars">{cards}</div></div></section>'''
    if info.get("schema"):
        add += f'''<section class="sec bg-w"><div class="wrap"><h2 class="h-l rv">Giải thích sơ đồ hệ thống.</h2>
<dl class="specs rv" style="margin-top:30px">{_dl(info["schema"])}</dl></div></section>'''
    if info.get("benefits"):
        lis = "".join(f"<li>{E(x)}.</li>" for x in info["benefits"])
        add += f'''<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Những lợi ích.</h2><ul class="g-ticks rv">{lis}</ul></div></section>'''
    if add:
        h = _chen(h, '<section class="sec bg-c" id="specs">', add)
        if info.get("variants"):
            h = h.replace('<a href="#specs">Thông số</a></nav>', '<a href="#phien-ban">Phiên bản</a><a href="#specs">Thông số</a></nav>', 1)
    return h

# ======================================================================= trang tổng thiết bị: chọn cỡ máy
def _co_cards(grp):
    out = ""
    for e in GOC_CO:
        if e["grp"] != grp:
            continue
        a, u, l = e["stats"][0]
        out += f'''<article class="lc"><a class="im" href="{e["slug"]}.html" aria-label="{e["name"]}">{im_tag(e["hero"], "r", e["name"])}</a>
<div class="tag">{e["series"]}</div><h3>{e["short"]}</h3><p>{a} {u} {l}</p>
<div class="btns"><a class="btn btn-f sm" href="{e["slug"]}.html">Tìm hiểu thêm</a><a class="lnk" href="{qlink(e["name"])}">Báo giá</a></div></article>'''
    return out

_page_equip_goc = page_equip
def page_equip(e):
    h = _page_equip_goc(e)
    grp = e.get("grp") or e["slug"]
    if e["slug"] in ("destoner", "afterburner"):
        blk = f'''<section class="sec bg-c" id="chon-co"><div class="wrap rail-head"><h2 class="h-l rv">Chọn cỡ máy.</h2></div>
<div class="wrap g-grid4">{_co_cards(e["slug"])}</div></section>'''
        h = _chen(h, 'id="highlights"', blk, before=False)
    elif grp in ("destoner", "afterburner"):   # trang từng cỡ: các cỡ khác cùng nhóm
        others = "".join(f'<a class="g-pill{" on" if x["slug"] == e["slug"] else ""}" href="{x["slug"]}.html">{x["short"]}</a>'
                         for x in GOC_CO if x["grp"] == grp)
        h = h.replace('<section class="sec bg-w" id="highlights">',
                      f'<nav class="g-sizes" aria-label="Các cỡ máy"><a class="lnk" href="{grp}.html">Tất cả cỡ</a>{others}</nav>'
                      '<section class="sec bg-w" id="highlights">', 1)
    return h

# ======================================================================= trang chủ: "Hình ảnh sản phẩm" như web gốc
_HOME_PICS = ["a101", "a106", "a137", "a159", "a120", "a50", "a160", "a161", "a162", "a89", "a140", "a311"]
_page_home_goc = page_home
def page_home():
    h = _page_home_goc()
    pics = "".join(f'<figure class="g-ph">{im_tag(k, "p", "Hình ảnh sản phẩm OTL " + str(n + 1))}</figure>' for n, k in enumerate(_HOME_PICS))
    blk = f'''<section class="sec bg-w" id="hinh-anh"><div class="wrap rail-head"><h2 class="h-l rv">Hình ảnh sản phẩm.</h2>
<a class="lnk rv" href="roasters.html">Khám phá các máy rang cà phê hiện đại</a></div>
<div class="wrap"><div class="g-photos rv">{pics}</div></div></section>'''
    i = h.find('id="videos"')
    if i > 0:
        j = h.rfind("<section", 0, i)
        return h[:j] + blk + h[j:]
    return _chen(h, "</main>", blk)

# ======================================================================= Công nghệ (/vi/cong-nghe-technologyotl)
def page_cong_nghe():
    tech = [("01", "Công nghệ đột phá", "OTL Roaster tự hào là đơn vị tiên phong trong việc tích hợp nhiều phương pháp gia nhiệt vào một máy rang duy nhất. Điều này bao gồm việc kết hợp luồng khí nóng thông minh và nhiều cấu hình trống khác nhau để đạt được hiệu quả xử lý nhiệt tối ưu, đảm bảo chất lượng hạt cà phê nhất quán giữa các mẻ rang."),
            ("02", "Tự động hóa thông minh", "Chúng tôi đã phát triển phần mềm quản lý tiên tiến hỗ trợ tự động hóa toàn bộ quy trình rang. Dòng máy rang thương mại OTL Roaster cho phép bạn: phân tích chi tiết — ghi chép và tối ưu hóa từng mẻ rang với độ chính xác cao; cá nhân hóa quá trình rang — thiết lập các cấu hình riêng biệt, phù hợp với phong cách và nhu cầu của từng người rang cà phê."),
            ("03", "Dây chuyền máy đa chức năng", "Bên cạnh các dây chuyền rang cà phê thương mại và công nghiệp, OTL Roaster cũng tập trung vào các dây chuyền rang cà phê mini. Những sản phẩm này kết hợp hoàn hảo giữa truyền thống và công nghệ, giúp các nhà nghiên cứu và những người đam mê cà phê khám phá sâu hơn về hương vị."),
            ("04", "Biểu tượng công nghệ", "Mỗi sản phẩm của OTL Roaster đều đi kèm với một bộ biểu tượng độc đáo giúp khách hàng dễ dàng nhận biết các tính năng và công nghệ được tích hợp. Những biểu tượng này chuẩn hóa thông tin và đơn giản hóa trải nghiệm người dùng."),
            ("05", "Kết nối và chia sẻ", "Chúng tôi cam kết liên tục đổi mới và chia sẻ kiến thức cũng như công nghệ thông qua các bài viết và hội thảo trực tuyến. Đừng quên theo dõi OTL Roaster trên các nền tảng mạng xã hội để cập nhật thông tin mới nhất!")]
    fc = "".join(f'<div class="fc"><p class="n">{n}</p><h3>{t}</h3><p>{d}</p></div>' for n, t, d in tech)
    sup = [("Tư vấn chuyên sâu", "Hỗ trợ khách hàng lựa chọn máy rang cà phê phù hợp nhất với nhu cầu của họ: từ máy rang mini, máy rang công nghiệp đến máy rang thông minh."),
           ("Đội ngũ chuyên gia", "Một đội ngũ chuyên gia giàu kinh nghiệm luôn sẵn sàng giải đáp mọi thắc mắc về công nghệ, vận hành và bảo trì."),
           ("Lắp đặt tại chỗ", "Đội ngũ kỹ thuật sẽ đảm bảo máy rang được lắp đặt theo đúng tiêu chuẩn, an toàn và hiệu quả."),
           ("Hướng dẫn sử dụng chi tiết", "Khách hàng sẽ được các chuyên gia hướng dẫn trực tiếp để vận hành máy một cách dễ dàng và tối ưu."),
           ("Đường dây nóng", "Đội ngũ kỹ thuật luôn sẵn sàng hỗ trợ khách hàng mọi lúc, mọi nơi."),
           ("Chẩn đoán từ xa", "Sử dụng công nghệ hiện đại để hỗ trợ khách hàng kiểm tra và khắc phục sự cố nhanh chóng.")]
    sp = "".join(f'<div class="fc"><h3>{t}</h3><p>{d}</p></div>' for t, d in sup)
    body = f'''{nav("cong-nghe")}
<main>
<section class="sec bg-w center" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">Công nghệ</p><h1 class="h-hero rv" style="margin-top:8px">Công nghệ tại OTL Roaster.</h1>
<p class="lead measure rv" style="margin-top:18px">Tại OTL Roaster, công nghệ là trọng tâm trong hành trình phát triển sản phẩm của chúng tôi. Chúng tôi không ngừng nỗ lực để thiết lập các tiêu chuẩn mới về hiệu quả năng lượng, tối ưu hóa các quy trình rang xay sạch và thông minh, đồng thời tích hợp những đổi mới tiên phong trong ngành rang cà phê.</p></div>
<div class="wrap"><div class="g-photos two rv"><figure class="g-ph">{im_tag("a172", "p", "Khách hàng và kỹ thuật viên bên máy rang OTL")}</figure>
<figure class="g-ph">{im_tag("a173", "p", "Màn hình điều khiển và hồ sơ rang OTL")}</figure></div></div></section>
<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Năm trụ cột công nghệ.</h2><div class="feats">{fc}</div></div></section>
<section class="sec bg-w" id="dich-vu"><div class="wrap">
<p class="eyebrow rv">Dịch vụ hỗ trợ</p><h2 class="h-l rv" style="margin-top:6px">Nhanh chóng, chuyên nghiệp, hiệu quả.</h2>
<p class="lead rv" style="margin-top:14px;max-width:760px">Công ty rang cà phê OTL cam kết cung cấp cho khách hàng không chỉ các sản phẩm chất lượng cao mà còn cả dịch vụ hỗ trợ toàn diện và tận tâm. Chúng tôi hiểu rằng thành công của khách hàng cũng chính là thành công của chúng tôi.</p>
<div class="feats three">{sp}</div>
<div class="g-photos three rv" style="margin-top:40px"><figure class="g-ph">{im_tag("a174", "p", "Gia công trống rang tại nhà máy OTL")}</figure>
<figure class="g-ph">{im_tag("a175", "p", "Kỹ thuật viên OTL lắp đặt máy rang")}</figure><figure class="g-ph">{im_tag("a122", "p", "Hướng dẫn vận hành máy rang OTL")}</figure></div></div></section>
<section class="sec bg-c"><div class="wrap rail-head"><h2 class="h-l rv">Bài viết mới.</h2><a class="lnk rv" href="kien-thuc.html">Tất cả bài viết</a></div>
<div class="wrap g-grid3">{"".join(_bai_card(b) for b in BAI[:3])}</div></section>
{cta("Rang thông minh hơn với OTL.", "Trò chuyện với đội ngũ OTL về công nghệ phù hợp với xưởng của bạn.", ("Nhận báo giá", "quote.html"), ("Liên hệ hỗ trợ", "support.html"), "bg-w")}
</main>{foot()}'''
    return head("Công nghệ — OTL Roaster", "Công nghệ đột phá, tự động hóa thông minh và dịch vụ hỗ trợ của OTL Roaster.") + body

# ======================================================================= Kiến thức: 7 bài viết đầy đủ như web gốc
_BAI_URL = ["/vi/ba-phuong-phap-truyen-nhiet-trong-rang-ca-phe-va-anh-huong-djen-huong-vi",
            "/vi/djanh-gia-ca-phe-rang-and-nhan-biet-huong-vi-chia-khoa-tao-nen-ca-phe-djac-san",
            "/vi/qua-trinh-hinh-thanh-va-phat-trien-cua-cong-ty-tnhh-cong-nghiep-otl",
            "/vi/danh-gia-qua-trinh-rang-ca-phe-va-nhan-biet-huong-vi",
            "/vi/ca-phe-len-men-nguon-goc-va-quy-trinh-che-bien",
            "/vi/ca-phe-pha-lanh",
            "/vi/nhung-cau-hoi-thuong-gap-khi-ban-moi-bat-djau-voi-ca-phe-rang"]
_ANH_BIA = {"/vi/ba-phuong-phap-truyen-nhiet-trong-rang-ca-phe-va-anh-huong-djen-huong-vi": "a68"}

def _bai(path):
    """Một bài viết gốc → tiêu đề, tóm tắt, ngày (đổi M/D/YYYY → D/M/YYYY), thời gian đọc, ảnh bìa, thân bài theo thứ tự."""
    bl = [b for b in _GOC["https://www.otlpro.com" + path]["blocks"] if b["t"] != "a"]
    title = next(b["x"] for b in bl if b["t"] == "h1")
    body, summary, date, read, cover = [], "", "", "", _ANH_BIA.get(path)
    seen = set()
    for b in bl:
        if b["t"] == "img":
            if b.get("key") and b["key"] not in seen:
                seen.add(b["key"]); cover = cover or b["key"]; body.append(("img", b["key"]))
            continue
        x = b["x"].strip()
        if b["t"] == "h1" or not x or any(x.startswith(j) for j in _JUNK) or (b["t"] == "li" and "\n" in x):
            continue
        m = _re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})(\d+) phút đọc", x)
        if m:
            date, read = f"{m.group(2)}/{m.group(1)}/{m.group(3)}", f"{m.group(4)} phút đọc"; continue
        if not summary and b["t"] == "p" and not date:
            summary = x; continue
        if body and body[-1][1] == x:
            continue
        body.append((b["t"], x))
    if body and body[0] == ("img", cover):
        body = body[1:]
    slug = "kt-" + path.rsplit("/", 1)[-1]
    return dict(path=path, slug=slug, title=title, summary=summary, date=date, read=read, cover=cover, body=body)

BAI = [_bai(p) for p in _BAI_URL]

def _bai_card(b):
    return f'''<article class="lc g-post"><a class="im g-cover" href="{b["slug"]}.html" aria-label="{E(b["title"])}">{im_tag(b["cover"], "p", b["title"]) if b["cover"] else ""}</a>
<div class="tag">{b["date"]} · {b["read"]}</div><h3>{E(b["title"].capitalize() if b["title"].isupper() else b["title"])}</h3><p>{E(b["summary"][:160])}</p>
<div class="btns"><a class="lnk" href="{b["slug"]}.html">Đọc bài viết</a></div></article>'''

def page_kien_thuc():
    body = f'''{nav("kien-thuc")}
<main>
<section class="sec bg-w" style="padding-top:64px;padding-bottom:40px"><div class="wrap">
<h1 class="h-hero rv">Kiến thức</h1><p class="sub rv" style="margin-top:12px">Rang cà phê, đánh giá hương vị và câu chuyện OTL.</p></div></section>
<section class="sec bg-c" style="padding-top:60px"><div class="wrap g-grid3">{"".join(_bai_card(b) for b in BAI)}</div></section>
{cta("Có câu hỏi về rang cà phê?", "Đội ngũ OTL sẵn sàng giải đáp về công nghệ, vận hành và bảo trì máy rang.", ("Liên hệ hỗ trợ", "support.html"), ("Khám phá máy rang", "roasters.html"), "bg-w")}
</main>{foot()}'''
    return head("Kiến thức — OTL Roaster", "Bài viết về rang cà phê, đánh giá hương vị và câu chuyện OTL.") + body

def page_bai(b):
    parts = []
    for t, x in b["body"]:
        if t == "img":
            parts.append(f'<figure class="g-art-im">{im_tag(x, "p", b["title"])}</figure>')
        elif t in ("h2", "h3", "h4"):
            parts.append(f"<{'h2' if t == 'h2' else 'h3'}>{E(x)}</{'h2' if t == 'h2' else 'h3'}>")
        elif t == "li":
            parts.append(f"<ul><li>{E(x)}</li></ul>")
        else:
            parts.append(f"<p>{E(x)}</p>")
    html_body = "".join(parts).replace("</ul><ul>", "")
    others = [x for x in BAI if x is not b][:3]
    cover = f'<figure class="g-art-cover rv">{im_tag(b["cover"], "p", b["title"], lazy=False)}</figure>' if b["cover"] else ""
    body = f'''{nav("kien-thuc")}
<main>
<article class="g-art"><header class="wrap g-art-h">
<p class="eyebrow rv"><a href="kien-thuc.html">Kiến thức</a></p><h1 class="h-xl rv">{E(b["title"])}</h1>
<p class="lead rv">{E(b["summary"])}</p><p class="small rv">{b["date"]} · {b["read"]} · OTL Roaster</p></header>
<div class="wrap">{cover}</div>
<div class="g-art-b rv">{html_body}</div></article>
<section class="sec bg-c"><div class="wrap rail-head"><h2 class="h-l rv">Đọc tiếp.</h2><a class="lnk rv" href="kien-thuc.html">Tất cả bài viết</a></div>
<div class="wrap g-grid3">{"".join(_bai_card(x) for x in others)}</div></section>
</main>{foot()}'''
    return head(f'{b["title"]} — OTL Roaster', b["summary"][:160]) + body

# ======================================================================= Cửa hàng (/vi/cua-hang-otl)
_SHOP = [("shop1", "Mới 100%", "DiFluid Omni", "$899.99"),
         ("shop2", "Mới 100%", "Kính quan sát cà phê — dùng cho máy rang thương hiệu O Tesla", "$4.00"),
         ("shop3", "Top quality", "Thùng chứa cà phê, silo cà phê", "$110.00")]
def page_cua_hang():
    cards = "".join(f'''<article class="lc g-shop"><div class="im">{im_tag(k, "p", n)}</div><div class="tag">{b}</div><h3>{E(n)}</h3>
<p class="g-price">{p}</p><div class="btns"><a class="btn btn-f sm" href="{qlink(n)}">Hỏi mua</a><a class="lnk" href="support.html#contact">Liên hệ</a></div></article>''' for k, b, n, p in _SHOP)
    body = f'''{nav("cua-hang")}
<main>
<section class="sec bg-w" style="padding-top:64px;padding-bottom:40px"><div class="wrap">
<h1 class="h-hero rv">Phụ tùng và hàng hóa</h1>
<p class="lead rv" style="margin-top:16px;max-width:820px">Chào mừng đến với Cửa hàng Phụ tùng và Quà lưu niệm của OTL – điểm đến lý tưởng cho những người đam mê cà phê và yêu thích công nghệ máy rang cà phê OTL. Tại đây, chúng tôi cung cấp đầy đủ các phụ tùng thay thế chính hãng cho máy rang cà phê OTL, đảm bảo hiệu suất tối ưu và độ bền lâu dài cho thiết bị của bạn.</p></div>
<div class="banner rv-f">{im_tag("a95", "p", "Cửa hàng OTL")}</div></section>
<section class="sec bg-c"><div class="wrap rail-head"><h2 class="h-l rv">Tất cả sản phẩm.</h2><p class="small">3 sản phẩm · giá tham khảo theo cửa hàng otlpro.com</p></div>
<div class="wrap g-grid3">{cards}</div></section>
{cta("Cần phụ tùng cho máy OTL?", "Gửi model máy và mô tả phụ tùng, OTL sẽ báo giá và thời gian giao.", ("Nhận báo giá", "quote.html"), ("Liên hệ hỗ trợ", "support.html"), "bg-w")}
</main>{foot()}'''
    return head("Cửa hàng — OTL Roaster", "Phụ tùng chính hãng và hàng hóa cho máy rang cà phê OTL.") + body

# ======================================================================= ghi thêm các trang mới
_page_about_goc = page_about
def page_about():
    h = _page_about_goc()
    b = next(x for x in BAI if "qua-trinh-hinh-thanh" in x["path"])
    return h.replace('<ul class="know rv">', f'<ul class="know rv"><li><a class="lnk" href="{b["slug"]}.html">{E(b["title"])}</a></li>', 1)

_main_goc = main
def main():
    _main_goc()
    shutil.copy(HERE / "goc.css", OUT / "goc.css")
    extra = {"cong-nghe": page_cong_nghe(), "kien-thuc": page_kien_thuc(), "cua-hang": page_cua_hang()}
    for b in BAI:
        extra[b["slug"]] = page_bai(b)
    for e in GOC_CO:
        extra[e["slug"]] = page_equip(e)
    for name, h in extra.items():
        h = h.replace("<main", '<main id="main-content" tabindex="-1"', 1)
        (OUT / f"{name}.html").write_text(h, encoding="utf-8")
    print(f"[goc] +{len(extra)} trang (cong nghe, kien thuc x{len(BAI) + 1}, cua hang, {len(GOC_CO)} co thiet bi)")

# 8 phong cách Apple theo nhóm trang (Claude 24/10) — chạy sau cùng, chỉ gắn lớp + phong.css
exec(compile((HERE / "phong.py").read_text(encoding="utf-8"), str(HERE / "phong.py"), "exec"))
