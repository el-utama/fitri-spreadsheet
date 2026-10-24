"""
Tarik data mentah dari 12 spreadsheet Google privat.

Cara kerja:
  1. Pastikan Chrome berjalan dengan profil Google yang sudah login (FlowAutomationChrome)
     dan remote debugging aktif di port 9222.
  2. Connect via CDP (Playwright), sehingga cookie sesi Google ikut terpakai.
  3. Untuk tiap dokumen, unduh EKSPOR XLSX (semua tab dalam 1 file) -> data/raw/.

Tidak ada file sumber yang diubah (hanya operasi export/baca).
"""
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import openpyxl
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "sources.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def cdp_alive(port: int) -> bool:
    try:
        r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return r.ok
    except Exception:
        return False


def ensure_chrome(port: int) -> None:
    if cdp_alive(port):
        print(f"[chrome] CDP sudah aktif di port {port}")
        return
    args = [
        CFG["chrome_path"],
        f"--remote-debugging-port={port}",
        f"--user-data-dir={CFG['profile_dir']}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        "--window-size=1920,1080",
    ]
    print(f"[chrome] menyalakan Chrome dengan profil {CFG['profile_dir']}")
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        time.sleep(1)
        if cdp_alive(port):
            print("[chrome] siap")
            return
    raise RuntimeError("Chrome tidak siap dengan remote debugging")


def main() -> int:
    ensure_chrome(CFG["cdp_port"])

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{CFG['cdp_port']}")
        ctx = browser.contexts[0]

        # cek login
        page = ctx.new_page()
        page.goto("https://www.google.com/", wait_until="domcontentloaded", timeout=60000)
        if "accounts.google.com/ServiceLogin" in page.url or "accounts.google.com/signin" in page.url:
            print("[auth] BELUM LOGIN - buka jendela Chrome yang muncul dan login manual, lalu ulangi.")
            page.screenshot(path=str(ROOT / "data" / "login_required.png"))
            browser.close()
            return 2
        print(f"[auth] login OK -> {page.title()}")
        page.close()

        api = ctx.request
        manifest = []
        for doc in CFG["docs"]:
            n, did = doc["n"], doc["id"]
            out = RAW / f"src{n:02d}.xlsx"
            entry = {"n": n, "id": did}

            # --- judul dokumen + daftar tab (dari halaman editor) ---
            page = ctx.new_page()
            try:
                page.goto(f"https://docs.google.com/spreadsheets/d/{did}/edit",
                          wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(1500)
                entry["title"] = page.title().replace(" - Google Sheets", "").strip()
                tabs = page.eval_on_selector_all(
                    ".docs-sheet-tab, .docs-tab-item, [role=tab]",
                    "els => els.map(e => (e.innerText||e.textContent||'').trim()).filter(Boolean)")
                entry["tabs"] = sorted({t for t in tabs if t and t not in entry["title"]})
            except Exception as e:
                entry["title"] = f"(halaman tidak bisa dibuka: {type(e).__name__})"
            finally:
                page.close()

            # --- unduh XLSX semua tab ---
            try:
                r = api.get(f"https://docs.google.com/spreadsheets/d/{did}/export?format=xlsx",
                            max_redirects=0, timeout=60000)
                loc = r.headers.get("location")
                if r.status == 307 and loc:
                    r2 = api.get(loc, timeout=120000)
                    if r2.status == 200:
                        body = r2.body()
                        out.write_bytes(body)
                        wb = openpyxl.load_workbook(io.BytesIO(body), read_only=True)
                        entry["tabs"] = list(wb.sheetnames)
                        wb.close()
                        entry.update(status="ok", file=out.name, bytes=len(body))
                        print(f"[{n:02d}] OK {entry.get('title','?')} | {len(body)/1024:.1f} KB | "
                              f"tabs: {entry.get('tabs')}")
                    else:
                        entry.update(status=f"http_{r2.status}", detail=r2.headers.get("content-type", ""))
                        print(f"[{n:02d}] redirect -> {r2.status} (akses ditolak?)")
                else:
                    entry.update(status=f"http_{r.status}", detail=r.headers.get("content-type", ""))
                    print(f"[{n:02d}] {r.status} tanpa redirect (dokumen tidak ada / tidak diakses)")
            except Exception as e:
                entry.update(status="error", detail=type(e).__name__)
                print(f"[{n:02d}] ERROR {type(e).__name__}")
            manifest.append(entry)
            time.sleep(1)

        (ROOT / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
