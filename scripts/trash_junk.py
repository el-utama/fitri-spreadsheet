"""Buang (trash) 2 file Drive sisa upload master yang tidak terpakai.
Strategi: halaman search Drive -> centang baris file -> tombol toolbar 'Move to trash'
(fallback: klik kanan baris -> item menu berisi 'trash'/'bin'/'remove')."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
JUNK = [
    "1niwoQ6CzNYDsre4LMc3h3kDlL_a1XjAC",   # xlsx lama lama (tab korup: 17 MASTER, 11 TEMPLET_PC)
    "12ttwamDnzftP4SFI8S3XWzyOHFozfW1N1lr8wkqdJHI",  # duplikat hasil konversi
]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    for fid in JUNK:
        p.goto("https://drive.google.com/drive/u/0/search?q=%22master_karyawan%22",
               wait_until="domcontentloaded", timeout=90000)
        p.wait_for_timeout(5000)
        row = p.query_selector(f'[data-id="{fid}"]')
        if not row:
            print(f"[{fid}] tidak ada di hasil search (mungkin sudah terhapus)")
            continue
        # strategi 1: centang checkbox baris -> tombol toolbar "Move to trash"
        try:
            cb = row.query_selector("div[role=checkbox]") or row.evaluate_handle(
                "el => el.closest('[data-id]').querySelector('div[role=checkbox]')")
            cb.as_element().click(timeout=5000)
            p.wait_for_timeout(1500)
            done = False
            for label in ("Move to trash", "Move to bin", "Hapus", "Remove", "Buang"):
                for el in p.query_selector_all("div[role=button], button"):
                    aria = ((el.get_attribute("aria-label") or "") + " "
                            + (el.inner_text() or "")).lower()
                    if label.lower() in aria and el.is_visible():
                        el.click()
                        p.wait_for_timeout(2500)
                        print(f"[{fid}] dibuang via checkbox ('{label}')")
                        done = True
                        break
                if done:
                    break
            if done:
                continue
        except Exception as e:
            print(f"[{fid}] strategi checkbox gagal:", type(e).__name__)
        # strategi 2: klik kanan baris -> menu konteks
        try:
            row = p.query_selector(f'[data-id="{fid}"]')
            row.click(button="right", timeout=5000)
            p.wait_for_timeout(1500)
            done = False
            for name in ("Move to trash", "Move to bin", "Hapus", "Remove"):
                for el in p.query_selector_all('[role="menuitem"], [role="menuitemcheckbox"]'):
                    if name.lower() in (el.inner_text() or "").lower():
                        el.click()
                        p.wait_for_timeout(2500)
                        print(f"[{fid}] dibuang via menu konteks ('{name}')")
                        done = True
                        break
                if done:
                    break
            if not done:
                print(f"[{fid}] item Buang tidak ditemukan -> hapus manual")
        except Exception as e:
            print(f"[{fid}] strategi klik kanan gagal:", type(e).__name__)
    p.screenshot(path=str(ROOT / "data" / "trash_result.png"))
    p.close(); b.close()
print("[selesai]")
