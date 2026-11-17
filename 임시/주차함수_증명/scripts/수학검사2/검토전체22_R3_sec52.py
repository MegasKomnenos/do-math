# R3 (22차): 5.2.1-5.2.2절의 항등식·부등식 수치 대조 (sympy 정확 산술)
import math
from math import comb, factorial
from fractions import Fraction as Fr
import sympy as sp

y = sp.symbols("y")
p = lambda n: 1 if n == 0 else (n + 1) ** (n - 1)  # p_0 = 1 (정수로 유지)


def Aw(N, wg):
    A = [sp.Integer(1)]
    for n in range(1, N + 1):
        A.append(sp.expand(sum(comb(n - 1, j) * wg(j + 1) * A[j] * A[n - 1 - j] for j in range(n))))
    return A


def Gamma(d, n, memo):
    if (d, n) in memo:
        return memo[(d, n)]
    if d == 0:
        r = sp.Integer(1)
    else:
        r = sp.expand(comb(n, d) * p(d) + y * sum(comb(n - d + j, j) * p(j) * Gamma(d - 1 - j, n, memo) for j in range(d)))
    memo[(d, n)] = r
    return r


memo = {}
ok = True
for k in range(1, 6):
    N = 2 * k + 1
    K = Aw(N, lambda t: t if t <= k else y)  # K_{n,k}(y)
    K1 = Aw(N + 2, lambda t: t if t <= k + 1 else y)  # K_{n,k+1}(y)
    phi = Aw(N, lambda t: t if t <= k else 0)  # phi^{[k]}_n
    for n in range(1, N + 1):
        rhs = phi[n] + y * sum(phi[m] * Gamma(n - m - 1, n, memo) for m in range(k, n))
        if sp.expand(K[n] - rhs) != 0:
            ok = False
            print("source-rep(ga) FAIL", n, k)
        if k + 1 <= n <= 2 * k + 1:
            if sp.expand(K[n] - K1[n] - (y - k - 1) * p(k) * Gamma(n - k - 1, n, memo)) != 0:
                ok = False
                print("green(da) FAIL", n, k)
print("source-rep(ga), green-connection(da):", ok)


def column(l, N):
    A = [1] * (N + 1)
    for n in range(1, N + 1):
        A[n] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j] for j in range(n))
    return A


N = 13
cols = {l: column(l, N) for l in range(0, N + 2)}


def A(n, l):
    if l < 0:
        return 1 if n == 0 else 0
    return cols[l][n]


dd = lambda n, k: A(n, k) - 2 * A(n, k - 1) + A(n, k - 2)
ok2 = True
for k in range(3, 7):
    Kk = Aw(2 * k + 1, lambda t: t if t <= k else y)
    phi = Aw(2 * k + 1, lambda t: t if t <= k else 0)
    for n in range(k + 2, 2 * k):
        r = n - k
        Kv = lambda v: Kk[n].subs(y, v)
        assert Kv(k + 1) == A(n, k) and Kv(k) == A(n, k - 1)
        Gm = p(k - 1) * Gamma(r, n, memo).subs(y, k - 1)
        Gp = p(k) * Gamma(r - 1, n, memo).subs(y, k + 2)
        twoE = Kv(k + 1) - 2 * Kv(k) + Kv(k - 1)
        c = Kv(k + 2) - 3 * Kv(k + 1) + 3 * Kv(k) - Kv(k - 1)
        if dd(n, k) != twoE - Gm:
            ok2 = False
            print("d=2E-G- FAIL", n, k)
        if dd(n, k + 1) != twoE + c - Gp:
            ok2 = False
            print("d'=2E+c-G+ FAIL", n, k)
        if Gm != Kv(k - 1) - A(n, k - 2):
            ok2 = False
            print("G- FAIL")
        if Gp != Kv(k + 2) - A(n, k + 1):
            ok2 = False
            print("G+ FAIL")
        hg = lambda d: sp.expand(y * Gamma(d, n, memo))
        sd = lambda d, v: hg(d).subs(y, v + 1) - 2 * hg(d).subs(y, v) + hg(d).subs(y, v - 1)
        S = Gp * dd(n, k) - Gm * dd(n, k + 1)
        S2 = sum(phi[n - d - 1] * (Gp * sd(d, k) - Gm * sd(d, k + 1)) for d in range(1, r))
        if S != S2:
            ok2 = False
            print("S FAIL", n, k)
        if twoE != sum(phi[m] * sd(n - m - 1, k) for m in range(k, n)):
            ok2 = False
            print("2E FAIL")
