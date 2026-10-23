"""Dựng bản demo NHIỀU TRANG kiểu Apple cho otlpro.com → F:\\Project\\otl-web-demo\\apple\\

Sếp chê bản 1 trang kéo dài (23/10/2026) → làm khung như apple.com/ipad + web hãng máy (Giesen, Loring, Probat):
trang chủ · trang dòng máy (dải biểu tượng + băng chuyền) · mỗi model 1 trang · so sánh · thiết bị phụ · giải pháp ·
hỗ trợ · về OTL · hỏi giá.

Nội dung + thông số lấy nguyên từ các trang sản phẩm otlpro.com (cào 23/10/2026). Ảnh lấy từ kho
F:\\Kho-anh\\09_Thiet-ke-khac\\261023_web-otlpro (a<số> = dòng thứ <số> trong danh-sach-anh.csv).
Luật ảnh OTL (F:\\Kho-anh\\OTL_MAY_LIEN_KHOI_THAM_CHIEU.md): ưu tiên máy liền khối;
OTL-60/120 dùng ảnh thật theo ngoại lệ người dùng đã duyệt ngày 23/10/2026.

Chạy:  python build.py        (ảnh đã xử lý được giữ lại, chỉ dựng lại HTML; xoá apple/img để xử lý ảnh lại)
"""
import csv, html, json, shutil
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "apple"
IMG = OUT / "img"
BASE = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro")
REF = Path(r"F:\Kho-anh\09_Thiet-ke-khac\File-AI\164_Destoner_24\Des_24_OTL-06A-white.png")
ROWS = list(csv.DictReader(open(BASE / "danh-sach-anh.csv", encoding="utf-8-sig")))
E = html.escape

# ======================================================================= ảnh
# Bộ hồ sơ sếp đưa 23/10 (chép từ máy chủ \\OTESLA-MAYCHU\otesla\06_QUAN_LY\OTL ROASTER)
MAYCHU = Path(r"F:\Kho-anh\01_May-rang\OTL-ROASTER-maychu")
EXTRA = {"h60": MAYCHU / "Roaster" / "ROASTER OTL-60" / "457098953_1000186252120932_8676377476762948059_n.jpg",   # OTL-60/120: ảnh thật, Thành cho ngoại lệ tủ rời 23/10
         "g60a": MAYCHU / "Roaster" / "ROASTER OTL-60" / "457317283_1000186382120919_4985083329957723627_n.jpg",
         "g60b": MAYCHU / "Roaster" / "ROASTER OTL-60" / "457362910_1000186538787570_3606097588361354739_n.jpg",
         "g60c": MAYCHU / "Roaster" / "ROASTER OTL-60" / "IMG_3249.JPG",
         "h120": MAYCHU / "Roaster" / "ROASTER OTL-120" / "ROASTER OTL-120(PICTURE2).jpg",
         "g120a": MAYCHU / "Roaster" / "ROASTER OTL-120" / "IMG_2776.JPG",
         "g120b": MAYCHU / "Roaster" / "ROASTER OTL-120" / "ROASTER OTL-120(PICTURE1)5.jpg",
          "w30": MAYCHU / "Roaster" / "ROASTER OTL-30" / "30kg trang (2).png",      # OTL-30 trắng, HMI gắn hông — đúng luật nhận diện
         "cyc": MAYCHU / "Cyclone" / "EXTERNAL CYCLONE-OTL6" / "DIMENTION.png"}  # bản vẽ kích thước, ảnh dựng ở bên phải
Image.MAX_IMAGE_PIXELS = None   # ảnh dựng máy chủ 10000 × 10000 px

def _src(key):
    if key == "ref": return REF
    if key in EXTRA: return EXTRA[key]
    if key[0] == "c": return BASE / "tach-nen" / f"a{key[1:]}_isnet-general-use.png"
    if key[0] == "s": return BASE / "tach-nen" / f"a{key[1:]}_sach.png"
    return BASE / "anh-goc" / ROWS[int(key[1:])]["file"]

def _clear_white(im):
    """Ảnh dựng 3D nền trắng → nền trong suốt: tô loang từ mép vào vùng gần trắng nối liền với mép."""
    im = im.convert("RGB")
    r, g, b = im.split()
    low = ImageChops.darker(ImageChops.darker(r, g), b)
    m = low.point(lambda v: 255 if v >= 240 else 0)
    w, h = m.size
    seeds = [(x, 0) for x in range(0, w, 24)] + [(x, h - 1) for x in range(0, w, 24)] + \
            [(0, y) for y in range(0, h, 24)] + [(w - 1, y) for y in range(0, h, 24)]
    for s in seeds:
        if m.getpixel(s) == 255:
            ImageDraw.floodfill(m, s, 128)
    alpha = m.point(lambda v: 0 if v == 128 else 255)
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out

def _clear_bg(im, tol=14):
    """Ảnh dựng nền MÀU ĐỒNG NHẤT (vd nền xanh than 26,31,37) → trong suốt: tô loang từ mép vùng gần màu góc ảnh."""
    im = im.convert("RGB"); bg = im.getpixel((2, 2))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L")
    m = diff.point(lambda v: 255 if v <= tol else 0)
    w, h = m.size
    for s in [(x, 0) for x in range(0, w, 24)] + [(x, h - 1) for x in range(0, w, 24)] + [(0, y) for y in range(0, h, 24)] + [(w - 1, y) for y in range(0, h, 24)]:
        if m.getpixel(s) == 255: ImageDraw.floodfill(m, s, 128)
    out = im.convert("RGBA"); out.putalpha(m.point(lambda v: 0 if v == 128 else 255))
    return out

WM = {"h60", "g60a", "g60b"}   # ảnh OTL-60 có logo "Tesla ROASTER" cũ đóng góc trái trên (nằm trên nền mái tôn)

def _no_wm(im):
    """Xoá logo cũ ở góc trái trên: mặt nạ = điểm đỏ/xanh bão hoà trong vùng 40% × 32%, nới rộng, tô lấp theo nền mái (OpenCV TELEA)."""
    import cv2, numpy as np
    a = np.array(im.convert("RGB")); h, w = a.shape[:2]
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 1] > 90) & (hsv[..., 2] > 60)).astype(np.uint8) * 255
    m[int(h * 0.32):, :] = 0; m[:, int(w * 0.40):] = 0
    m = cv2.dilate(m, np.ones((9, 9), np.uint8), iterations=2)
    return Image.fromarray(cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA))

def _cut(im):
    im = im.convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(box) if box else im

USED = {}
def img(key, mode="p"):
    """mode: r = ảnh dựng nền trắng → trong suốt · a = ảnh đã có nền trong suốt · p = ảnh chụp ·
    t = ảnh nhỏ cho dải biểu tượng/menu (từ ảnh r/a). Trả về đường dẫn tương đối."""
    if mode == "t":
        name, base_mode = f"{key}_t.webp", MODE_OF.get(key, "r")
    else:
        name, base_mode = f"{key}.{'jpg' if mode == 'p' else 'webp'}", mode
        USED.setdefault(key, mode)
    path = IMG / name
    if not path.exists():
        IMG.mkdir(parents=True, exist_ok=True)
        im = Image.open(_src(key))
        if key == "cyc": im = im.convert("RGB").crop((410, 180, im.width, 665))   # chỉ lấy ảnh dựng (đo vùng điểm tối), bỏ nét bản vẽ
        if im.width > 3000: im.thumbnail((3000, 3000), Image.LANCZOS)   # ảnh 10000 px: thu nhỏ trước khi tô loang
        if key in WM: im.thumbnail((1600, 1600), Image.LANCZOS); im = _no_wm(im)
        if base_mode == "r": im = _cut(_clear_white(im))
        elif base_mode == "k": im = _cut(_clear_bg(im))
        elif base_mode == "a": im = _cut(im)
        if mode == "t":
            im.thumbnail((240, 160), Image.LANCZOS)
            im.convert("RGBA").save(path, "WEBP", quality=82, method=6)
        elif mode == "p":
            im.thumbnail((1600, 1600), Image.LANCZOS)
            im.convert("RGB").save(path, "JPEG", quality=80, optimize=True, progressive=True)
        else:
            im.thumbnail((1400, 1400), Image.LANCZOS)
            im.save(path, "WEBP", quality=84, method=6)
    return f"img/{name}"

def im_tag(key, mode, alt, cls="", lazy=True, k=False):
    src = img(key, mode)
    cls = (cls + " wm").strip() if key in WHITE else cls
    at = f' class="{cls}"' if cls else ""
    dk = f' data-k="{key}"' if k else ""
    ld = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return f'<img src="{src}"{at}{dk} alt="{E(alt)}" decoding="async"{ld}>'

SYS_ICON = ('<svg viewBox="0 0 120 80" width="114" height="76" fill="none" stroke="#86868b" stroke-width="2" '
            'stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"><rect x="12" y="30" width="46" height="30" rx="5"/>'
            '<circle cx="35" cy="45" r="9"/><path d="M58 40h14V16h10"/><path d="M82 8h20v22l-10 13-10-13z"/><path d="M92 43v19"/>'
            '<path d="M6 66h108"/><path d="M20 60v6M50 60v6M86 62v4M98 62v4"/></svg>')


# ======================================================================= dữ liệu — TIẾNG VIỆT (23/10/2026)
# Câu chữ bám bản /vi của otlpro.com + brochure máy chủ. Bản tiếng Anh cũ: build_en_20261023.py (dịch các nước làm sau).
from urllib.parse import quote as _q

