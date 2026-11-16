# K2 검산 3: 3장 극한 상수, 4.3절 수치 상수, g(kappa) 전개 계수, 잔차의 Laurent 계수, 도함수 식.
from fractions import Fraction as Fr
import mpmath as mp
import sympy as sp

mp.mp.dps = 40
out = []
# 3장: 밀도 꼬리 상수 3/sqrt(2 pi) vs 곱 표현에서 계산한 값
G = mp.gamma
C_tail = 2 * G(mp.mpf(2) / 3) / (mp.sqrt(mp.pi) * G(mp.mpf(1) / 6)) * mp.sqrt(mp.mpf(3) / 2) * G(mp.mpf(1) / 3) / G(mp.mpf(5) / 6)
out.append("tail: Pr(X>x) ~ C x^{-3/2}, C from product rep = %s ; sqrt(2/pi) = %s" % (mp.nstr(C_tail, 12), mp.nstr(mp.sqrt(2 / mp.pi), 12)))
out.append("density const 1.5*C = %s ; 3/sqrt(2pi) = %s" % (mp.nstr(1.5 * C_tail, 12), mp.nstr(3 / mp.sqrt(2 * mp.pi), 12)))
# Legendre: Gamma(1/3)Gamma(5/6) = 2^{1/3} sqrt(pi) Gamma(2/3)
out.append("Legendre check: %s" % mp.nstr(G(mp.mpf(1) / 3) * G(mp.mpf(5) / 6) - 2 ** (mp.mpf(1) / 3) * mp.sqrt(mp.pi) * G(mp.mpf(2) / 3), 5))
# Mellin formula at sigma=0.7 vs product moments
s = mp.mpf('0.7')
mell = (mp.mpf(3) / 2) ** (s / 3) * G(1 + 2 * s / 3) * G(mp.mpf(5) / 6 - s / 3) / G(mp.mpf(5) / 6) * G(mp.mpf(1) / 2 - s / 3) * G(mp.mpf(2) / 3) / (G(mp.mpf(1) / 2) * G(mp.mpf(2) / 3 - s / 3))
# numeric moments: E[E^{2s/3}] etc
mE = G(1 + 2 * s / 3)
mH = mp.quad(lambda u: u ** (-s / 3) * u ** (mp.mpf(5) / 6 - 1) * mp.exp(-u), [0, mp.inf]) / G(mp.mpf(5) / 6)
mV = mp.quad(lambda u: u ** (-s / 3) * u ** (-mp.mpf(1) / 2) * (1 - u) ** (-mp.mpf(5) / 6), [0, 1]) / mp.beta(mp.mpf(1) / 2, mp.mpf(1) / 6)
out.append("Mellin at 0.7: formula %s ; direct %s" % (mp.nstr(mell, 12), mp.nstr((mp.mpf(3) / 2) ** (s / 3) * mE * mH * mV, 12)))
# (3/4)^{3/2}
out.append("(3/4)^{3/2} = %s ; 2^{-3}3^{3/2} = %s" % (mp.nstr((mp.mpf(3) / 4) ** 1.5, 8), mp.nstr(3 ** 1.5 / 8, 8)))

