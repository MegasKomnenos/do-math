# -*- coding: utf-8 -*-
# 장부 5절: 「이 장이 처음 정의하는 전역 기호」를 1.2의 정의 절(가장 앞 절)의 장으로 다시 모아 견준다.
# 여유 글자: 1.2의 「쓰이는 장」·정의 절, 1.1 변수, 6절 예약으로 금지되는 (바탕 글자, 글자체)가 목록에 든 것을 찾는다(후보).
import re, json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
rows=json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_rows12.json"),encoding="utf-8"))
J = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
s = next(i for i,l in enumerate(J) if l.startswith("## 5. "))
e = next(i for i,l in enumerate(J) if l.startswith("## 6. "))
sec5={}
for i in range(s,e):
    l=J[i]
    m=re.match(r"^\| (\d+) \| ",l)
    if m:
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        sec5[int(m.group(1))]=(i+1,c)
def key(sx):
    a,b=sx.split("."); return (int(a),int(b))
bych=collections.defaultdict(list)
for r in rows:
    secs=re.findall(r"(?<![\d.])(\d+\.\d+)(?![\d.])",r["sec"])
    first=min(secs,key=key)
    bych[int(first.split(".")[0])].append(r["sym"].strip("$"))
for ch in sorted(sec5):
    ln,c=sec5[ch]
    listed=[x.strip().strip("$") for x in c[1].split(";")] if c[1]!="없음" else []
    exp=bych.get(ch,[])
    a=set(listed)-set(exp); b=set(exp)-set(listed)
    print("장",ch,"행",ln,"목록",len(listed),"1.2에서",len(exp),"| 목록에만:",sorted(a),"| 1.2에만:",sorted(b))
# 여유 글자 검사
def base_of(r):
    return r["base"]
used=collections.defaultdict(set)   # ch -> set of (base·style)
for r in rows:
    b=r["base"].split("(")[0].strip()
    b=re.sub(r"\s*이름$","",b)
    chs=set(int(x) for x in re.findall(r"\d+",r["chs"]))
    secs=re.findall(r"(?<![\d.])(\d+\.\d+)(?![\d.])",r["sec"])
    chs|=set(int(x.split(".")[0]) for x in secs)
    for ch in chs: used[ch].add(b)
    if 1 in set(int(x.split(".")[0]) for x in secs):
        for ch in range(1,11): used[ch].add(b)
STY={"라틴 소문자":"일반","라틴 대문자":"일반","그리스":"일반","필기체":"필기체","프락투어":"프락투어","산세리프":"산세리프"}
for ch in sorted(sec5):
    ln,c=sec5[ch]
    cell=c[3]
    for grp in re.split(r"\.\s+(?=라틴 소문자|라틴 대문자|그리스|필기체|프락투어|산세리프)",cell):
        m=re.match(r"(라틴 소문자|라틴 대문자|그리스|필기체|프락투어|산세리프)[^:]*:\s*(.*)",grp)
        if not m: continue
        sty=STY[m.group(1)]
        for sym in re.findall(r"\$([^$]+)\$",m.group(2)):
            letter=re.sub(r"\\(mathcal|mathfrak|mathsf)\s*","",sym).strip()
            keyb="%s·%s"%(letter,sty)
            if keyb in used[ch]:
                print("여유 목록에 든 금지 글자 후보: 장",ch,sym,"←",keyb)
print({ch:sorted(x for x in used[ch] if "산세리프" in x) for ch in (6,)})
