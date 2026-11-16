# -*- coding: utf-8 -*-
"""1.3절 표의 b_{n,l}, 증인, 1.4절의 d_{n,k_n} 부호, 2.2절의 n<=6 섬유 단봉성, 2.1절 h_i 공식을 다시 센다."""
import io, sys, itertools
from math import comb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def brute(n):
    """선호 수열 전수로 b_{n,l}을 센다 (n<=7)."""
    b = [0]*n
    for a in itertools.product(range(1, n+1), repeat=n):
        occ = [False]*(n+2); M = 0; ok = True
        for ai in a:
            p = ai
            while p <= n and occ[p]: p += 1
            if p > n: ok = False; break
            occ[p] = True; M = max(M, p-ai)
        if ok: b[M] += 1
    return b

def A_rec(N):
    """정리 2-6 재귀로 A_{n,l} (0<=n<=N, 0<=l<=N)."""
    A = [[0]*(N+1) for _ in range(N+1)]
    for l in range(N+1):
        A[0][l] = 1
        for n in range(1, N+1):
            A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A

N = 20
A = A_rec(N)
def row(n): return [A[n][l] - (A[n][l-1] if l else 0) for l in range(n)]
for n in range(1, 8):
    assert brute(n) == row(n), n
print("brute force n<=7 agrees with last-car recursion")
for n in range(1, 11):
    r = row(n); print(n, r, sum(r), (n+1)**(n-1))
    assert sum(r) == (n+1)**(n-1)
# witnesses
for n in range(1, 21):
    r = row(n)
    peak = r.index(max(r))
    uni = all(r[i] <= r[i+1] for i in range(peak)) and all(r[i] >= r[i+1] for i in range(peak, n-1))
    kn = -(-n//2)
    d = r[kn] - r[kn-1] if kn <= n-1 else None
    print(n, "unimodal", uni, "least witness", peak, "k_n", kn, "d_{n,k_n}", d)
# fiber unimodality n<=6 (Theorem 2-5 last sentence), h_i formula check
def h_of(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        js = [j for j in range(1, i) if sigma[j-1] > sigma[i-1]]
        h.append(i - (max(js) if js else 0))
    return h
for n in range(1, 8):
    bad = 0; tot_check = 0
    for sigma in itertools.permutations(range(1, n+1)):
        h = h_of(sigma)
        Al = [1]
        for l in range(n):
            pr = 1
            for hi in h: pr *= min(hi, l+1)
            Al.append(pr)
        bl = [Al[l+1]-Al[l] for l in range(n)]
        pk = bl.index(max(bl))
        uni = all(bl[i] <= bl[i+1] for i in range(pk)) and all(bl[i] >= bl[i+1] for i in range(pk, n-1))
        if not uni: bad += 1
        tot_check += Al[-1]
    print("n", n, "non-unimodal fibers", bad, "sum of fiber sizes", tot_check, "= p_n", (n+1)**(n-1))
