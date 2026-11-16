# -*- coding: utf-8 -*-
# 10차 독립 검토 P2: 4장(4.3절 해석적 연쇄) 수치·기호 검산
import sympy as sp
import mpmath as mp
from fractions import Fraction as Fr
from itertools import permutations
from math import comb, factorial
mp.mp.dps = 30

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

print("=== (A) 따름정리 gauss-coeff-numeric ===")
a0 = mp.quad(lambda w: mp.e ** (-w ** 3 / 3), [0, mp.inf])
a1 = mp.quad(lambda w: w * mp.e ** (-w ** 3 / 3), [0, mp.inf])
print("a0", a0, "a1", a1, "a0 closed", 3 ** (-mp.mpf(2) / 3) * mp.gamma(mp.mpf(1) / 3), "a1 closed", 3 ** (-mp.mpf(1) / 3) * mp.gamma(mp.mpf(2) / 3))
print("1.287899<a0<1.2879:", 1.287899 < a0 < 1.2879, " 0.938892<a1<0.939:", 0.938892 < a1 < 0.939)
w = Fr(699, 100)
val = w - Fr(7, 2) - (6 * Fr(699, 100) + Fr(3, 4)) / 31 - (13 * Fr(699, 100) / 2) / 961 - 12 * Fr(699, 100) / 30000
print("(나) rational:", val, val == Fr(495594511, 240250000), float(val), val > 2)
w = Fr(698, 100)
kk13 = Fr(464159, 10 ** 7)
val2 = w - Fr(7, 2) - (4 * w + Fr(1, 2)) * Fr(12879, 10000) * kk13 - (13 * w / 2) * Fr(939, 1000) * kk13 ** 2 - 12 * w / 10000
print("(다) value with k^{-1/3}<=0.0464159:", float(val2), ">=1.6809:", val2 >= Fr(16809, 10000))
print("10000^{-1/3} =", mp.mpf(10000) ** (-mp.mpf(1) / 3))
# 조립
print("k>=30000 조립: 11/2*39/100*2-7/2 =", Fr(11, 2) * Fr(39, 100) * 2 - Fr(7, 2))
print("k>=10000 조립: 5.642*1.6809*0.39893-0.0163-3.554 =", Fr(5642, 1000) * Fr(16809, 10000) * Fr(39893, 100000) - Fr(163, 10000) - Fr(3554, 1000), float(Fr(5642, 1000) * Fr(16809, 10000) * Fr(39893, 100000) - Fr(163, 10000) - Fr(3554, 1000)))
print("Bor(k)k^{3/2} lower (2pi)^{-1/2}(1-1/120000) =", (2 * mp.pi) ** -0.5 * (1 - mp.mpf(1) / 120000))
print("4sqrt2(1-26/k) at 1e4, 3e4:", 4 * mp.sqrt(2) * (1 - mp.mpf(26) / 10000), 4 * mp.sqrt(2) * (1 - mp.mpf(26) / 30000))
print("sqrt2/pi e^{1/30000}, e^{1/10000}:", mp.sqrt(2) / mp.pi * mp.e ** (mp.mpf(1) / 30000), mp.sqrt(2) / mp.pi * mp.e ** (mp.mpf(1) / 10000))
print("46sqrt2-12 =", 46 * mp.sqrt(2) - 12, " -5000/173-0.02:", 46 * mp.sqrt(2) - 12 - mp.mpf(5000) / 173 - mp.mpf(2) / 100)
print("(나) 46sqrt2-12-5468.28/100 =", 46 * mp.sqrt(2) - 12 - mp.mpf('54.6828'))
print("0.451*3*2.51+0.056+0.01 =", 0.451 * 3 * 2.51 + 0.056 + 0.01, " 0.4503*3*2.50663+0.16752 =", 0.4503 * 3 * 2.50663 + 0.16752)
print("3sqrt(2pi) =", 3 * mp.sqrt(2 * mp.pi))
k = mp.mpf(30000)
print("k^5 e^{-k/520} at 30000:", k ** 5 * mp.e ** (-k / 520))
print("255k/131072-511/262144 vs k/520 at k=30000:", 255 * k / 131072 - mp.mpf(511) / 262144, k / 520)

