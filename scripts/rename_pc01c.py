"""Rename tab 'PC 1' -> 'PC 01' via mouse click pada item menu yang benar-benar visible."""
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
    tab.click(button="right")
    p.wait_for_timeout(1200)

    rec = p.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('[role="menuitem"]')) {
        if ((el.innerText || '').trim() === 'Rename') {
          const bb = el.getBoundingClientRect();
          const st = getComputedStyle(el);
          out.push({x: Math.round(bb.x), y: Math.round(bb.y),
                    w: Math.round(bb.width), h: Math.round(bb.height),
                    vis: bb.width > 0 && bb.height > 0,
                    pe: st.pointerEvents, disp: st.display,
                    aria: el.getAttribute('aria-disabled')});
        }
      }
      return out;
    }""")
    print("rename items:", rec)
    vis = [r for r in rec if r["vis"] and r["pe"] != "none"]
    if not vis:
        raise SystemExit("tidak ada item Rename visible")
    r0 = vis[0]
    p.mouse.click(r0["x"] + 40, r0["y"] + r0["h"] / 2)
    p.wait_for_timeout(1800)

    cands = p.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('input, textarea, [contenteditable="true"]')) {
        const bb = el.getBoundingClientRect();
        if (bb.width > 0 && bb.height > 0) {
          out.push({tag: el.tagName, cls: (el.className||'').toString().slice(0,90),
                    val: el.value || el.innerText || '',
                    x: Math.round(bb.x), y: Math.round(bb.y),
                    w: Math.round(bb.width), h: Math.round(bb.height)});
        }
      }
      return out;
    }""")
    for c in cands:
        print("cand:", c)
    p.screenshot(path=str(ROOT / "data" / "rename_dialog.png"))

    # Dialog rename sheet: input biasanya satu-satunya input di dialog (bukan title/name box)
    target = None
    for c in cands:
        if "docs-title-input" in c["cls"]:
            continue
        if "waffle-name-box" in c["cls"] or "omnibox" in c["cls"] or "combo-button" in c["cls"]:
            continue
        target = c
        break
    if target:
        p.mouse.click(target["x"] + 30, target["y"] + target["h"] / 2)
        p.wait_for_timeout(400)
        p.keyboard.press("Control+a")
        p.keyboard.type("PC 01")
        p.wait_for_timeout(400)
        p.keyboard.press("Enter")
        p.wait_for_timeout(3500)
    print("tabs now:", [t.inner_text().strip() for t in p.query_selector_all(".docs-sheet-tab")])
    p.screenshot(path=str(ROOT / "data" / "rename_after2.png"))
    p.close(); b.close()
