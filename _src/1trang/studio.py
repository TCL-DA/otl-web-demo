"""Dựng ảnh studio tối cho BMW: đặt ảnh thật đã tách nền (không sửa máy) lên phông tối có vùng sáng + bóng sàn."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
D = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro\tach-nen")
W, H = 2400, 1350
# (tên ra, file nguồn, độ sáng tâm phông, tỉ lệ chiều cao máy)
JOBS = [("studio_13", "a13_sach.png", 58, .80), ("studio_240", "a240_isnet-general-use.png", 52, .82),
        ("studio_37", "a37_isnet-general-use.png", 118, .84), ("studio_78", "a78_sach.png", 104, .78),
        ("studio_27", "a27_isnet-general-use.png", 110, .62), ("studio_180", "a180_isnet-general-use.png", 110, .70), ("studio_181", "a181_isnet-general-use.png", 110, .74), ("studio_182", "a182_isnet-general-use.png", 110, .62)]

def phong(center):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W * .5) / (W * .42)) ** 2 + ((y - H * .46) / (H * .62)) ** 2)
    t = np.clip(1 - d, 0, 1); t = t * t * (3 - 2 * t)          # smoothstep: ánh sáng tắt dần như đèn studio
    v = 10 + (center - 10) * t
    return Image.fromarray(np.dstack([v, v, v]).astype(np.uint8))

cells = []
for out, src, center, hs in JOBS:
    bg = phong(center).convert("RGBA")
    m = Image.open(D / src).convert("RGBA")
    s = H * hs / m.height
    if m.width * s > W * .7: s = W * .7 / m.width
    m = m.resize((int(m.width * s), int(m.height * s)), Image.LANCZOS)
    x0, y0 = (W - m.width) // 2, int(H * .90) - m.height
    sh = Image.new("L", (W, H), 0)                                  # bóng sàn: elip mờ dưới chân máy
    from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse([x0 + m.width * .05, y0 + m.height - 22, x0 + m.width * .95, y0 + m.height + 26], fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), bg, sh)
    bg.alpha_composite(m, (x0, y0))
    bg.convert("RGB").save(D / f"{out}.jpg", quality=90)
    t = bg.convert("RGB"); t.thumbnail((600, 400)); cells.append(t)
S = Image.new("RGB", (600 * len(cells) + 10 * len(cells), 340), "white")
for i, c in enumerate(cells): S.paste(c, (i * 610, 0))
S.save(Path(__file__).parent / "soat" / "studio.png"); print("ok")