ROASTERS = [
    dict(slug="otl-1-2", name="OTL-1.2", kind="Máy rang cà phê", hero="a51", mode="r", wash=False,
         tagline="Mẻ nhỏ. Kiểm soát chuẩn.", tag="",
         lead="Máy rang nhỏ gọn cho quán cà phê và phòng thử mẫu.",
         intro="OTL-1.2 là máy rang hiện đại, nhỏ gọn, thiết kế cho quán cà phê nhỏ và phòng thí nghiệm. "
               "Công nghệ tiên tiến giúp từng mẻ rang chính xác và đồng đều.",
         batch="0,5–1,2", kgh="2–4", burner="3", elec="1", power="1 pha 200–240 V · 50/60 Hz",
         dims=["1290 × 600 × 950"],
         features=[("Luồng khí nóng thông minh", "Hệ thống khí nóng giúp mẻ rang chín đều."),
                   ("Điều chỉnh dễ dàng", "Nhiệt độ và tốc độ trống cài đặt, thay đổi đơn giản."),
                   ("Tiết kiệm năng lượng", "Tiêu thụ thấp, thân thiện với môi trường."),
                   ("Sẵn sàng cho phòng thử mẫu", "Đủ nhỏ để rang mẫu và phát triển công thức.")],
         uses=["Quán cà phê", "Cơ sở rang quy mô nhỏ", "Phòng thí nghiệm, rang mẫu"],
         gallery=[("a62", "OTL-1.2 tại quán cà phê"), ("a59", "Khay làm nguội đồng"), ("a61", "Mặt trống và tay cầm"),
                  ("a55", "Kính quan sát")]),
    dict(slug="otl-03", name="OTL-03", kind="Máy rang cà phê", hero="c240", mode="a", wash=True,
         tagline="Sinh ra cho quán cà phê.", tag="",
         lead="Rang chính xác, đồng đều ngay tại quán.",
         intro="OTL-03 là giải pháp lý tưởng cho quán cà phê vừa và người rang chuyên nghiệp. Thiết kế chắc chắn cùng "
               "các tính năng tiên tiến giúp mỗi mẻ rang chính xác, ổn định và đạt chất lượng cao nhất.",
         batch="1–3", kgh="4–12", burner="10", elec="1,5", power="1 pha 200–240 V · 50/60 Hz",
         dims=["1800 × 860 × 1715 (V2)"],
         features=[("Luồng khí nóng hiệu quả", "Hệ thống khí nóng tiết kiệm năng lượng."),
                   ("Kiểm soát chính xác", "Nhiệt độ và lưu lượng gió được kiểm soát chính xác."),
                   ("Thiết kế bền bỉ", "Dễ vận hành, dễ bảo trì."),
                   ("Chất lượng ổn định", "Phù hợp mẻ rang chuyên nghiệp, kết quả đồng đều.")],
         uses=["Quán cà phê quy mô vừa", "Người rang chuyên nghiệp cần độ chính xác", "Sản xuất cà phê đặc sản"],
         gallery=[("a231", "OTL-03 màu trắng"), ("a233", "OTL-03 tại xưởng rang"), ("a238", "OTL-03 nhìn ngang"),
                  ("a254", "OTL-03 và khay làm nguội")]),
    dict(slug="otl-06", name="OTL-06", kind="Máy rang cà phê", hero="ref", mode="a", wash=True,
         tagline="Dành cho người rang chuyên nghiệp.", tag="Chủ lực",
         lead="Chắc chắn, hiện đại, đồng đều qua từng mẻ.",
         intro="OTL-06 kết hợp công nghệ tiên tiến với kết cấu chắc chắn, đáp ứng mọi nhu cầu rang chuyên nghiệp. "
               "Máy được tối ưu để tiết kiệm năng lượng và vận hành hiệu quả cao nhất.",
         batch="2–6", kgh="8–24", burner="15", elec="2,8", power="1 pha 200–240 V · 50/60 Hz",
         dims=["2150 × 1200 × 2020 (V1)", "2200 × 1200 × 1900 (V2)"],
         features=[("Hệ thống khí nóng mạnh", "Cung cấp nhiệt đều và ổn định suốt mẻ rang."),
                   ("Kiểm soát chính xác", "Dễ dàng điều chỉnh nhiệt độ và lưu lượng gió."),
                   ("Thiết kế bền bỉ", "Vật liệu cao cấp, kết cấu chắc chắn."),
                   ("Tối ưu năng lượng", "Hiệu suất cao, tiết kiệm chi phí vận hành.")],
         uses=["Cơ sở rang quy mô vừa và lớn", "Người rang cần chất lượng ổn định", "Dây chuyền cà phê đặc sản quy mô lớn"],
         gallery=[("a13", "OTL-06 màu trắng và inox"), ("a277", "OTL-06 tại nhà máy"),
                  ("a0", "OTL-06 cùng máy tách đá"), ("a280", "Màn hình cảm ứng và trống rang OTL-06")]),
    dict(slug="otl-12", name="OTL-12", kind="Máy rang cà phê", hero="a144", mode="r", wash=False,
         tagline="Gấp đôi mẻ. Vẫn chính xác.", tag="",
         lead="Công suất lớn cho nhu cầu sản xuất cao.",
         intro="OTL-12 được thiết kế cho sản xuất cà phê thương mại quy mô lớn. Hệ thống điều khiển thông minh và các tính năng "
               "hiện đại mang lại độ đồng nhất và hiệu quả cho từng mẻ rang.",
         batch="4–12", kgh="20–48", burner="40", elec="4", power="1 pha 200–240 V · 50/60 Hz",
         dims=["2600 × 1050 × 2000"],
         features=[("Hệ thống điều khiển tiên tiến", "Quản lý chính xác nhiệt độ và luồng gió cho từng mẻ."),
                   ("Công nghệ tiết kiệm năng lượng", "Hiệu suất cao, tiêu thụ năng lượng thấp."),
                   ("Thiết kế bền bỉ", "Vật liệu chất lượng cao, phù hợp vận hành liên tục."),
                   ("Công suất lớn", "Đáp ứng nhu cầu rang lớn với độ đồng nhất vượt trội.")],
         uses=["Nhà rang quy mô lớn, nhà sản xuất thương mại", "Thương hiệu cần chất lượng ổn định từng mẻ", "Rang cà phê đặc sản số lượng lớn"],
         gallery=[("a146", "OTL-12 tại xưởng rang"), ("a257", "Mặt trước OTL-12"), ("a148", "Đường cong rang trên màn hình cảm ứng"),
                  ("a153", "Cửa trống và tay cầm")]),
    dict(slug="otl-15", name="OTL-15", kind="Máy rang cà phê", hero="a107", mode="r", wash=False,
         tagline="Sản lượng lớn, vẫn ổn định.", tag="",
         lead="Công nghệ tiên tiến cho sản lượng lớn.",
         intro="OTL-15 kết hợp công nghệ tiên tiến với thiết kế thẩm mỹ, phù hợp doanh nghiệp cà phê lớn. "
               "Máy được tối ưu cho hiệu suất cao, tiết kiệm năng lượng và bền bỉ lâu dài.",
         batch="5–15", kgh="20–60", burner="40", elec="4", power="1 pha 200–240 V · 50/60 Hz",
         dims=["2500 × 1050 × 1900"],
         features=[("Điều khiển tự động hoàn toàn", "Tối ưu quá trình rang với độ chính xác cao."),
                   ("Hiệu suất cao", "Sản lượng lớn, thời gian rang ngắn và đồng đều."),
                   ("Dễ sử dụng", "Giao diện dễ vận hành, dễ bảo trì."),
                   ("Vận hành sạch hơn", "Tích hợp công nghệ giảm khí thải, giữ môi trường làm việc sạch.")],
         uses=["Cơ sở sản xuất cà phê quy mô lớn", "Thương hiệu chú trọng chất lượng và hiệu quả", "Rang thương mại và đặc sản"],
         gallery=[("a106", "OTL-15 tại quán rang"), ("a109", "Khay làm nguội OTL-15"), ("a111", "Mặt trước OTL-15"),
                  ("a116", "OTL-15 và giá màn hình cảm ứng")]),
    dict(slug="otl-30", name="OTL-30", kind="Máy rang công nghiệp", hero="w30", mode="k", wash=False, dark=True,
         tagline="Sản lượng công nghiệp, tự động hoàn toàn.", tag="",
         lead="Tự động hoá và hiệu quả ở quy mô công nghiệp.",
         intro="OTL-30 xử lý sản lượng lớn với độ đồng nhất vượt trội — giải pháp cho các xưởng rang cần hiệu suất "
               "và chất lượng ở quy mô lớn.",
         batch="10–30", kgh="40–120", burner="60", elec="5,8", power="3 pha 380–400 V · 50/60 Hz",
         dims=["3570 × 1400 × 2400 (V1)", "3050 × 2300 × 2500 (V2)"],
         features=[("Tự động hoàn toàn", "Hồ sơ rang tuỳ chỉnh, chạy tự động."),
                   ("Màn hình cảm ứng", "Điều chỉnh theo thời gian thực, dễ thao tác."),
                   ("Kết cấu hạng nặng", "Linh kiện công nghiệp, thiết kế cho vận hành liên tục."),
                   ("Cyclone thu vỏ lụa", "Hệ thống cyclone thu gom vỏ lụa từ luồng khí thải.")],
         uses=["Vận hành quy mô lớn", "Lịch rang dày đặc", "Trung tâm sản xuất cần mở rộng"],
         gallery=[("a123", "Mặt trống và bảng điều khiển OTL-30"), ("a126", "Khay làm nguội đồng"),
                  ("a121", "Hạt rơi xuống khay làm nguội"), ("a125", "Cánh đảo khay làm nguội")]),
    dict(slug="otl-60", name="OTL-60", kind="Hệ thống rang công nghiệp", hero="h60", mode="p", wash=False, dark=True,
         tagline="Tuần hoàn khí toàn phần. Giảm tới 30% năng lượng.", tag="Tuần hoàn khí",
         lead="Luồng khí khép kín cho sản xuất công nghiệp.",
         intro="OTL-60 dùng hệ thống tuần hoàn khí toàn phần tiên tiến, mang lại hiệu quả, độ chính xác và trách nhiệm "
               "với môi trường — thiết kế cho cơ sở sản xuất quy mô lớn.",
         batch="30–60", kgh="120–240", burner="200", elec="17,5", power="3 pha 380–400 V · 50/60 Hz",
         dims=["6500 × 5400 × 3900"], system=True,
         features=[("Tuần hoàn khí toàn phần", "Hệ thống khép kín tái sử dụng khí thải, giảm lãng phí năng lượng."),
                   ("Giám sát 7 điểm nhiệt", "Bảy nhiệt độ quan trọng được theo dõi để chỉnh chính xác."),
                   ("Buồng đốt khói tích hợp", "Khí thải sạch ngay trong hệ thống."),
                   ("Cảm ứng và hồ sơ rang", "Dữ liệu thời gian thực, hồ sơ lập trình được cho mẻ đồng đều.")],
         uses=["Sản xuất cà phê quy mô công nghiệp", "Nhà rang chú trọng phát triển bền vững", "Sản lượng lớn, chất lượng cao"],
         gallery=[("h60", "OTL-60 và tủ điều khiển"), ("g60a", "Khay làm nguội và trống OTL-60"),
                  ("g60b", "Bảng điều khiển OTL-60"), ("g60c", "OTL-60 lắp tại xưởng rang")]),
    dict(slug="otl-120", name="OTL-120", kind="Hệ thống rang công nghiệp", hero="h120", mode="p", wash=False, dark=True,
         tagline="Tuần hoàn khí toàn phần, quy mô lớn nhất.", tag="Tuần hoàn khí",
         lead="120 kg mỗi mẻ với hệ thống khí tuần hoàn khép kín.",
         intro="OTL-120 đưa hệ thống tuần hoàn khí toàn phần lên 120 kg mỗi mẻ, thiết kế cho sản xuất quy mô lớn với khả năng "
               "kiểm soát quá trình rang vượt trội.",
         batch="60–120", kgh="240–480", burner="350", elec="19,5", power="3 pha 380–400 V · 50/60 Hz",
         dims=["6700 × 5500 × 4300"], system=True,
         features=[("Tuần hoàn khí toàn phần", "Hệ thống khép kín tái sử dụng khí thải, giảm lãng phí năng lượng."),
                   ("Giám sát 7 điểm nhiệt", "Bảy nhiệt độ quan trọng được theo dõi để chỉnh chính xác."),
                   ("Buồng đốt khói tích hợp", "Khí thải sạch ngay trong hệ thống."),
                   ("Kết cấu mô-đun", "Vật liệu cao cấp, thiết kế mô-đun giúp bảo trì và nâng cấp đơn giản.")],
         uses=["Sản xuất cà phê quy mô công nghiệp", "Nhà rang chú trọng phát triển bền vững", "Sản lượng lớn, chất lượng cao"],
         gallery=[("h120", "OTL-120 tại nhà máy khách hàng"), ("g120a", "OTL-120 và cyclone"),
                  ("g120b", "Trống rang và màn hình OTL-120")]),
]
SENSORS = [("Nhiệt độ hạt", "Theo dõi nhiệt độ khối hạt trong quá trình rang."), ("Khí thải", "Giữ luồng khí sạch và hiệu quả."),
           ("Làm nguội", "Làm nguội nhanh, giữ trọn hương vị."), ("Không khí đầu đốt", "Truyền nhiệt tối ưu."),
           ("Buồng đốt", "Nhiệt ổn định trong buồng trống."), ("Cyclone", "Thu vỏ lụa, lưu thông khí."),
           ("Buồng đốt khói", "Giai đoạn cuối làm sạch khí thải.")]

EQUIP = [
    dict(slug="destoner", name="Máy tách đá OD", short="Tách đá", kind="Thiết bị", hero="a179", mode="r",
         series="OD-05 · OD-15 · OD-30 · OD-60", tagline="Loại sạch đá. Giữ chất lượng.",
         lead="Tách đá và tạp chất nặng khỏi hạt cà phê rang.",
         intro="Máy tách đá OD loại bỏ đá và tạp chất nặng khỏi hạt cà phê rang bằng hệ thống hút khí điều chỉnh được, "
               "kỹ thuật chính xác, có cỡ phù hợp cho từng máy rang.",
         stats=[("5–40", "kg", "mỗi mẻ, OD-05 đến OD-30"), ("0,75–2,2", "kW", "công suất tiêu thụ"), ("4", "", "cỡ máy, bản V1 và V2"),
                ("Inox", "", "thép không gỉ thực phẩm")],
         specs=[("Vật liệu", "Thép không gỉ dùng trong thực phẩm"), ("Tách đá", "Hút khí điều chỉnh được"),
                ("Phiên bản", "V1 và V2 cho mỗi cỡ"), ("Dòng máy", "OD-05 · OD-15 · OD-30 · OD-60")],
         table=(("Mẫu máy", "Năng suất", "Công suất", "Nguồn điện"),
                [("OD-05", "5–10 kg/mẻ", "0,75 kW", "1 pha 220 V"), ("OD-15", "15–20 kg/mẻ", "1,5 kW", "1 pha 220 V"),
                 ("OD-30", "30–40 kg/mẻ", "2,2 kW", "3 pha 380 V"), ("OD-60", "Cho máy rang 60 kg", "Theo yêu cầu", "Theo yêu cầu")]),
         # mô hình 3D (máy chủ: DESTONER-OD-30-V1.glb 15,6 MB → nén Draco 1,9 MB bằng gltf-transform)
         model3d=("3d/od-30-v1.glb", "3d/od-30-v1_poster.jpg", "OD-30 V1", "1,9 MB"),
         features=[("Tách hiệu quả cao", "Hút khí tách chính xác đá và tạp chất nặng."),
                   ("Luồng gió tuỳ chỉnh", "Chỉnh gió theo mật độ từng loại hạt."),
                   ("Điều khiển đơn giản", "Nút điều khiển trực quan, thao tác dễ."),
                   ("Thân inox", "Bền, dễ vệ sinh, gọn chỗ đặt.")],
         gallery=[("a189", "Máy tách đá OD màu trắng"), ("a37", "Máy tách đá OD"), ("a186", "Máy tách đá OD tại nhà máy"),
                  ("a190", "Máy tách đá OD nhìn ngang")]),
    dict(slug="afterburner", name="Buồng đốt khói AB", short="Xử lý khói", kind="Thiết bị", hero="a182", mode="r",
         series="AB-15 · AB-30 · AB-60 · AB-120", tagline="Khí sạch, từ thiết kế.",
         lead="Xử lý khói và mùi sinh ra khi rang công nghiệp.",
         intro="Buồng đốt khói xử lý khói và mùi trong quá trình rang công nghiệp, giúp xưởng rang giữ môi trường sạch "
               "và hỗ trợ giảm khói, mùi trong khí thải.",
         stats=[("15–30", "kg", "máy rang phục vụ (AB-30)"), ("12–70", "kW", "công suất nhiệt"), ("2", "", "cấp đầu đốt"),
                ("4", "", "cỡ, AB-15 đến AB-120")],
         specs=[("Đầu đốt", "Ecoflam (Ý), 2 cấp"), ("Bộ điều khiển nhiệt", "Delta"), ("Cảm biến nhiệt", "Omron (Nhật Bản)"),
                ("Nhiệt độ vận hành", "Tới 600 °C (AB-60)"), ("Công nghệ", "Buồng đốt hiệu suất cao, đốt lại hợp chất bay hơi và bụi"),
                ("Vật liệu", "Thép, sơn tĩnh điện"), ("Dòng máy", "AB-15 · AB-30 · AB-60 · AB-120")],
         table=(("Mẫu máy", "Dùng cho máy rang", "Nhiệt / kết nối", "Kích thước D × R × C"),
                [("AB-15", "Tới 15 kg", "Theo yêu cầu", "Theo yêu cầu"), ("AB-30", "15–30 kg", "12–70 kW", "Theo yêu cầu"),
                 ("AB-60", "Tới 60 kg", "Vào Ø250 · ra Ø310 mm", "1452 × 700 × 934 mm"), ("AB-120", "Tới 120 kg", "Theo yêu cầu", "Theo yêu cầu")]),
         features=[("Giảm khói mạnh", "Giảm đáng kể khói và mùi."),
                   ("Thân thiện môi trường", "Hỗ trợ giảm khói và mùi trong khí thải của xưởng rang."),
                   ("Dễ tích hợp", "Tối ưu cho máy rang OTL và các máy tương thích."),
                   ("Sản xuất tại Việt Nam", "Thiết kế và chế tạo với kiểm soát chất lượng nghiêm ngặt.")],
         gallery=[("a26", "Bản vẽ buồng đốt khói AB"), ("a180", "Buồng đốt khói AB, đặt đứng"), ("a181", "Buồng đốt khói AB trên giá")]),
    dict(slug="silo", name="Silo OTL", short="Silo", kind="Thiết bị", hero="a73", mode="r",
         series="Cụm silo mô-đun", tagline="Mở rộng dung tích theo nhu cầu.",
         lead="Lưu trữ mô-đun cho cà phê nhân và cà phê rang.",
         intro="Hệ thống silo OTL mở rộng bằng cách thêm cụm silo khi nhu cầu lưu trữ tăng, với cấu hình theo cách bạn "
               "vận hành và loại hạt bạn bảo quản.",
         stats=[("Mô-đun", "", "thêm cụm khi cần"), ("Kín khí", "", "chống ẩm, chống bẩn"),
                ("Tự động", "", "hệ thống băng tải"), ("Tuỳ chỉnh", "", "kích thước, dung tích")],
         specs=[("Thiết kế", "Cụm silo mô-đun, mở rộng được"), ("Lưu trữ", "Cà phê nhân và cà phê rang"),
                ("Vận chuyển", "Băng tải tự động, van xả điều chỉnh"), ("Vật liệu", "Thép không gỉ cao cấp"),
                ("Kích thước", "Từ xưởng thủ công đến cụm silo công nghiệp")],
         features=[("Mô-đun linh hoạt", "Tăng dung tích bằng cách thêm cụm silo."),
                   ("Lưu trữ kín khí", "Chống ẩm, chống nhiễm bẩn; tách riêng hạt nhân và hạt rang."),
                   ("Băng tải tiên tiến", "Vận chuyển tự động, xả liệu chính xác, giảm thao tác tay."),
                   ("Thiết kế theo yêu cầu", "Thiết kế riêng theo nhu cầu cụ thể của từng khách hàng.")],
         gallery=[("a72", "Silo OTL tại xưởng rang"), ("a78", "Cụm silo"), ("a220", "Cụm silo tại nhà máy"),
                  ("a71", "Silo tại quán cà phê")]),
    dict(slug="cyclone", name="Cyclone rời", short="Cyclone", kind="Thiết bị", hero="cyc", mode="r",
         series="Phụ kiện cho OTL-06", tagline="Tách vỏ lụa bên ngoài máy rang.",
         lead="Đưa việc thu vỏ lụa ra ngoài máy rang.",
         intro="Cyclone rời là phụ kiện thông minh cho máy rang OTL: vỏ lụa được tách khỏi khí thải bên ngoài máy và gom vào "
               "thùng tháo rời, giúp máy rang sạch lâu hơn, bảo trì dễ hơn.",
         stats=[("1950", "mm", "chiều cao"), ("Ø400", "mm", "đường kính"), ("0,75", "kW", "công suất tiêu thụ"), ("220", "V", "50/60 Hz")],
         specs=[("Chiều cao", "1950 mm"), ("Đường kính", "Ø400 mm"), ("Công suất tiêu thụ", "0,75 kW"), ("Điện áp", "220 V · 50/60 Hz"),
                ("Cổng vào / ra", "Lắp vừa dòng máy rang OTL"), ("Vật liệu", "Thép công nghiệp sơn tĩnh điện")],
         features=[("Bảo trì dễ", "Không còn phải mở cửa cyclone trong máy để lấy vỏ lụa sau mỗi mẻ."),
                   ("Tách sạch", "Vỏ lụa tách khỏi khí thải, gom vào thùng tháo rời."),
                   ("Đổ nhanh", "Tháo thùng, đổ, rang tiếp."),
                   ("Làm việc gọn hơn", "Ít thời gian dọn, nhiều thời gian rang.")],
         gallery=[]),
]

