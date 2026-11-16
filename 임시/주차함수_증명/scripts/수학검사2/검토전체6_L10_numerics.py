# -*- coding: utf-8 -*-
# 검토전체6 L10: 10장의 수치 주장(범위 표, 가족 첫 열, DDL♮, 가족 검사 표, 부호 보조정리, 젊은 걸음 합)을 배정밀도로 다시 센다.
import math
import random
from math import log, exp, sqrt, pi, lgamma, floor
try:
    import mpmath as mp
    HAVE_MP = True
except Exception:
    HAVE_MP = False


def quad(f, a, b, n=20000):
    if HAVE_MP:
        return float(mp.quad(lambda x: f(float(x)), [a, b]))
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * f(a + i * h)
    return s * h / 3


S2PI = 1 / sqrt(2 * pi)

print("== 10.3 range table")
for k in [6667, 6668, 8064, 8065, 9948, 9949]:
    nu_min = max(103, 20001 - 2 * k)
    print(k, "nu_min=", nu_min, "0.48k=", 0.48 * k, "band?", nu_min <= 0.48 * k, "nu_min/k=", round(nu_min / k, 5))
print("== family first columns")
for k in [9704, 9705, 9550, 9551, 8064, 8065]:
    print(k, "20001-2k=", 20001 - 2 * k, "1.3k^(2/3)=", round(1.3 * k ** (2 / 3), 2), "2k^(2/3)=", round(2 * k ** (2 / 3), 2), "0.48k=", 0.48 * k)


def qf(r):
    return 1 + 0.7501 * r / (1 + r)


def j2_int():
    return quad(lambda s: 2 * sqrt(1 + s * s) * 0.70836 * qf(s * s) ** 3, 0, 1)


def j1_int():
    return quad(lambda s: (2 * sqrt(1 + s * s) * 0.70836 * qf(s * s) ** 3 * (2.528571 - log(qf(s * s)) + 3 * log(s))) if s > 0 else 0.0, 0, 1)


J2 = j2_int()
J1 = j1_int()
print("== j2, j1 =", J2, J1, " (text: 2.7171998, 0.7998716)")
print("3*sqrt2*0.16696 =", 3 * sqrt(2) * 0.16696, " 2.5-log2-log0.485917 =", 2.5 - log(2) - log(0.485917))
print("(sqrt2*0.16696)^(1/2) =", (sqrt(2) * 0.16696) ** 0.5)


def DDLnat(k):
    dn = 2 * k ** (2 / 3)
    eps = -log(1 - sqrt(k + 1) / (0.485917 * k))
    epsp = 2.26 / k + 0.47 / (dn - 1)
    gam = 2.6047 * (2.53 + 0.5 * log(k) + eps + 1.5 / k) / k
    t1 = 0.457143 * S2PI * qf(dn / k) * sqrt(1 + dn / k) * (dn + 1) ** 3.5 / k ** 3
    t2 = 2 * S2PI * k ** -0.5 * (1 + epsp) * (J1 + (0.5 * log(k) + eps) * J2 + gam)
    t3 = 3.9 * S2PI / k
    return t1 + t2 + t3


for k in [6667, 6668, 8065, 9551, 9705, 9949]:
    print("DDLnat(%d) = %.9f" % (k, DDLnat(k)))
print("decrease condition j1+j2(0.5 log 6667 - 1) =", J1 + J2 * (0.5 * log(6667) - 1))


def sign_lemma(k):
    D = int(floor(2 * k ** (2 / 3)))
    while (D + 1) ** 3 <= 8 * k * k:
        D += 1
    while D ** 3 > 8 * k * k:
        D -= 1
    rho0 = D / k
    eps = -log(1 - sqrt(k + 1) / (0.485917 * k))

    def ih(r):
        return 0.70836 * qf(r) ** 3 * (2.528571 - log(qf(r)) + 1.5 * log(r) + 0.5 * log(k) + eps)
    val = quad(lambda s: (2 * sqrt(1 + s * s) * ih(s * s)) if s > 0 else 0.0, 0, sqrt(rho0))
    return D, rho0, val


for k in [6667, 10000]:
    print("sign lemma k=%d:" % k, sign_lemma(k), " (appendix D: 0.37808 at 6667, 0.33913 at 1e4)")

worst = -1
random.seed(1)
for n in [x / 100 for x in range(101, 3000)] + [random.uniform(1, 50) for _ in range(2000)]:
    s = sum(z * (1 - z / n) for z in range(1, int(math.ceil(n)) + 1) if z < n)
    worst = max(worst, s - n * n / 6)
print("== lemma old-8-21: max(sum - n^2/6) =", worst)

MS = 1.15


def u_(k):
    return 3 / 0.35 * (1.35 + 1 / k) * (0.65 - 1 / k) ** -1.5 * k ** -0.5


