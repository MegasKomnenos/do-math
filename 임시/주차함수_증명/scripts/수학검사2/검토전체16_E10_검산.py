# -*- coding: utf-8 -*-
"""E10 (장10) 독립 검토: 10.4–10.6절의 명시 함수와 표의 수치를 다시 센다.
배정밀도/mpmath 평가(검산 목적; 본문의 구간 산술을 대신하지 않는다)."""
import math
from mpmath import mp, mpf, quad, log, sqrt, exp, e, pi

mp.dps = 30

def Bor(m):
    m = mpf(m)
    return exp(-m + (m - 1) * log(m) - mp.loggamma(m + 1))

def g(x):
    x = mpf(x)
    return (x - 1) * log(1 + 1 / x)

# ---------- 10.3 표 ----------
print("== 10.3 범위 표 ==")
for k in [6667, 6668, 8064, 8065, 9948, 9949]:
    nu_min = max(103, 20001 - 2 * k)
    print(k, "nu_min", nu_min, "0.48k", 0.48 * k, "nu_min/k>0.48?", nu_min > 0.48 * k, "3k", 3 * k)

# ---------- 10.4 상수 ----------
print("== 10.4 ==")
k = 6667
print("0.48k vs 1.5(2k+3)^{2/3}:", 0.48 * k, 1.5 * (2 * k + 3) ** (2 / 3))
# pi^two Borel form check numerically for k=7000, nu=3500
def pi_two_direct(k, nu):
    N = k + nu
    return exp(mp.loggamma(N) - mp.loggamma(k + 1) - mp.loggamma(nu) + (k - 1) * log(k) + (nu - 2) * log(nu - 1) - (N - 2) * log(N))
def pi_two_borel(k, nu):
    N = k + nu
    return Bor(k) * Bor(nu - 1) / (e * Bor(N))
print("pi_two direct/borel:", pi_two_direct(7000, 3500), pi_two_borel(7000, 3500))

# ---------- 10.5 상수 ----------
print("== 10.5 ==")
print("3*sqrt2*0.16696 =", 3 * sqrt(2) * mpf("0.16696"))
print("2.5-log2-log0.485917 =", mpf("2.5") - log(2) - log(mpf("0.485917")))
print("(sqrt2*0.16696)^(1/2) =", sqrt(sqrt(2) * mpf("0.16696")))
print("1.00057 factor at k=6667:", (1 + 1 / mpf(6667)) * (1 + 2 / mpf(6667)) / (1 - 3 / (4 * mpf(6667))))
print("(1+e^{3/(2k)})*9/8/3 at 6667:", (1 + exp(mpf(3) / (2 * 6667))) * mpf(9) / 8 / 3)
print("rho0 bound 2*6667^{-1/3} =", 2 * mpf(6667) ** (-mpf(1) / 3))
print("log 2^{1.5} =", 1.5 * log(2))
dnat = 2 * mpf(6667) ** (mpf(2) / 3)
print("d^natural(6667) =", dnat, " (1-1/d)^{1.5} log:", 1.5 * log(1 - 1 / dnat))
rho0 = mpf("0.10635")
qrho0 = 1 + mpf("0.7501") * rho0 / (1 + rho0)
print("q(rho0) =", qrho0, " log:", log(qrho0))
iota0 = mpf("2.528571") - log(qrho0) + 1.5 * log(2) + 1.5 * log(1 - 1 / dnat)
print("iota0 >=", iota0)
sig0 = exp(-mpf("3.4964") / 1.5)
print("sigma0 =", sig0)
rr = rho0 * sig0
print("rho at sigma0:", rr, " d(rho)q(rho)^3*sqrt(rho):", sqrt(1 + rr) * (1 + mpf("0.7501") * rr / (1 + rr)) ** 3)
print("bracket 2*iota0-6-0.1728*sqrt(sigma0):", 2 * mpf("3.4964") - 6 - mpf("0.1728") * sqrt(sig0))
# j1, j2
def qf(r):
    return 1 + mpf("0.7501") * r / (1 + r)
