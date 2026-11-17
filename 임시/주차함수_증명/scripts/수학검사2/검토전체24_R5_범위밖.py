# 검토전체24 R5: (6.26) 이 진술 범위 바로 밖 (m = 2d-2, 곧 열 k=w+1 의 행 m=2k) 에서 성립하는지 (참고)
from fractions import Fraction as Fr
from math import comb
NMAX = 90
cache = {}
def build(cap, nmax):
    A = [1]
    for N in range(nmax):
        A.append(sum(comb(N, i) * min(i + 1, cap) * A[i] * A[N - i] for i in range(N + 1)))
    return A
def A(n, l):
    if l < 0: return 0
    if l + 1 not in cache: cache[l + 1] = build(l + 1, NMAX)
    return cache[l + 1][n]
def p(n): return (n + 1) ** (n - 1)
def c(m, Y): return Fr(A(m, Y) - A(m, Y - 1), p(m))
for off in (2, 3, 4):
    res = []
    for d in range(3, 40):
        m = 2 * d - off
        w = m - d
        if w < 1: continue
        lhs = (w + 2) * (m + 1) * c(m + 1, w + 1); rhs = w * (m + 2) * c(m, w)
        res.append((d, m, float(lhs / rhs)))
    print("m=2d-%d:" % off, "min ratio", min(r for _, _, r in res), "첫 위반", next(((d, m) for d, m, r in res if r <= 1), None))
