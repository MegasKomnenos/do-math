# 7.6-7.7절 항등식·부등식의 정확 유리수 검사 (O7b)
from fractions import Fraction as F
from math import comb
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)

@lru_cache(None)
def A(m, l):
    # 최대 변위 <= l 인 길이 m 주차함수 수 (정리 2-6 재귀)
    if l < 0: return 0
    if m == 0: return 1
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))

def p(m): return (m+1)**(m-1) if m>0 else 1
def s(m, y): return F(A(m, y-1), p(m))          # 생존 확률
def c(m, Y): return s(m, Y+1) - s(m, Y)          # 수준 질량 c_m(Y)
def P(n, j): return F(j*comb(n-1, j-1)*p(j-1)*p(n-j), p(n))   # 마지막 차 자리 법칙
def Pk(n, j, k): return F(min(j,k)*comb(n-1,j-1)*A(j-1,k-1)*A(n-j,k-1), A(n,k-1))
def clp(m,k): return F(A(m,k)-A(m,k-1), A(m,k-1))
def clm(m,k): return F(A(m,k-1)-A(m,k-2), A(m,k-1))
def mu(m,k): return clp(m,k)-clm(m,k)
def chi(m,j,k):
    L, R = j-1, m-j
    lin = F(0)
    if j == k: lin = -(1-clm(m-k,k))/k
    if j > k: lin = (clp(L,k)+clm(L,k)+clp(R,k)+clm(R,k))/k
    hv = 1 if j>k else 0
    return lin + (1+F(hv,k))*clp(L,k)*clp(R,k) + (1-F(hv,k))*clm(L,k)*clm(R,k)
def src(n,k): return sum(Pk(n,j,k)*chi(n,j,k) for j in range(1,n+1))
def inh(n,k): return sum(Pk(n,j,k)*(mu(j-1,k)*(k<=j-1<=2*k) + mu(n-j,k)*(k<=n-j<=2*k)) for j in range(1,n+1))
def d(n,k): return A(n,k)-2*A(n,k-1)+A(n,k-2)

ok = True
for k in [3,4,5]:
    for nu in range(1, k+3):
        n = 2*k+nu
        # 7.13 한 걸음 항등식 (sanity)
        lhs = mu(n,k); rhs = src(n,k)+sum(Pk(n,j,k)*(mu(j-1,k)+mu(n-j,k)) for j in range(1,n+1))
        assert lhs == rhs, ("7.13", k, n)
        # rw, root-symmetry
        rw = lambda q: F(k, k+1+q)*P(n,k+1+q)/P(n,k)
        assert rw(nu) == 1, ("rw(nu)", k, n)
        import math
        g = lambda x: (x-1)*math.log(1+1/x)
        for q in range(0, k+nu-1):
            r = float(rw(q+1)/rw(q)); e = math.exp(g(k+1+q)-g(k+nu-1-q))
            assert abs(r-e) < 1e-9, ("rw ratio", k, n, q, r, e)
        for q in range(nu, k+nu):
            assert rw(q) >= 1, ("rw>=1", k,n,q)
        # (7.22)
        left = k*s(n,k)*src(n,k)
        r722 = sum(F(k,j)*P(n,j)*((c(j-1,k-1)+c(j-1,k))*s(n-j,k)+s(j-1,k)*(c(n-j,k-1)+c(n-j,k))) for j in range(k+1,n+1)) - P(n,k)*s(n-k,k-1)
        assert left >= r722, ("7.22", k, n)
        # (7.23)
        b1 = sum(rw(q)*(c(k+q,k-1)+c(k+q,k)) for q in range(nu, k+nu)) - s(k+nu,k-1)
        b2 = c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1)
        assert r722 >= P(n,k)*b1 >= P(n,k)*b2, ("7.23", k, n)
        # apex^H identity: k s_n apex^H = P_n(k) * b1
        apex = (sum(Pk(n,j,k)*(clp(j-1,k)+clm(j-1,k)) for j in range(n-k+1,n+1)) - Pk(n,k,k)*(1-clm(n-k,k)))/k
        assert k*s(n,k)*apex == P(n,k)*b1, ("apex", k, n)
        # top-roots second/third inequality with U0 = k-1
        U0 = k-1
        extra = sum((rw(k+nu-1-U)-1)*(s(n-1-U,k)-s(n-U,k)) for U in range(0,U0+1))
        assert b1 >= b2 + extra, ("top-roots 2", k, n)
        hz = lambda N: 1 - s(N+1,k)/s(N,k)
        b3 = s(n,k)*(sum((rw(k+nu-1-U)-1)*hz(n-1-U) for U in range(0,U0+1)) - 1)
        assert b2 + extra >= b3, ("top-roots 3", k, n)
        # 7.7: w_m, (7.24), (7.25), (7.26)
        w = lambda m: F(comb(n-1,m)*p(m)*A(n-1-m,k-1), A(n,k-1))
        pfrak = lambda m: F((k+1)*(A(m,k)-A(m,k-1)) - (k-1)*(A(m,k-1)-A(m,k-2)), p(m))
        for m in range(k, 2*k+1):
            assert Pk(n,m+1,k) == k*s(m,k)*w(m), ("Pk=ksw", k, n, m)
        if n >= 2*k+1:
            for m in range(k, 2*k):
                assert w(m+1) >= w(m), ("w nondecr", k, n, m)
        if n >= 3*k+1:
            inhlin = sum(Pk(n,j,k)*((clp(j-1,k)+clm(j-1,k))*(k<=j-1<=2*k)+(clp(n-j,k)+clm(n-j,k))*(k<=n-j<=2*k)) for j in range(1,n+1))/k
            Left = sum(w(m)*pfrak(m) for m in range(k,2*k+1))
            assert inhlin + inh(n,k) == 2*Left, ("7.24", k, n)
        if n <= 3*k:
            KDp = sum((k+n-m)*comb(n-1,m)*p(n-1-m)*d(m,k) for m in range(2*k+1, n))
            assert A(n,k-1)*(src(n,k)+inh(n,k)) == d(n,k)-KDp, ("7.25", k, n)
        if n == 3*k:
            Left = sum(w(m)*pfrak(m) for m in range(k,2*k+1))
            u = w(2*k)*s(2*k,k+1)
            Quad = sum(Pk(n,j,k)*((1+F(1,k))*clp(j-1,k)*clp(n-j,k)+(1-F(1,k))*clm(j-1,k)*clm(n-j,k)) for j in range(k+1,n+1))
            Stem = sum(Pk(n,j,k)*((clp(j-1,k)+clm(j-1,k))*(j-1>2*k)+(clp(n-j,k)+clm(n-j,k))*(n-j>2*k)) for j in range(k+1,n+1))/k
            assert src(n,k)+inh(n,k) == 2*Left - u + Quad + Stem, ("7.26", k, n)
            # threshold-unit-ratio first equality
            ratio = u / w(k)
            e_g = math.exp(g(2*k)-g(k))
            rthr = s(2*k,k+1)/s(2*k-1,k)
            assert abs(float(ratio) - e_g*float(rthr)) < 1e-9, ("u/w", k, ratio, e_g*float(rthr))
print("all exact checks passed for k=3,4,5")
