# -*- coding: utf-8 -*-
"""E14: 장부 3절 낱말의 「첫 정의 절」을 장 파일에서 첫 출현 자리와 견준다(앞선 장에서 먼저 나오는 낱말을 뽑는다)."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
texts=[(f, open(f"{ROOT}/장v2/{f}.md",encoding='utf-8').read()) for f in files]
def secs(txt):
    out=[]
    for m in re.finditer(r'^#+\s*(\d+(?:\.\d+)*)[\s.]', txt, re.M): out.append((m.start(), m.group(1)))
    return out
S={f:secs(t) for f,t in texts}
def sec_at(f,pos):
    cur=None
    for p,s in S[f]:
        if p<=pos: cur=s
        else: break
    return cur
def chnum(f): return int(re.sub(r'[AB]$','',f[1:]))
lines=open(f"{ROOT}/장부_v2.md",encoding='utf-8').read().split("\n")
s=next(i for i,l in enumerate(lines) if l.startswith("## 3."))
e=next(i for i,l in enumerate(lines) if l.startswith("## 4."))
def secnum(x):
    m=re.match(r'(\d+)(?:\.(\d+))?',x)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else None
for l in lines[s:e]:
    if not l.startswith("| ") or l.startswith("| 낱말") or l.startswith("|---"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells)<4: continue
    words, meaning, first, old = cells[:4]
    if first.startswith('—') or first.startswith('부록'): continue
    claimed=[secnum(x.strip()) for x in re.split(r'[,·;]', first) if secnum(x.strip())]
    if not claimed: continue
    cmin=min(claimed)
    for w in [x.strip() for x in words.split(',')]:
        w=re.sub(r'\(.*?\)','',w).strip()
        if not w or w.startswith('$') or len(w)<2: continue
        for f,t in texts:
            i=t.find(w)
            if i>=0:
                sec=sec_at(f,i); sn=secnum(sec) if sec else (chnum(f),0)
                line=t.count("\n",0,i)+1
                if sn is None or sn<cmin:
                    if chnum(f)==1 and cmin>(1,99): tag="(1장)"
                    elif sn and sn[0]==cmin[0] and sn[1]==0: tag="(장 머리)"
                    else: tag="**앞선 장**"
                    print(f"{w:18s} 첫 정의 절 {first:12s} 첫 출현 {f}:{line} §{sec} {tag} :: {t[max(0,i-40):i+40].replace(chr(10),' ')}")
                break
