import sys, json, io, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
import openpyxl
from playwright.sync_api import sync_playwright

FID = json.loads(Path("data/drive_upload.json").read_text())["fileId"]
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    r = ctx.request.get(f"https://docs.google.com/spreadsheets/d/{FID}/export?format=xlsx")
    wb = openpyxl.load_workbook(io.BytesIO(r.body()))
    ws = wb["RINGKASAN"]
    for cell in ("C2", "D2", "E2", "F2", "G2", "H2", "I2", "J2"):
        v = str(ws[cell].value)
        cols = sorted(set(re.findall(r"'PC 1'!([A-Z]+)2", v)))
        print(cell, "source cols:", cols, "| len", len(v))
    b.close()
