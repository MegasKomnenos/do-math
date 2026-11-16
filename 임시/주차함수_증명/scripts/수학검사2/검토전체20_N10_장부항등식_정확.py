# 10.1-10.3절의 항등식(장부 항등식, 분할 무게, 꼬리합 꼴, 머묾 꼴, Stem/Theta 관계)을 작은 k에서 정확 유리수로 검산
from fractions import Fraction as F
from math import comb
import sys

def build(kmax, nmax):
    # A[m][l] for 0<=m<=nmax, 0<=l<=nmax
    A = [[F(0)]*(nmax+2) for _ in range(nmax+1)]
    for l in range(nmax+2):
        A[0][l] = F(1)
    for m in range(1, nmax+1):
        for l in range(nmax+2):
            s = F(0)
            for j in range(1, m+1):
                s += comb(m-1, j-1)*min(j, l+1)*A[j-1][l]*A[m-j][l]
            A[m][l] = s
    return A

def check(k, n, A, p):
    N = n-k; nu = n-2*k
    Ak = lambda m: A[m][k-1]          # A_{m,k-1}
    b = lambda m, l: A[m][l] - (A[m][l-1] if l>=1 else F(0))
    c = lambda m, l: b(m,l)/p[m]
    s = lambda m, l: (A[m][l-1] if l>=1 else F(0))/p[m]   # s_m(l)=A_{m,l-1}/p_m
    d = lambda m: b(m,k)-b(m,k-1)
    mu = lambda t: d(t)/Ak(t) if t>=0 else F(0)
    clp = lambda t: b(t,k)/Ak(t)
    clm = lambda t: b(t,k-1)/Ak(t)
    P = lambda j: F(min(j,k)*comb(n-1,j-1))*Ak(j-1)*Ak(n-j)/Ak(n)
    # (star)(n) from 7.5
    def chi(j):
        lin = F(0)
        if j==k: lin += -(1-clm(n-k))
        if j>k: lin += clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j)
        lin /= k
        q = (1+F(1 if j>k else 0, k))*clp(j-1)*clp(n-j) + (1-F(1 if j>k else 0, k))*clm(j-1)*clm(n-j)
        return lin+q
    src = sum(P(j)*chi(j) for j in range(1,n+1))
    inh = sum(P(j)*((mu(j-1) if k<=j-1<=2*k else 0)+(mu(n-j) if k<=n-j<=2*k else 0)) for j in range(1,n+1))
    star = src+inh
    # (7.25)
    KD = sum((k+n-m)*comb(n-1,m)*p[n-1-m]*d(m) for m in range(2*k+1, n))
    assert Ak(n)*star == d(n)-KD, ("7.25", k, n)
    # ledger
    w = lambda m: F(comb(n-1,m))*p[m]*Ak(n-1-m)/Ak(n)
    frak_p = lambda m: (k+1)*c(m,k)-(k-1)*c(m,k-1)
    def f(m):
        if m<=N: return 2*frak_p(m)
        return (k+n-m+1)*c(m,k)-(k+n-m-1)*c(m,k-1)
    T = lambda m: sum(f(i) for i in range(m, 2*k+1))
    u = w(N)*s(N,k+1)
    Quad = sum(P(j)*((1+F(1,k))*clp(j-1)*clp(n-j)+(1-F(1,k))*clm(j-1)*clm(n-j)) for j in range(k+1,n+1))
    Stem = sum(P(j)/k*((clp(j-1)+clm(j-1))*(1 if j-1>2*k else 0)+(clp(n-j)+clm(n-j))*(1 if n-j>2*k else 0)) for j in range(k+1,n+1))
    Stem2 = sum(w(m)*(c(m,k)+c(m,k-1)) for m in range(2*k+1, n))
    assert Stem==Stem2, ("Stem", k, n)
    assert star == sum(w(m)*f(m) for m in range(k,2*k+1)) - u + Quad + Stem, ("ledger", k, n)
    # Abel (old-8-6)
    assert sum(w(m)*f(m) for m in range(k,2*k+1)) == w(k)*T(k)+sum((w(m)-w(m-1))*T(m) for m in range(k+1,2*k+1)), ("abel",k,n)
    # old-8-3 (a),(d),(e)
    g = lambda x: None
    for m in range(k, n-1):
        r = Ak(n-1-m)/((n-1-m)*Ak(n-2-m))
        # e^{g(m+1)} = p_{m+1}/((m+1)p_m)
        assert w(m+1)/w(m) == (p[m+1]/((m+1)*p[m]))/r, ("a",k,n,m)
    for m in range(N, n):
        assert Ak(n-1-m)==p[n-1-m]
    for m in range(k, N+1):
        gL = F(1)
        for i in range(k, m):
            gL *= (p[i+1]/((i+1)*p[i]))/(p[n-1-i]/((n-1-i)*p[n-2-i]))
        assert w(m)/w(k) == gL*s(n-1-m,k)/s(N-1,k), ("e",k,n,m)
    eg = lambda x: p[x]/(x*p[x-1])  # e^{g(x)}
    assert u/w(k) == (eg(N)/eg(k))*s(N,k+1)/s(N-1,k), ("e-u",k,n)
    # old-8-4
    for l in (k-1,k,k+1):
        for n0 in range(1, 2*k+2):
            vs = lambda m: s(m+1,l+1)-s(m,l)
            assert sum(c(m,l) for m in range(n0,2*k+1)) == s(n0,l+1)-s(2*k+1,l+1)+sum(vs(m) for m in range(n0,2*k+1))
    # 머묾 꼴 (old-8-8), nu<=k-1
    if nu<=k-1 and k>=3:
        vs = lambda m,l: s(m+1,l+1)-s(m,l)
        DD = lambda m: (k+1)*s(m+1,k+1)-2*k*s(m,k)+(k-1)*s(m-1,k-1)
        for m in range(k+1, 2*k+1):
            assert DD(m) == (k+1)*vs(m,k)-(k-1)*vs(m-1,k-1)
        om = lambda m: F(2) if m<=N+1 else 2-F(m-N,k)
        Stays = 2*vs(N+1,k)+sum((2-F(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(N+2,2*k+1))
        Bd = -(k+nu)*(vs(2*k,k)+c(2*k,k-1))-s(2*k,k-1)
        for m0 in range(k, N+1):
            rhs = 2*k*c(m0,k)+2*s(m0,k+1)+2*s(m0,k)+(2*k+2)*vs(m0,k)-2*s(N+1,k+1)-s(N+2,k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-Stays
            assert T(m0)==rhs, ("S-ga",k,n,m0)
        for m0 in range(N+1, 2*k+1):
            mf = 3*k+nu-m0
            rhs = mf*c(m0,k)+s(m0,k)+(s(m0,k+1)-s(m0+1,k+1))+(mf+1)*vs(m0,k)+Bd+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-sum((2-F(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(m0+1,2*k+1))
            assert T(m0)==rhs, ("S-na",k,n,m0)
    # 10.3: Theta_n = (n/k) A_{n,k-1} u_n A_{N,k-1}/A_{N,k}; A_{n,k-1}Stem_n = sum_{m>2k} C(n-1,m)p_{n-1-m}b2_m; BV
    Theta = comb(n,k)*k**(k-2)*A[n-k][k-1]
    assert Theta == F(n,k)*Ak(n)*u*A[N][k-1]/A[N][k]
    assert Ak(n)*Stem == sum(comb(n-1,m)*p[n-1-m]*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
    BV = sum(comb(n,m+1)*p[n-1-m]*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
    assert Ak(n)*Stem >= F(2*k+2,n)*BV
    # 10.3 line 187
    assert f(k) == -2*(k-1)*c(k,k-1) and f(k)<=0
    # 10.4 (2): varsigma_{2k}(k) <= c_{2k}(k)
    assert s(2*k+1,k+1)-s(2*k,k) <= c(2*k,k)
    return True

kmax=7; nmax=3*kmax
A = build(kmax, nmax)
p = [F((m+1)**(m-1)) for m in range(nmax+1)]
for m in range(nmax+1):
    assert A[m][m] == p[m] and A[m][nmax+1]==p[m]
cnt=0
for k in range(2, kmax+1):
    for n in range(2*k+1, 3*k+1):
        check(k,n,A,p); cnt+=1
print("all identities verified exactly for", cnt, "pairs (k<=%d)"%kmax)
