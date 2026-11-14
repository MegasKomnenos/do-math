"""조립본 전체를 HTML 단계로 올려 FIT_JS를 돌린 뒤, 표마다 높이(쪽 본문 높이 대비)와 break-inside 값을 찍는다."""
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
body = md2pdf.tighten_quotes(md2pdf.substitute_math(body, rendered))
css = (kd / "node_modules" / "katex" / "dist" / "katex.min.css").as_uri()
hp = Path(r"C:\math\임시\주차함수_증명\_pdf검사\exp\full_stage.html"); hp.write_text(md2pdf.build_html(body, title, css, opts), encoding="utf-8")
ch = md2pdf.content_height_px(opts)
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page(viewport={"width": md2pdf.content_width_px(opts), "height": 1400})
    page.set_default_timeout(600000)
    page.goto(hp.as_uri(), wait_until="load"); page.evaluate("document.fonts.ready.then(()=>true)"); page.emulate_media(media="print")
    page.evaluate(f"window.__md2pdfContentHeight = {ch}")
    page.evaluate(md2pdf.FIT_JS)
    rows = page.evaluate(r"""() => Array.from(document.querySelectorAll('table')).map(t => ({h: Math.round(t.getBoundingClientRect().height), bi: t.style.breakInside, rows: t.querySelectorAll('tr').length, last: ((t.querySelector('tbody tr:last-child td')||{}).textContent||'').slice(0,40), head: (t.querySelector('th')||{}).textContent||'', first: ((t.querySelector('td')||{}).textContent||'').slice(0,30)}))""")
    print("content height px", ch, "tables", len(rows))
    import json; json.dump(rows, open(r"C:\math\임시\주차함수_증명\_pdf검사\exp/tables.json","w",encoding="utf-8"), ensure_ascii=False)
    for r in rows: print(f"{r['h']:5d}px {r['h']/ch:5.2f} rows={r['rows']:3d} bi={r['bi'] or '-':6s} {r['head'][:14]!r} {r['first']!r}")
    b.close()
