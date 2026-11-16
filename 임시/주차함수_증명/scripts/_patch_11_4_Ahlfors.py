# -*- coding: utf-8 -*-
"""11.4 문헌표에 Ahlfors 행 추가(4장이 Lagrange 계수의 윤곽 적분에 출처로 붙임), 1.3 4.3 묶음에 국소 글자 M 등록. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 11.4
p = os.path.join(ROOT, "장v2", "장11.md")
s = io.open(p, encoding="utf-8").read()
row = "| Ahlfors, *Complex Analysis*, 3판, McGraw-Hill, 1979 | Chapter 4 §2(Cauchy의 적분 공식과 적분 정리) | 4.3절(Lagrange 계수의 윤곽 적분 표현), 보조정리 {{4:correction-contour}} |"
anchor = "| Graham, Knuth, Patashnik, *Concrete Mathematics*, 2판, Addison-Wesley, 1994 |"
if "| Ahlfors, *Complex Analysis*" in s:
    print("11.4: 이미 있음")
else:
    i = s.index(anchor)
    j = s.index("\n", i)
    s = s[: j + 1] + row + "\n" + s[j + 1 :]
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("11.4: Ahlfors 행 추가")

# 1.3 4.3 묶음: 국소 글자 M (borel-tail-arc 증명)
q = os.path.join(ROOT, "장부_v2.md")
t = io.open(q, encoding="utf-8").read()
old = "$\\mathrm{Wi}_j$($j=0,1,2$; 두 보정의 수직선 적분"
new = "$\\mathfrak M=-\\tfrac32-\\tfrac12\\int_1^\\infty(\\{w\\}-\\tfrac12)w^{-3/2}dw$(보조정리 `{{4:borel-tail-arc}}` 증명의 Euler 합 공식 상수; 결정 38 후속), $\\mathrm{Wi}_j$($j=0,1,2$; 두 보정의 수직선 적분"
if "$\\mathfrak M=-\\tfrac32" in t:
    print("1.3: 이미 있음")
elif t.count(old) == 1:
    io.open(q, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
    print("1.3: M 등록")
else:
    print("1.3: 앵커 없음", t.count(old))
