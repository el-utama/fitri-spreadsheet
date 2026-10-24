"""Izinkan access IMPORTRANGE utk 12 sumber (klik 'Allow access' per baris RINGKASAN)."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
import pyperclip
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
        # cari tombol 'Allow access'; klik lewat DOM element.click() agar tak
        # diblokir pemeriksaan visibility element (popup docs bisa offscreen)
        btn = p.evaluate(
            """() => {
              const cands = Array.from(document.querySelectorAll('[role="button"], .docs-butterbar-control'));
              for (const el of cands) {
                const t = (el.innerText || el.textContent || '').toLowerCase();
                if (t.trim() === 'allow access' || (t.trim().startsWith('allow') && t.includes('access'))) {
                  el.click();
                  return true;
                }
              }
              return false;
            }""")
        if not btn:
            print(f"[{r-1}] tidak ada popup (mungkin sudah ok)")
            continue
        p.wait_for_timeout(2500)
        print(f"[{r-1}] allow ok")
    p.wait_for_timeout(8000)
    p.screenshot(path=str(ROOT / "output" / "ringkasan_live_final.png"))
    p.close(); b.close()
