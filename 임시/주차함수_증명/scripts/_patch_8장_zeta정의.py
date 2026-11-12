# -*- coding: utf-8 -*-
"""8장 8.2 머리 문단의 Riemann 제타 상수 정의 문장을 5.5의 정의를 가리키는 문장으로 바꾼다(결정 48: 정의 절 5.5; 정의는 한 번)."""
import io

p = r"C:\math\임시\주차함수_증명\장v2\장8.md"
s = io.open(p, encoding="utf-8").read()
a = "Riemann 제타 함수의 값은 $\\mathsf z_{1/2}:=\\zeta(\\tfrac12)$, $\\mathsf z_{-1/2}:=\\zeta(-\\tfrac12)$, $\\mathsf z_{3/2}:=\\zeta(\\tfrac32)$로 적는다(수치와 인증 구간은 부록 D)."
b = "Riemann 제타 함수의 세 값 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, $\\mathsf z_{3/2}$는 5.5절에서 정의한 명명 상수다."
print("count", s.count(a))
if s.count(a) == 1:
    s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("patched 장8.md")