# 4장 상수
a0 = mp.quad(lambda w: mp.exp(-w ** 3 / 3), [0, mp.inf])
a1 = mp.quad(lambda w: w * mp.exp(-w ** 3 / 3), [0, mp.inf])
out.append("a0 = %s (1.287899<a0<1.2879: %s) ; a1 = %s (0.938892<a1<0.939: %s)" % (mp.nstr(a0, 10), 1.287899 < a0 < 1.2879, mp.nstr(a1, 10), 0.938892 < a1 < 0.939))
w = Fr(699, 100)
val = w - Fr(7, 2) - (6 * w + Fr(3, 4)) / 31 - (13 * w / 2) / 961 - 12 * w / 30000
out.append("Cor (na) rational = %s ; equals 495594511/240250000: %s ; >2: %s ; float %.5f" % (val, val == Fr(495594511, 240250000), val > 2, float(val)))
w = Fr(698, 100)
k13 = mp.mpf(10000) ** (-mp.mpf(1) / 3)
k23 = mp.mpf(10000) ** (-mp.mpf(2) / 3)
v = mp.mpf(698) / 100 - mp.mpf(7) / 2 - (4 * mp.mpf(698) / 100 + mp.mpf(1) / 2) * mp.mpf('1.2879') * mp.mpf('0.0464159') - (13 * mp.mpf(698) / 200) * mp.mpf('0.939') * k23 - 12 * mp.mpf(698) / 100 / 10000
out.append("Cor (da) value with upper bounds = %s (>=1.6809: %s); k^{-1/3}=%s" % (mp.nstr(v, 8), v >= mp.mpf('1.6809'), mp.nstr(k13, 8)))
out.append("assembly k>=10000: 5.642*1.6809*0.39893-0.0163-3.554 = %s" % mp.nstr(mp.mpf('5.642') * mp.mpf('1.6809') * mp.mpf('0.39893') - mp.mpf('0.0163') - mp.mpf('3.554'), 8))
out.append("assembly k>=30000: 11/2*39/100*2-7/2 = %s" % mp.nstr(mp.mpf(11) / 2 * mp.mpf(39) / 100 * 2 - mp.mpf(7) / 2, 6))
out.append("46sqrt2-12 = %s ; minus 5000/173 and 0.02 = %s (>24: %s)" % (mp.nstr(46 * mp.sqrt(2) - 12, 8), mp.nstr(46 * mp.sqrt(2) - 12 - mp.mpf(5000) / 173 - mp.mpf('0.02'), 8), 46 * mp.sqrt(2) - 12 - mp.mpf(5000) / 173 - mp.mpf('0.02') > 24))
out.append("46sqrt2-12-54.6828 = %s (>-1.63: %s)" % (mp.nstr(46 * mp.sqrt(2) - 12 - mp.mpf('54.6828'), 8), 46 * mp.sqrt(2) - 12 - mp.mpf('54.6828') > -1.63))
out.append("J bound k>=30000: 0.451*3*2.51+0.056+0.01 = %s ; 3sqrt(2pi)=%s ; sqrt(2pi)=%s" % (mp.nstr(mp.mpf('0.451') * 3 * mp.mpf('2.51') + mp.mpf('0.056') + mp.mpf('0.01'), 6), mp.nstr(3 * mp.sqrt(2 * mp.pi), 8), mp.nstr(mp.sqrt(2 * mp.pi), 8)))
out.append("J bound k>=10000: 0.4503*3*2.50663+1675.2/10000 = %s (<3.554: %s)" % (mp.nstr(mp.mpf('0.4503') * 3 * mp.mpf('2.50663') + mp.mpf('1675.2') / 10000, 8), mp.mpf('0.4503') * 3 * mp.mpf('2.50663') + mp.mpf('1675.2') / 10000 + mp.mpf('1e-20') < 3.554))
out.append("Bn bound sqrt2/pi*e^{1/30000} = %s ; e^{1/10000} version = %s" % (mp.nstr(mp.sqrt(2) / mp.pi * mp.exp(mp.mpf(1) / 30000), 8), mp.nstr(mp.sqrt(2) / mp.pi * mp.exp(mp.mpf(1) / 10000), 8)))
out.append("4sqrt2(1-26/10000) = %s ; (1-26/30000) = %s" % (mp.nstr(4 * mp.sqrt(2) * (1 - mp.mpf(26) / 10000), 8), mp.nstr(4 * mp.sqrt(2) * (1 - mp.mpf(26) / 30000), 8)))
out.append("Bor(k)k^{3/2} lower: (2pi)^{-1/2}(1-1/120000) = %s ; (2pi)^{-1/2}e^{-1/(12*30000)} = %s" % (mp.nstr((2 * mp.pi) ** -0.5 * (1 - mp.mpf(1) / 120000), 8), mp.nstr((2 * mp.pi) ** -0.5 * mp.exp(-mp.mpf(1) / 360000), 8)))
out.append("x bound k/(3k-1)^2 at k=10000: %s" % mp.nstr(mp.mpf(10000) / (29999 ** 2), 8))
out.append("y_k: 255/131072 vs 1/520: %s vs %s" % (mp.nstr(mp.mpf(255) / 131072, 8), mp.nstr(mp.mpf(1) / 520, 8)))
out.append("k^5 e^{-k/520} at k=30000: %s" % mp.nstr(mp.mpf(30000) ** 5 * mp.exp(-mp.mpf(30000) / 520), 6))
out.append("130(k/256)^6 e^{-k/512} at k=30000: %s" % mp.nstr(130 * (mp.mpf(30000) / 256) ** 6 * mp.exp(-mp.mpf(30000) / 512), 6))

