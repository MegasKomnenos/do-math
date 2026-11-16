# -*- coding: utf-8 -*-
# 10차 독립 검토 P2: 정리 3.5 의 n=780 네 위반과 n=779 성립(열 573..580만) 재계산
from math import comb
import sys
def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1
NMAX = 780
binom = [[comb(n, j) for j in range(n + 1)] for n in range(NMAX)]
def column(l):
    Acol = [0] * (NMAX + 1)
    Acol[0] = 1
    for n in range(1, NMAX + 1):
        if l >= n - 1:
            Acol[n] = p(n)
        else:
            s = 0
            B = binom[n - 1]
            m = l + 1
            for j in range(n):
                s += B[j] * min(j + 1, m) * Acol[j] * Acol[n - 1 - j]
            Acol[n] = s
    return Acol
cols = {}
for l in range(573, 581):
    cols[l] = column(l)
    sys.stdout.write("col %d done\n" % l); sys.stdout.flush()
for n in (779, 780):
    for l in range(574, 580):
        if l + 1 > 580 or l - 1 < 573:
            continue
        a, am, ap = cols[l][n], cols[l - 1][n], cols[l + 1][n]
        diff = a * a - am * ap
        rel = diff / (a * a)
        print(n, l, "sign", (diff > 0) - (diff < 0), "rel", "%.4e" % rel)
