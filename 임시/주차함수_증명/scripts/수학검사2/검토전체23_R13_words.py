# -*- coding: utf-8 -*-
# 장부 3절 낱말: (1) 낱말이 장 파일에 실재하는지, (2) 첫 정의 절에 나타나는지, (3) 그 절보다 앞(1장·장 머리 제외)에 나타나는지(후보).
import re, sys, os, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
J = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
s = next(i for i,l in enumerate(J) if l.startswith("## 3. "))
e = next(i for i,l in enumerate(J) if l.startswith("## 4. "))
rows=[]
for i in range(s,e):
    l=J[i]
    if l.startswith("| ") and not l.startswith("| 낱말") and not l.startswith("|---"):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        rows.append((i+1,c))
print("행",len(rows),collections.Counter(len(c) for _,c in rows))
secs=[]
for f in files:
    t=rd(f); cur=None; buf=[]
    for line in t.split("\n"):
        m=re.match(r"^### (\d+\.\d+)",line); m2=re.match(r"^## (\d+)\.",line)
        if m or m2:
            if cur is not None: secs.append((cur,f,"\n".join(buf)))
            cur=m.group(1) if m else m2.group(1)+".0"; buf=[line]
        else: buf.append(line)
    if cur is not None: secs.append((cur,f,"\n".join(buf)))
apx="\n".join(rd(a) for a in appx if a.startswith("부록D"))
def key(sx):
    a,b=sx.split(".")[:2]; return (int(a),int(b))
out=[]
for ln,c in rows:
    words=[w.strip() for w in re.split(r"[,;]\s*",re.sub(r"\([^()]*\)","",c[0])) if w.strip()]
    claimed=re.findall(r"(?<![\d.])(\d+\.\d+)(?:\.\d+)?(?![\d.])",c[2])
    for w in words:
        w0=re.sub(r"\$[^$]*\$","",w).strip()
        if len(w0)<2: continue
        occ=[sx for sx,f,t in secs if w0 in t]
        inapx = w0 in apx
        msg=[]
        if not occ and not inapx: msg.append("글에 없음")
        elif not occ: msg.append("본문에 없음(부록 D에만)")
        else:
            for cl in claimed[:1]:
                if cl not in occ: msg.append("첫 정의 절 %s에 없음(첫 등장 %s)"%(cl,occ[0]))
                else:
                    early=[o for o in occ if key(o)<key(cl) and not o.startswith("1.") and not o.endswith(".0")]
                    if early: msg.append("첫 정의 절 %s 앞 등장: %s"%(cl,early[:5]))
        if msg: out.append((ln,w0,c[2][:30]," ; ".join(msg)))
mode=sys.argv[1] if len(sys.argv)>1 else "missing"
for o in out:
    if mode=="missing" and ("없음" in o[3]): print(*o,sep=" | ")
    if mode=="early" and ("앞 등장" in o[3]): print(*o,sep=" | ")
