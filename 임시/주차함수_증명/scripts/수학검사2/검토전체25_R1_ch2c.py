# R1 검산: 2장 2.6(g), 2.8-2.12 부등식·항등식 수치 대조
import math
from fractions import Fraction as Fr
from math import comb, factorial, log, exp, sqrt, pi as PI


def p(n):
    return 1 if n == 0 else (n + 1) ** (n - 1)


def Atab(N):
    A = {}
    for l in range(-1, N + 2):
        A[(0, l)] = 1 if l >= 0 else 0
        for n in range(1, N + 1):
            A[(n, l)] = 0 if l < 0 else sum(
                comb(n - 1, j) * min(j + 1, l + 1) * A[(j, l)] * A[(n - 1 - j, l)] for j in range(n))
    return A


N = 60
A = Atab(N)


def b(n, l):
    return 0 if l < 0 else A[(n, l)] - A[(n, l - 1)]


def d(n, k):
    return b(n, k) - b(n, k - 1)


def s(m, y):
    return Fr(A[(m, y - 1)], p(m)) if y >= 1 else Fr(0)


def c(m, Y):
    return Fr(b(m, Y), p(m))


def Bor(m):
    return exp(-m + (m - 1) * log(m) - math.lgamma(m + 1))


def Ren(j):
    return 1.0 if j == 0 else j * Bor(j)


def g(x):
    return (x - 1) * log(1 + 1 / x)


# lemma g
for x in [1, 1.5, 2, 3, 10, 100, 1e4]:
    gp = log(1 + 1 / x) - (x - 1) / (x * (x + 1))
    assert gp >= (3 * x + 1) / ((2 * x + 1) * x * (x + 1)) - 1e-15 and gp <= 3 / (2 * x * x) + 1e-15
    assert 1 - 3 / (2 * x) + 1 / (2 * x * x) - 1e-12 <= g(x) <= 1 - 3 / (2 * x) + 5 / (6 * x * x) + 1e-12
for x in [0.2, 0.25, 0.5, 0.9]:
    gp = log(1 + 1 / x) - (x - 1) / (x * (x + 1))
    assert gp <= 3 / (2 * x * x) + 1e-12
for m in range(1, 200):
    assert abs(Bor(m + 1) / Bor(m) - exp(g(m) - 1)) < 1e-12
print("g ok")


# P_m(j), lemma 2-32, 2-33
def P(m, j):
    return Fr(j * comb(m - 1, j - 1) * p(j - 1) * p(m - j), p(m))


for m in range(1, 40):
    assert sum(P(m, j) for j in range(1, m + 1)) == 1
    for rho in range(0, m):
        closed = Fr(comb(m - 1, rho) * (m - rho) ** (m - rho - 1) * p(rho), (m + 1) ** (m - 1))
        assert P(m, m - rho) == closed
        assert P(m + 1, m + 1 - rho) <= P(m, m - rho) and float(P(m, m - rho)) >= Bor(rho + 1) - 1e-15
    for j in range(1, m + 1):
        assert (m + 1) * P(m + 1, j) <= m * P(m, j)

    def F(mm, x):
        return sum(P(mm, j) for j in range(1, min(x, mm) + 1))
    for x in range(0, m + 1):
        assert F(m + 1, x) <= F(m, x) <= F(m + 1, x + 1)
print("2-32, 2-33 ok")

# level visit conservation
for Y in range(1, 20):
    for K in range(Y + 1, N - 1):
        lhs = sum(c(m, Y) for m in range(Y + 1, K + 1))
        assert lhs == 1 - s(K, Y) + sum(s(m, Y + 1) - s(m - 1, Y) for m in range(Y + 1, K + 1))

        def om(m):
            return Fr(1, m)
        l2 = sum(om(m) * c(m, Y) for m in range(Y + 1, K + 1))
        r2 = om(K) * (1 - s(K, Y)) + sum((om(m) - om(m + 1)) * (1 - s(m, Y)) for m in range(Y + 1, K))
        assert l2 - sum(om(m) * (s(m, Y + 1) - s(m - 1, Y)) for m in range(Y + 1, K + 1)) == r2 and l2 >= r2
print("level visit ok")


# tree curvature, b-top, theorem 2-38
def sT(t, y):
    return Fr(min(t, y) * A[(t - 1, y - 1)], t ** (t - 1)) if y >= 1 else Fr(0)


def xcur(t, y):
    return sT(t, y + 1) - 2 * sT(t, y) + sT(t, y - 1)


