# -*- coding: utf-8 -*-
# R11 검산: D.logconcavity-failure-n80 (마지막 차 재귀, 정확 정수)
import re, sys
from math import comb
from fractions import Fraction
N = 120
fails = []
B = {}
for l in range(0, N):
    A = [1]
    for n in range(1, N + 1):
        s = 0
        for j in range(n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j]
        A.append(s)
    B[l] = A
def b(n, l):
    return B[l][n] - (B[l - 1][n] if l >= 1 else 0)
for n in range(1, N + 1):
    assert sum(b(n, l) for l in range(n)) == (n + 1) ** (n - 1)
    assert B[n - 1][n] == (n + 1) ** (n - 1)
    for l in range(1, n - 1):
        if b(n, l) ** 2 < b(n, l - 1) * b(n, l + 1):
            fails.append((n, l))
print("first failures:", fails[:10], "count", len(fails))
print("rows failing <=120:", sorted(set(n for n, _ in fails))[:50])
txt = open(r"C:/math/임시/주차함수_증명/장v2/부록D_장3.md", encoding="utf-8").read()
ints = re.findall(r"b_\{80,(\d+)\}=(\d{50,})", txt)
for l, v in ints:
    print(l, int(v) == b(80, int(l)))
r1 = Fraction(b(80, 40), b(80, 39)); r2 = Fraction(b(80, 41), b(80, 40))
print(float(r1), float(r2), r1 < Fraction(25928, 25000) < r2)
print("%.12f %.12f" % (r1, r2))
