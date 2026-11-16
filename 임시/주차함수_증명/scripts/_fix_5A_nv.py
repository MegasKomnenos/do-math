# -*- coding: utf-8 -*-
"""정리 5.8 증명(장5A 188–200행)에서 변수 z를 사전의 현행 글자 nv로 바꾼다. 그 범위의 맨 z는 이 변수뿐이다(검토7 D 보고). 멱등.
사용: python scripts/_fix_5A_nv.py [--dry]"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "장5A.md")
DRY = "--dry" in sys.argv
LO, HI = 186, 202  # 1-based, inclusive; 여유를 두고 잡되 머리 줄은 아래에서 확인

s = io.open(P, encoding="utf-8").read()
lines = s.split("\n")
pat = re.compile(r"(?<![A-Za-z\\])z(?![A-Za-z])")
changed = 0
for i in range(LO - 1, HI):
    l = lines[i]
    if l.startswith("**") and "{{" in l and "증명" not in l:
        continue  # 진술 머리는 건드리지 않음(변수 z가 있으면 아래 출력으로 확인)
    new = re.sub(r"\\binom z(?=[0-9A-Za-z])", r"\\binom{\\mathrm{nv}}", l)
    new = pat.sub(r"\\mathrm{nv}", new)
    if new != l:
        n = len(pat.findall(l)) + len(re.findall(r"\\binom z(?=[0-9A-Za-z])", l))
        changed += n
        print(f"{i+1}: {n}곳")
        for m in re.finditer(r".{0,30}\\mathrm\{nv\}.{0,30}", new):
            print("    ", m.group())
        lines[i] = new
print("총", changed, "곳")
if DRY:
    print("(dry)")
else:
    io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("기록함")
