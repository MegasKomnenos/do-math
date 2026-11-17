# 검토전체24 R7a: 7.4-7.5절 항등식의 작은 크기 전수 검사
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial
import sympy as sp


def caps(sig):
    n = len(sig)
    h = []
    for i in range(n):
        z = 0
        for j in range(i - 1, -1, -1):
            if sig[j] > sig[i]:
                z = j + 1
                break
        h.append(i + 1 - z)
    return h


def A_table(N, maxl):
    # A[n][l+1] = A_{n,l}, l = 0..maxl
    A = [[0] * (maxl + 2) for _ in range(N + 1)]
    for l in range(0, maxl + 1):
        A[0][l + 1] = 1
    for n in range(1, N + 1):
        for l in range(0, maxl + 1):
            A[n][l + 1] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j][l + 1] * A[n - 1 - j][l + 1] for j in range(n))
    return A


def pcount(m):
    return (m + 1) ** (m - 1) if m > 0 else 1


print("== (1) 재귀와 순열 전수의 일치, 모멘트 재귀 (7.1)(7.2), 뿌리 자리 법칙")
N = 8
A = A_table(N + 2, N + 3)


def Aget(n, l):
    return A[n][l + 1]


ok = True
for k in range(2, 5):
    stats = {}
    for n in range(0, N + 1):
        tot = 0
        EZ = 0
        EH = 0
        EZZ = 0
        pos = [0] * (n + 2)
        for sig in permutations(range(1, n + 1)):
            h = caps(sig)
            w = 1
            for xx in h:
                w *= min(xx, k)
            Z = sum(1 for xx in h if xx > k)
            H = sum(1 for xx in h if xx == k)
            tot += w
            EZ += w * Z
            EH += w * H
            EZZ += w * Z * (Z - 1)
            if n > 0:
                pos[sig.index(n) + 1] += w
        assert tot == Aget(n, k - 1), (n, k)
        stats[n] = (F(EZ, tot), F(EH, tot), F(EZZ, tot), [F(pp, tot) for pp in pos])
    an = lambda m: F(Aget(m, k - 1), factorial(m))
    s = lambda m: F(Aget(m, k - 1), pcount(m))
    Zf = lambda m: stats[m][0]
    Zh = lambda m: stats[m][1]
    Zz = lambda m: stats[m][2]
    for n in range(1, N + 1):
        assert n * an(n) == sum(min(j, k) * an(j - 1) * an(n - j) for j in range(1, n + 1))
        P = [None] + [F(min(j, k) * comb(n - 1, j - 1) * Aget(j - 1, k - 1) * Aget(n - j, k - 1), Aget(n, k - 1)) for j in range(1, n + 1)]
        assert all(P[j] == stats[n][3][j] for j in range(1, n + 1))
        assert all(P[j] == min(j, k) * an(j - 1) * an(n - j) / (n * an(n)) for j in range(1, n + 1))
        r1 = sum(P[j] * ((1 if j > k else 0) + Zf(j - 1) + Zf(n - j)) for j in range(1, n + 1))
        r2 = sum(P[j] * ((1 if j == k else 0) + Zh(j - 1) + Zh(n - j)) for j in range(1, n + 1))
        r3 = sum(P[j] * (Zz(j - 1) + Zz(n - j) + 2 * Zf(j - 1) * Zf(n - j) + 2 * (1 if j > k else 0) * (Zf(j - 1) + Zf(n - j))) for j in range(1, n + 1))
        if not (r1 == Zf(n) and r2 == Zh(n) and r3 == Zz(n)):
            ok = False
            print("FAIL", n, k)
        if n <= k:
            assert Zf(n) == 0
        if n < k:
            assert Zh(n) == 0
        if n <= k + 1:
            assert Zz(n) == 0
        for j in range(1, n + 1):
            Pm = F(j * comb(n - 1, j - 1) * pcount(j - 1) * pcount(n - j), pcount(n))
            assert P[j] == F(min(j, k), j) * Pm * s(j - 1) * s(n - j) / s(n)
print("모멘트 재귀·뿌리 자리 법칙·2.8절 관계:", ok)

