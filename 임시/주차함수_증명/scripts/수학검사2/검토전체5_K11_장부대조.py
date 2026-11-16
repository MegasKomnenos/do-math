# -*- coding: utf-8 -*-
"""부록 A(기호표)·부록 C(용어·글자 대응)를 장부 1.2절·3절·7절과 행 단위로 견준다. 차이만 출력한다(판정은 읽어서)."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/"
L = open(root+"장부_v2.md", encoding="utf-8").read()
A = open(root+"장v2/부록A.md", encoding="utf-8").read()
C = open(root+"장v2/부록C.md", encoding="utf-8").read()
def rows(txt, start, end):
    seg = txt.split(start,1)[1]
    if end: seg = seg.split(end,1)[0]
    out=[]
    for l in seg.split("\n"):
        if l.startswith("| ") and not l.startswith("|---") :
            out.append([x.strip() for x in l.strip().strip("|").split(" | ")])
    return out
norm=lambda s: re.sub(r"\s+","",s)
# --- 7절 vs 부록 C 글자 표
L7 = rows(L, "## 7. 기록 글자 대응", "## 8.")
C3 = rows(C, "### 기록의 글자와 이 글의 글자", None)
d7 = {norm(r[0]):r for r in L7 if len(r)>=4}
print("## 7절 행", len(d7), "/ 부록 C 글자 행", len(C3))
for r in C3[1:]:
    if len(r)<4: print("  C 열 수 이상:", r[:1]); continue
    k=norm(r[0]); m=d7.get(k)
    if not m: print("  C에만:", r[0][:70]); continue
    if norm(m[1])!=norm(r[1]): print("  기록 열 다름:", r[0][:50], "| 장부:", m[1][:120], "| C:", r[1][:120])
    if norm(m[2])!=norm(r[2]): print("  기록 글자 다름:", r[0][:50], "| 장부:", m[2][:150], "| C:", r[2][:150])
    # 이동 열: 장부는 (확인)·Q·세션 주석이 붙으므로 글자 수 기준이 아니라 포함 관계로
    a=norm(re.sub(r"\((확인|Q\d+|세션[^)]*)\)|\(확인[^)]*\)","",m[3])); b=norm(r[3])
    if a!=b and b not in a and a not in b: print("  이동 열 다름:", r[0][:50], "| 장부:", m[3][:160], "| C:", r[3][:160])
for k in d7:
    if k not in {norm(r[0]) for r in C3}: print("  장부 7절에만:", d7[k][0][:70])
# --- 3절 vs 부록 C 낱말 표
L3 = rows(L, "## 3. 낱말 사전", "## 4.")
C1 = rows(C, "### 낱말: 이 글의 용어와 기록의 용어", "### 기록이 결과에")
d3 = {norm(r[0]):r for r in L3 if len(r)>=4}
print("\n## 3절 행", len(d3), "/ 부록 C 낱말 행", len(C1))
for r in C1[1:]:
    k=norm(r[0]); m=d3.get(k)
    if not m: print("  C에만:", r[0][:70]); continue
    if norm(m[3])!=norm(r[1]): print("  기록 용어 다름:", r[0][:40], "| 장부:", m[3][:150], "| C:", r[1][:150])
    if norm(m[2])!=norm(r[2]): print("  절 다름:", r[0][:40], "| 장부:", m[2], "| C:", r[2])
for k in d3:
    if k not in {norm(r[0]) for r in C1}: print("  장부 3절에만:", d3[k][0][:60], "|", d3[k][3][:60])
# --- 1.2절 vs 부록 A
L12 = rows(L, "### 1.2 전역 기호", "### 1.3")
L11 = rows(L, "### 1.1 변수", "### 1.2")
Arows = rows(A, "### 변수와 지표 글자", None)
dA = {}
for r in Arows:
    if len(r)>=4 and r[0]!="기호": dA[norm(r[0])]=r
print("\n## 장부 1.1+1.2 행", len(L11)+len(L12), "/ 부록 A 행", len(dA))
for r in L11+L12:
    if len(r)<3 or r[0] in ("기호","글자"): continue
    k=norm(r[0]); a=dA.get(k)
    if not a: print("  장부에만:", r[0][:60]); continue
    # 비교: 절 열 (장부 열 구조 확인용 출력 첫 행)
print("장부 1.2 첫 행 열 구조:", L12[0] if L12 else None)
print("부록 A에만:", [r[0][:50] for k,r in dA.items() if k not in {norm(x[0]) for x in L11+L12}][:40])
