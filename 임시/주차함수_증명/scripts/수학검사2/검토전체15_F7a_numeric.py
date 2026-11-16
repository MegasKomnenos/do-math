# F7a 검산 2: 7.4절의 수치·기호 주장.
# (a) 명제 pair-check-10000: 경우 수 10,725와 (7.11) 우변의 최솟값·자리
# (b) 꼬리 삼중 (7.12), nu_P 표 (float 재현), tf M^{3/2}
# (c) n_M(k)/k^{3/2} 끝값, 0.8165 k^{3/2} > 2k+1, Robbins 비 1.84, 2.08, 0.83
# (d) polar-PD 상수, 2002^{4/3}
# (e) sympy: M_2/M_0, U_4/V_4, H_0..H_2 전개, 'k 계수 20'
# (f) mpmath: k=10000, nu=1..5 의 d, M_0 실제값 vs 하계
from fractions import Fraction as Fr
from math import comb, factorial, exp, sqrt, log, ceil, floor, e as E
import sys

print("== (a) pair-check-10000 ==")
k = 10000
def pis(q): return Fr(q * (q - 1), 2 * (k + 1))
def exbar(q): p = pis(q); return q + (k + q) * p / (1 - p)
cnt = 0; mn = None
for q in range(1, 50):
    for qp in range(q, 50):
        if q + qp > 50: break
        for j in range(0, 50 - q - qp + 1):
            cnt += 1
            v = 1 - Fr(j, k) * (exbar(q) + exbar(qp)) - (exbar(q) * (qp - 1) + exbar(qp) * (q - 1)) / (2 * k)
            if mn is None or v < mn[0]: mn = (v, (q, qp, j))
print("cases", cnt, "min", float(mn[0]), mn[1])

print("== (b) tail triples / nu_P ==")
from math import lgamma
def Bor(m): return exp(-m + (m - 1) * log(m) - lgamma(m + 1))
def kebar(K1, M):
    return 3 * (M - 1) / (2 * (K1 + 1)) + (M - 1) * (3 * M - 4) / (12 * (K1 + 1) ** 2) + (M - 1) ** 2 / (2 * (K1 + 1) * (K1 + 2 - M)) + (M - 1) ** 4 / (12 * (K1 + 1) ** 2 * (K1 + 2 - M))
triples = [(10 ** 4, 120, 0.54), (2 * 10 ** 4, 250, 0.593), (10 ** 5, 300, 0.522), (10 ** 5, 450, 0.548), (10 ** 6, 700, 0.519)]
for K1, M, tf in triples:
    kb = kebar(K1, M)
    worst = min((tf * q ** 1.5 - exp(kb) * sum(Bor(s + 1) * ((q - 1 - s) + tf * (q - 1 - s) ** 1.5) for s in range(0, q - 1))) / (tf * q ** 1.5) for q in range(2, M + 1))
    print(f"triple {K1},{M},{tf}: kebar={kb:.4f} min rel margin={worst:.3e} tfM^1.5={tf*M**1.5:.0f} <K1? {tf*M**1.5<K1}")
def nuP(K1, M, tf):
    kk = K1
    def nhat(q): return 0.0 if q == 1 else tf * q ** 1.5 / kk
    def exhat(q): h = nhat(q); return q + (kk + q) * h / (1 - h)
    def lb(q, qp, j): return 1 - j / kk * (exhat(q) + exhat(qp)) - (exhat(q) * (qp - 1) + exhat(qp) * (q - 1)) / (2 * kk)
    nu = 1
    while True:
        bad = False; worst = (9, None)
        for q in range(1, nu):
            qp = nu - q  # j=0 .. with j decreasing lb, check j = nu-q-qp = 0? No: shell nu means q+qp+j=nu; lb decreasing in j so check j=nu-q-qp for each (q,qp) with q+qp<=nu
        for q in range(1, nu + 1):
            for qp in range(q, nu - q + 1):
                j = nu - q - qp
                if q > M or qp > M: bad = True; break
                v = lb(q, qp, j)
                if v < worst[0]: worst = (v, (q, qp, j))
                if v <= 0: bad = True
            if bad: break
        if bad: return nu - 1, prev
        prev = worst
        nu += 1
cols = [(12000, 120, 0.54), (13000, 120, 0.54), (14000, 120, 0.54), (15000, 120, 0.54), (20000, 120, 0.54), (30000, 250, 0.593), (50000, 250, 0.593), (10 ** 5, 300, 0.522), (2 * 10 ** 5, 450, 0.548), (5 * 10 ** 5, 450, 0.548), (10 ** 6, 700, 0.519)]
for K1, M, tf in cols:
    print("K1", K1, "nu_P(float) =", nuP(K1, M, tf))

print("== (c) moment threshold numbers ==")
for kk, nM in [(841, 20507), (2000, 73032)]:
    print(kk, nM, nM / kk ** 1.5)