j2 = quad(lambda s: 2 * sqrt(1 + s ** 2) * mpf("0.70836") * qf(s ** 2) ** 3, [0, mpf("1e-6"), mpf("0.01"), 1])
j1 = quad(lambda s: 2 * sqrt(1 + s ** 2) * mpf("0.70836") * qf(s ** 2) ** 3 * (mpf("2.528571") - log(qf(s ** 2)) + 3 * log(s)), [0, mpf("1e-6"), mpf("0.01"), 1])
print("j2 =", j2, " j1 =", j1)
print("j1 + j2(0.5 log 6667 - 1) =", j1 + j2 * (0.5 * log(6667) - 1))

def DDLnat(k):
    k = mpf(k)
    d = 2 * k ** (mpf(2) / 3)
    eps = -log(1 - sqrt(k + 1) / (mpf("0.485917") * k))
    epsp = mpf("2.26") / k + mpf("0.47") / (d - 1)
    gam = mpf("2.6047") * (mpf("2.53") + 0.5 * log(k) + eps + 1.5 / k) / k
    t1 = mpf("0.457143") / sqrt(2 * pi) * qf(d / k) * sqrt(1 + d / k) * (d + 1) ** mpf("3.5") / k ** 3
    t2 = 2 / sqrt(2 * pi) / sqrt(k) * (1 + epsp) * (j1 + (0.5 * log(k) + eps) * j2 + gam)
    t3 = mpf("3.9") / sqrt(2 * pi) / k
    return t1 + t2 + t3
for k in [6667, 6668, 8065, 9551, 9705, 9949]:
    print("DDLnat(%d) =" % k, DDLnat(k))
# sign lemma integral at k=6667
def sign_integral(k):
    k = mpf(k)
    D = int(mp.floor(2 * k ** (mpf(2) / 3)))
    r0 = mpf(D) / k
    f = lambda s: 2 * sqrt(1 + s ** 2) * mpf("0.70836") * qf(s ** 2) ** 3 * (mpf("2.528571") - log(qf(s ** 2)) + 3 * log(s) + 0.5 * log(k) + (-log(1 - sqrt(k + 1) / (mpf("0.485917") * k))))
    return quad(f, [0, mpf("1e-6"), sqrt(r0) / 10, sqrt(r0)])
print("sign integral(6667) =", sign_integral(6667))

# old-8-25 constants
print("2/sqrt(pi) =", 2 / sqrt(pi))
print("(1.15*6666)^{2/3} =", (mpf("1.15") * 6666) ** (mpf(2) / 3))
def Ecoef(ups, q=389):
    return 2 / sqrt(2 * pi) * (mpf(1) / 4 * (1 - 1 / (2 * mpf(q))) ** (-1.5) + (1 + ups + ups ** 2) * (1 - ups) ** (-0.5) * (1 + ups) ** (-1.5))
for u in ["0.9", "0.99", "0.9999"]:
    print("E coef at ups=%s:" % u, Ecoef(mpf(u)))
print("F at ups=0.9 bound 3*sqrt(0.19):", 2 / sqrt(2 * pi) * 3 * sqrt(mpf("0.19")), " at 0.99:", 2 / sqrt(2 * pi) * 3 * sqrt(1 - mpf("0.9801")))
print("1.28/sqrt50 =", mpf("1.28") / sqrt(50), " 2/sqrt(2pi)*sqrt(50/0.77) =", 2 / sqrt(2 * pi) * sqrt(50 / mpf("0.77")))
print("0.98^{-1.5}-1 =", mpf("0.98") ** (-1.5) - 1)

