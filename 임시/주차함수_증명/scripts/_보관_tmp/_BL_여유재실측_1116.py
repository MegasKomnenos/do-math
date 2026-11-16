# -*- coding: utf-8 -*-
"""BL(12차): 장부 5절 여유 글자 목록을 1.2 전역(쓰이는 장·정의 절)·1장 정의 기호·1.1 변수·6절 예약 글자와 (바탕 글자, 글자체)로 대조한다(읽기 전용). 2026-11-16."""
import io, re
L = io.open(r"C:\math\임시\주차함수_증명\장부_v2.md", encoding="utf-8").read().split("\n")


def cells(ln):
    return [c.strip() for c in ln.strip().strip("|").split(" | ")]


rows12 = [cells(l) for l in L[46:339] if l.startswith("| $")]
rows11 = [cells(l) for l in L[26:42] if l.startswith("| $")]
GREEK = ("alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|varkappa|lambda|mu|nu|xi|pi|rho|varrho|sigma|varsigma|tau|upsilon|phi|varphi|chi|psi|omega|"
         "Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega")
P1 = re.compile(r"\\(mathcal|mathfrak|mathsf|mathbb)[ ]*[{]?([A-Za-z]+)[}]?")
P2 = re.compile(r"\\(" + GREEK + r")(?![A-Za-z])")
P3 = re.compile(r"\\[A-Za-z]+([{][^{}]*[}])?")
P4 = re.compile(r"(?<![A-Za-z\\])([A-Za-z])(?![A-Za-z])")


def glyphs(s):
    out = set()
    for m in P1.finditer(s):
        f, b = m.group(1), m.group(2)
        out.add((f, b if f == "mathsf" else b[0]))
    for m in P2.finditer(s):
        out.add(("greek", m.group(1)))
    s2 = P3.sub("", s)
    for m in P4.finditer(s2):
        out.add(("it", m.group(1)))
    return out


chap = {c: set() for c in range(1, 12)}
for r in rows12:
    if len(r) < 5:
        continue
    g = glyphs(r[0]); defsec = r[3]; used = r[4]
    chs = set(range(1, 12)) if "전 장" in used else {int(m.group()) for m in re.finditer(r"\d+", used)}
    for m in re.finditer(r"(\d+)\.", defsec):
        chs.add(int(m.group(1)))
    if re.match(r"1\.", defsec):
        chs = set(range(1, 12))
    for c in chs:
        if c in chap:
            chap[c] |= g
vars11 = set()
for r in rows11:
    vars11 |= glyphs(r[0])
reserved = {("it", "a"), ("it", "b"), ("it", "c"), ("it", "e"), ("it", "h"), ("greek", "delta"), ("greek", "Delta"), ("greek", "Sigma"), ("it", "l"), ("it", "o"), ("it", "O")}
allgreek = {("greek", g) for g in GREEK.split("|")}
for ln in L[1197:1209]:
    c = cells(ln)
    if len(c) < 4 or not c[0].strip().isdigit():
        continue
    ch = int(c[0]); free = glyphs(c[3])
    bad = free & (chap[ch] | vars11 | reserved)
    miss = allgreek - chap[ch] - vars11 - reserved - free
    print("장", ch, "| 여유 목록 가운데 전역·변수·예약과 겹치는 것:", sorted(bad), "| 전역이 안 쓰는데 여유 목록에 없는 그리스:", sorted(miss))
