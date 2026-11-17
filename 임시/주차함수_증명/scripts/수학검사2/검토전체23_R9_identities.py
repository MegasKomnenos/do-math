# R9: exact check of 9.1-9.3 identities for small k (rational arithmetic)
from fractions import Fraction as F
from math import comb
from functools import lru_cache
import sys

@lru_cache(None)
def A(m, l):
    # number of parking functions of size m with max displacement <= l
    if l < 0:
        return 1 if m == 0 else 0
    if m == 0:
        return 1
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))

def p(m): return (m+1)**(m-1) if m >= 1 else 1
def b(m, l): return A(m, l) - A(m, l-1)
def s(m, y): return F(A(m, y-1), p(m))
def c(m, l): return F(b(m, l), p(m))
def stay(m, l): return s(m+1, l+1) - s(m, l)

def check(k):
    ok = True
    for n in range(2*k+1, 3*k+1):
        nu = n-2*k; N = k+nu
        An = A(n, k-1)
        def P(j): return F(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), An)
        def clp(m): return F(b(m, k), A(m, k-1))
        def clm(m): return F(b(m, k-1), A(m, k-1))
        def mu(m): return clp(m)-clm(m)
        def chi(j):
            h = 1 if j > k else 0
            lin = F(1, k)*(-(1 if j == k else 0)*(1-clm(n-k)) + h*(clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j)))
            return lin + (1+F(h, k))*clp(j-1)*clp(n-j) + (1-F(h, k))*clm(j-1)*clm(n-j)
        src = sum(P(j)*chi(j) for j in range(1, n+1))
        inh = sum(P(j)*((mu(j-1) if k <= j-1 <= 2*k else 0) + (mu(n-j) if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
        star = src+inh
        # 7.14
        KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*(b(m, k)-b(m, k-1)) for m in range(2*k+1, n))
        assert An*star == (b(n, k)-b(n, k-1)) - KD, ("7.14", k, n)
        def w(m): return F(comb(n-1, m)*p(m)*A(n-1-m, k-1), An)
        u = w(N)*s(N, k+1)
        Quad = sum(P(j)*((1+F(1, k))*clp(j-1)*clp(n-j)+(1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
        Stem = sum(P(j)*F(1, k)*(((clp(j-1)+clm(j-1)) if j-1 > 2*k else 0)+((clp(n-j)+clm(n-j)) if n-j > 2*k else 0)) for j in range(k+1, n+1))
        c2 = lambda m: c(m, k)+c(m, k-1)
        assert Stem == sum(w(m)*c2(m) for m in range(2*k+1, n)), ("Stem", k, n)
        def f(m):
            kap = 2 if m <= N else 1+F(n-m, k)
            v = kap*k*(c(m, k)-c(m, k-1)) + (2-(1 if m > N else 0))*c2(m)
            if m <= N:
                assert v == 2*((k+1)*c(m, k)-(k-1)*c(m, k-1))
            else:
                assert v == (k+n-m+1)*c(m, k)-(k+n-m-1)*c(m, k-1)
            return v
        lhs = sum(w(m)*f(m) for m in range(k, 2*k+1)) - u + Quad + Stem
        if lhs != star:
            ok = False; print("LEDGER FAIL", k, n)
        def T(m): return sum(f(i) for i in range(m, 2*k+1))
        # tail form
        assert sum(w(m)*f(m) for m in range(k, 2*k+1)) == w(k)*T(k)+sum((w(m)-w(m-1))*T(m) for m in range(k+1, 2*k+1))
        assert T(k+1) == T(k)+2*(k-1)*c(k, k-1)
        # monotone w on [k,2k] (needs k>=43 in text; just report)
        mono = all(w(m+1) >= w(m) for m in range(k, 2*k))
        # (c): w_m = pi_n(m+1)/(n s_n(k)), m>=N ; pi_n(t)=C(n,t) t^{t-1} p_{n-t}/p_n
        for m in range(N, n):
            t = m+1
            pi = F(comb(n, t)*t**(t-1)*p(n-t), p(n))
            assert w(m) == pi/(n*s(n, k)), ("c", k, n, m)
        # (d) last: u/w_k = e^{g(N)-g(k)} s_N(k+1)/s_{N-1}(k), e^{g(x)}=(1+1/x)^(x-1)
        eg = lambda x: F(x+1, x)**(x-1)
        assert u/w(k) == eg(N)/eg(k)*s(N, k+1)/s(N-1, k), ("d", k, n)
        # (a)
        for m in range(k, n-1):
            assert w(m+1)/w(m) == eg(m+1)/eg(n-1-m)*s(n-2-m, k)/s(n-1-m, k), ("a", k, n, m)
        # theta identity & Stem identity of thm 8-10
        Theta = comb(n, k)*k**(k-2)*A(n-k, k-1)
        assert Theta == F(n, k)*An*u*F(A(N, k-1), A(N, k)), ("Theta", k, n)
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
        assert An*Stem >= F(2*k+2, n)*BV
        # staying form 9:old-8-8
        if nu <= k-1 and k >= 3:
            DD = lambda m: (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
            assert all(DD(m) == (k+1)*stay(m, k)-(k-1)*stay(m-1, k-1) for m in range(k+1, 2*k+1))
            om = lambda m: 2 if m <= N+1 else 2-F(m-N, k)
            Stays = 2*stay(N+1, k)+sum((2-F(m-N, k))*(stay(m, k)+stay(m-1, k-1)) for m in range(N+2, 2*k+1))
            Bd = -(k+nu)*(stay(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
            for m0 in range(k, N+1):
                rhs = 2*k*c(m0, k)+2*s(m0, k+1)+2*s(m0, k)+(2*k+2)*stay(m0, k)-2*s(N+1, k+1)-s(N+2, k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-Stays
                if rhs != T(m0):
                    ok = False; print("STAY(ga) FAIL", k, n, m0, float(rhs-T(m0)))
            for m0 in range(N+1, 2*k+1):
                mf = 3*k+nu-m0
                rhs = mf*c(m0, k)+s(m0, k)+(s(m0, k+1)-s(m0+1, k+1))+(mf+1)*stay(m0, k)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-sum((2-F(m-N, k))*(stay(m, k)+stay(m-1, k-1)) for m in range(m0+1, 2*k+1))
                if rhs != T(m0):
                    ok = False; print("STAY(na) FAIL", k, n, m0, float(rhs-T(m0)))
        print(k, n, "ok" if ok else "FAIL", "w mono" if mono else "w NOT mono", "star>=0" if star >= 0 else "star<0")
    return ok

for k in range(2, 9):
    check(k)