print("source-rep(na)(da):", ok2)

tw = lambda j: sp.Integer(1) if j == 1 else sp.Rational((j - 1) ** (j - 1), factorial(j))


def V(d, co):
    v = [sp.Integer(1)]
    for i in range(1, d + 1):
        v.append(sp.expand((1 + co[i - 1]) * v[i - 1] + sum(tw(j) * v[i - j] for j in range(2, i + 1))))
    return v[d]


ok3 = True
for n in range(2, 9):
    for d in range(0, n):
        lhs = Gamma(d, n, memo)
        rhs = sp.expand(sp.ff(n, d) * V(d, [y / (n - i) for i in range(d)]))
        if sp.expand(lhs - rhs) != 0:
            ok3 = False
            print("tile FAIL", n, d)
print("inverse-renewal tile identity:", ok3)

rho = sp.symbols("rho")
ok4 = True
for d in range(1, 9):
    hb = sp.Poly(V(d, [rho] * d), rho)
    for j in range(0, d + 1):
        want = sp.Rational(j + 1) * sp.Rational(d + 1) ** (d - j - 1) / factorial(d - j)
        if hb.coeff_monomial(rho ** j) != want:
            ok4 = False
            print("hb coeff FAIL", d, j)
    if hb.eval(1) != sp.Rational((d + 1) ** d, factorial(d)):
        ok4 = False
print("hb coefficients / hb(1):", ok4)

ok5 = all(
    sum(math.prod(1 - i / (d + 1) for i in range(1, j + 1)) for j in range(1, d + 1)) <= math.sqrt(math.pi * d / 2)
    for d in range(1, 400)
)
print("tm_d(1)<=sqrt(pi d/2), d<400:", ok5)


def tb(r, k):
    n = k + r
    rh = Fr(k, n)
    bt = [Fr(1)]
    for j in range(1, r):
        bt.append(bt[-1] * (1 - Fr(j, r)))
    w = [(j + 1) * rh ** j * bt[j] for j in range(r)]
    Z = sum(w)
    mu = sum(j * w[j] for j in range(r)) / Z
    m2 = sum(j * j * w[j] for j in range(r)) / Z
    return mu, m2


ok6 = True
for r, k in [(2, 3), (3, 4), (5, 9), (10, 40), (30, 31), (64, 1024), (64, 5000), (100, 1800), (170, 3577)]:
    mu, m2 = tb(r, k)
    if m2 + (3 + Fr(r * r, k)) * mu + 2 != 2 * r:
        ok6 = False
        print("(ii) FAIL", r, k)
    if not (m2 - mu <= Fr(3, 2) * mu * mu):
        ok6 = False
        print("(i) FAIL", r, k)
    if r >= 64 and k >= r ** 1.5 + 8 * r and not float(mu) >= 6 / 7 * math.sqrt(r):
        ok6 = False
        print("(iii) FAIL", r, k)
    print("  r=%d k=%d mu=%.4f (6/7)sqrt r=%.4f" % (r, k, float(mu), 6 / 7 * math.sqrt(r)))
print("tilted-birthday-mean (i)(ii)(iii):", ok6)

