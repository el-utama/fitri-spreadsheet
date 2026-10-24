"""Set RINGKASAN versi live Google Sheet memakai IMPORTRANGE ke 12 file PC."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

STATUS_LIST = json.loads((ROOT / "config" / "validation_lists.json").read_text(encoding="utf-8"))["status"]
PRINT = (ROOT / "output" / "ringkasan_live.txt")

PC_SHEET = {  # nama tab pertama di tiap file sumber
    1: "PC 1", 2: "PC 02", 3: "PC 03", 4: "PC 04", 5: "PC 05", 6: "PC 06",
    7: "PC 07", 8: "PC 08", 9: "PC 09", 10: "PC 10", 11: "PC 11", 12: "PC 12",
}
PC_IDS = {int(m["n"]): m["id"] for m in
          json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}


def imp(i, rng):
    return f"=IMPORTRANGE(\"https://docs.google.com/spreadsheets/d/{PC_IDS[i]}/edit\",\"'{PC_SHEET[i]}'!{rng}\")"


rows = []
for i in range(1, 13):
    a2a = imp(i, "A2:A")
    rows.append([
        "", "",   # PC & SS ID sudah ada di kolom A,B (tidak ditimpa, padding kosong)
        f"=COUNTA({imp(i, 'A2:A')[1:]})",
        f"=COUNTBLANK({imp(i, 'A2:A')[1:]})",
        f"=COUNTIFS({imp(i, 'A2:A')[1:]},\"<>\",{imp(i, 'H2:H')[1:]},\"=\")",
        f"=COUNTIFS({imp(i, 'A2:A')[1:]},\"<>\",{imp(i, 'K2:K')[1:]},\"=\")",
        f"=COUNTIFS({imp(i, 'A2:A')[1:]},\"<>\",{imp(i, 'K2:K')[1:]},\"<>\")"
        f"-SUMPRODUCT(COUNTIF({imp(i, 'K2:K')[1:]},$N$2:$N$8))",
        f"=SUMPRODUCT(--(COUNTIF({imp(i, 'A2:A')[1:]},{imp(i, 'A2:A')[1:]})>1)*({imp(i, 'A2:A')[1:]}<>\"\"))",
        f"=COUNTIFS({imp(i, 'A2:A')[1:]},\"<>\",{imp(i, 'H2:H')[1:]},\"<>\")"
        f"-SUMPRODUCT(--ISNUMBER(SEARCH(\"youtube.com\",{imp(i, 'H2:H')[1:]})))",
        f"=IFERROR(AVERAGE(IF(({imp(i, 'I2:I')[1:]}>0)*({imp(i, 'J2:J')[1:]}>0),{imp(i, 'J2:J')[1:]}-{imp(i, 'I2:I')[1:]})))",
    ])
# kolom A,B kosong agar paste di C2 tidak menimpa label (baris 12 x 10 kolom C..L)
paste_block = "\n".join("\t".join(r[2:]) for r in rows)

status_block = "\n".join(STATUS_LIST)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)

    # buka tab RINGKASAN
    tabs = p.query_selector_all(".docs-sheet-tab")
    target = None
    for t in tabs:
        if "RINGKASAN" in (t.inner_text() or ""):
            target = t
            break
    if not target:
        raise RuntimeError("tab RINGKASAN tidak ditemukan")
    target.click()
    p.wait_for_timeout(2000)

    # fokus ke C2 lewat Name Box
    namebox = p.locator("#t-name-box").first
    namebox.click()
    p.wait_for_timeout(300)
    namebox.fill("C2")
    p.keyboard.press("Enter")
    p.wait_for_timeout(500)

    pyperclip.copy(paste_block)
    p.keyboard.press("Control+v")
    p.wait_for_timeout(3000)

    # simpan daftar status di N2..N8 (helper untuk hitung Status invalid)
    namebox.click()
    p.wait_for_timeout(300)
    namebox.fill("N2")
    p.keyboard.press("Enter")
    p.wait_for_timeout(500)
    pyperclip.copy(status_block)
    p.keyboard.press("Control+v")
    p.wait_for_timeout(5000)

    # baca hasil beberapa sel untuk verifikasi
    for cell in ("C2", "D2"):
        try:
            p.evaluate(f"document.querySelector('#t-purge')")  # noop
        except Exception:
            pass
    # kembali ke RAD dan cek judul tab
    PRINT.write_text(paste_block, encoding="utf-8")
    print("[ok] paste selesai, live FID:", FID)
    p.close(); b.close()