print("=== (B) 정리 4.7 피적분함수 조립 ===")
v, om, kk, chi, F = sp.symbols('v omega k chi F', positive=True)
# 둘째 단계 피적분함수 (f_k/(1-v)) * { (k v^6/4 + om v^4/2)[1/F - 1/2 - 3/(2kF^2)] - v e^{-v^2/2} }
# 부분적분: k v^6/(4F(1-v)) -> (1-v)^{-1} * (1-v)[v^3/F - v^5/(4(1-v)F^2)]
expr = (kk * v ** 6 / 4 + om * v ** 4 / 2) * (1 / F - sp.Rational(1, 2) - 3 / (2 * kk * F ** 2)) - v * sp.exp(-v ** 2 / 2)
expr = expr - kk * v ** 6 / (4 * F) + (1 - v) * (v ** 3 / F - v ** 5 / (4 * (1 - v) * F ** 2))
expr = expr.subs(F, v ** 2 / (2 * chi))
pv = v * (2 * (1 - v) * chi - chi ** 2 - sp.exp(-v ** 2 / 2)) + om * v ** 2 * chi - sp.Rational(3, 2) * v ** 2 * chi ** 2 - 3 * om / kk * chi ** 2 - kk / 8 * v ** 6 - om / 4 * v ** 4
print("p(v) 조립 일치:", sp.simplify(sp.expand(expr - pv)) == 0)
# 모멘트 계수
print("k^{-1/3}: (om+1/2+3om)=", sp.simplify(om + sp.Rational(1, 2) + 3 * om), " k^{-2/3}: om/2+6om =", sp.Rational(1, 2) * om + 6 * om)

print("=== (C) 보조정리 gauss-contraction ===")
g, iota, X = sp.symbols('gamma iota X', positive=True)
ups = (1 + g) / 2
C1 = (1 - ups) / g ** 2
C2 = -(1 - ups) * (2 + ups) / g ** 5
C3 = 5 * (1 - ups) * (6 + g - g ** 2) / (2 * g ** 8)
print("C1,C2,C3 in gamma:", sp.simplify(C1 - (1 - g) / (2 * g ** 2)), sp.simplify(C2 + (1 - g) * (5 + g) / (4 * g ** 5)), sp.simplify(C3 - 5 * (1 - g) * (6 + g - g ** 2) / (4 * g ** 8)))
print("at gamma=1/3:", [sp.nsimplify(c.subs(g, sp.Rational(1, 3))) for c in (C1, C2, C3)])
# d/d iota = (-2/gamma) d/dgamma
D = lambda f: sp.simplify(-2 / g * sp.diff(f, g))
u4 = D(D(D(D(ups))))
print("ups'''' =", sp.simplify(u4), " expected -120 g^-7")
c1_3 = D(D(D(C1))); c2_2 = D(D(C2)); c3_1 = D(C3)
print("C1''' =", sp.expand(c1_3), " expected 192g^-8-60g^-7")
print("C2'' =", sp.expand(c2_2), " expected -(175g^-9-96g^-8-15g^-7)")
print("C3' =", sp.expand(c3_1), " expected 5/2(48g^-10-35g^-9-12g^-8+5g^-7)")
# termwise abs sum at 1/3
def termabs(e):
    return sum(abs(t.subs(g, sp.Rational(1, 3))) for t in sp.Add.make_args(sp.expand(e)))
