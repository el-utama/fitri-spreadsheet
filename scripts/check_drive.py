import sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]

    # 1) cek status toggle Convert uploads
    p = ctx.new_page()
    p.goto("https://drive.google.com/drive/u/0/settings", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(4000)
    info = p.eval_on_selector_all(
        '[role="checkbox"], [role="switch"]',
        "els => els.map(e => ({a: e.getAttribute('aria-label'), c: e.getAttribute('aria-checked'), t: (el_t(e)).slice(0,60) }) )"
        .replace("el_t(e)", "(e.closest('label')?e.closest('label').innerText:e.parentElement.innerText)")
    ) or []
    for i in info:
        print("switch:", i)
    p.close()

    # 2) cek isi My Drive / search
    p2 = ctx.new_page()
    p2.goto("https://drive.google.com/drive/u/0/search?q=%22master_karyawan%22", wait_until="domcontentloaded", timeout=90000)
    p2.wait_for_timeout(5000)
    rows = p2.eval_on_selector_all(
        "[data-id]",
        """els => els.map(e => ({
             id: e.getAttribute('data-id'),
             label: (e.getAttribute('aria-label')||''),
             tip: (e.getAttribute('data-tooltip')||'')
           })).filter(r => r.id && r.id.length > 20)""")
    seen = set()
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        print("row:", r["id"], "|", r["label"], "|", r["tip"])
    p2.close()
    b.close()
