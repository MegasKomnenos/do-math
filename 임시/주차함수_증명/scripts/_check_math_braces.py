# -*- coding: utf-8 -*-
"""장 파일의 수식 구간($…$, $$…$$)마다 중괄호 균형을 검사해 불균형 구간을 보고한다(세션 점검)."""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md")))
MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)
bad = 0
for p in files:
    s = io.open(p, encoding="utf-8").read()
    for m in MATH.finditer(s):
        seg = m.group(1) or m.group(2)
        seg2 = seg.replace("\\{", "").replace("\\}", "")
        if seg2.count("{") != seg2.count("}"):
            bad += 1
            ln = s.count("\n", 0, m.start()) + 1
            print(f"{os.path.basename(p)}:{ln}: 불균형({seg2.count('{')}:{seg2.count('}')}) {seg[:120]!r}")
print("불균형 구간", bad)
