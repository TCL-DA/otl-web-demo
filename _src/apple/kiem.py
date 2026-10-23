"""Kiểm bản demo nhiều trang (apple/) — trang nào cũng phải ĐẠT hết:
lỗi console/JS/request = 0 · ảnh hỏng = 0 · liên kết nội bộ hỏng = 0 · tràn ngang = 0 (1440 & 390)
· phần tử kẹt ẩn sau khi lướt hết = 0 · chữ sát mép 390 = 0 · thanh dính che tiêu đề = 0
· tương tác có trên trang (thư viện ảnh, so sánh, biểu mẫu, menu điện thoại, băng chuyền) chạy đúng
· tác vụ luồng chính > 50 ms khi cuộn = 0 (đo trên trang chủ + trang dòng máy).
Chạy:  python kiem.py            (mọi trang)   |   python kiem.py index otl-06   (vài trang)"""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
SITE = Path(__file__).parent.parent.parent / "apple"

STUCK = """()=>{const out=[];const nm=el=>(el.tagName+'.'+(typeof el.className==='string'?el.className:'')+' «'+(el.textContent||'').trim().slice(0,24)+'»');
  document.querySelectorAll('body *').forEach(el=>{
    if(el.closest('.mnav,[hidden],.fly')) return;
    if(!el._m||!el.getClientRects().length) return;
    if(!el.classList.contains('m-done')&&!el.classList.contains('m-split')){out.push('CHUA CHAY '+nm(el));return;}
    if(el.getAnimations().length) return;
    const cs=getComputedStyle(el);
    if(parseFloat(cs.opacity)<0.99) out.push('MO '+nm(el)+' op='+cs.opacity);
  });
  /* phần tử bị CSS ẩn vĩnh viễn (vd quy tắc hiệu ứng viết sai làm opacity 0 không có hiệu ứng nào gỡ) */
  document.querySelectorAll('main *').forEach(el=>{
    if(el.closest('[hidden],.fly')) return; const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
    if(el.getAnimations().length) return;
    const t=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1);
    if(t&&parseFloat(getComputedStyle(el).opacity)<0.99) out.push('AN '+nm(el));
  });return out.slice(0,15)}"""

SAT_MEP = """()=>{const out=[];const W=innerWidth;
  document.querySelectorAll('body *').forEach(el=>{
    if(el.closest('[hidden],.mnav,.fly')) return;
    for(let a=el.parentElement;a&&a!==document.body;a=a.parentElement){const ox=getComputedStyle(a).overflowX;if(ox==='auto'||ox==='scroll')return;}
    const cs=getComputedStyle(el); if(cs.position==='fixed'||cs.display==='none'||cs.visibility==='hidden') return;
    const txt=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1); if(!txt) return;
    const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
    const rg=document.createRange(); rg.selectNodeContents(el); const t=rg.getBoundingClientRect();
    if(t.left<10||t.right>W-10) out.push(el.tagName+'.'+(typeof el.className==='string'?el.className:'')+' «'+el.textContent.trim().slice(0,30)+'» L='+Math.round(t.left)+' R='+Math.round(W-t.right));
  });return out.slice(0,12)}"""

MENU_CHE = """async()=>{const out=[];const ids=[...new Set([...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href')).filter(h=>h.length>1))];
  for(const h of ids){const t=document.querySelector(h);if(!t)continue;
    document.documentElement.style.scrollBehavior='auto';t.scrollIntoView();await new Promise(r=>setTimeout(r,150));
    let bar=0;document.querySelectorAll('body *').forEach(e=>{const cs=getComputedStyle(e);if((cs.position==='sticky'||cs.position==='fixed')&&!e.matches('.mnav,[hidden]')){const r=e.getBoundingClientRect();if(r.top<=1&&r.height>20&&r.height<240&&r.width>innerWidth*.5)bar=Math.max(bar,r.bottom)}});
    const top=t.getBoundingClientRect().top;if(top<bar-2)out.push(h+' bi che '+Math.round(bar-top)+'px')}
  document.documentElement.style.scrollBehavior='';scrollTo(0,0);return out}"""

