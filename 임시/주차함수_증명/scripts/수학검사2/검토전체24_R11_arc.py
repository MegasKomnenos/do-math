# -*- coding: utf-8 -*-
# R11 검산: D.central-gap-rational-audit 의 두 호 상계 식을 k=10000에서 평가, D.critical-window-rig 의 급수 상수
from mpmath import mp, mpf, exp, pi, factorial, binomial, zeta, cos, sin, log, sqrt
mp.dps = 40
k = mpf(10000); G = mpf(1) / 8; R = mpf('1.0079'); far = mpf('4.031425')
yk = mpf(63) / 8192 * k - mpf(127) / 16384
def I(m): return sum(binomial(m, i) * (G * G) ** (m - i) * 2 ** i * factorial(i) / (k - 1) ** (i + 1) for i in range(m + 1))
D = k ** 3 * 2 * k ** 2 * 3 * exp(-yk) * (2 * R / G * (I(3) + k / 4 * I(4)) + mpf(22) / 7 * R * exp(-(k - 1)) * (far ** 3 + k / 4 * far ** 4))
J = k ** 3 * mpf('0.4503') * mpf(1) / 2 * exp(-yk) * (2 * R / G * 3 / k + mpf(22) / 7 * R * far ** 2)
print("k^3|b_D^arc| <=", mp.nstr(D, 6), "  k^{5/2}|b_J^arc| <=", mp.nstr(J, 6))
# critical window series constants
l = lambda m: (2 + mpf(1) / m) * zeta(2 * m) / pi ** (2 * m)
print("l1,l2,l3 =", l(1), l(2), l(3), 1 / mpf(36), 1 / mpf(405))
print("sum 2m l_m 4^(1-m) =", mp.nstr(sum(2 * m * l(m) * mpf(4) ** (1 - m) for m in range(1, 60)), 10))
print("sum_{m>=2} l_m 4^(1-m) =", mp.nstr(sum(l(m) * mpf(4) ** (1 - m) for m in range(2, 60)), 10))
print("log et(1/2) =", mp.nstr(sum(l(m) * mpf(4) ** (-m) for m in range(1, 60)), 12))
print("lg_ku, L_ku, lg_kuku, L_kuku consts:",
      mp.nstr(sum(6 * m * (m - 1) * l(m) * mpf(4) ** (1 - m) for m in range(2, 60)), 8),
      mp.nstr(sum(3 * (m - 1) * l(m) * mpf(4) ** (1 - m) for m in range(2, 60)), 8),
      mp.nstr(sum(2 * m * 3 * (m - 1) * (3 * m - 4) * l(m) * mpf(4) ** (1 - m) for m in range(2, 60)), 8),
      mp.nstr(sum(3 * (m - 1) * (3 * m - 4) * l(m) * mpf(4) ** (1 - m) for m in range(2, 60)), 8))
print("e^0.085-e^0.0761 =", exp(mpf('0.085')) - exp(mpf('0.0761')), " 1-cos(0.39) =", 1 - cos(mpf('0.39')), " 0.1666*0.39^3 =", mpf('0.1666') * mpf('0.39') ** 3)
print("e^0.1267-e^0.1108 =", exp(mpf('0.1267')) - exp(mpf('0.1108')), " 1-cos(0.475) =", 1 - cos(mpf('0.475')), " 0.1666*0.475^3 =", mpf('0.1666') * mpf('0.475') ** 3)
kk = mpf(10001)
print("arc: log(0.029 k^1.5 e^-0.085k) =", log(mpf('0.029')) + 1.5 * log(kk) - mpf('0.085') * kk, " pi/8*1.03/8/1.8 =", pi / 8 * mpf('1.03') / 8 / mpf('1.8'))
print("real: log(177 k^-1/6 e^-0.1267k) =", log(mpf(177)) - log(kk) / 6 - mpf('0.1267') * kk, " pi/0.0178 =", pi / mpf('0.0178'), " code: ", log(pi / mpf('0.0048')) - log(kk) / 6 - mpf('0.1267') * kk)
print("0.009*10001^(2/3) =", mpf('0.009') * kk ** (mpf(2) / 3), " 10001^(-1/3) =", kk ** (-mpf(1) / 3), " (1.0307e-4)^-3 =", mpf('1.0307e-4') ** -3, " 0.0015/1.25^12 =", mpf('0.0015') / mpf('1.25') ** 12)
# xi constants on 0<a<=1
import mpmath
def xi(a): return mpmath.exp(1j * a) * mpmath.exp(1 - mpmath.exp(1j * a))
vals = [(abs(xi(a) - 1) / a ** 2, (xi(a) - 1).imag / a ** 3) for a in [mpf(i) / 2000 for i in range(1, 2001)]]
print("min/max |xi-1|/a^2 =", mp.nstr(min(v[0] for v in vals), 8), mp.nstr(max(v[0] for v in vals), 8), " min Im(xi-1)/a^3 =", mp.nstr(min(v[1] for v in vals), 8), " (1-cos1) =", 1 - cos(mpf(1)))
