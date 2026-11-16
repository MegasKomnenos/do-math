import pymupdf as fitz, tempfile, os
from pathlib import Path
from playwright.sync_api import sync_playwright
variants = {
 "plain": "",
 "main_clip": "main{overflow-x:clip}",
 "html_hidden": "html{overflow-x:hidden}",
 "body_clip": "body{overflow-x:clip}",
}
tmp = Path(tempfile.mkdtemp())
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge"); page = b.new_page()
    page.set_viewport_size({"width": 612, "height": 1400})
    for name, css in variants.items():
        html = f"""<!doctype html><html><head><meta charset=utf-8><style>@page{{size:A4}} body{{margin:0;font-size:14px;font-family:'Noto Serif KR',serif}} {css}
        h2{{font-size:20px}} h3{{font-size:16px}}</style></head><body>
        <h2>차례</h2><main><h2>1. 첫째 장</h2><p>본문 글자 가나다라마바사 아자차카타파하 가나다라마바사.</p><h3>1.1 소절</h3><p>x</p>
        <div style="width:1200px;background:#eee">넓은 상자 1200px</div><h2>2. 둘째 장 $\mathsf W$</h2><p>y</p></main></body></html>"""
        f = tmp / f"{name}.html"; f.write_text(html, encoding="utf-8")
        page.goto(f.as_uri()); page.emulate_media(media="print")
        sw = page.evaluate("document.documentElement.scrollWidth")
        pdf = page.pdf(prefer_css_page_size=True, margin={"top":"22mm","bottom":"24mm","left":"24mm","right":"24mm"}, tagged=True, outline=True)
        doc = fitz.open(stream=pdf, filetype="pdf")
        d = doc[0].get_text("rawdict"); sizes=set(); adv=None
        for bl in d["blocks"]:
            for l in bl["lines"]:
                for s in l["spans"]:
                    sizes.add(round(s["size"],1))
                    if adv is None and len(s["chars"])>3: adv = round(s["chars"][1]["bbox"][0]-s["chars"][0]["bbox"][0],2)
        print(name, "scrollWidth", sw, "pages", doc.page_count, "font sizes", sorted(sizes), "first adv", adv, "toc", doc.get_toc())
    b.close()
