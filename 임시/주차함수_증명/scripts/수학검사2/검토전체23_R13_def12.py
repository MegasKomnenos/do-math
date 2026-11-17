# -*- coding: utf-8 -*-
# 장부 1.2 「정의 절」: 기호의 핵이 그 절에 나타나는지, 그 절보다 앞 절(1장 개관 제외)에 먼저 나타나는지.
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import 검토전체23_R13_use12 as U
from 검토전체23_R13_lib import *
# 본문 파일을 절(### N.M)로 자른다
secs=[]  # (secno, file, text)
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
def key(s):
    a,b=s.split("."); return (int(a),int(b))
order=[s[0] for s in secs]
for r in U.rows:
    ln=r["line"]
    if ln not in U.P: continue
    claimed=re.findall(r"(?<![\d.])(\d+\.\d+)(?![\d.])",r["sec"])
    occ=[]
    for s,f,t in secs:
        n=len(U.P[ln](t))
        if n: occ.append((s,n))
    occs=[o[0] for o in occ]
    msgs=[]
    for c in claimed:
        if c not in occs: msgs.append("정의 절 %s에 없음"%c)
    first=[o for o in occs if not o.startswith("1.")]
    cmin=min(claimed,key=key) if claimed else None
    if cmin and not cmin.startswith("1."):
        early=[o for o in first if key(o)<key(cmin)]
        if early: msgs.append("정의 절 %s보다 앞 절에 나타남: %s"%(cmin,early[:6]))
    if msgs: print(ln,r["sym"][:50],"| 정의 절:",r["sec"][:40],"|"," ; ".join(msgs))
