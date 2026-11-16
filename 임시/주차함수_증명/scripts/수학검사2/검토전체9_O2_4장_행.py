# O2 검산: 4장 작은 n 주장 (정리 4.5 (ㄴ), D:crossing-small-n, D:QL-small-n) 및 정리 3.5 n=780 일부
from math import comb
import sys, time

def A_table(nmax, lmax):
    A = [[0]*(lmax+1) for _ in range(nmax+1)]
    for l in range(lmax+1): A[0][l] = 1
    for n in range(1, nmax+1):
        for l in range(lmax+1):
            if l >= n-1: A[n][l] = (n+1)**(n-1)
            else:
                s = 0
                for j in range(n):
                    s += comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l]
                A[n][l] = s
    return A

A = A_table(80, 79)
rows = {n: [A[n][l] - (A[n][l-1] if l>=1 else 0) for l in range(n)] for n in range(1, 81)}
# 정리 4.5: d_{n,k_n}<0 for 2<=n<=15, >0 for n>=16; right half nonincreasing for 2<=n<=15
neg = [n for n in range(2, 81) if rows[n][-(-n//2)] - rows[n][-(-n//2)-1] < 0]
print("d_{n,k_n}<0 for n in:", neg)
for n in range(2, 16):
    kn = -(-n//2); r = rows[n]
    assert all(r[j] >= r[j+1] for j in range(kn, n-1)), n
print("right half nonincreasing for 2..15: OK")
# D:crossing-small-n: b_{n,k_n} < b_{n,k_n+1} true for 20<=n<=80, false for 5<=n<=19
cross = [n for n in range(5, 81) if rows[n][-(-n//2)] < rows[n][-(-n//2)+1]]
print("b_{n,k_n}<b_{n,k_n+1} holds for n in 5..80:", cross == list(range(20, 81)), "first:", cross[:3])
# D:QL-small-n: Q_L(n) for 3<=n<=15
for n in range(3, 16):
    r = rows[n]
    for l in range(0, n-2):
        if 2*l <= n-2 and r[l] > r[l+1]:
            assert r[l+1]**2 >= r[l]*r[l+2], (n, l)
print("Q_L(n) for 3..15: OK")
# 정리 4.8 reverse-direction check: increase level j in [k_n, n-2] exists for 20<=n<=80
for n in range(20, 81):
    kn = -(-n//2); r = rows[n]
    assert any(r[j] < r[j+1] for j in range(kn, n-1)), n
print("increase level in right half for 20..80: OK")
# 4.4 statement: for 5<=n<=19 false -> check which n in 1..19 have no increase level in right half
noinc = [n for n in range(1, 20) if not any(rows[n][j] < rows[n][j+1] for j in range(-(-n//2), n-1))]
print("n<=19 with no right-half increase level:", noinc)

# 정리 3.5 partial: A_{780,l} for l=573..580 and A_{779,l}; column-wise recursion
def column(l, mmax):
    col = [0]*(mmax+1); col[0] = 1
    for n in range(1, mmax+1):
        if l >= n-1: col[n] = (n+1)**(n-1); continue
        s = 0
        for j in range(n):
            s += comb(n-1, j)*min(j+1, l+1)*col[j]*col[n-1-j]
        col[n] = s
    return col
t0 = time.time()
cols = {l: column(l, 780) for l in range(573, 581)}
print("columns computed in %.1fs" % (time.time()-t0))
from fractions import Fraction
for n in (779, 780):
    for l in range(574, 580):
        num = cols[l][n]**2 - cols[l-1][n]*cols[l+1][n]
        rel = Fraction(num, cols[l][n]**2)
        print(n, l, "sign", (num > 0) - (num < 0), "rel %.4e" % float(rel))
