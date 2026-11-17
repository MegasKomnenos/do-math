# -*- coding: utf-8 -*-
# 의존지도 1절 「본문 인용」: 본문을 「머리 다음 줄부터 다음 진술 머리 전까지(절 머리를 넘어)」로 잡고, 뒤로 미룬 증명 단락
# (「…의 증명.」 머리)의 인용은 그 진술에 붙여 다시 센다. 표와 같은지 본다.
import re, json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
LAB = re.compile(r"\{\{(\d+:[A-Za-z0-9\-]+)\}\}")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+:[A-Za-z0-9\-]+)\}\}")
DEF = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{(\d+:[A-Za-z0-9\-]+)\}\}의 증명\.\*\*")
body = collections.defaultdict(set); headcite = {}
for f in files:
    cur = None; curdef = None
    for line in lines(f):
        m = HEAD.match(line)
        d = DEF.match(line)
        if m and not d:
            cur = m.group(2); curdef = None
            headcite[cur] = set(x for x in LAB.findall(line) if x != cur)
            continue
        if d:
            curdef = d.group(1)
        if line.strip() == "" and curdef:
            pass
        tgt = curdef or cur
        if tgt:
            for x in LAB.findall(line):
                if x != tgt: body[tgt].add(x)
        if curdef and line.strip().endswith("∎"): curdef = None
L = open(os.path.join(base, "의존지도_v2.md"), encoding="utf-8").read().split("\n")
s1 = next(i for i, l in enumerate(L) if l.startswith("## 1. ")); s11 = next(i for i, l in enumerate(L) if l.startswith("### 1.1 "))
nd = 0
for i in range(s1, s11):
    l = L[i]
    if not l.startswith("| `{{"): continue
    c = [x.strip() for x in l.strip()[1:-1].split(" | ")]
    lab = c[0].strip("`")[2:-2]
    tall = set(LAB.findall(c[5]))
    mine = headcite.get(lab, set()) | body.get(lab, set())
    if tall != mine:
        nd += 1
        print(i + 1, lab, "표에만:", sorted(tall - mine), "글에만:", sorted(mine - tall))
print("다른 행", nd)
