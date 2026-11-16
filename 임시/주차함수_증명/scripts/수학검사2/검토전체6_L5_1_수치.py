# 검토전체6 L5: 장6 본문 수치의 재계산 (6.1–6.5)
from mpmath import mp, mpf, sqrt, exp, log, e, pi, ceil, floor, factorial, quad
from fractions import Fraction
mp.dps = 30

def Bor(n):
    return exp(-n) * mpf(n) ** (n - 1) / factorial(n)

print("== 6.1 (6.8) 상수 ==")
C = 3; k = 4000
qs = int(ceil((C * k) ** (mpf(2) / 3)))
print("q_* at k=4000:", qs, "(본문 525)")
print("1-1.6/sqrt(525) =", 1 - mpf(1.6) / sqrt(525), "(본문 0.93017...)")
t1 = mpf(0.8) * sqrt(2) / 3 * (1 + mpf(1) / 1048)
t2 = mpf(3.923) * mpf(3) ** (-mpf(4) / 3) * mpf(4000) ** (-mpf(1) / 3)
t3 = mpf(1.5) / (3 * sqrt(525))
print("세 항:", t1, t2, t3, "합", t1 + t2 + t3, "(본문 0.3775+0.0572+0.0219=0.4566)")
print("1.2(1-2/525)^(-5/2) =", mpf(1.2) * (1 - mpf(2) / 525) ** (-mpf(2.5)), "(<=1.212)")
print("1.2(1+2/525)^(1/2) =", mpf(1.2) * (1 + mpf(2) / 525) ** mpf(0.5), "(<=1.203)")
print("1.5(1-1/525)^(-5/2) =", mpf(1.5) * (1 - mpf(1) / 525) ** (-mpf(2.5)), "(<=1.508)")
print("Up(1/2)=", sqrt(mpf(1) / 2) * 2)

print("\n== 6.2 B_2(k) ==")
def B2(k):
    k = mpf(k)
    return (1 - 1 / e) + (exp(mpf(1.5) + 1 / k) - 1) * 2 * (sqrt(k + 1) - 1) / (sqrt(2 * pi) * (k + 1))
for kk in (42, 43, 2000):
    print("B_2(%d) =" % kk, B2(kk))
print("1-1/e =", 1 - 1 / e, " e^{3/2+1/43}-1 =", exp(mpf(1.5) + mpf(1) / 43) - 1, " 2(sqrt44-1)=", 2 * (sqrt(44) - 1), " sqrt(2pi)*44=", sqrt(2 * pi) * 44)
print("1-B_2(2000) =", 1 - B2(2000), "(>=0.307?)")

print("\n== 6.2 기울인 Borel 질량 합 (정확 유리수), k=2..60 ==")
def tilt_sum(k):
    xk = Fraction(k, k + 1) ** (k - 1)
    s = Fraction(0)
    for n in range(2, k + 2):
        s += Fraction(n ** (n - 1), factorial_int(n)) * xk ** n
    return s
