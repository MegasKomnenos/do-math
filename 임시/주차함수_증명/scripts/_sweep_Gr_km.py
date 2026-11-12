# -*- coding: utf-8 -*-
"""세션 결정 54: 본문의 $T^{\\mathrm G}$를 사전의 $\\mathrm{Gr}$로, $\\mathfrak K^{\\mathrm U}$를 $\\mathrm{km}$로 바꾼다(장v2 전 파일; 멱등)."""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
total = {"Gr": 0, "km": 0}
for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))):
    s = io.open(p, encoding="utf-8").read()
    t, n1 = re.subn(r"T\^\{\\mathrm\s*\{?G\}?\}", r"\\mathrm{Gr}", s)
    t, n2 = re.subn(r"\\mathfrak K\^\{\\mathrm\s*\{?U\}?\}", r"\\mathrm{km}", t)
    if t != s:
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        print(os.path.basename(p), "Gr", n1, "km", n2)
        total["Gr"] += n1
        total["km"] += n2
print("총", total)
