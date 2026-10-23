"""Lọc mẩu thừa sau tách nền: giữ các khối alpha liền nhau có diện tích >= ngưỡng × khối lớn nhất."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
D = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro\tach-nen")
cells = []
for i in sys.argv[2].split(","):
    f = D / f"a{i}_isnet-general-use.png"
    im = Image.open(f).convert("RGBA"); a = np.array(im)
    m = a[:, :, 3] > 40
    lab, n = ndimage.label(m)
    sz = ndimage.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, [k + 1 for k, s in enumerate(sz) if s >= float(sys.argv[1]) * sz.max()])
    a[:, :, 3] = np.where(keep, a[:, :, 3], 0)
    out = Image.fromarray(a); out = out.crop(out.getbbox())
    out.save(D / f"a{i}_sach.png")
    for bg in ("#141414", "#ffffff"):
        c = Image.new("RGB", (420, 520), bg); t = out.copy(); t.thumbnail((400, 500))
        c.paste(t, ((420 - t.width) // 2, (520 - t.height) // 2), t); cells.append(c)
    print(i, "khoi:", n, "giu:", int((np.array(sz) >= float(sys.argv[1]) * sz.max()).sum()))
S = Image.new("RGB", (len(cells) * 430, 520), "white")
for j, c in enumerate(cells): S.paste(c, (j * 430, 0))
S.thumbnail((2000, 2000)); S.save(Path(__file__).parent / "soat" / "loc_manh.png")
