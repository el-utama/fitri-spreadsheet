import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import requests
from playwright.sync_api import sync_playwright

DID = "13ZTrmU9eZ0ltVSNirEcBuqq017_b-TB85qZEqfPPF5Q"
PORT = 9222

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    ctx = b.contexts[0]
    api = ctx.request

    # A) context.request tanpa redirect
    r = api.get(f"https://docs.google.com/spreadsheets/d/{DID}/export?format=xlsx", max_redirects=0, timeout=60000)
    print("A)", r.status, r.headers.get("content-type"), r.headers.get("location", "")[:120])
    loc = r.headers.get("location")
    if loc:
        r2 = api.get(loc, timeout=120000)
        print("A2)", r2.status, r2.headers.get("content-type"), len(r2.body()))
        if r2.status == 200:
            Path("data/raw/probe_A.xlsx").write_bytes(r2.body())

    # B) gviz csv
    r3 = api.get(f"https://docs.google.com/spreadsheets/d/{DID}/gviz/tq?tqx=out:csv", timeout=60000)
    print("B)", r3.status, r3.headers.get("content-type"), r3.text()[:200].replace("\n", " | "))

    # C) halaman edit -> nama tab
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{DID}/edit", wait_until="domcontentloaded", timeout=90000)
    tabs = p.eval_on_selector_all(".docs-sheet-tab, .docs-tab-item, [role=tab]",
                                  "els => els.map(e => (e.innerText||e.textContent||'').trim()).filter(Boolean)")
    print("C) tabs:", tabs[:30], "| title:", p.title())
    p.close()
    b.close()
