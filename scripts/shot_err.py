import json, sys, time
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
    p.wait_for_timeout(15000)  # biar importrange selesai evaluasi

    # tooltip pesan error pada sel C2
    try:
        p.locator("#t-name-box").first.click()
        p.wait_for_timeout(200)
        p.locator("#t-name-box").first.fill("C2")
        p.keyboard.press("Enter")
        p.wait_for_timeout(1200)
        p.screenshot(path=str(ROOT / "output" / "ref_err.png"), full_page=False)
    except Exception as e:
        print("shot gagal", type(e).__name__)
    p.close(); b.close()
