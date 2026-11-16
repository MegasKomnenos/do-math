# O10: 10장 항등식(보조정리 old-8-2, old-8-3(a)(d)(e), old-8-4, 명제 old-8-6, old-8-8)을 작은 k에서 정확 유리수로 검산
from fractions import Fraction as Fr
from math import comb
import sys

def build_A(nmax):
    # A[n][l] for 0<=n<=nmax, -1<=l<=nmax (store l+1 index)
    A = [[0]*(nmax+3) for _ in range(nmax+1)]
    for l in range(-1, nmax+2):
        A[0][l+1] = 1 if l >= 0 else 0  # A_{0,-1}=0? use 0 only for n>=1; A_{0,l}=1
    A[0][0] = 1  # treat A_{0,-1}=1 harmlessly? not used
    for l in range(0, nmax+2):
        for N in range(0, nmax):
            s = 0
            for i in range(0, N+1):
                s += comb(N, i) * min(i+1, l+1) * A[i][l+1] * A[N-i][l+1]
            A[N+1][l+1] = s
    return A

def get(A, n, l):
    if n == 0: return 1
    if l < 0: return 0
    return A[n][l+1]

def p(n): return (n+1)**(n-1) if n >= 1 else 1

nmax = 24
A = build_A(nmax)
# sanity
for n in range(1, nmax+1):
    assert get(A, n, n-1) == p(n), n
    assert get(A, n, 0) == __import__('math').factorial(n)
print("A_{n,l} sanity OK")

