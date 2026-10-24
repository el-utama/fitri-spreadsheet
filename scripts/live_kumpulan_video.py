"""Buat/segarkan tab Kumpulan Video di master live.

Tab berisi 9 kolom, hanya baris yang Link Video YT (K) terisi, dan hanya
link unik (kemunculan pertama dipertahankan).
Sumber: QUERY dari MASTER (snapshot).
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]
TAB = "Kumpulan Video"
HEADERS = ["PC", "Worker ID", "Song ID YT", "Judul Lagu Kompilasi", "Nama Channel",
           "Link Video YT", "Status Upload", "Tanggal Video Dibuat", "Tanggal Video Dipublish"]
FORMULA = ('=IFERROR(LET(q,QUERY(MASTER!A2:O,'
           '"select A,C,E,F,I,K,N,L,M where K is not null",0),'
           'FILTER(q,MATCH(INDEX(q,0,6),INDEX(q,0,6),0)=SEQUENCE(ROWS(q)))),"")')


def click_text(p, text):
    loc = p.get_by_text(text, exact=True)
    if loc.count():
        loc.first.click()
        return True
    return False


def tab_by_name(p, name):
    for t in p.query_selector_all(".docs-sheet-tab"):
        if (t.inner_text() or "").strip() == name:
            return t
    return None


def rename_selected_tab(p, name):
    # Tab baru biasanya otomatis terpilih. Double-click tab -> nama jadi
    # contenteditable (lebih andal daripada menu context "Rename").
    tab = p.query_selector(".docs-sheet-tab-selected")
    if not tab:
        tabs = p.query_selector_all(".docs-sheet-tab")
        tab = tabs[-1] if tabs else None
    if not tab:
        raise RuntimeError("Tab baru tidak ditemukan")

    tab.dblclick()
    p.wait_for_timeout(1000)
    name_el = tab.query_selector(".docs-sheet-tab-name")
    if name_el:
        name_el.click()
        p.keyboard.press("Control+a")
        p.keyboard.type(name)
        p.wait_for_timeout(300)
        p.keyboard.press("Enter")
        p.wait_for_timeout(2500)
        return

    # fallback: menu context Rename + dialog input
    tab.click(button="right")
    p.wait_for_timeout(1000)
    if not click_text(p, "Rename"):
        if not click_text(p, "Ganti nama"):
            raise RuntimeError("Menu Rename tidak ditemukan")
    p.wait_for_timeout(1000)
    inp = None
    for sel in ['input[aria-label="Rename sheet"]', 'input[aria-label="Ganti nama sheet"]']:
        loc = p.locator(sel)
        if loc.count():
            inp = loc.first
            break
    if inp is None:
        inputs = [x for x in p.query_selector_all("input") if x.is_visible()]
        if inputs:
            inp = inputs[-1]
    if inp is None:
        raise RuntimeError("Input rename tidak ditemukan")
    inp.click()
    p.keyboard.press("Control+a")
    p.keyboard.type(name)
    p.keyboard.press("Enter")
    p.wait_for_timeout(2500)


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)

    tab = tab_by_name(p, TAB)
    if tab:
        print("[tab] sudah ada:", TAB)
        tab.click()
    else:
        print("[tab] membuat tab baru:", TAB)
        p.locator('[aria-label="Add Sheet"]').first.click()
        p.wait_for_timeout(2500)
        rename_selected_tab(p, TAB)
        tab = tab_by_name(p, TAB)
        if not tab:
            raise RuntimeError("Tab Kumpulan Video gagal dibuat")
        tab.click()
    p.wait_for_timeout(2500)

    nb = p.locator("#t-name-box").first
    # header
    nb.click(); p.wait_for_timeout(250)
    nb.fill("A1"); p.keyboard.press("Enter")
    p.wait_for_timeout(500)
    pyperclip.copy("\t".join(HEADERS))
    p.keyboard.press("Control+v")
    p.wait_for_timeout(1500)
    p.keyboard.press("Escape")

    # formula
    nb.click(); p.wait_for_timeout(250)
    nb.fill("A2"); p.keyboard.press("Enter")
    p.wait_for_timeout(500)
    pyperclip.copy(FORMULA)
    p.keyboard.press("Control+v")
    p.wait_for_timeout(8000)
    p.keyboard.press("Escape")

    # format tanggal H:I
    nb.click(); p.wait_for_timeout(250)
    nb.fill("H2:I1000"); p.keyboard.press("Enter")
    p.wait_for_timeout(800)
    p.keyboard.press("Control+Shift+3")  # format tanggal di Google Sheets
    p.wait_for_timeout(1500)
    p.keyboard.press("Escape")

    # freeze 1 baris
    nb.click(); p.wait_for_timeout(250)
    nb.fill("1:1"); p.keyboard.press("Enter")
    p.wait_for_timeout(500)
    # View > Freeze > 1 row
    click_text(p, "View")
    p.wait_for_timeout(500)
    if click_text(p, "Freeze"):
        p.wait_for_timeout(500)
        click_text(p, "1 row")
    p.wait_for_timeout(1000)
    p.keyboard.press("Escape")

    # filter
    nb.click(); p.wait_for_timeout(250)
    nb.fill("A1:I1000"); p.keyboard.press("Enter")
    p.wait_for_timeout(600)
    click_text(p, "Data")
    p.wait_for_timeout(500)
    click_text(p, "Create a filter")
    p.wait_for_timeout(1500)
    p.keyboard.press("Escape")

    p.wait_for_timeout(4000)
    p.screenshot(path=str(ROOT / "output" / "kumpulan_video_live.png"))
    print("[ok] tab Kumpulan Video siap")
    p.close(); b.close()
