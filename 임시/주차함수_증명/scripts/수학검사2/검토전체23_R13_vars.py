# -*- coding: utf-8 -*-
# 장부 1.1 변수 글자의 「쓰이는 장」: 수식 안의 맨 글자(명령·로마체 이름·글자체 명령의 인수 제외)를 장별로 센다(후보).
import re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
def maths(t):
    out=[]
    for m in re.finditer(r"\$\$(.+?)\$\$|\$([^$\n]+?)\$",t,re.S):
        out.append((m.start(), m.group(1) or m.group(2)))
    return out
def strip(m):
    # 로마체·텍스트·연산자 이름의 인수 제거
    m=re.sub(r"\\(?:mathrm|text|operatorname|mathsf|mathbf|mathtt|mathit)\s*\{[^{}]*\}"," ",m)
    m=re.sub(r"\\(?:mathrm|mathsf|mathfrak|mathcal|mathbb|mathscr|mathbf)\s+[A-Za-z]"," ",m)
    m=re.sub(r"\\(?:mathfrak|mathcal|mathbb|mathscr)\s*\{[^{}]*\}"," ",m)
    m=re.sub(r"\\[A-Za-z]+"," ",m)   # 나머지 명령
    return m
letters=sys.argv[1:] or ["n","m","t","N","k","y","Y","i","j","u","v","r","d","q"]
res={L:collections.OrderedDict() for L in letters}
ctxs={L:collections.defaultdict(list) for L in letters}
for f in files+[a for a in appx if a.startswith("부록D")]:
    t=rd(f)
    for pos,m in maths(t):
        s=strip(m)
        for L in letters:
            for mm in re.finditer(r"(?<![A-Za-z])"+L+r"(?![A-Za-z])",s):
                res[L][f]=res[L].get(f,0)+1
                if len(ctxs[L][f])<int(os.environ.get("MAXN","0")):
                    ctxs[L][f].append((t.count("\n",0,pos)+1,m[:160].replace("\n"," ")))
for L in letters:
    print(L, dict(res[L]))
    for f in ctxs[L]:
        if os.environ.get("ONLY") and f not in os.environ["ONLY"].split(","): continue
        for c in ctxs[L][f]: print("    ",f,c[0],c[1])
