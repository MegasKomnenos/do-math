import pymupdf as fitz, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
tmp = Path(tempfile.mkdtemp())
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge"); page = b.new_page(); page.set_viewport_size({"width": 612, "height": 1400})
    for name, css in {"wrapper_clip": "#sheet{overflow-x:clip}", "wrapper_hidden": "#sheet{overflow-x:hidden}", "main_clip_only": "main{overflow-x:clip}"}.items():
        html = f"""<!doctype html><html><head><meta charset=utf-8><style>@page{{size:A4}} body{{margin:0;font-size:14px}} {css} h2{{break-before:page}}</style></head><body><div id="sheet">
        <header><h1>제목</h1><div style="width:1300px;background:#eee">머리 넓은 상자</div></header><nav><h2>차례</h2><p>항목</p></nav>
        <main><h2>1. 첫째 장</h2><p>본문 글자 가나다라마바사 아자차카타파하.</p><div style="width:1200px;background:#eee">넓은 상자</div>{'<p>줄</p>'*80}<h2>2. 둘째</h2><p>끝</p></main></div></body></html>"""
        f = tmp / f"{name}.html"; f.write_text(html, encoding="utf-8")
        page.goto(f.as_uri()); page.emulate_media(media="print")
        sw = page.evaluate("document.documentElement.scrollWidth")
        pdf = page.pdf(prefer_css_page_size=True, margin={"top":"22mm","bottom":"24mm","left":"24mm","right":"24mm"})
        doc = fitz.open(stream=pdf, filetype="pdf"); sizes=set()
        for bl in doc[0].get_text("dict")["blocks"]:
            for l in bl.get("lines", []):
                for s in l["spans"]: sizes.add(round(s["size"],1))
        print(name, "scrollWidth", sw, "pages", doc.page_count, "sizes", sorted(sizes))
    b.close()
