# -*- coding: utf-8 -*-
# 검토전체25 R7b: 7.6-7.8절 항등식·부등식의 작은 k 정확 유리수 검산
from fractions import Fraction as F
from math import comb, log, exp
import sys

def p(m):
    return 1 if m == 0 else (m + 1) ** (m - 1)

def Atable(nmax, l):
    # A_{m,l}: max displacement <= l ; l=-1 -> 0 (m>=1)
    A = [0] * (nmax + 1)
    A[0] = 1
    if l < 0:
        return A
    for m in range(1, nmax + 1):
        A[m] = sum(comb(m - 1, j - 1) * min(j, l + 1) * A[j - 1] * A[m - j] for j in range(1, m + 1))
    return A

def g(x):
    return (x - 1) * log(1 + 1 / x)

def run(k, nmax):
    Am2 = Atable(nmax, k - 2); Am1 = Atable(nmax, k - 1); A0 = Atable(nmax, k); Ap = Atable(nmax, k + 1)
    b = lambda m, l: {k: A0[m] - Am1[m], k - 1: Am1[m] - Am2[m]}[l]
    s = lambda m, y: F({k - 1: Am2, k: Am1, k + 1: A0, k + 2: Ap}[y][m], p(m))
    c = lambda m, Y: F(b(m, Y), p(m))
    clp = lambda m: F(b(m, k), Am1[m]); clm = lambda m: F(b(m, k - 1), Am1[m])
    d = lambda m: b(m, k) - b(m, k - 1)
    mu = lambda m: F(d(m), Am1[m])
    Pk = lambda m, j: F(min(j, k) * comb(m - 1, j - 1) * Am1[j - 1] * Am1[m - j], Am1[m])
    P = lambda m, j: F(j * comb(m - 1, j - 1) * p(j - 1) * p(m - j), p(m))
    def chi(m, j):
        h = 1 if j > k else 0
        lin = F(0)
        if j == k:
            lin -= (1 - clm(m - k))
        if j > k:
            lin += clp(j - 1) + clm(j - 1) + clp(m - j) + clm(m - j)
        return lin / k + (1 + F(h, k)) * clp(j - 1) * clp(m - j) + (1 - F(h, k)) * clm(j - 1) * clm(m - j)
    src = lambda m: sum(Pk(m, j) * chi(m, j) for j in range(1, m + 1))
    inh = lambda m: sum(Pk(m, j) * ((mu(j - 1) if k <= j - 1 <= 2 * k else 0) + (mu(m - j) if k <= m - j <= 2 * k else 0)) for j in range(1, m + 1))
    inhlin = lambda m: sum(Pk(m, j) * (((clp(j - 1) + clm(j - 1)) if k <= j - 1 <= 2 * k else 0) + ((clp(m - j) + clm(m - j)) if k <= m - j <= 2 * k else 0)) for j in range(1, m + 1)) / k
    apex = lambda n: (sum(Pk(n, j) * (clp(j - 1) + clm(j - 1)) for j in range(n - k + 1, n + 1)) - Pk(n, k) * (1 - clm(n - k))) / k
    hz = lambda N: 1 - s(N + 1, k) / s(N, k)
    w = lambda n, m: F(comb(n - 1, m) * p(m) * Am1[n - 1 - m], Am1[n])
    pm = lambda m: F((k + 1) * b(m, k) - (k - 1) * b(m, k - 1), p(m))
    V = lambda m: sum(pm(x) for x in range(m, 2 * k + 1))
    ok = True
    def chk(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print("FAIL", k, msg)
    # (7.10)
    for m in range(1, nmax + 1):
        chk(mu(m) == src(m) + sum(Pk(m, j) * (mu(j - 1) + mu(m - j)) for j in range(1, m + 1)), "7.10 m=%d" % m)
    # P^(k) relation
    for n in range(k + 1, nmax + 1):
        for j in range(1, n + 1):
            chk(Pk(n, j) == F(min(j, k), j) * P(n, j) * s(j - 1, k) * s(n - j, k) / s(n, k), "Pk rel")
    for n in range(2 * k + 1, nmax + 1):
        nu = n - 2 * k
        rw = lambda q: F(k, k + 1 + q) * P(n, k + 1 + q) / P(n, k)
        chk(rw(nu) == 1, "rw(nu)")
        for q in range(0, k + nu - 1):
            r = rw(q + 1) / rw(q)
            chk(abs(float(r) - exp(g(k + 1 + q) - g(k + nu - 1 - q))) < 1e-9 * float(r), "rw ratio")
        for q in range(nu, k + nu):
            chk(rw(q) >= 1, "rw>=1")
        S = src(n); ap = apex(n)
        chk(S >= ap, "src>=apex n=%d" % n)
        lhs = k * s(n, k) * ap
        eq = P(n, k) * (sum(rw(q) * (c(k + q, k - 1) + c(k + q, k)) for q in range(nu, k + nu)) - s(k + nu, k - 1))
        chk(lhs == eq, "7.11 eq n=%d" % n)
        for U0 in range(0, k):
            mid = P(n, k) * (c(k + nu, k - 1) + s(k + nu, k + 1) - s(n, k) - s(n, k + 1) + sum((rw(k + nu - 1 - U) - 1) * (s(n - 1 - U, k) - s(n - U, k)) for U in range(0, U0 + 1)))
            last = P(n, k) * s(n, k) * (sum((rw(k + nu - 1 - U) - 1) * hz(n - 1 - U) for U in range(0, U0 + 1)) - 1)
            chk(eq >= mid >= last, "7.11 ineq n=%d U0=%d" % (n, U0))
        if n >= 3 * k + 1:
            il = inhlin(n)
            chk(S >= il + ap, "src>=inhlin+apex n=%d" % n)
            Left = sum(w(n, m) * pm(m) for m in range(k, 2 * k + 1))
            chk(il + inh(n) == 2 * Left, "7.13 n=%d" % n)
        if n <= 3 * k:
            KD = sum((k + n - m) * comb(n - 1, m) * p(n - 1 - m) * d(m) for m in range(2 * k + 1, n))
            chk(Am1[n] * (S + inh(n)) == d(n) - KD, "7.14 n=%d" % n)
        # w_m = k s_m(k) w_m relation
        for m in range(k, 2 * k + 1):
            if m + 1 <= n:
                chk(Pk(n, m + 1) == k * s(m, k) * w(n, m), "Pk=k s w")
    # n=3k
    n = 3 * k
    if n <= nmax:
        u = w(n, 2 * k) * s(2 * k, k + 1)
        Left = sum(w(n, m) * pm(m) for m in range(k, 2 * k + 1))
        Quad = sum(Pk(n, j) * ((1 + F(1, k)) * clp(j - 1) * clp(n - j) + (1 - F(1, k)) * clm(j - 1) * clm(n - j)) for j in range(k + 1, n + 1))
        Stem = sum(Pk(n, j) * (((clp(j - 1) + clm(j - 1)) if j - 1 > 2 * k else 0) + ((clp(n - j) + clm(n - j)) if n - j > 2 * k else 0)) for j in range(k + 1, n + 1)) / k
        chk(src(n) + inh(n) == 2 * Left - u + Quad + Stem, "7.15")
        ratio = u / w(n, k)
        rho = s(2 * k, k + 1) / s(2 * k - 1, k)
        chk(abs(float(ratio) - exp(g(2 * k) - g(k)) * float(rho)) < 1e-9, "thr unit ratio")
        chk(float(rho) <= exp(g(k)), "rho<=e^g(k)")
        print("k=%d  u/w_k=%.5f  rho=%.5f  e^g(k)=%.5f  V_k(k)=%.5f  (star)(3k)/w_k=%.5f" % (k, float(ratio), float(rho), exp(g(k)), float(V(k)), float((src(n) + inh(n)) / w(n, k))))
        # threshold root piece
        chk(Pk(n, k) * (mu(2 * k) - (1 - clm(2 * k)) / k) == w(n, 2 * k) * pm(2 * k) - u, "threshold piece")
    # sign of d_{m,k} in first layer
    print("  d_{m,k} sign, m=k..2k:", "".join("+" if d(m) > 0 else ("0" if d(m) == 0 else "-") for m in range(k, 2 * k + 1)))
    print("  p_m sign, m=k..2k:    ", "".join("+" if pm(m) > 0 else ("0" if pm(m) == 0 else "-") for m in range(k, 2 * k + 1)))
    # w monotone check for n in second layer & third
    for n in (2 * k + 1, 3 * k, 3 * k + 1, min(nmax, 4 * k)):
        mono = all(w(n, m + 1) >= w(n, m) for m in range(k, 2 * k))
        print("  n=%d w nondecreasing on [k,2k]: %s" % (n, mono))
    print("k=%d nmax=%d: %s" % (k, nmax, "ALL OK" if ok else "FAILURES"))

for k in (2, 3, 4, 5, 6, 7):
    run(k, 5 * k + 6)
run(12, 40)