print("bounds:", termabs(u4) / 24, termabs(c1_3) / 6, termabs(c2_2) / 2, termabs(c3_1), termabs(u4) / 24 + termabs(c1_3) / 6 + termabs(c2_2) / 2 + termabs(c3_1))
# m1,m2,m3
m1 = sp.simplify(-D(ups) + C1); m2 = sp.simplify(D(D(ups)) / 2 - D(C1) + C2); m3 = sp.simplify(-D(D(D(ups))) / 6 + D(D(C1)) / 2 - D(C2) + C3)
print("m1 - ups/g^2:", sp.simplify(m1 - ups / g ** 2), " m2 - (C2-2/g^4):", sp.simplify(m2 - (C2 - 2 / g ** 4)), " m3 - (C3+5(5-g^2)/(2g^7)):", sp.simplify(m3 - (C3 + 5 * (5 - g ** 2) / (2 * g ** 7))))
print("m at 1/3:", [sp.nsimplify(m.subs(g, sp.Rational(1, 3))) for m in (m1, m2, m3)])
# residual expansion in X: gamma(iota - X) = sqrt(gamma^2 + 4X)
gm = sp.sqrt(g ** 2 + 4 * X)
def uhat(gg, x):
    u = (1 + gg) / 2
    c1 = (1 - u) / gg ** 2; c2 = -(1 - u) * (2 + u) / gg ** 5; c3 = 5 * (1 - u) * (6 + gg - gg ** 2) / (2 * gg ** 8)
    return u + x * c1 + x ** 2 * c2 + x ** 3 * c3
iota_g = (1 - g ** 2) / 4
R = (uhat(g, X) - 1) * uhat(gm, X) + iota_g
ser = sp.series(R, X, 0, 5).removeO()
for j in range(5):
    cj = sp.simplify(ser.coeff(X, j))
    print("R coeff X^%d:" % j, cj if j < 4 else sp.nsimplify(cj.subs(g, sp.Rational(1, 3))))
# contraction factor
xx = 1.12e-5
print("contraction factor:", (2 / 9) / (4 / 9 - 144 * xx ** 2), " residual/uhat:", 4.25e6 / (2 / 3 - 216 * xx ** 2), " total:", 7e6 / (1 - 0.51))
print("x^5 x^6 terms:", (216 * 60750 + 34020 * 378) * xx, 34020 * 60750 * xx ** 2, " |uhat-1| bound:", 1 / 3 + 3 * xx + 216 * xx ** 2 + 34020 * xx ** 3)
print("total residual:", 468018 + 291 + 1 + (1 / 3 + 4e-5) * 11328660)
# 두 적분 식 미분 확인
I1 = iota * sp.log(ups) + (1 - ups) ** 2 / 2
I1g = I1.subs(iota, iota_g)
print("d/diota [iota log ups + (1-ups)^2/2] - log ups:", sp.simplify(D(I1g) - sp.log(ups)))
I2 = sp.log(ups) - sp.log(g) / 2
print("d/diota [log ups - log g /2] - C1/ups:", sp.simplify(D(I2) - C1 / ups))
print("C1/ups at 1/3:", (C1 / ups).subs(g, sp.Rational(1, 3)), " 1/(g ups) at 1/3:", (1 / (g * ups)).subs(g, sp.Rational(1, 3)))
# (라) identity
kS, nu, th = sp.symbols('k nu theta')
NN = 3 * kS + nu + 1 - th
print("(라) identity:", sp.expand(2 * NN ** 2 - 9 * (2 * kS + nu) * (kS - th) - ((3 * nu + 12 + 6 * th) * kS + 2 * (nu + 1 - th) ** 2 + 9 * nu * th)))
print("k/(3k-1)^2 at 1e4:", 10000 / (29999 ** 2), " 11/2/9+350*2/81 =", 5.5 / 9 + 700 / 81, " nu=-1: 9.26*(1-1/30000)^-4 =", 9.26 * (1 - 1 / 30000) ** -4)