def BdT(k, nu):
    return (k + nu) * u_(k) * (1 / (k - 1) + 1 / k) + 3 * (k + 1) * (k - 1) ** -1.5


def sup_(d, y):
    return min(1.0, MS * (y + d) / d ** 1.5)


def ec(k, nup):
    return 3 * nup ** 2 / ((k - 1) * k) + 4.8 * sqrt(nup) / k + nup ** 2 / (2 * (k - 1) ** 2)


def ebar(k):
    xi = (sqrt(5 * k * log(k)) + 2) / k
    return exp(1.5 / k) * (exp(sqrt(5 * log(k) / k) + 1 / k) + 2.40918 * k ** (1.5 - 2.5 / (1 + xi)))


def abar(k):
    return 3 * MS * (1.48 * k + 2) / (0.48 * k + 1) ** 1.5


def bbar(k):
    return 2 * u_(k) * (2 * k - 1) / (k - 1) + 3 * (k + 1) * (k - 1) ** -1.5


def dbar(k):
    return 72.217 / sqrt(k)


def cAb(r):
    return 2 * sqrt(r) / (1 - r) + 2 * log((1 + sqrt(r)) / (1 - sqrt(r)))


def Sub(k, nubar):
    xi = (nubar + 4) / (k - 1)
    if xi >= 0.6:
        return 0.0
    return (k - 1) / k * quad(lambda r: (r - xi) * (1 + r) * r ** -1.5 * (1 - r) ** -2, xi, 0.6)


def Top(k, nubar):
    return quad(lambda r: min(2, 2 + (nubar + 1) / k - r) * (1 + r / 3) * r ** -1.5, 0.6 - 2.6 / k, 1)


def Flat(y):
    ab = (MS * (y + 2 * y ** (2 / 3))) ** (2 / 3)
    return 2 * (ab - 1) / (y + 2 - ab)


def Ab(y, k, nubar):
    z = 0.6 + 1 / y
    return MS * (1 + 1 / y) * (4 * ((MS * y) ** (2 / 3) - 1) ** -0.5 + y ** -0.5 * (2 * cAb(z) - 4 * z ** -0.5 - Sub(k, nubar)))


def StaysUp(k, nubar):
    return sum(Flat(y) + Ab(y, k, nubar) for y in (k - 1, k)) + 2 * 16.54 * k ** -0.5 * Top(k, nubar)


print("== (na) family checks")
fams = {}
for name, k0 in [("bulk", 6668), ("2", 8065), ("1b", 9551), ("1a", 9705)]:
    D = DDLnat(k0)
    if name == "bulk":
        o = 4 - ebar(k0)
        st = abar(k0) + bbar(k0) + D + dbar(k0)
        Rs = st
        Rsp = None
        print(name, k0, "o_F=%.5f" % o, "abar=%.4f bbar=%.4f DDL=%.4f dbar=%.4f ebar=%.4f sum5=%.4f" % (abar(k0), bbar(k0), D, dbar(k0), ebar(k0), abar(k0) + bbar(k0) + D + dbar(k0) + ebar(k0)), "Stays_up_F=%.5f" % st, "margin=%.4f" % (o - st))
    elif name == "2":
        nubar = 0.48 * k0
        th0 = (2 * exp(-0.48) - 1) * exp(-0.48)
        s3 = 3 * sup_(2 * k0 ** (2 / 3) + 1, k0 + 1)
        o = 4 - s3 + th0 - BdT(k0, nubar) - D
        st = StaysUp(k0, nubar)
        Rs = s3 + BdT(k0, nubar) + D + st
        Rsp = None
        print(name, k0, "3sup=%.4f th0=%.4f BdT=%.4f DDL=%.4f o_F=%.5f" % (s3, th0, BdT(k0, nubar), D, o), "Stays_up=%.5f" % st, "margin=%.4f" % (o - st), "Rsharp=%.5f" % Rs)
    elif name == "1b":
        nubar = 2 * k0 ** (2 / 3)
        xi2 = 2 * k0 ** (2 / 3) / (k0 - 1)
        thb = (2 * exp(-xi2) - 1) * exp(-xi2)
        s3 = 3 * sup_(1.3 * k0 ** (2 / 3) + 1, k0 + 1)
        o = 4 - s3 + thb - BdT(k0, nubar) - D
        st = StaysUp(k0, nubar)
        Rs = s3 + BdT(k0, nubar) + D + st
        Rsp = BdT(k0, nubar) + D + st
        print(name, k0, "3sup=%.4f th=%.4f BdT=%.4f DDL=%.4f o_F=%.5f" % (s3, thb, BdT(k0, nubar), D, o), "Stays_up=%.5f" % st, "margin=%.4f" % (o - st), "Rsharp=%.5f Rsharp'=%.5f" % (Rs, Rsp))
    else:
        nubar = 1.3 * k0 ** (2 / 3)
        o = 2 - ec(k0, nubar) - BdT(k0, nubar) - D
        st = StaysUp(k0, nubar)
        Rs = 3 + BdT(k0, nubar) + D + st
        Rsp = BdT(k0, nubar) + D + st
        print(name, k0, "ec=%.4f BdT=%.4f DDL=%.4f o_F=%.5f" % (ec(k0, nubar), BdT(k0, nubar), D, o), "Stays_up=%.5f (Flat %.4f x2, Ab %.4f x2, Top-part %.4f)" % (st, Flat(k0), Ab(k0, k0, nubar), 2 * 16.54 * k0 ** -0.5 * Top(k0, nubar)), "margin=%.4f" % (o - st), "Rsharp=%.5f Rsharp'=%.5f" % (Rs, Rsp))
    fams[name] = (k0, Rs, Rsp)


