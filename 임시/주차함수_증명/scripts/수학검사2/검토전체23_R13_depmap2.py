# -*- coding: utf-8 -*-
# 의존지도 1절의 「첫 판 번호」(장부 4절), 「요지」(머리 이름), 「문헌」(10.3 표), 「부록 D 계산」(10.2 표) 열을 원천과 맞댄다.
import re, json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
L = open(os.path.join(base,"의존지도_v2.md"),encoding="utf-8").read().split("\n")
s1 = next(i for i,l in enumerate(L) if l.startswith("## 1. "))
s11 = next(i for i,l in enumerate(L) if l.startswith("### 1.1 "))
rows=[]
for i in range(s1,s11):
    l=L[i]
    if l.startswith("| `{{"):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        rows.append((i+1,c))
# 장부 4절
J = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
s = next(i for i,l in enumerate(J) if l.startswith("## 4. "))
e = next(i for i,l in enumerate(J) if l.startswith("## 5. "))
first={}
for i in range(s,e):
    l=J[i]
    if l.startswith("| ") and "{{" in l.split(" | ")[-1]:
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        first[c[5][2:-2]]=(c[0],c[1])
# 10.2, 10.3
ch10=rd("장10").split("\n")
dmap=collections.defaultdict(list); lit=collections.defaultdict(list)
mode=None
LAB=re.compile(r"\{\{(\d+:[A-Za-z0-9\-]+)\}\}")
for l in ch10:
    if l.startswith("### 10.2"): mode="D"
    elif l.startswith("### 10.3"): mode="L"
    elif l.startswith("| ") and not l.startswith("|---"):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        if mode=="D" and c[0].startswith("부록 D."):
            name=re.search(r"\{\{D:([A-Za-z0-9\-]+)\}\}",c[0]).group(1)
            for lab in LAB.findall(c[1]): dmap[lab].append((name,c[2]))
        if mode=="L" and len(c)>=3 and c[0]!="문헌":
            for lab in LAB.findall(c[2]): lit[lab].append(c[0].split(",")[0])
for ln,c in rows:
    lab=c[0].strip("`")[2:-2]; h=hd[lab]
    # 첫 판 번호
    f=first.get(lab)
    exp = "새 진술" if (not f or f[0]=="—") else "%s %s"%(f[1],f[0])
    if c[2]!=exp: print("첫 판 번호 다름",ln,lab,"표:",c[2],"| 장부:",exp)
    # 요지
    if h["name"] and c[3]!=h["name"]: print("요지 다름",ln,lab,"표:",c[3][:80],"| 머리:",h["name"][:80])
    # 부록 D
    td=set(re.findall(r"D\.\{?\{?D?:?([A-Za-z0-9\-]+)",c[8])) if c[8]!="없음" else set()
    td=set(re.findall(r"\{\{D:([A-Za-z0-9\-]+)\}\}",c[8]))
    ed=set(n for n,_ in dmap.get(lab,[]))
    if td!=ed: print("부록 D 다름",ln,lab,"표:",c[8][:160],"| 10.2:",sorted(ed))
    else:
        for n,ar in dmap.get(lab,[]):
            if ar not in c[8]: print("산술 다름",ln,lab,n,"표:",c[8][:200],"| 10.2:",ar)
    # 문헌
    el=lit.get(lab,[])
    if (c[7] in ("—","없음")) != (len(el)==0):
        print("문헌 유무 다름",ln,lab,"표:",c[7][:120],"| 10.3:",el)
    else:
        for a in el:
            if a.split(" ")[0] not in c[7]: print("문헌 저자 없음",ln,lab,a,"| 표:",c[7][:160])