# ---------- 10.6 ----------
print("== 10.6 ==")
mS = mpf("1.15")
f1 = mpf(4) / 3 / sqrt(2 * pi)
cR = sqrt(2 * pi) / 2 * exp(mpf(1) / 12)
print("f1 =", f1, " cR =", cR)
print("beta0 min =", cR * mpf("1.04") ** 1.5 / sqrt(2), " g^e(1.0216) =", exp(-mpf("1.0216")) * (1 + 1.5 * mpf("1.0216")))
print("iota q0 max =", cR * 2 ** (mpf(2) / 3) / mpf(6669) ** (mpf(1) / 3))
print("beta2 range =", cR * mpf("1.04") ** 1.5, cR * 2)
print("sqrt(1/2+1/562) =", sqrt(mpf(1) / 2 + mpf(1) / 562))
print("|g^e'| at 2.73 =", exp(-mpf("2.73")) * (1.5 * mpf("2.73") - 0.5), " at 1.02:", exp(-mpf("1.02")) * (1.5 * mpf("1.02") - 0.5))
print("0.234*0.2916*1.444 =", mpf("0.234") * mpf("0.2916") * mpf("1.444"))
print("theta0 =", (2 * exp(mpf("-0.48")) - 1) * exp(mpf("-0.48")))
print("pi_two const:", 1 / sqrt(2 * pi) / e * 2 ** 1.5, 1 / sqrt(2 * pi) / e * 2 ** 1.5 * exp(-mpf(1) / (12 * 6667) - mpf(1) / (12 * 3200)))
print("1/0.41508 =", 1 / mpf("0.41508"))
print("m_hit/k at 6667:", math.ceil(math.sqrt(5 * 6667 * math.log(6667))) / 6667)
# families first columns
for k, phi in [(9705, 1.3), (9551, 2.0), (8065, None)]:
    if phi:
        print(k, "20001-2k =", 20001 - 2 * k, " phi k^{2/3} =", phi * k ** (2 / 3), " prev k:", 20001 - 2 * (k - 1), phi * (k - 1) ** (2 / 3))
    else:
        print(k, "20001-2k =", 20001 - 2 * k, " 0.48k =", 0.48 * k, " prev:", 20001 - 2 * (k - 1), 0.48 * (k - 1))
for k0 in [6668, 8065, 9551, 9705]:
    print("eps0(%d) =" % k0, math.floor(2 ** (2 / 3) * (k0 + 1) ** (2 / 3)))

def u_fn(k):
    k = mpf(k)
    return 3 / mpf("0.35") * (mpf("1.35") + 1 / k) * (mpf("0.65") - 1 / k) ** (-1.5) / sqrt(k)
def BdT(k, nu):
    k = mpf(k); nu = mpf(nu)
    return (k + nu) * u_fn(k) * (1 / (k - 1) + 1 / k) + 3 * (k + 1) * (k - 1) ** (-1.5)
def s_up(d, y):
    d = mpf(d); y = mpf(y)
    return min(mpf(1), mS * (y + d) / d ** 1.5)
def e_c(k, nup):
    k = mpf(k); nup = mpf(nup)
    return 3 * nup ** 2 / ((k - 1) * k) + mpf("4.8") * sqrt(nup) / k + nup ** 2 / (2 * (k - 1) ** 2)
def ebar(k):
    k = mpf(k)
    xi = (sqrt(5 * k * log(k)) + 2) / k
    return exp(mpf(3) / (2 * k)) * (exp(sqrt(5 * log(k) / k) + 1 / k) + mpf("2.40918") * k ** (mpf("1.5") - mpf("2.5") / (1 + xi)))
def o_F(fam, k):
    k = mpf(k)
    k23 = k ** (mpf(2) / 3)
    if fam == "1a":
        return 2 - e_c(k, mpf("1.3") * k23) - BdT(k, mpf("1.3") * k23) - DDLnat(k)
    if fam == "1b":
        xi2 = 2 * k23 / (k - 1)
        return 4 - 3 * s_up(mpf("1.3") * k23 + 1, k + 1) + (2 * exp(-xi2) - 1) * exp(-xi2) - BdT(k, 2 * k23) - DDLnat(k)
    if fam == "2":
        th0 = (2 * exp(mpf("-0.48")) - 1) * exp(mpf("-0.48"))
        return 4 - 3 * s_up(2 * k23 + 1, k + 1) + th0 - BdT(k, mpf("0.48") * k) - DDLnat(k)
    if fam == "bulk":
        return 4 - ebar(k)

def cAb(rho):
    rho = mpf(rho)
    return 2 * sqrt(rho) / (1 - rho) + 2 * log((1 + sqrt(rho)) / (1 - sqrt(rho)))
def Sub(k, nubar):
    k = mpf(k)
    xi = (mpf(nubar) + 4) / (k - 1)
    if xi >= mpf("0.6"):
        return mpf(0)
    f = lambda r: (r - xi) * (1 + r) * r ** (-1.5) * (1 - r) ** (-2)
    return (k - 1) / k * quad(f, [xi, mpf("0.6")])