def logBor(j):
    return -j + (j - 1) * log(j) - lgamma(j + 1)


def Bor(j):
    return exp(logBor(j))


def sfrak_all(y, Q):
    s = [None] * (Q + 2)
    s[1] = 1.0
    for q in range(2, Q + 2):
        lb = logBor(y + q)
        psum = 0.0
        tot = 0.0
        for qp in range(1, q):
            p = exp(logBor(q - qp) + logBor(y + qp) - lb)
            psum += p
            tot += p * y / (y + qp) * s[qp]
        s[q] = (1 - psum) + tot
    return s


F1 = 4 / (3 * sqrt(2 * pi))


def slow(d, y):
    return exp(-F1 * ((y + d - 1) / y) ** 1.5 * d ** 1.5 / y)


CR = sqrt(2 * pi) / 2 * exp(1 / 12)


def Qfun(y, xi):
    k = y - 1
    q0 = xi * y ** (2 / 3)
    pref = k / (k + 1) * (1 - q0 / (2 * k)) * 2 * S2PI * exp(-1 / 12) * y / (CR * q0)
    b1 = exp(-q0 / y) * slow(q0, y) * (exp(-CR * q0 / y) - exp(-CR * q0 * sqrt(q0 / 2) / y))
    b2 = exp(-q0 / (2 * y)) * slow(q0 / 2, y) * (exp(-CR * q0 * sqrt(q0 / 2 + 1) / y) - exp(-CR * q0 ** 1.5 / y))
    return pref * (b1 + b2)


def RenStar(j):
    return S2PI * j ** -0.5 * exp(-1 / (12 * j))


def Aup(q0, q):
    return sqrt(2 * pi) / 4 * exp(1 / (12 * (q0 - q))) * (q0 + q) * sqrt(q0 - q)


print("== (ga) family checks")
for name, (k0, Rs, Rsp) in fams.items():
    y = k0 + 1
    eps0 = int(floor(2 ** (2 / 3) * (k0 + 1) ** (2 / 3)))
    sy = sfrak_all(y, eps0)
    sk = sfrak_all(k0, eps0 + 1)
    bor = [0.0] + [Bor(j) for j in range(1, eps0 + 2)]
    cum = [0.0] * (eps0 + 3)
    for j in range(1, eps0 + 2):
        cum[j] = cum[j - 1] + bor[j]
    best = (1e9, None)
    bestp = (1e9, None)
    for q0 in range(2, eps0 + 1):
        zR = sum(RenStar(q0 - q) * exp(-(q + Aup(q0, q)) / y) * sy[q] for q in range(1, q0))
        tail = max(0.0, 1 - cum[q0 - 1])
        eR = k0 / (k0 + 1) * (1 - q0 / (2 * k0)) * (max(zR, sy[q0] - tail) + bor[q0])
        elow = 4 * sk[q0 + 1] + 2 * eR
        m = elow - Rs
        if m < best[0]:
            best = (m, q0)
        if Rsp is not None and q0 >= 104:
            mp_ = eR + sk[q0 + 1] - Rsp
            if mp_ < bestp[0]:
                bestp = (mp_, q0)
    xcap = 1.3 if name == "1a" else 2 ** (2 / 3)
    edge = 4 * slow(xcap * (k0 + 1) ** (2 / 3) + 1, k0) + 2 * Qfun(k0 + 1, xcap) - Rs
    out = "%s k0=%d eps0=%d (a)min=%.4f at q0=%s (b)edge=%.4f" % (name, k0, eps0, best[0], best[1], edge)
    if Rsp is not None:
        edgep = Qfun(k0 + 1, 2 ** (2 / 3)) + slow(2 ** (2 / 3) * (k0 + 1) ** (2 / 3) + 1, k0) - Rsp
        out += " | m0>N: (a)min=%.4f at q0=%s (b)=%.4f" % (bestp[0], bestp[1], edgep)
    print(out)
    print("   s_2(k0+1)=%.6f s_3(k0)=%.6f" % (sy[2], sk[3]))
