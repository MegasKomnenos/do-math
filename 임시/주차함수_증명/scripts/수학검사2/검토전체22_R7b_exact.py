# 검토전체22 R7b: 7.6-7.8절 항등식·부등식의 정확 유리수 검산 (작은 k)
from fractions import Fraction as F
from math import comb
import sys

def build(k, nmax):
    # A[l][m] for l in {k-2,k-1,k}
    A = {}
    for l in (k-2, k-1, k):
        a = [1]
        for m in range(1, nmax+1):
            a.append(sum(comb(m-1, j-1)*min(j, l+1)*a[j-1]*a[m-j] for j in range(1, m+1)))
        A[l] = a
    return A

def p(n): return (n+1)**(n-1) if n >= 1 else 1

def run(k, nmax):
    A = build(k, nmax)
    Ak = A[k-1]
    def b(m, l):  # exact level count l in {k-1,k}
        if l == k: return A[k][m]-A[k-1][m]
        if l == k-1: return A[k-1][m]-A[k-2][m]
    def s(m, y): return F(A[y-1][m], p(m))
    def c(m, Y): return F(b(m, Y), p(m))
    def clp(m): return F(b(m, k), Ak[m])
    def clm(m): return F(b(m, k-1), Ak[m])
    def mu(m): return clp(m)-clm(m)
    def d(m): return b(m, k)-b(m, k-1)
    def Pk(m, j): return F(min(j, k)*comb(m-1, j-1)*Ak[j-1]*Ak[m-j], Ak[m])
    def P(m, j): return F(j*comb(m-1, j-1)*p(j-1)*p(m-j), p(m))
    def chi(m, j):
        L, R = j-1, m-j
        v = F(0)
        if j == k: v -= F(1, k)*(1-clm(m-k))
        if j > k: v += F(1, k)*(clp(L)+clm(L)+clp(R)+clm(R))
        hv = 1 if j > k else 0
        v += (1+F(hv, k))*clp(L)*clp(R) + (1-F(hv, k))*clm(L)*clm(R)
        return v
    def src(m): return sum(Pk(m, j)*chi(m, j) for j in range(1, m+1))
    def inh(m): return sum(Pk(m, j)*((mu(j-1) if k <= j-1 <= 2*k else 0)+(mu(m-j) if k <= m-j <= 2*k else 0)) for j in range(1, m+1))
    def inhlin(m): return F(1, k)*sum(Pk(m, j)*(((clp(j-1)+clm(j-1)) if k <= j-1 <= 2*k else 0)+((clp(m-j)+clm(m-j)) if k <= m-j <= 2*k else 0)) for j in range(1, m+1))
    def apex(n): return F(1, k)*(sum(Pk(n, j)*(clp(j-1)+clm(j-1)) for j in range(n-k+1, n+1)) - Pk(n, k)*(1-clm(n-k)))
    def w(n, m): return F(comb(n-1, m)*p(m)*Ak[n-1-m], Ak[n])
    def pm(m): return (k+1)*c(m, k)-(k-1)*c(m, k-1)
    def Left(n): return sum(w(n, m)*pm(m) for m in range(k, 2*k+1))
    def Quad(n): return sum(Pk(n, j)*((1+F(1, k))*clp(j-1)*clp(n-j)+(1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
    def Stem(n): return F(1, k)*sum(Pk(n, j)*(((clp(j-1)+clm(j-1)) if j-1 > 2*k else 0)+((clp(n-j)+clm(n-j)) if n-j > 2*k else 0)) for j in range(k+1, n+1))
    def KD(n): return sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m) for m in range(2*k+1, n))
    def hz(N): return 1 - s(N+1, k)/s(N, k)
    ok = True
    # (7.10)
    for m in range(1, nmax+1):
        rhs = src(m)+sum(Pk(m, j)*(mu(j-1)+mu(m-j)) for j in range(1, m+1))
        if rhs != mu(m): ok = False; print('7.10 FAIL', k, m)
        if abs(sum(Pk(m, j) for j in range(1, m+1)) - 1) != 0: ok = False; print('Pk not prob', k, m)
    # root symmetry, top-roots (7.11)
    for n in range(2*k+1, nmax+1):
        nu = n-2*k
        def rw(q): return F(k, k+1+q)*P(n, k+1+q)/P(n, k)
        if rw(nu) != 1: ok = False; print('rw(nu) FAIL', k, n)
        for q in range(nu, k+nu): 
            if rw(q) < 1: ok = False; print('rw>=1 FAIL', k, n, q)
        lhs = k*s(n, k)*apex(n)
        mid0 = P(n, k)*(sum(rw(q)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1))
        if lhs != mid0: ok = False; print('7.11 eq FAIL', k, n)
        if src(n) < apex(n): ok = False; print('src>=apex FAIL', k, n)
        for U0 in range(0, k):
            mid1 = P(n, k)*(c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)+sum((rw(k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1)))
            mid2 = P(n, k)*s(n, k)*(sum((rw(k+nu-1-U)-1)*hz(n-1-U) for U in range(0, U0+1))-1)
            if not (mid0 >= mid1 >= mid2): ok = False; print('7.11 ineq FAIL', k, n, U0)
        # 7.14 second layer
        if n <= 3*k:
            if Ak[n]*(src(n)+inh(n)) != d(n)-KD(n): ok = False; print('7.14 FAIL', k, n)
        if n >= 3*k+1:
            if inhlin(n)+inh(n) != 2*Left(n): ok = False; print('7.13 FAIL', k, n)
            if src(n) < inhlin(n)+apex(n): ok = False; print('src-plus ineq FAIL', k, n)
        if n == 3*k:
            u = w(n, 2*k)*s(2*k, k+1)
            if src(n)+inh(n) != 2*Left(n)-u+Quad(n)+Stem(n): ok = False; print('7.15 FAIL', k)
            # threshold unit ratio: u/w_k = e^{g(2k)-g(k)} r_thr ; e^{g(x)}=(1+1/x)^(x-1) rational
            eg = lambda x: F(x+1, x)**(x-1)
            rthr = s(2*k, k+1)/s(2*k-1, k)
            if u/w(n, k) != eg(2*k)/eg(k)*rthr: ok = False; print('thr ratio FAIL', k)
            if not rthr <= eg(k): ok = False; print('rthr bound FAIL', k)
            print('  k=%d: u/w_k=%.5f  rthr=%.5f  e^g(k)=%.5f  (star)(3k)/w_k=%.5f  V_k(k)=%.5f' % (k, float(u/w(n, k)), float(rthr), float(eg(k)), float((src(n)+inh(n))/w(n, k)), float(sum(pm(m) for m in range(k, 2*k+1)))))
    # mu_k(k) = -p_{k-1}/p_k
    if mu(k) != -F(p(k-1), p(k)): ok = False; print('mu_k FAIL', k)
    print('k=%d nmax=%d all exact checks %s' % (k, nmax, 'OK' if ok else 'FAILED'))

for k in range(2, 9):
    run(k, 5*k+4)
