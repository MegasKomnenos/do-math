# -*- coding: utf-8 -*-
# 장부 1.2 「정의 절」: 기호 바로 뒤(45자 안)에 ':='가 오는 자리가 주장한 절에 있는지. 없으면 그 절의 첫 등장 문맥을 보인다.
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import 검토전체23_R13_use12 as U
from 검토전체23_R13_lib import *
secs=[]
for f in files:
    t=U.norm(rd(f)); cur=None; buf=[]
    for line in t.split("\n"):
        m=re.match(r"^### (\d+\.\d+)",line)
        m2=re.match(r"^## (\d+)\.",line)
        if m or m2:
            if cur is not None: secs.append((cur,f,"\n".join(buf)))
            cur=m.group(1) if m else m2.group(1)+".0"; buf=[line]
        else:
            buf.append(line)
    if cur is not None: secs.append((cur,f,"\n".join(buf)))
want=set(int(x) for x in sys.argv[1:])
for r in U.rows:
    ln=r["line"]
    if ln not in U.P: continue
    claimed=re.findall(r"(?<![\d.])(\d+\.\d+)(?![\d.])",r["sec"])
    defsecs=[]
    ctx={}
    for s,f,t in secs:
        ps=U.P[ln](t)
        for p in ps:
            if ":=" in t[p:p+45]:
                defsecs.append(s); break
        if ps and s in claimed:
            p=ps[0]
            ctx[s]=t[max(0,p-110):p+110].replace("\n"," ")
    miss=[c for c in claimed if c not in defsecs]
    if want:
        if ln in want:
            print(ln,r["sym"][:60],"| 주장:",claimed,"| ':=' 절:",sorted(set(defsecs)))
            for c in claimed: print("     ",c,"…"+ctx.get(c,"(없음)")+"…")
    elif miss:
        print(ln,r["sym"][:60],"| 주장:",claimed,"| ':=' 절:",sorted(set(defsecs)))
        for c in miss: print("     ",c,"…"+ctx.get(c,"(없음)")+"…")