# g(kappa) 전개 (sympy, 정확)
kap, th, nu_s = sp.symbols('kappa theta nu')
def g_series(nu, theta, order=3):
    Nt = 3 + (nu + 1 - theta) * kap
    x = (1 - theta * kap) * kap / Nt ** 2
    xn = (2 + (nu - 1) * kap) * (1 - theta * kap) / Nt ** 2
    gam = sp.sqrt(1 - 4 * xn)
    ups = (1 + gam) / 2
    C1 = (1 - ups) / gam ** 2
    C2 = -(1 - ups) * (2 + ups) / gam ** 5
    C3 = sp.Rational(5, 2) * (1 - ups) * (6 + gam - gam ** 2) / gam ** 8
    uhat = ups + x * C1 + x ** 2 * C2 + x ** 3 * C3
    g = (Nt * uhat - 2 - nu * kap) / kap
    return sp.series(g, kap, 0, order).removeO()
for nu in (0, -1):
    for theta in (0, 1, sp.Rational(1, 2)):
        se = sp.expand(g_series(nu, theta))
        c0, c1, c2 = [sp.nsimplify(se.coeff(kap, i)) for i in range(3)]
        pred1 = -(26 + 4 * nu + 8 * theta)
        pred2 = 506 + 97 * nu + 5 * nu ** 2 + (168 + 16 * nu) * theta + 12 * theta ** 2
        out.append("g series nu=%d theta=%s: c0=%s c1=%s (pred %s) c2=%s (pred %s)" % (nu, theta, c0, c1, pred1, c2, pred2))

# 잔차 R(iota)의 x-전개 계수 (gamma의 Laurent 다항식)
gm, xx = sp.symbols('gamma x', positive=True)
def ups_of_gamma(gg):
    return (1 + gg) / 2
def C1g(gg):
    return (1 - ups_of_gamma(gg)) / gg ** 2
def C2g(gg):
    return -(1 - ups_of_gamma(gg)) * (2 + ups_of_gamma(gg)) / gg ** 5
def C3g(gg):
    return sp.Rational(5, 2) * (1 - ups_of_gamma(gg)) * (6 + gg - gg ** 2) / gg ** 8
def uhat_g(gg):
    return ups_of_gamma(gg) + xx * C1g(gg) + xx ** 2 * C2g(gg) + xx ** 3 * C3g(gg)
iota = (1 - gm ** 2) / 4
gm_shift = sp.sqrt(gm ** 2 + 4 * xx)  # gamma(iota - x)
R = (uhat_g(gm) - 1) * uhat_g(gm_shift) + iota
Rs = sp.series(R, xx, 0, 5).removeO()
coeffs = [sp.simplify(sp.expand(Rs.coeff(xx, i))) for i in range(5)]
out.append("R coefficients x^0..x^3: %s" % coeffs[:4])
out.append("R x^4 coefficient at gamma=1/3: %s" % sp.nsimplify(coeffs[4].subs(gm, sp.Rational(1, 3))))
# 도함수 식 확인: d/diota = (-2/gamma) d/dgamma
def Dio(expr, times):
    for _ in range(times):
        expr = sp.simplify(-2 / gm * sp.diff(expr, gm))
    return expr
