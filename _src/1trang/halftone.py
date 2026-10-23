"""Tấm halftone Caldera: nền Plasma Violet, chấm Ember to dần về góc trên-phải tới khi phủ kín (không dùng dải chuyển màu)."""
import math
from pathlib import Path
from PIL import Image, ImageDraw
OUT = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro\tach-nen")
VIOLET, EMBER = (0x52, 0x4a, 0xe9), (0xfc, 0x50, 0x00)

def tam(w, h, step, ten, goc=(1.0, 0.0), mu=1.25):
    S = 2                                                     # vẽ gấp đôi rồi thu nhỏ cho chấm tròn mịn
    im = Image.new("RGB", (w * S, h * S), VIOLET); d = ImageDraw.Draw(im)
    gx, gy = goc[0] * w, goc[1] * h
    dmax = math.hypot(max(gx, w - gx), max(gy, h - gy))
    for y in range(0, h + step, step):
        for x in range(0, w + step, step):
            t = 1 - math.hypot(x - gx, y - gy) / dmax         # 1 ở góc nóng, 0 ở góc xa
            r = step * 0.78 * max(0.0, t) ** mu               # bán kính > step/√2 thì các chấm chồng thành mảng đặc
            if r > 0.6:
                d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=EMBER)
    im = im.resize((w, h), Image.LANCZOS); im.save(OUT / f"{ten}.png", optimize=True); return im

tam(1200, 1400, 18, "halftone_hero")
tam(1200, 900, 16, "halftone_card", goc=(1.0, 0.0), mu=1.6)
Image.open(OUT / "halftone_hero.png").resize((300, 350)).save(Path(__file__).parent / "soat" / "halftone.png")
print("ok")
