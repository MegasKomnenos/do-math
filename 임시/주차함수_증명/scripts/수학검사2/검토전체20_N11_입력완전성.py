# -*- coding: utf-8 -*-
"""9장·10장과 정리 old-6-22의 증명이 직접 인용하는 앞 장의 진술이 11.3 세 표에 모두 있는지 본다."""
import re, io, os
ROOT = r"C:\math\임시\주차함수_증명"
OUT = os.path.join(ROOT, r"대조v2\수학검사2\_N11_입력완전성_out.txt")
LAB = re.compile(r"\{\{(\d+[AB]?):([^}]+)\}\}")
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?):([^}]+)\}\}(.*?)\*\*")
def cited_from(path, own_ch):
    out = {}
    cur = None
    for i, ln in enumerate(io.open(path, encoding="utf-8").read().split("\n")):
        h = HEAD.match(ln)
        if h and not h.group(4).strip().startswith("의 증명"):
            cur = h.group(1) + " " + h.group(3)
        for c, l in LAB.findall(ln):
            if c not in own_ch:
                out.setdefault((c, l), set()).add(cur or "(준비 문단)")
    return out
c9 = cited_from(os.path.join(ROOT, r"장v2\장9.md"), {"9"})
c10 = cited_from(os.path.join(ROOT, r"장v2\장10.md"), {"10"})
# 정리 old-6-22의 블록
lines = io.open(os.path.join(ROOT, r"장v2\장7B.md"), encoding="utf-8").read().split("\n")
blk, on = [], False
for ln in lines:
    h = HEAD.match(ln)
    if h:
        if h.group(3) == "old-6-22": on = True
        elif not h.group(4).strip().startswith("의 증명"): on = False
    if on: blk.append(ln)
c22 = {}
for c, l in LAB.findall("\n".join(blk)):
    c22.setdefault((c, l), set()).add("정리 old-6-22 블록")
# 11.3 표의 라벨 전부
t11 = io.open(os.path.join(ROOT, r"장v2\장11.md"), encoding="utf-8").read().split("\n")
in113, tbl = False, set()
for ln in t11:
    if ln.startswith("### 11.3"): in113 = True
    if ln.startswith("### 11.4"): in113 = False
    if in113 and ln.startswith("| "):
        tbl |= set(LAB.findall(ln))
o = io.open(OUT, "w", encoding="utf-8")
for name, c in [("9장", c9), ("10장", c10), ("old-6-22", c22)]:
    print("\n==", name, "이 인용하는 앞 장 진술 가운데 11.3 표에 없는 것:", file=o)
    for k in sorted(c):
        if k not in tbl and k[0] != "D":
            print("  ", k, sorted(c[k])[:6], file=o)
o.close()
