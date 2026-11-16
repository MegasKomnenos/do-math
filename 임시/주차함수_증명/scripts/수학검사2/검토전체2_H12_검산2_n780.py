# -*- coding: utf-8 -*-
"""H12 검산 2: 마지막 차 재귀로 n=779, 780의 열 573..580을 정확 정수로 계산해
누적 로그오목성의 위반 자리(ℓ=575..578)와 상대 크기를 다시 구한다 (부록 D.cumulative-logconcavity)."""
import sys, io, math, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
N = 780
t0 = time.time()
binom = [[math.comb(n, j) for j in range(n + 1)] for n in range(N)]
def column(l):
    A = [0] * (N + 1); A[0] = 1
    for n in range(1, N + 1):
        if n <= l + 1:
            A[n] = (n + 1) ** (n - 1); continue
        s = 0; B = binom[n - 1]
        for j in range(n):
            s += B[j] * min(j + 1, l + 1) * A[j] * A[n - 1 - j]
        A[n] = s
    return A
cols = {l: column(l) for l in range(574, 580)}
print("time", round(time.time() - t0, 1), "s")
for n in (779, 780):
    for l in range(575, 579):
        a0, a1, a2 = cols[l - 1][n], cols[l][n], cols[l + 1][n]
        diff = a1 * a1 - a0 * a2
        rel = diff / (a1 * a1)
        print(n, l, "sign", (diff > 0) - (diff < 0), "rel %.4e" % rel, "digits", len(str(a1)))