MODE_OF = {x["hero"]: x["mode"] for x in ROASTERS + EQUIP}   # ảnh nhỏ phải xử lý theo đúng kiểu ảnh gốc
_CIRC_VI = [(">Burner<", ">Lò đốt<"), (">Drum<", ">Trống rang<"), (">Chaff cyclone<", ">Cyclone vỏ lụa<"), (">Fan<", ">Quạt<"),
            (">Afterburner<", ">Đốt khói<"), (">Cooling tray<", ">Khay làm nguội<"), (">Clean exhaust<", ">Khí sạch ra<"),
            (">Recirculated hot air returns to the burner<", ">Khí nóng tuần hoàn trở về lò đốt<"), (">Cooling air<", ">Gió làm nguội<"),
            ("Simplified schematic of the OTL full-circulation airflow with seven temperature points",
             "Sơ đồ đơn giản hệ thống tuần hoàn khí toàn phần OTL với bảy điểm đo nhiệt")]
CIRC = (HERE / "circulation.svg").read_text(encoding="utf-8")   # sơ đồ tuần hoàn khí, đánh số 7 điểm nhiệt theo SENSORS
for _a, _b in _CIRC_VI: CIRC = CIRC.replace(_a, _b)

# ======================================================================= khung trang
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">')
MOTION = {"preset": {"d": 24, "dur": 850, "ease": "cubic-bezier(.2,.7,.2,1)", "stagger": 70, "each": 30, "cover": "#f5f5f7"},
          "rules": [[".rv", "rise", {"d": 26}], [".rv-up", "rise", {"d": 56, "dur": 1150}], [".rv-f", "fade", {"dur": 1100}],
                    [".stats>div", "rise", {"d": 20}], [".fc", "rise", {"d": 24}], [".tile", "rise", {"d": 30}],
                    [".step", "rise", {"d": 24}], [".strip", "rise", {"d": 18}], [".rail", "rise", {"d": 30}],
                    [".grid3 .lc", "rise", {"d": 26}], [".cmp-col", "rise", {"d": 22}], [".uses li", "rise", {"d": 14}],
                    [".sensors li", "rise", {"d": 14}], [".tl-item", "rise", {"d": 22}]]}

# chọn giao diện TRƯỚC khi vẽ (không nháy trắng): đã bấm nút thì theo lựa chọn đã lưu, chưa bấm thì theo máy người xem
THEME_JS = ("<script>(function(){var d=document.documentElement,k='otl-theme',s=null,m=matchMedia('(prefers-color-scheme: dark)');"
            "try{s=localStorage.getItem(k)}catch(e){}function a(){d.dataset.theme=s||(m.matches?'dark':'light')}a();"
            "if(m.addEventListener)m.addEventListener('change',function(){if(!s)a()});"
            "window.OTLTheme={toggle:function(){s=d.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem(k,s)}catch(e){}a();return s}}})()</script>")
THEME_BTN = ('<button class="theme" type="button" data-theme-toggle aria-label="Chuyển sang giao diện tối">'
             '<svg class="moon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>'
             '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
             '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>')
WHITE = {"ref", "c240", "w30"}   # máy trắng: nền tối KHÔNG cần tấm sáng phía sau

def V(name):
    """Mã phiên bản theo nội dung file → đổi file là đổi đường dẫn (GitHub Pages cho trình duyệt giữ CSS/JS 10 phút)."""
    import hashlib
    return f"{name}?v={hashlib.md5((HERE / name).read_bytes()).hexdigest()[:8]}"

def VI(name):
    """Mã phiên bản cho ẢNH trong img/ (logo đổi mà trình duyệt giữ ảnh cũ 10 phút — Thành thấy logo lỗi 23/10)."""
    import hashlib
    return hashlib.md5((IMG / name).read_bytes()).hexdigest()[:8]

def head(title, desc, gallery_keys=()):
    imgs = {k: img(k, m) for k, m in gallery_keys}
    return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="color-scheme" content="light dark">{THEME_JS}{FONT}'
            f'<link rel="stylesheet" href="{V("site.css")}"><link rel="icon" href="img/icon.png">'
            f'<script>window.IMGS={json.dumps(imgs)}</script><script src="{V("motion.js")}"></script>'
            f'<script>OTLM.start({json.dumps(MOTION)})</script></head><body>')

def nav(active="", dk=False):
    def top(href, label, key):
        return f'<a class="top{" on" if key == active else ""}" href="{href}">{label}</a>'
    models = "".join(f'<a href="{r["slug"]}.html">{thumb(r)}<span>{r["name"]}</span></a>' for r in ROASTERS)
    eq = "".join(f'<a href="{e["slug"]}.html">{im_tag(e["hero"], "t", e["name"])}<span>{e["short"]}</span></a>' for e in EQUIP)
    m_models = "".join(f'<a class="sm" href="{r["slug"]}.html">{r["name"]}</a>' for r in ROASTERS)
    return f'''<header class="gnav{" dk" if dk else ""}"><div class="in">
<a class="logo" href="index.html" aria-label="Trang chủ OTL Roaster"><img class="lg-l" src="{img_logo()}?v={VI('logo.png')}" alt="OTL Roaster" width="85" height="22"><img class="lg-d" src="img/logo_dark.png?v={VI('logo_dark.png')}" alt="OTL Roaster" width="85" height="22"></a>
<ul>
<li>{top("roasters.html", "Máy rang", "roasters")}<div class="fly"><div class="in"><div class="big"><h4>Khám phá máy rang</h4>
<a href="roasters.html">Tất cả máy rang</a><a href="compare.html">So sánh</a><a href="quote.html">Nhận báo giá</a></div>
<div><h4>Các mẫu máy</h4><div class="models">{models}</div></div></div></div></li>
<li>{top("equipment.html", "Thiết bị", "equipment")}<div class="fly"><div class="in"><div class="big"><h4>Hoàn thiện dây chuyền</h4>
<a href="equipment.html">Tất cả thiết bị</a><a href="solutions.html">Giải pháp công nghiệp</a></div>
<div><h4>Thiết bị</h4><div class="models">{eq}</div></div></div></div></li>
<li>{top("solutions.html", "Giải pháp", "solutions")}</li>
<li>{top("compare.html", "So sánh", "compare")}</li>
<li>{top("support.html", "Hỗ trợ", "support")}</li>
<li>{top("about.html", "Về OTL", "about")}</li>
</ul>
<a class="btn btn-f sm cta" href="quote.html">Nhận báo giá</a>
{THEME_BTN}<button class="burger" type="button" aria-label="Menu" aria-expanded="false"><i></i><i></i></button>
</div></header>
<div class="mnav" hidden><button class="mnav-x" type="button" aria-label="Đóng menu">&times;</button>
<a href="roasters.html">Máy rang</a>{m_models}
<a href="equipment.html">Thiết bị</a><a href="solutions.html">Giải pháp</a><a href="compare.html">So sánh</a>
<a href="support.html">Hỗ trợ</a><a href="about.html">Về OTL</a><a href="quote.html">Nhận báo giá</a>
<button class="theme-t" type="button" data-theme-toggle>Giao diện tối</button></div>'''

def img_logo():
    path = IMG / "logo.png"
    if not path.exists():
        IMG.mkdir(parents=True, exist_ok=True)
        im = _cut(Image.open(_src("a2")))
        # chữ "OTL ROASTER" trong logo gốc màu trắng → đổi màu chữ, giữ nguyên biểu tượng đỏ-xanh bên trái.
        # Ranh giới = cột trong suốt hoàn toàn ĐẦU TIÊN sau biểu tượng (đoán theo tỉ lệ cũ cắt lẹm mép phải biểu tượng).
        al = im.getchannel("A")
        filled = [any(al.getpixel((x, y)) > 8 for y in range(im.height)) for x in range(im.width)]
        ic_w = next(x for x in range(1, im.width) if filled[x - 1] and not filled[x])
        def recolor(src, rgb):
            out = src.copy(); px = out.load()
            for y in range(out.height):
                for x in range(ic_w, out.width):
                    if px[x, y][3]: px[x, y] = rgb + (px[x, y][3],)
            out.thumbnail((400, 66), Image.LANCZOS)
            return out
        recolor(im, (61, 67, 77)).save(path, optimize=True)                # nền sáng: chữ xám than
        recolor(im, (232, 232, 237)).save(IMG / "logo_dark.png", optimize=True)   # nền tối: chữ sáng
        ic = _cut(Image.open(_src("a1"))); ic.thumbnail((180, 180), Image.LANCZOS); ic.save(IMG / "icon.png", optimize=True)
    return "img/logo.png"

def thumb(r):
    return SYS_ICON if r.get("system") else im_tag(r["hero"], "t", r["name"])

def hero_img(r, lazy=False):
    return im_tag(r["hero"], r["mode"], r["name"], lazy=lazy)

def card_img(r):
    if r.get("system"):   # ảnh thật trong thẻ: cắt khung cho đầy ô
        return im_tag(r["hero"], "p", r["name"], cls="ph-card")
    return im_tag(r["hero"], r["mode"], r["name"])

# Liên hệ nhanh + chat: có trên otlpro.com hiện tại (form + nút WhatsApp) — trình bày lại kiểu Apple.
WA = "https://wa.me/84936198938"
WA_SVG = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="#25d366" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/>'
          '<path fill="#fff" d="M16.9 14.3c-.3-.1-1.6-.8-1.8-.9-.3-.1-.4-.1-.6.1l-.8 1c-.2.2-.3.2-.6.1-1.6-.8-2.7-1.5-3.8-3.3-.3-.5.3-.5.8-1.6.1-.2 0-.3 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.3.3-1 1-1 2.3s1 2.7 1.2 2.9c.1.2 2 3.1 4.9 4.3 1.8.8 2.5.8 3.4.7.6-.1 1.6-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.3-.6-.4z"/></svg>')
