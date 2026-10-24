import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

IDS = ["1niwoQ6CzNYDsre4LMc3h3kDlL_a1XjAC",
       "19cPX4jWZ-kh12T6NgP8tECCemz0iN2zPc1HcFKfeDdg",
       "12ttwamDnzftP4SFI8S3XWzyOHFozfW1N1lr8wkqdJHI"]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    for fid in IDS:
        p = ctx.new_page()
        try:
            p.goto(f"https://docs.google.com/spreadsheets/d/{fid}/edit",
                   wait_until="domcontentloaded", timeout=90000)
            p.wait_for_timeout(4000)
            print(fid, "| title:", p.title()[:60], "| url:", p.url.split("/")[3] if len(p.url.split("/"))>3 else "?")
            tabs = p.eval_on_selector_all(
                ".docs-sheet-tab, .docs-tab-item, [role=tab]",
                "els => els.map(e => (e.innerText||'').trim()).filter(Boolean)")
            print("     tabs:", tabs[:14])
        except Exception as e:
            print(fid, "GAGAL:", type(e).__name__)
        p.close()
    b.close()
