# -*- coding: utf-8 -*-
"""표준 결과 Euler–Maclaurin 공식의 출처를 5B 본문·부록 D에 붙인다(결정 38: 표준 결과는 진술과 출처). 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "Graham–Knuth–Patashnik, *Concrete Mathematics*, 2nd ed., §9.5"

EDITS = [
    (os.path.join(ROOT, "장v2", "장5B.md"),
     "(Euler–Maclaurin 공식; 표준)",
     f"(Euler–Maclaurin 공식; {SRC})"),
    (os.path.join(ROOT, "장v2", "부록D_장5B.md"),
     "$\\mathsf z_{-1/2}$와 $\\mathsf z_{1/2}$: Euler–Maclaurin 공식",
     f"$\\mathsf z_{{-1/2}}$와 $\\mathsf z_{{1/2}}$: Euler–Maclaurin 공식({SRC})"),
]

for p, old, new in EDITS:
    s = io.open(p, encoding="utf-8").read()
    if new in s:
        print(os.path.basename(p), "이미 반영")
        continue
    n = s.count(old)
    if n != 1:
        print(os.path.basename(p), f"원문 {n}곳 — 건너뜀: {old[:60]}")
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print(os.path.basename(p), "출처 붙임")
