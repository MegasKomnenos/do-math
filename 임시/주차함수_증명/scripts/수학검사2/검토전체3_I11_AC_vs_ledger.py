# -*- coding: utf-8 -*-
"""부록 A·C를 장부 1·3절과 맞춘다(자리 찾기용)."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT=r"C:\math\임시\주차함수_증명"
L=open(os.path.join(ROOT,"장부_v2.md"),encoding="utf-8").read()
A=open(os.path.join(ROOT,"장v2","부록A.md"),encoding="utf-8").read()
C=open(os.path.join(ROOT,"장v2","부록C.md"),encoding="utf-8").read()
def rows(txt, start, end=None):
    seg=txt.split(start,1)[1]
    if end: seg=seg.split(end,1)[0]
    out=[]
    for l in seg.splitlines():
        if l.startswith("|") and not l.startswith("|---") :
            c=[x.strip() for x in l.strip().strip("|").split(" | ")]
            out.append(c)
    return out[1:]  # drop header
# 장부 3절 vs 부록 C 낱말 표
L3=rows(L,"## 3. 낱말 사전","## 4.")
C1=rows(C,"### 낱말: 이 글의 용어와 기록의 용어","### 기록이 결과에 붙인 이름")
L3d={r[0]:r for r in L3 if len(r)>=4}
print("장부 3절 행:",len(L3),"부록 C 낱말 행:",len(C1))
for r in C1:
    if len(r)<3: print("!! C 행 꼴:",r); continue
    w,rec,sec=r
    if w not in L3d: print("C에 있으나 장부 3절에 없음:",w); continue
    lr=L3d[w]
    if lr[3]!=rec: print(f"기록 용어 다름 «{w}»:\n   C : {rec}\n   장부: {lr[3]}")
    if lr[2]!=sec: print(f"절 다름 «{w}»: C {sec} / 장부 {lr[2]}")
cw={r[0] for r in C1}
miss=[r[0] for r in L3 if r[0] not in cw]
print("장부 3절에 있으나 C에 없음:",len(miss)); print("   ",miss)
# 장부 1.1·1.2 vs 부록 A
L11=rows(L,"### 1.1 변수·지표 글자","### 1.2")
L12=rows(L,"### 1.2 전역 기호","### 1.3")
Arows=rows(A,"### 변수와 지표 글자")
Ad={r[0]:r for r in Arows if len(r)>=4}
print("\n장부 1.1 행:",len(L11),"1.2 행:",len(L12),"부록 A 행:",len(Arows))
for r in L11:
    if len(r)<2: continue
    if r[0] not in Ad: print("장부 1.1 글자가 A에 없음:",r[0]); continue
    a=Ad[r[0]]
    if a[1]!=r[1]: print(f"뜻 다름 «{r[0]}»:\n   A : {a[1]}\n   장부: {r[1]}")
for r in L12:
    if len(r)<7: continue
    sym,base,mean,sec,chs,first,rec=r[:7]
    if sym not in Ad: print("장부 1.2 글자가 A에 없음:",sym, "|", mean[:60]); continue
    a=Ad[sym]
    if a[1]!=mean: print(f"뜻 다름 «{sym}»:\n   A : {a[1]}\n   장부: {mean}")
    if a[2]!=sec: print(f"절 다름 «{sym}»: A {a[2]} / 장부 {sec}")
    if a[3]!=rec: print(f"기록 글자 다름 «{sym}»:\n   A : {a[3]}\n   장부: {rec}")
l12s={r[0] for r in L12}|{r[0] for r in L11}
print("A에 있으나 장부 1절에 없음:",[r[0] for r in Arows if r[0] not in l12s])