def check(k, n):
    nu = n - 2*k; N = n - k
    def Ak(m, l): return get(A, m, l)
    def b(m, l): return Ak(m, l) - Ak(m, l-1)
    def d(m): return b(m, k) - b(m, k-1)
    def s(m, y): return Fr(Ak(m, y-1), p(m))
    def c(m, Y): return Fr(b(m, Y), p(m))
    def vs(m, l): return s(m+1, l+1) - s(m, l)
    def P(j): return Fr(min(j, k) * comb(n-1, j-1) * Ak(j-1, k-1) * Ak(n-j, k-1), Ak(n, k-1))
    def clp(m): return Fr(b(m, k), Ak(m, k-1)) if m >= 1 else Fr(0)
    def clm(m): return Fr(b(m, k-1), Ak(m, k-1)) if m >= 1 else Fr(0)
    def mu(m): return Fr(d(m), Ak(m, k-1)) if m >= 1 else Fr(0)
    def chi(j):
        L, R = j-1, n-j
        lin = Fr(1, k) * (-(1 if j == k else 0) * (1 - clm(R)) + (1 if j > k else 0) * (clp(L)+clm(L)+clp(R)+clm(R)))
        quad = (1 + Fr(1 if j > k else 0, k)) * clp(L)*clp(R) + (1 - Fr(1 if j > k else 0, k)) * clm(L)*clm(R)
        return lin + quad
    src = sum(P(j)*chi(j) for j in range(1, n+1))
    inh = sum(P(j)*(mu(j-1)*(1 if k <= j-1 <= 2*k else 0) + mu(n-j)*(1 if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
    star = src + inh
    # old-6-21
    KDp = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m) for m in range(2*k+1, n))
    assert Ak(n, k-1)*star == d(n) - KDp, ("old-6-21", k, n)
    # 1/p ledger
    def w(m): return Fr(comb(n-1, m)*p(m)*Ak(n-1-m, k-1), Ak(n, k-1))
    def c2(m): return c(m, k) + c(m, k-1)
    def f(m):
        kap = Fr(2) if m <= N else 1 + Fr(n-m, k)
        return kap*k*Fr(d(m), p(m)) + (2 - (1 if m > N else 0))*c2(m)
    def fp(m): return (k+1)*c(m, k) - (k-1)*c(m, k-1)
    for m in range(k, 2*k+1):
        if m <= N: assert f(m) == 2*fp(m)
        else: assert f(m) == (k+n-m+1)*c(m, k) - (k+n-m-1)*c(m, k-1)
    u = w(N)*s(N, k+1)
    assert u == w(N)*Fr(Ak(N, k), p(N))
    Quad = sum(P(j)*((1+Fr(1, k))*clp(j-1)*clp(n-j) + (1-Fr(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
    Stem = Fr(1, k)*sum(P(j)*((clp(j-1)+clm(j-1))*(1 if j-1 > 2*k else 0) + (clp(n-j)+clm(n-j))*(1 if n-j > 2*k else 0)) for j in range(k+1, n+1))
    assert Stem == sum(w(m)*c2(m) for m in range(2*k+1, n)), ("Stem", k, n)
    assert star == sum(w(m)*f(m) for m in range(k, 2*k+1)) - u + Quad + Stem, ("old-8-2", k, n)
    # old-8-3 (a),(d),(e)
    def r(M): return Fr(Ak(M+1, k-1), (M+1)*Ak(M, k-1))
    def eg(m): return Fr((m+1)**(m-1), m**(m-1))  # e^{g(m)} = (1+1/m)^{m-1}
    for m in range(k, n-1):
        assert w(m+1)/w(m) == eg(m+1)/r(n-2-m), ("(a)", k, n, m)
    def Bor_ratio(mm, nn):  # Bor(mm)/Bor(nn) exact
        from math import factorial
        return Fr(mm**(mm-1)*factorial(nn), nn**(nn-1)*factorial(mm)) * Fr(1)  # ignore e^{-mm+nn}
    # (d): w_m/w_N = Bor(m+1)Bor(n-m)/(Bor(N+1)Bor(k)); e-factors: e^{-(m+1)-(n-m)} / e^{-(N+1)-k} = e^{-(n+1)}/e^{-(n+1)} = 1
    from math import factorial
    def BorNoE(mm): return Fr(mm**(mm-1), factorial(mm))
    for m in range(N, n):
        assert w(m)/w(N) == BorNoE(m+1)*BorNoE(n-m)/(BorNoE(N+1)*BorNoE(k)), ("(d)", k, n, m)
    # (e)
    for m in range(k, N+1):
        gL = Fr(1)
        for i in range(k, m):
            gL *= eg(i+1)/eg(n-1-i)
        assert w(m)/w(k) == gL*s(n-1-m, k)/s(N-1, k), ("(e)", k, n, m)
    assert u/w(k) == eg(N)/eg(k)*s(N, k+1)/s(N-1, k), ("(e)u", k, n)
    # old-8-4
    for l in [k-1, k]:
        for np_ in range(1, 2*k+2):
            lhs = sum(c(m, l) for m in range(np_, 2*k+1))
            rhs = s(np_, l+1) - s(2*k+1, l+1) + sum(vs(m, l) for m in range(np_, 2*k+1))
            assert lhs == rhs, ("old-8-4", k, l, np_)
    # old-8-6
    def T(m): return sum(f(i) for i in range(m, 2*k+1))
    assert sum(w(m)*f(m) for m in range(k, 2*k+1)) == w(k)*T(k) + sum((w(m)-w(m-1))*T(m) for m in range(k+1, 2*k+1))
    # 10.3 claim
    assert T(k+1) == T(k) + 2*(k-1)*c(k, k-1)
    assert f(k) == -2*(k-1)*c(k, k-1)
    # old-8-8
    if nu <= k-1 and k >= 3:
        def DD(m): return (k+1)*s(m+1, k+1) - 2*k*s(m, k) + (k-1)*s(m-1, k-1)
        for m in range(k+1, 2*k+1):
            assert DD(m) == (k+1)*vs(m, k) - (k-1)*vs(m-1, k-1)
        def om(m): return Fr(2) if m <= N+1 else 2 - Fr(m-N, k)
        Stays = 2*vs(N+1, k) + sum((2-Fr(m-N, k))*(vs(m, k)+vs(m-1, k-1)) for m in range(N+2, 2*k+1))
        BdS = -(k+nu)*(vs(2*k, k) + c(2*k, k-1)) - s(2*k, k-1)
        for m0 in range(k, N+1):
            rhs = 2*k*c(m0, k) + 2*s(m0, k+1) + 2*s(m0, k) + (2*k+2)*vs(m0, k) - 2*s(N+1, k+1) - s(N+2, k+1) + BdS + sum(om(m)*DD(m) for m in range(m0+1, 2*k+1)) - Stays
            assert T(m0) == rhs, ("old-8-8 (ga)", k, n, m0)
        for m0 in range(N+1, 2*k+1):
            mf = 3*k + nu - m0
            rhs = mf*c(m0, k) + s(m0, k) + (s(m0, k+1) - s(m0+1, k+1)) + (mf+1)*vs(m0, k) + BdS + sum(om(m)*DD(m) for m in range(m0+1, 2*k+1)) - sum((2-Fr(m-N, k))*(vs(m, k)+vs(m-1, k-1)) for m in range(m0+1, 2*k+1))
            assert T(m0) == rhs, ("old-8-8 (na)", k, n, m0)
        # 10.4 (2): varsigma_{2k}(k) <= c_{2k}(k)
        assert vs(2*k, k) <= c(2*k, k)
        # Stays <= Stays^vis uses 6:old-8-13 (y>=50) -- skip
    return True

cnt = 0
for k in range(2, 8):
    for n in range(2*k+1, 3*k+1):
        if n <= nmax:
            check(k, n); cnt += 1
print("checked (k,n) pairs:", cnt, "all identities OK")
