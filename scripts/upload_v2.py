"""Unggah master_karyawan.xlsx (kini dengan Convert uploads aktif),
tunggu hasil Google Sheet muncul, lalu buang file lama .xlsx."""
import json, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "output" / "master_karyawan.xlsx"
OLD_ID = "1niwoQ6CzNYDsre4LMc3h3kDlL_a1XjAC"


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


def find_new_sheets_id(p, exclude=(), timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        rows = p.eval_on_selector_all(
            "[data-id]",
            """els => els.map(e => ({
                 id: e.getAttribute('data-id'),
                 label: (e.getAttribute('aria-label')||''),
                 tip: (e.getAttribute('data-tooltip')||'')
               })).filter(r => r.id && r.id.length > 20)""") or []
        seen, uniq = set(), []
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            uniq.append(r)
        for r in uniq:
            if r["id"] in exclude:
                continue
            lab = (r["label"] + " " + r["tip"]).lower()
            if "master_karyawan" in lab and "excel" not in lab:
                return r["id"]
        time.sleep(4)
    return None


def main():
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = b.contexts[0]
        pg = ctx.new_page()
        pg.goto("https://drive.google.com/drive/u/0/my-drive", wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(6000)

        print("[upload] klik New -> File upload")
        if not click_new_button(pg):
            pg.screenshot(path=str(ROOT / "data" / "no_new.png"))
            raise RuntimeError("tombol New tidak ditemukan")
        pg.wait_for_timeout(1500)
        with pg.expect_file_chooser(timeout=60000) as fc_info:
            ok = click_upload_menuitem(pg)
        if not ok:
            pg.screenshot(path=str(ROOT / "data" / "no_upload_item.png"))
            raise RuntimeError("menu Upload tidak ditemukan")
        fc_info.value.set_files(str(FILE))
        print("[upload] file dipilih, menunggu hasil Google Sheet baru...")

        fid = find_new_sheets_id(pg, exclude=(OLD_ID,), timeout=180)
        if not fid:
            # mungkin halaman belum menampilkan; coba via halaman search
            pg.goto("https://drive.google.com/drive/u/0/search?q=%22master_karyawan%22",
                    wait_until="domcontentloaded", timeout=90000)
            pg.wait_for_timeout(5000)
            fid = find_new_sheets_id(pg, exclude=(OLD_ID,), timeout=30)
        if not fid:
            pg.screenshot(path=str(ROOT / "data" / "no_new_result.png"))
            raise RuntimeError("hasil upload konversi tidak ditemukan")
        print("[hasil] fileId Google Sheets baru:", fid)
        (ROOT / "data" / "drive_upload.json").write_text(
            json.dumps({"fileId": fid, "reused": False, "converted": True}), encoding="utf-8")

        # buang file xlsx lama
        print("[cleanup] buang file lama", OLD_ID)
        pg.goto(f"https://drive.google.com/file/d/{OLD_ID}/view",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(4500)
        try:
            more = pg.locator('[aria-label*="More actions"]').first
            more.click(timeout=8000)
            pg.wait_for_timeout(1200)
            item = None
            for name in ("Move to trash", "Move to bin", "Hapus", "Remove"):
                cand = pg.query_selector_all('[role="menuitem"]')
                for el in cand:
                    if name.lower() in (el.inner_text() or "").lower():
                        item = el
                        break
                if item:
                    break
            if item:
                item.click()
                pg.wait_for_timeout(2500)
                print("[cleanup] file lama dibuang")
            else:
                print("[cleanup] item hapus tidak ditemukan (abaikan; hapus manual jika perlu)")
        except Exception as e:
            print("[cleanup] gagal:", type(e).__name__, "(abaikan; hapus manual jika perlu)")
        pg.close(); b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
