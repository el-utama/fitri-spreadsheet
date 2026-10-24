"""V3: formula RINGKASAN live tahan terhadap file sumber kosong (sel "" dari importrange)."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

R = 1000
PC_SHEET = {1: "PC 1", 2: "PC 02", 3: "PC 03", 4: "PC 04", 5: "PC 05", 6: "PC 06",
            7: "PC 07", 8: "PC 08", 9: "PC 09", 10: "PC 10", 11: "PC 11", 12: "PC 12"}
PC_IDS = {int(m["n"]): m["id"] for m in
          json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}


def imp(i, rng):
    return f"IMPORTRANGE(\"https://docs.google.com/spreadsheets/d/{PC_IDS[i]}/edit\",\"'{PC_SHEET[i]}'!{rng}\")"


rows = []
for i in range(1, 13):
    A, Fg, Gc, H, I, J, K = (imp(i, f"A2:A{R}"), imp(i, f"F2:F{R}"), imp(i, f"G2:G{R}"),
                             imp(i, f"H2:H{R}"), imp(i, f"I2:I{R}"), imp(i, f"J2:J{R}"),
                             imp(i, f"K2:K{R}"))
    rows.append([
        f"=SUMPRODUCT(--({A}<>\"\"))",                                   # Baris Data
        f"=SUMPRODUCT(({A}<>\"\")*({H}=\"\"))",                          # Link Kosong
        f"=SUMPRODUCT(({A}<>\"\")*({Fg}=\"\"))",                         # Genre Kosong (kolom F)
        f"=SUMPRODUCT(({A}<>\"\")*({K}=\"\"))",                          # Status Kosong (kolom K)
        f"=SUMPRODUCT(({A}<>\"\")*({K}<>\"\"))-SUMPRODUCT(COUNTIF({K},$N$2:$N$8))",  # Status Invalid
        f"=SUMPRODUCT(--(COUNTIF({A},{A})>1)*({A}<>\"\"))",              # Duplikat
        f"=SUMPRODUCT(({A}<>\"\")*({H}<>\"\"))-SUMPRODUCT(--ISNUMBER(SEARCH(\"youtube.com\",{H})))",  # Link bukan YT
        f"=IFERROR(AVERAGE(ARRAYFORMULA(IF(ISNUMBER({I})*ISNUMBER({J})*({J}>={I}),{J}-{I},\"\"))),\"\")",  # Rata2 masa produksi
    ])
paste_block = "\n".join("\t".join(r) for r in rows)
(ROOT / "output" / "ringkasan_live.txt").write_text(paste_block, encoding="utf-8")

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
    namebox.click(); p.wait_for_timeout(200)
    namebox.fill("C2"); p.keyboard.press("Enter"); p.wait_for_timeout(500)
    pyperclip.copy(paste_block)
    p.keyboard.press("Control+v")
    p.wait_for_timeout(6000)
    p.keyboard.press("Escape")
    p.wait_for_timeout(3000)
    p.screenshot(path=str(ROOT / "output" / "ringkasan_live_v3.png"))
    print("[ok] v3 terpasang")
    p.close(); b.close()
