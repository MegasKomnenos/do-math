# 7.6-7.7절 항등식·부등식의 정확 유리수 검산 (작은 k)
from fractions import Fraction as Fr
from math import comb, log, exp, sqrt, pi, factorial
import sys

def build_A(maxn, lmax):
    # A[l][m] for -1<=l<=lmax, 0<=m<=maxn ; A_{m,-1}=0 (m>=1), A_{0,l}=1
    A = {}
    for l in range(-1, lmax+1):
        row = [0]*(maxn+1)
        row[0] = 1
        for m in range(1, maxn+1):
            if l == -1:
                row[m] = 0; continue
            s = 0
            for j in range(1, m+1):
                s += comb(m-1, j-1)*min(j, l+1)*row[j-1]*row[m-j]
            row[m] = s
        A[l] = row
    return A

def p(m): return (m+1)**(m-1) if m>=1 else 1

def check(k, nmax):
    A = build_A(nmax, k)
    def Aa(m,l):
        if l < -1: return 0
        return A[l][m]
    def s(m,y):  # s_m(y)=A_{m,y-1}/p_m
        return Fr(Aa(m,y-1), p(m))
    def c(m,Y):  # c_m(Y)=b_{m,Y}/p_m
        return Fr(Aa(m,Y)-Aa(m,Y-1), p(m))
    def P(n,j):  # P_n(j)
        return Fr(j*comb(n-1,j-1)*p(j-1)*p(n-j), p(n))
    def Pk(n,j):
        return Fr(min(j,k)*comb(n-1,j-1)*Aa(j-1,k-1)*Aa(n-j,k-1), Aa(n,k-1))
    def clp(m): return c(m,k)/s(m,k)
    def clm(m): return c(m,k-1)/s(m,k)
    def mu(m): return clp(m)-clm(m)
    def chi(n,j):
        v = Fr(0)
        if j==k: v += -Fr(1,k)*(1-clm(n-k))
        if j>k: v += Fr(1,k)*(clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j))
        ind = 1 if j>k else 0
        v += (1+Fr(ind,k))*clp(j-1)*clp(n-j) + (1-Fr(ind,k))*clm(j-1)*clm(n-j)
        return v
    def src(n): return sum(Pk(n,j)*chi(n,j) for j in range(1,n+1))
    def inh(n):
        return sum(Pk(n,j)*(mu(j-1)*(1 if k<=j-1<=2*k else 0)+mu(n-j)*(1 if k<=n-j<=2*k else 0)) for j in range(1,n+1))
    def inhlin(n):
        return Fr(1,k)*sum(Pk(n,j)*((clp(j-1)+clm(j-1))*(1 if k<=j-1<=2*k else 0)+(clp(n-j)+clm(n-j))*(1 if k<=n-j<=2*k else 0)) for j in range(1,n+1))
    def rw(n,q): return Fr(k,k+1+q)*P(n,k+1+q)/P(n,k)
    def d(n): return Aa(n,k)-2*Aa(n,k-1)+Aa(n,k-2)
    ok = True
    def rep(name, cond, info=""):
        nonlocal ok
        if not cond:
            ok = False; print("FAIL", k, name, info)
    for n in range(2*k+1, nmax+1):
        nu = n-2*k
        # P^(k) formula via s
        for j in range(1,n+1):
            rep("Pk-formula", Pk(n,j)==Fr(min(j,k),j)*P(n,j)*s(j-1,k)*s(n-j,k)/s(n,k), (n,j))
        # root-symmetry
        rep("rw(nu)=1", rw(n,nu)==1, n)
        for q in range(0, k+nu-1):
            lhs = rw(n,q+1)/rw(n,q)
            j = k+1+q
            rhs = Fr((j+1)**(j-1), j**(j-1))*Fr((n-j)**(n-j-1), (n-j+1)**(n-j-1))
            rep("rw-ratio", lhs==rhs, (n,q))
        for q in range(nu, k+nu):
            rep("rw>=1", rw(n,q)>=1, (n,q))
        # (7.22)
        rhs722 = sum(Fr(k,j)*P(n,j)*((c(j-1,k-1)+c(j-1,k))*s(n-j,k)+s(j-1,k)*(c(n-j,k-1)+c(n-j,k))) for j in range(k+1,n+1)) - P(n,k)*s(n-k,k-1)
        lhs722 = k*s(n,k)*src(n)
        rep("(7.22)", lhs722>=rhs722, n)
        # (7.23)
        br1 = sum(rw(n,q)*(c(k+q,k-1)+c(k+q,k)) for q in range(nu,k+nu)) - s(k+nu,k-1)
        rep("(7.23a)", rhs722 >= P(n,k)*br1, n)
        br2 = c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1)
        rep("(7.23b)", br1>=br2, n)
        # top-roots
        for U0 in range(0,k):
            br3 = br2 + sum((rw(n,k+nu-1-U)-1)*(s(n-1-U,k)-s(n-U,k)) for U in range(0,U0+1))
            rep("top-roots-2", br1>=br3, (n,U0))
            hz = lambda N: 1-s(N+1,k)/s(N,k)
            br4 = s(n,k)*(sum((rw(n,k+nu-1-U)-1)*hz(n-1-U) for U in range(0,U0+1))-1)
            rep("top-roots-3", br3>=br4, (n,U0))
        # apex^H identity
        apex = Fr(1,k)*(sum(Pk(n,j)*(clp(j-1)+clm(j-1)) for j in range(n-k+1,n+1)) - Pk(n,k)*(1-clm(n-k)))
        rep("apex-identity", k*s(n,k)*apex == P(n,k)*br1, n)
        # (7.24) for n>=3k+1
        if n>=3*k+1:
            w = lambda m: Fr(comb(n-1,m)*p(m)*Aa(n-1-m,k-1), Aa(n,k-1))
            fp = lambda m: Fr((k+1)*(Aa(m,k)-Aa(m,k-1))-(k-1)*(Aa(m,k-1)-Aa(m,k-2)), p(m))
            Left = sum(w(m)*fp(m) for m in range(k,2*k+1))
            rep("(7.24)", inhlin(n)+inh(n)==2*Left, n)
        # (7.25) for n<=3k
        if n<=3*k:
            KD = sum((k+n-m)*comb(n-1,m)*p(n-1-m)*d(m) for m in range(2*k+1,n))
            rep("(7.25)", Aa(n,k-1)*(src(n)+inh(n))==d(n)-KD, n)
        # (7.26) at n=3k
        if n==3*k:
            w = lambda m: Fr(comb(n-1,m)*p(m)*Aa(n-1-m,k-1), Aa(n,k-1))
            fp = lambda m: Fr((k+1)*(Aa(m,k)-Aa(m,k-1))-(k-1)*(Aa(m,k-1)-Aa(m,k-2)), p(m))
            Left = sum(w(m)*fp(m) for m in range(k,2*k+1))
            u = w(2*k)*s(2*k,k+1)
            Quad = sum(Pk(n,j)*((1+Fr(1,k))*clp(j-1)*clp(n-j)+(1-Fr(1,k))*clm(j-1)*clm(n-j)) for j in range(k+1,n+1))
            Stem = Fr(1,k)*sum(Pk(n,j)*((clp(j-1)+clm(j-1))*(1 if j-1>2*k else 0)+(clp(n-j)+clm(n-j))*(1 if n-j>2*k else 0)) for j in range(k+1,n+1))
            rep("(7.26)", src(n)+inh(n)==2*Left-u+Quad+Stem, n)
            # threshold-unit-ratio first identity: u/w_k = e^{g(2k)-g(k)} r^thr ; e^{g(x)}=(1+1/x)^{x-1}
            eg = lambda x: Fr((x+1)**(x-1), x**(x-1))
            rep("u/w_k identity", u/w(k)==eg(2*k)/eg(k)*s(2*k,k+1)/s(2*k-1,k), n)
            # w_{m+1}/w_m identity
            for m in range(k,2*k):
                rep("w-ratio", w(m+1)/w(m)==eg(m+1)*s(n-2-m,k)/(eg(n-1-m)*s(n-1-m,k)), (n,m))
            # P^(k)_{3k}(k) = k w_{2k} A_{2k,k-1}/p_{2k}
            rep("Pk(k) at 3k", Pk(n,k)==k*w(2*k)*Fr(Aa(2*k,k-1),p(2*k)), n)
    print("k=%d nmax=%d %s" % (k, nmax, "OK" if ok else "has FAIL"))

for k in range(2,7):
    check(k, 3*k+4)
