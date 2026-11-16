import sys, pymupdf as fitz, statistics, collections
doc = fitz.open(sys.argv[1])
mm=72/25.4
isword=lambda ch: ('가'<=ch<='힣') or ch.isalnum()
res=[]
for pno in range(3, doc.page_count):
    p=doc[pno]; r=p.rect
    left,right=24*mm, r.width-24*mm
    d=p.get_text("rawdict")
    chars=[]
    for b in d["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for c in s["chars"]:
                    if c["c"].strip()=="": continue
                    x0,y0,x1,y1=c["bbox"]; chars.append(((y0+y1)/2,x0,x1,c["c"],s["size"],s["font"]))
    chars.sort()
    lines=[]; cur=[]
    for ch in chars:
        if cur and abs(ch[0]-cur[-1][0])>4: lines.append(cur); cur=[]
        cur.append(ch)
    if cur: lines.append(cur)
    for ln in lines:
        ln.sort(key=lambda c:c[1])
        if len(ln)<15: continue
        width=ln[-1][2]-ln[0][1]
        if width < (right-left)*0.9: continue
        # body font size ~10.5pt; skip tables (size<9.5) 
        size=statistics.median(c[4] for c in ln)
        if size<9.5: continue
        # gaps between Hangul/word chars in body (Type3) font
        gaps=[]
        for i in range(len(ln)-1):
            a,b=ln[i],ln[i+1]
            if 'Type3' in a[5] and 'Type3' in b[5] and isword(a[3]) and isword(b[3]):
                g=b[1]-a[2]
                if g>1.0: gaps.append(g)
        if not gaps: continue
        res.append((max(gaps)/size, pno+1, "".join(c[3] for c in ln)[:45]))
res.sort(reverse=True)
hist=collections.Counter(round(r[0]*2)/2 for r in res)
print("lines measured", len(res)); print("hist of max word-gap (em):", sorted(hist.items()))
print(">0.8em:", sum(1 for r in res if r[0]>0.8), " >1.0em:", sum(1 for r in res if r[0]>1.0), " >1.5em:", sum(1 for r in res if r[0]>1.5))
pages=collections.Counter(r[1] for r in res if r[0]>1.0)
print("pages with >1.0em lines:", len(pages))
for r in res[:25]: print(round(r[0],2), r[1], r[2])