def Top(k, nubar):
    k = mpf(k); c = (mpf(nubar) + 1) / k
    f = lambda r: min(mpf(2), 2 + c - r) * (1 + r / 3) * r ** (-1.5)
    return quad(f, [mpf("0.6") - mpf("2.6") / k, c, 1]) if c > mpf("0.6") - mpf("2.6") / k else quad(f, [mpf("0.6") - mpf("2.6") / k, 1])
def Flat(y):
    y = mpf(y)
    ab = (mS * (y + 2 * y ** (mpf(2) / 3))) ** (mpf(2) / 3)
    return 2 * (ab - 1) / (y + 2 - ab)
def Ab(y, k, nubar):
    y = mpf(y)
    z = mpf("0.6") + 1 / y
    return mS * (1 + 1 / y) * (4 * ((mS * y) ** (mpf(2) / 3) - 1) ** (-0.5) + y ** (-0.5) * (2 * cAb(z) - 4 * z ** (-0.5) - Sub(k, nubar)))
def Stays_up(k, nubar):
    return sum(Flat(y) + Ab(y, k, nubar) for y in [k - 1, k]) + 2 * mpf("16.54") / sqrt(mpf(k)) * Top(k, nubar)

print("2c^Ab(0.6)-4/sqrt0.6 =", 2 * cAb(mpf("0.6")) - 4 / sqrt(mpf("0.6")), " Sub max:", quad(lambda r: (1 + r) * r ** (-0.5) * (1 - r) ** (-2), [0, mpf("0.6")]))
print("132.32 bracket at 0.48:", (mpf("0.48") ** (-0.5) - 1 + (1 - sqrt(mpf("0.48"))) / 3), " *132.32:", mpf("132.32") * (mpf("0.48") ** (-0.5) - 1 + (1 - sqrt(mpf("0.48"))) / 3))

k = mpf(6668)
abar = 3 * mS * (mpf("1.48") * k + 2) / (mpf("0.48") * k + 1) ** 1.5
bbar = 2 * u_fn(k) * (2 * k - 1) / (k - 1) + 3 * (k + 1) * (k - 1) ** (-1.5)
dbar = mpf("72.217") / sqrt(k)
print("bulk 6668: abar", abar, "bbar", bbar, "DDL", DDLnat(6668), "dbar", dbar, "ebar", ebar(6668), "sum", abar + bbar + DDLnat(6668) + dbar, "o_F", o_F("bulk", 6668), "sum+ebar", abar + bbar + DDLnat(6668) + dbar + ebar(6668))
R_bulk = abar + bbar + DDLnat(6668) + dbar
for fam, k0, nubar_fn in [("2", 8065, lambda k: mpf("0.48") * k), ("1b", 9551, lambda k: 2 * mpf(k) ** (mpf(2) / 3)), ("1a", 9705, lambda k: mpf("1.3") * mpf(k) ** (mpf(2) / 3))]:
    nb = nubar_fn(k0)
    su = Stays_up(k0, nb)
    o = o_F(fam, k0)
    print(fam, k0, "o_F", o, "Stays_up", su, "margin", o - su)
    k23 = mpf(k0) ** (mpf(2) / 3)
    if fam == "1a":
        Rs = 3 + BdT(k0, nb) + DDLnat(k0) + su
    elif fam == "1b":
        Rs = 3 * s_up(mpf("1.3") * k23 + 1, k0 + 1) + BdT(k0, nb) + DDLnat(k0) + su
    else:
        Rs = 3 * s_up(2 * k23 + 1, k0 + 1) + BdT(k0, nb) + DDLnat(k0) + su
    Rsp = BdT(k0, nb) + DDLnat(k0) + su
    print("   R#", Rs, " R#'", Rsp, " pieces: BdT", BdT(k0, nb), "DDL", DDLnat(k0), "3s_up(1.3)", 3 * s_up(mpf("1.3") * k23 + 1, k0 + 1), "3s_up(2)", 3 * s_up(2 * k23 + 1, k0 + 1), "e_c", e_c(k0, mpf("1.3") * k23))
    print("   Flat", Flat(k0), "Ab", Ab(k0, k0, nb), "Top term", 2 * mpf("16.54") / sqrt(mpf(k0)) * Top(k0, nb))
