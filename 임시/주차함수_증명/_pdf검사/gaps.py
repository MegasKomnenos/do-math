import sys, pymupdf as fitz, statistics
doc = fitz.open(sys.argv[1])
mm=72/25.4
bad=[]; total_lines=0
for pno in range(doc.page_count):
    p=doc[pno]; r=p.rect
    left,right=24*mm, r.width-24*mm
    d=p.get_text("rawdict")
    # gather all chars with positions, group into lines by y-center
    chars=[]
    for b in d["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for c in s["chars"]:
                    if c["c"].strip()=="" : continue
                    x0,y0,x1,y1=c["bbox"]; chars.append(((y0+y1)/2,x0,x1,c["c"],s["size"]))
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
        if width < (right-left)*0.9: continue  # not a full justified line
        total_lines+=1
        gaps=[ln[i+1][1]-ln[i][2] for i in range(len(ln)-1)]
        gaps=[g for g in gaps if g>0.5]
        if not gaps: continue
        size=statistics.median(c[4] for c in ln)
        big=[g for g in gaps if g>size*0.9]   # gap wider than ~0.9em
        if len(big)>=2 or (big and max(big)>size*1.6):
            bad.append((pno+1, round(max(gaps)/size,2), len(big), "".join(c[3] for c in ln)[:50]))
print("full lines", total_lines, "stretched", len(bad))
import collections
print("by page:", sorted(collections.Counter(b[0] for b in bad).items())[:80])
for b in bad[:40]: print(b)
