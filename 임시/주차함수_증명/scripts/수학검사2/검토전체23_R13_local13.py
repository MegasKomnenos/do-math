# -*- coding: utf-8 -*-
# 장부 1.3: 「글자」 열의 괄호 밖 토큰(글자체 명령 + 글자, 로마체 이름)이 「자리」 열이 가리키는 장(본문+부록 D)에 실재하는지(후보).
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
def norm(t):
    t=re.sub(r"\\(mathsf|mathfrak|mathcal|mathrm|mathbb)\{([A-Za-z])\}", r"\\\1 \2", t)
    t=t.replace("\\prime","'")
    return t
chtext={}
for f in files+[a for a in appx if a.startswith("부록D")]:
    ch=chap_of_file[f]; chtext[ch]=chtext.get(ch,"")+"\n"+norm(rd(f))
J = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
s=next(i for i,l in enumerate(J) if l.startswith("### 1.3 ")); e=next(i for i,l in enumerate(J) if l.startswith("## 2. "))
TOK=re.compile(r"\\mathrm\{[A-Za-z]+\}|\\math(?:frak|sf|cal) [A-Za-z]|\\mathsf\{[A-Za-z]+\}|\\(?:hat|tilde|bar|widehat|widetilde)\{?\\math(?:rm|frak|cal)\{? ?[A-Za-z]+\}?\}?")
def strip_par(t):
    prev=None
    while prev!=t:
        prev=t
        t=re.sub(r"\([^()]*\)","",t)
    return t
n=0
for i in range(s,e):
    l=J[i]
    if not l.startswith("| ") or l.startswith("| 글자") or l.startswith("|---"): continue
    c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
    if len(c)<4: print("칸수",i+1,len(c)); continue
    n+=1
    place=c[2]
    chs=set(int(x) for x in re.findall(r"\{\{(\d+):",place))|set(int(x) for x in re.findall(r"(?<![\d.])(\d+)\.\d+",place))
    chs={x for x in chs if 1<=x<=9}
    if not chs: print("자리 장 못 읽음",i+1,place[:80]); continue
    cell=norm(c[0])
    # 수식만
    maths=re.findall(r"\$([^$]+)\$",cell)
    top=strip_par(cell)
    seen=set()
    for m in TOK.finditer(top):
        t=m.group(0)
        if t in seen: continue
        seen.add(t)
        if not any(t in chtext[ch] for ch in chs):
            where=[ch for ch in chtext if t in chtext[ch]]
            print(i+1,"장",sorted(chs),t,"| 다른 장:",where,"|",top[max(0,m.start()-50):m.end()+50])
print("행",n)