# Facebook / Instagram / TikTok lấy từ chân trang otlpro.com; YouTube trên otlpro.com (@otesla577) HỎNG 404 → kênh đúng @otlroaster;
# Threads cùng tên Instagram; Zalo theo số hotline (máy tính hiện QR); Messenger theo mã trang Facebook.
ZALO = "https://zalo.me/0936198938"
MSGR = "https://m.me/61571855303133"
SOCIAL = [
    ("Facebook", "https://www.facebook.com/profile.php?id=61571855303133",
     '<path d="M14 8.5V7c0-.6.4-1 1-1h2V2.5h-2.8C11.6 2.5 10 4.2 10 6.7v1.8H7.5V12H10v9.5h4V12h2.7l.5-3.5z" fill="currentColor"/>'),
    ("Instagram", "https://www.instagram.com/o_tesla_roaster/",
     '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.2" cy="6.8" r="1.2" fill="currentColor"/>'),
    ("Threads", "https://www.threads.net/@o_tesla_roaster",   # biểu tượng theo Simple Icons (CC0)
     '<path fill="currentColor" d="M12.19 24h-.01c-3.58-.02-6.33-1.2-8.18-3.51C2.35 18.44 1.5 15.59 1.47 12.01v-.02c.03-3.58.88-6.43 2.53-8.48C5.85 1.2 8.6.02 12.18 0h.01c2.75.02 5.04.73 6.83 2.1 1.68 1.29 2.86 3.13 3.51 5.47l-2.04.57c-1.1-3.96-3.9-5.98-8.3-6.02-2.91.02-5.11.94-6.54 2.72C4.31 6.5 3.62 8.91 3.59 12c.03 3.09.72 5.5 2.06 7.16 1.43 1.78 3.63 2.7 6.54 2.72 2.62-.02 4.36-.63 5.8-2.05 1.65-1.61 1.62-3.59 1.09-4.8-.31-.71-.87-1.3-1.63-1.75-.19 1.35-.62 2.45-1.28 3.27-.89 1.1-2.14 1.7-3.73 1.79-1.2.07-2.36-.22-3.26-.8-1.06-.69-1.69-1.74-1.75-2.96-.07-1.19.41-2.29 1.33-3.08.88-.76 2.12-1.21 3.58-1.29a13.85 13.85 0 0 1 3.02.14c-.13-.74-.38-1.33-.75-1.76-.51-.59-1.31-.88-2.36-.89h-.03c-.84 0-1.99.23-2.72 1.32L7.73 7.85c.98-1.45 2.57-2.26 4.48-2.26h.04c3.2.02 5.1 1.98 5.29 5.39.11.05.22.09.32.14 1.49.7 2.58 1.76 3.15 3.07.8 1.82.87 4.79-1.55 7.16-1.85 1.81-4.09 2.63-7.28 2.65zm1-11.69c-.24 0-.49.01-.74.02-1.84.1-2.98.95-2.92 2.14.07 1.26 1.45 1.84 2.78 1.77 1.22-.07 2.82-.54 3.09-3.71a10.5 10.5 0 0 0-2.21-.22z"/>'),
    ("YouTube", "https://www.youtube.com/@otlroaster",
     '<rect x="2.5" y="5.5" width="19" height="13" rx="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.2v5.6l4.8-2.8z" fill="currentColor"/>'),
    ("TikTok", "https://www.tiktok.com/@o_tesla_roaster",
     '<path d="M14 3.5v11.2a3.3 3.3 0 1 1-3.3-3.3M14 3.5c.4 2.4 2 4 4.5 4.2" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>'),
]
ZALO_SVG = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="6" fill="#0068ff"/>'
            '<path d="M7.5 8.2h8.2l-7.4 7.6h8" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
MSGR_SVG = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="#0084ff" d="M12 2C6.4 2 2 6.1 2 11.6c0 2.9 1.2 5.4 3.2 7.1V22l3-1.7c1.2.3 2.4.5 3.8.5 5.6 0 10-4.1 10-9.6S17.6 2 12 2z"/>'
            '<path fill="#fff" d="M6.4 14.3l3-4.7 2.4 1.9 3.3-1.9-3 4.7-2.4-1.9z"/></svg>')
COPY_SVG = ('<svg class="i-copy" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2.5" '
            'fill="none" stroke="currentColor" stroke-width="1.9"/><path d="M16 8V6.5A2.5 2.5 0 0 0 13.5 4h-7A2.5 2.5 0 0 0 4 6.5v7A2.5 2.5 0 0 0 6.5 16H8" '
            'fill="none" stroke="currentColor" stroke-width="1.9"/></svg>'
            '<svg class="i-ok" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" '
            'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def copy_btn(value, what, label="Sao chép"):
    """Nút "Sao chép" có chữ + biểu tượng; bấm xong đổi "Đã chép" (tô cả nút) rồi tự trở lại."""
    return f'<button type="button" class="copy" data-copy="{E(value)}" aria-label="Sao chép {E(what)}">{COPY_SVG}<span>{label}</span></button>'

PHONE, EMAIL = "+84 936 198 938", "otlpro.com@gmail.com"
OFFICE = "Số 44, Đường N5, KP Tân Phước, P. Tân Bình, TP Dĩ An, Bình Dương"
FACTORY = "398/33 ĐT743B, Ấp Đông Thành, P. Tân Đông Hiệp, TP Dĩ An, Bình Dương"
ALL_INFO = ("Công ty TNHH Công Nghiệp OTL (OTL Roaster)\nĐiện thoại / WhatsApp / Zalo: " + PHONE + "\nEmail: " + EMAIL
            + "\nVăn phòng: " + OFFICE + "\nNhà máy: " + FACTORY + "\nWebsite: www.otlpro.com")

def zalo_qr_svg():
    """Mã QR của link Zalo (số hotline). Trên máy tính zalo.me/<số> bắt đăng nhập (tài khoản cá nhân, chưa có Zalo OA)
    → hiện QR để khách quét bằng app Zalo trên điện thoại."""
    import qrcode
    q = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(ZALO); q.make(fit=True)
    m = q.get_matrix(); n = len(m)
    d = "".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return (f'<svg viewBox="0 0 {n} {n}" width="168" height="168" shape-rendering="crispEdges" role="img" aria-label="Mã QR Zalo">'
            f'<rect width="{n}" height="{n}" fill="#fff"/><path d="{d}" fill="#1b1d21"/></svg>')

CHATS = [("WhatsApp", WA, WA_SVG), ("Zalo", ZALO, ZALO_SVG), ("Messenger", MSGR, MSGR_SVG)]
CHAT_BTN = ('<div class="chat"><div class="chat-p" id="chat-p" hidden><p>Nhắn tin với OTL</p>'
            + "".join(f'<a href="{u}" target="_blank" rel="noopener"{" data-zalo" if n == "Zalo" else ""}>{s}<span>{n}</span></a>' for n, u, s in CHATS)
            + f'<div class="zqr" hidden>{zalo_qr_svg()}<p>Quét bằng Zalo trên điện thoại<br><b>{PHONE}</b></p>{copy_btn(PHONE, "số điện thoại")}</div>'
            + f'<div class="chat-copy"><span>{PHONE}</span>{copy_btn(PHONE, "số điện thoại")}</div>'
            + f'<div class="chat-copy"><span>{EMAIL}</span>{copy_btn(EMAIL, "email")}</div>'
            + '</div><button class="chat-b" type="button" aria-expanded="false" aria-controls="chat-p">'
            '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 5.5h16v10H9l-5 4z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/></svg>'
            '<span>Nhắn tin</span></button></div>')
FOLLOW = ('<div class="follow"><span>Theo dõi OTL</span>'
          + "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="OTL trên {n}"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">{p}</svg></a>'
                    for n, u, p in SOCIAL) + '</div>')

# Video Shorts của kênh @otlroaster (chọn 5/9). Bấm mới nạp YouTube.
SHORTS = [("fkA0S2HNY0E", "Cà phê nhân vào phễu"), ("2vsMH8x4P9U", "Rang theo hồ sơ đã lưu"),
          ("_slyMbj3dDc", "Máy rang mẻ nhỏ"), ("8lh8zY4CeUo", "Cà phê mỗi ngày"),
          ("Syhw4mr3PK0", "Kỹ sư tại nhà máy")]

