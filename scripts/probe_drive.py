import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto("https://drive.google.com/drive/u/0/my-drive", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)
    print("title:", p.title())
    inputs = p.eval_on_selector_all(
        "input[type=file]",
        "els => els.map(e => ({id: e.id, cls: e.className.slice(0,60), acc: (e.getAttribute('aria-label')||'')}))")
    print("file inputs:", inputs)
    btns = p.eval_on_selector_all(
        'div[role=button], button',
        "els => els.slice(0, 60).map(e => ({aria: (e.getAttribute('aria-label')||'').slice(0,50), txt: (e.innerText||'').slice(0,24), id: e.id.slice(0,40)})).filter(x => x.aria || x.txt)")
    seen = set()
    for x in btns:
        k = (x["aria"], x["txt"])
        if k in seen:
            continue
        seen.add(k)
        print("BTN:", x)
    p.close()
    b.close()
