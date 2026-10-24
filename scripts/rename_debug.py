"""Debug rename tab: dblclick lalu dump input/contenteditable yang visible + screenshot."""
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
    print("tab html:", (tab.inner_html() or "")[:400] if tab else "")
    tab.dblclick()
    p.wait_for_timeout(1500)
    cands = p.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('input, textarea, [contenteditable="true"]')) {
        const bb = el.getBoundingClientRect();
        if (bb.width > 0 && bb.height > 0) {
          out.push({tag: el.tagName, cls: (el.className||'').toString().slice(0,80),
                    type: el.getAttribute('type'), val: el.value || el.innerText || '',
                    x: Math.round(bb.x), y: Math.round(bb.y)});
        }
      }
      return out;
    }""")
    for c in cands:
        print("cand:", c)
    p.screenshot(path=str(ROOT / "data" / "rename_debug.png"))
    # coba ketik langsung
    p.keyboard.press("Control+a")
    p.keyboard.type("PC 01")
    p.wait_for_timeout(300)
    p.keyboard.press("Enter")
    p.wait_for_timeout(3000)
    print("tabs after typing:", [t.inner_text().strip() for t in p.query_selector_all(".docs-sheet-tab")])
    p.screenshot(path=str(ROOT / "data" / "rename_debug2.png"))
    p.close(); b.close()
