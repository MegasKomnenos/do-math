# -*- coding: utf-8 -*-
# 장부 7절 첫 열·2절 둘째 열(쓰는 글자·이름)의 글자체 토큰(\mathrm{..}, \mathfrak X, \mathsf X, \mathcal X, \mathsf{..})이
# 장 파일(본문+부록 D)에 실재하는지(후보 — 원문 확인용).
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
def norm(t):
    t=re.sub(r"\\(mathsf|mathfrak|mathcal|mathrm|mathbb)\{([A-Za-z])\}", r"\\\1 \2", t)
    return t
ALL=norm("\n".join(rd(f) for f in files+[a for a in appx if a.startswith("부록D")]))
J = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
def sect(a,b):
    s=next(i for i,l in enumerate(J) if l.startswith(a)); e=next(i for i,l in enumerate(J) if l.startswith(b)); return s,e
TOK=re.compile(r"\\mathrm\{[A-Za-z]+\}(?:\^\{\\mathrm\{?[A-Za-z ]+\}?\})?|\\math(?:frak|sf|cal) [A-Za-z](?:\^\{\\mathrm\{?[A-Za-z ]+\}?\}|\^\\[a-z]+)?|\\mathsf\{[A-Za-z]+\}")
def check(name,s,e,col):
    seen=set()
    for i in range(s,e):
        l=J[i]
        if not l.startswith("| "): continue
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        if len(c)<=col: continue
        cell=norm(c[col])
        for m in TOK.finditer(cell):
            t=m.group(0)
            if t in seen: continue
            seen.add(t)
            if t not in ALL:
                print(name,i+1,t,"|",cell[max(0,m.start()-60):m.end()+60])
s,e=sect("## 7. ","## 8. "); check("7절",s,e,0)
s,e=sect("## 2. ","## 3. "); check("2절",s,e,1)
