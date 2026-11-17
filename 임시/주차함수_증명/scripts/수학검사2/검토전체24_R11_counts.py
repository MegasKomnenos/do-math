# -*- coding: utf-8 -*-
# R11 검산: D.exact-n20000, D.c50, D.band-A 의 개수
from math import ceil, isqrt
def ns(k): return -(-k * k // 4)
for a, b in ((121, 160), (161, 500)):
    d = sum(2 * ns(k) - 2 * k for k in range(a, b + 1)); r = sum(ns(k) + 1 for k in range(a, b + 1))
    print(a, b, "direct", d, "ratio", r)
print("k2..120:", sum(10000 - max(2 * k + 1, 12) + 1 for k in range(2, 121)))
print("rows 501..4999:", sum(10000 - 2 * k for k in range(501, 5000)))
print("(ㄴ):", sum((n + 1) // 2 - 1 for n in range(10001, 20001)))
print("(ㄹ):", sum((n - 3) - (-(-(n - 1) // 2)) + 1 for n in range(5, 20001)))
print("c50 positions:", sum((n - 3) - (-(-(n - 1) // 2)) + 1 for n in range(20001, 50001)), "pairs:", sum((n - 2) - (-(-(n - 1) // 2)) + 1 for n in range(20001, 50001)))
print("c20 pairs:", sum((n - 2) - (-(-(n - 1) // 2)) + 1 for n in range(5, 20001)))
# band A+ second piece rectangle count: s^-1 rows of width 1/4000 up to r>=966, x^{3/2} cols width 1/500 on [3/2,9/5], keep x_lo <= s0^3/20001 ?
from fractions import Fraction as F
import math
rows1 = math.ceil(F(1) / F(math.isqrt(833)) * 2000)  # rough
print("1/sqrt(833)*2000 =", 2000 / math.sqrt(833), " 1/sqrt(966)*4000 =", 4000 / math.sqrt(966), " 1/sqrt(598)*1000 =", 1000 / math.sqrt(598))
