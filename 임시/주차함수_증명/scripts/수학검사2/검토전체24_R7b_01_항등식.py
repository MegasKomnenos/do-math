# -*- coding: utf-8 -*-
# 검토전체24 R7b: 7.6-7.8절의 항등식과 부등식을 작은 k에서 정확 유리수로 검산한다.
import sys
from fractions import Fraction as F
from math import comb, log, exp, sqrt, pi, factorial
sys.setrecursionlimit(10000)

def p(m):
    if m == 0: return 1
    return (m+1)**(m-1)

class Tab:
    def __init__(self, N):
        self.N = N
        self.cache = {}
    def A(self, m, l):
        # 최대 변위 <= l 인 길이 m 주차함수의 수
        if l < 0:
            return 1 if m == 0 else 0
        if m == 0: return 1
        key = l
        if key not in self.cache:
            a = [1]
            for mm in range(1, self.N+1):
                s = 0
                for j in range(1, mm+1):
                    s += comb(mm-1, j-1)*min(j, l+1)*a[j-1]*a[mm-j]
                a.append(s)
            self.cache[key] = a
        return self.cache[key][m]

def g(x): return (x-1)*log(1+1/x)

def run(k, nmax):
    T = Tab(nmax)
    A = T.A
    b = lambda m, y: A(m, y) - A(m, y-1)
    d = lambda m, y: b(m, y) - b(m, y-1)
    s = lambda m, y: F(A(m, y-1), p(m))
    c = lambda m, y: F(b(m, y), p(m))
    P = lambda m, j: F(j*comb(m-1, j-1)*p(j-1)*p(m-j), p(m))
    Pk = lambda m, j: F(min(j, k)*comb(m-1, j-1)*A(j-1, k-1)*A(m-j, k-1), A(m, k-1))
    clp = lambda m: F(b(m, k), A(m, k-1))
    clm = lambda m: F(b(m, k-1), A(m, k-1))
    mu = lambda m: F(d(m, k), A(m, k-1))
    def chi(m, j):
        v = F(0)
        if j == k: v -= F(1, k)*(1-clm(m-k))
        if j > k: v += F(1, k)*(clp(j-1)+clm(j-1)+clp(m-j)+clm(m-j))
        ind = 1 if j > k else 0
        v += (1+F(ind, k))*clp(j-1)*clp(m-j) + (1-F(ind, k))*clm(j-1)*clm(m-j)
        return v
    src = lambda m: sum(Pk(m, j)*chi(m, j) for j in range(1, m+1))
    def inh(m):
        v = F(0)
        for j in range(1, m+1):
            t = F(0)
            if k <= j-1 <= 2*k: t += mu(j-1)
            if k <= m-j <= 2*k: t += mu(m-j)
            v += Pk(m, j)*t
        return v
    def inhlin(m):
        v = F(0)
        for j in range(1, m+1):
            t = F(0)
            if k <= j-1 <= 2*k: t += clp(j-1)+clm(j-1)
            if k <= m-j <= 2*k: t += clp(m-j)+clm(m-j)
            v += Pk(m, j)*t
        return v/k
    star = lambda m: src(m)+inh(m)
    delta = lambda m1: (k+1)*b(m1-1, k) - (k-1)*b(m1-1, k-1)
    pp = lambda m: F(delta(m+1), p(m))
    V = lambda m: sum(pp(x) for x in range(m, 2*k+1))
    ok = True
    def chk(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print("  FAIL k=%d: %s" % (k, msg))
    # P^(k) 관계
    for m in range(1, nmax+1):
        for j in range(1, m+1):
            chk(Pk(m, j) == F(min(j, k), j)*P(m, j)*s(j-1, k)*s(m-j, k)/s(m, k), "Pk relation m=%d j=%d" % (m, j))
        chk(sum(Pk(m, j) for j in range(1, m+1)) == 1, "Pk sums to 1")
    # (7.10)
    for m in range(1, nmax+1):
        rhs = src(m) + sum(Pk(m, j)*(mu(j-1)+mu(m-j)) for j in range(1, m+1))
        chk(mu(m) == rhs, "(7.10) m=%d" % m)
    # 7.6
    for n in range(2*k+1, nmax+1):
        nu = n-2*k
        rw = lambda q: F(k, k+1+q)*P(n, k+1+q)/P(n, k)
        chk(rw(nu) == 1, "rw(nu)=1 n=%d" % n)
        for q in range(0, k+nu-1):
            lhs = float(rw(q+1)/rw(q)); rhs = exp(g(k+1+q)-g(k+nu-1-q))
            chk(abs(lhs/rhs-1) < 1e-9, "rw ratio n=%d q=%d" % (n, q))
        for q in range(nu, k+nu):
            chk(rw(q) >= 1, "rw>=1")
        apex = F(1, k)*(sum(Pk(n, j)*(clp(j-1)+clm(j-1)) for j in range(n-k+1, n+1)) - Pk(n, k)*(1-clm(n-k)))
        S = src(n)
        chk(S >= apex, "src>=apex n=%d" % n)
        lhs = k*s(n, k)*apex
        eq = P(n, k)*(sum(rw(q)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1))
        chk(lhs == eq, "(7.11) equality n=%d" % n)
        hz = lambda N: 1 - s(N+1, k)/s(N, k)
        for U0 in range(0, k):
            mid = P(n, k)*(c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)
                 + sum((rw(k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1)))
            last = P(n, k)*s(n, k)*(sum((rw(k+nu-1-U)-1)*hz(n-1-U) for U in range(0, U0+1)) - 1)
            chk(eq >= mid, "(7.11) first ineq n=%d U0=%d" % (n, U0))
            chk(mid >= last, "(7.11) second ineq n=%d U0=%d" % (n, U0))
        if n >= 3*k+1:
            chk(S >= inhlin(n)+apex, "src-plus decomposition n=%d" % n)
        # 분할 무게
        w = lambda m: F(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
        ww = lambda t: comb(n, t)*t**(t-1)*A(n-t, k-1)
        for m in range(k, 2*k+1):
            chk(Pk(n, m+1) == k*s(m, k)*w(m), "Pk=k s w")
            chk(w(m) == F(ww(m+1), n*A(n, k-1)), "w=marked/(nA)")
        Left = sum(w(m)*pp(m) for m in range(k, 2*k+1))
        v713 = (inhlin(n)+inh(n) == 2*Left)
        if n >= 3*k+1:
            chk(v713, "(7.13) n=%d" % n)
        else:
            if v713: print("  note k=%d n=%d: (7.13) also holds below 3k+1" % (k, n))
        # w ratio
        for m in range(k, 2*k):
            lhs = float(w(m+1)/w(m))
            rhs = exp(g(m+1))*float(s(n-2-m, k))/(exp(g(n-1-m))*float(s(n-1-m, k)))
            chk(abs(lhs/rhs-1) < 1e-9, "w ratio")
        if 2*k+1 <= n <= 3*k:
            KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m, k) for m in range(2*k+1, n))
            chk(A(n, k-1)*star(n) == d(n, k)-KD, "(7.14) n=%d" % n)
        if n == 3*k:
            u = w(n-k)*s(n-k, k+1)
            Quad = sum(Pk(n, j)*((1+F(1, k))*clp(j-1)*clp(n-j)+(1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
            Stem = F(1, k)*sum(Pk(n, j)*(((clp(j-1)+clm(j-1)) if j-1 > 2*k else 0)+((clp(n-j)+clm(n-j)) if n-j > 2*k else 0)) for j in range(k+1, n+1))
            chk(star(n) == 2*Left-u+Quad+Stem, "(7.15)")
            r1 = float(u/w(k)); r2 = exp(g(2*k)-g(k))*float(s(2*k, k+1)/s(2*k-1, k))
            chk(abs(r1/r2-1) < 1e-9, "threshold-unit equality")
            chk(float(s(2*k, k+1)/s(2*k-1, k)) <= exp(g(k))*(1+1e-12), "ratio<=e^g(k)")
            chk(Pk(n, k) == k*w(2*k)*F(A(2*k, k-1), p(2*k)), "Pk(3k)(k)")
            print("  k=%d: u/w_k=%.5f, e^{g(2k)}=%.5f, star(3k)/w_k=%.5f, V_k(k)=%.5f, Quad/w_k=%.4f Stem/w_k=%.4f"
                  % (k, r1, exp(g(2*k)), float(star(n)/w(k)), float(V(k)), float(Quad/w(k)), float(Stem/w(k))))
    print("k=%d nmax=%d: %s" % (k, nmax, "all ok" if ok else "FAILED"))

for k in range(2, 9):
    run(k, 4*k+3)