print("0.8165*841^1.5 =", 0.8165 * 841 ** 1.5, "> 2k+1 =", 2 * 841 + 1)
print("(1.50005)^1.5 e^(1/240000) =", 1.50005 ** 1.5 * exp(1 / 240000), "*2/sqrt(pi)=", 1.84 * 2 / sqrt(3.141592653589793), "Bn<=", 2.08 / sqrt(2 * 3.141592653589793))
print("13*501^2/100 =", 13 * 501 ** 2 / 100, " 13*840^2/100=", 13 * 840 ** 2 / 100)
print("== (d) polar-PD ==")
print("2002^(4/3) =", 2002 ** (4 / 3), "ceil", ceil(2002 ** (4 / 3)))
print("3130^(4/3)=", 3130 ** (4 / 3), " minus 3*3130 =", ceil(3130 ** (4 / 3)) - 3 * 3130)
print("0.7*2001/2002 =", 0.7 * 2001 / 2002, " 0.3^1.5/2 =", 0.3 ** 1.5 / 2)
print("2 e^{-5.3146*0.6996} =", 2 * exp(-5.3146 * 0.6996), " 0.0821 e^{-3/25233}=", 0.0821 * exp(-3 / 25233), " varsigma needed:", -log(0.0820 / 2) / 0.6996)
print("ceil(0.3*2001)=", ceil(0.3 * 2001), "<= k-2")
print("== integer-strips counts ==")
c1 = sum(2 * kk + 40 - max(20001, 2 * kk + 1) + 1 for kk in range(9981, 11100))
c2 = sum(2 * kk + 102 - max(2 * kk + 41, 20001) + 1 for kk in range(9950, 12000) if 2 * kk + 102 >= max(2 * kk + 41, 20001))
c3 = 1000 * (102 - 59 + 1) + 1000 * (102 - 80 + 1) + 1000 * (102 - 96 + 1)
print("(가)", c1, "(나)+(다)", c2 + c3, "(나)", c2, "(다)", c3)
print("(20001-102)/2 =", (20001 - 102) / 2)

