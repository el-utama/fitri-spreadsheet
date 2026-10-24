"""Pasang formula RINGKASAN baris PC 01 yang tahan nama tab 'PC 01' maupun 'PC 1'.

RINGKASAN minimal: 10 kolom A:J, blok formula 8 kolom C:J.
Sumber: A, D, F, I, J, K, L (Link Video YT = I; status = L).
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pyperclip
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]
PC_IDS = {int(m["n"]): m["id"] for m in
          json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}
R = 1000
STATUS_LIST = json.loads((ROOT / "config" / "validation_lists.json").read_text(encoding="utf-8"))["status"]


def imp(i, tab, rng):
    url = f"https://docs.google.com/spreadsheets/d/{PC_IDS[i]}/edit"
    return f'IMPORTRANGE("{url}","\'{tab}\'!{rng}")'


def metrics(i, tab):
    A, D, F = imp(i, tab, f"A2:A{R}"), imp(i, tab, f"D2:D{R}"), imp(i, tab, f"F2:F{R}")
    I, J, K, L = (imp(i, tab, f"I2:I{R}"), imp(i, tab, f"J2:J{R}"),
                  imp(i, tab, f"K2:K{R}"), imp(i, tab, f"L2:L{R}"))
    return [
        f'=SUMPRODUCT(--({D}<>""))',
        f'=SUMPRODUCT(({D}<>"")*({I}=""))',
        f'=SUMPRODUCT(({D}<>"")*({F}=""))',
        f'=SUMPRODUCT(({D}<>"")*({L}=""))',
        f'=SUMPRODUCT(({D}<>"")*({L}<>""))-SUMPRODUCT(COUNTIF({L},$N$2:$N$8))',
        f'=SUMPRODUCT(--(COUNTIF({A},{A})>1)*({A}<>""))',
        f'=SUMPRODUCT(({D}<>"")*({I}<>""))-SUMPRODUCT(--ISNUMBER(SEARCH("youtu",{I})))',
        f'=AVERAGE(FILTER({K}-{J},ISNUMBER({J}),ISNUMBER({K}),{K}>={J}))',
    ]


prim = metrics(1, "PC 01")
fall = metrics(1, "PC 1")
row = [f"=IFERROR({p[1:]},{f[1:]})" for p, f in zip(prim, fall)]
# Rata-rata: jangan bungkus IFERROR di dalam, karena hasil "" dari tab
# primer akan dianggap sukses dan fallback "PC 1" tidak dievaluasi.
row[-1] = f'=IFERROR({prim[-1][1:]},IFERROR({fall[-1][1:]},""))'
block = "\t".join(row)

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
    nb.click(); p.wait_for_timeout(200)
    nb.fill("C2"); p.keyboard.press("Enter")
    p.wait_for_timeout(500)
    pyperclip.copy(block)
    p.keyboard.press("Control+v")
    p.wait_for_timeout(6000)
    p.keyboard.press("Escape")
    p.wait_for_timeout(4000)
    try:
        p.screenshot(path=str(ROOT / "output" / "ringkasan_v6_pc01.png"), timeout=60000)
    except Exception as exc:
        print("screenshot gagal (tidak fatal):", exc)
    print("[ok] formula PC 01 dual-tab terpasang")
    p.close(); b.close()
