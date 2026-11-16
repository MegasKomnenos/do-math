# -*- coding: utf-8 -*-
"""Q10 exact checks for chapter 10 (ledger identity, split weights, stay form, chain reps).
Uses Fractions. Small k."""
from fractions import Fraction as F
from math import comb, factorial
import itertools


def build(K, NMAX):
    p = [(m + 1) ** (m - 1) if m >= 1 else 1 for m in range(NMAX + 1)]
    LMAX = K + 2
    A = [[F(0)] * (LMAX + 2) for _ in range(NMAX + 1)]  # index l+1

    def getA(m, l):
        if l < 0:
            return F(0)
        return A[m][l + 1]

    for l in range(0, LMAX + 1):
        A[0][l + 1] = F(1)
        for m in range(1, NMAX + 1):
            A[m][l + 1] = sum(F(comb(m - 1, j - 1)) * min(j, l + 1) * getA(j - 1, l) * getA(m - j, l)
                              for j in range(1, m + 1))
    return p, getA


def run(k):
    NMAX = 3 * k
    p, A = build(k, NMAX)

    def s(m, y):
        return A(m, y - 1) / p[m]

    def c(m, Y):
        return s(m, Y + 1) - s(m, Y)

    def b(m, l):
        return A(m, l) - A(m, l - 1)

    def d(m):
        return b(m, k) - b(m, k - 1)

    def clp(m):
        return c(m, k) / s(m, k) if m >= 1 else F(0)

    def clm(m):
        return c(m, k - 1) / s(m, k) if m >= 1 else F(0)

    def mu(m):
        return d(m) / A(m, k - 1) if m >= 1 else F(0)

    def P(n, j):
        return F(min(j, k) * comb(n - 1, j - 1)) * A(j - 1, k - 1) * A(n - j, k - 1) / A(n, k - 1)

    def chi(n, j):
        L, R = j - 1, n - j
        lin = F(1, k) * (-(1 if j == k else 0) * (1 - clm(R))
                         + (1 if j > k else 0) * (clp(L) + clm(L) + clp(R) + clm(R)))
        quad = (1 + F(1 if j > k else 0, k)) * clp(L) * clp(R) + (1 - F(1 if j > k else 0, k)) * clm(L) * clm(R)
        return lin + quad

    def src(n):
        return sum(P(n, j) * chi(n, j) for j in range(1, n + 1))

    def inh(n):
        return sum(P(n, j) * (mu(j - 1) * (1 if k <= j - 1 <= 2 * k else 0)
                              + mu(n - j) * (1 if k <= n - j <= 2 * k else 0)) for j in range(1, n + 1))

    def eg(x):  # e^{g(x)} for integer x>=1
        return (1 + F(1, x)) ** (x - 1)

    def borr(j):  # Bor(j) * e^j
        return F(j ** (j - 1), factorial(j))

    for m in range(1, NMAX + 1):
        rhs = src(m) + sum(P(m, j) * (mu(j - 1) + mu(m - j)) for j in range(1, m + 1))
        assert mu(m) == rhs, ("7.13 fail", k, m)
    ok = True
    for n in range(2 * k + 1, 3 * k + 1):
        nu = n - 2 * k
        N = n - k
        star = src(n) + inh(n)
        KDp = sum(F((k + n - m) * comb(n - 1, m)) * p[n - 1 - m] * d(m) for m in range(2 * k + 1, n))
        assert A(n, k - 1) * star == d(n) - KDp, ("7.25 fail", k, n)
        w = {m: F(comb(n - 1, m)) * p[m] * A(n - 1 - m, k - 1) / A(n, k - 1) for m in range(k, n)}
        u = w[N] * A(N, k) / p[N]
        Quad = sum(P(n, j) * ((1 + F(1, k)) * clp(j - 1) * clp(n - j) + (1 - F(1, k)) * clm(j - 1) * clm(n - j))
                   for j in range(k + 1, n + 1))
        Stem = sum(P(n, j) * F(1, k) * ((clp(j - 1) + clm(j - 1)) * (1 if j - 1 > 2 * k else 0)
                                        + (clp(n - j) + clm(n - j)) * (1 if n - j > 2 * k else 0))
                   for j in range(k + 1, n + 1))

        def c2(m):
            return c(m, k) + c(m, k - 1)

        assert Stem == sum(w[m] * c2(m) for m in range(2 * k + 1, n)), ("Stem fail", k, n)

        def kap(m):
            return F(2) if m <= N else 1 + F(n - m, k)

        def f(m):
            return kap(m) * k * d(m) / p[m] + (2 - (1 if m > N else 0)) * c2(m)

        def f2(m):
            if m <= N:
                return 2 * ((k + 1) * c(m, k) - (k - 1) * c(m, k - 1))
            return (k + n - m + 1) * c(m, k) - (k + n - m - 1) * c(m, k - 1)

        for m in range(k, 2 * k + 1):
            assert f(m) == f2(m)
        T = {m: sum(f(i) for i in range(m, 2 * k + 1)) for m in range(k, 2 * k + 2)}
        ledger = sum(w[m] * f(m) for m in range(k, 2 * k + 1)) - u + Quad + Stem
        if ledger != star:
            print("LEDGER FAIL", k, n, float(ledger), float(star))
            ok = False
        abel = w[k] * T[k] + sum((w[m] - w[m - 1]) * T[m] for m in range(k + 1, 2 * k + 1))
        assert abel == sum(w[m] * f(m) for m in range(k, 2 * k + 1))

        def rr(m):
            return A(m + 1, k - 1) / ((m + 1) * A(m, k - 1))

        for m in range(k, n - 1):
            assert w[m + 1] / w[m] == eg(m + 1) / rr(n - 2 - m), ("(a) fail", k, n, m)
        for m in range(k, 2 * k):
            assert w[m + 1] >= w[m], ("(c) fail", k, n, m)
        for m in range(N, n):
            assert w[m] / w[N] == borr(m + 1) * borr(n - m) / (borr(N + 1) * borr(k)), ("(d) fail", k, n, m)
        for m in range(k, N + 1):
            gL = F(1)
            for i in range(k, m):
                gL *= eg(i + 1) / eg(n - 1 - i)
            assert w[m] / w[k] == gL * s(n - 1 - m, k) / s(N - 1, k), ("(e) fail", k, n, m)
        assert u / w[k] == eg(N) / eg(k) * s(N, k + 1) / s(N - 1, k), ("(e)u fail", k, n)

        def vs(m, l):
            return s(m + 1, l + 1) - s(m, l)

        if k >= 3 and nu <= k - 1:
            def DD(m):
                return (k + 1) * s(m + 1, k + 1) - 2 * k * s(m, k) + (k - 1) * s(m - 1, k - 1)

            for m in range(k + 1, 2 * k + 1):
                assert DD(m) == (k + 1) * vs(m, k) - (k - 1) * vs(m - 1, k - 1)

            def om(m):
                return F(2) if m <= N + 1 else 2 - F(m - N, k)

            Stays = 2 * vs(N + 1, k) + sum((2 - F(m - N, k)) * (vs(m, k) + vs(m - 1, k - 1))
                                           for m in range(N + 2, 2 * k + 1))
            BdS = -(k + nu) * (vs(2 * k, k) + c(2 * k, k - 1)) - s(2 * k, k - 1)
            for m0 in range(k, N + 1):
                rhs = (2 * k * c(m0, k) + 2 * s(m0, k + 1) + 2 * s(m0, k) + (2 * k + 2) * vs(m0, k)
                       - 2 * s(N + 1, k + 1) - s(N + 2, k + 1) + BdS
                       + sum(om(m) * DD(m) for m in range(m0 + 1, 2 * k + 1)) - Stays)
                if rhs != T[m0]:
                    print("STAYFORM (ga) FAIL", k, n, m0, float(rhs), float(T[m0]))
                    ok = False
            for m0 in range(N + 1, 2 * k + 1):
                mf = 3 * k + nu - m0
                rhs = (mf * c(m0, k) + s(m0, k) + (s(m0, k + 1) - s(m0 + 1, k + 1)) + (mf + 1) * vs(m0, k) + BdS
                       + sum(om(m) * DD(m) for m in range(m0 + 1, 2 * k + 1))
                       - sum((2 - F(m - N, k)) * (vs(m, k) + vs(m - 1, k - 1)) for m in range(m0 + 1, 2 * k + 1)))
                if rhs != T[m0]:
                    print("STAYFORM (na) FAIL", k, n, m0, float(rhs), float(T[m0]))
                    ok = False
            rhs = 4 - 2 * s(N + 1, k + 1) - s(N + 2, k + 1) + BdS + sum(om(m) * DD(m) for m in range(k + 1, 2 * k + 1)) - Stays
            assert rhs == T[k]
        if n <= 3 * k - 1:
            Theta = F(comb(n, k)) * k ** (k - 2) * A(n - k, k - 1)
            assert Theta == F(n, k) * A(n, k - 1) * u * A(N, k - 1) / A(N, k), ("Theta fail", k, n)
            BV = sum(F(comb(n, m + 1)) * p[n - 1 - m] * (b(m, k) + b(m, k - 1)) for m in range(2 * k + 1, n))
            assert A(n, k - 1) * Stem == sum(F(comb(n - 1, m)) * p[n - 1 - m] * (b(m, k) + b(m, k - 1))
                                             for m in range(2 * k + 1, n))
            assert A(n, k - 1) * Stem >= F(2 * k + 2, n) * BV
        if n == 3 * k:
            for m in range(k, 2 * k + 1):
                assert f(m) == 2 * ((k + 1) * c(m, k) - (k - 1) * c(m, k - 1))

    # ---- chain law checks (2.11 / 10.5 / old-8-28) ----
    def trans(y, q, qp):
        return borr(q - qp) * borr(y + qp) / borr(y + q)

    def paths(dd):
        res = [()]
        for L in range(1, dd):
            for combo in itertools.combinations(range(1, dd), L):
                res.append(tuple(sorted(combo, reverse=True)))
        return res

    def pathprob(y, dd, path):
        pr = F(1)
        cur = dd
        for q in path:
            pr *= trans(y, cur, q)
            cur = q
        stop = 1 - sum(trans(y, cur, qp) for qp in range(1, cur))
        return pr * stop, pr

    def Pi(y, path):
        r = F(1)
        for q in path:
            r *= F(y, y + q)
        return r

    for y in (k - 1, k, k + 1):
        if y < 2:
            continue
        for dd in range(1, y + 3):
            if y + dd - 1 > NMAX:
                continue
            val = sum(pathprob(y, dd, pa)[0] * Pi(y, pa) for pa in paths(dd))
            assert val == s(y + dd - 1, y), ("chain law fail", k, y, dd)
    y0 = k

    def hy(y, q):
        return borr(y + q) / borr(y0 + q)

    for dd in range(2, k + 2):
        m = k + dd - 1
        if m + 1 > NMAX:
            continue
        DDv = (k + 1) * s(m + 1, k + 1) - 2 * k * s(m, k) + (k - 1) * s(m - 1, k - 1)
        pths = paths(dd)
        sfr = {y: sum(pathprob(y0, dd, pa)[0] * Pi(y, pa) for pa in pths) for y in (y0 - 1, y0, y0 + 1)}
        frozen = (y0 + 1) * sfr[y0 + 1] - 2 * y0 * sfr[y0] + (y0 - 1) * sfr[y0 - 1]
        Res = DDv - frozen

        def G(y, q):
            tot = F(0)
            for pa in pths:
                if pa and pa[-1] == q:  # distinct prefixes ending at q
                    tot += pathprob(y0, dd, pa)[1] * Pi(y, pa)
            return tot

        for y in (y0 - 1, y0 + 1):
            lhs = s(y + dd - 1, y) - sfr[y]
            rhs = -sum(F(q, y) * G(y, q) * (hy(y, q) / hy(y, dd) - 1) for q in range(1, dd))
            assert lhs == rhs, ("old-8-18 first fail", k, dd, y)
        einc_p = {q: eg(y0 + q) / eg(y0 + dd) for q in range(1, dd)}
        einc_m = {q: eg(y0 - 1 + dd) / eg(y0 - 1 + q) for q in range(1, dd)}
        rhs2 = sum(q * (G(y0 + 1, q) * (1 - einc_p[q]) - G(y0 - 1, q) * (einc_m[q] - 1)) for q in range(1, dd))
        assert Res == rhs2, ("old-8-18 second fail", k, dd)
        assert frozen >= 0, ("frozen convexity fail", k, dd)
        for pa in pths:
            for j in range(1, len(pa) + 1):
                pre = pa[:j]
                Aj = sum(F(q, y0 + 1 + q) for q in pre)
                assert Pi(y0 + 1, pre) / Pi(y0 - 1, pre) >= 1 + 2 * Aj / (y0 - 1)
    y = k + 1
    for q0 in range(1, k + 2):
        if k + q0 > NMAX:
            continue
        lhs = c(k + q0, k)
        tot = F(0)
        for pa in paths(q0):
            pr_stop, pr_pref = pathprob(y, q0, pa)
            qL = pa[-1] if pa else q0
            pich = borr(y) * borr(qL) / borr(y + qL)
            L = len(pa)
            stop = pr_stop / pr_pref
            assert stop >= pich
            tot += pr_pref * Pi(y, pa) * (pich * (1 - (1 - F(1, y)) ** (L + 1)) + (stop - pich) * (1 - (1 - F(1, y)) ** L))
        assert tot == lhs, ("old-8-28 fail", k, q0, float(tot), float(lhs))
    return ok


if __name__ == "__main__":
    allok = True
    for k in range(2, 7):
        r = run(k)
        allok = allok and r
        print("k=", k, "ok" if r else "FAIL")
    print("ALL OK" if allok else "SOME FAIL")
