# -*- coding: utf-8 -*-
"""5A 94행: 평행이동 변수 a의 잔존 하나($\\mathcal Y(a)$)를 집필자가 쓴 $\\mathrm{sh}'$로 맞춘다(세션 예약 글자 검사)."""
import io
import os

P = r"C:\math\임시\주차함수_증명\장v2\장5A.md"
s = io.open(P, encoding="utf-8").read()
a = "상수항 $\\mathcal Y(a)\\le\\mathcal Y(0)<0$이다."
b = "상수항 $\\mathcal Y(\\mathrm{sh}')\\le\\mathcal Y(0)<0$이다."
print("count:", s.count(a))
if s.count(a) == 1:
    s = s.replace(a, b)
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("patched 장5A.md")
os.remove(r"C:\math\임시\주차함수_증명\scripts\_tmp_ctx_10_5A.py")
print("tmp removed")