out.append("ups'''' = %s (text -120 g^-7)" % sp.simplify(Dio(ups_of_gamma(gm), 4)))
out.append("C1''' = %s (text 192g^-8-60g^-7)" % sp.simplify(Dio(C1g(gm), 3) - (192 * gm ** -8 - 60 * gm ** -7)))
out.append("C2'' - text = %s" % sp.simplify(Dio(C2g(gm), 2) + (175 * gm ** -9 - 96 * gm ** -8 - 15 * gm ** -7)))
out.append("C3' - text = %s" % sp.simplify(Dio(C3g(gm), 1) - sp.Rational(5, 2) * (48 * gm ** -10 - 35 * gm ** -9 - 12 * gm ** -8 + 5 * gm ** -7)))
# m1,m2,m3: coefficients of uhat(iota - x) expansion
us = sp.series(uhat_g(gm_shift), xx, 0, 4).removeO()
m1 = sp.simplify(us.coeff(xx, 1) - ups_of_gamma(gm) / gm ** 2)
m2 = sp.simplify(us.coeff(xx, 2) - (C2g(gm) - 2 / gm ** 4))
m3 = sp.simplify(us.coeff(xx, 3) - (C3g(gm) + sp.Rational(5, 2) * (5 - gm ** 2) / gm ** 7))
out.append("m1,m2,m3 differences from text: %s %s %s" % (m1, m2, m3))
# 적분 항등식 (gauss-contraction 다)
io = sp.symbols('iota')
upsI = (1 + sp.sqrt(1 - 4 * io)) / 2
gamI = sp.sqrt(1 - 4 * io)
F1 = io * sp.log(upsI) + (1 - upsI) ** 2 / 2
out.append("d/diota[iota log ups + (1-ups)^2/2] - log ups = %s" % sp.simplify(sp.diff(F1, io) - sp.log(upsI)))
F2 = sp.log(upsI) - sp.log(gamI) / 2
out.append("d/diota[log ups - log gamma/2] - C1/ups = %s" % sp.simplify(sp.diff(F2, io) - ((1 - upsI) / gamI ** 2) / upsI))
# 3.4절 적분: d/dphi 2 sqrt(phi/(1-phi)) = phi^{-1/2}(1-phi)^{-3/2}
ph = sp.symbols('phi', positive=True)
out.append("eta antiderivative check: %s" % sp.simplify(sp.diff(2 * sp.sqrt(ph / (1 - ph)), ph) - ph ** sp.Rational(-1, 2) * (1 - ph) ** sp.Rational(-3, 2)))
# P 다항식 k-계수 (gauss-coeff 셋째 단계)
kk, thh = sp.symbols('k theta')
for nu in (0, -1):
    n = 2 * kk + nu
    y = kk - thh
    a = 26 + 4 * nu + 8 * thh
    bb = 506 + 97 * nu + 5 * nu ** 2 + (168 + 16 * nu) * thh + 12 * thh ** 2
    vth = 4 - a / kk + bb / kk ** 2
    P = sp.expand(vth * ((n - y) ** 2 + n) - n * (n + 1))
    out.append("nu=%d: P expanded (k^2,k^1,k^0 coeffs): %s" % (nu, [sp.factor(sp.expand(P).coeff(kk, i)) for i in (2, 1, 0)]))
    Q1 = sp.expand(kk * P + 5 * y ** 2 * vth)
    Q2 = sp.expand(100 * kk * P + 499 * y ** 2 * vth)
    out.append("nu=%d: kP+5y^2th k^2,k coeffs: %s ; 100kP+499y^2th k^2 coeff: %s" % (nu, [sp.factor(Q1.coeff(kk, i)) for i in (2, 1)], sp.factor(Q2.coeff(kk, 2))))
    # M4/M0 center
    if nu == 0:
        f = 1 + 16 / kk + 18 / kk ** 2 + 2 / kk ** 3 - (4 + 38 / kk + 22 / kk ** 2 + 2 / kk ** 3) / (4 - 26 / kk + 506 / kk ** 2)
    else:
        f = 1 + 12 / kk - 6 / kk ** 2 - (4 + 26 / kk - 14 / kk ** 2) / (4 - 22 / kk + 414 / kk ** 2)
    out.append("nu=%d: M4/M0 center series in 1/k: %s" % (nu, sp.series(f.subs(kk, 1 / kap), kap, 0, 4)))
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체17_K2_numeric_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