def theta(t, k):
    return Fr(comb(t, k) * k ** (k - 1) * (t - k) ** (t - k), t ** (t - 1))


for k in range(2, 25):
    for t in range(1, N):
        x = xcur(t, k)
        if t >= k + 1:
            assert x == Fr(1, t) * ((k + 1) * c(t - 1, k) - (k - 1) * c(t - 1, k - 1))
        elif t == k:
            assert x == Fr(-1, k)
        else:
            assert x == 0
        if t >= k:
            assert k * x >= -theta(t, k)
        bTk = min(t, k + 1) * A[(t - 1, k)] - min(t, k) * A[(t - 1, k - 1)]
        bTk1 = min(t, k) * A[(t - 1, k - 1)] - min(t, k - 1) * A[(t - 1, k - 2)]
        dl = bTk - bTk1
        assert dl == t ** (t - 1) * x
        if t >= k + 1:
            assert bTk == A[(t - 1, k)] + k * b(t - 1, k)
            assert dl == k * d(t - 1, k) + b(t - 1, k) + b(t - 1, k - 1) == (k + 1) * b(t - 1, k) - (k - 1) * b(t - 1, k - 1)
        if t == k + 1:
            assert dl == -(k - 1) * k ** (k - 2)
        if t == k:
            assert bTk1 == b(k, k - 1) == p(k - 1) == k ** (k - 2) and dl == -k ** (k - 2)
print("curvature, b-top, 2-38 ok")

# tree expansion truncations
for k in range(2, 12):
    def bT(t, l):
        return min(t, l + 1) * A[(t - 1, l)] - min(t, l) * A[(t - 1, l - 1)] if l >= 0 else 0
    for n in range(1, 31):
        if n <= 2 * k + 1:
            assert b(n, k) == sum(comb(n, t) * bT(t, k) * A[(n - t, k - 1)] for t in range(1, n + 1))
        if n <= 2 * k - 1:
            assert b(n, k - 1) == sum(comb(n, t) * bT(t, k - 1) * A[(n - t, k - 1)] for t in range(1, n + 1))
        first = sum(comb(n, t) * (bT(t, k) - bT(t, k - 1)) * A[(n - t, k - 1)] for t in range(k, n + 1))
        assert d(n, k) >= first
        if n <= 2 * k - 1:
            assert d(n, k) == first
print("tree expansion truncations ok")

# renewal lemma
Psi = [0.0]
for j in range(1, 3000):
    Psi.append(Psi[-1] + Ren(j))
for j in range(1, 60):
    assert abs(Ren(j) - (Bor(j) + sum(Bor(m) * Ren(j - m) for m in range(1, j)))) < 1e-13
for q in range(1, 60):
    assert abs(sum(Bor(m) * Psi[q - m] for m in range(1, q + 1)) - (Psi[q] - sum(Bor(m) for m in range(1, q + 1)))) < 1e-12
z12, zm12, z32 = -1.4603545088095868, -0.2078862249773546, 2.6123753486854883
cPsi = -z12 + z32 / 12
print("c_Psi=", cPsi, "interval bounds:", 1.46035 + 2.61237 / 12, 1.46036 + 2.61238 / 12)
for q in range(1, 2000):
    assert Psi[q] <= (2 * PI) ** -0.5 * (2 * sqrt(q) - 1) + 1e-12
    low = (2 * PI) ** -0.5 * (2 * sqrt(q) - cPsi + 0.5 / sqrt(q) - q ** -1.5 / 24)
    assert Psi[q] >= low - 1e-12 and low > 0
    if q < 300:
        S1 = sum(j ** -0.5 for j in range(1, q + 1))
        assert 2 * sqrt(q) + z12 + 0.5 * q ** -0.5 - q ** -1.5 / 24 - 1e-11 <= S1 <= 2 * sqrt(q) + z12 + 0.5 * q ** -0.5 + 1e-11
        S2 = sum(j ** 0.5 for j in range(1, q + 1))
        assert 2 / 3 * q ** 1.5 + 0.5 * q ** 0.5 + zm12 - 1e-9 <= S2 <= 2 / 3 * q ** 1.5 + 0.5 * q ** 0.5 + zm12 + q ** -0.5 / 24 + 1e-9
for q in range(0, 300):
    tl = 1 - sum(Bor(m) for m in range(1, q + 1))
    assert 2 * (2 * PI) ** -0.5 * exp(-1 / (12 * (q + 1))) * (q + 1) ** -0.5 - 1e-12 <= tl <= 2 * (2 * PI) ** -0.5 * (q + 0.5) ** -0.5 + 1e-12
