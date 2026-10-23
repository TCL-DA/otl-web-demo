"""Kiểm tra demo otlpro — 'tuyệt đối không lỗi'. Mỗi file phải ĐẠT hết:
lỗi console/JS/request = 0 · ảnh hỏng = 0 · tràn ngang = 0 (1440 & 390) · ảnh anh-goc ≥ 20 · sản phẩm = 5
· phần tử kẹt ẩn sau khi lướt hết = 0 · animation đã chạy ≥ 100 · tác vụ luồng chính > 16,7 ms khi cuộn = 0
· tương tác: menu, đổi ảnh, lọc, form."""
import json, statistics, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(r"F:\Kho-anh\09_Thiet-ke-khac\261023_web-otlpro\demo")
SH = Path(__file__).parent / "soat"; SH.mkdir(exist_ok=True)

SAMPLER = """
window.__S=new Set();window.__F=[];window.__rec=false;
setInterval(()=>{try{document.getAnimations().forEach(a=>__S.add(a))}catch(e){}},25);
(function loop(t){if(window.__rec){__F.push(t)}requestAnimationFrame(loop)})();
"""
# kẹt = (a) phần tử có hiệu ứng mà lướt hết trang vẫn chưa chạy, (b) đã chạy xong mà vẫn mờ / co về 0
# (trừ chỗ thiết kế cố ý: ảnh nhỏ chưa chọn, phần tử đang chạy hiệu ứng lặp, phần tử bị ẩn)
STUCK = """()=>{const out=[];const nm=el=>(el.tagName+'.'+(typeof el.className==='string'?el.className:'')+' «'+(el.textContent||'').trim().slice(0,24)+'»');
  document.querySelectorAll('body *').forEach(el=>{
    if(el.closest('.mnav,.totop,[hidden],.m-cover')) return;
    const target=el._m||el.classList.contains('m-i')||el.classList.contains('m-c');
    if(!target||!el.getClientRects().length) return;
    if(!el.classList.contains('m-done')&&!el.classList.contains('m-split')){out.push('CHUA CHAY '+nm(el));return;}
    if(el.matches('.pg-t button:not(.on)')) return;
    if(el.getAnimations().length) return;
    const cs=getComputedStyle(el);
    if(parseFloat(cs.opacity)<0.99||/^matrix\\(0,/.test(cs.transform)) out.push('MO '+nm(el)+' op='+cs.opacity);
  });return out.slice(0,20)}"""

def tasks_long(evs):
    main = None
    for e in evs:
        if e.get("name") == "thread_name" and e.get("args", {}).get("name") == "CrRendererMain":
            main = (e["pid"], e["tid"]); break
    d = [e.get("dur", 0) / 1000 for e in evs if e.get("ph") == "X" and e.get("name") in ("RunTask", "ThreadControllerImpl::RunTask") and (e["pid"], e["tid"]) == main]
    return sorted(d, reverse=True)

def scroll_all(pg, rec=False):
    pg.mouse.move(700, 450)
    h = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < h:
        pg.mouse.wheel(0, 140); pg.wait_for_timeout(33); y += 140
        h = pg.evaluate("document.documentElement.scrollHeight") if y % 2800 == 0 else h
    pg.wait_for_timeout(1800)

