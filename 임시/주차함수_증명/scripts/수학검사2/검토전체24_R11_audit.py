# -*- coding: utf-8 -*-
# R11 검산: D.central-gap-rational-audit 의 (ㄱ)(ㄴ)(ㅁ)(ㅅ)
from fractions import Fraction as Q
from mpmath import mp, quad, gamma, sqrt, mpf, pi, exp
mp.dps = 30
# (ㄱ)
a0 = mpf(3) ** (mpf(1) / 3 - 1) * gamma(mpf(1) / 3)
a1 = mpf(3) ** (mpf(2) / 3 - 1) * gamma(mpf(2) / 3)
print("a0", a0, 1.287899 < a0 < 1.2879, " a1", a1, 0.938892 < a1 < 0.939)
# (ㄴ) 잔차의 x^0..x^4 계수, gamma=1/3 및 다른 유리점
N = 6
def con(v): return [Q(v)] + [Q(0)] * N
def add(x, y): return [p + q for p, q in zip(x, y)]
def sc(x, c): return [Q(c) * p for p in x]
def mul(x, y): return [sum(x[j] * y[i - j] for j in range(i + 1)) for i in range(N + 1)]
def inv(x):
    y = con(1 / x[0])
    for i in range(1, N + 1): y[i] = -sum(x[j] * y[i - j] for j in range(1, i + 1)) / x[0]
    return y
def pw(x, n):
    if n < 0: return pw(inv(x), -n)
    r = con(1)
    for _ in range(n): r = mul(r, x)
    return r
def sqrt1(x):
    y = con(1)
    for i in range(1, N + 1): y[i] = (x[i] - sum(y[j] * y[i - j] for j in range(1, i))) / 2
    return y
def uhat(g, X):
    # g: series for gamma, X: series for x
    u0 = sc(add(con(1), g), Q(1, 2)); om = add(con(1), sc(u0, -1))
    C1 = mul(om, pw(g, -2))
    C2 = sc(mul(mul(om, add(con(2), u0)), pw(g, -5)), -1)
    C3 = sc(mul(mul(om, add(add(con(6), g), sc(mul(g, g), -1))), pw(g, -8)), Q(5, 2))
    return add(add(add(u0, mul(X, C1)), mul(pw(X, 2), C2)), mul(pw(X, 3), C3))
def resid(gam):
    gam = Q(gam)
    X = [Q(0), Q(1)] + [Q(0)] * (N - 1)
    iota = (1 - gam * gam) / 4
    g0 = con(gam)
    # gamma(iota - x) = gam*sqrt(1+4x/gam^2)
    g1 = sc(sqrt1(add(con(1), sc(X, 4 / gam ** 2))), gam)
    U0 = uhat(g0, X); U1 = uhat(g1, X)
    return add(mul(add(U0, con(-1)), U1), con(iota))
for g in (Q(1, 3), Q(1, 2), Q(4, 5), Q(1)):
    R = resid(g)
    print("gamma", g, "coeffs x^0..x^4:", R[:5])
# (ㅁ)
f = lambda r: r ** 2 * ((mpf(4) / 3) * r ** 2 * (1 - r ** 2) * 105 * (1 + r ** 2) ** (-mpf(9) / 2)
                        + ((mpf(1) / 3) * r ** 2 * (1 - r ** 2) ** 2 - (mpf(2) / 3) * r * (1 - r ** 2)) * 945 * (1 + r ** 2) ** (-mpf(11) / 2)
                        - (mpf(1) / 6) * r * (1 - r ** 2) ** 2 * 10395 * (1 + r ** 2) ** (-mpf(13) / 2))
S = quad(f, [0, 1])
print("three finite integrals sum:", S, " -23+3sqrt2 =", -23 + 3 * sqrt(2), "  times -2sqrt2:", -2 * sqrt(2) * S, 46 * sqrt(2) - 12)
# (ㅅ)
print("5.642*1.6809*0.39893-0.0163-3.554 =", Q(5642, 1000) * Q(16809, 10000) * Q(39893, 100000) - Q(163, 10000) - Q(3554, 1000), float(Q(5642, 1000) * Q(16809, 10000) * Q(39893, 100000) - Q(163, 10000) - Q(3554, 1000)))
lam = Q(698, 100); x = mpf(10000) ** (-mpf(1) / 3)
print("C3 lower at k=1e4:", 6.98 - 3.5 - (4 * 6.98 + 0.5) * 1.2879 * x - 6.5 * 6.98 * 0.939 * x * x - 12 * 6.98 / 10000)
print("4sqrt2(1-23.75/1e4)=", 4 * sqrt(2) * (1 - mpf(2375) / 10 ** 6), " (2pi)^-1/2 (1-1/(12k)) =", (1 - mpf(1) / 120000) / sqrt(2 * pi))
print("(46sqrt2-12-54.6828-1e-22)e^{1/k}-1e-19 =", (46 * sqrt(2) - 12 - mpf('54.6828') - mpf('1e-22')) * exp(mpf(1) / 10000) - mpf('1e-19'))
print("0.4503*3*2.50663+1675.2/1e4+2e-20 =", mpf('0.4503') * 3 * mpf('2.50663') + mpf('0.16752') + mpf('2e-20'), " sqrt2/pi*e^{1/k} =", sqrt(2) / pi * exp(mpf(1) / 10000))
