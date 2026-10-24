"""Sisipkan kolom K di MASTER live dan set header Link Video YT.

Prasyarat: MASTER live masih 18 kolom (K = Tanggal Video Dibuat).
Setelah sisip: K kosong, L = Tanggal Video Dibuat, M = Tanggal Video Dipublish,
N = Status Upload, O = PIC channel, P..S = formula lama yang ikut bergeser.
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]


def click_menu_text(p, text):
    loc = p.get_by_text(text, exact=True)
    if loc.count():
        loc.first.click()
        return True
    return False


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)
    for t in p.query_selector_all(".docs-sheet-tab"):
        if (t.inner_text() or "").strip().startswith("MASTER"):
            t.click()
            break
    p.wait_for_timeout(2500)

    nb = p.locator("#t-name-box").first
    nb.click(); p.wait_for_timeout(250)
    nb.fill("K1"); p.keyboard.press("Enter")
    p.wait_for_timeout(800)
    p.keyboard.press("Control+Space")
    p.wait_for_timeout(800)
    p.keyboard.press("Shift+F10")
    p.wait_for_timeout(1200)
    if not click_menu_text(p, "Insert 1 column left"):
        raise SystemExit("Menu 'Insert 1 column left' tidak ditemukan")
    p.wait_for_timeout(3000)

    # set header K1
    nb.click(); p.wait_for_timeout(250)
    nb.fill("K1"); p.keyboard.press("Enter")
    p.wait_for_timeout(600)
    pyperclip.copy("Link Video YT")
    p.keyboard.press("Control+v")
    p.wait_for_timeout(1000)
    p.keyboard.press("Escape")
    p.wait_for_timeout(3000)
    p.screenshot(path=str(ROOT / "output" / "master_insert_k.png"))
    print("[ok] kolom K disisipkan dan header K1 = Link Video YT")
    p.close(); b.close()
