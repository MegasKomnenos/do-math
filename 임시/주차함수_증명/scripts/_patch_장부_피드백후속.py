# -*- coding: utf-8 -*-
"""작업 장부: 사용자 확인 질문(7A 부록 D 표 값 가족)에 대한 처리와 제타 글자 정리(결정 58)를 적는다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()
ENTRY = (
    "- 2026-11-13 03:4x 사용자 확인(「7A 부록 D의 표 값 가족도 처리됐나」): `_fix_피드백_기계.py` (바)로 $\\mathfrak K$·$\\mathrm{km}_j$ 가족 27곳을 $\\mathrm{pw}$ 가족으로 바꿨고, 괄호 꼴이 다른 변형 1곳($\\mathfrak K^{\\mathrm{L,U}}_j$)이 남아 있어 마저 바꿈 — 7A 부록 D에 프락투어 K 0, $\\mathrm{km}$은 8장의 전역 $\\mathrm{km}_N$ 8곳만 남음. "
    "제타 글자 정리: 7A 부록 D의 $\\zeta(3/2)$ 6곳 → $\\mathsf z_{3/2}$; 8장 8.2의 $\\mathsf z$ 중복 정의 문장 → 5.5 정의를 가리키는 문장(5B가 cumulant-bounds 앞에서 정의함을 확인); 5.2의 $\\zeta(2m)$·8.2의 $\\zeta(\\beta)$(Riemann 제타 함수의 함수 꼴)는 세션 결정 58로 셋째 예외(0절·6절 행; 1.2 $\\mathsf z$ 행 쓰이는 장 +7) — `_patch_장부_세션최종.py`(멱등; 설계 에이전트 재개 없이 세션이 사전에 직접 넣음)."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "사용자 확인(「7A 부록 D의 표 값 가족도 처리됐나」)" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md")
