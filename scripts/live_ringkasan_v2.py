"""Perbaiki formula RINGKASAN versi live (rentang berbatas + kolom benar) dan
pasang nama ulang judul file live."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

R = 1000  # kedalaman rentang importrange
PC_SHEET = {1: "PC 1", 2: "PC 02", 3: "PC 03", 4: "PC 04", 5: "PC 05", 6: "PC 06",
            7: "PC 07", 8: "PC 08", 9: "PC 09", 10: "PC 10", 11: "PC 11", 12: "PC 12"}
PC_IDS = {int(m["n"]): m["id"] for m in
          json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}
STATUS_LIST = json.loads((ROOT / "config" / "validation_lists.json").read_text(encoding="utf-8"))["status"]


def imp(i, rng, base_url=True):
    url = f"https://docs.google.com/spreadsheets/d/{PC_IDS[i]}/edit"
    return f"IMPORTRANGE(\"{url}\",\"'{PC_SHEET[i]}'!{rng}\")"


rows = []
for i in range(1, 13):
    A, Fg, Gc, H, I, J, K = (imp(i, f"A2:A{R}"), imp(i, f"F2:F{R}"), imp(i, f"G2:G{R}"),
                             imp(i, f"H2:H{R}"), imp(i, f"I2:I{R}"), imp(i, f"J2:J{R}"),
                             imp(i, f"K2:K{R}"))
    rows.append([
        # Baris Data
        f"=COUNTIF({A},\"<>\")",
        # Link Kosong (baris berisi data tapi tanpa link)
        f"=COUNTIFS({A},\"<>\",{H},\"=\")",
        # Genre Kosong (kolom F sumber)
        f"=COUNTIFS({A},\"<>\",{Fg},\"=\")",
        # Status Kosong (kolom K sumber)
        f"=COUNTIFS({A},\"<>\",{K},\"=\")",
        # Status Invalid = status terisi - status yang termasuk daftar baku N2:N9
        f"=COUNTIFS({A},\"<>\",{K},\"<>\")-SUMPRODUCT(COUNTIF({K},$N$2:$N$8))",
        # Duplikat: Worker ID yang berulang di file PC ini
        f"=SUMPRODUCT(--(COUNTIF({A},{A})>1)*({A}<>\"\"))",
        # Link Bukan YouTube
        f"=COUNTIFS({A},\"<>\",{H},\"<>\")-SUMPRODUCT(--ISNUMBER(SEARCH(\"youtube.com\",{H})))",
        # Rata-rata Masa Produksi (hari)
        f"=IFERROR(QUERY({{'',{I}*0+ROW({I}),{I},{J}}},"
        f"\"select avg(Col4-Col3) where Col2>0 and Col3>0 and Col4>0 label avg(Col4-Col3) ''\",0),\"\")",
    ])
paste_block = "\n".join("\t".join(r) for r in rows)
(ROOT / "output" / "ringkasan_live.txt").write_text(paste_block, encoding="utf-8")

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)
    # buka tab RINGKASAN
    for t in p.query_selector_all(".docs-sheet-tab"):
        if "RINGKASAN" in (t.inner_text() or ""):
            t.click()
            break
    p.wait_for_timeout(2000)
    namebox = p.locator("#t-name-box").first

    def go(cell):
        namebox.click()
        p.wait_for_timeout(200)
        namebox.fill(cell)
        p.keyboard.press("Enter")
        p.wait_for_timeout(400)

    # ganti header kolom E1 -> "Genre Kosong" benar dan D1 "Link Kosong"
    pyperclip.copy("Link Kosong\tGenre Kosong")
    go("D1")
    p.keyboard.press("Control+v")
    p.wait_for_timeout(800)
    p.keyboard.press("Escape")

    # timpa formula C2:J13
    pyperclip.copy(paste_block)
    go("C2")
    p.keyboard.press("Control+v")
    p.wait_for_timeout(6000)
    p.keyboard.press("Escape")

    # ganti judul file
    try:
        p.click(".docs-title-input")
        p.keyboard.press("Control+a")
        p.keyboard.type("MASTER_KARYAWAN_PC01-12")
        p.keyboard.press("Enter")
        p.wait_for_timeout(1500)
    except Exception as e:
        print("[judul] gagal:", type(e).__name__)

    p.wait_for_timeout(4000)
    p.screenshot(path=str(ROOT / "output" / "ringkasan_live_v2.png"))
    print("[ok] formula baru terpasang")
    p.close(); b.close()
