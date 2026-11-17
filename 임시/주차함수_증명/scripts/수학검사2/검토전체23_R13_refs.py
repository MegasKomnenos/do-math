# -*- coding: utf-8 -*-
# 장부·의존지도·구조표가 부르는 라벨·종류·부분 표지·절 번호·식 번호·부록 D 라벨이 장 파일에 실재하는지(후보 — 원문 확인용).
import re, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
target = sys.argv[1]
L = open(os.path.join(base, target), encoding="utf-8").read().split("\n")
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
hi = int(sys.argv[3]) if len(sys.argv) > 3 else len(L)
# 절 목록, 식 번호, D 라벨
secset=set(); tags=set(); dlabels=set()
for f in files+appx:
    t=rd(f)
    for m in re.finditer(r"^#{2,5} (\d+(?:\.\d+)+)",t,re.M): secset.add(m.group(1))
    for m in re.finditer(r"^## (\d+)\.",t,re.M): secset.add(m.group(1))
    for m in re.finditer(r"\\tag\{([^}]*)\}",t): tags.add(m.group(1))
    for m in re.finditer(r"^### D\.\{\{D:([A-Za-z0-9\-]+)\}\}",t,re.M): dlabels.add(m.group(1))
KIND=r"(정의|정리|명제|보조정리|따름정리)"
for i in range(lo-1,hi):
    line=L[i]
    # 1. 라벨 실재와 종류
    for m in re.finditer(r"\{\{(\d+:[A-Za-z0-9\-]+)\}\}",line):
        lab=m.group(1)
        if lab not in hd:
            print(i+1,"라벨 없음:",lab,"|",line[max(0,m.start()-60):m.end()+40]); continue
        # 종류: 바로 앞 낱말
        pre=line[max(0,m.start()-12):m.start()]
        km=re.search(KIND+r" `?$",pre)
        if km and km.group(1)!=hd[lab]["kind"]:
            print(i+1,"종류 다름:",lab,"글:",km.group(1),"머리:",hd[lab]["kind"],"|",line[max(0,m.start()-40):m.end()+20])
        # 부분 표지
        post=line[m.end():m.end()+40]
        pm=re.match(r"`?((?:\((?:[가-하]|[ㄱ-ㅎ]|[ivx]+|[a-z]′?)\))+)",post)
        if pm:
            st,full=block(lab)
            for p in re.findall(r"\(([^()]+)\)",pm.group(1)):
                if "("+p+")" not in full:
                    print(i+1,"부분 표지 없음:",lab,"("+p+")","|",line[max(0,m.start()-30):m.end()+40])
    # 2. 부록 D 라벨
    for m in re.finditer(r"\{\{D:([A-Za-z0-9\-]+)\}\}",line):
        if m.group(1) not in dlabels: print(i+1,"D 라벨 없음:",m.group(1),"|",line[max(0,m.start()-50):m.end()+30])
    # 3. 절 번호 "N.M절", "N.M.K절"
    for m in re.finditer(r"(?<![\d.])(\d{1,2}(?:\.\d{1,2}){1,2})절",line):
        s=m.group(1)
        if s not in secset:
            ctx=line[max(0,m.start()-50):m.end()+30]
            print(i+1,"절 없음:",s,"|",ctx)
    # 4. 식 번호 (N.M)
    for m in re.finditer(r"\((\d{1,2}\.\d{1,3}[a-z]?)\)",line):
        if m.group(1) not in tags:
            ctx=line[max(0,m.start()-50):m.end()+30]
            print(i+1,"식 번호 없음:",m.group(1),"|",ctx)
