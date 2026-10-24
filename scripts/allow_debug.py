"""Debug: inspeksi elemen 'Allow access' di RINGKASAN (kemunculan & bounding box)."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FID = json.loads((ROOT / "data" / "drive_upload.json").read_text(encoding="utf-8"))["fileId"]

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    p = ctx.new_page()
    p.goto(f"https://docs.google.com/spreadsheets/d/{FID}/edit",
           wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(6000)
    for t in p.query_selector_all(".docs-sheet-tab"):
        if "RINGKASAN" in (t.inner_text() or ""):
            t.click()
            break
    p.wait_for_timeout(2500)
    nb = p.locator("#t-name-box").first
    nb.click(); p.wait_for_timeout(200)
    nb.fill("C2"); p.keyboard.press("Enter")
    p.wait_for_timeout(2500)

    info = p.evaluate("""() => {
      const out = [];
      const walk = (doc, tag) => {
        for (const el of doc.querySelectorAll('*')) {
          const t = (el.innerText || '').trim();
          if (!t.includes('Allow access')) continue;
          const bb = el.getBoundingClientRect();
          if (out.filter(o => o.tag === tag).length >= 12) continue;
          out.push({frame: tag, tag: el.tagName, cls: (el.className||'').toString().slice(0,80),
                    role: el.getAttribute('role'), rect: {x: Math.round(bb.x), y: Math.round(bb.y),
                    w: Math.round(bb.width), h: Math.round(bb.height)}, text: t.slice(0,40)});
        }
      };
      walk(document, 'main');
      for (let i = 0; i < window.frames.length; i++) {
        try { walk(window.frames[i].document, 'iframe' + i); } catch (e) {}
      }
      return out;
    }""")
    for r in info:
        print(r)
    p.screenshot(path=str(ROOT / "data" / "allow_debug.png"))
    p.close(); b.close()
