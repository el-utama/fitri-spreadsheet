"""Verifikasi live: MASTER 19 kolom, RINGKASAN minimal, dan Kumpulan Video."""
import sys, json, csv, io
from pathlib import Path
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text())["fileId"]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]

    def rows_of(sheet):
        url = (f"https://docs.google.com/spreadsheets/d/{FID}/gviz/tq"
               f"?tqx=out:csv&sheet={quote(sheet)}")
        r = ctx.request.get(url)
        return list(csv.reader(io.StringIO(r.text())))

    m = rows_of("MASTER")
    print("MASTER total rows (incl header):", len(m))
    print("MASTER header count:", len(m[0]) if m else 0)
    print("MASTER K1:", m[0][10] if m and len(m[0]) > 10 else "(tidak ada)")
    print("MASTER R1:", m[0][17] if m and len(m[0]) > 17 else "(tidak ada)")
    for row in m[1:4]:
        print("  ", row[0], "|", row[5] if len(row) > 5 else "",
              "| K:", row[10] if len(row) > 10 else "",
              "| R:", row[17] if len(row) > 17 else "")
    print("  ...")
    for row in m[-2:]:
        print("  ", row[0], "|", row[5] if len(row) > 5 else "",
              "| K:", row[10] if len(row) > 10 else "",
              "| R:", row[17] if len(row) > 17 else "")
    qerr = sum(1 for row in m[1:] if len(row) > 17 and row[17] == "#ERROR!")
    merr = sum(1 for row in m for cell in row if "#ERROR" in str(cell))
    data_rows = sum(1 for row in m[1:] if row and str(row[0]).strip())
    print("baris data MASTER:", data_rows)
    print("baris R #ERROR!:", qerr)
    print("sel #ERROR! di MASTER:", merr)

    rg = rows_of("RINGKASAN")
    print("\nRINGKASAN:")
    print("  header:", rg[0][:10] if rg else [])
    for row in rg[1:13]:
        if row and row[0].startswith("PC"):
            print("  ", row[0], row[2:10])

    vt = rows_of("VALIDASI_TEMPLATE")
    vt_err = sum(1 for row in vt for cell in row if "#ERROR" in str(cell))
    print("\nVALIDASI_TEMPLATE:")
    print("  baris:", len(vt), "| sel #ERROR!:", vt_err)
    print("  A4:", vt[3][0] if len(vt) > 3 and vt[3] else "(kosong)")

    kv = rows_of("Kumpulan Video")
    print("\nKumpulan Video:")
    print("  total rows (incl header):", len(kv))
    print("  header:", kv[0][:9] if kv else [])
    data_kv = [r for r in kv[1:] if r and str(r[0]).strip()]
    links_kv = [r[5].strip() for r in data_kv if len(r) > 5 and str(r[5]).strip()]
    print("  baris data:", len(data_kv))
    print("  link unik:", len(set(links_kv)), "| duplikat:", len(links_kv) - len(set(links_kv)))
    for row in data_kv[:3]:
        print("  ", row[0], "|", row[1], "|", row[3], "|", row[5])
    b.close()
