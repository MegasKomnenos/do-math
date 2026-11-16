# -*- coding: utf-8 -*-
"""부록 A의 「처음 정의된 절」을 장부 1.2절의 「정의 절(둘째 판)」·「기록의 글자」와 견주고, 기호 문자열이 본문에서 처음 나오는 절도 함께 적는다."""
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/"
L = open(root+"장부_v2.md", encoding="utf-8").read()
A = open(root+"장v2/부록A.md", encoding="utf-8").read()
def rows(txt, start, end):
    seg = txt.split(start,1)[1]
    if end: seg = seg.split(end,1)[0]
    return [[x.strip() for x in l.strip().strip("|").split(" | ")] for l in seg.split("\n") if l.startswith("| ") and not l.startswith("|---")]
norm=lambda s: re.sub(r"\s+","",s)
L12 = rows(L, "### 1.2 전역 기호", "### 1.3"); L11 = rows(L, "### 1.1 변수", "### 1.2")
dL={norm(r[0]):r for r in L11+L12 if len(r)>=7}
Arows=[r for r in rows(A, "### 변수와 지표 글자", None) if len(r)>=4 and r[0]!="기호"]
# 본문 첫 출현 절
order=["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md"]
text=[]
for f in order:
    sec=None
    for l in open(root+"장v2/"+f,encoding="utf-8"):
        m=re.match(r"###+ (\d+\.\d+)",l)
        if m: sec=m.group(1)
        text.append((sec,l))
def first_sec(sym):
    # 기호 셀의 첫 LaTeX 토막
    m=re.search(r"\$([^$]+)\$", sym)
    if not m: return None
    key=m.group(1).split(",")[0].strip()
    key=re.sub(r":=.*$","",key).strip()
    for sec,l in text:
        if key in l: return sec
    return "(없음:"+key+")"
n=0
for r in Arows:
    k=norm(r[0]); m=dL.get(k)
    if not m: print("장부에 없음:", r[0][:60]); continue
    probs=[]
    if norm(m[3])!=norm(r[2]): probs.append(f"절: A「{r[2]}」 장부「{m[3]}」")
    if norm(m[6])!=norm(r[3]): probs.append(f"기록글자: A「{r[3][:80]}」 장부「{m[6][:80]}」")
    fs=first_sec(r[0])
    a_secs=re.findall(r"\d+\.\d+", r[2])
    if fs and a_secs and fs not in a_secs and not fs.startswith("(없음"): probs.append(f"본문 첫 출현 {fs} vs A {r[2]}")
    if probs: n+=1; print(r[0][:50], "::", " | ".join(probs))
print("차이 있는 행", n, "/", len(Arows))