# Tương phản: chữ thường cần 4,5:1, chữ lớn cần 3:1; không thay thế kiểm tra thủ công chữ nằm trên ảnh.
TUONG_PHAN = """()=>{const out=[];const rgb=s=>{const m=s.match(/[\\d.]+/g);return m?m.map(Number):[0,0,0,0]};
  const L=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
  document.querySelectorAll('body *').forEach(el=>{
    if(el.closest('[hidden],.mnav,.fly,svg')) return;
    const txt=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1); if(!txt) return;
    const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
    const cs=getComputedStyle(el); if(parseFloat(cs.opacity)<.99) return;
    let bg=null;for(let a=el;a;a=a.parentElement){const c=rgb(getComputedStyle(a).backgroundColor);if(c[3]===undefined||c[3]>.5){bg=c;break}}
    if(!bg) bg=[255,255,255];const fg=rgb(cs.color);
    const l1=L(fg),l2=L(bg),k=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
    const large=parseFloat(cs.fontSize)>=24||(parseFloat(cs.fontSize)>=18.66&&parseInt(cs.fontWeight,10)>=700);
    if(k<(large?3:4.5)) out.push(el.tagName+' «'+el.textContent.trim().slice(0,26)+'» '+k.toFixed(2)+':1');
  });return out.slice(0,10)}"""

def lot(pg, step=420, pause=50):
    h = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < h + 900:
        pg.evaluate(f"scrollTo(0,{y})"); pg.wait_for_timeout(pause); y += step
    pg.wait_for_timeout(1600)

def tasks_long(evs):
    main = next(((e["pid"], e["tid"]) for e in evs if e.get("name") == "thread_name" and e.get("args", {}).get("name") == "CrRendererMain"), None)
    return sorted((e.get("dur", 0) / 1000 for e in evs if e.get("ph") == "X" and e.get("name") in ("RunTask", "ThreadControllerImpl::RunTask")
                   and (e["pid"], e["tid"]) == main), reverse=True)


def kiem_tuong_phan(name, browser):
    """Rà chữ nhỏ trên cả hai giao diện; giảm chuyển động để mọi nội dung xuất hiện ngay."""
    result = {}
    for theme in ("light", "dark"):
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        ctx.add_init_script(f"try{{localStorage.setItem('otl-theme','{theme}')}}catch(e){{}}")
        page = ctx.new_page()
        page.goto((SITE / f"{name}.html").as_uri(), wait_until="networkidle")
        result[theme] = page.evaluate(TUONG_PHAN)
        ctx.close()
    result["KET_QUA"] = "DAT" if not result["light"] and not result["dark"] else "CHUA DAT: tuong phan"
    return result