ok7 = True
for (r, k) in [(2, 3), (3, 5), (4, 5), (5, 8), (6, 7)]:
    n = k + r
    Vr = lambda d, yy: Gamma(d, n, memo).subs(y, yy) / sp.ff(n, d)
    if not Vr(r, k - 1) <= sp.Rational(r + 1, r) ** r * Vr(r - 1, k):
        ok7 = False
        print("(ga) FAIL", r, k)
    for d in range(1, r):
        hg = sp.expand(y * Gamma(d, n, memo))
        h2, h3 = sp.diff(hg, y, 2), sp.diff(hg, y, 3)
        for yy in [sp.Rational(k - 1), sp.Rational(k), sp.Rational(k + 1), sp.Rational(k + 2)]:
            if not float(h3.subs(y, yy) / h2.subs(y, yy)) <= (1 + math.sqrt(3 * math.pi * d / 2)) / float(yy):
                ok7 = False
                print("(da) FAIL", r, k, d, yy)
        sdv = lambda v: hg.subs(y, v + 1) - 2 * hg.subs(y, v) + hg.subs(y, v - 1)
        if not float(sdv(k + 1) / sdv(k)) <= math.exp((1 + math.sqrt(3 * math.pi * (r - 1) / 2)) / (k - 1)):
            ok7 = False
            print("(da)2 FAIL")
    mu, _ = tb(r, k)
    if not math.log(float(Vr(r - 1, k + 2) / Vr(r - 1, k))) >= float(mu) * math.log(1 + 2 / k) - 1e-12:
        ok7 = False
        print("(ra) FAIL", r, k)
print("suff-cond (ga)(da)(ra) samples:", ok7)

s = 8.0
br = 1 / (3 * s) + 8 / (3 * s * s) + 12 / (7 * s * s) + (1 + 2.1709 * s) / (s ** 3 + 8 * s * s - 1)
print("sqrt(3pi/2)=%.6f  31/14-2.1709=%.6f  bracket(s=8)=%.6f  bound=%.4f" % (math.sqrt(1.5 * math.pi), 31 / 14 - 2.1709, br, 0.0433 * 8 + 0.5 - 0.1281))


def Pc(k, r, eb):
    return k * (1 / (2 * r) - 1 / (3 * r * r)) - 2.5 + 2 * eb * (1 - 1 / k) - k / (k - 1) * (1 + math.sqrt(3 * math.pi * (r - 1) / 2))


print("Pc(19831,170,0)=%.4f ; 19831*127/43350=%.4f ; (19831/19830)(1+13 sqrt(3pi/2))=%.4f" % (Pc(19831, 170, 0), 19831 * 127 / 43350, 19831 / 19830 * (1 + 13 * math.sqrt(1.5 * math.pi))))
print("min over 64<=r<=4000 of Pc(ceil(r^1.5+8r), r, 6/7 sqrt r) = %.4f" % min(Pc(math.ceil(r ** 1.5 + 8 * r), r, 6 / 7 * math.sqrt(r)) for r in range(64, 4001)))


def mcell(n):
    m = 170
    while n - 9 * (m + 1) >= 0 and (m + 1) ** 3 <= (n - 9 * (m + 1)) ** 2:
        m += 1
    return m


print("m(20001)=%d m(50001)=%d" % (mcell(20001), mcell(50001)))
print("597^1.5+9*597=%.3f  598^1.5+9*598=%.3f" % (597 ** 1.5 + 9 * 597, 598 ** 1.5 + 9 * 598))
bad = [n for n in list(range(20001, 60001, 7)) + [10 ** 6, 10 ** 7, 10 ** 8 + 3] if not (n ** (2 / 3) - 6 * n ** (1 / 3) - 1 <= mcell(n) <= n ** (2 / 3) - 6 * n ** (1 / 3) + 37)]
print("tail-cells(na) bound violations:", bad)
print("floor(20001^(2/3)-6*20001^(1/3)) =", math.floor(20001 ** (2 / 3) - 6 * 20001 ** (1 / 3)))
print("1/(1+9/sqrt598)=%.6f ; 832^1.5=%.2f 833^1.5=%.2f (>1.2*20001=%.1f) ; 965^1.5=%.2f 966^1.5=%.2f (>=1.5*20001=%.1f)" % (1 / (1 + 9 / math.sqrt(598)), 832 ** 1.5, 833 ** 1.5, 1.2 * 20001, 965 ** 1.5, 966 ** 1.5, 1.5 * 20001))
print("rq caps: %.5f %.5f %.5f ; 5/9*sqrt598=%.4f ; (9/5)^(2/3)=%.5f ; 10/2^(2/3)=%.5f" % (1.2 / math.sqrt(598), 1.5 / math.sqrt(833), 1.8 / math.sqrt(966), 5 / 9 * math.sqrt(598), 1.8 ** (2 / 3), 10 / 2 ** (2 / 3)))
