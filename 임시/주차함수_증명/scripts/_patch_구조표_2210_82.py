# -*- coding: utf-8 -*-
"""구조표 v2: 2.10 제목 「다섯 몫 분해」, 8.2 셀에 Ψ^low_(ϱ)·𝗰_Ψ 정의 언급."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "구조표_v2.md")
s = io.open(P, encoding="utf-8").read()
n = s.count("다섯 조각 분해")
s = s.replace("다섯 조각 분해", "다섯 몫 분해")
lines = s.split("\n")
for i, ln in enumerate(lines):
    if ln.startswith("| 8.2 ") and "Psi^{\\mathrm{low}}_{(\\varrho)}" not in ln:
        cells = ln.split(" | ")
        cells[1] = cells[1] + "; 갱신함수의 칸 하계 $\\Psi^{\\mathrm{low}}_{(\\varrho)}$와 상수 $\\mathsf c_\\Psi$의 정의는 8.2 `{{8:explicit-bounds}}`에(봉투 보조정리 H가 먼저 쓴다; 정수판 $\\Psi^{\\mathrm{low}}(d)$는 9.5)"
        lines[i] = " | ".join(cells)
s = "\n".join(lines)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("다섯 조각 분해→다섯 몫 분해:", n, "| 8.2 갱신")