def kiem(name, b):
    R, url = {}, (SITE / f"{name}.html").as_uri()
    # ---------- máy tính ----------
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, permissions=["clipboard-read", "clipboard-write"])
    ctx.add_init_script("try{localStorage.setItem('otl-theme','light')}catch(e){}")
    pg = ctx.new_page(); errs = []
    pg.on("console", lambda m: m.type == "error" and errs.append("console: " + m.text[:160]))
    pg.on("pageerror", lambda e: errs.append("js: " + str(e)[:160]))
    pg.on("requestfailed", lambda r: errs.append("request: " + r.url[:110]))
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(800)
    R["ngon_ngu"] = "ok" if pg.locator("html").get_attribute("lang") == "vi" else "LOI lang khong phai vi"
    hrefs = pg.evaluate("[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))")
    R["lien_ket_hong"] = sorted({h for h in hrefs if not re.match(r"(https?:|mailto:|tel:|#)", h)
                                 and not (SITE / h.split("?")[0].split("#")[0]).exists()})
    if name in ("index", "roasters"):
        cdp = ctx.new_cdp_session(pg); evs, done = [], []
        cdp.on("Tracing.dataCollected", lambda ev: evs.extend(ev["value"])); cdp.on("Tracing.tracingComplete", lambda ev: done.append(1))
        cdp.send("Tracing.start", {"categories": "devtools.timeline,toplevel", "transferMode": "ReportEvents"})
        pg.mouse.move(700, 450)
        for _ in range(int(pg.evaluate("document.documentElement.scrollHeight") / 140) + 8):
            pg.mouse.wheel(0, 140); pg.wait_for_timeout(33)
        cdp.send("Tracing.end")
        while not done: pg.wait_for_timeout(100)
        d = tasks_long(evs); R["task>50ms"] = sum(1 for x in d if x > 50); R["task_max_ms"] = round(d[0], 1) if d else 0
        pg.wait_for_timeout(1200)
    lot(pg)
    R["ket_an"] = pg.evaluate(STUCK)
    R["anh_hong"] = pg.evaluate("[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src'))")
    R["tran_1440"] = pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
    R["menu_che"] = pg.evaluate(MENU_CHE)
    if pg.query_selector(".pg"):
        R["doi_anh"] = pg.evaluate("""async()=>{const g=document.querySelector('.pg');const b=g.querySelectorAll('.pg-t button')[1];
          b.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,300));b.click();await new Promise(r=>setTimeout(r,900));
          const im=g.querySelectorAll('.pg-main img');return im.length===1&&im[0].src===new URL(OTLM.src(b.dataset.k),location.href).href?'ok':'LOI'}""")
    if pg.query_selector("[data-rail]"):
        R["bang_chuyen"] = pg.evaluate("""async()=>{const r=document.querySelector('.rail'),n=document.querySelector('[data-next]'),p=document.querySelector('[data-prev]');
          r.scrollIntoView({block:'center'});await new Promise(x=>setTimeout(x,300));const p0=p.disabled,x0=r.scrollLeft;n.click();await new Promise(x=>setTimeout(x,900));
          return p0&&r.scrollLeft>x0+100&&!p.disabled?'ok':'LOI p0='+p0+' x='+x0+'->'+r.scrollLeft}""")
    if pg.query_selector(".cmp"):
        R["so_sanh"] = pg.evaluate("""async()=>{const s=document.getElementById('cmp2');s.value='otl-120';s.dispatchEvent(new Event('change'));
          await new Promise(r=>setTimeout(r,300));const c=s.closest('.cmp-col');
          return c.querySelector('[data-f=name]').textContent==='OTL-120'&&c.querySelector('[data-k=batch]').textContent==='60–120 kg'?'ok':'LOI'}""")
    if pg.query_selector("form[data-demo]"):
        R["bieu_mau"] = pg.evaluate("""async()=>{const f=document.querySelector('form[data-demo]');const b=f.querySelector('button[type=submit]');const t0=b.textContent;
          f.requestSubmit();await new Promise(r=>setTimeout(r,500));const bad=f.querySelectorAll('.m-bad').length;
          f.querySelectorAll('[required]').forEach(i=>{i.value=i.type==='email'?'sai-email':'Test'});
          f.requestSubmit();await new Promise(r=>setTimeout(r,200));
          const email=f.querySelector('[type=email]');const blocked=email.classList.contains('m-bad')&&email.getAttribute('aria-invalid')==='true'&&b.textContent===t0;
          email.value='a@b.co';f.requestSubmit();await new Promise(r=>setTimeout(r,700));
          return (bad>0&&blocked&&b.textContent!==t0&&!f.querySelectorAll('.m-bad').length)?'ok':'LOI bad='+bad+' email='+blocked}""")
    R["tuong_phan_sang"] = pg.evaluate(TUONG_PHAN)
    if name == "quote":
        pg.goto(url + "?model=OTL-30", wait_until="networkidle")
        R["dien_san_model"] = "ok" if pg.evaluate("document.getElementById('f-model').value") == "OTL-30" else "LOI"
    if name == "index":
        R["nut_toi"] = pg.evaluate("""async()=>{const d=document.documentElement,b=document.querySelector('.gnav .theme');scrollTo(0,0);
          const t0=d.dataset.theme,bg0=getComputedStyle(document.body).backgroundColor;b.click();await new Promise(r=>setTimeout(r,200));
          const ok=t0==='light'&&d.dataset.theme==='dark'&&localStorage.getItem('otl-theme')==='dark'&&getComputedStyle(document.body).backgroundColor!==bg0
                  &&b.getAttribute('aria-label')==='Chuyển sang giao diện sáng';
          b.click();await new Promise(r=>setTimeout(r,200));const back=d.dataset.theme==='light'&&localStorage.getItem('otl-theme')==='light';
          localStorage.removeItem('otl-theme');return ok&&back?'ok':'LOI t0='+t0+' t1='+d.dataset.theme}""")
    R["chat"] = pg.evaluate("""async()=>{const b=document.querySelector('.chat-b'),p=document.getElementById('chat-p');if(!b)return 'LOI khong co';
      b.click();await new Promise(r=>setTimeout(r,400));const hs=[...p.querySelectorAll('a')].map(a=>a.href).join(' ');
      const open=!p.hidden&&/wa\\.me/.test(hs)&&/zalo\\.me/.test(hs)&&/m\\.me/.test(hs)&&b.getAttribute('aria-expanded')==='true';
      document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));await new Promise(r=>setTimeout(r,200));
      if(!open||!p.hidden)return 'LOI open='+open+' hidden='+p.hidden;
      const z=document.querySelector('[data-zalo]');z.click();await new Promise(r=>setTimeout(r,500));
      const q=p.querySelector('.zqr');const qr=!p.hidden&&q&&!q.hidden&&!!q.querySelector('svg path')&&location.href.indexOf('zalo')<0;
      document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));await new Promise(r=>setTimeout(r,200));
      return qr&&p.hidden&&q.hidden?'ok':'LOI zalo qr='+qr}""")
    if pg.query_selector(".copy"):
        R["copy"] = pg.evaluate("""async()=>{const bs=[...document.querySelectorAll('.copy')].filter(b=>b.getClientRects().length);if(!bs.length)return 'khong co nut hien';
          const b=bs[0];b.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,200));b.click();await new Promise(r=>setTimeout(r,300));
          let clip='';try{clip=await navigator.clipboard.readText()}catch(e){clip='(khong doc duoc)'}
          const ok=b.classList.contains('ok')&&/Đã chép/.test(b.textContent)&&(clip==='(khong doc duoc)'||clip===b.dataset.copy);
          await new Promise(r=>setTimeout(r,2200));const back=!b.classList.contains('ok')&&/Sao chép/.test(b.textContent.trim())&&!/Đã chép/.test(b.textContent);
          return ok&&back?'ok':'LOI ok='+ok+' back='+back+' clip='+clip.slice(0,30)}""")
    if pg.query_selector(".short button"):
        pg.route("**/*youtube-nocookie.com/**", lambda rt: rt.fulfill(status=200, body="<html></html>", content_type="text/html"))
        R["video"] = pg.evaluate("""async()=>{const b=document.querySelector('.short button');const id=b.dataset.yt;b.scrollIntoView({block:'center'});
          await new Promise(r=>setTimeout(r,300));b.click();await new Promise(r=>setTimeout(r,600));
          const f=document.querySelector('.yt-box iframe');return f&&f.src.includes('/embed/'+id)?'ok':'LOI'}""")
    R["loi_trang"] = list(errs)
    ctx.close()
    # ---------- máy tính, giao diện tối (cách A) ----------
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
    pg = ctx.new_page(); e3 = []
    pg.on("pageerror", lambda e: e3.append("js: " + str(e)[:160])); pg.on("console", lambda m: m.type == "error" and e3.append("console: " + m.text[:160]))
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(500)
    R["toi_tu_bat"] = "ok" if pg.evaluate("document.documentElement.dataset.theme") == "dark" else "LOI"
    lot(pg)
    R["tuong_phan_toi"] = pg.evaluate(TUONG_PHAN)
    R["ket_an_toi"] = pg.evaluate(STUCK)
    R["loi_trang"] += e3
    ctx.close()
    # ---------- điện thoại ----------
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); e2 = []
    pg.on("pageerror", lambda e: e2.append("js: " + str(e)[:160])); pg.on("console", lambda m: m.type == "error" and e2.append("console: " + m.text[:160]))
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(600)
    R["menu_dt"] = pg.evaluate("""async()=>{const b=document.querySelector('.burger'),p=document.querySelector('.mnav');if(!b||!p)return 'khong co';
       if(getComputedStyle(b).display==='none')return 'LOI burger an';b.click();await new Promise(r=>setTimeout(r,900));
       const open=!p.hidden&&getComputedStyle(p).opacity>.99;p.querySelector('.mnav-x').click();await new Promise(r=>setTimeout(r,600));
       return open&&p.hidden?'ok':'LOI open='+open+' hidden='+p.hidden}""")
    lot(pg, 500, 80)
    R["tran_390"] = pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
    R["sat_mep_390"] = pg.evaluate(SAT_MEP)
    R["ket_an_390"] = pg.evaluate(STUCK)
    R["loi_trang"] += e2
    ctx.close()
    loi = [k for k in ("loi_trang", "anh_hong", "lien_ket_hong", "ket_an", "ket_an_390", "ket_an_toi", "sat_mep_390", "menu_che",
                       "tuong_phan_sang", "tuong_phan_toi") if R.get(k)]
    loi += [k for k in ("tran_1440", "tran_390") if R.get(k)]
    loi += [k for k, v in R.items() if isinstance(v, str) and v.startswith("LOI")]
    if R.get("task>50ms"): loi.append("task>50ms")
    R["KET_QUA"] = "DAT" if not loi else "CHUA DAT: " + ", ".join(loi)
    return R

if __name__ == "__main__":
    contrast_only = "--contrast" in sys.argv[1:]
    names = [n for n in sys.argv[1:] if n != "--contrast"] or sorted(p.stem for p in SITE.glob("*.html"))
    tong = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--disable-renderer-backgrounding", "--disable-background-timer-throttling"])
        for n in names:
            R = kiem_tuong_phan(n, b) if contrast_only else kiem(n, b)
            tong[n] = R
            print(f"{n:12s} {R['KET_QUA']}")
            if R["KET_QUA"] != "DAT":
                for k, v in R.items():
                    if k != "KET_QUA" and v not in ([], False, "ok", 0): print(f"    {k}: {v}")
        b.close()
    report = "kiem_tuong_phan.json" if contrast_only else "kiem_ket_qua.json"
    (Path(__file__).parent / report).write_text(json.dumps(tong, ensure_ascii=False, indent=1), encoding="utf-8")
    dat = sum(1 for r in tong.values() if r["KET_QUA"] == "DAT")
    print(f"\n{dat}/{len(tong)} trang DAT")
    sys.exit(0 if dat == len(tong) else 1)
