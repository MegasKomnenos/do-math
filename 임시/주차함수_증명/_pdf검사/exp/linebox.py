"""HTML을 인쇄 폭 뷰포트로 열어 FIT_JS를 돌린 뒤, 각 문단의 시각적 줄 머리/끝 글자와 넘침을 찍는다. 변형 실험용."""
import sys, re
sys.path.insert(0, r"C:\math\도구")
import md2pdf
from pathlib import Path
from playwright.sync_api import sync_playwright
html_path = Path(sys.argv[1]).resolve()
opts = md2pdf.parse_args([str(html_path)])
w = md2pdf.content_width_px(opts)
JS = r"""
() => {
  const out = [];
  for (const p of document.querySelectorAll('main p')) {
    const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    const items = []; let n;
    while ((n = walker.nextNode())) {
      for (let i = 0; i < n.data.length; i++) {
        const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + 1);
        const rc = r.getClientRects()[0]; if (!rc || rc.width === 0) continue;
        items.push({ch: n.data[i], x: rc.left, y: Math.round(rc.top), r: rc.right});
      }
    }
    const lines = new Map();
    for (const it of items) { const k = Math.round(it.y / 8); if (!lines.has(k)) lines.set(k, []); lines.get(k).push(it); }
    const res = [];
    for (const [k, arr] of [...lines.entries()].sort((a, b) => a[0] - b[0])) {
      arr.sort((a, b) => a.x - b.x);
      res.push({first: arr[0].ch, last: arr[arr.length - 1].ch, right: Math.round(arr[arr.length-1].r), txt: arr.map(a => a.ch).join('').slice(0, 40)});
    }
    out.push({w: p.clientWidth, lines: res});
  }
  return out;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": w, "height": 1400})
    page.goto(html_path.as_uri())
    page.evaluate("document.fonts.ready.then(() => true)")
    page.emulate_media(media="print")
    page.evaluate(f"window.__md2pdfContentHeight = {md2pdf.content_height_px(opts)}")
    still = page.evaluate(md2pdf.FIT_JS)
    for para in page.evaluate(JS):
        print("para width", para["w"])
        for ln in para["lines"]:
            flag = ("  <<OVER" if ln["right"] > para["w"] + 1 else "")
            print("   first=%r last=%r right=%d %s%s" % (ln["first"], ln["last"], ln["right"], ln["txt"], flag))
    b.close()
