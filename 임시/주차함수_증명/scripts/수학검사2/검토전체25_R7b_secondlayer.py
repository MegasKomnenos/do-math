# -*- coding: utf-8 -*-
# 검토전체25 R7b: 7.7절 끝 문단(n<3k에서 가벼운 뿌리의 첫 층 자식 몫)의 정확 검산
from fractions import Fraction as F
from math import comb

def p(m):
    return 1 if m == 0 else (m + 1) ** (m - 1)

def Atable(nmax, l):
    A = [0] * (nmax + 1); A[0] = 1
    if l < 0:
        return A
    for m in range(1, nmax + 1):
        A[m] = sum(comb(m - 1, j - 1) * min(j, l + 1) * A[j - 1] * A[m - j] for j in range(1, m + 1))
    return A

def run(k):
    nmax = 3 * k
    Am2 = Atable(nmax, k - 2); Am1 = Atable(nmax, k - 1); A0 = Atable(nmax, k)
    bk = lambda m: A0[m] - Am1[m]; bk1 = lambda m: Am1[m] - Am2[m]
    clp = lambda m: F(bk(m), Am1[m]); clm = lambda m: F(bk1(m), Am1[m])
    d = lambda m: bk(m) - bk1(m)
    mu = lambda m: F(d(m), Am1[m])
    Pk = lambda m, j: F(min(j, k) * comb(m - 1, j - 1) * Am1[j - 1] * Am1[m - j], Am1[m])
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
    pm = lambda m: F((k + 1) * bk(m) - (k - 1) * bk1(m), p(m))
    ok = True
    for n in range(2 * k + 1, 3 * k + 1):
        w = lambda m: F(comb(n - 1, m) * p(m) * Am1[n - 1 - m], Am1[n])
        Left = sum(w(m) * pm(m) for m in range(k, 2 * k + 1))
        Right = sum(w(m) * pm(m) for m in range(k, n - k + 1))
        u = w(n - k) * F(A0[n - k], p(n - k))
        light = sum((n - m) * w(m) * F(d(m), p(m)) for m in range(n - k + 1, 2 * k + 1))
        Quad = sum(Pk(n, j) * ((1 + F(1, k)) * clp(j - 1) * clp(n - j) + (1 - F(1, k)) * clm(j - 1) * clm(n - j)) for j in range(k + 1, n + 1))
        Stem = sum(Pk(n, j) * (((clp(j - 1) + clm(j - 1)) if j - 1 > 2 * k else 0) + ((clp(n - j) + clm(n - j)) if n - j > 2 * k else 0)) for j in range(k + 1, n + 1)) / k
        lhs = src(n) + inh(n)
        good = (lhs == Left + Right - u + light + Quad + Stem)
        # per-root check for light roots
        for j in range(max(1, n - 2 * k), k):
            m = n - j
            good = good and (Pk(n, j) * mu(m) == (n - m) * w(m) * F(d(m), p(m)))
        ok = ok and good
        print("k=%d n=%d: decomposition %s; light term=%.5g  (star)=%.5g  light d-signs: %s" % (
            k, n, good, float(light), float(lhs), "".join("+" if d(m) > 0 else "-" for m in range(n - k + 1, 2 * k + 1))))
    print("k=%d %s" % (k, "ALL OK" if ok else "FAIL"))

for k in (4, 7, 12):
    run(k)