print("== (2) 한 걸음 항등식 (7.10), mu_k(k)")
N2 = 40
for k in range(2, 9):
    A2 = A_table(N2, k + 1)
    Ag = lambda n, l: A2[n][l + 1]
    b = lambda n, l: Ag(n, l) - (Ag(n, l - 1) if l >= 1 else 0)

    def clp(m):
        return F(b(m, k), Ag(m, k - 1))

    def clm(m):
        return F(b(m, k - 1), Ag(m, k - 1))

    def mu(m):
        return clp(m) - clm(m)

    def P(m, j):
        return F(min(j, k) * comb(m - 1, j - 1) * Ag(j - 1, k - 1) * Ag(m - j, k - 1), Ag(m, k - 1))

    def chi(m, j):
        hv = 1 if j > k else 0
        v = F(0)
        if j == k:
            v -= F(1, k) * (1 - clm(m - k))
        v += F(hv, k) * (clp(j - 1) + clm(j - 1) + clp(m - j) + clm(m - j))
        v += (1 + F(hv, k)) * clp(j - 1) * clp(m - j) + (1 - F(hv, k)) * clm(j - 1) * clm(m - j)
        return v

    def src(m):
        return sum(P(m, j) * chi(m, j) for j in range(1, m + 1))

    for m in range(1, N2 + 1):
        lhs = mu(m)
        rhs = src(m) + sum(P(m, j) * (mu(j - 1) + mu(m - j)) for j in range(1, m + 1))
        assert lhs == rhs, (k, m)
        if m <= k - 1:
            assert mu(m) == 0 and src(m) == 0 and clp(m) == 0 and clm(m) == 0
    assert clp(k) == 0
    assert mu(k) == -F(pcount(k - 1), pcount(k))
print("한 걸음 항등식 k=2..8, m<=40: OK")

print("== (3) 7.4 생성함수: (7.3)(7.4), Neumann, pd 값, (7.6), POS^G, Green 원자, (7.5)")
z, x, eta = sp.symbols("z x eta")


