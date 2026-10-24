"""Rename tab 'PC 1' -> 'PC 01' di file sumber PC 01."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ids = {int(m["n"]): m["id"] for m in
       json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}
FID = ids[1]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)

    # cari tab 'PC 1' (bukan 'PC 01'/'PC 12')
    tabs = p.query_selector_all(".docs-sheet-tab")
    target = None
    for t in tabs:
        name = (t.inner_text() or "").strip().replace("\n", " ")
        if name == "PC 1":
            target = t
            break
    if not target:
        print("[rename] tab 'PC 1' tidak ditemukan; tabs:", [t.inner_text().strip() for t in tabs])
        sys.exit(1)

    target.dblclick()
    p.wait_for_timeout(1200)
    # input inline (bisa juga dialog)
    ok = False
    for sel in ("input.docs-sheet-tab-name-input", ".docs-sheet-tab-name-input input",
                "input[type=text]:visible", "input[type=text]"):
        try:
            inp = p.locator(sel).first
            if inp.count() and inp.is_visible():
                inp.click()
                p.keyboard.press("Control+a")
                p.keyboard.type("PC 01")
                p.wait_for_timeout(400)
                p.keyboard.press("Enter")
                ok = True
                break
        except Exception:
            pass
    if not ok:
        # fallback: menu konteks -> Rename
        target.click(button="right")
        p.wait_for_timeout(800)
        for el in p.query_selector_all('[role="menuitem"]'):
            if "rename" in (el.inner_text() or "").lower() or "ganti nama" in (el.inner_text() or "").lower():
                el.click()
                p.wait_for_timeout(1200)
                break
        inp = p.locator("input[type=text]").first
        inp.click()
        p.keyboard.press("Control+a")
        p.keyboard.type("PC 01")
        p.keyboard.press("Enter")
        ok = True
    p.wait_for_timeout(3000)
    names = [t.inner_text().strip().replace("\n", " ") for t in p.query_selector_all(".docs-sheet-tab")]
    print("[rename] tabs sekarang:", names)
    p.screenshot(path=str(ROOT / "data" / "rename_pc01.png"))
    p.close(); b.close()
