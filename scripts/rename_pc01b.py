"""Rename tab lewat menu klik kanan pada tab 'PC 1'."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ids = {int(m["n"]): m["id"] for m in
       json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{ids[1]}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)
    tab = None
    for t in p.query_selector_all(".docs-sheet-tab"):
        if (t.inner_text() or "").strip() == "PC 1":
            tab = t
            break
    print("tab found:", bool(tab))
    tab.click(button="right")
    p.wait_for_timeout(1200)
    items = p.query_selector_all('[role="menuitem"]')
    texts = [(el.inner_text() or "").strip() for el in items]
    print("menu items:", texts)
    clicked = False
    for el in items:
        txt = (el.inner_text() or "").strip().lower()
        if txt in ("rename", "ganti nama"):
            el.click()
            clicked = True
            break
    print("rename clicked:", clicked)
    p.wait_for_timeout(1500)
    cands = p.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('input, textarea, [contenteditable="true"]')) {
        const bb = el.getBoundingClientRect();
        if (bb.width > 0 && bb.height > 0) {
          out.push({tag: el.tagName, cls: (el.className||'').toString().slice(0,80),
                    val: el.value || el.innerText || '',
                    x: Math.round(bb.x), y: Math.round(bb.y)});
        }
      }
      return out;
    }""")
    for c in cands:
        print("cand:", c)
    if clicked:
        # input rename sheet biasanya dialog; cari input yg bukan docs-title-input
        target = None
        for c in cands:
            if "docs-title-input" not in c["cls"] and c["y"] > 100:
                target = c
                break
        if target:
            p.mouse.click(target["x"] + 20, target["y"] + 8)
            p.wait_for_timeout(300)
            p.keyboard.press("Control+a")
            p.keyboard.type("PC 01")
            p.wait_for_timeout(300)
            p.keyboard.press("Enter")
        else:
            p.wait_for_timeout(800)
            p.screenshot(path=str(ROOT / "data" / "rename_menu.png"))
    p.wait_for_timeout(3500)
    print("tabs now:", [t.inner_text().strip() for t in p.query_selector_all(".docs-sheet-tab")])
    p.screenshot(path=str(ROOT / "data" / "rename_after.png"))
    p.close(); b.close()