print("=== (D) 보조정리 gauss-coeff ===")
kap = sp.symbols('kappa')
Nt = 3 + (nu + 1 - th) * kap
xn = (2 + (nu - 1) * kap) * (1 - th * kap) / Nt ** 2
xs = (1 - th * kap) * kap / Nt ** 2
nn = sp.expand(Nt ** 2 - 4 * (2 + (nu - 1) * kap) * (1 - th * kap))
print("n(kappa) =", sp.collect(nn, kap), " expected 1+(2nu+10+2th)k+((nu+1)^2+2(nu-3)th+th^2)k^2")
gam_n = sp.sqrt(nn) / Nt
def uhat_sym(gg, x):
    u = (1 + gg) / 2
    c1 = (1 - u) / gg ** 2; c2 = -(1 - u) * (2 + u) / gg ** 5; c3 = 5 * (1 - u) * (6 + gg - gg ** 2) / (2 * gg ** 8)
    return u + x * c1 + x ** 2 * c2 + x ** 3 * c3
gfun = (Nt * uhat_sym(gam_n, xs) - 2 - nu * kap) / kap
for nuv in (0, -1):
    s = sp.series(gfun.subs(nu, nuv), kap, 0, 5).removeO()
    coeffs = [sp.factor(sp.simplify(s.coeff(kap, j))) for j in range(5)]
    print("nu=%d g coeffs:" % nuv)
    for j, c in enumerate(coeffs):
        print("   kappa^%d:" % j, sp.expand(c))
    g3 = sp.Poly(sp.expand(coeffs[3]), th); g4 = sp.Poly(sp.expand(coeffs[4]), th)
    import numpy as np
    ths = np.linspace(0, 1, 2001)
    f3 = sp.lambdify(th, coeffs[3]); f4 = sp.lambdify(th, coeffs[4])
    print("   max|g3| on [0,1]:", max(abs(f3(t)) for t in ths), " max|g4|:", max(abs(f4(t)) for t in ths))
print("Cauchy terms at kappa=1/30000:", 16988 / 30000, 404903 / 30000 ** 2, 1000 * 100 ** 5 / 30000 ** 3 / (1 - 100 / 30000), 9300 / 30000)
# (4.9) via Hermite recurrence
He_n, He_nm1, y, n = sp.symbols('He_n He_nm1 y n')
NNs = n + y + 1
He_nm2 = (NNs * He_nm1 - He_n) / ((n - 1) * y)
He_nm3 = (NNs * He_nm2 - He_nm1) / ((n - 2) * y)
num2 = He_n - 3 * n * He_nm1 + 3 * n * (n - 1) * He_nm2 - n * (n - 1) * (n - 2) * He_nm3
num0 = He_n - n * He_nm1
vth = sp.symbols('vartheta')
ratio2 = sp.simplify((num2 / num0).subs(He_n, (n + vth) * He_nm1))
target = (vth * ((n - y) ** 2 + n) - n * (n + 1)) / (y ** 2 * vth)
print("(4.9) check:", sp.simplify(ratio2 - target))
# M4/M0
He_nm4 = (NNs * He_nm3 - He_nm2) / ((n - 3) * y)
num4 = He_n - 5 * n * He_nm1 + 10 * n * (n - 1) * He_nm2 - 10 * n * (n - 1) * (n - 2) * He_nm3 + 5 * n * (n - 1) * (n - 2) * (n - 3) * He_nm4 - n * (n - 1) * (n - 2) * (n - 3) * (n - 4) * (NNs * He_nm4 - He_nm3) / ((n - 4) * y)
ratio4 = sp.simplify((num4 / num0).subs(He_n, (n + vth) * He_nm1))
for nuv, formula in ((0, 1 + 16 / kS + 18 / kS ** 2 + 2 / kS ** 3 - (4 + 38 / kS + 22 / kS ** 2 + 2 / kS ** 3) / vth), (-1, 1 + 12 / kS - 6 / kS ** 2 - (4 + 26 / kS - 14 / kS ** 2) / vth)):
    r4 = ratio4.subs({n: 2 * kS + nuv, y: kS})
    print("M4/M0 formula nu=%d:" % nuv, sp.simplify(r4 - formula))
    center = {0: 4 - 26 / kS + 506 / kS ** 2, -1: 4 - 22 / kS + 414 / kS ** 2}[nuv]
    ser4 = sp.series(formula.subs(vth, center), kS, sp.oo, 4)
    print("   with center:", ser4)
