"""Tách nền ảnh chính 5 sản phẩm bằng rembg -> PNG trong suốt + tấm xem thử trên nền tối & sáng."""
import csv, sys
from pathlib import Path
from PIL import Image
from rembg import remove, new_session
BASE = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro")
OUT = BASE / "tach-nen"; OUT.mkdir(exist_ok=True)
ROWS = list(csv.DictReader(open(BASE / "danh-sach-anh.csv", encoding="utf-8-sig")))
ids = [int(x) for x in sys.argv[2].split(",")]
ses = new_session(sys.argv[1])
cells = []
for i in ids:
    im = Image.open(BASE / "anh-goc" / ROWS[i]["file"]).convert("RGB")
    im.thumbnail((1600, 1600))
    cut = remove(im, session=ses, post_process_mask=True)
    cut = cut.crop(cut.getbbox())
    cut.save(OUT / f"a{i}_{sys.argv[1]}.png")
    for bg in ("#141414", "#f6f4f2"):
        c = Image.new("RGB", (420, 520), bg); t = cut.copy(); t.thumbnail((400, 500))
        c.paste(t, ((420 - t.width) // 2, (520 - t.height) // 2), t); cells.append(c)
S = Image.new("RGB", (len(cells) * 430, 520), "white")
for j, c in enumerate(cells): S.paste(c, (j * 430, 0))
S.thumbnail((2000, 2000)); S.save(Path(__file__).parent / "soat" / f"tachnen_{sys.argv[1]}.png")
print("ok")
