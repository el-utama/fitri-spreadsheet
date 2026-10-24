"""Segarkan tab dokumentasi di master live dari master lokal.

Tab: PETUNJUK, KAMUS_KOLOM, TEMUAN_STRUKTUR, DAFTAR_SUMBER, TEMPLET_PC.
TEMPLET_PC hanya header 13 kolom (template lengkap ada di master lokal).
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import openpyxl, pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

wb = openpyxl.load_workbook(ROOT / "output" / "master_karyawan.xlsx", data_only=True)
wb_formulas = openpyxl.load_workbook(ROOT / "output" / "master_karyawan.xlsx", data_only=False)


def table(name, max_rows=None, max_cols=None, use_formulas=False):
    ws = (wb_formulas if use_formulas else wb)[name]
    rows = []
    for r in range(1, (max_rows or ws.max_row) + 1):
        vals = []
        for c in range(1, (max_cols or ws.max_column) + 1):
            v = ws.cell(r, c).value
            vals.append("" if v is None else str(v))
        rows.append(vals)
    return rows


def tsv(rows):
    return "\n".join("\t".join(r) for r in rows)


def click_tab(p, name):
    for t in p.query_selector_all(".docs-sheet-tab"):
        if (t.inner_text() or "").strip() == name:
            t.click()
            return True
    return False


def paste_tab(p, name, rows):
    if not click_tab(p, name):
        print("[skip] tab tidak ada:", name)
        return
    p.wait_for_timeout(1800)
    nb = p.locator("#t-name-box").first
    nb.click(); p.wait_for_timeout(200)
    nb.fill("A1:Z1000"); p.keyboard.press("Enter")
    p.wait_for_timeout(700)
    p.keyboard.press("Delete")
    p.wait_for_timeout(1000)
    nb.click(); p.wait_for_timeout(200)
    nb.fill("A1"); p.keyboard.press("Enter")
    p.wait_for_timeout(400)
    pyperclip.copy(tsv(rows))
    p.keyboard.press("Control+v")
    p.wait_for_timeout(4000)
    p.keyboard.press("Escape")
    print(f"[ok] {name}: {len(rows)} baris x {len(rows[0]) if rows else 0} kolom")


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)

    paste_tab(p, "PETUNJUK", table("PETUNJUK", max_cols=1))
    paste_tab(p, "KAMUS_KOLOM", table("KAMUS_KOLOM", max_cols=6))
    paste_tab(p, "TEMUAN_STRUKTUR", table("TEMUAN_STRUKTUR", max_cols=5))
    paste_tab(p, "DAFTAR_SUMBER", table("DAFTAR_SUMBER", max_cols=5))
    paste_tab(p, "TEMPLET_PC", table("TEMPLET_PC", max_rows=1, max_cols=13))
    paste_tab(p, "VALIDASI_TEMPLATE", table("VALIDASI_TEMPLATE", max_cols=1, use_formulas=True))

    p.wait_for_timeout(3000)
    p.screenshot(path=str(ROOT / "output" / "live_docs_tabs.png"))
    wb.close(); wb_formulas.close()
    p.close(); b.close()
