# -*- coding: utf-8 -*-
# 장부 4절 뺌 행의 주석이 부르는 현행 라벨과 그 부분 표지((가)(ㄱ)(i) 등)가 실재하는지.
import re, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
d=json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_dead.json"),encoding="utf-8"))
for ln,lab,c in d["dead"]:
    txt=c[2]+" "+c[3]
    for m in re.finditer(r"`\{?\{?(\d+:[A-Za-z0-9\-]+)\}?\}?`((?:\([가-힣ㄱ-ㅎivx]+\))*)",txt):
        L=m.group(1); parts=re.findall(r"\(([가-힣ㄱ-ㅎivx]+)\)",m.group(2))
        if L not in hd:
            print(ln,lab,"라벨 없음:",L, "|", txt[max(0,m.start()-40):m.end()+30]); continue
        st,full=block(L)
        for p in parts:
            if "("+p+")" not in full:
                print(ln,lab,"부분 없음:",L,p)
