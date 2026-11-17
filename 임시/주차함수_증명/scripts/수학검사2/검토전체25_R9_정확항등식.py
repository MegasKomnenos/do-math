# 검토전체25 R9: 9.1-9.3절의 정확 항등식을 작은 k에서 유리수로 검산
from fractions import Fraction as Fr
from math import comb
import sys

def build(k, nmax):
    # A[l][m]: 최대 변위 <= l 인 길이 m 주차함수의 수 (l = k-2, k-1, k)
    A = {}
    for l in (k-2, k-1, k):
        a = [1]
        for m in range(1, nmax+1):
            a.append(sum(comb(m-1, j-1)*min(j, l+1)*a[j-1]*a[m-j] for j in range(1, m+1)))
        A[l] = a
    return A

def p(m):
    return 1 if m == 0 else (m+1)**(m-1)

def run(k):
    nmax = 3*k+2
    A = build(k, nmax)
    for m in range(0, k-1):
        assert A[k-2][m] == p(m)
    Ak = lambda m: A[k][m]; Ak1 = lambda m: A[k-1][m]; Ak2 = lambda m: A[k-2][m]
    b_k = lambda m: Ak(m)-Ak1(m)
    b_k1 = lambda m: Ak1(m)-Ak2(m)
    d = lambda m: b_k(m)-b_k1(m)
    s = lambda m, y: Fr(A[y-1][m], p(m))      # y in {k-1,k,k+1}
    c = lambda m, l: s(m, l+1)-s(m, l)        # l in {k-1,k}
    clp = lambda m: Fr(b_k(m), Ak1(m)); clm = lambda m: Fr(b_k1(m), Ak1(m))
    mu = lambda m: Fr(d(m), Ak1(m))
    sig = lambda m, l: s(m+1, l+1)-s(m, l)
    for nu in range(1, k+1):
        n = 2*k+nu; N = k+nu
        P = lambda j: Fr(min(j, k)*comb(n-1, j-1)*Ak1(j-1)*Ak1(n-j), Ak1(n))
        assert sum(P(j) for j in range(1, n+1)) == 1
        def chi(j):
            hv = 1 if j > k else 0
            lin = Fr(1, k)*(-(1 if j == k else 0)*(1-clm(n-k)) + hv*(clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j)))
            return lin + (1+Fr(hv, k))*clp(j-1)*clp(n-j) + (1-Fr(hv, k))*clm(j-1)*clm(n-j)
        src = sum(P(j)*chi(j) for j in range(1, n+1))
        inh = sum(P(j)*((mu(j-1) if k <= j-1 <= 2*k else 0) + (mu(n-j) if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
        star = src+inh
        # (7.14)
        KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m) for m in range(2*k+1, n))
        assert Ak1(n)*star == d(n)-KD, ("7.14", k, nu)
        w = lambda m: Fr(comb(n-1, m)*p(m)*Ak1(n-1-m), Ak1(n))
        u = w(N)*s(N, k+1)
        Quad = sum(P(j)*((1+Fr(1, k))*clp(j-1)*clp(n-j)+(1-Fr(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
        Stem = sum(P(j)*Fr(1, k)*(((clp(j-1)+clm(j-1)) if j-1 > 2*k else 0)+((clp(n-j)+clm(n-j)) if n-j > 2*k else 0)) for j in range(k+1, n+1))
        c2 = lambda m: c(m, k)+c(m, k-1)
        assert Stem == sum(w(m)*c2(m) for m in range(2*k+1, n)), ("Stem", k, nu)
        def f(m):
            if m <= N:
                return 2*((k+1)*c(m, k)-(k-1)*c(m, k-1))
            return (k+n-m+1)*c(m, k)-(k+n-m-1)*c(m, k-1)
        # 정의식 (kappa)
        for m in range(k, 2*k+1):
            kap = 2 if m <= N else 1+Fr(n-m, k)
            assert f(m) == kap*k*Fr(d(m), p(m))+(2-(1 if m > N else 0))*c2(m)
        led = sum(w(m)*f(m) for m in range(k, 2*k+1))-u+Quad+Stem
        assert led == star, ("ledger", k, nu)
        T = {2*k+1: Fr(0)}
        for m in range(2*k, k-1, -1):
            T[m] = T[m+1]+f(m)
        assert sum(w(m)*f(m) for m in range(k, 2*k+1)) == w(k)*T[k]+sum((w(m)-w(m-1))*T[m] for m in range(k+1, 2*k+1))
        assert T[k+1] == T[k]+2*(k-1)*c(k, k-1)
        # 따름정리 (d): u/w_k = e^{g(N)-g(k)} s_N(k+1)/s_{N-1}(k);  e^{g(x)} = (1+1/x)^(x-1)
        eg = lambda x: Fr(x+1, x)**(x-1)
        assert u/w(k) == eg(N)/eg(k)*s(N, k+1)/s(N-1, k), ("d", k, nu)
        for m in range(k, n-1):
            assert w(m+1)/w(m) == eg(m+1)/eg(n-1-m)*s(n-2-m, k)/s(n-1-m, k)
        # Theta_n 과 Stem 하계 대수
        Theta = comb(n, k)*k**(k-2)*Ak1(n-k)
        assert Theta == Fr(n, k)*Ak1(n)*u*Fr(Ak1(N), Ak(N))
        BV = sum(comb(n, m+1)*p(n-1-m)*(b_k(m)+b_k1(m)) for m in range(2*k+1, n))
        assert Ak1(n)*Stem >= Fr(2*k+2, n)*BV
        # 머묾 꼴 (nu <= k-1, k>=3)
        if nu <= k-1 and k >= 3:
            DD = lambda m: (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
            for m in range(k+1, 2*k+1):
                assert DD(m) == (k+1)*sig(m, k)-(k-1)*sig(m-1, k-1)
            om = lambda m: Fr(2) if m <= N+1 else 2-Fr(m-N, k)
            Stays = 2*sig(N+1, k)+sum((2-Fr(m-N, k))*(sig(m, k)+sig(m-1, k-1)) for m in range(N+2, 2*k+1))
            Bd = -(k+nu)*(sig(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
            for m0 in range(k, N+1):
                rhs = 2*k*c(m0, k)+2*s(m0, k+1)+2*s(m0, k)+(2*k+2)*sig(m0, k)-2*s(N+1, k+1)-s(N+2, k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-Stays
                assert rhs == T[m0], ("S-ga", k, nu, m0)
            for m0 in range(N+1, 2*k+1):
                mf = 3*k+nu-m0
                rhs = mf*c(m0, k)+s(m0, k)+(s(m0, k+1)-s(m0+1, k+1))+(mf+1)*sig(m0, k)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-sum((2-Fr(m-N, k))*(sig(m, k)+sig(m-1, k-1)) for m in range(m0+1, 2*k+1))
                assert rhs == T[m0], ("S-na", k, nu, m0)
            # 결손 좌표의 Stays
            tot = Fr(0)
            for y, lo in ((k, nu+2), (k-1, nu+3)):
                for dd in range(lo, k+2):
                    wgt = Fr(2) if (y == k and dd == nu+2) else 2-Fr(dd-nu-1, k)
                    tot += wgt*sig(y+dd-1, y)
            assert tot == Stays, ("Stays-d", k, nu)
            # n=3k 꼴: N=2k 에서 T_m = 2 V_k(m)
        if nu == k:
            V = {2*k+1: Fr(0)}
            for m in range(2*k, k-1, -1):
                V[m] = V[m+1]+(k+1)*c(m, k)-(k-1)*c(m, k-1)
            assert all(T[m] == 2*V[m] for m in range(k, 2*k+1))
    return True

for k in range(3, 9):
    run(k)
    print("k=%d 통과" % k)
