# R3 (22차): 5.2.3절·5.4절의 수치 대조 (mpmath)
import math
from math import comb, factorial
from fractions import Fraction as Fr
import mpmath as mp

mp.mp.dps = 40

# --- 갱신 방문 핵의 상하계 (kernel-C-bound, kernel-bounds, kernel-crude)
Ren = lambda m: mp.mpf(m) ** m * mp.e ** (-m) / mp.factorial(m)
cb = lambda m: mp.binomial(2 * m, m) / mp.mpf(4) ** m
o = 1 / mp.sqrt(2)
ok = True
prev = None
for m in range(1, 3000):
    q = Ren(m) / (o * cb(m))
    if not (1 <= q <= 1 + mp.mpf(1) / (12 * (2 * m - 1))):
        ok = False
        print("C-bound FAIL", m)
    if not (q >= 1 + mp.mpf(1) / (25 * (2 * m - 1))):
        ok = False
        print("K1 FAIL", m)
    rr = Ren(m) / cb(m)
    if prev is not None and not rr < prev:
        ok = False
        print("crude monotone FAIL", m)
    prev = rr
print("kernel bounds m<3000:", ok, " Ren(1)/(o cb_1)=%s (26/25=1.04)" % mp.nstr(Ren(1) / (o * cb(1)), 8))
print("312m^2-374m+25 at m=1,2:", 312 - 374 + 25, 312 * 4 - 374 * 2 + 25)

# --- nf(n,d), lc_i, W^{[1]}, W^{[2]}
def nf(n, d):
    t = n - d
    return mp.factorial(n) * mp.e ** d * mp.mpf(t) ** (t - 2) / (mp.factorial(t) * mp.mpf(n) ** (n - 2))

def W(n, gam):
    ds = []
    s = 0
    for g in gam:
        s += g
        ds.append(s)
    val = nf(n, ds[-1] - 1)
    for di in ds[:-1]:
        val *= mp.mpf(n) / (n + 1 - di)
    return val, ds

def LN(gam):
    ds = []
    s = 0
    for g in gam:
        s += g
        ds.append(s)
    L = Fr(5, 2) * (ds[-1] - 1) + sum(d - 1 for d in ds[:-1])
    Nn = L * L / 2 + Fr(5, 4) * (ds[-1] - 1) ** 2 - Fr(ds[-1] - 1, 12) + Fr(1, 2) * sum((d - 1) ** 2 for d in ds[:-1])
    return L, Nn

ok = True
for gam in [(1,), (3,), (2, 1), (1, 4, 2), (5, 1, 1, 3), (2, 2, 2, 2, 2)]:
    L, Nn = LN(gam)
    for n in [10 ** 4, 10 ** 5]:
        w, ds = W(n, gam)
        rem = (w - 1 - mp.mpf(L.numerator) / L.denominator / n - mp.mpf(Nn.numerator) / Nn.denominator / n ** 2) * mp.mpf(n) ** 3
        j = len(gam)
        r = ds[-1] - 1
        up = (1 - mp.mpf(r) / n) ** (-j - mp.mpf(3) / 2)
        if not (w >= 1 and w <= up and rem >= -1e-20):
            ok = False
            print("W FAIL", gam, n)
    # 분해식
    if len(gam) >= 2:
        j = len(gam)
        g1 = gam[0]
        L1, N1 = LN(gam[1:])
        if L != L1 + (j + Fr(3, 2)) * g1 - 1:
            ok = False
            print("L decomposition FAIL", gam)
        if Nn != N1 + ((j + Fr(5, 2)) * g1 - 1) * L1 + Fr(1, 2) * (j + Fr(3, 2)) * (j + Fr(5, 2)) * g1 * g1 - (j + Fr(31, 12)) * g1 + 1:
            ok = False
            print("N decomposition FAIL", gam)
print("W_n = 1 + L/n + N/n^2 + O(n^-3) >=, envelope, decompositions:", ok)

# --- 표시 사슬 합의 생성함수 재귀 대 직접 열거 (j<=3, r<=9)
M = 16  # z^M까지
RenF = [mp.mpf(0)] + [Ren(m) for m in range(1, M + 1)]

