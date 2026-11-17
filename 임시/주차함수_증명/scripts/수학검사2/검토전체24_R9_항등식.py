# 검토전체24 R9: 9.1-9.3절 항등식의 정확 유리수 검산 (작은 k)
from fractions import Fraction as F
from math import comb
from functools import lru_cache
import sys

@lru_cache(None)
def A(m, l):
    if m == 0:
        return 1
    if l < 0:
        return 0
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))

def p(m): return F(m+1)**(m-1) if m >= 1 else F(1)
def b(m, l): return A(m, l) - A(m, l-1)
def s(m, y): return F(A(m, y-1)) / p(m)
def c(m, l): return F(b(m, l)) / p(m)
def sig(m, l): return s(m+1, l+1) - s(m, l)

def check(k, nu):
    n = 2*k+nu; N = k+nu
    Ank = A(n, k-1)
    def P(j): return F(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), Ank)
    def clp(m): return F(b(m, k), A(m, k-1))
    def clm(m): return F(b(m, k-1), A(m, k-1))
    def mu(m): return clp(m) - clm(m)
    def chi(j):
        lin = F(0)
        if j == k: lin -= (1 - clm(n-k))
        if j > k: lin += clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j)
        ind = 1 if j > k else 0
        return lin/k + (1+F(ind, k))*clp(j-1)*clp(n-j) + (1-F(ind, k))*clm(j-1)*clm(n-j)
    src = sum(P(j)*chi(j) for j in range(1, n+1))
    inh = sum(P(j)*((mu(j-1) if k <= j-1 <= 2*k else 0) + (mu(n-j) if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
    star = src + inh
    def w(m): return F(comb(n-1, m)*A(n-1-m, k-1)) * p(m) / Ank
    def c2(m): return c(m, k)+c(m, k-1)
    def dp(m): return c(m, k)-c(m, k-1)
    def f(m):
        if m <= N: return 2*((k+1)*c(m, k)-(k-1)*c(m, k-1))
        return (k+n-m+1)*c(m, k)-(k+n-m-1)*c(m, k-1)
    # 정의식과 경우식의 일치
    for m in range(k, 2*k+1):
        kap = F(2) if m <= N else 1+F(n-m, k)
        assert kap*k*dp(m) + (2-(1 if m > N else 0))*c2(m) == f(m)
    T = {2*k+1: F(0)}
    for m in range(2*k, k-1, -1): T[m] = T[m+1]+f(m)
    u = w(N)*s(N, k+1)
    Quad = sum(P(j)*((1+F(1, k))*clp(j-1)*clp(n-j)+(1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
    Stem = sum(P(j)*F(1, k)*(((clp(j-1)+clm(j-1)) if j-1 > 2*k else 0)+((clp(n-j)+clm(n-j)) if n-j > 2*k else 0)) for j in range(k+1, n+1))
    assert Stem == sum(w(m)*c2(m) for m in range(2*k+1, n))
    # 보조정리 9:old-8-2
    assert star == sum(w(m)*f(m) for m in range(k, 2*k+1)) - u + Quad + Stem, ("ledger", k, nu)
    # (7.14)
    KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*(b(m, k)-b(m, k-1)) for m in range(2*k+1, n))
    assert Ank*star == (b(n, k)-b(n, k-1)) - KD
    # 꼬리합 꼴
    assert sum(w(m)*f(m) for m in range(k, 2*k+1)) == w(k)*T[k]+sum((w(m)-w(m-1))*T[m] for m in range(k+1, 2*k+1))
    assert T[k+1] == T[k]+2*(k-1)*c(k, k-1)
    # 따름정리 9:old-8-3 (a)(c)(d) 등식
    def eg(x): return (1+F(1, x))**(x-1)
    for m in range(k, n-1):
        assert w(m+1)/w(m) == eg(m+1)/eg(n-1-m)*s(n-2-m, k)/s(n-1-m, k)
    def Borratio(m):  # Bor(m)e^m = m^{m-1}/m!
        from math import factorial
        return F(m**(m-1), factorial(m))
    for m in range(N, n):
        pi = Borratio(m+1)*Borratio(n-m)/Borratio(n+1)  # e 인자 상쇄: (m+1)+(n-m)-(n+1)=0
        assert w(m) == pi/(n*s(n, k))
    for m in range(k, N+1):
        gL = F(1)
        for i in range(k, m): gL *= eg(i+1)/eg(n-1-i)
        assert w(m)/w(k) == gL*s(n-1-m, k)/s(N-1, k)
    assert u/w(k) == eg(N)/eg(k)*s(N, k+1)/s(N-1, k)
    # Theta 관계
    Theta = comb(n, k)*F(k)**(k-2)*A(n-k, k-1)
    assert Theta == F(n, k)*Ank*u*F(A(N, k-1), A(N, k))
    assert Ank*Stem == sum(comb(n-1, m)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
    # 머묾 꼴 (k>=3, nu<=k-1)
    if k >= 3 and nu <= k-1:
        def DD(m): return (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
        assert all(DD(m) == (k+1)*sig(m, k)-(k-1)*sig(m-1, k-1) for m in range(k+1, 2*k+1))
        def om(m): return F(2) if m <= N+1 else 2-F(m-N, k)
        Stays = 2*sig(N+1, k)+sum((2-F(m-N, k))*(sig(m, k)+sig(m-1, k-1)) for m in range(N+2, 2*k+1))
        Bd = -(k+nu)*(sig(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
        for m0 in range(k, N+1):
            rhs = 2*k*c(m0, k)+2*s(m0, k+1)+2*s(m0, k)+(2*k+2)*sig(m0, k)-2*s(N+1, k+1)-s(N+2, k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-Stays
            assert T[m0] == rhs, ("stay-ga", k, nu, m0)
        for m0 in range(N+1, 2*k+1):
            mf = 3*k+nu-m0
            rhs = mf*c(m0, k)+s(m0, k)+(s(m0, k+1)-s(m0+1, k+1))+(mf+1)*sig(m0, k)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-sum((2-F(m-N, k))*(sig(m, k)+sig(m-1, k-1)) for m in range(m0+1, 2*k+1))
            assert T[m0] == rhs, ("stay-na", k, nu, m0)
        # 결손 좌표 Stays
        St2 = F(0)
        for d in range(nu+2, k+2):
            St2 += (F(2) if d == nu+2 else 2-F(d-nu-1, k))*sig(k+d-1, k)
        for d in range(nu+3, k+2):
            St2 += (2-F(d-nu-1, k))*sig(k-1+d-1, k-1)
        assert St2 == Stays
    # n=3k: T_m = 2 V_k(m)
    if nu == k:
        V = 0
        for m in range(2*k, k-1, -1):
            V += (k+1)*c(m, k)-(k-1)*c(m, k-1)
            assert T[m] == 2*V
    return True

cnt = 0
for k in range(2, 9):
    for nu in range(1, k+1):
        check(k, nu); cnt += 1
print("모든 항등식 통과; (k,nu) 쌍 수 =", cnt)
