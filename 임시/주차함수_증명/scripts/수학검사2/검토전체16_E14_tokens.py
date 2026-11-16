# -*- coding: utf-8 -*-
"""E14: 1.2 전역 기호 가운데 로마체·산세리프·프락투어·필기체 토큰을 고정 문자열로 장 파일에서 찾아 「쓰이는 장」·「정의 절」과 견준다."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
BS = chr(92)
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
texts = {f: open(f"{ROOT}/장v2/{f}.md", encoding='utf-8').read() for f in files}
def sections(txt):
    return [(m.start(), m.group(1)) for m in re.finditer(r'^#+\s*(\d+(?:\.\d+)*)[\s.]', txt, re.M)]
secs = {f: sections(t) for f,t in texts.items()}
def sec_at(f,pos):
    cur=None
    for p,s in secs[f]:
        if p<=pos: cur=s
        else: break
    return cur
lines = open(f"{ROOT}/장부_v2.md", encoding='utf-8').read().split("\n")
s = next(i for i,l in enumerate(lines) if l.startswith("### 1.2"))
e = next(i for i,l in enumerate(lines) if l.startswith("### 1.3"))
def chnum(f): return int(re.sub(r'[AB]$','',f[1:]))
def variants(tok):
    vs={tok}
    vs|={re.sub(r'([\^_])\{([A-Za-z0-9])\}', r'\1\2', v) for v in list(vs)}
    vs|={re.sub(r'([\^_])([A-Za-z0-9])(?![A-Za-z0-9{])', r'\1{\2}', v) for v in list(vs)}
    vs|={v.replace(BS+'prime',"'") for v in list(vs)}
    vs|={v.replace(' ','') for v in list(vs)}
    return vs
pat_cmd = re.compile(BS+BS+r'math(rm|sf|frak|cal)|'+BS+BS+r'Pr|'+BS+BS+r'mathbb')
for l in lines[s:e]:
    if not l.startswith("| $"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    latex, basefont, meaning, defsec, chs, old, rec = cells
    if not pat_cmd.search(latex): continue
    items=[x.strip().strip('$') for x in re.split(r',\s*(?=\$)', latex)]
    toks=[]
    for it in items:
        it=re.sub(r'\(.*$','',it).strip()
        if it: toks.append(it)
    if chs=='전 장': claimed=set(range(1,12))
    else: claimed=set(int(x) for x in re.findall(r'\d+', chs))
    found={}
    firsts=[]
    for f,t in texts.items():
        best=None
        for tok in toks:
            for v in variants(tok):
                i=t.find(v)
                if i>=0:
                    found.setdefault(chnum(f), set()).add(sec_at(f,i))
                    if best is None or i<best: best=i
        if best is not None: firsts.append((chnum(f), sec_at(f,best), f, t.count("\n",0,best)+1))
    fset=set(found)
    extra=sorted(fset-claimed); missing=sorted(claimed-fset)
    first = min(firsts) if firsts else None
    flag = ""
    if extra: flag += f" 더 있음:{extra}"
    if missing: flag += f" 못 찾음:{missing}"
    print(f"{latex[:55]:55s} | 장부:{chs:26s} 정의절:{defsec:10s} | 찾음:{sorted(fset)} 첫:{first}{flag}")