def mul(a, b):
    c = [mp.mpf(0)] * (M + 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j2, bj in enumerate(b):
            if i + j2 > M:
                break
            c[i + j2] += ai * bj
    return c

def der(a):
    return [a[i + 1] * (i + 1) for i in range(M)] + [mp.mpf(0)]

def zmul(a):
    return [mp.mpf(0)] + a[:M]

inv1mz = [mp.mpf(1)] * (M + 1)
C = RenF[:]
zCp = zmul(der(C))
zzCpp = zmul(der(zCp))
add = lambda *xs: [sum(v) for v in zip(*xs)]
sc = lambda c, a: [c * v for v in a]

def step(F):  # z (F' + 2F/(1-z))
    return zmul(add(der(F), sc(2, mul(F, inv1mz))))

Z = {1: zmul(C)}
Y = {1: sc(mp.mpf(5) / 2, zmul(add(zCp, sc(-1, C))))}
O = {1: zmul(add(sc(mp.mpf(35) / 8, add(zzCpp, sc(-2, zCp), C)), sc(-mp.mpf(1) / 12, add(zCp, sc(-1, C)))))}
for j in range(2, 4):
    Z[j] = mul(C, step(Z[j - 1]))
    Y[j] = add(mul(C, step(Y[j - 1])), mul(add(sc(j + mp.mpf(3) / 2, zCp), sc(-1, C)), step(Z[j - 1])))
    O[j] = add(
        mul(C, step(O[j - 1])),
        mul(add(sc(j + mp.mpf(5) / 2, zCp), sc(-1, C)), step(Y[j - 1])),
        mul(add(sc(mp.mpf((2 * j + 3) * (2 * j + 5)) / 8, zzCpp), sc(-(j + mp.mpf(31) / 12), zCp), C), step(Z[j - 1])),
    )

def compositions(j, maxsum):
    if j == 0:
        yield ()
        return
    for g in range(1, maxsum - (j - 1) + 1):
        for rest in compositions(j - 1, maxsum - g):
            yield (g,) + rest

def direct(j, d, which):
    tot = mp.mpf(0)
    for gam in compositions(j, d - 1):
        ds = []
        s = 0
        for g in gam:
            s += g
            ds.append(s)
        pr = mp.mpf(1)
        for g, di in zip(gam, ds):
            pr *= Ren(g) * (d - di)
        L, Nn = LN(gam)
        wt = 1 if which == 0 else (mp.mpf(L.numerator) / L.denominator if which == 1 else mp.mpf(Nn.numerator) / Nn.denominator)
        tot += wt * pr
    return tot

ok = True
for j in range(1, 4):
    for r in range(1, 10):
        for which, G in [(0, Z), (1, Y), (2, O)]:
            dr = direct(j, r + 2, which) - 2 * direct(j, r + 1, which) + direct(j, r, which)
            if abs(dr - G[j][r + 2]) > mp.mpf(10) ** (-25) * (1 + abs(dr)):
                ok = False
                print("marked recursion FAIL", j, r, which, dr, G[j][r + 2])
print("marked-recursion (Z, Y, O) vs direct enumeration, j<=3, r<=9:", ok)
print("all coefficients nonneg:", all(v >= 0 for G in (Z, Y, O) for j in G for v in G[j]))

# --- parity-tail: Z_j <= dc'_j (1-z)^(-theta'_j)
dc = {2: mp.mpf(2)}
th = lambda j: mp.mpf(3 * j) / 2 - 1
dc[3] = mp.mpf(3) / 4 * (th(2) + 2) * dc[2]
ok = all(Z[j][m] <= dc[j] * mp.binomial(m + th(j) - 1, m) for j in (2, 3) for m in range(M + 1))
print("parity-tail j=2,3 up to z^%d:" % M, ok)

# --- laurent-coeff 네 경우
z = mp.mpf("0.3")
def coeff_w(i, U):
    return mp.taylor(lambda t: (1 - t) ** (mp.mpf(i) / 2), 0, U)[U]
ok = True
for U in range(1, 9):
    for Up in range(1, 5):
        a = coeff_w(-2 * Up, U)
        if abs(a - mp.binomial(U + Up - 1, Up - 1)) > 1e-20:
            ok = False
            print("case1 FAIL")
        b = coeff_w(2 * Up - 1, U)
        num = mp.mpf(1)
        den = mp.mpf(1)
        for t in range(1, Up + 1):
            num *= (mp.mpf(1) / 2 - t)
            den *= (U + mp.mpf(1) / 2 - t)
        if abs(b - cb(U) * num / den) > 1e-20:
            ok = False
            print("case4 FAIL", U, Up, b, cb(U) * num / den)
    for Up in range(0, 4):
        a = coeff_w(-1 - 2 * Up, U)
        num = mp.mpf(1)
        den = mp.mpf(1)
        for t in range(Up):
            num *= (U + mp.mpf(1) / 2 + t)
            den *= (mp.mpf(1) / 2 + t)
        if abs(a - cb(U) * num / den) > 1e-20:
            ok = False
            print("case3 FAIL")
print("laurent-coeff cases:", ok)

# --- omitted-tail (나)
print("(r+1)/n cap: %.5f ; (12/11)^1.5*(1+1/598)=%.5f ; 12/(110e)=%.5f (1/24=%.5f) ; log10(1.15*598^3)=%.4f ; 598 log10 24=%.3f" % (
    1.8 * (1 + 1 / 598) / math.sqrt(598), (12 / 11) ** 1.5 * (1 + 1 / 598), 12 / (110 * math.e), 1 / 24, math.log10(1.15 * 598 ** 3), 598 * math.log10(24)))

# --- cut-rep (라)
l = lambda m: (2 + mp.mpf(1) / m) * mp.zeta(2 * m) / mp.pi ** (2 * m)
print("l_1,l_2,l_3 =", mp.nstr(l(1), 10), mp.nstr(l(2), 10), mp.nstr(l(3), 10), " 1/36=%.10f 1/405=%.10f" % (1 / 36, 1 / 405))
print("sum_{m>=5} 2m l_m 2^(2-2m) =", mp.nstr(mp.nsum(lambda m: 2 * m * l(m) * mp.mpf(2) ** (2 - 2 * m), [5, mp.inf]), 8))
et = lambda ph: mp.e * ph * mp.e ** (-ph * mp.cot(ph)) / mp.sin(ph)
print("log et(1/2) =", mp.nstr(mp.log(et(mp.mpf(1) / 2)), 10), " series:", mp.nstr(mp.nsum(lambda m: l(m) * mp.mpf(1) / 4 ** m, [1, mp.inf]), 10))
# T_+ 매개화: pt e^{-pt} = ct
ph = mp.mpf("1.3")
pt = ph * mp.cot(ph) + 1j * ph
print("pt e^-pt - ct =", mp.nstr(pt * mp.e ** (-pt) - ph / mp.sin(ph) * mp.e ** (-ph * mp.cot(ph)), 5))
# (가) k^{k-1}/k! 적분 표현
for k in (1, 3, 7):
    val = mp.quad(lambda f: f * (f / mp.sin(f) * mp.e ** (-f * mp.cot(f))) ** (-k) * (1 / f - mp.cot(f) + f / mp.sin(f) ** 2 - mp.cot(f)) if False else
                  f * (et(f) / mp.e) ** (-k) * mp.diff(lambda u: mp.log(et(u)), f), [0, 1, 2, 3, mp.pi]) / mp.pi
    print("  k=%d  integral=%s  k^(k-1)/k!=%s" % (k, mp.nstr(val, 12), mp.nstr(mp.mpf(k) ** (k - 1) / mp.factorial(k), 12)))
# (다) Borel 꼬리의 절단 표현
def bortail(k, ptp):
    return 1 - sum(mp.e ** (-j * ptp) * (j * ptp) ** (j - 1) / mp.factorial(j) for j in range(1, k + 1))
for k, ag in [(3, 0.7), (6, 1.9), (10, 0.3)]:
    ptp = mp.e ** (1j * ag)
    xi = ptp * mp.e ** (1 - ptp)
    integ = mp.quad(lambda f: f * et(f) ** (-k) * mp.diff(lambda u: mp.log(et(u)), f) / (et(f) - xi), [0, 0.5, 1, 2, 3, mp.pi])
    rhs = xi ** (k + 1) / (mp.pi * ptp) * integ
    print("  (da) k=%d ag'=%.1f  |lhs-rhs|=%s" % (k, ag, mp.nstr(abs(bortail(k, ptp) - rhs), 5)))
print("1-cos(1)=%.5f ; 10001^(-1/3)=%.6f ; 0.0015/1.25^12=%.4e ; boxes=%d ; cells=%.1f" % (1 - math.cos(1), 10001 ** (-1 / 3), 0.0015 / 1.25 ** 12, 29 + 1 + 12 + 1 + 1, (10 - 1.4) / 0.2))
