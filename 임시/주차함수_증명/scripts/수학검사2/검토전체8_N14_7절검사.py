# -*- coding: utf-8 -*-
r"""장부 7절의 「이 글의 글자」가 1.2(전역) 또는 1.1에 있는지(근사: 첫 글자 바탕 문자열) 본다."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
txt=open(os.path.join(root,"장부_v2.md"),encoding='utf-8').read().split("\n")
def sect(start,end):
    out=[]; on=False
    for i,l in enumerate(txt,1):
        if l.startswith(start): on=True; continue
        if on and l.startswith(end): break
        if on: out.append((i,l))
    return out
g12=" ".join(l for _,l in sect("### 1.2","### 1.3") if l.startswith("| $")).replace(" ","")
g11=" ".join(l for _,l in sect("### 1.1","### 1.2") if l.startswith("| $")).replace(" ","")
glob=g12+g11
def base(sym):
    s=sym.strip("$").replace(" ","")
    s=re.sub(r"\([^()]*\)$","",s)
    return s
missing=[]
for i,l in sect("## 7.","## 8."):
    if not l.startswith("| $"): continue
    cells=[c.strip() for c in l.strip().strip("|").split(" | ")]
    syms=re.findall(r"\$([^$]+)\$",cells[0])
    for s in syms:
        b=base(s)
        if b.replace(" ","") not in glob:
            # 더 느슨히: 바탕 글자(첨자 전)만
            b2=re.split(r"[_^(]",b)[0]
            if b2 and b2 in glob: continue
            missing.append((i,s))
print("7절에 있으나 1.1·1.2에 같은 꼴이 없는 글자:",len(missing))
for i,s in missing: print(f"  행{i}: ${s}$")
