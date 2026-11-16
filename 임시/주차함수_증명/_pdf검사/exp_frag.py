"""문단 안 디스플레이 수식이 쪽 경계에 놓일 때 글자 조각이 남는지(현 구조 vs 분리 구조) 재현한다."""
import sys, re, tempfile, pymupdf as fitz
sys.path.insert(0, r"C:\math\도구"); import md2pdf
from pathlib import Path
from playwright.sync_api import sync_playwright
kd = md2pdf.ensure_katex(md2pdf.DEFAULT_CACHE, False)
tex = r"J_{n+1}(z)=\sum_{i=0}^{n}\binom ni(z+i+1)\,p_i\,J_{n-i}(z)+\mathbf 1_{n\ge k-1}\binom n{k-1}p_{k-1}p_{n-k+1}"
(html_disp,), _, _ = md2pdf.render_math([(tex, True)], kd, False)
css_link = (kd / "dist" / "katex.min.css").as_uri()
opts = md2pdf.parse_args(["x.md"])
from string import Template
css = Template(md2pdf.CSS).substitute({"font_body": opts.font_body, "font_head": opts.font_head, "font_mono": md2pdf.FONT_MONO,
    "font_size": opts.font_size, "line_height": opts.line_height, "paper": opts.paper, "align": "justify", "h2_break": "", "toc_break": "", "math_scale": opts.math_scale})
mm = 72/25.4
def run(page, body, tag):
    html = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><link rel="stylesheet" href="{css_link}"><style>{css}</style></head><body><main>{body}</main></body></html>'
    f = Path(tempfile.mkdtemp()) / "t.html"; f.write_text(html, encoding="utf-8")
    page.goto(f.as_uri()); page.wait_for_function("document.fonts.status === 'loaded'"); page.emulate_media(media="print")
    pdf = page.pdf(prefer_css_page_size=True, margin={"top":"22mm","bottom":"24mm","left":"24mm","right":"24mm"})
    doc = fitz.open(stream=pdf, filetype="pdf"); bad = []
    for pno in range(doc.page_count):
        p = doc[pno]; bottom = p.rect.height - 24*mm
        for b in p.get_text("dict")["blocks"]:
            if b["type"] == 0 and b["bbox"][3] > bottom + 1.5: bad.append((pno+1, round(b["bbox"][3],1), "".join(s["text"] for l in b["lines"] for s in l["spans"])[:20]))
    return doc.page_count, bad
filler = "<p>" + "가나다라 마바사 아자차카 타파하 " * 20 + "</p>"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge"); page = b.new_page(); page.set_viewport_size({"width": 612, "height": 1400})
    for n in range(14, 24):
        body_old = filler*n + f'<p>(나) 범위에서 다음이 성립한다. 아래 식을 보자 {html_disp}\n이다.</p>' + filler
        body_new = filler*n + f'<div class="para"><p>(나) 범위에서 다음이 성립한다. 아래 식을 보자</p><div class="dmath" style="break-inside:avoid">{html_disp}</div><p class="cont">이다.</p></div>' + filler
        for tag, body in (("old", body_old), ("new", body_new)):
            pages, bad = run(page, body, tag)
            if bad: print(n, tag, pages, bad)
    print("done")
    b.close()
