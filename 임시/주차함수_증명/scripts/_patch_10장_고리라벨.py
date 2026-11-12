# -*- coding: utf-8 -*-
"""10장 2차 대조 #19: 10.7 넷째·다섯째·여섯째 고리의 절 참조를 7장의 라벨로 바꾼다(7A·7B 회수 뒤 라벨 확정)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "장10.md")
s = io.open(P, encoding="utf-8").read()

REPL = [
    ("7.5절에서 보았듯 열 $2001\\le k\\le3130$의 $\\mathsf Q^\\star$는 대각선 접기와 극 영역의 갱신 인증서로 닫혀 있고, 두 열 범위를 합치면 7.5절의 명제 $\\mathsf Q^\\star$, 곧 모든 $k\\ge2001$에서의 판정이다.",
     "열 $2001\\le k\\le3130$의 $\\mathsf Q^\\star$는 정리 {{7:qstar-columns}}이고, 두 열 범위를 합치면 명제 $\\mathsf Q^\\star$, 곧 모든 $k\\ge2001$에서의 판정이다."),
    ("다섯째 고리는 $\\mathsf Q^\\star$ ⇒ $\\mathsf W_L^\\flat$이다. 명제 {{7:old-6-15}}에",
     "다섯째 고리는 $\\mathsf Q^\\star$ ⇒ $\\mathsf W_L^\\flat$, 곧 따름정리 {{7:qstar-implies-wlflat}}이다. 명제 {{7:old-6-15}}에"),
    ("이고, 7.5절 끝에서 보았듯 $\\mathsf W_L^\\flat$의 나머지 범위는 7.4절의 모멘트 인증, 정리 {{7:old-6-13}}, 정리 {{5:old-5-1}}, 7.3절의 극 영역(정리 {{7:old-6-12}})으로 닫혀 있다.",
     "이고, $\\mathsf W_L^\\flat$의 나머지 범위는 따름정리 {{7:qstar-implies-wlflat}}(가)가 닫는다."),
    ("7.2절의 $\\mathsf W_L^\\flat\\Leftrightarrow\\mathsf W_L$과 명제 {{7:old-6-9}}의",
     "따름정리 {{7:flat-threshold}}(라)의 $\\mathsf W_L^\\flat\\Leftrightarrow\\mathsf W_L$과 명제 {{7:old-6-9}}의"),
]
n = 0
for a, b in REPL:
    c = s.count(a)
    if c == 1:
        s = s.replace(a, b)
        n += 1
    elif b in s:
        print("이미 반영:", b[:40])
    else:
        print("찾지 못함(건수 %d):" % c, a[:60])
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("치환", n, "건")
