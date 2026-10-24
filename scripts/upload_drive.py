import json, re, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "output" / "master_karyawan.xlsx"
NAME_BASE = "master_karyawan"


def find_upload_input(p):
    loc = p.locator("input[type=file]").first
    try:
        loc.set_input_files(str(FILE), timeout=6000)
        return True
    except Exception as e:
        print("[upload] direct input gagal:", type(e).__name__)
    return False


def click_new_button(p):
    cand = p.query_selector_all("div[role=button], button")
    for el in cand:
        txt = (el.inner_text() or "").strip()
        aria = (el.get_attribute("aria-label") or "").strip()
        if txt == "New" or aria in ("New", "Baru", "Buat"):
            el.click()
            return True
    return False


def click_upload_menuitem(p):
    items = p.query_selector_all('div[role="menuitem"], [role="menuitem"]')
    for el in items:
        txt = (el.inner_text() or "").strip().lower()
        if "file upload" in txt or "unggah file" in txt or "upload file" in txt:
            el.click()
            return True
    return False


def find_result_id(p, timeout=240):
    t0 = time.time()
    while time.time() - t0 < timeout:
        hrefs = p.eval_on_selector_all(
            "a[href]",
            """els => els.map(e => e.getAttribute('href'))
                  .filter(h => h && /\\/(file|document|spreadsheets)\\/d\\/[A-Za-z0-9-_]{25,}\\//.test(h))""") or []
        ids = []
        for h in hrefs:
            m = re.search(r"/(?:file|document|spreadsheets)/d/([A-Za-z0-9-_]{25,})/", h)
            if m and m.group(1) not in ids:
                ids.append(m.group(1))
        body = p.inner_text("body")
        # pastikan halaman baru ini adalah halaman dokumen master kita
        if ids and NAME_BASE in body:
            return ids[0]
        time.sleep(3)
    return None


def main():
    url_out = ROOT / "data" / "drive_upload.json"
    already = None
    if url_out.exists():
        d = json.loads(url_out.read_text(encoding="utf-8"))
        already = d.get("fileId")
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = b.contexts[0]
        p = ctx.new_page()
        pg = ctx.new_page()

        # 0) kalau sudah pernah upload, hanya cek keberadaan
        if already:
            pg.goto(f"https://drive.google.com/drive/u/0/search?q=%22{NAME_BASE}%22",
                    wait_until="domcontentloaded", timeout=90000)
            pg.wait_for_timeout(4000)
            if NAME_BASE in pg.inner_text("body"):
                print(f"[upload] pakai file lama: {already}")
                pg.close(); p.close(); b.close()
                return 0

        # 1) coba langusung pakai input[type=file]
        pg.goto("https://drive.google.com/drive/u/0/my-drive", wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(6000)
        used = find_upload_input(pg)
        print("[upload] direct input:", used)
        if not used:
            # 2) pakai tombol New + menu upload
            if not click_new_button(pg):
                pg.screenshot(path=str(ROOT / "data" / "no_new.png"))
                raise RuntimeError("tombol New tidak ditemukan (screensho no_new.png)")
            pg.wait_for_timeout(1500)
            clicked = False
            with pg.expect_file_chooser(timeout=60000) as fc_info:
                clicked = click_upload_menuitem(pg)
            if not clicked:
                pg.screenshot(path=str(ROOT / "data" / "no_upload_item.png"))
                raise RuntimeError("item Upload tidak ditemukan (screensho)")
            fc = fc_info.value
            fc.set_files(str(FILE))

        print("[upload] mengunggah...")
        fid = find_result_id(pg)
        if not fid:
            pg.screenshot(path=str(ROOT / "data" / "no_id.png"))
            raise RuntimeError("fileId tidak ditemukan (screensho no_id.png)")
        url_out.write_text(json.dumps({"fileId": fid, "reused": False}), encoding="utf-8")
        print("[upload] fileId:", fid)
        print("[upload] link:", f"https://docs.google.com/spreadsheets/d/{fid}")
        pg.close(); p.close(); b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
