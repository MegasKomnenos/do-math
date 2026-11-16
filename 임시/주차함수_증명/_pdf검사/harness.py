"""md2pdf 파이프라인의 HTML 단계를 재현하고 Chromium에서 넘침을 진단한다 (PDF는 만들지 않는다)."""
import sys, re, json, argparse
sys.path.insert(0, r"C:\math\도구")
import md2pdf
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("input"); ap.add_argument("--html", default=r"C:\math\임시\주차함수_증명\_pdf검사\full.html")
ap.add_argument("--no-fit", action="store_true")
a = ap.parse_args()
opts = md2pdf.parse_args([a.input])
text = Path(a.input).read_text(encoding="utf-8")
md = md2pdf.build_markdown(); env = {"math": []}
text = md2pdf.escape_stray_asterisks(text)
body, title, headings = md2pdf.convert_markdown(md, text, env)
body = md2pdf.decorate(body)
katex_dir = md2pdf.ensure_katex(opts.katex_dir, False)
rendered, errors, warnings = md2pdf.render_math(env["math"], katex_dir, False)
print("math", len(env["math"]), "errors", len(errors))
body = md2pdf.substitute_math(body, rendered)
for h in headings: h["html"] = md2pdf.substitute_math(h["html"], rendered)
katex_css = (katex_dir / "node_modules" / "katex" / "dist" / "katex.min.css").as_uri()
html = md2pdf.build_html(body, title, headings, katex_css, opts, None)
Path(a.html).write_text(html, encoding="utf-8")
print("html written", a.html, len(html))

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    page = b.new_page()
    w = md2pdf.content_width_px(opts)
    page.set_viewport_size({"width": w, "height": 1400})
    page.set_default_timeout(600000)
    page.goto(Path(a.html).as_uri(), wait_until="load")
    page.wait_for_function("document.fonts.status === 'loaded'", timeout=120000)
    page.emulate_media(media="print")
    still = [] if a.no_fit else page.evaluate(md2pdf.FIT_JS)
    print("viewport", w, "still:", [s[:50] for s in still])
    info = page.evaluate("""(w) => {
      const out = {scrollWidth: document.documentElement.scrollWidth, bodyScroll: document.body.scrollWidth, wide: []};
      for (const el of document.querySelectorAll('main *')) {
        const r = el.getBoundingClientRect();
        if (r.right > w + 1 || r.left < -1) {
          if (el.closest('.katex') && !el.classList.contains('katex')) continue;
          out.wide.push({tag: el.tagName, cls: el.className.toString().slice(0,40), left: Math.round(r.left), right: Math.round(r.right), txt: (el.textContent||'').trim().slice(0,60)});
        }
      }
      return out;
    }""", w)
    print("scrollWidth", info["scrollWidth"], "body", info["bodyScroll"])
    print("wide elements", len(info["wide"]))
    seen=set()
    for e in info["wide"]:
        key=(e["tag"], e["txt"][:30])
        if key in seen: continue
        seen.add(key); print("  ", e)
        if len(seen)>60: break
    b.close()
