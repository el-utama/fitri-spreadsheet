"""Ambil fileId master_karyawan dari Drive (cari by nama), lalu simpan ke data/drive_upload.json."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto("https://drive.google.com/drive/u/0/search?q=%22master_karyawan%22",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(5000)
    rows = p.eval_on_selector_all(
        "[data-id]",
        """els => els.map(e => ({
             id: e.getAttribute('data-id'),
             label: (e.getAttribute('aria-label')||e.getAttribute('data-tooltip')||'').slice(0,80)
           })).filter(r => r.id)""")
    fid = None
    for r in rows:
        if "master_karyawan" in r["label"]:
            fid = r["id"]
            break
    if not fid and rows:
        fid = rows[0]["id"]
    print("rows:", rows[:5])
    print("fileId:", fid)
    if fid:
        (ROOT / "data" / "drive_upload.json").write_text(
            json.dumps({"fileId": fid, "reused": True}), encoding="utf-8")
    p.close()
    b.close()
