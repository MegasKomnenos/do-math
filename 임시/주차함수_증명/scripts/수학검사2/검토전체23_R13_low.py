# -*- coding: utf-8 -*-
# 표가 든 장 가운데 기계 검색의 건수가 적은(<=N) 자리를 문맥과 함께 보인다(원문 확인용).
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import 검토전체23_R13_use12 as U
N=int(sys.argv[1]) if len(sys.argv)>1 else 2
for r in U.rows:
    ln=r["line"]
    if ln not in U.P: continue
    claimed=set(int(x) for x in re.findall(r"\d+",r["chs"]))
    for ch in sorted(claimed):
        hits=[]
        for f,t in U.texts.get(ch,[]):
            for p in U.P[ln](t):
                hits.append((f,t.count("\n",0,p)+1,t[max(0,p-80):p+60].replace("\n"," ")))
        if 0<len(hits)<=N:
            for h in hits:
                print(ln,r["sym"][:40],"| 장",ch,"|",h[0],h[1],"…"+h[2]+"…")
