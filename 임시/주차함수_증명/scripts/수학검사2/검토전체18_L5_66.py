# 6.6 검산: 상수들, (6.50) 열세 값, Low·O 값, (6.49), theorem-D 상수, 정확 항등식 (6.45)·path-shift (가)(나), (6.47)·Low의 작은 범위 확인
from fractions import Fraction as Fr
from math import comb, factorial
from mpmath import mp, mpf, sqrt, exp, log, e, pi
mp.dps = 25
c = 1 / sqrt(2 * pi)


def Bor(n):
    n = mpf(n)
    return exp(-n) * n ** (n - 1) / mp.factorial(n)


def Ren(n):
    return n * Bor(n)


def Psi(d):
    return sum(Ren(j) for j in range(1, d + 1))


print("Psi(14)/(2e)=", Psi(14) / (2 * e))
k = mpf(3131)
f1 = sqrt(2 * pi) * mpf(3146) ** 1.5 * Bor(3146)
f2 = (k / (k + 15)) ** 1.5
f3 = (k + 1) / (k + 14)
print("Fr factor k=3131:", f1 * f2 * f3, " *Psi(14)/2e=", f1 * f2 * f3 * Psi(14) / (2 * e))
gW = 2 * exp(mpf("0.0031")) / e
print("gamma_W=", gW)


def ups(k):
    k = mpf(k)
    return mpf(1) / 2 + 5 / (2 * k) + 1 / (4 * k * k)


def u(k):
    k = mpf(k)
    return 3 / mpf("0.35") * (mpf("1.35") + 1 / k) * (mpf("0.65") - 1 / k) ** (-mpf(3) / 2) * k ** (-mpf(1) / 2)


print("ups*gW 3131:", ups(3131) * gW, " u/(e 2^1.5) 3131:", u(3131) / (e * 2 ** mpf(1.5)))


def dfrak(k):
    return gW * ups(k) + u(k) / (e * 2 ** mpf(1.5))


print("d(3131)=", dfrak(3131), " d(10001)=", dfrak(10001))
print("0.0648 e 2^1.5=", mpf("0.0648") * e * 2 ** mpf(1.5), " 0.3951/(e2^1.5)=", mpf("0.3951") / (e * 2 ** mpf(1.5)))


def Low(k, rho):
    k = mpf(k)
    rho = mpf(rho)
    eps = k ** (-mpf(1) / 3)
    br = 2 * sqrt(rho) - mpf("2.218") * eps
    return c * k ** (mpf(1) / 3) * br / (1 + rho * eps) * exp(-1 / (12 * (k + 1))) * exp(-rho ** 2 * (1 + rho * eps) ** 1.5 * exp(1 / (4 * (k + 1))) / (c * br))


print("Low(10001,1.4)=", Low(10001, mpf("1.4")), " Low(3131,0.75)=", Low(3131, mpf("0.75")))


def Obar(k, x):
    k = mpf(k)
    return dfrak(k) * exp(1 + 1 / (12 * k)) * (1 + x) ** 1.5


print("Obar k=10001 (1.4k^-1/3+1/k):", Obar(10001, mpf("1.4") * mpf(10001) ** (-mpf(1) / 3) + 1 / mpf(10001)))
print("Obar k=3131 (0.75k^-1/3+1/k):", Obar(3131, mpf("0.75") * mpf(3131) ** (-mpf(1) / 3) + 1 / mpf(3131)))


def wp(m):
    m = mpf(m)
    return mpf("1.99") + mpf("0.59963") * (m + 1) ** (mpf(2) / 3) + mpf("1.24847") * (m + 1) ** (mpf(1) / 3)


