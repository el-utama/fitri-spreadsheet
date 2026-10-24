"""Izinkan IMPORTRANGE: klik nyata tombol 'Allow access' via koordinat bounding box."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)
    for t in p.query_selector_all(".docs-sheet-tab"):
        if "RINGKASAN" in (t.inner_text() or ""):
            t.click()
            break
    p.wait_for_timeout(2500)
    namebox = p.locator("#t-name-box").first

    for r in range(2, 14):
        namebox.click(); p.wait_for_timeout(150)
        namebox.fill(f"C{r}")
        p.keyboard.press("Enter")
        p.wait_for_timeout(1200)

        rec = p.evaluate(
            """() => {
              const cands = Array.from(document.querySelectorAll('[role="button"], .docs-butterbar-control, div.GoogleObainlessInput'));
              for (const el of cands) {
                const t = (el.innerText || '').toLowerCase();
                if (t.trim() === 'allow access') {
                  const bb = el.getBoundingClientRect();
                  return {x: bb.x + bb.width/2, y: bb.y + bb.height/2, w: bb.width, h: bb.height,
                          visible: bb.width > 0 && bb.height > 0};
                }
              }
              return null;
            }""")
        if not rec or not rec["visible"]:
            print(f"[{r-1}] tidak ada tombol visible (skip)")
            continue
        p.mouse.click(rec["x"], rec["y"])
        p.wait_for_timeout(3000)
        # konfirmasi: popup masih ada?
        still = p.evaluate(
            """() => Array.from(document.querySelectorAll('[role="button"]'))
                 .some(el => ((el.innerText||'').toLowerCase().trim() === 'allow access'
                              && el.getBoundingClientRect().width > 0))""")
        print(f"[{r-1}]", "klik di", round(rec["x"]), round(rec["y"]),
              "| popup masih:", still)

    p.wait_for_timeout(10000)
    p.screenshot(path=str(ROOT / "output" / "ringkasan_final2.png"))
    p.close(); b.close()
