# -*- coding: utf-8 -*-
"""7A 부록 D의 Riemann 제타 값 ζ(3/2)를 장부의 명명 상수 𝗓_{3/2}로 바꾼다(세션 결정 34·48)."""
import io

p = r"C:\math\임시\주차함수_증명\장v2\부록D_장7A.md"
s = io.open(p, encoding="utf-8").read()
n = s.count("\\zeta(3/2)")
s = s.replace("\\zeta(3/2)", "\\mathsf z_{3/2}")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("replaced", n, "| remaining zeta(:", s.count("\\zeta("))