uu = mpf(3131) ** (mpf(1) / 3)
print("u=k^(1/3)=", uu, " quad=", mpf("0.15037") * uu ** 2 - mpf("1.54829") * uu - mpf("1.3314"))
print("(6.49) diff:", mpf("0.75") * mpf(3131) ** (mpf(2) / 3) - (wp(3131 + mpf("0.75") * mpf(3131) ** (mpf(2) / 3)) - 1))
print("wp deriv at 1=", mpf(2) / 3 * mpf("0.59963") * 2 ** (-mpf(1) / 3) + mpf(1) / 3 * mpf("1.24847") * 2 ** (-mpf(2) / 3))
print("0.39976/u+0.41616/u^2=", mpf("0.39976") / uu + mpf("0.41616") / uu ** 2)
print("roots of quad:", (mpf("1.54829") + sqrt(mpf("1.54829") ** 2 + 4 * mpf("0.15037") * mpf("1.3314"))) / (2 * mpf("0.15037")))
m = mpf(701)
print("0.0563:", m ** (mpf(2) / 3) / (2 * m), " kfrak max:", (m ** (mpf(2) / 3) / 2) ** 1.5 / (m - m ** (mpf(2) / 3) / 2), " 0.161 check:", mpf("1.1212") * m ** (-mpf(2) / 3) + mpf("1.3036") * m ** (-mpf(1) / 3), " 0.025 m^-2/3:", mpf("0.025") * m ** (-mpf(2) / 3))
print("1.4963,2.4604:", mpf("0.09") * 1.5 * mpf("0.7979") + (1 + mpf("0.09") / 701) * mpf("1.74") * mpf("0.7979"), (1 + mpf("0.09") / 701) * mpf("3.28") * 1.5 / 2)
print("1.1212, 1.3036 coefs:", mpf("1.4963") / (sqrt(2) * mpf("0.9437")), mpf("2.4604") / (2 * mpf("0.9437")))
print("bracket lower:", mpf("0.99987") * (1 - 0.5 - mpf("0.2991")) - mpf("0.7979") * 0.5 * mpf("0.3747"))
print("(4/3)^1.5=", (mpf(4) / 3) ** 1.5, " 1+1.732/3=", 1 + mpf("1.732") / 3)
print("max f(D):", max(((1 - D) * (1 + mpf("0.7183") * D) / (2 - D), D) for D in [mpf(i) / 1000 for i in range(0, 1001)]))
print("(e+3/4)/3131=", (e + mpf(3) / 4) / 3131, " 6.03/3131=", mpf("6.03") / 3131, " 0.5006*k*(3.469/k)^2 k=3131:", mpf("0.5006") * 3469 ** 2 / 1000 ** 2 / 3131)
k = 3131
for d in range(1, 14):
    L = (k - 1) * (e * Ren(d + 1) - mpf(60) * (d + 1) / (k + d))
    R = 2 * (1 + sum(e * Ren(r + 1) + mpf(60) * (r + 1) / (k + d) for r in range(1, d)))
    print("d=", d, " L=", mp.nstr(L, 6), " R=", mp.nstr(R, 5))


def g(x):
    x = mpf(x)
    return (x - 1) * log(1 + 1 / x)


print("1-g bound ok n=3..50:", all(1 - g(n) <= mpf(3) / (2 * n) - mpf(5) / (6 * n * n) + mpf(7) / (12 * n ** 3) for n in range(3, 51)))
print("ratio>=1 n=3..50:", all(((n + 1) / mpf(n)) ** 1.5 * exp(g(n) - 1) >= 1 for n in range(3, 51)))

NMAX = 120
A = [[0] * (NMAX + 1) for _ in range(NMAX + 1)]
for l in range(NMAX + 1):
    A[0][l] = 1
for n in range(1, NMAX + 1):
    for l in range(NMAX + 1):
        A[n][l] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l] for j in range(n))
p = [(n + 1) ** (n - 1) if n > 0 else 1 for n in range(NMAX + 1)]


def s(m, yc):
    return Fr(A[m][yc - 1], p[m]) if yc >= 1 else Fr(0)


def cc(m, Y):
    return s(m, Y + 1) - s(m, Y) if Y >= 0 else Fr(0)


def pim(m, j):
    a = j
    bb = m + 1 - j
    return Fr(a ** (a - 1) * bb ** (bb - 1) * comb(a + bb, a), (a + bb) ** (a + bb - 1))


def Pm(m, j):
    return Fr(j, m) * pim(m, j)


