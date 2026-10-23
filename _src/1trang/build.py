"""Dựng demo otlpro: mỗi file HTML tự chứa (ảnh base64 nhúng 1 lần + bộ animation).
Trong template: <img data-k="a278"> (a<số> = ảnh thứ <số> trong anh-goc/danh-sach-anh.csv), {{IMGS}}, {{INC:_motion.js}}, {{IMG:k}}."""
import base64, csv, io, json, re, sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
BASE = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro")
OUT = BASE / "demo"
ROWS = list(csv.DictReader(open(BASE / "danh-sach-anh.csv", encoding="utf-8-sig")))
REF = Path(r"F:\Kho-anh\09_Thiet-ke-khac\File-AI\164_Destoner_24\Des_24_OTL-06A-white.png")
ALPHA = {27, 156, 180, 181, 182, 98, 99, 230, 157, 179, 291}   # render nền trắng/trong suốt -> webp giữ alpha

def web(i): return BASE / "anh-goc" / ROWS[i]["file"]

SPECIAL = {"hero": (REF, 1300, "WEBP_A"), "icon": (web(1), 240, "PNG"),
           "hthero": (BASE / "tach-nen" / "halftone_hero.png", 1400, "WEBP_A"),     # halftone.py
           "htcard": (BASE / "tach-nen" / "halftone_card.png", 1200, "WEBP_A")}
for n, nm in enumerate(["1-superlative", "2-dyson", "3-bmw", "4-caldera", "5-peakdesign"], 1):
    SPECIAL[f"t{n}"] = (HERE / "soat" / f"thumb_{nm}.jpg", 1100, "JPEG")

def nguon(k):
    if k in SPECIAL: return SPECIAL[k]
    c = re.fullmatch(r"c(\d+)", k)          # c<số> = ảnh đã tách nền (rembg isnet) của ảnh a<số>
    if c: return (BASE / "tach-nen" / f"a{c.group(1)}_isnet-general-use.png", 1300, "WEBP_A")
    d = re.fullmatch(r"d(\d+)", k)          # d<số> = ảnh studio tối dựng từ ảnh tách nền (studio.py)
    if d: return (BASE / "tach-nen" / f"studio_{d.group(1)}.jpg", 1920, "JPEG")
    s = re.fullmatch(r"s(\d+)", k)          # s<số> = ảnh tách nền đã lọc mẩu thừa (loc_manh.py)
    if s: return (BASE / "tach-nen" / f"a{s.group(1)}_sach.png", 1300, "WEBP_A")
    m = re.fullmatch(r"a(\d+)", k)
    if not m: raise KeyError(k)
    i = int(m.group(1))
    return (web(i), 1000, "WEBP_A" if i in ALPHA else "JPEG")

_cache = {}
def data_uri(k):
    if k in _cache: return _cache[k]
    src, maxside, fmt = nguon(k)
    im = Image.open(src)
    if k == "hero": im = im.crop(im.getbbox())      # cắt sát máy -> toạ độ nhãn in lụa tính theo % ảnh
    im.thumbnail((maxside, maxside), Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "JPEG": im.convert("RGB").save(buf, "JPEG", quality=76, optimize=True, progressive=True); mime = "image/jpeg"
    elif fmt == "PNG": im.convert("RGBA").save(buf, "PNG", optimize=True); mime = "image/png"
    else: im.convert("RGBA").save(buf, "WEBP", quality=80, method=6); mime = "image/webp"
    _cache[k] = f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()
    return _cache[k]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or sorted(p.stem for p in (HERE / "tpl").glob("*.html") if not p.stem.startswith("_"))
    for name in names:
        html = (HERE / "tpl" / f"{name}.html").read_text(encoding="utf-8")
        html = re.sub(r"\{\{INC:([\w.]+)\}\}", lambda m: (HERE / "tpl" / m.group(1)).read_text(encoding="utf-8"), html)
        keys = sorted(set(re.findall(r'data-k="(\w+)"', html)))
        imgs = {k: data_uri(k) for k in keys}
        html = html.replace("{{IMGS}}", "<script>window.IMGS=" + json.dumps(imgs) + "</script>")
        html = re.sub(r"\{\{IMG:(\w+)\}\}", lambda m: data_uri(m.group(1)), html)
        left = re.findall(r"\{\{[^}]+\}\}", html)
        assert not left, f"{name}: con placeholder {left}"
        (OUT / f"{name}.html").write_text(html, encoding="utf-8")
        thuc = sorted(k for k in keys if re.fullmatch(r"a\d+", k))
        print(f"{name}.html  {len(html.encode())/1e6:.2f} MB  | anh-goc: {len(thuc)} anh | khac: {[k for k in keys if k not in thuc]}")

if __name__ == "__main__":
    main()