# P expansion
P = vth * ((n - y) ** 2 + n) - n * (n + 1)
for nuv in (0, -1):
    center = 4 - (26 + 4 * nuv + 8 * th) / kS + (506 + 97 * nuv + 5 * nuv ** 2 + (168 + 16 * nuv) * th + 12 * th ** 2) / kS ** 2
    Pk = sp.expand(P.subs({n: 2 * kS + nuv, y: kS - th, vth: center}))
    print("nu=%d P:" % nuv, sp.collect(Pk, kS))
    den = sp.expand((kS - th) ** 2 * center)
    print("   denominator y^2 vth:", sp.collect(den, kS))
    e1 = sp.expand(kS * Pk + 5 * den); e2 = sp.expand(100 * kS * Pk + 499 * den)
    print("   kP+5y^2vth:", sp.collect(e1, kS))
    print("   100kP+499y^2vth k^2 coeff:", sp.expand(e2).coeff(kS, 2))
# l root bounds
for nuv in (0, -1):
    nn_ = 2 * kS + nuv
    fl = lambda l: l ** 2 + (nn_ - kS - 1) * l - nn_
    print("nu=%d f(2)=" % nuv, sp.expand(fl(2)), " f(2-2/k)=", sp.factor(fl(2 - 2 / kS)))
print("(1-3/k)^2 e^{-12.75/k}(4-26/k) >= 4sqrt2... check k=1e4:", (1 - 3e-4) ** 2 * mp.e ** (-12.75e-4) * (4 - 26e-4) * mp.sqrt(2), 4 * mp.sqrt(2) * (1 - 26e-4))

print("=== (E) two-corrections: 선도 적분 ===")
def Dawson(b):
    return mp.e ** (-b * b / 2) * mp.quad(lambda t: mp.e ** (t * t / 2), [0, b])
def BorldR(b):
    return mp.e ** (b * b / 2) * (2 - 2 * b * Dawson(b))
ninf = 2 / mp.sqrt(mp.pi)
def F0(z):
    inner = mp.quad(lambda r: r ** 2 * mp.e ** ((1 - r ** 2) * z ** 2 / 2) * ((1 - r ** 2) * z ** 2 + (1 - r ** 2) ** 2 * z ** 4 / 4) * BorldR(r * z) / mp.sqrt(2 * mp.pi), [0, 1])
    return -ninf * z ** 4 * mp.e ** (-z * z) * inner
def F1(z):
    inner = mp.quad(lambda r: r ** 2 * mp.e ** ((1 - r ** 2) * z ** 2 / 2) * ((1 - r ** 2) * z ** 2 + (1 - r ** 2) ** 2 * z ** 4 / 4) * (mp.mpf(4) / 3 * r ** 2 * z ** 2 - mp.mpf(2) / 3 * r * z ** 4), [0, 1])
    return -ninf * z ** 4 * mp.e ** (-z * z) * inner
mp.mp.dps = 15
print("int F0 =", 2 * mp.quad(F0, [0, 1, 2, 4, 8]))
print("int F1 =", 2 * mp.quad(F1, [0, 1, 2, 4, 8]), " 46sqrt2-12 =", 46 * mp.sqrt(2) - 12)
print("J leading:", mp.quad(lambda z: z ** 3 * mp.e ** (-z * z / 2) * ((mp.mpf(4) / 15) * z ** 3 - z / 3), [-mp.inf, mp.inf]), 3 * mp.sqrt(2 * mp.pi))
# beta*Dawson max
print("max beta*Dawson:", max(b * Dawson(mp.mpf(b)) for b in [0.5 * i for i in range(1, 40)]))
mp.mp.dps = 20