bad = []
for m in range(1, 61):
    for d in range(1, (m + 1) // 2 + 1):
        rhs = Fr(0)
        for J in range(0, d):
            sz = m - J - 1
            sv = s(sz, m - d + 1) if sz > 0 else Fr(1)
            cv = cc(sz, m - d) if sz > m - d else Fr(0)
            rhs += pim(m, J + 1) / m * (sv + (m - d) * cv)
        for Q in range(1, min(d - 1, m - d) + 1):
            rhs += Pm(m, Q) * (cc(m - Q, m - d) if m - Q > m - d else Fr(0))
        if rhs != cc(m, m - d):
            bad.append((m, d))
print("(6.45) exact failures m<=60:", bad[:5], len(bad))

lo, hi = mpf(10), mpf(0)
for m in range(4, 121):
    for d in range(1, int(mpf(m) ** (mpf(2) / 3) / 2) + 1):
        q = cc(m, m - d)
        r = m * mpf(q.numerator) / mpf(q.denominator) / Psi(d)
        lo = min(lo, r)
        hi = max(hi, r)
print("ratio m c/Psi range m=4..120:", lo, hi)


def forests_le(N, y):
    f = [Fr(0)] * (N + 1)
    f[0] = Fr(1)
    for n in range(1, N + 1):
        f[n] = sum(Fr(comb(n - 1, t - 1) * t ** (t - 1)) * f[n - t] for t in range(1, min(y, n) + 1))
    return f[N]


def pi0(N, y):
    return forests_le(N, y) / p[N] if N > 0 else Fr(1)


def borr(n):
    return Fr(n ** (n - 1), factorial(n))


badA = []
badB = []
for k in range(5, 10):
    for n in range(k + 1, 2 * k + 1):
        tot = Fr(0)
        first = Fr(0)
        stack = [(n, [])]
        while stack:
            prev, path = stack.pop()
            for S in range(k, prev):
                newp = path + [S]
                L = len(newp)
                seq = [n] + newp
                w = Fr(1)
                for i in range(L):
                    w *= borr(seq[i] - seq[i + 1])
                w *= borr(S) * pi0(S - 1, k - 1) * Fr(k ** L - (k - 1) ** L)
                for Sj in newp:
                    w /= Sj
                tot += w
                Phi1 = Fr(k + 1) * (borr(S + 1) / borr(S)) * (pi0(S, k) / pi0(S - 1, k - 1)) * Fr((k + 1) ** L - k ** L, k ** L - (k - 1) ** L)
                for Sj in newp:
                    Phi1 *= Fr(Sj, Sj + 1)
                first += w * Phi1
                stack.append((S, newp))
        if tot != borr(n) * cc(n - 1, k - 1):
            badA.append((k, n))
        if first != (k + 1) * borr(n + 1) * cc(n, k):
            badB.append((k, n))
print("path-shift (ga) failures:", badA, " (na) failures:", badB)


def theta(t, kk):
    if t > kk:
        return Fr(comb(t, kk) * kk ** (kk - 1) * (t - kk) ** (t - kk), t ** (t - 1))
    return Fr(1) if t == kk else Fr(0)


viol = []
for m in range(2, 50):
    for d in range(1, (m + 1) // 2 + 1):
        mu1 = sum(theta(m + 1, m + 1 - j) for j in range(1, d + 1))
        mu2 = mu1 + 2 * sum(theta(m + 1, m + 1 - j) * theta(m + 1 - j, m + 1 - jp) for j in range(1, d + 1) for jp in range(j + 1, d + 1))
        q = cc(m, m - d)
        lhs = mpf(q.numerator) / mpf(q.denominator)
        ex = mu2 / mu1 - 1
        rhs = mpf(mu1.numerator) / mpf(mu1.denominator) / m * (1 - mpf(d) / m) ** (mpf(ex.numerator) / mpf(ex.denominator))
        if lhs < rhs * (1 - mpf(10) ** -15):
            viol.append((m, d))
print("(6.47) violations m<50:", viol)

viol = []
for kk in range(1, 56):
    for d in range(2, 200):
        m = kk + d
        if m > NMAX or d > (m + 1) / 2:
            break
        q = cc(m, kk)
        lhs = (kk + 1) * mpf(q.numerator) / mpf(q.denominator)
        rho = mpf(d) / mpf(kk) ** (mpf(2) / 3)
        if lhs < Low(kk, rho):
            viol.append((kk, d, float(lhs), float(Low(kk, rho))))
print("lemma-Hprime violations:", viol[:5], len(viol))