def factorial_int(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r
mx = (0, Fraction(0))
for kk in range(2, 61):
    s = tilt_sum(kk)
    if s > mx[1]:
        mx = (kk, s)
    assert s < 1, kk
print("최댓값 k=%d: %s = %.6f" % (mx[0], mx[1], float(mx[1])))
for kk in (3, 10, 20, 42, 43):
    print("k=%d: %.6f" % (kk, float(tilt_sum(kk))))

print("\n== 6.2 increment-bounds (다) ==")
k = mpf(2000)
print("k*rho^L(3k) =", mpf(3) / 4 * (1 - mpf(1.2) / k), " k*rho^H(3k) bound 0.307*2000/3999 =", mpf(0.307) * 2000 / 3999)
print("(k-1)log(1+1/k) >= 1-3/(2k+1)? k=2:", (2 - 1) * log(mpf(1.5)), 1 - mpf(3) / 5)

print("\n== 6.3 lemma-omega 상수 ==")
Xs = (5 - sqrt(7)) / 6
print("X* =", Xs, " f(X*) =", Xs * (1 - Xs) * (3 - 2 * Xs), " (10+7sqrt7)/54 =", (10 + 7 * sqrt(7)) / 54)
y = 50
tl_inv = 1 / (1 - mpf(0.75) / (y + 1))
print("tl^-1 <=", tl_inv, " e^{1/24+1/612}=", exp(mpf(1) / 24 + mpf(1) / 612), " 1+1/51=", 1 + mpf(1) / 51)
u = exp(mpf(1) / 24 + mpf(1) / 612) * tl_inv * (1 + mpf(1) / 51) * mpf(4) / 3
print("u <=", u, " M/G <= 0.5282*1.449 =", mpf(0.5282) * mpf(1.449), " 0.52815*u=", mpf(0.52815) * u)
print("L/G (V>=2) <=", mpf(1.5) / 53 * (mpf(4) / 3) * mpf(0.5) * (1 + mpf(1) / 51) * tl_inv)
print("L/G (V=1) <=", mpf(1.5) / 52 * mpf(2.02) * mpf(0.51) * (1 + mpf(1) / 51) * tl_inv)
print("e^{3/(2*51)} =", exp(mpf(3) / 102), " (<=1.03)")
print("e^-2 =", exp(-2), " 1.545 e^-1 =", mpf(1.545) * exp(-1))
print("2e^-2+e^-1-1.03e^-2/51 =", 2 * exp(-2) + exp(-1) - mpf(1.03) * exp(-2) / 51)
print("0.2 e^-1 *0.6 =", mpf(0.2) * exp(-1) * mpf(0.6))
y = mpf(50)
print("비 at y=50:", mpf(0.0441) * (y - 1) / (y + 3) ** 2 / (mpf(1.2) * (y + 1) / ((y + 2) ** 2 * (y + 3))))
print("1.03 e^-1 /2 =", mpf(1.03) * exp(-1) / 2, " (<=1/5)")

print("\n== 6.4 u(k), 증인 상계 ==")
def u(k):
    k = mpf(k)
    return 3 / mpf(0.35) * (mpf(1.35) + 1 / k) * (mpf(0.65) - 1 / k) ** (-mpf(1.5)) / sqrt(k)
for kk in (3131, 6667, 10000):
    print("u(%d) =" % kk, u(kk), " 2u=", 2 * u(kk))
print("u(3131)/2 =", u(3131) / 2, " 3130 factors:", 3 / mpf(0.35), mpf(1.35) + mpf(1) / 3131, (mpf(0.65) - mpf(1) / 3131) ** (-mpf(1.5)), 1 / sqrt(3131))
n = 20000
wb = mpf(1.99) + mpf(0.59963) * (n + 1) ** (mpf(2) / 3) + mpf(1.24847) * (n + 1) ** (mpf(1) / 3)
print("증인 상계 n=20000:", wb, " (<=478?)")
print("(6262)^(2/3) =", mpf(6262) ** (mpf(2) / 3), " 0.65*3131-1 =", mpf(0.65) * 3131 - 1)
print("9*(3/2)^(3/2) =", 9 * mpf(1.5) ** 1.5, " 16.54*4/3 =", mpf(16.54) * 4 / 3)
print("K>=1.35k at 3131:", mpf(1.35) * 3131)

print("\n== 6.5 V-핵심 ==")
print("50.62/sqrt(3130) =", mpf(50.62) / sqrt(3130))
print("24000/2263^1.5 =", 24000 / mpf(2263) ** 1.5)
for kk in (3131, 6667, 10000):
    k = mpf(kk)
    vp = max(kk + 1, 4000); io = 2 * kk + 1 - vp
    a = 2 * min(1, 3 * vp * mpf(io) ** (-1.5)); b = 2 * u(kk); c = mpf(50.62) / sqrt(k - 1)
    print("v(%d): %s %s %s -> %s" % (kk, a, b, c, 2 - a - b - c))
print("12000*3997^-1.5 vs 12000*3999^-1.5:", 12000 * mpf(3997) ** -1.5, 12000 * mpf(3999) ** -1.5)
cc = 1 / sqrt(2 * pi)
print("c =", cc)
print("3c(8.133+10.301c) =", 3 * cc * (mpf(8.133) + mpf(10.301) * cc))
print("1.5*2.7323*0.8051*c*(17.951+23.462c) =", mpf(1.5) * mpf(2.7323) * mpf(0.8051) * cc * (mpf(17.951) + mpf(23.462) * cc))
# c_*(0.55, 2.4978)
tp = mpf(0.55); ka = mpf(2.4978)
disc = (ka * tp + 2) ** 2 - 4 * tp * ka
root = ((ka * tp + 2) + sqrt(disc)) / (2 * tp)
print("큰 근 =", root, " c_* =", (root ** 2 - ka * root) * exp(-tp * root))
x = mpf(3132) / 3130
print("Gamma_* =", x / ((1 + x) ** (1 - tp) - 1))
print("kappa_d >= 1.498+2*3130/6261 =", mpf(1.498) + 2 * mpf(3130) / 6261)
print("ex_max(3130) =", mpf(3131) / 6261, " 2-ex_max-20/(9*3130) =", 2 - mpf(3131) / 6261 - mpf(20) / (9 * 3130))
print("lemma-N: 12.15, 4.908:", mpf(4.5) * 2 + mpf(4.5) * mpf(2) / 3 + mpf(0.375) * mpf(2) / 5, mpf(4.5) * mpf(2) / 3 + mpf(4.5) * mpf(2) / 5 + mpf(0.375) * mpf(2) / 7)
print("Z_q >= t(2t+2)/(t+2)^2 at 3130:", mpf(3130) * 6262 / mpf(3132) ** 2)