def run(k, N):
    def wg(t):
        return sp.Integer(t) if t < k else (eta if t == k else z)

    K2 = [sp.Integer(1)]
    for n in range(1, N + 1):
        K2.append(sp.expand(sum(comb(n - 1, j) * wg(j + 1) * K2[j] * K2[n - 1 - j] for j in range(n))))
    Kn = [sp.expand(e.subs(eta, k)) for e in K2]
    Jn = [sp.expand(sp.diff(e, eta).subs(eta, k)) for e in K2]

    def ser(coefs):
        return sum(c * x ** i / factorial(i) for i, c in enumerate(coefs))

    def trunc(e):
        e = sp.expand(e)
        return sum(e.coeff(x, i) * x ** i for i in range(N + 1))

    def sexp(e):
        r = sp.Integer(1)
        term = sp.Integer(1)
        for i in range(1, N + 1):
            term = trunc(term * e) / i
            r += term
        return trunc(r)

    T = ser([0] + [t ** (t - 1) for t in range(1, N + 1)])
    Tle = ser([0] + [t ** (t - 1) if t <= k else 0 for t in range(1, N + 1)])
    Tgt = sp.expand(T - Tle)
    eT = ser([pcount(m) for m in range(N + 1)])
    Elt = ser([pcount(m) if m < k else 0 for m in range(N + 1)])
    Kser = ser(Kn)
    Gr = trunc(T - T ** 2 / 2)
    sm = trunc((1 - T) * (eT - Elt))
    intg = lambda e: sp.integrate(sp.expand(e), x)
    Gstar = trunc(Elt + sm + z * trunc(eT * sexp(z * Gr)) * intg(trunc(sm * sexp(-z * Gr))))
    X = sp.expand(Kser - Gstar)
    pd = trunc(sp.expand(z * intg(Kser - Elt) - Tgt))
    for t in range(1, N + 1):
        c = sp.expand(pd.coeff(x, t) * factorial(t))
        want = 0 if t <= k else sp.expand(z * Kn[t - 1] - t ** (t - 1))
        assert sp.expand(c - want) == 0, (k, t)
    assert sp.expand(trunc(sexp(Tle + z * intg(Kser - Elt))) - Kser) == 0
    nz = [i for i in range(N + 1) if sp.expand(X.coeff(x, i)) != 0]
    lowest = min(nz) if nz else None
    R = sp.expand(X - trunc(sexp(Tle) * (z * intg(X) + pd ** 2 / 2)))
    M = min(N, 3 * k + 2)
    assert all(sp.expand(R.coeff(x, i)) == 0 for i in range(M + 1)), k
    viol = [i for i in range(M + 1, N + 1) if sp.expand(R.coeff(x, i)) != 0]
    A3 = A_table(N, k + 1)
    Ag = lambda n, l: A3[n][l + 1]
    eTGr = trunc(eT * sexp((k - 1) * Gr))
    JGser = trunc(eTGr * intg(trunc(sexp(-(k - 1) * Gr) * x ** (k - 1) / factorial(k - 1))))
    strict = []
    for n in range(N + 1):
        Kpp = sp.diff(Kn[n], z, 2).subs(z, k)
        POS = sp.diff(Gstar.coeff(x, n), z, 2).subs(z, k) * factorial(n)
        Xpp = sp.diff(X.coeff(x, n), z, 2).subs(z, k) * factorial(n)
        assert sp.simplify(Kpp - POS - Xpp) == 0
        if n <= 2 * k + 1:
            assert Xpp == 0
        if n >= 1 and k <= n:
            jg = pcount(k - 1) * factorial(n) * JGser.coeff(x, n)
            jn = Jn[n].subs(z, k - 1)
            assert jn <= jg, (k, n)
            if n <= 2 * k:
                assert jn == jg, (k, n)
            else:
                strict.append((n, jn < jg))
            d = Ag(n, k) - 2 * Ag(n, k - 1) + Ag(n, k - 2)
            assert d >= Kpp - jg, (k, n, d, Kpp, jg)
    ZF = {}
    ZZ = {}
    for m in range(N + 1):
        a = Ag(m, k - 1)
        ZF[m] = sp.Rational(k) * sp.diff(Kn[m], z).subs(z, k) / a
        ZZ[m] = sp.Rational(k) ** 2 * sp.diff(Kn[m], z, 2).subs(z, k) / a

    def ex(t):
        return sp.Rational(t * pcount(t - 1), Ag(t - 1, k - 1)) - k

    def pdv(t, o):
        if t <= k:
            return sp.Integer(0)
        e = sp.expand(z * Kn[t - 1] - t ** (t - 1))
        return sp.diff(e, z, o).subs(z, k) if o > 0 else e.subs(z, k)

    for t in range(k + 1, N + 1):
        a = Ag(t - 1, k - 1)
        assert pdv(t, 0) == -a * ex(t)
        assert pdv(t, 1) == a * (1 + ZF[t - 1])
        assert sp.simplify(pdv(t, 2) - sp.Rational(a, k) * (2 * ZF[t - 1] + ZZ[t - 1])) == 0

    def ps(j, t, tp):
        return (sp.Rational(j * (j - 1), 2 * k * k) * pdv(t, 0) * pdv(tp, 0)
                + sp.Rational(j, k) * (pdv(t, 0) * pdv(tp, 1) + pdv(t, 1) * pdv(tp, 0))
                + pdv(t, 1) * pdv(tp, 1)
                + sp.Rational(1, 2) * (pdv(t, 0) * pdv(tp, 2) + pdv(t, 2) * pdv(tp, 0)))

    def ps76(j, t, tp):
        a = Ag(t - 1, k - 1)
        ap = Ag(tp - 1, k - 1)
        return a * ap * ((1 + ZF[t - 1]) * (1 + ZF[tp - 1]) + sp.Rational(j * (j - 1), 2 * k * k) * ex(t) * ex(tp)
                         - sp.Rational(j, k) * (ex(t) * (1 + ZF[tp - 1]) + ex(tp) * (1 + ZF[t - 1]))
                         - sp.Rational(1, 2 * k) * (ex(t) * (2 * ZF[tp - 1] + ZZ[tp - 1]) + ex(tp) * (2 * ZF[t - 1] + ZZ[t - 1])))

    for j in range(0, 4):
        for t in range(k + 1, min(N, 2 * k + 4)):
            for tp in range(k + 1, min(N, 2 * k + 4)):
                assert sp.simplify(ps(j, t, tp) - ps76(j, t, tp)) == 0
    eTle = sexp(Tle)
    Neu = lambda f: trunc(eTle * intg(f))
    tot = sp.Integer(0)
    for j in range(0, N):
        Q = sum(sum(comb(m, t) * ps(j, t, m - t) for t in range(k + 1, m - k)) * x ** m / factorial(m) for m in range(2 * k + 2, N + 1))
        term = trunc(eTle * Q)
        for _ in range(j):
            term = Neu(term)
        tot += sp.Integer(k) ** j * term
    tot = sp.expand(tot)
    for n in range(0, M + 1):
        Xpp = sp.diff(X.coeff(x, n), z, 2).subs(z, k)
        assert sp.simplify(tot.coeff(x, n) - Xpp) == 0, (k, n)
    for t in range(k + 1, N + 1):
        q = t - k
        assert sp.Poly(Kn[t - 1], z).degree() <= q - 1
        s = sp.Rational(Ag(t - 1, k - 1), pcount(t - 1))
        assert ex(t) == q + (k + q) * (1 - s) / s and ex(t) >= q
    print('  n>2k에서 J_n(k-1) < J^G_n(k-1) 엄격 여부:', strict)
    return lowest, viol


for k, N in [(2, 9), (3, 12)]:
    print("k=", k, "N=", N, " 잔차 최저 차수 / (7.4)가 깨지는 차수(3k+3 이상):", run(k, N))
print("생성함수 항등식 OK")
