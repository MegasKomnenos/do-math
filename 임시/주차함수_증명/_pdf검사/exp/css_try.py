"""md 조각을 md2pdf의 HTML 단계로 만들고, 추가 CSS를 끼운 뒤 인쇄 폭 뷰포트에서 FIT_JS를 돌려 PNG로 찍는다.
사용: python css_try.py 입력.md 출력.png ["추가 CSS"]"""
import sys
from pathlib import Path
sys.path.insert(0, r"C:\math\도구")
import md2pdf
from playwright.sync_api import sync_playwright
src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
extra = sys.argv[3] if len(sys.argv) > 3 else ""
opts = md2pdf.parse_args([str(src), "--no-toc"])
text = md2pdf.escape_stray_asterisks(src.read_text(encoding="utf-8"))
text = md2pdf.escape_pipes_in_table_math(text)
md = md2pdf.build_markdown(); env = {"math": []}
body, title, headings = md2pdf.convert_markdown(md, text, env)
body = md2pdf.decorate(body)
kd = md2pdf.ensure_katex(opts.katex_dir, False)
rendered, errors, warnings = md2pdf.render_math(env["math"], kd, False)
body = md2pdf.tighten_quotes(md2pdf.substitute_math(body, rendered))
css = (kd / "node_modules" / "katex" / "dist" / "katex.min.css").as_uri()
html = md2pdf.build_html(body, title, css, opts).replace("</head>", f"<style>{extra}</style></head>")
hp = out.with_suffix(".html"); hp.write_text(html, encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.launch(); print("chromium", b.version)
    page = b.new_page(viewport={"width": md2pdf.content_width_px(opts), "height": 1200})
    page.goto(hp.as_uri()); page.evaluate("document.fonts.ready.then(()=>true)")
    page.emulate_media(media="print")
    page.evaluate(f"window.__md2pdfContentHeight = {md2pdf.content_height_px(opts)}")
    still = page.evaluate(md2pdf.FIT_JS)
    page.screenshot(path=str(out), full_page=True)
    print("still", still, "->", out)
    b.close()