def kiem(name, b):
    url = (OUT / f"{name}.html").as_uri()
    loi, R = [], {}
    # ---------- desktop ----------
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(SAMPLER)
    pg = ctx.new_page()
    errs = []
    pg.on("console", lambda m: m.type == "error" and errs.append("console: " + m.text[:160]))
    pg.on("pageerror", lambda e: errs.append("js: " + str(e)[:160]))
    pg.on("requestfailed", lambda r: errs.append("request: " + r.url[:100]))
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(2500)
    R["anh_goc"] = pg.evaluate("new Set([...document.querySelectorAll('img[data-k]')].map(i=>i.dataset.k).filter(k=>/^a\\d+$/.test(k))).size")
    R["san_pham"] = pg.evaluate("document.querySelectorAll('[data-product]').length")
    # cuộn có đo
    cdp = ctx.new_cdp_session(pg); evs = []; done = []
    cdp.on("Tracing.dataCollected", lambda ev: evs.extend(ev["value"]))
    cdp.on("Tracing.tracingComplete", lambda ev: done.append(1))
    cdp.send("Tracing.start", {"categories": "devtools.timeline,toplevel", "transferMode": "ReportEvents"})
    pg.evaluate("window.__rec=true")
    scroll_all(pg)
    pg.evaluate("window.__rec=false")
    cdp.send("Tracing.end")
    while not done: pg.wait_for_timeout(100)
    d = tasks_long(evs)
    F = pg.evaluate("window.__F")
    iv = [F[i + 1] - F[i] for i in range(len(F) - 1)]
    R["task>16.7ms"] = sum(1 for x in d if x > 16.7)
    R["task_max_ms"] = round(d[0], 1) if d else 0
    R["frame_p50_ms"] = round(statistics.median(iv), 1) if iv else None
    R["frame_p95_ms"] = round(sorted(iv)[int(len(iv) * .95)], 1) if iv else None
    R["frame>25ms_%"] = round(100 * sum(1 for x in iv if x > 25) / max(1, len(iv)), 2)
    R["fps_tb"] = round(1000 / statistics.mean(iv), 1) if iv else None
    R["anim_da_chay"] = pg.evaluate("__S.size")
    R["waapi"] = pg.evaluate("window.OTLM?OTLM.n:0")
    R["css_lap"] = pg.evaluate("[...__S].filter(a=>a.animationName).length")
    R["ket_an"] = pg.evaluate(STUCK)
    R["anh_hong"] = pg.evaluate("[...document.images].filter(i=>i.src&&(!i.complete||!i.naturalWidth)).map(i=>i.dataset.k||i.src.slice(0,40))")
    R["tran_ngang_1440"] = pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
    # tương tác desktop: đổi ảnh, lọc, form
    g = pg.evaluate("""async()=>{const g=document.querySelector('.pg');if(!g)return 'khong co';const b=g.querySelectorAll('.pg-t button')[1];
       b.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,300));b.click();await new Promise(r=>setTimeout(r,900));
       return g.querySelector('.pg-main img').src===OTLM.src(b.dataset.k)&&g.querySelectorAll('.pg-main img').length===1?'ok':'LOI'}""")
    R["doi_anh"] = g
    # bấm liên kết nội trang: mục đích không được nằm khuất dưới thanh menu dính/cố định
    R["menu_che"] = pg.evaluate("""async()=>{const out=[];const ids=[...new Set([...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href')).filter(h=>h.length>1))];
      for(const h of ids){const t=document.querySelector(h);if(!t)continue;
        document.documentElement.style.scrollBehavior='auto';t.scrollIntoView();await new Promise(r=>setTimeout(r,120));
        let bar=0;document.querySelectorAll('body *').forEach(e=>{const cs=getComputedStyle(e);if((cs.position==='sticky'||cs.position==='fixed')&&!e.matches('.progress,.totop,.mnav,[hidden]')){const r=e.getBoundingClientRect();if(r.top<=1&&r.height>20&&r.height<240&&r.width>innerWidth*.5)bar=Math.max(bar,r.bottom)}});
        const top=t.getBoundingClientRect().top;if(top<bar-2)out.push(h+' bi che '+Math.round(bar-top)+'px')}
      document.documentElement.style.scrollBehavior='';return out}""")
    f = pg.evaluate("""async()=>{const G=document.querySelector('[data-filter-group]');if(!G)return 'khong co';
       const items=[...document.querySelectorAll(G.getAttribute('data-filter-group'))];const bs=[...G.querySelectorAll('button')];
       bs[bs.length-1].click();await new Promise(r=>setTimeout(r,600));const vis1=items.filter(i=>!i.hidden).length;
       bs[0].click();await new Promise(r=>setTimeout(r,600));const vis2=items.filter(i=>!i.hidden).length;
       return (vis1>0&&vis1<items.length&&vis2===items.length)?'ok':'LOI '+vis1+'/'+vis2}""")
    R["loc"] = f
    fm = pg.evaluate("""async()=>{const f=document.querySelector('form[data-demo]');if(!f)return 'khong co';const b=f.querySelector('button[type=submit]');const t0=b.textContent;
       f.requestSubmit();await new Promise(r=>setTimeout(r,500));const bad=f.querySelectorAll('.m-bad').length;
       f.querySelectorAll('input,textarea').forEach(i=>{i.value=i.type==='email'?'a@b.co':'Test'});f.requestSubmit();await new Promise(r=>setTimeout(r,700));
       const con=f.querySelectorAll('.m-bad').length;
       return (bad>0&&b.textContent!==t0&&con===0)?'ok':'LOI bad='+bad+' con_do='+con}""")
    R["form"] = fm
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(500)
    pg.screenshot(path=str(SH / f"{name}_d.png"), full_page=True)
    R["loi_trang"] = list(errs)
    ctx.close()
    # ---------- mobile ----------
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    ctx.add_init_script(SAMPLER)
    pg = ctx.new_page(); errs2 = []
    pg.on("pageerror", lambda e: errs2.append("js: " + str(e)[:160]))
    pg.on("console", lambda m: m.type == "error" and errs2.append("console: " + m.text[:160]))
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(1500)
    mn = pg.evaluate("""async()=>{const b=document.querySelector('.burger'),p=document.querySelector('.mnav');if(!b||!p)return 'khong co';
       if(getComputedStyle(b).display==='none')return 'LOI burger an';b.click();await new Promise(r=>setTimeout(r,900));
       const open=!p.hidden&&getComputedStyle(p).opacity>.99;const a=p.querySelector('a');a.click();await new Promise(r=>setTimeout(r,600));
       return open&&p.hidden?'ok':'LOI open='+open+' hidden='+p.hidden}""")
    R["menu_dt"] = mn
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(1500)
    for _ in range(int(pg.evaluate("document.documentElement.scrollHeight") / 500) + 3):
        pg.evaluate("scrollBy(0,500)"); pg.wait_for_timeout(120)
    pg.wait_for_timeout(1800)
    R["tran_ngang_390"] = pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
    # chữ dính mép: phần tử có chữ trực tiếp mà mép trái/phải cách màn hình < 10px (trừ vùng cuộn ngang, phần tử cố định)
    R["sat_mep_390"] = pg.evaluate("""()=>{const out=[];const W=innerWidth;
      document.querySelectorAll('body *').forEach(el=>{
        if(el.closest('[hidden],.mnav,.marquee,.marq,.track,.co')) return;
        for(let a=el.parentElement;a&&a!==document.body;a=a.parentElement){const ox=getComputedStyle(a).overflowX;if(ox==='auto'||ox==='scroll')return;}  /* vùng cuộn ngang có chủ đích */
        const cs=getComputedStyle(el); if(cs.position==='fixed'||cs.display==='none'||cs.visibility==='hidden') return;
        const txt=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1); if(!txt) return;
        const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
        const rg=document.createRange(); rg.selectNodeContents(el); const t=rg.getBoundingClientRect();
        if(t.left<10||t.right>W-10) out.push(el.tagName+'.'+(typeof el.className==='string'?el.className:'')+' «'+el.textContent.trim().slice(0,30)+'» L='+Math.round(t.left)+' R='+Math.round(W-t.right));
      });return out.slice(0,12)}""")
    R["ket_an_390"] = pg.evaluate(STUCK)
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(400)
    pg.screenshot(path=str(SH / f"{name}_m.png"), full_page=True)
    R["loi_trang"] += errs2
    ctx.close()
    # ---------- kết luận ----------
    if R["loi_trang"]: loi.append("loi trang")
    if R["anh_hong"]: loi.append("anh hong")
    if R["tran_ngang_1440"] or R["tran_ngang_390"]: loi.append("tran ngang")
    if R["anh_goc"] < 20: loi.append("anh<20")
    if R["san_pham"] != 5: loi.append("san pham!=5")
    if R["ket_an"] or R["ket_an_390"]: loi.append("ket an")
    if R["sat_mep_390"]: loi.append("chu sat mep")
    if R["menu_che"]: loi.append("menu che tieu de")
    if R["anim_da_chay"] < 100: loi.append("anim<100")
    if R["task>16.7ms"]: loi.append("task>16.7ms")
    for k in ("doi_anh", "loc", "form", "menu_dt"):
        if str(R[k]).startswith("LOI"): loi.append(k)
    R["KET_QUA"] = "DAT" if not loi else "CHUA DAT: " + ", ".join(loi)
    return R

with sync_playwright() as p:
    import os
    kw = {"channel": "chrome", "headless": True} if os.environ.get("OTL_CHROME") else {}   # OTL_CHROME=1: Chrome thật, có GPU
    b = p.chromium.launch(args=["--enable-gpu-rasterization", "--disable-renderer-backgrounding", "--disable-background-timer-throttling", "--ignore-gpu-blocklist"], **kw)
    tong = {}
    for name in sys.argv[1:]:
        R = kiem(name, b); tong[name] = R
        print(f"\n=== {name}: {R['KET_QUA']}")
        for k, v in R.items():
            if k != "KET_QUA": print(f"  {k:16s} {v}")
    b.close()
(Path(__file__).parent / "kiem_ket_qua.json").write_text(json.dumps(tong, ensure_ascii=False, indent=1), encoding="utf-8")
