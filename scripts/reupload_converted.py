"""Siapkan Drive agar mengonversi upload -> Google Sheets,
buang master_karyawan.xlsx lama, lalu unggah ulang file master."""
import json, re, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "output" / "master_karyawan.xlsx"
NAME_BASE = "master_karyawan"


def trash_existing(p, timeout=60):
    p.goto(f"https://drive.google.com/drive/u/0/search?q=%22{NAME_BASE}%22",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(4500)
    found = p.eval_on_selector_all(
        "[data-id]",
        """els => els.map(e => ({
             id: e.getAttribute('data-id'),
             label: (e.getAttribute('aria-label')||'')
           })).filter(r => r.label.includes('master_karyawan'))""")
    ids = []
    for r in found:
        if r["id"] and r["id"] not in ids and "Microsoft Excel" in r["label"]:
            ids.append(r["id"])
    for fid in ids:
        # buka file lalu hapus dari tombol "More actions"
        p.goto(f"https://drive.google.com/file/d/{fid}/view",
               wait_until="domcontentloaded", timeout=90000)
        p.wait_for_timeout(4000)
        more = p.query_selector('div[aria-label*="More actions"], button[aria-label*="More actions"]')
        if not more:
            more = p.locator("div[role=button]").filter(has_text="").nth(0)
        try:
            more.click(timeout=5000)
            p.wait_for_timeout(1000)
        except Exception as e:
            print("menu more gagal:", type(e).__name__)
            continue
        item = None
        for name in ("Move to trash", "Move to bin", "Hapus", "Remove"):
            cand = p.query_selector_all('[role="menuitem"]')
            for el in cand:
                if name.lower() in (el.inner_text() or "").lower():
                    item = el
                    break
            if item:
                break
        if item:
            item.click()
            p.wait_for_timeout(2000)
            print("[trash] dibuang:", fid)
        else:
            print("[trash] item hapus tidak ditemukan untuk", fid)
    return len(ids)


def enable_convert(p):
    p.goto("https://drive.google.com/drive/u/0/settings", wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(4000)
    # cari toggle "Convert uploads"
    sw = p.query_selector_all('[role="checkbox"], [role="switch"], label, div[role="button"]')
    for el in sw:
        aria = (el.get_attribute("aria-label") or "") + " " + (el.inner_text() or "")
        if "convert" in aria.lower() or "konversi" in aria.lower():
            cls = el.get_attribute("aria-checked")
            if cls == "true":
                print("[setel] Convert uploads sudah aktif")
                return True
            el.click()
            p.wait_for_timeout(1500)
            print("[setel] Convert uploads diaktifkan")
            return True
    print("[setel] toggle Convert tidak ditemukan")
    return False


def click_new_button(p):
    for el in p.query_selector_all("div[role=button], button"):
        txt = (el.inner_text() or "").strip()
        aria = (el.get_attribute("aria-label") or "").strip()
        if txt == "New" or aria in ("New", "Baru"):
            el.click()
            return True
    return False


def click_upload_menuitem(p):
    for el in p.query_selector_all('[role="menuitem"]'):
        txt = (el.inner_text() or "").strip().lower()
        if "file upload" in txt or "unggah file" in txt:
            el.click()
            return True
    return False


def wait_upload_id(p, timeout=240):
    t0 = time.time()
    while time.time() - t0 < timeout:
        rows = p.eval_on_selector_all(
            "[data-id]",
            """els => els.map(e => ({
                 id: e.getAttribute('data-id'),
                 label: (e.getAttribute('aria-label')||''),
                 href: (e.closest('a') ? e.closest('a').getAttribute('href') : '')
               })).filter(r => r.label.includes('master_karyawan'))""") or []
        for r in rows:
            if "Google Sheets" in r["label"]:
                return r["id"]
        # belum terkonversi? cek apakah sumber xlsx ada; timeout akan berhenti
        time.sleep(4)
    return None


def main():
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = b.contexts[0]

        # 1) buang file xlsx lama supaya tidak duplikat
        pg = ctx.new_page()
        trashed = trash_existing(pg)
        print(f"[trash] dibuang {trashed} file lama")

        # 2) aktifkan Convert uploads
        enable_convert(pg)

        # 3) upload ulang lewat menu New -> File upload
        pg2 = ctx.new_page()
        pg2.goto("https://drive.google.com/drive/u/0/my-drive", wait_until="domcontentloaded", timeout=90000)
        pg2.wait_for_timeout(6000)
        if not click_new_button(pg2):
            pg2.screenshot(path=str(ROOT / "data" / "no_new.png"))
            raise RuntimeError("tombol New tidak ditemukan")
        pg2.wait_for_timeout(1500)
        with pg2.expect_file_chooser(timeout=60000) as fc_info:
            ok = click_upload_menuitem(pg2)
        if not ok:
            pg2.screenshot(path=str(ROOT / "data" / "no_upload_item.png"))
            raise RuntimeError("menu Upload tidak ditemukan")
        fc_info.value.set_files(str(FILE))

        # 4) tunggu hasil: cari entri Google Sheets bernama master_karyawan
        fid = None
        t0 = time.time()
        while time.time() - t0 < 240 and not fid:
            # refresh grid agar row baru terlihat
            pg2.goto("https://drive.google.com/drive/u/0/my-drive", wait_until="domcontentloaded", timeout=90000)
            pg2.wait_for_timeout(3500)
            fid = wait_upload_id(pg2, timeout=8)
        if not fid:
            pg2.screenshot(path=str(ROOT / "data" / "no_converted.png"))
            raise RuntimeError("file belum terkonversi ke Google Sheets (screensho no_converted.png)")
        out = {"fileId": fid, "reused": False, "converted": True}
        (ROOT / "data" / "drive_upload.json").write_text(json.dumps(out), encoding="utf-8")
        print("[hasil] fileId (Sheets):", fid)
        pg.close(); pg2.close(); b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
