"""Izinkan IMPORTRANGE utk 12 sumber: pilih sel C{r}, tunggu popup,
klik koordinat tombol 'Allow access' yang VISIBLE (jfk-button di annotation-overlay)."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

FIND_BTN = """() => {
  const btns = Array.from(document.querySelectorAll(
      '.annotation-overlaywithallowaccess .jfk-button'));
  for (const el of btns) {
    const t = (el.innerText || '').trim();
    if (t === 'Allow access') {
      const bb = el.getBoundingClientRect();
      if (bb.width > 10 && bb.height > 10) {
        return {x: bb.x + bb.width/2, y: bb.y + bb.height/2, w: bb.width, h: bb.height};
      }
    }
  }
  return null;
}"""

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)
    for t in p.query_selector_all(".docs-sheet-tab"):
        if "RINGKASAN" in (t.inner_text() or ""):
            t.click()
            break
    p.wait_for_timeout(2500)
    nb = p.locator("#t-name-box").first

    for r in range(2, 14):
        nb.click(); p.wait_for_timeout(150)
        nb.fill(f"C{r}")
        p.keyboard.press("Enter")
        done = False
        for attempt in range(3):
            p.wait_for_timeout(3000)
            rec = p.evaluate(FIND_BTN)
            if not rec:
                continue
            p.mouse.click(rec["x"], rec["y"])
            p.wait_for_timeout(3500)
            still = p.evaluate(FIND_BTN)
            if still is None:
                print(f"[{r-1}] allow OK (klik ke-{attempt+1})")
                done = True
                break
        if not done:
            res = p.evaluate(FIND_BTN)
            print(f"[{r-1}] MASIH GAGAL: tombol visible={bool(res)}")
    p.wait_for_timeout(15000)
    p.screenshot(path=str(ROOT / "output" / "ringkasan_final3.png"))
    print("[ok] selesai -> output/ringkasan_final3.png")
    p.close(); b.close()