print("=== (E2) Borel 꼬리 전개 (4.14) 수치 점검 ===")
def bor(j):
    return mp.e ** (-j) * mp.mpf(j) ** (j - 1) / mp.factorial(j)
def bortail(k, Z):
    # Bor(j;Z)=Bor(j) Z^{-1} (Z e^{1-Z})^j
    s = mp.mpf(0)
    q = Z * mp.e ** (1 - Z)
    pw = mp.mpf(1)
    for j in range(1, k + 1):
        pw *= q
        s += bor(j) * pw
    return 1 - s / Z
def Borld(phi):
    return 2 + mp.quad(lambda w: w ** (-1.5) * (1 - mp.e ** (-phi * w)), [0, 1])
for k, G, TR, TI in ((30000, mp.mpf(1) / 16, lambda b: mp.mpf(3) / 5 + mp.mpf(12) / 5 * b ** 2 + mp.mpf(3) / 2 * b ** 4 + b ** 6 / 25, lambda b: mp.mpf(1) / 100 + mp.mpf(201) / 100 * b + mp.mpf(7) / 10 * b ** 3 + b ** 4 / 500 + b ** 5 / 50000 + b ** 7 / 500000),
                    (10000, mp.mpf(1) / 8, lambda b: mp.mpf(3) / 5 + mp.mpf(12) / 5 * b ** 2 + mp.mpf(8) / 5 * b ** 4 + b ** 6 / 25, lambda b: mp.mpf(1) / 100 + mp.mpf(201) / 100 * b + mp.mpf(3) / 4 * b ** 3 + b ** 4 / 250 + b ** 5 / 10 ** 4 + b ** 7 / 10 ** 5)):
    eps = 1 / mp.sqrt(k)
    print("k=%d" % k)
    for beta in (0.3, 1.0, 2.5, 5.0, 8.0, float(G * mp.sqrt(k))):
        beta = mp.mpf(beta)
        Z = 1 + 1j * beta * eps
        val = mp.sqrt(k) * bortail(k, Z)
        reerr = abs(mp.re(val) - BorldR(beta) / mp.sqrt(2 * mp.pi) - mp.mpf(4) / 3 * beta ** 2 * eps)
        imerr = abs(mp.im(val) - beta)
        reb = eps ** 2 * mp.e ** (beta ** 2 / 2) * TR(beta) / mp.sqrt(2 * mp.pi)
        imb = eps * mp.e ** (beta ** 2 / 2) * TI(beta) / mp.sqrt(2 * mp.pi)
        phi = -k * (mp.log(Z) + 1 - Z)
        print("  beta=%.3f re_err=%.3e bound=%.3e ok=%s | im_err=%.3e bound=%.3e ok=%s | |phi|/beta^2=%.4f" % (beta, reerr, reb, reerr <= reb, imerr, imb, imerr <= imb, abs(phi) / beta ** 2))
        # (4.11) check
        lhs = abs(1 - Z * bortail(k, Z) - 1 + Borld(phi) / mp.sqrt(2 * mp.pi * k) - mp.mpf(2) / 3 * phi / k)
        rhs = (2 * mp.pi) ** -0.5 * k ** -1.5 * mp.e ** (-mp.re(phi)) * (mp.mpf(5) / 9 + mp.mpf(2) / 3 * abs(phi) + mp.mpf(13) / 12 * abs(phi) ** 2)
        print("     (4.11) err=%.3e bound=%.3e ok=%s" % (lhs, rhs, lhs <= rhs))

print("(F) is in 검토전체10_P2_장4_F.py")
print("done")
