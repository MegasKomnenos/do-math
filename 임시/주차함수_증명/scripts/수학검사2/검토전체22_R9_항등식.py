# 검토 22차 R9: 9.1절 장부 항등식(보조정리 old-8-2), 9.2절 머묾 꼴(명제 old-8-8), 따름정리 old-8-3(c)(d)를
# 작은 k에서 정확 유리수로 대조한다. A_{n,l}은 마지막 차 재귀(정리 2:old-2-6).
from fractions import Fraction as Fr
from math import comb, factorial
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)

@lru_cache(None)
def A(n, l):
    if l < 0: return 0 if n > 0 else 1
    if n == 0: return 1
    return sum(comb(n-1, j-1)*min(j, l+1)*A(j-1, l)*A(n-j, l) for j in range(1, n+1))
def p(n): return 1 if n == 0 else (n+1)**(n-1)
def b(n, l): return A(n, l)-A(n, l-1)
def s(m, y): return Fr(A(m, y-1), p(m))
def c(m, l): return Fr(b(m, l), p(m))
def stay(m, l): return s(m+1, l+1)-s(m, l)

bad = 0; cnt = 0
for k in range(2, 9):
    for nu in range(1, k+1):
        n = 2*k+nu; N = k+nu
        Ank = A(n, k-1)
        def P(j): return Fr(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), Ank)
        def clp(m): return Fr(b(m, k), A(m, k-1))
        def clm(m): return Fr(b(m, k-1), A(m, k-1))
        def mu(m): return clp(m)-clm(m)
        def chi(j):
            v = Fr(0)
            if j == k: v -= Fr(1, k)*(1-clm(n-k))
            if j > k: v += Fr(1, k)*(clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j))
            h = 1 if j > k else 0
            v += (1+Fr(h, k))*clp(j-1)*clp(n-j)+(1-Fr(h, k))*clm(j-1)*clm(n-j)
            return v
        src = sum(P(j)*chi(j) for j in range(1, n+1))
        inh = sum(P(j)*((mu(j-1) if k <= j-1 <= 2*k else 0)+(mu(n-j) if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
        star = src+inh
        def w(m): return Fr(comb(n-1, m)*p(m)*A(n-1-m, k-1), Ank)
        def f(m):
            if m <= N: return 2*((k+1)*c(m, k)-(k-1)*c(m, k-1))
            return (k+n-m+1)*c(m, k)-(k+n-m-1)*c(m, k-1)
        u = w(N)*s(N, k+1)
        Quad = sum(P(j)*((1+Fr(1, k))*clp(j-1)*clp(n-j)+(1-Fr(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
        Stem = sum(w(m)*(c(m, k)+c(m, k-1)) for m in range(2*k+1, n))
        rhs = sum(w(m)*f(m) for m in range(k, 2*k+1))-u+Quad+Stem
        cnt += 1
        if star != rhs: bad += 1; print("ledger mismatch", k, nu)
        # (7.14)
        KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*(b(m, k)-b(m, k-1)) for m in range(2*k+1, n))
        if Ank*star != (b(n, k)-b(n, k-1))-KD: bad += 1; print("7.14 mismatch", k, nu)
        # 머묾 꼴
        if k >= 3 and nu <= k-1:
            T = {2*k+1: Fr(0)}
            for m in range(2*k, k-1, -1): T[m] = T[m+1]+f(m)
            def om(m): return Fr(2) if m <= N+1 else 2-Fr(m-N, k)
            def DD(m): return (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
            Stays = 2*stay(N+1, k)+sum((2-Fr(m-N, k))*(stay(m, k)+stay(m-1, k-1)) for m in range(N+2, 2*k+1))
            BdS = -(k+nu)*(stay(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
            for m0 in range(k, 2*k+1):
                if m0 <= N:
                    r = 2*k*c(m0, k)+2*s(m0, k+1)+2*s(m0, k)+(2*k+2)*stay(m0, k)-2*s(N+1, k+1)-s(N+2, k+1)+BdS \
                        + sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-Stays
                else:
                    mf = 3*k+nu-m0
                    r = mf*c(m0, k)+s(m0, k)+(s(m0, k+1)-s(m0+1, k+1))+(mf+1)*stay(m0, k)+BdS \
                        + sum(om(m)*DD(m) for m in range(m0+1, 2*k+1)) \
                        - sum((2-Fr(m-N, k))*(stay(m, k)+stay(m-1, k-1)) for m in range(m0+1, 2*k+1))
                cnt += 1
                if r != T[m0]: bad += 1; print("stay-form mismatch", k, nu, m0)
        # (c): w_m = pi_n(m+1)/(n s_n(k)), N<=m<=n-1 ; pi_n(t)=C(n,t) t^{t-1} p_{n-t}/p_n
        for m in range(N, n):
            t = m+1
            pi = Fr(comb(n, t)*t**(t-1)*p(n-t), p(n))
            if w(m) != pi/(n*s(n, k)): bad += 1; print("(c) mismatch", k, nu, m)
print("cases", cnt, "mismatches", bad)
