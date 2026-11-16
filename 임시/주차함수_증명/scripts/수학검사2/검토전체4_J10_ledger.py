# J10: 보조정리 old-8-2(장부 항등식)와 명제 old-8-8(머묾 꼴)을 작은 k에서 정확 유리수로 검산
from fractions import Fraction as F
from math import comb
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)

@lru_cache(None)
def A(n, l):
    # 마지막 차 재귀 (정리 2:old-2-6): A_{n,l} = sum_j C(n-1,j-1) min(j,l+1) A_{j-1,l} A_{n-j,l}
    if l < 0:
        return 0
    if n == 0:
        return 1
    return sum(comb(n-1, j-1)*min(j, l+1)*A(j-1, l)*A(n-j, l) for j in range(1, n+1))

def p(n):
    return (n+1)**(n-1) if n >= 1 else 1

def check(k, n):
    nu = n-2*k; N = n-k
    b = lambda m, l: A(m, l)-A(m, l-1)
    c = lambda m, l: F(b(m, l), p(m))
    s = lambda m, l: F(A(m, l-1), p(m))     # s_m(l) = A_{m,l-1}/p_m
    d = lambda m: b(m, k)-b(m, k-1)
    mu = lambda m: F(d(m), A(m, k-1))
    clp = lambda m: F(b(m, k), A(m, k-1))
    clm = lambda m: F(b(m, k-1), A(m, k-1))
    P = lambda j: F(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), A(n, k-1))
    # 7.5 정의
    def chi(j):
        L, R = j-1, n-j
        lin = F(0)
        if j == k: lin -= (1-clm(R))
        if j > k: lin += clp(L)+clm(L)+clp(R)+clm(R)
        lin /= k
        ind = 1 if j > k else 0
        return lin + (1+F(ind, k))*clp(L)*clp(R) + (1-F(ind, k))*clm(L)*clm(R)
    src = sum(P(j)*chi(j) for j in range(1, n+1))
    inh = sum(P(j)*((mu(j-1) if k <= j-1 <= 2*k else 0)+(mu(n-j) if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
    star = src+inh
    # 10.1 장부
    w = lambda m: F(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
    c2 = lambda m: c(m, k)+c(m, k-1)
    def f(m):
        if m <= N: return 2*((k+1)*c(m, k)-(k-1)*c(m, k-1))
        return (k+n-m+1)*c(m, k)-(k+n-m-1)*c(m, k-1)
    u = w(N)*s(N, k+1)
    Quad = sum(P(j)*((1+F(1, k))*clp(j-1)*clp(n-j)+(1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
    Stem = sum(w(m)*c2(m) for m in range(2*k+1, n))
    ledger = sum(w(m)*f(m) for m in range(k, 2*k+1)) - u + Quad + Stem
    ok1 = (star == ledger)
    # 7.25: A_{n,k-1} star = d_n - KD'_n
    KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m) for m in range(2*k+1, n))
    ok2 = (A(n, k-1)*star == d(n)-KD)
    # 10.2 머묾 꼴 (nu <= k-1)
    T = lambda m0: sum(f(i) for i in range(m0, 2*k+1))
    vs = lambda m, l: s(m+1, l+1)-s(m, l)
    DD = lambda m: (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
    om = lambda m: F(2) if m <= N+1 else 2-F(m-N, k)
    ok3 = True
    if nu <= k-1:
        Stays = 2*vs(N+1, k)+sum((2-F(m-N, k))*(vs(m, k)+vs(m-1, k-1)) for m in range(N+2, 2*k+1))
        BdS = -(k+nu)*(vs(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
        for m0 in range(k, N+1):
            rhs = 2*k*c(m0, k)+2*s(m0, k+1)+2*s(m0, k)+(2*k+2)*vs(m0, k)-2*s(N+1, k+1)-s(N+2, k+1)+BdS+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-Stays
            if rhs != T(m0): ok3 = False; print("  (가) fail", k, n, m0)
        for m0 in range(N+1, 2*k+1):
            mf = 3*k+nu-m0
            rhs = mf*c(m0, k)+s(m0, k)+(s(m0, k+1)-s(m0+1, k+1))+(mf+1)*vs(m0, k)+BdS+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-sum((2-F(m-N, k))*(vs(m, k)+vs(m-1, k-1)) for m in range(m0+1, 2*k+1))
            if rhs != T(m0): ok3 = False; print("  (나) fail", k, n, m0)
    # 보조정리 old-8-3 (a),(d),(e) 수치 검사
    import math
    g = lambda x: (x-1)*math.log(1+1/x)
    r = lambda M: F(A(M+1, k-1), (M+1)*A(M, k-1))
    oka = all(abs(float(w(m+1)/w(m)) - math.exp(g(m+1))/float(r(n-2-m))) < 1e-12 for m in range(k, n-1))
    Bor = lambda j: math.exp(-j)*j**(j-1)/math.factorial(j)
    okd = all(abs(float(w(m)/w(N)) - Bor(m+1)*Bor(n-m)/(Bor(N+1)*Bor(k))) < 1e-9 for m in range(N, n))
    oke = abs(float(u/w(k)) - math.exp(g(N)-g(k))*float(s(N, k+1)/s(N-1, k))) < 1e-12
    okc = all(w(m+1) >= w(m) for m in range(k, 2*k))
    return ok1, ok2, ok3, oka, okd, oke, okc

for k in range(3, 9):
    for n in range(2*k+1, 3*k+1):
        res = check(k, n)
        if not all(res): print("FAIL", k, n, res)
print("done")
