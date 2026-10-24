"""Cek nama tab aktual di 12 file sumber (via UI Sheets)."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ids = {int(m["n"]): m["id"] for m in
       json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))}

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    for n in (1, 2, 12):
        p.goto(f"https://docs.google.com/spreadsheets/d/{ids[n]}/edit",
               wait_until="domcontentloaded", timeout=90000)
        p.wait_for_timeout(4000)
        tabs = p.eval_on_selector_all(
            ".docs-sheet-tab",
            "els => els.map(e => (e.innerText || '').trim().replace(/\\s+/g,' '))")
        print(f"PC {n:02d}:", tabs)
    p.close(); b.close()
