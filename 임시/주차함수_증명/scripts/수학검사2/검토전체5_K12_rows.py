# K12: exact rows via the last-car recursion (n<=120), checks for D.logconcavity-failure-n80,
# D.central-gap-integer (part ㄴ), D.QL-small-n, and the complement recursion of D.crossing-small-n (n<=300)
import time, math
from math import comb, factorial
NMAX = 120
p = [(n+1)**(n-1) if n > 0 else 1 for n in range(0, 1001)]

def columnA(l, N):
    A = [1]
    for n in range(1, N+1):
        if l >= n-1: A.append(p[n]); continue
        A.append(sum(comb(n-1, j)*min(j+1, l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A

t = time.time()
A = {l: columnA(l, NMAX) for l in range(0, NMAX)}
def b(n, l): return (A[l][n] if l >= 0 else 0) - (A[l-1][n] if l >= 1 else 0)
for n in range(1, NMAX+1):
    assert sum(b(n, l) for l in range(n)) == p[n] and A[0][n] == factorial(n)
fails = [(n, l) for n in range(1, NMAX+1) for l in range(1, n-1) if b(n, l)**2 < b(n, l-1)*b(n, l+1)]
print("first LC failure:", fails[0], "count n<=120:", len(fails), "; failures with n<=79:", [f for f in fails if f[0] <= 79])
B39, B40, B41 = b(80, 39), b(80, 40), b(80, 41)
print("b80,39 =", B39); print("b80,40 =", B40); print("b80,41 =", B41)
print("b39*b41-b40^2>0:", B39*B41-B40**2 > 0, " increasing:", B39 < B40 < B41)
print("ratios:", f"{B40/B39:.11f}", f"{B41/B40:.11f}", " separator 25928/25000 cross-products:", B40*25000 < 25928*B39, 25928*B40 < B41*25000)
neg = []
for n in range(2, 61):
    k = math.ceil(n/2); d = b(n, k)-b(n, k-1)
    if d < 0:
        neg.append(n); assert all(b(n, j) >= b(n, j+1) for j in range(k, n-1)), n
    else:
        assert d > 0, (n, d)
print("d_{n,k_n}<0 exactly for n in", neg)
for n in range(3, 16):
    for l in range(0, n-2):
        if 2*l <= n-2 and b(n, l) > b(n, l+1): assert b(n, l+1)**2 > b(n, l)*b(n, l+2), (n, l)
print("Q_L(n) strict for 3<=n<=15: ok")
def uni(z):
    i = 0
    while i+1 < len(z) and z[i] <= z[i+1]: i += 1
    while i+1 < len(z) and z[i] >= z[i+1]: i += 1
    return i+1 == len(z)
print("all rows n<=120 unimodal:", all(uni([b(n, l) for l in range(n)]) for n in range(1, NMAX+1)))
def leftstrict(n): return all(b(n, l) < b(n, l+1) for l in range(0, math.ceil(n/2)-1))
print("left strict increase b_{n,0}<...<b_{n,k_n-1} fails for n in", [n for n in range(2, NMAX+1) if not leftstrict(n)])
# complement recursion of D.crossing-small-n, valid for n<=2l+4
def Ac_col(l, N):
    Ac = [0]*(N+1)
    for n in range(l+2, N+1):
        s = sum(comb(n-1, j)*(j-l)*p[j]*p[n-1-j] for j in range(l+1, n))
        s += sum(Ac[i]*comb(n-1, i)*p[n-1-i]*((l+1)+min(n-i, l+1)) for i in range(l+2, n))
        Ac[n] = s
    return Ac
ok = True
for l in range(0, NMAX):
    Ac = Ac_col(l, min(NMAX, 2*l+4))
    for n in range(l+2, min(NMAX, 2*l+4)+1):
        if Ac[n] != p[n]-A[l][n]: ok = False; print("mismatch", l, n)
print("complement recursion matches exact A^c for n<=120, n<=2l+4:", ok)
N2 = 300
Ac = {l: Ac_col(l, min(N2, 2*l+4)) for l in range(0, N2)}
def bC(n, l): return (Ac[l-1][n] if l >= 1 else p[n]) - Ac[l][n]
bad = [n for n in range(5, N2+1) if not (bC(n, math.ceil(n/2)) < bC(n, math.ceil(n/2)+1))]
print("b_{n,k_n}<b_{n,k_n+1} false for n in", bad, "(5<=n<=300)")
print("time", round(time.time()-t, 1))
