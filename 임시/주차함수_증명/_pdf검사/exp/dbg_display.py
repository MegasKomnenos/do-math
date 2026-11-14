import sys
from pathlib import Path
sys.path.insert(0, r"C:\math\도구")
import md2pdf
from playwright.sync_api import sync_playwright
src = Path(sys.argv[1]).resolve()
opts = md2pdf.parse_args([str(src), "--no-toc"])
text = md2pdf.escape_pipes_in_table_math(md2pdf.escape_stray_asterisks(src.read_text(encoding="utf-8")))
md = md2pdf.build_markdown(); env = {"math": []}
body, title, headings = md2pdf.convert_markdown(md, text, env); body = md2pdf.decorate(body)
kd = md2pdf.ensure_katex(opts.katex_dir, False)
rendered, errors, warnings = md2pdf.render_math(env["math"], kd, False)
body = md2pdf.substitute_math(body, rendered)
css = (kd / "node_modules" / "katex" / "dist" / "katex.min.css").as_uri()
hp = src.with_name(src.stem + "_dbg.html"); hp.write_text(md2pdf.build_html(body, title, css, opts), encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page(viewport={"width": md2pdf.content_width_px(opts), "height": 1200})
    page.goto(hp.as_uri()); page.evaluate("document.fonts.ready.then(()=>true)"); page.emulate_media(media="print")
    page.evaluate(f"window.__md2pdfContentHeight = {md2pdf.content_height_px(opts)}")
    page.evaluate(md2pdf.FIT_JS)
    info = page.evaluate(r"""() => Array.from(document.querySelectorAll('.katex-display')).map(el => {
      const k = el.querySelector(':scope > .katex'); const kh = k.querySelector('.katex-html');
      const grps = Array.from(kh.querySelectorAll(':scope > .vr-grp'));
      const bases = Array.from(kh.children).filter(n => n.classList.contains('base'));
      return {avail: el.clientWidth, scroll: k.scrollWidth, fs: k.style.fontSize, ngrp: grps.length, nbaseTop: bases.length,
        grps: grps.map(g => [Math.round(g.getBoundingClientRect().width), (g.textContent||'').slice(0,25), g.dataset.depth]),
        kids: Array.from(kh.children).map(c => c.className.slice(0,20)),
        txt: (kh.textContent||'').slice(0,60)}; })""")
    for d in info: print(d)
    b.close()
