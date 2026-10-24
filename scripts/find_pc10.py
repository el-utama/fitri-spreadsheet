import sys, re, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto("https://drive.google.com/drive/u/0/search?q=%22PC%2010%22",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)
    rows = p.eval_on_selector_all(
        "[data-id]",
        """els => els.map(e => ({
             id: e.getAttribute('data-id'),
             label: (e.getAttribute('aria-label')||e.getAttribute('data-tooltip')||'').slice(0,120),
             tag: e.tagName
           })).filter(r => r.id)""")
    seen = set()
    for r in rows:
        key = (r["id"], r["label"])
        if key in seen:
            continue
        seen.add(key)
        if "PC 10" in r["label"] or re.match(r"^[a-zA-Z0-9-_]{25,}$", r["id"]):
            print(r["tag"], r["id"], "|", r["label"])
    p.close()
    b.close()