for m in range(1, 100):
    for m2 in range(m + 1, 120):
        assert 1 < Bor(m) / Bor(m2) <= (m2 / m) ** 1.5
print("borel arithmetic, power sums ok; 2(2pi)^-1/2=", 2 * (2 * PI) ** -0.5)

for n in range(2, N):
    for y in range(1, n):
        q = n - y
        u1 = ((n + 1) / (y + 1)) ** 1.5 / (y + 1) * sum(Psi[i] for i in range(1, q + 1))
        u2 = (2 * PI) ** -0.5 * ((n + 1) / (y + 1)) ** 1.5 / (y + 1) * (4 / 3 * q ** 1.5 + sqrt(q) - q - 1 / 3)
        assert float(1 - s(n, y)) <= u1 + 1e-12 <= u2 + 2e-12
print("union-bound-closed ok")

for y in range(2, 25):
    for q in range(1, y + 3):
        m = y + q - 1
        if m > N:
            continue
        phi1 = 1 - sum(Bor(j) * (q - j) / (y + q - j) for j in range(1, q))
        assert float(s(m, y)) <= phi1 + 1e-12 and 0 < phi1 <= 1
print("supersolution phi_1 ok")


def nf(n, dd):
    return exp(dd + math.lgamma(n + 1) - math.lgamma(n - dd + 1) + (n - dd - 2) * log(n - dd) - (n - 2) * log(n))


for n in range(3, N + 1):
    for r in range(1, (n - 1) // 2 + 1):
        Q1 = comb(n, r) * (n - r) ** (n - r - 2) * (r + 1) ** r
        diff = b(n, n - r - 1) - b(n, n - r)
        assert diff <= Q1 and diff == -d(n, n - r)

        def W(g1, g2):
            t1 = n + 1 - g1
            t2 = t1 - g2
            return Fr(p(n)) * Fr(t2 ** (t2 - 1), factorial(t2)) * Fr(g1 ** g1, factorial(g1)) * Fr(g2 ** g2, factorial(g2)) / Fr((n + 1) ** n, factorial(n + 1))
        Q2 = Fr(0)
        for g1 in range(1, r + 1):
            for g2 in range(1, r + 2 - g1):
                t1 = n + 1 - g1
                t2 = t1 - g2
                coef = 2 if g1 + g2 <= r else (g2 + 1)
                Q2 += coef * W(g1, g2) / (t1 * t2)
        assert Q1 - Q2 <= diff
        lhs = nf(n, r) * math.e * Ren(r + 1) + float(Fr(d(n, n - r), n ** (n - 2)))
        assert -1e-9 <= lhs <= math.e * (5 * r - 1) / (4 * n * (1 - r / n) ** 4) + 1e-9
        assert abs(float(Fr(-d(n, n - r), n ** (n - 2))) - math.e * Ren(r + 1)) <= 60 * (r + 1) / n
    for dd in range(0, n):
        assert (n / (n - dd)) ** 2 * (1 - 1e-12) <= nf(n, dd) <= (n / (n - dd)) ** 2.5 * (1 + 1e-12)
for r in range(0, 400):
    assert math.e * Ren(r + 1) <= 1 + 1e-12
    if r >= 1:
        assert math.e * Ren(r + 1) >= exp(-0.5) * r ** -0.5 > 1 / (2 * sqrt(r + 1))
for j in range(2, 200):
    assert sum(Ren(a) * Ren(j - a) for a in range(1, j)) <= 0.5
    assert sum((j - a) * Ren(a) * Ren(j - a) for a in range(1, j)) <= j / 4
for D in range(2, 4):
    n = math.ceil(20 * D ** 1.5)
    if n <= N:
        assert all(b(n, n - D + i) > b(n, n - D + i + 1) for i in range(D - 1)), (D, n)
        print("(아) D", D, "n", n, "ok")
for n in range(5, 30):
    for dd in range(0, n - 1):
        val = sum((Fr(dd ** (i + 1), i + 1) + 2 * dd ** i - sum(rho ** i for rho in range(dd))) / i / Fr(n) ** i for i in range(1, 300))
        assert abs(float(val) - log(nf(n, dd))) < 1e-6 * max(1, abs(log(nf(n, dd)))), (n, dd, float(val), log(nf(n, dd)))
        for d2 in range(0, n - dd - 1):
            assert abs(nf(n, dd + d2) - nf(n, dd) * nf(n - dd, d2)) < 1e-9 * nf(n, dd + d2)
print("moving tail, nf ok")
