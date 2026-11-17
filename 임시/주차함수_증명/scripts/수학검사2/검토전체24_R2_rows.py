# R2 검산: 행 b_{n,l} (마지막 차 재귀), 로그오목성 n<=80, 중앙 틈 부호, 증인
import sys
from math import comb
NMAX = 130
def rows(NMAX):
    # A[l][n]
    out = {}
    binom = [[comb(n, j) for j in range(n+1)] for n in range(NMAX+1)]
    Acols = []
    for l in range(NMAX):
        A = [1]
        for n in range(1, NMAX+1):
            s = 0
            bn = binom[n-1]
            for j in range(n):
                s += bn[j]*min(j+1, l+1)*A[j]*A[n-1-j]
            A.append(s)
        Acols.append(A)
    b = {}
    for n in range(1, NMAX+1):
        row = []
        for l in range(n):
            row.append(Acols[l][n] - (Acols[l-1][n] if l > 0 else 0))
        assert sum(row) == (n+1)**(n-1), n
        b[n] = row
    return b
b = rows(NMAX)
print("n<=10 rows match table?", b[3], b[4], b[10][:3])
# witnesses
for n in range(1, 11):
    m = max(b[n]); w = [i for i, v in enumerate(b[n]) if v == m]
    print(n, "witness", w, "ceil(n/2)=", -(-n//2))
# log-concavity
fails = []
for n in range(1, NMAX+1):
    r = b[n]
    for l in range(1, n-1):
        if r[l]**2 < r[l-1]*r[l+1]:
            fails.append((n, l))
print("first lc failures:", fails[:10], "count<=", NMAX, len(fails))
print("fails n<=80:", [f for f in fails if f[0] <= 80])
r = b[80]
print("b80,39<b80,40<b80,41:", r[39] < r[40] < r[41])
print("b80_39 ends", str(r[39])[:12], str(r[39])[-6:], "b80_40", str(r[40])[:12], str(r[40])[-6:], "b80_41", str(r[41])[:12], str(r[41])[-6:])
# central gap
for n in range(1, NMAX+1):
    kn = -(-n//2)
    if kn <= n-1:
        d = b[n][kn] - b[n][kn-1]
        if n <= 20 or d <= 0:
            tail = all(b[n][j] >= b[n][j+1] for j in range(kn, n-1))
            print("n", n, "kn", kn, "sign d", (d > 0) - (d < 0), "tail nonincr from kn:", tail)
# unimodality check all rows
for n in range(1, NMAX+1):
    r = b[n]; m = r.index(max(r))
    ok = all(r[i] <= r[i+1] for i in range(m)) and all(r[i] >= r[i+1] for i in range(m, n-1))
    if not ok: print("NOT unimodal", n)
print("done")
