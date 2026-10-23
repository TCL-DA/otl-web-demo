"""Hồi quy các lỗi menu, gallery, giảm chuyển động và phục hồi tải 3D.

Chạy tại gốc kho mã: python -u -X utf8 _src/apple/kiem_tuong_tac.py
Máy chủ chỉ nghe trên localhost; dữ liệu biểu mẫu không được gửi ra ngoài.
"""
import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parents[2] / "apple"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def run(browser, base):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.goto(base, wait_until="networkidle")
    assert page.locator("html").get_attribute("data-theme") == "dark", "Gallery chưa mặc định tối"
    page.locator(".burger").focus()
    page.keyboard.press("Enter")
    page.wait_for_timeout(150)
    assert page.locator(".mnav-x").evaluate("e=>e===document.activeElement"), "Menu không nhận focus"
    page.keyboard.press("Shift+Tab")
    assert page.locator(".mnav .theme-t").evaluate("e=>e===document.activeElement"), "Shift+Tab thoát menu"
    page.keyboard.press("Tab")
    assert page.locator(".mnav-x").evaluate("e=>e===document.activeElement"), "Tab thoát menu"
    assert page.locator("main").evaluate("e=>e.inert"), "Nền chưa được khóa tương tác"
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    assert page.locator(".burger").evaluate("e=>e===document.activeElement"), "Không trả focus khi đóng"
    page.evaluate("""async()=>{
      const b=document.querySelector('.burger');
      b.click(); b.click(); await new Promise(r=>setTimeout(r,50)); b.click();
    }""")
    page.wait_for_timeout(600)
    state = page.evaluate("""()=>({open:document.querySelector('.burger').getAttribute('aria-expanded'),
      hidden:document.querySelector('.mnav').hidden,locked:document.documentElement.classList.contains('m-lock')})""")
    assert state == {"open": "true", "hidden": False, "locked": True}, state
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    assert not page.locator("main").evaluate("e=>e.inert"), "Nền còn inert sau khi đóng"
    print("DAT menu: focus, Tab, Escape, mở lại nhanh, trả tương tác nền")

    page.goto(base + "otl-06.html", wait_until="networkidle")
    thumbs = page.locator(".pg-t button")
    last_alt = thumbs.last.get_attribute("data-alt")
    page.evaluate("""()=>{
      const bs=[...document.querySelectorAll('.pg-t button')];
      bs.slice(1).forEach(b=>b.click());
    }""")
    page.wait_for_function("document.querySelector('.pg-main img').alt === document.querySelector('.pg-t button:last-child').dataset.alt")
    page.wait_for_timeout(800)
    assert page.locator(".pg-main img").count() == 1
    assert page.locator(".pg-main img").get_attribute("alt") == last_alt
    assert page.locator('.pg-t button[aria-pressed="true"]').count() == 1
    assert thumbs.last.get_attribute("aria-pressed") == "true"
    print("DAT gallery: bấm nhanh, đúng ảnh/mô tả/trạng thái chọn")
    ctx.close()

    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, permissions=["clipboard-read", "clipboard-write"], reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(base, wait_until="networkidle")
    for batch, expected in [(0.5, "OTL-1.2"), (0.75, "OTL-1.2"), ("0,75", "OTL-1.2"), (1.2, "OTL-1.2"), (1.25, "OTL-03"), ("1,25", "OTL-03"), (3, "OTL-03"), (6, "OTL-06"), (12, "OTL-12"), (15, "OTL-15"), (30, "OTL-30"), (60, "OTL-60"), (120, "OTL-120")]:
        page.locator("#finder-batch").fill(str(batch))
        page.locator("[data-finder-form] button").click()
        assert page.locator("[data-finder-title]").inner_text() == expected, (batch, expected)
        assert expected in page.locator("[data-finder-quote]").get_attribute("href")
    for batch in [121, 500]:
        page.locator("#finder-batch").fill(str(batch));page.locator("[data-finder-form] button").click()
        assert "theo yêu cầu" in page.locator("[data-finder-title]").inner_text()
        assert "model=" in page.locator("[data-finder-quote]").get_attribute("href")
    for batch in ["", "0.4", "501", "abc", "1,2,3", "-1"]:
        page.locator("#finder-batch").fill(batch);page.locator("[data-finder-form] button").click()
        assert page.locator("#finder-batch").get_attribute("aria-invalid") == "true"
        assert not page.locator("[data-finder-quote]").is_visible()
    print("DAT chọn máy: các mốc dải mẻ, cấu hình riêng và giá trị không hợp lệ")

    page.goto(base + "quote.html?model=OTL-30", wait_until="networkidle")
    posts = []
    page.on("request", lambda r: posts.append(r.url) if r.method == "POST" else None)
    text = '<img src=x onerror="alert(1)"> cần tư vấn máy rang'
    page.locator("#f-name").fill("Khách kiểm tra")
    page.locator("#f-mail").fill("test@example.com")
    page.locator("#f-country").fill("Việt Nam")
    page.locator("#f-msg").fill(text)
    original = page.locator("form[data-request] button[type=submit]").inner_text()
    page.locator("form[data-request] button[type=submit]").click()
    assert page.locator(".request-preview").is_visible()
    assert text in page.locator(".request-preview").inner_text()
    assert page.locator(".request-preview img").count() == 0
    email = page.locator('.request-preview a[href^="mailto:"]').get_attribute("href")
    assert email.startswith("mailto:otlpro.com@gmail.com?") and "OTL-30" in email
    assert not posts and "quote.html" in page.url, "Chuẩn bị yêu cầu đã tự gửi hoặc điều hướng"
    page.locator("[data-request-copy]").click()
    copied = page.evaluate("navigator.clipboard.readText()")
    assert text in copied and "OTL-30" in copied
    page.locator("#f-msg").fill("Nhu cầu mới")
    assert page.locator(".request-preview").count() == 0, "Còn bản yêu cầu cũ sau khi sửa"
    assert page.locator("form[data-request] button[type=submit]").inner_text() == original
    print("DAT tư vấn: bản xem trước, mã hóa email, sao chép, không tự gửi, sửa lại nội dung")
    ctx.close()

    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(base + "compare.html", wait_until="networkidle")
    page.select_option("#cmp2", "otl-120")
    page.locator(".chat-b").click()
    moving = page.evaluate("""()=>document.getAnimations().filter(a=>a.effect.getTiming().duration>1 &&
      a.effect.getKeyframes().some(k=>k.transform && k.transform!=='none')).length""")
    assert moving == 0, f"Còn {moving} chuyển động khi đã chọn giảm chuyển động"
    page.goto(base + "roasters.html", wait_until="networkidle")
    page.locator("[data-next]").click()
    position = page.locator(".rail").evaluate("e=>e.scrollLeft")
    assert position > 100, f"Băng chuyền chưa cuộn tức thì: {position}"
    print("DAT giảm chuyển động: so sánh, chat, băng chuyền")
    ctx.close()

    # Chặn đúng thư viện 3D để tái hiện lỗi mạng; lần thử lại dùng thư viện và mô hình thật.
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    pattern = "**/model-viewer.min.js*"
    blocked = []
    def block_library(route):
        blocked.append(route.request.url)
        route.abort()
    page.route(pattern, block_library)
    page.goto(base + "destoner.html", wait_until="networkidle")
    page.locator(".v3d button").click()
    page.wait_for_function("!document.querySelector('.v3d button').disabled", timeout=20000)
    assert blocked, "Chưa chặn được thư viện nên chưa tái hiện lỗi mạng"
    assert page.locator(".v3d-status").is_visible(), "Lỗi tải 3D chưa có thông báo"
    assert page.locator(".v3d button").inner_text().strip(), "Nút thử lại không có nhãn"
    page.unroute(pattern)
    page.locator(".v3d button").click()
    page.wait_for_function("document.querySelector('.v3d').classList.contains('on')", timeout=60000)
    page.wait_for_timeout(200)
    assert page.locator(".v3d model-viewer").count() == 1, "Trình xem bị nhân đôi khi thử lại"
    assert page.locator(".v3d > button").count() == 0
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_timeout(100)
    assert not page.locator(".v3d model-viewer").evaluate("e=>e.hasAttribute('auto-rotate')")
    print("DAT 3D: lỗi CDN phục hồi được, thử lại tải mô hình thật")
    ctx.close()


if __name__ == "__main__":
    handler = functools.partial(QuietHandler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                run(browser, f"http://127.0.0.1:{server.server_port}/")
            finally:
                browser.close()
        print("\nDAT toàn bộ hồi quy tương tác")
    finally:
        server.shutdown()
        server.server_close()
