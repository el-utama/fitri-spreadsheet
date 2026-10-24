"""Inventarisasi struktur: semua file -> daftar tab, dimensi, header, contoh baris."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import openpyxl

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT = Path(__file__).resolve().parents[1] / "data" / "inventory.json"

inv = []
for f in sorted(RAW.glob("src*.xlsx")):
    wb = openpyxl.load_workbook(f, data_only=True)
    doc = {"file": f.name, "tabs": []}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        # buang baris penuh kosong di akhir
        while rows and all(v is None for v in rows[-1]):
            rows.pop()
        ncols = max((len(r) for r in rows), default=0)
        header_row = next((i for i, r in enumerate(rows) if sum(v is not None for v in r) >= 2), None)
        tab = {
            "name": ws.title,
            "rows": len(rows),
            "max_cols": ncols,
            "header_row_index": header_row,
            "row1": [str(v)[:40] if v is not None else None for v in (rows[0] if rows else [])][:40],
            "row2": [str(v)[:40] if v is not None else None for v in (rows[1] if len(rows) > 1 else [])][:40],
            "sample": [[str(v)[:28] if v is not None else None for v in r][:ncols]
                       for r in rows[2:6]],
        }
        doc["tabs"].append(tab)
    inv.append(doc)
    print(f"{f.name}: tabs=" + ", ".join(t["name"] for t in doc["tabs"]) +
          "" + "".join(f" [{t['rows']}x{t['max_cols']}]" for t in doc["tabs"]))

OUT.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
print("->", OUT)
