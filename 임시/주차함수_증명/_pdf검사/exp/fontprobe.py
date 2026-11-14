from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0, r"C:\math\도구"); import md2pdf
html = f"""<style>body{{font-family:{md2pdf.FONT_BODY};font-size:16px}} p.t{{text-spacing-trim:trim-all}} p.n{{font-family:"Noto Serif KR"}}</style>
<p id=a>가나다 123 abc 「순열을 거쳐 세기」 라</p><p id=b class=t>가나다 123 abc 「순열을 거쳐 세기」 라</p><p id=c class="t n">가나다 123 abc 「순열을 거쳐 세기」 라</p>"""
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page(); page.set_content(html)
    page.evaluate("document.fonts.ready.then(()=>true)")
    cdp = page.context.new_cdp_session(page); cdp.send("DOM.enable"); cdp.send("CSS.enable")
    doc = cdp.send("DOM.getDocument", {"depth": -1})
    for sel in ("#a", "#b", "#c"):
        nid = cdp.send("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": sel})["nodeId"]
        fonts = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": nid})["fonts"]
        w = page.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().width")
        print(sel, round(w), [(f["familyName"], f["glyphCount"]) for f in fonts])
    b.close()
