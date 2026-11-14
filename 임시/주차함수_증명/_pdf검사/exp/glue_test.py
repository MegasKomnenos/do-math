from playwright.sync_api import sync_playwright
# 너비를 조절해 inline-block 바로 뒤의 쉼표가 줄 머리에 오는지 본다
variants = {
 "A plain": '<span class="ib">XXXXXXXXXXXXXXXX</span>, 다음',
 "B WJ": '<span class="ib">XXXXXXXXXXXXXXXX</span>&#x2060;, 다음',
 "C nowrap wrap": '<span style="white-space:nowrap"><span class="ib">XXXXXXXXXXXXXXXX</span>,</span> 다음',
 "D WJ inside ib end": '<span class="ib">XXXXXXXXXXXXXXXX&#x2060;</span>, 다음',
 "E ib display inline": '<span class="ib" style="display:inline">XXXXXXXXXXXXXXXX</span>, 다음',
 "F josa plain": '<span class="ib">XXXXXXXXXXXXXXXX</span>이다. 다음',
 "G josa WJ": '<span class="ib">XXXXXXXXXXXXXXXX</span>&#x2060;이다. 다음',
 "H josa nowrap": '<span style="white-space:nowrap"><span class="ib">XXXXXXXXXXXXXXXX</span>이다.</span> 다음',
 "I open plain": '앞 (<span class="ib">XXXXXXXXXXXXXXXX</span>) 다음',
 "J open WJ": '앞 (&#x2060;<span class="ib">XXXXXXXXXXXXXXXX</span>) 다음',
 "K open nowrap": '앞 <span style="white-space:nowrap">(<span class="ib">XXXXXXXXXXXXXXXX</span>)</span> 다음',
}
css = "body{font-family:'Noto Serif KR',serif;font-size:16px;word-break:keep-all;line-break:strict;overflow-wrap:anywhere;text-align:justify} .ib{display:inline-block;white-space:nowrap} p{margin:0 0 8px}"
js = r"""
() => { const out=[]; for (const p of document.querySelectorAll('p')) {
  const w=document.createTreeWalker(p, NodeFilter.SHOW_TEXT); let n; const items=[];
  while((n=w.nextNode())){ for(let i=0;i<n.data.length;i++){const r=document.createRange(); r.setStart(n,i); r.setEnd(n,i+1); const rc=r.getClientRects()[0]; if(!rc||rc.width===0)continue; items.push({ch:n.data[i],x:rc.left,y:Math.round(rc.top)});}}
  const ys=[...new Set(items.map(i=>i.y))].sort((a,b)=>a-b);
  out.push(ys.map(y=>items.filter(i=>i.y===y).sort((a,b)=>a.x-b.x).map(i=>i.ch).join('')));
} return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page()
    for width in (200, 230, 260):
        html = "<style>"+css+"</style>" + "".join(f'<p style="width:{width}px">가나다 라마바 사아자 차카타 {v}</p>' for v in variants.values())
        page.set_content(html); page.evaluate("document.fonts.ready.then(()=>true)")
        res = page.evaluate(js)
        print("== width", width)
        for name, lines in zip(variants, res):
            bad = any(l[:1] in ",이" or l.endswith("(") for l in lines)
            print(f"  {'BAD ' if bad else 'ok  '} {name:22s} {lines}")
    b.close()