def short_poster(vid):
    """Ảnh bìa dọc 9:16 tải từ YouTube (oar2 nếu có, không thì frame0), cắt giữa, lưu img/yt_<mã>.jpg."""
    path = IMG / f"yt_{vid}.jpg"
    if not path.exists():
        import io, urllib.request
        for n in ("oar2.jpg", "frame0.jpg"):
            try:
                data = urllib.request.urlopen(urllib.request.Request(f"https://i.ytimg.com/vi/{vid}/{n}", headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read()
                break
            except Exception:
                data = None
        im = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = im.size; tw = round(h * 9 / 16)
        if tw < w: im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
        im.thumbnail((540, 960), Image.LANCZOS); im.save(path, "JPEG", quality=80, optimize=True, progressive=True)
    return f"img/yt_{vid}.jpg"

def shorts_section(bg="bg-w"):
    cards = "".join(f'''<figure class="short"><button type="button" data-yt="{v}" aria-label="Xem video: {E(t)}">
<img src="{short_poster(v)}" alt="" loading="lazy" decoding="async"><span class="play" aria-hidden="true"></span></button>
<figcaption>{E(t)}</figcaption></figure>''' for v, t in SHORTS)
    return f'''<section class="sec {bg}" id="videos"><div class="wrap rail-head"><h2 class="h-l rv">Xem OTL làm việc.</h2>
<a class="lnk rv" href="https://www.youtube.com/@otlroaster/shorts" target="_blank" rel="noopener">Xem thêm trên YouTube</a></div>
<div class="wrap"><div class="shorts rv">{cards}</div></div></section>'''

ALL_BTN = copy_btn(ALL_INFO, "toàn bộ thông tin liên hệ", "Sao chép toàn bộ thông tin liên hệ")
CONTACT = f'''<section class="sec bg-c" id="contact"><div class="wrap contact">
<div><h2 class="h-xl rv">Trò chuyện với OTL.</h2>
<p class="lead rv" style="margin-top:14px">Cần tư vấn máy rang, báo giá hay dịch vụ? Để lại thông tin, đội ngũ OTL sẽ liên hệ lại với bạn.</p>
<ul class="ct-ways rv"><li><a class="lnk" href="{WA}" target="_blank" rel="noopener">Nhắn qua WhatsApp</a></li>
<li><a class="lnk" href="{ZALO}" target="_blank" rel="noopener" data-zalo>Nhắn qua Zalo</a></li><li><a class="lnk" href="{MSGR}" target="_blank" rel="noopener">Nhắn qua Facebook</a></li>
<li><a class="lnk" href="mailto:{EMAIL}">{EMAIL}</a>{copy_btn(EMAIL, "email")}</li>
<li><a class="lnk" href="tel:+84936198938">{PHONE}</a>{copy_btn(PHONE, "số điện thoại")}</li>
<li>{ALL_BTN}</li></ul></div>
<form class="form ct-f rv" data-demo data-ok="Cảm ơn bạn — bản demo, chưa gửi đi đâu." novalidate>
<div class="full"><label for="h-name">Tên của bạn</label><input id="h-name" autocomplete="name"></div>
<div><label for="h-mail">Email *</label><input id="h-mail" type="email" required autocomplete="email"></div>
<div><label for="h-phone">Số điện thoại *</label><input id="h-phone" type="tel" required autocomplete="tel"></div>
<div class="full"><label for="h-msg">Tin nhắn của bạn *</label><textarea id="h-msg" required></textarea></div>
<div class="btns"><button class="btn btn-f" type="submit">Gửi tin nhắn</button><a class="lnk" href="quote.html">Gửi yêu cầu báo giá đầy đủ</a></div></form>
</div></section>'''

def foot():
    rl = "".join(f'<li><a href="{r["slug"]}.html">{r["name"]}</a></li>' for r in ROASTERS)
    el = "".join(f'<li><a href="{e["slug"]}.html">{e["name"]}</a></li>' for e in EQUIP)
    return f'''<footer class="foot"><div class="wrap">
<p class="note">Thông số trên trang lấy từ trang sản phẩm otlpro.com và brochure OTL. Bản thiết kế demo để duyệt — biểu mẫu chưa gửi dữ liệu.</p>
<div class="cols">
<div><h4>Máy rang</h4><ul>{rl}<li><a href="compare.html">So sánh mẫu máy</a></li></ul></div>
<div><h4>Thiết bị</h4><ul>{el}<li><a href="equipment.html">Tất cả thiết bị</a></li></ul></div>
<div><h4>Giải pháp</h4><ul><li><a href="solutions.html">Giải pháp công nghiệp</a></li><li><a href="solutions.html#circulation">Tuần hoàn khí toàn phần</a></li><li><a href="solutions.html#profiles">Hồ sơ rang</a></li></ul></div>
<div><h4>Hỗ trợ</h4><ul><li><a href="support.html">Hỗ trợ và dịch vụ</a></li><li><a href="support.html#contact">Liên hệ</a></li><li><a href="quote.html">Nhận báo giá</a></li></ul></div>
<div><h4>OTL</h4><ul><li><a href="about.html">Về OTL</a></li><li><a href="about.html#lo-trinh">Lộ trình</a></li><li><a href="index.html">Trang chủ</a></li><li><a href="../index.html">Tất cả phương án thiết kế</a></li></ul></div>
</div>
{FOLLOW}
<div class="fine"><span>© 2026 Công ty TNHH Công Nghiệp OTL. Bảo lưu mọi quyền.</span><span>otlpro.com — bản thiết kế demo</span></div>
</div></footer>
{CHAT_BTN}<script src="{V("site.js")}"></script></body></html>'''

def cta(title, text, primary=("Nhận báo giá", "quote.html"), secondary=("So sánh mẫu máy", "compare.html"), bg="bg-c"):
    return f'''<section class="sec {bg} cta-band"><div class="wrap">
<h2 class="h-xl rv">{title}</h2><p class="lead measure rv" style="margin-top:14px">{text}</p>
<div class="btns rv"><a class="btn btn-f" href="{primary[1]}">{primary[0]}</a><a class="btn btn-o" href="{secondary[1]}">{secondary[0]}</a></div>
</div></section>'''

def strip(items, active=""):
    out = []
    for it in items:
        em = f'<em>{it["tag"]}</em>' if it.get("tag") else ""
        out.append(f'<a href="{it["href"]}"><div class="ic">{it["icon"]}</div><span>{it["label"]}{em}</span></a>')
    return f'<div class="strip" role="list">{"".join(out)}</div>'

CUSTOM = "Hệ thống theo yêu cầu, tới 500 kg"   # trên 120 kg: chưa có model + thông số công khai → chỉ "làm theo yêu cầu", không bịa số
QCUSTOM = "quote.html?model=" + _q(CUSTOM)

def qlink(name):
    return "quote.html?model=" + _q(name)

def roaster_items():
    return [dict(href=f'{r["slug"]}.html', icon=thumb(r), label=r["name"], tag=r["tag"]) for r in ROASTERS] + \
           [dict(href=QCUSTOM, icon=SYS_ICON, label="Tới 500 kg", tag="Theo yêu cầu")]

def equip_items():
    return [dict(href=f'{e["slug"]}.html', icon=im_tag(e["hero"], "t", e["name"]), label=e["short"]) for e in EQUIP]

def lc(r):
    tag = f'<div class="tag">{r["tag"]}</div>' if r["tag"] else '<div class="tag"></div>'
    return f'''<article class="lc"><a class="im" href="{r["slug"]}.html" aria-label="{r["name"]}">{card_img(r)}</a>{tag}
<h3>{r["name"]}</h3><p>{r["tagline"]}</p>
<dl><div><dt>Mỗi mẻ</dt><dd>{r["batch"]} kg</dd></div><div><dt>Năng suất</dt><dd>{r["kgh"]} kg/giờ</dd></div></dl>
<div class="btns"><a class="btn btn-f sm" href="{r["slug"]}.html">Tìm hiểu thêm</a><a class="lnk" href="{qlink(r["name"])}">Báo giá</a></div></article>'''

def lc_custom():
    return f'''<article class="lc"><a class="im" href="{QCUSTOM}" aria-label="Hệ thống theo yêu cầu tới 500 kg">{SYS_ICON.replace('width="114" height="76"', 'width="300" height="200"')}</a>
<div class="tag">Theo yêu cầu</div><h3>Tới 500 kg</h3><p>Hệ thống công nghiệp lớn, thiết kế theo nhà máy của bạn.</p>
<dl><div><dt>Mỗi mẻ</dt><dd>Tới 500 kg</dd></div><div><dt>Năng suất</dt><dd>Theo yêu cầu</dd></div></dl>
<div class="btns"><a class="btn btn-f sm" href="{QCUSTOM}">Nhận báo giá</a><a class="lnk" href="support.html#contact">Liên hệ</a></div></article>'''

def lc_eq(e):
    return f'''<article class="lc"><a class="im" href="{e["slug"]}.html" aria-label="{e["name"]}">{im_tag(e["hero"], e["mode"], e["name"])}</a>
<div class="tag">{e["series"]}</div><h3>{e["name"]}</h3><p>{e["tagline"]}</p>
<div class="btns"><a class="btn btn-f sm" href="{e["slug"]}.html">Tìm hiểu thêm</a><a class="lnk" href="{qlink(e["name"])}">Báo giá</a></div></article>'''

def gallery(items):
    if not items: return ""
    main_k, main_alt = items[0]
    th = "".join(f'<button type="button" class="{"on" if i == 0 else ""}" data-k="{k}" aria-label="Ảnh {i + 1}: {E(a)}">'
                 f'{im_tag(k, "p", "", k=True)}</button>' for i, (k, a) in enumerate(items))
    return (f'<div class="pg rv"><div class="pg-main">{im_tag(main_k, "p", main_alt, k=True)}</div>'
            f'<div class="pg-t">{th}</div></div>')

# ======================================================================= trang
FAMILY = [  # (chỉ số trong ROASTERS, chiều cao thật mm theo otlpro.com, ẩn trên điện thoại?)
    (0, 950, False), (1, 1715, False), (2, 2020, False), (3, 2000, True), (4, 1900, True), (5, 2400, False)]

def img_hero_bg():
    """Ảnh nền đầu trang chủ = ảnh máy rang của web cũ (a158), làm MỜ sẵn bằng PIL (khỏi tốn CSS blur khi cuộn)."""
    path = IMG / "hero_bg.jpg"
    if not path.exists():
        from PIL import ImageFilter, ImageEnhance
        im = Image.open(_src("a158")).convert("RGB"); im.thumbnail((1600, 1600), Image.LANCZOS)
        im = im.filter(ImageFilter.GaussianBlur(7)); im = ImageEnhance.Color(im).enhance(0.75)
        im.save(path, "JPEG", quality=72, optimize=True, progressive=True)
    return "img/hero_bg.jpg"

# Thị trường xuất khẩu (Thành chốt 23/10: EU, châu Á, Tây Á, Nam Á, châu Úc, Đông Á, …)
MARKETS = "".join(f"<li>{m}</li>" for m in ["Châu Âu", "Tây Á – Trung Đông", "Nam Á", "Đông Á", "Đông Nam Á", "Châu Úc"])

def family_row():
    """Ảnh "cả nhà" kiểu Apple: các máy đứng cạnh nhau, cao theo tỉ lệ chiều cao thật (OTL-30 = 360 px)."""
    out = []
    for i, mm, hide in FAMILY:
        r = ROASTERS[i]
        hm = ' class="hm"' if hide else ""
        out.append(f'<figure{hm} style="--h:{round(360 * mm / 2400)}">'
                   f'<a href="{r["slug"]}.html">{im_tag(r["hero"], r["mode"], r["name"], lazy=False)}</a>'
                   f'<figcaption>{r["name"]}</figcaption></figure>')
    return f'<div class="family rv-up">{"".join(out)}</div>'

def page_home():
    """Thứ tự thông điệp (23/10): 1 OTL là ai + làm gì, có con số · 2 cả dòng máy · 3 lý do chọn OTL · máy nổi bật ·
    4 bằng chứng · 5 hỗ trợ · 6 liên hệ. Chỉ dùng thông tin có trên otlpro.com / brochure."""
    six = ROASTERS[2]; thirty = ROASTERS[5]
    body = f'''{nav()}
<main>
<section class="hero pb home-hero dk" style="--hbg:url({img_hero_bg()})"><div class="wrap">
<p class="eyebrow rv">OTL Roaster</p>
<h1 class="h-hero rv">Máy rang cà phê,<br>từ 1,2 đến 500&nbsp;kg.</h1>
<p class="sub rv">Thiết kế và chế tạo tại Việt Nam, cùng mọi thiết bị quanh máy rang.</p>
<div class="btns rv"><a class="btn btn-f" href="roasters.html">Khám phá máy rang</a><a class="btn btn-o" href="quote.html">Nhận báo giá</a></div>
</div>{family_row()}</section>

<section class="sec bg-w center tight"><div class="wrap">
<h2 class="h-l rv">Chọn cỡ máy của bạn.</h2><p class="lead rv" style="margin-top:12px">Tám mẫu máy máy rang tiêu chuẩn, hệ thống lớn tới 500 kg làm theo yêu cầu, và thiết bị hoàn thiện dây chuyền.</p>
</div><div class="wide" style="margin-top:40px">{strip(roaster_items() + equip_items())}</div>
<div class="btns c rv" style="margin-top:28px"><a class="lnk" href="roasters.html">Xem tất cả máy rang</a><a class="lnk" href="compare.html">So sánh mẫu máy</a></div></section>

<section class="sec bg-c"><div class="wrap">
<h2 class="h-xl rv center">Vì sao chọn OTL.</h2>
<div class="feats">
<div class="fc"><p class="n">Một nhà sản xuất</p><h3>Trọn dây chuyền, một đội ngũ.</h3><p>Máy rang, máy tách đá, silo, buồng đốt khói — thiết kế để chạy cùng nhau và lắp đặt cùng nhau.</p><p style="margin-top:14px"><a class="lnk" href="solutions.html">Giải pháp công nghiệp</a></p></div>
<div class="fc"><p class="n">Hiệu quả</p><h3>Giảm tới 30% năng lượng.</h3><p>Tuần hoàn khí toàn phần trên OTL-60 và OTL-120 tái sử dụng khí thải thay vì bỏ phí.</p><p style="margin-top:14px"><a class="lnk" href="solutions.html#circulation">Tuần hoàn khí toàn phần</a></p></div>
<div class="fc"><p class="n">Hỗ trợ</p><h3>Lắp đặt, đào tạo, đồng hành.</h3><p>Lắp đặt tận nơi, hướng dẫn trực tiếp, đường dây nóng kỹ thuật và chẩn đoán từ xa.</p><p style="margin-top:14px"><a class="lnk" href="support.html">Hỗ trợ và dịch vụ</a></p></div>
<div class="fc"><p class="n">Làm tại Việt Nam</p><h3>Chế tạo tại Việt Nam từ 2018.</h3><p>Thiết kế và sản xuất tại nhà máy của OTL, phục vụ khách trong nước và xuất khẩu đi châu Âu, Trung Đông, châu Á, châu Úc.</p><p style="margin-top:14px"><a class="lnk" href="about.html">Về OTL</a></p></div>
</div></div></section>

<section class="hero bg-wash pb"><div class="wrap">
<p class="eyebrow rv">Chủ lực</p><h2 class="h-hero rv">OTL-06</h2><p class="sub rv">{six["tagline"]}</p>
<div class="btns rv"><a class="btn btn-f" href="otl-06.html">Tìm hiểu thêm</a><a class="btn btn-o" href="{qlink("OTL-06")}">Nhận báo giá</a></div>
<div class="shot rv-up">{hero_img(six, lazy=True)}</div></div></section>

<div class="tiles">
<div class="tile dk"><h2 class="h-l">OTL-30</h2><p class="sub">{thirty["tagline"]}</p>
<div class="btns"><a class="btn btn-f sm" href="otl-30.html">Tìm hiểu thêm</a><a class="btn btn-o sm" href="{qlink("OTL-30")}">Báo giá</a></div>
<div class="art">{im_tag(thirty["hero"], "r", "OTL-30")}</div></div>
<div class="tile dk"><h2 class="h-l">OTL-60 · OTL-120</h2><p class="sub">Tuần hoàn khí toàn phần. Giảm tới 30% năng lượng.</p>
<div class="btns"><a class="btn btn-f sm" href="otl-60.html">OTL-60</a><a class="btn btn-o sm" href="otl-120.html">OTL-120</a></div>
<div class="art ph">{im_tag("h120", "p", "OTL-120 tại nhà máy khách hàng")}</div></div>
<div class="tile"><h2 class="h-l">Thiết bị</h2><p class="sub">Tách đá. Xử lý khói. Silo.</p>
<div class="btns"><a class="btn btn-f sm" href="equipment.html">Tìm hiểu thêm</a><a class="btn btn-o sm" href="solutions.html">Giải pháp</a></div>
<div class="art">{im_tag("a73", "r", "Cụm silo OTL")}</div></div>
<div class="tile"><h2 class="h-l">Hỗ trợ</h2><p class="sub">Lắp đặt, đào tạo và đồng hành.</p>
<div class="btns"><a class="btn btn-f sm" href="support.html">Tìm hiểu thêm</a><a class="btn btn-o sm" href="support.html#contact">Liên hệ</a></div>
<div class="art ph">{im_tag("a175", "p", "Kỹ thuật viên OTL lắp đặt máy rang")}</div></div>
</div>

<section class="sec bg-w" style="padding-bottom:0"><div class="wrap center">
<h2 class="h-xl rv">Làm tại Việt Nam.<br>Rang khắp thế giới.</h2>
<p class="lead measure rv" style="margin-top:14px">OTL phát triển từ thương hiệu O Tesla, thành lập năm 2018, thiết kế và sản xuất máy rang cà phê tại Việt Nam.</p></div>
<div class="wrap"><div class="stats">
<div><b>2018</b><span>năm bắt đầu chế tạo</span></div><div><b>1,2–500<small>kg</small></b><span>mỗi mẻ</span></div>
<div><b>8</b><span>mẫu máy tiêu chuẩn</span></div><div><b>6+</b><span>khu vực xuất khẩu</span></div></div><ul class="markets rv">{MARKETS}</ul></div>
<div class="banner rv-f">{im_tag("a168", "p", "Hàn trống rang tại nhà máy OTL")}</div>
<div class="wrap"><div class="duo">
<figure class="rv">{im_tag("a62", "p", "OTL-1.2 tại quán cà phê")}<figcaption class="cap">OTL-1.2 tại một quán cà phê.</figcaption></figure>
<figure class="rv">{im_tag("a106", "p", "OTL-15 tại quán rang")}<figcaption class="cap">OTL-15 tại một quán rang.</figcaption></figure></div>
<div class="btns c rv" style="margin:30px 0 110px"><a class="lnk" href="about.html">Về OTL</a><a class="lnk" href="about.html#lo-trinh">Lộ trình phát triển</a></div></div></section>
{shorts_section("bg-c")}
{CONTACT.replace('class="sec bg-c" id="contact"', 'class="sec bg-w" id="contact"')}
</main>{foot()}'''
    return head("OTL Roaster — Máy rang cà phê 1,2 đến 500 kg, chế tạo tại Việt Nam", "OTL thiết kế và chế tạo máy rang cà phê từ 1,2 đến 500 kg mỗi mẻ tại Việt Nam, cùng máy tách đá, silo và buồng đốt khói hoàn thiện dây chuyền.") + body

def page_roasters():
    rail = "".join(lc(r) for r in ROASTERS) + lc_custom()
    eq = "".join(lc_eq(e) for e in EQUIP)
    body = f'''{nav("roasters")}
<main>
<section class="sec bg-w" style="padding-top:64px;padding-bottom:40px"><div class="wrap">
<h1 class="h-hero rv">Máy rang</h1></div>
<div class="wrap" style="margin-top:40px">{strip(roaster_items() + [dict(href="compare.html", icon=COMPARE_ICON, label="So sánh")])}</div></section>

<section class="sec bg-c" data-rail style="padding-top:80px"><div class="wrap rail-head">
<h2 class="h-l rv">Khám phá dòng máy.</h2><a class="lnk rv" href="compare.html">So sánh tất cả mẫu máy</a></div>
<div class="rail">{rail}</div>
<div class="wrap rail-ctl"><button type="button" data-prev aria-label="Mẫu máy trước">&#8249;</button><button type="button" data-next aria-label="Mẫu máy tiếp">&#8250;</button></div>
</section>

<section class="sec bg-w"><div class="wrap">
<h2 class="h-l rv">Vì sao chọn OTL.</h2>
<div class="feats">
<div class="fc"><p class="n">Kiểm soát</p><h3>Nhiệt độ và gió chính xác.</h3><p>Quản lý nhiệt và gió chính xác qua từng mẻ để chất lượng luôn ổn định.</p></div>
<div class="fc"><p class="n">Hiệu quả</p><h3>Tối ưu năng lượng từ thiết kế.</h3><p>Hệ thống khí nóng, và trên các máy OTL-60 và OTL-120 là tuần hoàn khí toàn phần tái sử dụng khí thải.</p></div>
<div class="fc"><p class="n">Kết cấu</p><h3>Làm ra để chạy mỗi ngày.</h3><p>Thép sơn tĩnh điện, bộ phận tiếp xúc bằng inox, kết cấu chắc chắn — thiết kế và chế tạo tại Việt Nam.</p></div>
<div class="fc"><p class="n">Hỗ trợ</p><h3>Có đội ngũ sau mỗi chiếc máy.</h3><p>Tư vấn trước khi mua, lắp đặt tận nơi, hướng dẫn trực tiếp và chẩn đoán từ xa.</p></div>
</div></div></section>

<section class="sec bg-c"><div class="wrap rail-head"><h2 class="h-l rv">Hoàn thiện dây chuyền.</h2><a class="lnk rv" href="equipment.html">Tất cả thiết bị</a></div>
<div class="wrap grid3">{eq}</div></section>
{cta("Chưa biết chọn cỡ nào?", "Đội ngũ OTL giúp bạn chọn máy theo khối lượng mẻ, sản lượng và mặt bằng.", ("Nhận báo giá", "quote.html"), ("Liên hệ hỗ trợ", "support.html"), "bg-w")}
</main>{foot()}'''
    return head("Máy rang — OTL Roaster", "Máy rang cà phê OTL từ 1,2 đến 500 kg mỗi mẻ. Khám phá dòng máy và so sánh model.") + body

COMPARE_ICON = ('<svg viewBox="0 0 80 76" width="80" height="76" fill="none" stroke="#86868b" stroke-width="2" aria-hidden="true">'
                '<rect x="8" y="18" width="26" height="44" rx="4"/><rect x="46" y="18" width="26" height="44" rx="4"/>'
                '<path d="M14 30h14M14 38h14M14 46h10M52 30h14M52 38h14M52 46h10"/></svg>')

def specs_rows(r):
    rows = [("Năng suất mỗi mẻ", f'{r["batch"]} kg/mẻ'), ("Công suất rang", f'{r["kgh"]} kg/giờ'), ("Công suất đầu đốt", f'{r["burner"]} kW'),
            ("Điện năng tiêu thụ", f'{r["elec"]} kWh'), ("Nguồn điện", r["power"]),
            ("Kích thước (D × R × C, mm)", "".join(f"<span>{d}</span>" for d in r["dims"]))]
    return "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in rows)

def page_model(i):
    r = ROASTERS[i]
    nb = [x for x in sorted(ROASTERS, key=lambda x: abs(ROASTERS.index(x) - i) + ROASTERS.index(x) / 100) if x is not r][:3]
    gal_keys = [(k, "p") for k, _ in r["gallery"]]
    feats = "".join(f'<div class="fc"><p class="n">{n + 1:02d}</p><h3>{E(a)}</h3><p>{E(b)}</p></div>' for n, (a, b) in enumerate(r["features"]))
    uses = "".join(f"<li>{E(u)}</li>" for u in r["uses"])
    if r.get("system"):
        sens = "".join(f"<li><b><i>{n + 1}</i>{a}</b><span>{b}</span></li>" for n, (a, b) in enumerate(SENSORS))
        middle = f'''<section class="sec bg-w" id="system"><div class="wrap">
<h2 class="h-l rv">Bảy điểm đo. Một vòng khép kín.</h2>
<p class="lead rv" style="margin-top:14px;max-width:760px">Bảy nhiệt độ quan trọng được giám sát để bạn chỉnh hồ sơ rang chính xác, trong khi vòng khí khép kín tái sử dụng khí thải và buồng đốt khói tích hợp làm sạch phần khí thoát ra.</p>
<div class="diagram rv-f" style="margin-top:40px">{CIRC}</div>
<ul class="sensors">{sens}</ul>
<div class="btns rv" style="margin-top:36px"><a class="lnk" href="solutions.html#circulation">Tuần hoàn khí toàn phần hoạt động thế nào</a></div></div></section>
<section class="sec bg-c" id="gallery"><div class="wrap"><h2 class="h-l rv">Xem kỹ hơn.</h2>{gallery(r["gallery"])}</div></section>'''
        shot = f'<div class="shot photo rv-up">{hero_img(r)}</div>'
        mini_g = '<a href="#system">Hệ thống</a><a href="#gallery">Hình ảnh</a>'
    else:
        middle = f'''<section class="sec bg-w" id="gallery"><div class="wrap">
<h2 class="h-l rv">Xem kỹ hơn.</h2>{gallery(r["gallery"])}</div></section>'''
        shot = f'<div class="shot rv-up">{hero_img(r)}</div>'
        mini_g = '<a href="#gallery">Hình ảnh</a>'
    dk = " dk" if r.get("dark") else ""
    body = f'''{nav("roasters", bool(dk))}
<div class="mini{dk}"><div class="in"><span class="nm">{r["name"]}</span>
<nav aria-label="{r["name"]}"><a href="#overview">Tổng quan</a><a href="#highlights">Điểm nổi bật</a>{mini_g}<a href="#specs">Thông số</a></nav>
<a class="btn btn-f sm" href="{qlink(r["name"])}">Nhận báo giá</a></div></div>
<main class="{dk.strip()}">
<section class="hero {"bg-wash" if r["wash"] else "bg-c"}{" pb" if r.get("system") else ""}" id="overview"><div class="wrap">
<p class="eyebrow rv">{r["kind"]}</p><h1 class="h-hero rv">{r["name"]}</h1><p class="sub rv">{r["tagline"]}</p>
<div class="btns rv"><a class="btn btn-f" href="{qlink(r["name"])}">Nhận báo giá</a><a class="btn btn-o" href="compare.html?a={r["slug"]}">So sánh</a></div>
{shot}</div></section>

<section class="sec bg-w" id="highlights"><div class="wrap">
<h2 class="h-l rv measure center">{E(r["lead"])}</h2>
<p class="lead rv measure center" style="margin-top:18px">{E(r["intro"])}</p>
<div class="stats">
<div><b>{r["batch"]}<small>kg</small></b><span>mỗi mẻ</span></div>
<div><b>{r["kgh"]}<small>kg/giờ</small></b><span>công suất rang</span></div>
<div><b>{r["burner"]}<small>kW</small></b><span>công suất đầu đốt</span></div>
<div><b>{r["elec"]}<small>kWh</small></b><span>điện năng tiêu thụ</span></div>
</div></div></section>

<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Tính năng chính.</h2><div class="feats">{feats}</div></div></section>
{middle}
<section class="sec bg-c" id="specs"><div class="wrap">
<h2 class="h-l rv">Thông số kỹ thuật.</h2><dl class="specs rv">{specs_rows(r)}</dl>
<h3 class="h-m rv" style="margin-top:60px">Phù hợp cho</h3><ul class="uses">{uses}</ul></div></section>

<section class="sec bg-w"><div class="wrap rail-head"><h2 class="h-l rv">Xem thêm.</h2><a class="lnk rv" href="compare.html?a={r["slug"]}">So sánh {r["name"]} với mẫu máy khác</a></div>
<div class="wrap grid3">{"".join(lc(n) for n in nb)}</div></section>
{cta(f'Đưa {r["name"]} về xưởng của bạn.', "Gửi yêu cầu, OTL sẽ chuẩn bị báo giá, thời gian giao hàng và kế hoạch lắp đặt.", ("Nhận báo giá", qlink(r["name"])), ("Liên hệ hỗ trợ", "support.html"))}
</main>{foot()}'''
    return head(f'{r["name"]} — {r["kind"]} — OTL Roaster', f'{r["name"]}: {r["tagline"]} {r["batch"]} kg mỗi mẻ.', gal_keys) + body

def page_equip_hub():
    tiles = "".join(f'''<div class="tile"><p class="eyebrow">{e["series"]}</p><h2 class="h-l">{e["name"]}</h2><p class="sub">{e["tagline"]}</p>
<div class="btns"><a class="btn btn-f sm" href="{e["slug"]}.html">Tìm hiểu thêm</a><a class="btn btn-o sm" href="{qlink(e["name"])}">Báo giá</a></div>
<div class="art">{im_tag(e["hero"], e["mode"], e["name"])}</div></div>''' for e in EQUIP)
    body = f'''{nav("equipment")}
<main>
<section class="sec bg-w" style="padding-top:64px;padding-bottom:40px"><div class="wrap">
<h1 class="h-hero rv">Thiết bị</h1><p class="sub rv" style="margin-top:12px">Mọi thứ quanh máy rang, làm ra để chạy cùng máy rang.</p></div>
<div class="wrap" style="margin-top:40px">{strip(equip_items())}</div></section>
<div class="tiles">{tiles}<div class="tile" style="grid-column:1/-1"><p class="eyebrow">Giải pháp công nghiệp</p><h2 class="h-l">Trọn dây chuyền.</h2><p class="sub">Từ hạt nhân đến khí sạch.</p>
<div class="btns"><a class="btn btn-f sm" href="solutions.html">Tìm hiểu thêm</a><a class="btn btn-o sm" href="quote.html">Báo giá</a></div>
<div class="art ph">{im_tag("a72", "p", "Silo và máy rang OTL tại xưởng rang")}</div></div></div>
{cta("Lên kế hoạch trọn dây chuyền rang.", "Máy rang, tách đá, silo và buồng đốt khói — chọn cấu hình đồng bộ, một đội ngũ lắp đặt.", ("Nhận báo giá", "quote.html"), ("Giải pháp công nghiệp", "solutions.html"), "bg-w")}
</main>{foot()}'''
    return head("Thiết bị — OTL Roaster", "Máy tách đá, buồng đốt khói, silo và cyclone rời của OTL.") + body

def page_equip(e):
    gal_keys = [(k, "p") for k, _ in e["gallery"]]
    st = "".join(f'<div><b>{a}<small>{u}</small></b><span>{l}</span></div>' for a, u, l in e["stats"])
    sp = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in e["specs"])
    feats = "".join(f'<div class="fc"><p class="n">{n + 1:02d}</p><h3>{E(a)}</h3><p>{E(b)}</p></div>' for n, (a, b) in enumerate(e["features"]))
    others = [x for x in EQUIP if x is not e][:3]
    gal = (f'<section class="sec bg-w" id="gallery"><div class="wrap"><h2 class="h-l rv">Xem kỹ hơn.</h2>{gallery(e["gallery"])}</div></section>'
           if e["gallery"] else "")
    v3d = ""
    if e.get("model3d"):
        glb, poster, nm, mb = e["model3d"]
        v3d = f'''<section class="sec bg-w" id="view3d"><div class="wrap center">
<h2 class="h-l rv">Xem 3D.</h2><p class="lead rv" style="margin-top:12px">Xoay {nm} bằng ngón tay hoặc chuột. Chụm hai ngón hoặc cuộn chuột để phóng to.</p>
<div class="v3d rv" data-glb="{glb}" data-name="{nm}"><img src="{poster}" alt="{nm}, xem trước 3D" loading="lazy">
<button class="btn btn-f" type="button">Xem 3D <small>{mb}</small></button></div></div></section>'''
    tbl = ""
    if e.get("table"):
        hd, rows = e["table"]
        tbl = ('<div class="series-wrap rv"><table class="series"><thead><tr>' + "".join(f"<th>{h}</th>" for h in hd) + "</tr></thead><tbody>"
               + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")
        tbl = f'<h3 class="h-m rv" style="margin-top:60px">Theo cỡ máy</h3>{tbl}'
    body = f'''{nav("equipment")}
<div class="mini"><div class="in"><span class="nm">{e["name"]}</span>
<nav aria-label="{e["name"]}"><a href="#overview">Tổng quan</a><a href="#highlights">Điểm nổi bật</a>{'<a href="#gallery">Hình ảnh</a>' if e["gallery"] else ''}<a href="#specs">Thông số</a></nav>
<a class="btn btn-f sm" href="{qlink(e["name"])}">Nhận báo giá</a></div></div>
<main>
<section class="hero bg-c" id="overview"><div class="wrap">
<p class="eyebrow rv">{e["series"]}</p><h1 class="h-hero rv">{e["name"]}</h1><p class="sub rv">{e["tagline"]}</p>
<div class="btns rv"><a class="btn btn-f" href="{qlink(e["name"])}">Nhận báo giá</a><a class="btn btn-o" href="solutions.html">Xem trọn dây chuyền</a></div>
<div class="shot rv-up">{im_tag(e["hero"], e["mode"], e["name"], lazy=False)}</div></div></section>
<section class="sec bg-w" id="highlights"><div class="wrap">
<h2 class="h-l rv measure center">{E(e["lead"])}</h2><p class="lead rv measure center" style="margin-top:18px">{E(e["intro"])}</p>
<div class="stats">{st}</div></div></section>
<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Tính năng chính.</h2><div class="feats">{feats}</div></div></section>
{gal}
{v3d}
<section class="sec bg-c" id="specs"><div class="wrap"><h2 class="h-l rv">Thông số kỹ thuật.</h2><dl class="specs rv">{sp}</dl>{tbl}</div></section>
<section class="sec bg-w"><div class="wrap rail-head"><h2 class="h-l rv">Hoàn thiện dây chuyền.</h2><a class="lnk rv" href="roasters.html">Máy rang</a></div>
<div class="wrap grid3">{"".join(lc_eq(x) for x in others)}</div></section>
{cta(f'Thêm {e["name"]} vào dây chuyền.', "Cho OTL biết bạn dùng máy rang nào, chúng tôi sẽ chọn công suất phù hợp.", ("Nhận báo giá", qlink(e["name"])), ("Liên hệ hỗ trợ", "support.html"))}
</main>{foot()}'''
    return head(f'{e["name"]} — OTL Roaster', f'{e["name"]}: {e["lead"]}', gal_keys) + body

def page_compare():
    data = {}
    for r in ROASTERS:
        data[r["slug"]] = dict(name=r["name"], tagline=r["tagline"], url=f'{r["slug"]}.html', img=card_img(r), q=qlink(r["name"]),
                               spec=dict(batch=f'{r["batch"]} kg', kgh=f'{r["kgh"]} kg/giờ', burner=f'{r["burner"]} kW',
                                         elec=f'{r["elec"]} kWh', power=r["power"], dims=" · ".join(r["dims"]),
                                         air="Tuần hoàn khí toàn phần" if r.get("system") else "Luồng khí nóng",
                                         ab="Tích hợp" if r.get("system") else "Tuỳ chọn, dòng AB"))
    rows = [("batch", "Năng suất mỗi mẻ"), ("kgh", "Công suất rang"), ("burner", "Công suất đầu đốt"), ("elec", "Điện năng"),
            ("power", "Nguồn điện"), ("air", "Hệ thống khí"), ("ab", "Buồng đốt khói"), ("dims", "Kích thước, mm")]
    def col(n, default):
        opts = "".join(f'<option value="{r["slug"]}"{" selected" if r["slug"] == default else ""}>{r["name"]}</option>' for r in ROASTERS)
        dl = "".join(f'<dt>{lbl}</dt><dd data-k="{k}"></dd>' for k, lbl in rows)
        return f'''<div class="cmp-col c{n}"><label class="vh" for="cmp{n}">Mẫu máy {n}</label><select id="cmp{n}">{opts}</select>
<div class="im" data-f="img"></div><h3 data-f="name"></h3><p class="tl" data-f="tag"></p>
<div class="btns"><a class="btn btn-f sm" data-f="more" href="#">Tìm hiểu thêm</a><a class="lnk" data-f="quote" href="quote.html">Báo giá</a></div>
<dl>{dl}</dl></div>'''
    pre = ('<script>(function(){var a=new URLSearchParams(location.search).get("a");if(!a)return;'
           'document.addEventListener("DOMContentLoaded",function(){var s=document.getElementById("cmp1");'
           'if(s&&s.querySelector(\'option[value="\'+a+\'"]\')){s.value=a;if(a===document.getElementById("cmp2").value)'
           'document.getElementById("cmp2").value=a==="otl-06"?"otl-15":"otl-06";}})})()</script>')
    body = f'''{nav("compare")}
<main><section class="sec bg-w" style="padding-top:64px"><div class="wrap">
<h1 class="h-xl rv center">So sánh các mẫu máy rang.</h1>
<p class="lead rv center" style="margin-top:12px">Chọn tối đa ba mẫu máy để xem cạnh nhau.</p>
<div class="cmp">{col(1, "otl-06")}{col(2, "otl-15")}{col(3, "otl-30")}</div></div></section>
{cta("Vẫn đang cân nhắc?", "Gửi OTL khối lượng mẻ, sản lượng mỗi ngày và mặt bằng — chúng tôi sẽ đề xuất mẫu máy phù hợp.", ("Nhận báo giá", "quote.html"), ("Liên hệ hỗ trợ", "support.html"))}
</main><script>window.CMP={json.dumps(data, ensure_ascii=False)}</script>{pre}{foot()}'''
    return head("So sánh máy rang — OTL Roaster", "So sánh các mẫu máy rang cà phê OTL cạnh nhau.") + body

def page_solutions():
    steps = [("01", "Lưu cà phê nhân", "Silo kín khí giữ cà phê nhân trong điều kiện lý tưởng.", "a73", "r", "silo.html", "Silo OTL"),
             ("02", "Rang", "Nhiệt độ và gió chính xác qua từng mẻ.", "ref", "a", "roasters.html", "Máy rang"),
             ("03", "Tách đá", "Hút khí loại bỏ đá và tạp chất nặng.", "a179", "r", "destoner.html", "Máy tách đá OD"),
             ("04", "Lưu cà phê rang", "Băng tải tự động đưa vào silo cà phê rang.", "a73", "r", "silo.html", "Silo OTL"),
             ("05", "Làm sạch khí", "Buồng đốt khói xử lý khói và mùi.", "a182", "r", "afterburner.html", "Buồng đốt khói AB")]
    st = "".join(f'''<div class="step"><div class="im">{im_tag(k, m, l)}</div><p class="k">{n}</p><h3>{t}</h3><p>{d}</p><a class="lnk" href="{h}">{l}</a></div>'''
                 for n, t, d, k, m, h, l in steps)
    sens = "".join(f"<li><b><i>{n + 1}</i>{a}</b><span>{b}</span></li>" for n, (a, b) in enumerate(SENSORS))
    body = f'''{nav("solutions")}
<main>
<section class="sec bg-w center dk" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">Giải pháp công nghiệp</p><h1 class="h-hero rv" style="margin-top:8px">Từ hạt nhân<br>đến khí sạch.</h1>
<p class="lead measure rv" style="margin-top:18px">Máy rang, máy tách đá, silo và buồng đốt khói thiết kế để chạy cùng nhau, chọn cấu hình theo sản lượng của bạn và do một đội ngũ lắp đặt.</p>
<div class="btns c rv" style="margin-top:26px"><a class="btn btn-f" href="quote.html">Lên kế hoạch dây chuyền</a><a class="btn btn-o" href="roasters.html">Khám phá máy rang</a></div></div></section>

<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Một dây chuyền, năm bước.</h2><div class="steps">{st}</div></div></section>

<section class="sec bg-w dk" id="circulation"><div class="wrap">
<p class="eyebrow rv">OTL-60 · OTL-120</p><h2 class="h-xl rv" style="margin-top:6px">Tuần hoàn khí toàn phần.</h2>
<p class="lead rv" style="margin-top:16px;max-width:760px">Hệ thống khí khép kín tái sử dụng khí thải để giảm lãng phí năng lượng và phân bố nhiệt đều. Theo OTL, mức tiêu thụ năng lượng giảm tới 30%.</p>
<div class="diagram rv-f" style="margin-top:40px">{CIRC}</div>
<ul class="sensors">{sens}</ul></div></section>

<section class="sec bg-c" id="profiles"><div class="wrap">
<p class="eyebrow rv">Tự động hoá thông minh</p><h2 class="h-xl rv" style="margin-top:6px">Mỗi mẻ rang đều được ghi lại.</h2>
<p class="lead rv" style="margin-top:16px;max-width:760px">Phần mềm điều khiển OTL ghi và phân tích từng mẻ với độ chính xác cao, cho mỗi người rang lưu hồ sơ riêng — giúp tái lập kết quả rang.</p>
<div class="duo"><figure class="rv">{im_tag("a148", "p", "Đường cong rang trên màn hình OTL")}<figcaption class="cap">Đường cong rang trên màn hình cảm ứng.</figcaption></figure>
<figure class="rv">{im_tag("a173", "p", "Bảng điều khiển OTL với hồ sơ rang")}<figcaption class="cap">Hồ sơ rang lập trình được cho mẻ đồng đều.</figcaption></figure></div></div></section>
{cta("Cùng lên kế hoạch dây chuyền.", "Gửi sản lượng mục tiêu và mặt bằng, OTL sẽ đề xuất cấu hình trọn bộ.", ("Nhận báo giá", "quote.html"), ("Liên hệ hỗ trợ", "support.html"), "bg-w")}
</main>{foot()}'''
    return head("Giải pháp công nghiệp — OTL Roaster", "Trọn dây chuyền rang cà phê: lưu trữ, rang, tách đá và xử lý khí thải.") + body

def page_support():
    items = [("Tư vấn", "Chọn đúng máy", "Từ máy rang mini đến hệ thống công nghiệp, chúng tôi giúp bạn chọn máy phù hợp nhu cầu."),
             ("Lắp đặt", "Lắp đặt tận nơi", "Đội kỹ thuật lắp đặt máy rang đúng tiêu chuẩn, an toàn và hiệu quả."),
             ("Đào tạo", "Hướng dẫn trực tiếp", "Chuyên gia hướng dẫn trực tiếp để bạn vận hành máy dễ dàng và tối ưu."),
             ("Đường dây nóng", "Hỗ trợ kỹ thuật", "Đội kỹ thuật luôn sẵn sàng hỗ trợ, dù bạn rang ở đâu."),
             ("Từ xa", "Chẩn đoán từ xa", "Công nghệ hiện đại giúp kiểm tra và khắc phục sự cố nhanh, không cần chờ người đến."),
             ("Phụ tùng", "Phụ tùng chính hãng", "Phụ tùng thay thế thiết kế khớp với máy rang OTL, bền lâu.")]
    fc = "".join(f'<div class="fc"><p class="n">{a}</p><h3>{b}</h3><p>{c}</p></div>' for a, b, c in items)
    body = f'''{nav("support")}
<main>
<section class="sec bg-w center" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">Hỗ trợ và dịch vụ</p><h1 class="h-hero rv" style="margin-top:8px">Hỗ trợ có mặt<br>đúng lúc.</h1>
<p class="lead measure rv" style="margin-top:18px">Nhanh chóng, chuyên nghiệp, hiệu quả — trước và sau khi mua. Thành công của khách hàng là thành công của OTL.</p></div>
<div class="banner rv-f">{im_tag("a175", "p", "Kỹ thuật viên OTL lắp đặt máy rang", lazy=False)}</div></section>
<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Đồng hành ở mọi bước.</h2><div class="feats three">{fc}</div></div></section>
<section class="sec bg-w" id="contact"><div class="wrap">
<h2 class="h-l rv">Liên hệ.</h2><p class="lead rv" style="margin-top:12px">Chúng tôi phản hồi trong một ngày làm việc.</p>
<form class="form" data-demo data-ok="Cảm ơn bạn — bản demo, chưa gửi đi đâu." novalidate>
<div><label for="c-name">Tên *</label><input id="c-name" required autocomplete="name"></div>
<div><label for="c-mail">Email *</label><input id="c-mail" type="email" required autocomplete="email"></div>
<div class="full"><label for="c-msg">Chúng tôi giúp gì được bạn? *</label><textarea id="c-msg" required></textarea></div>
<div class="btns"><button class="btn btn-f" type="submit">Gửi tin nhắn</button></div></form>
<div class="addr">
<div><b>Văn phòng</b><p>{OFFICE}</p>{copy_btn(OFFICE, "địa chỉ văn phòng")}</div>
<div><b>Nhà máy</b><p>{FACTORY}</p>{copy_btn(FACTORY, "địa chỉ nhà máy")}</div>
<div><b>Email và điện thoại</b><p class="cp-row">{EMAIL} {copy_btn(EMAIL, "email")}</p><p class="cp-row">{PHONE} {copy_btn(PHONE, "số điện thoại")}</p>
<p style="margin-top:10px"><a class="lnk" href="{WA}" target="_blank" rel="noopener">WhatsApp</a> &nbsp;<a class="lnk" href="{ZALO}" target="_blank" rel="noopener" data-zalo>Zalo</a> &nbsp;<a class="lnk" href="{MSGR}" target="_blank" rel="noopener">Messenger</a></p></div></div>
<div class="btns" style="margin-top:28px">{ALL_BTN}</div></div></section>
</main>{foot()}'''
    return head("Hỗ trợ — OTL Roaster", "Tư vấn, lắp đặt, đào tạo, chẩn đoán từ xa và phụ tùng máy rang OTL.") + body

# --- Về OTL: nội dung từ bài "Quá trình hình thành và phát triển của Công ty TNHH Công Nghiệp OTL" (otlpro.com/vi),
#     trang Công nghệ, trang Hỗ trợ, brochure. Lộ trình chỉ gán năm cho mốc có nguồn (2018, 2025).
ROADMAP = [
    ("2018", "Khởi đầu", "Thành lập thương hiệu O Tesla", "Nghiên cứu và chế tạo máy rang cà phê cho quán cà phê và xưởng rang."),
    ("2025", "Thương hiệu mới", "Đổi tên thương hiệu O Tesla thành OTL",
     "Bước chuyển mình thể hiện cam kết đổi mới, chuyên nghiệp hoá sản phẩm và mở rộng thị trường trong nước, quốc tế."),
    ("Hôm nay", "Hiện tại", "1,2 đến 500 kg, 6+ khu vực xuất khẩu",
     "Tám mẫu máy tiêu chuẩn, hệ thống lớn tới 500 kg làm theo yêu cầu, xuất khẩu đi châu Âu, Trung Đông, Nam Á, Đông Á, Đông Nam Á, châu Úc."),
    ("Tiếp theo", "Định hướng", "Tiết kiệm năng lượng, tăng cường hậu mãi",
     "Thiết bị tiết kiệm năng lượng, giảm khí thải; nâng chất lượng dịch vụ hậu mãi và hỗ trợ kỹ thuật; xây thương hiệu uy tín."),
]
SCIENCE = [
    ("Dẫn nhiệt", "Nhiệt truyền trực tiếp từ thành trống nóng sang hạt khi hạt lăn trên bề mặt trống."),
    ("Đối lưu", "Nhiệt truyền từ luồng khí nóng tới hạt. Điều chỉnh gió và đầu đốt giúp kiểm soát quá trình truyền nhiệt."),
    ("Bức xạ", "Năng lượng nhiệt truyền từ các bề mặt nóng tới hạt bằng bức xạ. Mức đóng góp phụ thuộc kết cấu và điều kiện vận hành."),
]
PROCESS = [
    ("01", "Tư vấn", "Chọn cỡ máy theo khối lượng mẻ, sản lượng và mặt bằng."),
    ("02", "Thiết kế", "Bản vẽ kích thước và cấu hình riêng cho từng xưởng."),
    ("03", "Chế tạo", "Gia công, hàn, sơn tĩnh điện tại nhà máy OTL ở Bình Dương."),
    ("04", "Lắp đặt", "Đội kỹ thuật lắp đặt tận nơi, đúng tiêu chuẩn, an toàn."),
    ("05", "Đào tạo", "Chuyên gia hướng dẫn vận hành trực tiếp tại xưởng."),
    ("06", "Đồng hành", "Đường dây nóng, chẩn đoán từ xa, phụ tùng chính hãng."),
]
KNOWLEDGE = [  # bài viết tiếng Việt trên otlpro.com
    ("Ba phương pháp truyền nhiệt trong rang cà phê", "https://www.otlpro.com/vi/ba-phuong-phap-truyen-nhiet-trong-rang-ca-phe-va-anh-huong-djen-huong-vi"),
    ("Đánh giá quá trình rang và nhận biết hương vị", "https://www.otlpro.com/vi/danh-gia-qua-trinh-rang-ca-phe-va-nhan-biet-huong-vi"),
    ("Đánh giá cà phê rang — chìa khoá của cà phê đặc sản", "https://www.otlpro.com/vi/djanh-gia-ca-phe-rang-and-nhan-biet-huong-vi-chia-khoa-tao-nen-ca-phe-djac-san"),
    ("Cà phê lên men: nguồn gốc và quy trình", "https://www.otlpro.com/vi/ca-phe-len-men-nguon-goc-va-quy-trinh-che-bien"),
    ("Cà phê pha lạnh", "https://www.otlpro.com/vi/ca-phe-pha-lanh"),
    ("Câu hỏi thường gặp khi mới bắt đầu với cà phê rang", "https://www.otlpro.com/vi/nhung-cau-hoi-thuong-gap-khi-ban-moi-bat-djau-voi-ca-phe-rang"),
]

def page_about():
    tl = "".join(f'''<li class="tl-item{" tl-now" if y == "Hôm nay" else ""}{" tl-next" if y == "Tiếp theo" else ""}"><div class="tl-y">{y}</div><div class="tl-b">
<p class="tl-k">{k}</p><h3>{t}</h3><p>{d}</p></div></li>''' for y, k, t, d in ROADMAP)
    sci = "".join(f'<div class="fc"><p class="n">{a}</p><p>{b}</p></div>' for a, b in SCIENCE)
    proc = "".join(f'<div class="step"><p class="k">{n}</p><h3>{t}</h3><p>{d}</p></div>' for n, t, d in PROCESS)
    know = "".join(f'<li><a class="lnk" href="{u}" target="_blank" rel="noopener">{t}</a></li>' for t, u in KNOWLEDGE)
    body = f'''{nav("about")}
<div class="mini"><div class="in"><span class="nm">Về OTL</span>
<nav aria-label="Về OTL"><a href="#cau-chuyen">Câu chuyện</a><a href="#lo-trinh">Lộ trình</a><a href="#khoa-hoc">Khoa học</a><a href="#quy-trinh">Quy trình</a><a href="#nha-may">Nhà máy</a></nav>
<a class="btn btn-f sm" href="quote.html">Nhận báo giá</a></div></div>
<main>
<section class="sec bg-w center" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">Về OTL</p><h1 class="h-hero rv" style="margin-top:8px">Từ O Tesla đến OTL.</h1>
<p class="lead measure rv" style="margin-top:18px">Công ty TNHH Công Nghiệp OTL thiết kế và sản xuất máy rang cà phê tại Việt Nam. Tiền thân là thương hiệu O Tesla, thành lập năm 2018, chính thức đổi tên thương hiệu thành OTL năm 2025.</p>
<div class="stats">
<div><b>2018</b><span>thành lập O Tesla</span></div><div><b>1,2–500<small>kg</small></b><span>dải công suất mỗi mẻ</span></div>
<div><b>8</b><span>mẫu máy tiêu chuẩn, cùng hệ thống theo yêu cầu</span></div><div><b>6+</b><span>khu vực xuất khẩu</span></div></div>
<ul class="markets rv" style="justify-content:center">{MARKETS}</ul></div></section>

<section class="sec bg-c" id="cau-chuyen"><div class="wrap">
<div class="story">
<div><p class="eyebrow rv">Câu chuyện</p><h2 class="h-l rv" style="margin-top:6px">Kế thừa nền tảng kỹ thuật, nâng tầm thương hiệu.</h2></div>
<div class="story-t rv"><p>O Tesla bắt đầu từ việc nghiên cứu và chế tạo máy rang cà phê cho quán cà phê và xưởng rang. Công ty tập trung vào chất lượng máy: thép sơn tĩnh điện, công nghệ điều khiển nhiệt độ và tốc độ gió để tối ưu quy trình rang.</p>
<p>Năm 2025, để phù hợp với định hướng phát triển, thương hiệu O Tesla đổi tên thành <b>OTL</b> — thể hiện cam kết đổi mới, chuyên nghiệp hoá sản phẩm và mở rộng thị trường trong nước cũng như quốc tế.</p>
<p>Với định hướng <b>chất lượng – cải tiến – phát triển bền vững</b>, OTL tiếp tục kế thừa nền tảng kỹ thuật từ O Tesla, không ngừng nâng cao công nghệ, tối ưu thiết kế và hiệu quả vận hành, từng bước khẳng định vị thế trong ngành thiết bị công nghiệp tại Việt Nam.</p></div>
</div>
<div class="duo"><figure class="rv">{im_tag("a168", "p", "Hàn tại nhà máy OTL")}<figcaption class="cap">Mỗi chiếc máy được chế tạo tại nhà máy OTL ở Bình Dương.</figcaption></figure>
<figure class="rv">{im_tag("a161", "p", "Máy rang đang sản xuất tại nhà máy OTL")}<figcaption class="cap">Máy rang cho quán cà phê và xưởng rang công nghiệp.</figcaption></figure></div></div></section>

<section class="sec bg-w" id="lo-trinh"><div class="wrap">
<p class="eyebrow rv">Lộ trình</p><h2 class="h-xl rv" style="margin-top:6px">Chặng đường phát triển.</h2>
<p class="lead rv" style="margin-top:14px;max-width:760px">Từ một xưởng chế tạo máy rang đến nhà sản xuất trọn dây chuyền rang cà phê, xuất khẩu nhiều khu vực.</p>
<ol class="timeline">{tl}</ol></div></section>

<section class="sec bg-c dk" id="khoa-hoc"><div class="wrap">
<p class="eyebrow rv">Khoa học phía sau mỗi mẻ rang</p><h2 class="h-xl rv" style="margin-top:6px">Ba cơ chế truyền nhiệt tới hạt.</h2>
<p class="lead rv" style="margin-top:14px;max-width:760px">Máy rang OTL tích hợp nhiều phương pháp gia nhiệt trong một máy — kết hợp luồng khí nóng thông minh với cấu hình trống phù hợp — để hạt chín đều và ổn định qua từng mẻ.</p>
<div class="feats three">{sci}</div>
<div class="stats">
<div><b>7</b><span>điểm đo nhiệt trên OTL-60/120</span></div><div><b>Tới 30%</b><span>giảm năng lượng nhờ tuần hoàn khí trên OTL-60/120, theo OTL</span></div>
<div><b>Hồ sơ rang</b><span>ghi và phân tích mẻ rang theo cấu hình điều khiển</span></div><div><b>Theo nhu cầu</b><span>chọn cấu hình máy và thiết bị theo sản lượng, mặt bằng</span></div></div>
<div class="btns rv" style="margin-top:36px"><a class="lnk" href="solutions.html#circulation">Xem sơ đồ tuần hoàn khí</a><a class="lnk" href="solutions.html#profiles">Phần mềm ghi hồ sơ rang</a></div></div></section>

<section class="sec bg-w" id="quy-trinh"><div class="wrap">
<p class="eyebrow rv">Quy trình</p><h2 class="h-xl rv" style="margin-top:6px">Từ ý tưởng đến mẻ rang đầu tiên.</h2>
<div class="steps six">{proc}</div></div></section>

<section class="sec bg-c"><div class="wrap">
<p class="eyebrow rv">Giá trị</p><h2 class="h-l rv" style="margin-top:6px">Điều OTL theo đuổi.</h2>
<div class="feats three">
<div class="fc"><p class="n">Sứ mệnh</p><h3>Chất lượng, bền bỉ, tối ưu.</h3><p>Cung cấp sản phẩm chất lượng cao, thiết kế bền bỉ và giải pháp tối ưu cho người rang cà phê.</p></div>
<div class="fc"><p class="n">Khách hàng</p><h3>Khách hàng là trọng tâm.</h3><p>Không ngừng nâng cao chất lượng sản phẩm, dịch vụ hậu mãi và hỗ trợ kỹ thuật để tạo giá trị lâu dài.</p></div>
<div class="fc"><p class="n">Bền vững</p><h3>Trách nhiệm với môi trường.</h3><p>Thiết bị tiết kiệm năng lượng, giảm khí thải, sử dụng tài nguyên hiệu quả.</p></div>
</div></div></section>

<section class="sec bg-w" id="nha-may"><div class="wrap">
<p class="eyebrow rv">Văn phòng và nhà máy</p><h2 class="h-l rv" style="margin-top:6px">Ghé thăm OTL.</h2>
<div class="addr">
<div><b>Văn phòng</b><p>{OFFICE}</p>{copy_btn(OFFICE, "địa chỉ văn phòng")}</div>
<div><b>Nhà máy</b><p>{FACTORY}</p>{copy_btn(FACTORY, "địa chỉ nhà máy")}</div>
<div><b>Liên hệ</b><p class="cp-row">{PHONE} {copy_btn(PHONE, "số điện thoại")}</p><p class="cp-row">{EMAIL} {copy_btn(EMAIL, "email")}</p></div></div>
<h3 class="h-m rv" style="margin-top:70px">Kiến thức rang cà phê</h3>
<ul class="know rv">{know}</ul></div></section>
{cta("Rang cùng OTL.", "Khám phá dòng máy hoặc trò chuyện với đội ngũ OTL về chiếc máy rang tiếp theo của bạn.", ("Khám phá máy rang", "roasters.html"), ("Nhận báo giá", "quote.html"), "bg-c")}
</main>{foot()}'''
    return head("Về OTL — OTL Roaster", "Công ty TNHH Công Nghiệp OTL: từ O Tesla (2018) đến OTL (2025) — câu chuyện, lộ trình, khoa học rang và quy trình.") + body

def page_quote():
    opts = "".join(f'<option value="{r["name"]}">{r["name"]} — {r["batch"]} kg</option>' for r in ROASTERS)
    opts += f'<option value="{CUSTOM}">{CUSTOM}</option>'
    opts += "".join(f'<option value="{e["name"]}">{e["name"]}</option>' for e in EQUIP)
    body = f'''{nav()}
<main><section class="sec bg-c" style="padding-top:72px"><div class="wrap" style="max-width:820px">
<h1 class="h-xl rv">Nhận báo giá.</h1>
<p class="lead rv" style="margin-top:12px">Cho OTL biết bạn rang gì và rang bao nhiêu. Chúng tôi sẽ gửi báo giá, thời gian giao hàng và kế hoạch lắp đặt.</p>
<form class="form" data-demo data-ok="Cảm ơn bạn — bản demo, chưa gửi đi đâu." novalidate>
<div><label for="f-name">Tên *</label><input id="f-name" required autocomplete="name"></div>
<div><label for="f-company">Công ty</label><input id="f-company" autocomplete="organization"></div>
<div><label for="f-mail">Email *</label><input id="f-mail" type="email" required autocomplete="email"></div>
<div><label for="f-phone">Điện thoại</label><input id="f-phone" type="tel" autocomplete="tel"></div>
<div><label for="f-country">Quốc gia *</label><input id="f-country" required autocomplete="country-name"></div>
<div><label for="f-model">Mẫu máy</label><select id="f-model"><option value="">Chưa chắc chắn</option>{opts}</select></div>
<div class="full"><label for="f-msg">Khối lượng mẻ, sản lượng mỗi ngày và yêu cầu khác *</label><textarea id="f-msg" required></textarea></div>
<div class="btns"><button class="btn btn-f" type="submit">Gửi yêu cầu báo giá</button><a class="lnk" href="compare.html">So sánh mẫu máy trước</a></div></form>
</div></section></main>{foot()}'''
    return head("Nhận báo giá — OTL Roaster", "Gửi yêu cầu báo giá máy rang hoặc thiết bị OTL.") + body

# ======================================================================= ghi
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in ("site.css", "site.js"):
        shutil.copy(HERE / f, OUT / f)
    shutil.copy(HERE / "motion.js", OUT / "motion.js")
    shutil.copytree(HERE / "3d", OUT / "3d", dirs_exist_ok=True)   # mô hình 3D đã nén
    pages = {"index": page_home(), "roasters": page_roasters(), "equipment": page_equip_hub(), "compare": page_compare(),
             "solutions": page_solutions(), "support": page_support(), "about": page_about(), "quote": page_quote()}
    for i, r in enumerate(ROASTERS):
        pages[r["slug"]] = page_model(i)
    for e in EQUIP:
        pages[e["slug"]] = page_equip(e)
    for name, h in pages.items():
        (OUT / f"{name}.html").write_text(h, encoding="utf-8")
    total = sum(p.stat().st_size for p in IMG.iterdir())
    print(f"{len(pages)} trang -> {OUT}  | anh: {len(list(IMG.iterdir()))} file, {total / 1e6:.1f} MB")

if __name__ == "__main__":
    main()