print("== (e) sympy ==")
import sympy as sp
n, y, d, nu, kk, w, th = sp.symbols('n y d nu k w theta')
# He_{n}/He_{n-1} = n + d ; backward recurrence He_{j-1} = (N He_j - He_{j+1})/(y j)
N_ = n + y + 1
He_n = n + d; He_nm1 = sp.Integer(1)
He_nm2 = (N_ * He_nm1 - He_n) / (y * (n - 1))
He_nm3 = (N_ * He_nm2 - He_nm1) / (y * (n - 2))
He_nm4 = (N_ * He_nm3 - He_nm2) / (y * (n - 3))
He_nm5 = (N_ * He_nm4 - He_nm3) / (y * (n - 4))
ff = sp.ff
M0 = He_n - n * He_nm1
M2 = He_n - 3 * n * He_nm1 + 3 * ff(n, 2) * He_nm2 - ff(n, 3) * He_nm3
M4 = He_n - 5 * n * He_nm1 + 10 * ff(n, 2) * He_nm2 - 10 * ff(n, 3) * He_nm3 + 5 * ff(n, 4) * He_nm4 - ff(n, 5) * He_nm5
r2 = sp.simplify(M2 / M0 - (1 - 2 * n / y + n * (n + 1) / y ** 2 - n * (n + 1) / (y ** 2 * d)))
print("(4.9) M2/M0 formula residual:", r2)
U2 = 1 + (2 * nu + 2) / kk + nu * (nu + 1) / kk ** 2
V2 = 4 + (4 * nu + 2) / kk + nu * (nu + 1) / kk ** 2
U4 = 1 + (4 * nu + 16) / kk + (6 * nu ** 2 + 30 * nu + 18) / kk ** 2 + (4 * nu ** 3 + 17 * nu ** 2 + 15 * nu + 2) / kk ** 3 + nu * (nu + 1) ** 3 / kk ** 4
V4 = 4 + (12 * nu + 38) / kk + (13 * nu ** 2 + 49 * nu + 22) / kk ** 2 + (6 * nu ** 3 + 21 * nu ** 2 + 17 * nu + 2) / kk ** 3 + nu * (nu + 1) ** 3 / kk ** 4
sub = {n: 2 * kk + nu, y: kk}
print("U2,V2 residual:", sp.simplify((M2 / M0).subs(sub) - (U2 - V2 / d)))
print("U4,V4 residual:", sp.simplify((M4 / M0).subs(sub) - (U4 - V4 / d)))
# 'k coefficient 20': n(n+1) - d[(n-y)^2+n] with d = 4 - (26+4nu+8th)/k, y = k - th, n=2k+nu
dd = 4 - (26 + 4 * nu + 8 * th) / kk
expr = sp.expand(((n * (n + 1)) - dd * ((n - y) ** 2 + n)).subs({n: 2 * kk + nu, y: kk - th}))
print("diff poly in k:", sp.collect(expr, kk))
# H expansion
gam = sp.symbols('gamma')
ups = (1 + gam) / 2
C1 = (1 - ups) / gam ** 2; C2 = -(1 - ups) * (2 + ups) / gam ** 5; C3 = 5 * (1 - ups) * (6 + gam - gam ** 2) / (2 * gam ** 8)
Nk = 3 + (nu + 1 - th) * w
xx = w * (1 - th * w) / Nk ** 2
xn = (2 + (nu - 1) * w) * (1 - th * w) / Nk ** 2
nm = 1 + (2 * nu + 10 + 2 * th) * w + ((nu + 1) ** 2 + 2 * (nu - 3) * th + th ** 2) * w ** 2
print("1-4xn - nm/Nk^2 residual:", sp.simplify(1 - 4 * xn - nm / Nk ** 2))
gamma_expr = sp.sqrt(nm) / Nk
uhat = (ups + xx * C1 + xx ** 2 * C2 + xx ** 3 * C3).subs(gam, gamma_expr)
H = sp.series((Nk * uhat - 2 - nu * w) / w, w, 0, 3).removeO()
H = sp.expand(H)
print("H0 =", sp.simplify(H.coeff(w, 0)), " H1 =", sp.factor(H.coeff(w, 1)), " H2 =", sp.expand(H.coeff(w, 2)))
print("expected H2 =", sp.expand(506 + 97 * nu + 5 * nu ** 2 + (168 + 16 * nu) * th + 12 * th ** 2))
# C1 at gamma = 1/3 + (2nu+14+4th)/(9k)
print("C1 series:", sp.series(C1.subs(gam, sp.Rational(1, 3) + (2 * nu + 14 + 4 * th) * w / 9), w, 0, 2))
print("C2(1/3)=", C2.subs(gam, sp.Rational(1, 3)), " C1(1/3)=", C1.subs(gam, sp.Rational(1, 3)))
# kernel-bound algebra: log ratio terms
s_, m_ = sp.symbols('s m', positive=True)
W = s_ + 1; J = W / (m_ + 1)
lhs = W + (m_ + 1) * (-J + J ** 2 / 2 + J ** 3 / 6 + J ** 4 / (12 * (1 - J))) + (J + J ** 2 / (2 * (1 - J))) - s_ * (s_ + 1) / (2 * (m_ + 1)) - s_ * (s_ + 1) * (2 * s_ + 1) / (12 * (m_ + 1) ** 2)
ke = 3 * W / (2 * (m_ + 1)) + W * (3 * s_ + 2) / (12 * (m_ + 1) ** 2) + W ** 2 / (2 * (m_ + 1) * (m_ - s_)) + W ** 4 / (12 * (m_ + 1) ** 2 * (m_ - s_))
print("kernel-bound algebra residual:", sp.simplify(lhs - ke))
# quadratic for off
off = sp.symbols('off')
U_ = n + off
print("off quadratic:", sp.expand((U_ ** 2 - (n + kk + 1) * U_ + n * kk).subs(n, 2 * kk + nu)))
print("1-4q numerator:", sp.expand(((3 * kk + nu + 1) ** 2 - 4 * (2 * kk + nu) * kk) - ((kk + nu + 3) ** 2 - 4 * (nu + 2))))

print("== (f) mpmath Hermite at k=10000 ==")
import mpmath as mp
mp.mp.dps = 60
def hermite_d_M0(k, nu, theta=0):
    y = mp.mpf(k) - theta; n = 2 * k + nu; N = n + y + 1
    H0 = mp.mpf(1); H1 = N
    for j in range(2, n + 1):
        H0, H1 = H1, N * H1 - (j - 1) * y * H0
    dval = H1 / H0 - n
    # M0 = e^{-y/2} He_{n-1} d / p_n ; p_n=(n+1)^{n-1}
    logM0 = -y / 2 + mp.log(H0) + mp.log(dval) - (n - 1) * mp.log(n + 1)
    M0 = mp.e ** logM0
    # M2/M0, M4/M0 via formulas
    r2 = 1 - 2 * n / y + n * (n + 1) / y ** 2 - n * (n + 1) / (y ** 2 * dval)
    return dval, M0, r2
for nu_ in [1, 2, 5, 19, 40, 102, 600]:
    dval, M0, r2 = hermite_d_M0(10000, nu_)
    lb = 4 * mp.sqrt(2) * (1 - (23.75 + 2.5 * nu_) / 10000)
    print(f"nu={nu_}: d={mp.nstr(dval,12)} in [{mp.nstr(4-(26+4*nu_)/mp.mpf(10000),10)},4)? M0={mp.nstr(M0,10)} >= lb {mp.nstr(lb,10)}? {M0>=lb}  k M2/M0={mp.nstr(10000*r2,8)}  g_k={mp.nstr(2-10000*r2,8)}")
dval, M0, r2 = hermite_d_M0(10000, 1, theta=1)
print("theta=1 nu=1: d=", mp.nstr(dval, 12), " M2/M0<0?", r2 < 0)
