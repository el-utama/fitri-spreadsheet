import sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright
import openpyxl, io, csv, requests

DID = "13ZTrmU9eZ0ltVSNirEcBuqq017_b-TB85qZEqfPPF5Q"  # PC 12

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    api = ctx.request

    def gviz(qs):
        r = api.get(f"https://docs.google.com/spreadsheets/d/{DID}/gviz/tq?{qs}", timeout=60000)
        return r.status, r.text()

    for qs in ["tqx=out:csv", "tqx=out:csv&sheet=Extract", "tqx=out:csv&sheet=Refresh%20%26%20manage"]:
        st, txt = gviz(qs)
        print(f"--- {qs} -> {st}")
        print(txt[:600].replace("\r", ""))
        print()

    # isi grid yang sedang aktif di editor (sheet pertama), cek apakah ada data
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{DID}/edit", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)
    tabs = p.eval_on_selector_all(".docs-sheet-tab", "els=>els.map(e=>({name:(e.innerText||'').trim(),cls:e.className}))")
    print("tabs:", json.dumps(tabs, ensure_ascii=False)[:500])
    # baca beberapa sel dari grid aktif
    cells = p.eval_on_selector_all(
        ".ritz .sheet-container [role=gridcontainer] table td, .shtm, .wiz-vbar, .sheet-container td",
        "els=>els.slice(0,60).map(e=>(e.innerText||'').trim()).filter(Boolean)")
    print("grid cells:", cells[:40])
    p.close()
    b.close()
