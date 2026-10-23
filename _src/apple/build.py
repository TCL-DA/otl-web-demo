"""Dựng bản demo NHIỀU TRANG kiểu Apple cho otlpro.com → F:\\Project\\otl-web-demo\\apple\\

Sếp chê bản 1 trang kéo dài (23/10/2026) → làm khung như apple.com/ipad + web hãng máy (Giesen, Loring, Probat):
trang chủ · trang dòng máy (dải biểu tượng + băng chuyền) · mỗi model 1 trang · so sánh · thiết bị phụ · giải pháp ·
hỗ trợ · về OTL · hỏi giá.

Nội dung + thông số lấy nguyên từ các trang sản phẩm otlpro.com (cào 23/10/2026). Ảnh lấy từ kho
F:\\Kho-anh\\09_Thiet-ke-khac\\261023_web-otlpro (a<số> = dòng thứ <số> trong danh-sach-anh.csv).
Luật ảnh OTL (F:\\Kho-anh\\OTL_MAY_LIEN_KHOI_THAM_CHIEU.md): không dùng ảnh máy có tủ điều khiển đứng rời →
OTL-60/120 dùng sơ đồ tuần hoàn khí thay ảnh máy.

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
def _src(key):
    if key == "ref": return REF
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
        if base_mode == "r": im = _cut(_clear_white(im))
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

# ======================================================================= dữ liệu (nguyên văn otlpro.com)
ROASTERS = [
    dict(slug="otl-1-2", name="OTL-1.2", kind="Coffee roaster", hero="a51", mode="r", wash=False,
         tagline="Small batch. Serious control.", tag="",
         lead="A compact roaster for cafés and the lab.",
         intro="The OTL-1.2 is a compact, modern roasting machine designed for small coffee shops and laboratory use. "
               "Advanced technology keeps every batch precise and consistent.",
         batch="0.5–1.2", kgh="2–4", burner="3", elec="1", power="1-phase 200–240 V · 50/60 Hz",
         dims=["1290 × 600 × 950"],
         features=[("Smart hot air flow", "A hot-air flow system that roasts the batch evenly."),
                   ("Easy adjustment", "Temperature and drum speed are simple to set and to change."),
                   ("Energy efficient", "Low consumption and an environmentally friendly design."),
                   ("Lab ready", "Small enough for sample roasting and recipe development.")],
         uses=["Coffee shops", "Small-scale roasters", "Laboratory and sample roasting"],
         gallery=[("a62", "OTL-1.2 in a café"), ("a59", "Brass cooling tray"), ("a61", "Drum front and handles"),
                  ("a55", "Sight glass")]),
    dict(slug="otl-03", name="OTL-03", kind="Coffee roaster", hero="c240", mode="a", wash=True,
         tagline="Made for the café floor.", tag="",
         lead="Precise, consistent roasting for the café.",
         intro="The OTL-03 is the ideal solution for medium-sized coffee shops and professional roasters. "
               "With its robust design and advanced features, it delivers precise, consistent roasting in every batch.",
         batch="1–3", kgh="4–12", burner="10", elec="1.5", power="1-phase 200–240 V · 50/60 Hz",
         dims=["1800 × 860 × 1715"],
         features=[("Efficient hot air flow", "An energy-saving hot-air system."),
                   ("Precise control", "Temperature and airflow under precise control."),
                   ("Durable design", "Easy to operate and easy to maintain."),
                   ("Stable quality", "Built for professional batches with consistent results.")],
         uses=["Medium-sized coffee shops", "Professional roasters looking for precision", "Specialty coffee production"],
         gallery=[("a231", "OTL-03 in white"), ("a233", "OTL-03 in a roastery"), ("a238", "OTL-03 side view"),
                  ("a254", "OTL-03 with cooling tray")]),
    dict(slug="otl-06", name="OTL-06", kind="Coffee roaster", hero="ref", mode="a", wash=True,
         tagline="Built for the professional roaster.", tag="Flagship",
         lead="Robust, modern and consistent, batch after batch.",
         intro="The OTL-06 combines advanced technology with a solid build to meet every professional roasting need. "
               "It is optimised to save energy and run at the highest efficiency.",
         batch="2–6", kgh="8–24", burner="15", elec="2.8", power="1-phase 200–240 V · 50/60 Hz",
         dims=["2150 × 1200 × 2020 (V1)", "2200 × 1200 × 1900 (V2)"],
         features=[("Powerful hot air system", "Even, stable heat through the whole batch."),
                   ("Precise control", "Manage temperature and airflow with ease."),
                   ("Durable design", "High-quality materials and sturdy construction."),
                   ("Energy optimisation", "High efficiency that lowers operating costs.")],
         uses=["Medium and large roasting facilities", "Roasters who need consistent quality", "Specialty lines at production scale"],
         gallery=[("a13", "OTL-06 in white and stainless steel"), ("a277", "OTL-06 at the factory"),
                  ("a0", "OTL-06 with destoner"), ("a280", "OTL-06 touchscreen and drum")]),
    dict(slug="otl-12", name="OTL-12", kind="Coffee roaster", hero="a144", mode="r", wash=False,
         tagline="Twice the batch. Same precision.", tag="",
         lead="High capacity for high production needs.",
         intro="The OTL-12 is designed for large-scale commercial production. An intelligent operating system and modern "
               "features bring consistency and efficiency to every batch.",
         batch="4–12", kgh="20–48", burner="40", elec="4", power="1-phase 200–240 V · 50/60 Hz",
         dims=["2600 × 1050 × 2000"],
         features=[("Advanced control system", "Precise temperature and airflow management for every batch."),
                   ("Energy-saving technology", "High performance with low energy consumption."),
                   ("Durable design", "High-quality materials, suitable for continuous operation."),
                   ("Large capacity", "Meets large roasting needs with superior consistency.")],
         uses=["Large-scale roasters and commercial producers", "Brands that need quality in every batch", "High-volume specialty roasting"],
         gallery=[("a146", "OTL-12 in a roastery"), ("a257", "OTL-12 front"), ("a148", "Roast profile on the touchscreen"),
                  ("a153", "Drum door and handles")]),
    dict(slug="otl-15", name="OTL-15", kind="Coffee roaster", hero="a107", mode="r", wash=False,
         tagline="High volume, held steady.", tag="",
         lead="Advanced technology for high-volume roasting.",
         intro="The OTL-15 combines advanced technology with an aesthetic design for large coffee businesses. "
               "It is optimised for high performance, energy saving and long-term durability.",
         batch="5–15", kgh="20–60", burner="40", elec="4", power="1-phase 200–240 V · 50/60 Hz",
         dims=["2500 × 1050 × 1900"],
         features=[("Fully automated control", "Optimises the roasting process with high precision."),
                   ("High efficiency", "Large output with short, uniform roast times."),
                   ("User-friendly design", "An interface that is easy to operate and to maintain."),
                   ("Cleaner operation", "Integrated technology to reduce emissions and keep the workplace clean.")],
         uses=["Large-scale coffee production", "Brands focused on quality and efficiency", "Commercial and specialty roasting"],
         gallery=[("a106", "OTL-15 in a café roastery"), ("a109", "OTL-15 cooling tray"), ("a111", "OTL-15 front"),
                  ("a116", "OTL-15 with touchscreen stand")]),
    dict(slug="otl-30", name="OTL-30", kind="Industrial roaster", hero="a118", mode="r", wash=False, dark=True,
         tagline="Industrial output, fully automated.", tag="",
         lead="Automation and efficiency at industrial scale.",
         intro="The OTL-30 handles high volumes with unparalleled consistency. It is the solution for roasteries that "
               "want performance and quality at scale.",
         batch="10–30", kgh="40–120", burner="60", elec="5.8", power="3-phase 380–400 V · 50/60 Hz",
         dims=["3570 × 1400 × 2400 (V1)", "3050 × 2300 × 2500 (V2)"],
         features=[("Fully automated", "Customisable roasting profiles, run automatically."),
                   ("Touchscreen control", "Real-time adjustments on an easy-to-use touchscreen."),
                   ("Heavy-duty build", "Industrial-grade components designed for non-stop operation."),
                   ("Cyclone chaff collection", "Advanced cyclone systems and emissions in line with environmental standards.")],
         uses=["Large-scale operations", "Demanding roasting schedules", "Production hubs that need scalability"],
         gallery=[("a123", "OTL-30 drum front and control panel"), ("a126", "Brass cooling tray"),
                  ("a121", "Beans dropping into the cooling tray"), ("a125", "Cooling tray agitator")]),
    dict(slug="otl-60", name="OTL-60", kind="Industrial roasting system", hero="a293", mode="p", wash=False, dark=True,
         tagline="Full circulation. Up to 30% less energy.", tag="Full circulation",
         lead="Closed-loop airflow for industrial production.",
         intro="The OTL-60 uses an advanced full-circulation airflow system for efficiency, precision and environmental "
               "responsibility, engineered for large-scale production facilities.",
         batch="30–60", kgh="120–240", burner="200", elec="17.5", power="3-phase 380–400 V · 50/60 Hz",
         dims=["6500 × 5400 × 3900"], system=True,
         features=[("Full circulation airflow", "A closed loop that recycles exhaust air and minimises energy waste."),
                   ("Seven-point temperature control", "Seven critical temperatures monitored for precise adjustment."),
                   ("Integrated afterburner", "Clean emissions built into the system."),
                   ("Touchscreen and profiles", "Real-time data and programmable profiles for consistent batches.")],
         uses=["Industrial-scale coffee production", "Roasters focused on sustainable practice", "High-quality output at scale"],
         gallery=[]),
    dict(slug="otl-120", name="OTL-120", kind="Industrial roasting system", hero="a293", mode="p", wash=False, dark=True,
         tagline="The full-circulation flagship.", tag="Full circulation",
         lead="Our largest system, on a closed loop.",
         intro="The OTL-120 brings the full-circulation airflow system to 120 kg per batch, engineered for large-scale "
               "production with superior control over the roasting process.",
         batch="60–120", kgh="240–480", burner="350", elec="19.5", power="3-phase 380–400 V · 50/60 Hz",
         dims=["6700 × 5500 × 4300"], system=True,
         features=[("Full circulation airflow", "A closed loop that recycles exhaust air and minimises energy waste."),
                   ("Seven-point temperature control", "Seven critical temperatures monitored for precise adjustment."),
                   ("Integrated afterburner", "Clean emissions built into the system."),
                   ("Modular construction", "High-grade materials and a modular design that simplifies maintenance.")],
         uses=["Industrial-scale coffee production", "Roasters focused on sustainable practice", "High-quality output at scale"],
         gallery=[]),
]
SENSORS = [("Bean", "Core bean temperature for precise roasting."), ("Exhaust", "Keeps airflow clean and efficient."),
           ("Cooling", "Rapid cooling that preserves flavour."), ("Burner air", "Optimal heat delivery."),
           ("Chamber", "Consistent heat in the drum chamber."), ("Cyclone", "Chaff collection and air circulation."),
           ("Afterburner", "Final stage that cleans exhaust gases.")]

EQUIP = [
    dict(slug="destoner", name="OD Destoner", short="Destoner", kind="Equipment", hero="a179", mode="r",
         series="OD-05 · OD-15 · OD-30 · OD-60", tagline="Stones out. Quality in.",
         lead="Stones and heavy material, removed from roasted beans.",
         intro="The OD destoner removes stones and other heavy foreign materials from roasted beans, with precise engineering "
               "and an adjustable air suction system. Shown below: the OD-15.",
         stats=[("15–20", "kg", "per batch (OD-15)"), ("1.5", "kW", "power consumption"), ("220", "V", "1-phase, 50/60 Hz"),
                ("4", "", "sizes, OD-05 to OD-60")],
         specs=[("Capacity", "15–20 kg/batch (OD-15)"), ("Power consumption", "1.5 kW"), ("Voltage", "1-phase 220 V · 50/60 Hz"),
                ("Material", "Food-grade stainless steel"), ("Series", "OD-05 · OD-15 · OD-30 · OD-60")],
         features=[("High-efficiency separation", "Air suction removes stones and heavy impurities precisely."),
                   ("Adjustable airflow", "Tune the airflow for beans of different density."),
                   ("Simple controls", "Intuitive controls for easy operation."),
                   ("Stainless construction", "Durable and easy to clean, in a compact footprint.")],
         gallery=[("a189", "White OD destoner"), ("a37", "OD destoner"), ("a186", "OD destoner on the factory floor"),
                  ("a190", "OD destoner side view")]),
    dict(slug="afterburner", name="AB Afterburner", short="Afterburner", kind="Equipment", hero="a182", mode="r",
         series="AB-15 · AB-30 · AB-60 · AB-120", tagline="Clean air, by design.",
         lead="Treats the smoke and odour of industrial roasting.",
         intro="The afterburner treats smoke and odours from industrial roasting, so roasteries keep a clean environment and "
               "comply with emission standards. Shown below: the AB-30.",
         stats=[("15–30", "kg", "roasters served (AB-30)"), ("12–70", "kW", "heating capacity"), ("2", "", "stage burner"),
                ("4", "", "sizes, AB-15 to AB-120")],
         specs=[("For roasters", "15–30 kg (AB-30)"), ("Burner", "Ecoflam (Italy), 2-stage"), ("Heating capacity", "12–70 kW"),
                ("Temperature controller", "Delta"), ("Temperature sensor", "Omron (Japan)"),
                ("Material", "Mild steel, electrostatic powder coating"), ("Series", "AB-15 · AB-30 · AB-60 · AB-120")],
         features=[("High smoke reduction", "Significantly reduces smoke and odour."),
                   ("Eco-friendly", "Helps your operation comply with air-quality regulations."),
                   ("Easy integration", "Optimised for OTL roasters and other compatible models."),
                   ("Made in Vietnam", "Designed and manufactured under strict quality control.")],
         gallery=[("a26", "AB afterburner drawing"), ("a180", "AB afterburner, vertical"), ("a181", "AB afterburner on stand")]),
    dict(slug="silo", name="OTL-Silo", short="Silo", kind="Equipment", hero="a73", mode="r",
         series="Modular silo clusters", tagline="Storage that grows with you.",
         lead="Modular storage for green and roasted coffee.",
         intro="The OTL silo system expands by adding silo clusters as your storage needs grow, in configurations matched to "
               "how you work and the beans you store.",
         stats=[("Modular", "", "add clusters as you grow"), ("Airtight", "", "protects against moisture"),
                ("Auto", "", "conveying system"), ("Custom", "", "sizes and capacities")],
         specs=[("Design", "Modular, expandable silo clusters"), ("Stores", "Green and roasted coffee beans"),
                ("Conveying", "Automatic, with adjustable discharge valves"), ("Material", "High-grade stainless steel"),
                ("Sizes", "From craft workshops to industrial clusters")],
         features=[("Flexible modular design", "Expand capacity by adding silo clusters."),
                   ("Airtight storage", "Prevents moisture and contamination; keeps green and roasted beans apart."),
                   ("Advanced conveying", "Automatic conveying and precise discharge reduce manual work."),
                   ("Fully customisable", "Designed around each customer's specific requirements.")],
         gallery=[("a72", "OTL silos in a roastery"), ("a78", "Silo cluster"), ("a220", "Silo cluster at the factory"),
                  ("a71", "Silos in a café")]),
]

MODE_OF = {x["hero"]: x["mode"] for x in ROASTERS + EQUIP}   # ảnh nhỏ phải xử lý theo đúng kiểu ảnh gốc
CIRC = (HERE / "circulation.svg").read_text(encoding="utf-8")   # sơ đồ tuần hoàn khí, đánh số 7 điểm nhiệt theo SENSORS

# ======================================================================= khung trang
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">')
MOTION = {"preset": {"d": 24, "dur": 850, "ease": "cubic-bezier(.2,.7,.2,1)", "stagger": 70, "each": 30, "cover": "#f5f5f7"},
          "rules": [[".rv", "rise", {"d": 26}], [".rv-up", "rise", {"d": 56, "dur": 1150}], [".rv-f", "fade", {"dur": 1100}],
                    [".stats>div", "rise", {"d": 20}], [".fc", "rise", {"d": 24}], [".tile", "rise", {"d": 30}],
                    [".step", "rise", {"d": 24}], [".strip", "rise", {"d": 18}], [".rail", "rise", {"d": 30}],
                    [".grid3 .lc", "rise", {"d": 26}], [".cmp-col", "rise", {"d": 22}], [".uses li", "rise", {"d": 14}], [".sensors li", "rise", {"d": 14}]]}

# chọn giao diện TRƯỚC khi vẽ (không nháy trắng): đã bấm nút thì theo lựa chọn đã lưu, chưa bấm thì theo máy người xem
THEME_JS = ("<script>(function(){var d=document.documentElement,k='otl-theme',s=null,m=matchMedia('(prefers-color-scheme: dark)');"
            "try{s=localStorage.getItem(k)}catch(e){}function a(){d.dataset.theme=s||(m.matches?'dark':'light')}a();"
            "if(m.addEventListener)m.addEventListener('change',function(){if(!s)a()});"
            "window.OTLTheme={toggle:function(){s=d.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem(k,s)}catch(e){}a();return s}}})()</script>")
THEME_BTN = ('<button class="theme" type="button" data-theme-toggle aria-label="Switch to dark mode">'
             '<svg class="moon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>'
             '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
             '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>')
WHITE = {"ref", "c240"}   # máy trắng: nền tối KHÔNG cần tấm sáng phía sau

def head(title, desc, gallery_keys=()):
    imgs = {k: img(k, m) for k, m in gallery_keys}
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="color-scheme" content="light dark">{THEME_JS}{FONT}'
            f'<link rel="stylesheet" href="site.css"><link rel="icon" href="img/icon.png">'
            f'<script>window.IMGS={json.dumps(imgs)}</script><script src="motion.js"></script>'
            f'<script>OTLM.start({json.dumps(MOTION)})</script></head><body>')

def nav(active="", dk=False):
    def top(href, label, key):
        return f'<a class="top{" on" if key == active else ""}" href="{href}">{label}</a>'
    models = "".join(f'<a href="{r["slug"]}.html">{thumb(r)}<span>{r["name"]}</span></a>' for r in ROASTERS)
    eq = "".join(f'<a href="{e["slug"]}.html">{im_tag(e["hero"], "t", e["name"])}<span>{e["short"]}</span></a>' for e in EQUIP)
    m_models = "".join(f'<a class="sm" href="{r["slug"]}.html">{r["name"]}</a>' for r in ROASTERS)
    return f'''<header class="gnav{" dk" if dk else ""}"><div class="in">
<a class="logo" href="index.html" aria-label="OTL Roaster home"><img class="lg-l" src="{img_logo()}" alt="OTL Roaster" width="85" height="22"><img class="lg-d" src="img/logo_dark.png" alt="OTL Roaster" width="85" height="22"></a>
<ul>
<li>{top("roasters.html", "Roasters", "roasters")}<div class="fly"><div class="in"><div class="big"><h4>Explore roasters</h4>
<a href="roasters.html">All roasters</a><a href="compare.html">Compare</a><a href="quote.html">Request a quote</a></div>
<div><h4>Models</h4><div class="models">{models}</div></div></div></div></li>
<li>{top("equipment.html", "Equipment", "equipment")}<div class="fly"><div class="in"><div class="big"><h4>Complete the line</h4>
<a href="equipment.html">All equipment</a><a href="solutions.html">Industrial solutions</a></div>
<div><h4>Equipment</h4><div class="models">{eq}</div></div></div></div></li>
<li>{top("solutions.html", "Solutions", "solutions")}</li>
<li>{top("compare.html", "Compare", "compare")}</li>
<li>{top("support.html", "Support", "support")}</li>
<li>{top("about.html", "About", "about")}</li>
</ul>
<a class="btn btn-f sm cta" href="quote.html">Request a quote</a>
{THEME_BTN}<button class="burger" type="button" aria-label="Menu" aria-expanded="false"><i></i><i></i></button>
</div></header>
<div class="mnav" hidden><button class="mnav-x" type="button" aria-label="Close menu">&times;</button>
<a href="roasters.html">Roasters</a>{m_models}
<a href="equipment.html">Equipment</a><a href="solutions.html">Solutions</a><a href="compare.html">Compare</a>
<a href="support.html">Support</a><a href="about.html">About</a><a href="quote.html">Request a quote</a>
<button class="theme-t" type="button" data-theme-toggle>Dark mode</button></div>'''

def img_logo():
    path = IMG / "logo.png"
    if not path.exists():
        IMG.mkdir(parents=True, exist_ok=True)
        im = _cut(Image.open(_src("a2")))
        # chữ "OTL ROASTER" trong logo gốc màu trắng (cho nền tối) → tô xám than, giữ nguyên biểu tượng đỏ-xanh bên trái
        px, ic_w = im.load(), int(im.height * 1.15)
        for y in range(im.height):
            for x in range(ic_w, im.width):
                r_, g_, b_, a_ = px[x, y]
                if a_ and min(r_, g_, b_) > 150:
                    px[x, y] = (61, 67, 77, a_)
        im.thumbnail((400, 66), Image.LANCZOS); im.save(path, optimize=True)
        dk_ = im.copy(); pd = dk_.load()   # bản cho nền tối: chữ sáng #E8E8ED
        for y in range(dk_.height):
            for x in range(int(dk_.height * 1.15), dk_.width):
                if pd[x, y][3]: pd[x, y] = (232, 232, 237, pd[x, y][3])
        dk_.save(IMG / "logo_dark.png", optimize=True)
        ic = _cut(Image.open(_src("a1"))); ic.thumbnail((180, 180), Image.LANCZOS); ic.save(IMG / "icon.png", optimize=True)
    return "img/logo.png"

def thumb(r):
    return SYS_ICON if r.get("system") else im_tag(r["hero"], "t", r["name"])

def hero_img(r, lazy=False):
    if r.get("system"):   # sơ đồ vẽ lại — ảnh sơ đồ gốc (a293) có chữ "Đắk Nông" + logo chìm đè lên khay làm nguội
        return f'<div class="diagram">{CIRC}</div>'
    return im_tag(r["hero"], r["mode"], r["name"], lazy=lazy)

def card_img(r):
    return SYS_ICON.replace('width="114" height="76"', 'width="300" height="200"') if r.get("system") else im_tag(r["hero"], r["mode"], r["name"])

# Liên hệ nhanh + WhatsApp: có trên otlpro.com hiện tại (form đè lên ảnh nền + nút WhatsApp nổi) — giữ chức năng,
# trình bày lại kiểu Apple: form là một mục riêng nền sạch; nút WhatsApp viên thuốc viền mảnh, không bóng.
WA = "https://wa.me/84936198938"
WA_SVG = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="#25d366" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/>'
          '<path fill="#fff" d="M16.9 14.3c-.3-.1-1.6-.8-1.8-.9-.3-.1-.4-.1-.6.1l-.8 1c-.2.2-.3.2-.6.1-1.6-.8-2.7-1.5-3.8-3.3-.3-.5.3-.5.8-1.6.1-.2 0-.3 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.3.3-1 1-1 2.3s1 2.7 1.2 2.9c.1.2 2 3.1 4.9 4.3 1.8.8 2.5.8 3.4.7.6-.1 1.6-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.3-.6-.4z"/></svg>')
WA_BTN = f'<a class="wa" href="{WA}" target="_blank" rel="noopener" aria-label="Chat with OTL on WhatsApp">{WA_SVG}<span>WhatsApp</span></a>'
CONTACT = f'''<section class="sec bg-c" id="contact"><div class="wrap contact">
<div><h2 class="h-xl rv">Talk to OTL.</h2>
<p class="lead rv" style="margin-top:14px">Questions about a roaster, a quote or service? Leave your details and our team will get back to you.</p>
<ul class="ct-ways rv"><li><a class="lnk" href="{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a></li>
<li><a class="lnk" href="mailto:otlpro.com@gmail.com">otlpro.com@gmail.com</a></li><li><a class="lnk" href="tel:+84936198938">+84 936 198 938</a></li></ul></div>
<form class="form ct-f rv" data-demo data-ok="Thank you — demo only, nothing was sent." novalidate>
<div class="full"><label for="h-name">Your name</label><input id="h-name" autocomplete="name"></div>
<div><label for="h-mail">Email address *</label><input id="h-mail" type="email" required autocomplete="email"></div>
<div><label for="h-phone">Phone number *</label><input id="h-phone" type="tel" required autocomplete="tel"></div>
<div class="full"><label for="h-msg">Your message *</label><textarea id="h-msg" required></textarea></div>
<div class="btns"><button class="btn btn-f" type="submit">Send message</button><a class="lnk" href="quote.html">Request a full quote</a></div></form>
</div></section>'''

def foot():
    rl = "".join(f'<li><a href="{r["slug"]}.html">{r["name"]}</a></li>' for r in ROASTERS)
    el = "".join(f'<li><a href="{e["slug"]}.html">{e["name"]}</a></li>' for e in EQUIP)
    return f'''<footer class="foot"><div class="wrap">
<p class="note">Specifications on this site are taken from the current otlpro.com product pages. Design concept for review — forms do not send data.</p>
<div class="cols">
<div><h4>Roasters</h4><ul>{rl}<li><a href="compare.html">Compare models</a></li></ul></div>
<div><h4>Equipment</h4><ul>{el}<li><a href="equipment.html">All equipment</a></li></ul></div>
<div><h4>Solutions</h4><ul><li><a href="solutions.html">Industrial solutions</a></li><li><a href="solutions.html#circulation">Full circulation</a></li><li><a href="solutions.html#profiles">Roast profiles</a></li></ul></div>
<div><h4>Support</h4><ul><li><a href="support.html">Support and service</a></li><li><a href="support.html#contact">Contact</a></li><li><a href="quote.html">Request a quote</a></li></ul></div>
<div><h4>OTL</h4><ul><li><a href="about.html">About OTL</a></li><li><a href="index.html">Home</a></li><li><a href="../index.html">All design concepts</a></li></ul></div>
</div>
<div class="fine"><span>© 2026 OTL Industry Co., Ltd. All rights reserved.</span><span>otlpro.com — design concept</span></div>
</div></footer>
{WA_BTN}<script src="site.js"></script></body></html>'''

def cta(title, text, primary=("Request a quote", "quote.html"), secondary=("Compare models", "compare.html"), bg="bg-c"):
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

def roaster_items():
    return [dict(href=f'{r["slug"]}.html', icon=thumb(r), label=r["name"], tag=r["tag"]) for r in ROASTERS]

def equip_items():
    return [dict(href=f'{e["slug"]}.html', icon=im_tag(e["hero"], "t", e["name"]), label=e["short"]) for e in EQUIP]

def lc(r):
    tag = f'<div class="tag">{r["tag"]}</div>' if r["tag"] else '<div class="tag"></div>'
    return f'''<article class="lc"><a class="im" href="{r["slug"]}.html" aria-label="{r["name"]}">{card_img(r)}</a>{tag}
<h3>{r["name"]}</h3><p>{r["tagline"]}</p>
<dl><div><dt>Batch</dt><dd>{r["batch"]} kg</dd></div><div><dt>Output</dt><dd>{r["kgh"]} kg/h</dd></div></dl>
<div class="btns"><a class="btn btn-f sm" href="{r["slug"]}.html">Learn more</a><a class="lnk" href="quote.html?model={r["name"]}">Quote</a></div></article>'''

def lc_eq(e):
    return f'''<article class="lc"><a class="im" href="{e["slug"]}.html" aria-label="{e["name"]}">{im_tag(e["hero"], e["mode"], e["name"])}</a>
<div class="tag">{e["series"]}</div><h3>{e["name"]}</h3><p>{e["tagline"]}</p>
<div class="btns"><a class="btn btn-f sm" href="{e["slug"]}.html">Learn more</a><a class="lnk" href="quote.html?model={e["name"]}">Quote</a></div></article>'''

def gallery(items):
    if not items: return ""
    main_k, main_alt = items[0]
    th = "".join(f'<button type="button" class="{"on" if i == 0 else ""}" data-k="{k}" aria-label="Photo {i + 1}: {E(a)}">'
                 f'{im_tag(k, "p", "", k=True)}</button>' for i, (k, a) in enumerate(items))
    return (f'<div class="pg rv"><div class="pg-main">{im_tag(main_k, "p", main_alt, k=True)}</div>'
            f'<div class="pg-t">{th}</div></div>')

# ======================================================================= trang
def page_home():
    six = ROASTERS[2]; thirty = ROASTERS[5]
    body = f'''{nav()}
<main>
<section class="hero bg-wash"><div class="wrap">
<p class="eyebrow rv">Coffee roaster</p><h1 class="h-hero rv">OTL-06</h1><p class="sub rv">{six["tagline"]}</p>
<div class="btns rv"><a class="btn btn-f" href="otl-06.html">Learn more</a><a class="btn btn-o" href="quote.html?model=OTL-06">Request a quote</a></div>
<div class="shot rv-up">{hero_img(six)}</div></div></section>

<section class="sec bg-w center"><div class="wrap">
<h2 class="h-l rv">Roasters for every batch.</h2><p class="lead rv" style="margin-top:12px">From 1.2 kg sample roasting to 120 kg full-circulation systems.</p>
</div><div class="wide" style="margin-top:44px">{strip(roaster_items() + equip_items())}</div>
<div class="btns c rv" style="margin-top:30px"><a class="lnk" href="roasters.html">Explore all roasters</a><a class="lnk" href="compare.html">Compare models</a></div></section>

<div class="tiles">
<div class="tile dk"><h2 class="h-l">OTL-30</h2><p class="sub">{thirty["tagline"]}</p>
<div class="btns"><a class="btn btn-f sm" href="otl-30.html">Learn more</a><a class="btn btn-o sm" href="quote.html?model=OTL-30">Quote</a></div>
<div class="art">{im_tag(thirty["hero"], "r", "OTL-30")}</div></div>
<div class="tile dk"><h2 class="h-l">OTL-60 · OTL-120</h2><p class="sub">Full circulation. Up to 30% less energy.</p>
<div class="btns"><a class="btn btn-f sm" href="otl-60.html">OTL-60</a><a class="btn btn-o sm" href="otl-120.html">OTL-120</a></div>
<div class="art dg">{CIRC}</div></div>
<div class="tile"><h2 class="h-l">Equipment</h2><p class="sub">Destoner. Afterburner. Silo.</p>
<div class="btns"><a class="btn btn-f sm" href="equipment.html">Learn more</a><a class="btn btn-o sm" href="solutions.html">Solutions</a></div>
<div class="art">{im_tag("a73", "r", "OTL silo cluster")}</div></div>
<div class="tile"><h2 class="h-l">Support</h2><p class="sub">Installed, trained and supported.</p>
<div class="btns"><a class="btn btn-f sm" href="support.html">Learn more</a><a class="btn btn-o sm" href="support.html#contact">Contact</a></div>
<div class="art ph">{im_tag("a175", "p", "OTL technician setting up a roaster")}</div></div>
</div>

<section class="sec bg-w center" style="padding-bottom:0"><div class="wrap">
<h2 class="h-xl rv">Designed and built in Vietnam.</h2>
<p class="lead measure rv" style="margin-top:14px">OTL has designed and manufactured coffee roasters since 2018, from 1.2 kg to 120 kg per batch, for customers at home and export to the EU and Asia.</p>
<div class="btns c rv" style="margin-top:20px"><a class="lnk" href="about.html">About OTL</a></div></div>
<div class="banner rv-f">{im_tag("a168", "p", "Welding a roaster drum at the OTL factory")}</div></section>
{CONTACT}
</main>{foot()}'''
    return head("OTL Roaster — Coffee roasters from 1.2 to 120 kg", "Modern coffee roasters, destoners, afterburners and silos, designed and built by OTL in Vietnam.") + body

def page_roasters():
    rail = "".join(lc(r) for r in ROASTERS)
    eq = "".join(lc_eq(e) for e in EQUIP)
    body = f'''{nav("roasters")}
<main>
<section class="sec bg-w" style="padding-top:64px;padding-bottom:40px"><div class="wrap">
<h1 class="h-hero rv">Roasters</h1></div>
<div class="wrap" style="margin-top:40px">{strip(roaster_items() + [dict(href="compare.html", icon=COMPARE_ICON, label="Compare")])}</div></section>

<section class="sec bg-c" data-rail style="padding-top:80px"><div class="wrap rail-head">
<h2 class="h-l rv">Explore the lineup.</h2><a class="lnk rv" href="compare.html">Compare all models</a></div>
<div class="rail">{rail}</div>
<div class="wrap rail-ctl"><button type="button" data-prev aria-label="Previous models">&#8249;</button><button type="button" data-next aria-label="Next models">&#8250;</button></div>
</section>

<section class="sec bg-w"><div class="wrap">
<h2 class="h-l rv">Why OTL.</h2>
<div class="feats">
<div class="fc"><p class="n">Control</p><h3>Precise temperature and airflow.</h3><p>Manage heat and air with precision, batch after batch, for consistent quality.</p></div>
<div class="fc"><p class="n">Efficiency</p><h3>Energy-optimised by design.</h3><p>Hot-air systems and, on our largest models, full circulation that recycles exhaust air.</p></div>
<div class="fc"><p class="n">Build</p><h3>Made to run every day.</h3><p>Powder-coated steel, stainless contact parts and sturdy construction, designed and built in Vietnam.</p></div>
<div class="fc"><p class="n">Support</p><h3>A team behind every machine.</h3><p>Consulting before you buy, on-site installation, hands-on training and remote diagnosis.</p></div>
</div></div></section>

<section class="sec bg-c"><div class="wrap rail-head"><h2 class="h-l rv">Complete the line.</h2><a class="lnk rv" href="equipment.html">All equipment</a></div>
<div class="wrap grid3">{eq}</div></section>
{cta("Not sure which size?", "Our team can help you match a roaster to your batch size, output and space.", ("Request a quote", "quote.html"), ("Talk to support", "support.html"), "bg-w")}
</main>{foot()}'''
    return head("Roasters — OTL Roaster", "OTL coffee roasters from 1.2 kg to 120 kg per batch. Explore the lineup and compare models.") + body

COMPARE_ICON = ('<svg viewBox="0 0 80 76" width="80" height="76" fill="none" stroke="#86868b" stroke-width="2" aria-hidden="true">'
                '<rect x="8" y="18" width="26" height="44" rx="4"/><rect x="46" y="18" width="26" height="44" rx="4"/>'
                '<path d="M14 30h14M14 38h14M14 46h10M52 30h14M52 38h14M52 46h10"/></svg>')

def specs_rows(r):
    rows = [("Batch capacity", f'{r["batch"]} kg/batch'), ("Output", f'{r["kgh"]} kg/hour'), ("Burner capacity", f'{r["burner"]} kW'),
            ("Electricity consumption", f'{r["elec"]} kWh'), ("Power supply", r["power"]),
            ("Dimensions (L × W × H, mm)", "".join(f"<span>{d}</span>" for d in r["dims"]))]
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
<h2 class="h-l rv">Seven points. One closed loop.</h2>
<p class="lead rv" style="margin-top:14px;max-width:760px">Seven critical temperatures are monitored so you can adjust the roast profile precisely, while the closed loop recycles exhaust air and the integrated afterburner cleans what leaves the system.</p>
<ul class="sensors">{sens}</ul>
<div class="btns rv" style="margin-top:36px"><a class="lnk" href="solutions.html#circulation">How full circulation works</a></div></div></section>'''
        shot = f'<div class="shot photo rv-up">{hero_img(r)}</div><p class="cap note rv">Simplified schematic of the full-circulation airflow. Photography of the {r["name"]} is being updated.</p>'
        mini_g = '<a href="#system">System</a>'
    else:
        middle = f'''<section class="sec bg-w" id="gallery"><div class="wrap">
<h2 class="h-l rv">Take a closer look.</h2>{gallery(r["gallery"])}</div></section>'''
        shot = f'<div class="shot rv-up">{hero_img(r)}</div>'
        mini_g = '<a href="#gallery">Gallery</a>'
    dk = " dk" if r.get("dark") else ""
    body = f'''{nav("roasters", bool(dk))}
<div class="mini{dk}"><div class="in"><span class="nm">{r["name"]}</span>
<nav aria-label="{r["name"]}"><a href="#overview">Overview</a><a href="#highlights">Highlights</a>{mini_g}<a href="#specs">Tech specs</a></nav>
<a class="btn btn-f sm" href="quote.html?model={r["name"]}">Request a quote</a></div></div>
<main class="{dk.strip()}">
<section class="hero {"bg-wash" if r["wash"] else "bg-c"}{" pb" if r.get("system") else ""}" id="overview"><div class="wrap">
<p class="eyebrow rv">{r["kind"]}</p><h1 class="h-hero rv">{r["name"]}</h1><p class="sub rv">{r["tagline"]}</p>
<div class="btns rv"><a class="btn btn-f" href="quote.html?model={r["name"]}">Request a quote</a><a class="btn btn-o" href="compare.html?a={r["slug"]}">Compare</a></div>
{shot}</div></section>

<section class="sec bg-w" id="highlights"><div class="wrap">
<h2 class="h-l rv measure center">{E(r["lead"])}</h2>
<p class="lead rv measure center" style="margin-top:18px">{E(r["intro"])}</p>
<div class="stats">
<div><b>{r["batch"]}<small>kg</small></b><span>per batch</span></div>
<div><b>{r["kgh"]}<small>kg/h</small></b><span>roasting output</span></div>
<div><b>{r["burner"]}<small>kW</small></b><span>burner capacity</span></div>
<div><b>{r["elec"]}<small>kWh</small></b><span>electricity consumption</span></div>
</div></div></section>

<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Key features.</h2><div class="feats">{feats}</div></div></section>
{middle}
<section class="sec bg-c" id="specs"><div class="wrap">
<h2 class="h-l rv">Tech specs.</h2><dl class="specs rv">{specs_rows(r)}</dl>
<h3 class="h-m rv" style="margin-top:60px">Made for</h3><ul class="uses">{uses}</ul></div></section>

<section class="sec bg-w"><div class="wrap rail-head"><h2 class="h-l rv">Keep exploring.</h2><a class="lnk rv" href="compare.html?a={r["slug"]}">Compare {r["name"]} with other models</a></div>
<div class="wrap grid3">{"".join(lc(n) for n in nb)}</div></section>
{cta(f'Bring the {r["name"]} to your roastery.', "Send us your requirements and we will prepare a quote, delivery time and installation plan.", ("Request a quote", f'quote.html?model={r["name"]}'), ("Talk to support", "support.html"))}
</main>{foot()}'''
    return head(f'{r["name"]} — {r["kind"]} — OTL Roaster', f'{r["name"]}: {r["tagline"]} {r["batch"]} kg per batch.', gal_keys) + body

def page_equip_hub():
    tiles = "".join(f'''<div class="tile"><p class="eyebrow">{e["series"]}</p><h2 class="h-l">{e["name"]}</h2><p class="sub">{e["tagline"]}</p>
<div class="btns"><a class="btn btn-f sm" href="{e["slug"]}.html">Learn more</a><a class="btn btn-o sm" href="quote.html?model={e["name"]}">Quote</a></div>
<div class="art">{im_tag(e["hero"], e["mode"], e["name"])}</div></div>''' for e in EQUIP)
    body = f'''{nav("equipment")}
<main>
<section class="sec bg-w" style="padding-top:64px;padding-bottom:40px"><div class="wrap">
<h1 class="h-hero rv">Equipment</h1><p class="sub rv" style="margin-top:12px">Everything around the roaster, made to work with it.</p></div>
<div class="wrap" style="margin-top:40px">{strip(equip_items())}</div></section>
<div class="tiles">{tiles}<div class="tile"><p class="eyebrow">Industrial solutions</p><h2 class="h-l">The whole line.</h2><p class="sub">From green bean to clean air.</p>
<div class="btns"><a class="btn btn-f sm" href="solutions.html">Learn more</a><a class="btn btn-o sm" href="quote.html">Quote</a></div>
<div class="art ph">{im_tag("a72", "p", "OTL silos and roaster in a roastery")}</div></div></div>
{cta("Plan a complete roasting line.", "Roaster, destoner, silo and afterburner, sized together and installed by one team.", ("Request a quote", "quote.html"), ("Industrial solutions", "solutions.html"), "bg-w")}
</main>{foot()}'''
    return head("Equipment — OTL Roaster", "OTL destoners, afterburners and silos.") + body

def page_equip(e):
    gal_keys = [(k, "p") for k, _ in e["gallery"]]
    st = "".join(f'<div><b>{a}<small>{u}</small></b><span>{l}</span></div>' for a, u, l in e["stats"])
    sp = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in e["specs"])
    feats = "".join(f'<div class="fc"><p class="n">{n + 1:02d}</p><h3>{E(a)}</h3><p>{E(b)}</p></div>' for n, (a, b) in enumerate(e["features"]))
    others = [x for x in EQUIP if x is not e]
    body = f'''{nav("equipment")}
<div class="mini"><div class="in"><span class="nm">{e["name"]}</span>
<nav aria-label="{e["name"]}"><a href="#overview">Overview</a><a href="#highlights">Highlights</a><a href="#gallery">Gallery</a><a href="#specs">Tech specs</a></nav>
<a class="btn btn-f sm" href="quote.html?model={e["name"]}">Request a quote</a></div></div>
<main>
<section class="hero bg-c" id="overview"><div class="wrap">
<p class="eyebrow rv">{e["series"]}</p><h1 class="h-hero rv">{e["name"]}</h1><p class="sub rv">{e["tagline"]}</p>
<div class="btns rv"><a class="btn btn-f" href="quote.html?model={e["name"]}">Request a quote</a><a class="btn btn-o" href="solutions.html">See the whole line</a></div>
<div class="shot rv-up">{im_tag(e["hero"], e["mode"], e["name"], lazy=False)}</div></div></section>
<section class="sec bg-w" id="highlights"><div class="wrap">
<h2 class="h-l rv measure center">{E(e["lead"])}</h2><p class="lead rv measure center" style="margin-top:18px">{E(e["intro"])}</p>
<div class="stats">{st}</div></div></section>
<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Key features.</h2><div class="feats">{feats}</div></div></section>
<section class="sec bg-w" id="gallery"><div class="wrap"><h2 class="h-l rv">Take a closer look.</h2>{gallery(e["gallery"])}</div></section>
<section class="sec bg-c" id="specs"><div class="wrap"><h2 class="h-l rv">Tech specs.</h2><dl class="specs rv">{sp}</dl></div></section>
<section class="sec bg-w"><div class="wrap rail-head"><h2 class="h-l rv">Complete the line.</h2><a class="lnk rv" href="roasters.html">Roasters</a></div>
<div class="wrap grid3">{"".join(lc_eq(x) for x in others)}</div></section>
{cta(f'Add the {e["name"]} to your line.', "Tell us which roaster it will work with and we will size it for you.", ("Request a quote", f'quote.html?model={e["name"]}'), ("Talk to support", "support.html"))}
</main>{foot()}'''
    return head(f'{e["name"]} — OTL Roaster', f'{e["name"]}: {e["lead"]}', gal_keys) + body

def page_compare():
    data = {}
    for r in ROASTERS:
        data[r["slug"]] = dict(name=r["name"], tagline=r["tagline"], url=f'{r["slug"]}.html', img=card_img(r),
                               spec=dict(batch=f'{r["batch"]} kg', kgh=f'{r["kgh"]} kg/h', burner=f'{r["burner"]} kW',
                                         elec=f'{r["elec"]} kWh', power=r["power"], dims=" · ".join(r["dims"]),
                                         air="Full circulation" if r.get("system") else "Hot air flow",
                                         ab="Integrated" if r.get("system") else "Optional, AB series"))
    rows = [("batch", "Batch capacity"), ("kgh", "Output"), ("burner", "Burner capacity"), ("elec", "Electricity"),
            ("power", "Power supply"), ("air", "Airflow system"), ("ab", "Afterburner"), ("dims", "Dimensions, mm")]
    def col(n, default):
        opts = "".join(f'<option value="{r["slug"]}"{" selected" if r["slug"] == default else ""}>{r["name"]}</option>' for r in ROASTERS)
        dl = "".join(f'<dt>{lbl}</dt><dd data-k="{k}"></dd>' for k, lbl in rows)
        return f'''<div class="cmp-col c{n}"><label class="vh" for="cmp{n}">Model {n}</label><select id="cmp{n}">{opts}</select>
<div class="im" data-f="img"></div><h3 data-f="name"></h3><p class="tl" data-f="tag"></p>
<div class="btns"><a class="btn btn-f sm" data-f="more" href="#">Learn more</a><a class="lnk" data-f="quote" href="quote.html">Quote</a></div>
<dl>{dl}</dl></div>'''
    pre = ('<script>(function(){var a=new URLSearchParams(location.search).get("a");if(!a)return;'
           'document.addEventListener("DOMContentLoaded",function(){var s=document.getElementById("cmp1");'
           'if(s&&s.querySelector(\'option[value="\'+a+\'"]\')){s.value=a;if(a===document.getElementById("cmp2").value)'
           'document.getElementById("cmp2").value=a==="otl-06"?"otl-15":"otl-06";}})})()</script>')
    body = f'''{nav("compare")}
<main><section class="sec bg-w" style="padding-top:64px"><div class="wrap">
<h1 class="h-xl rv center">Compare roaster models.</h1>
<p class="lead rv center" style="margin-top:12px">Choose up to three models to see them side by side.</p>
<div class="cmp">{col(1, "otl-06")}{col(2, "otl-15")}{col(3, "otl-30")}</div></div></section>
{cta("Still deciding?", "Send us your batch size, daily output and available space. We will recommend the right model.", ("Request a quote", "quote.html"), ("Talk to support", "support.html"))}
</main><script>window.CMP={json.dumps(data)}</script>{pre}{foot()}'''
    return head("Compare roasters — OTL Roaster", "Compare OTL coffee roasters side by side.") + body

def page_solutions():
    steps = [("01", "Store green", "Airtight silos keep green coffee in ideal condition.", "a73", "r", "silo.html", "OTL-Silo"),
             ("02", "Roast", "Precise temperature and airflow, batch after batch.", "ref", "a", "roasters.html", "Roasters"),
             ("03", "Destone", "Air suction removes stones and heavy impurities.", "a179", "r", "destoner.html", "OD Destoner"),
             ("04", "Store roasted", "Automatic conveying into roasted-coffee silos.", "a73", "r", "silo.html", "OTL-Silo"),
             ("05", "Clean the air", "The afterburner treats smoke and odour.", "a182", "r", "afterburner.html", "AB Afterburner")]
    st = "".join(f'''<div class="step"><div class="im">{im_tag(k, m, l)}</div><p class="k">{n}</p><h3>{t}</h3><p>{d}</p><a class="lnk" href="{h}">{l}</a></div>'''
                 for n, t, d, k, m, h, l in steps)
    sens = "".join(f"<li><b><i>{n + 1}</i>{a}</b><span>{b}</span></li>" for n, (a, b) in enumerate(SENSORS))
    body = f'''{nav("solutions")}
<main>
<section class="sec bg-w center dk" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">Industrial solutions</p><h1 class="h-hero rv" style="margin-top:8px">From green bean<br>to clean air.</h1>
<p class="lead measure rv" style="margin-top:18px">Roasters, destoners, silos and afterburners designed to work together, sized for your output and installed by one team.</p>
<div class="btns c rv" style="margin-top:26px"><a class="btn btn-f" href="quote.html">Plan your line</a><a class="btn btn-o" href="roasters.html">Explore roasters</a></div></div></section>

<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">One line, five steps.</h2><div class="steps">{st}</div></div></section>

<section class="sec bg-w dk" id="circulation"><div class="wrap">
<p class="eyebrow rv">OTL-60 · OTL-120</p><h2 class="h-xl rv" style="margin-top:6px">Full circulation, explained.</h2>
<p class="lead rv" style="margin-top:16px;max-width:760px">A closed-loop airflow system recycles exhaust air to minimise energy waste and distribute heat evenly. OTL rates it at up to 30% lower energy consumption.</p>
<div class="diagram rv-f" style="margin-top:40px">{CIRC}</div>
<ul class="sensors">{sens}</ul></div></section>

<section class="sec bg-c" id="profiles"><div class="wrap">
<p class="eyebrow rv">Smart automation</p><h2 class="h-xl rv" style="margin-top:6px">Every roast, recorded.</h2>
<p class="lead rv" style="margin-top:16px;max-width:760px">OTL control software records and analyses each roast with high precision and lets every roaster save personal profiles, so a good batch can be repeated.</p>
<div class="duo"><figure class="rv">{im_tag("a148", "p", "Roast curve on the OTL touchscreen")}<figcaption class="cap">Roast curve on the touchscreen.</figcaption></figure>
<figure class="rv">{im_tag("a173", "p", "OTL control panel with profile")}<figcaption class="cap">Programmable profiles for consistent batches.</figcaption></figure></div></div></section>
{cta("Let's plan your line.", "Share your output target and floor plan. We will propose a complete configuration.", ("Request a quote", "quote.html"), ("Talk to support", "support.html"), "bg-w")}
</main>{foot()}'''
    return head("Industrial solutions — OTL Roaster", "Complete coffee roasting lines: storage, roasting, destoning and emission treatment.") + body

def page_support():
    items = [("Consulting", "Choosing the right machine", "From mini roasters to industrial systems, we help you choose the roaster that fits your needs."),
             ("Installation", "On-site installation", "Our technical team installs every roaster to standard, safely and effectively."),
             ("Training", "Hands-on training", "Experts guide your team directly, so the machine is easy and efficient to run."),
             ("Hotline", "Technical hotline", "Our technical team is ready to support you, wherever you roast."),
             ("Remote", "Remote diagnosis", "Modern tools let us check and fix problems quickly, without waiting for a visit."),
             ("Parts", "Genuine spare parts", "Replacement parts designed to match OTL roasters for long-lasting performance.")]
    fc = "".join(f'<div class="fc"><p class="n">{a}</p><h3>{b}</h3><p>{c}</p></div>' for a, b, c in items)
    body = f'''{nav("support")}
<main>
<section class="sec bg-w center" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">Support and service</p><h1 class="h-hero rv" style="margin-top:8px">Support that<br>shows up.</h1>
<p class="lead measure rv" style="margin-top:18px">Fast, professional and effective, before and after you buy. Your success is our success.</p></div>
<div class="banner rv-f">{im_tag("a175", "p", "OTL technician setting up a roaster", lazy=False)}</div></section>
<section class="sec bg-c"><div class="wrap"><h2 class="h-l rv">Here for every step.</h2><div class="feats three">{fc}</div></div></section>
<section class="sec bg-w" id="contact"><div class="wrap">
<h2 class="h-l rv">Contact us.</h2><p class="lead rv" style="margin-top:12px">We reply within one working day.</p>
<form class="form" data-demo data-ok="Thank you — demo only, nothing was sent." novalidate>
<div><label for="c-name">Name *</label><input id="c-name" required autocomplete="name"></div>
<div><label for="c-mail">Email *</label><input id="c-mail" type="email" required autocomplete="email"></div>
<div class="full"><label for="c-msg">How can we help? *</label><textarea id="c-msg" required></textarea></div>
<div class="btns"><button class="btn btn-f" type="submit">Send message</button></div></form>
<div class="addr">
<div><b>Office</b><p>No. 44, N5 Street, Tan Phuoc Quarter, Tan Binh Ward, Di An City, Binh Duong, Vietnam</p></div>
<div><b>Factory</b><p>398/33 DT743B, Dong Thanh Hamlet, Tan Dong Hiep Ward, Di An City, Binh Duong, Vietnam</p></div>
<div><b>Email and phone</b><p>otlpro.com@gmail.com<br>+84 936 198 938</p></div></div></div></section>
</main>{foot()}'''
    return head("Support — OTL Roaster", "OTL consulting, installation, training, remote diagnosis and spare parts.") + body

def page_about():
    body = f'''{nav("about")}
<main>
<section class="sec bg-w center" style="padding-top:72px"><div class="wrap">
<p class="eyebrow rv">About OTL</p><h1 class="h-hero rv" style="margin-top:8px">From O Tesla to OTL.</h1>
<p class="lead measure rv" style="margin-top:18px">OTL Industry Co., Ltd. designs and manufactures coffee roasting machines in Vietnam. The company grew from the O Tesla brand, established in 2018, and became OTL in 2025.</p>
<div class="stats">
<div><b>2018</b><span>founded as O Tesla</span></div><div><b>1.2–120<small>kg</small></b><span>batch range</span></div>
<div><b>8</b><span>roaster models</span></div><div><b>EU · Asia</b><span>export markets</span></div></div></div></section>
<section class="sec bg-c"><div class="wrap">
<div class="duo"><figure class="rv">{im_tag("a168", "p", "Welding at the OTL factory")}<figcaption class="cap">Every machine is built at our factory in Binh Duong.</figcaption></figure>
<figure class="rv">{im_tag("a161", "p", "Roasters in production at the OTL factory")}<figcaption class="cap">Roasters for cafés and industrial roasteries.</figcaption></figure></div>
<div class="feats three">
<div class="fc"><p class="n">Build</p><h3>Quality, in steel.</h3><p>Powder-coated steel and temperature and airflow control technology that optimise the roasting process.</p></div>
<div class="fc"><p class="n">Reach</p><h3>Home and abroad.</h3><p>Serving the domestic market and exporting to the EU, Asia and other markets.</p></div>
<div class="fc"><p class="n">Future</p><h3>Efficient by intent.</h3><p>Energy-efficient, durable equipment that reduces emissions, with customers at the centre.</p></div>
</div></div></section>
{cta("Roast with OTL.", "Explore the lineup or talk to our team about your next roaster.", ("Explore roasters", "roasters.html"), ("Request a quote", "quote.html"), "bg-w")}
</main>{foot()}'''
    return head("About — OTL Roaster", "OTL Industry Co., Ltd. designs and manufactures coffee roasters in Vietnam since 2018.") + body

def page_quote():
    opts = "".join(f'<option value="{r["name"]}">{r["name"]} — {r["batch"]} kg</option>' for r in ROASTERS)
    opts += "".join(f'<option value="{e["name"]}">{e["name"]}</option>' for e in EQUIP)
    body = f'''{nav()}
<main><section class="sec bg-c" style="padding-top:72px"><div class="wrap" style="max-width:820px">
<h1 class="h-xl rv">Request a quote.</h1>
<p class="lead rv" style="margin-top:12px">Tell us what you roast and how much. We will reply with a quote, delivery time and installation plan.</p>
<form class="form" data-demo data-ok="Thank you — demo only, nothing was sent." novalidate>
<div><label for="f-name">Name *</label><input id="f-name" required autocomplete="name"></div>
<div><label for="f-company">Company</label><input id="f-company" autocomplete="organization"></div>
<div><label for="f-mail">Email *</label><input id="f-mail" type="email" required autocomplete="email"></div>
<div><label for="f-phone">Phone</label><input id="f-phone" type="tel" autocomplete="tel"></div>
<div><label for="f-country">Country *</label><input id="f-country" required autocomplete="country-name"></div>
<div><label for="f-model">Model</label><select id="f-model"><option value="">Not sure yet</option>{opts}</select></div>
<div class="full"><label for="f-msg">Your batch size, daily output and anything else *</label><textarea id="f-msg" required></textarea></div>
<div class="btns"><button class="btn btn-f" type="submit">Request a quote</button><a class="lnk" href="compare.html">Compare models first</a></div></form>
</div></section></main>{foot()}'''
    return head("Request a quote — OTL Roaster", "Request a quote for an OTL roaster or equipment.") + body

# ======================================================================= ghi
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in ("site.css", "site.js"):
        shutil.copy(HERE / f, OUT / f)
    shutil.copy(HERE / "motion.js", OUT / "motion.js")
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
