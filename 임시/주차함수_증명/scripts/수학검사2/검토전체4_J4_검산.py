# -*- coding: utf-8 -*-
"""검토전체4 J4: 장5B의 식과 수치를 다시 센다.

1. 작은 n에서 주차함수를 전수 열거해 A_{n,l}, b_{n,l}을 얻고
   - 보조정리 5.19 (열 재귀) c_n(y)-c_n(y-1)=sum_t pi_n(t) x_t(y)
   - 5.5.1의 x_t(y) 식 (t=y: -1/y; t>=y+1: [(y+1)c_{t-1}(y)-(y-1)c_{t-1}(y-1)]/t)
   - 보조정리 5.27 (기저 항등식), 따름정리 6.cor-L (기저량 하계)
   - 정리 5.28 (크기 방향 하계)
   - 보조정리 5.25 (창 항의 항별 상계) (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t))
   를 정확 유리수로 확인한다.
2. 5.5.5, 5.5.8의 손 계산 상수를 부동소수점으로 다시 센다.
"""
from fractions import Fraction as Fr
from itertools import product
from math import comb, exp, factorial, log, pi, sqrt, floor, ceil

# ---------- 1. 전수 열거 ----------
def maxdisp_counts(n):
    """길이 n 주차함수의 최대 변위별 개수 b[l], l=0..n-1."""
    b = [0] * n
    for a in product(range(1, n + 1), repeat=n):
        occ = [False] * (n + 1)
        ok = True
        M = 0
        for ai in a:
            p = ai
            while p <= n and occ[p]:
                p += 1
            if p > n:
                ok = False
                break
            occ[p] = True
            if p - ai > M:
                M = p - ai
        if ok:
            b[M] += 1
    return b

NMAX = 8
B = {}
A = {}
P = {}
for n in range(0, NMAX + 1):
    if n == 0:
        B[0] = []
        P[0] = 1
    else:
        B[n] = maxdisp_counts(n)
        P[n] = (n + 1) ** (n - 1)
        assert sum(B[n]) == P[n], (n, sum(B[n]), P[n])

def Acum(n, l):
    if l < 0:
        return 0
    if n == 0:
        return 1
    return sum(B[n][:min(l, n - 1) + 1])

def s(m, Y):  # 생존 확률 s_m(Y)=A_{m,Y-1}/p_m
    if Y <= 0:
        return Fr(0)
    return Fr(Acum(m, Y - 1), P[m])

def c(m, Y):  # 수준 질량
    return s(m, Y + 1) - s(m, Y)

def pi_kernel(n, t):  # 가장 큰 나무 핵 (대수적 꼴)
    return Fr(comb(n, t) * t ** (t - 1) * P[n - t], P[n])

def sT(t, Y):  # 나무 생존 확률
    if t <= Y:
        return Fr(1)
    return Fr(Y, t) * s(t - 1, Y)

def x_curv(t, y):
    return sT(t, y + 1) - 2 * sT(t, y) + sT(t, y - 1)

print("== 1a. 보조정리 5.19 열 재귀, 5.5.1 x_t(y) 식 ==")
bad = 0
for n in range(3, NMAX + 1):
    for y in range(ceil((n + 1) / 2), n):  # (n+1)/2 <= y <= n-1
        lhs = c(n, y) - c(n, y - 1)
        rhs = sum(pi_kernel(n, t) * x_curv(t, y) for t in range(y, n + 1))
        if lhs != rhs:
            bad += 1
            print("5.19 불일치", n, y, lhs, rhs)
        # x_t 식
        if x_curv(y, y) != Fr(-1, y):
            bad += 1
            print("x_y(y) != -1/y", y)
        for t in range(y + 1, n + 1):
            f = ((y + 1) * c(t - 1, y) - (y - 1) * c(t - 1, y - 1)) / t
            if x_curv(t, y) != f:
                bad += 1
                print("x_t 식 불일치", t, y)
print("불일치 수:", bad)

print("== 1b. 보조정리 5.27 기저 항등식, 따름정리 cor-L ==")
bad = 0
for n in range(3, NMAX + 1):
    for y in range(ceil((n + 1) / 2), n):
        Pn = sum(x_curv(t, y) for t in range(y, n + 1))
        ident = Fr(-1, y) + sum(((y + 1) * c(m, y) - (y - 1) * c(m, y - 1)) / (m + 1) for m in range(y, n))
        if Pn != ident:
            bad += 1
            print("5.27 불일치", n, y)
        top = Fr(y * (y - 1)) * c(n - 1, y - 1) / n
        if Pn < -(1 + top) / y:
            bad += 1
            print("cor-L 위반", n, y, float(Pn), float(-(1 + top) / y))
print("불일치/위반 수:", bad)

print("== 1c. 정리 5.28 크기 방향 하계 (m+1 <= NMAX) ==")
bad = 0
for m in range(2, NMAX):
    for d in range(1, m // 2 + 1):
        w = m - d
        z = exp((d - 1) / w) / (w + 1) + 3 * d / (2 * (w + 1) * (m + 1))
        lhs = float(c(m + 1, w + 1))
        rhs = (1 - z) * float(c(m, w))
        if lhs < rhs - 1e-15:
            bad += 1
            print("5.28 위반", m, d, lhs, rhs)
print("위반 수:", bad)

def Bor(m):
    return exp(-m) * m ** (m - 1) / factorial(m)

print("== 1d. 보조정리 5.25 (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t)), t>y>t/2, t<=NMAX ==")
bad = 0
for t in range(2, NMAX + 1):
    for y in range(t // 2 + 1, t):
        neg = max(-float(x_curv(t, y)), 0.0)
        bound = (t - y) * Bor(t - y) * Bor(y) / (y * Bor(t))
        if neg > bound + 1e-15:
            bad += 1
            print("5.25 위반", t, y, neg, bound)
print("위반 수:", bad)

# ---------- 2. 상수 검산 ----------
print("== 2a. 5.5.2: t_0(y)<=n 사슬, varrho_0 상계 ==")
def t0(y):
    t = y + 2
    while not (y <= (t - 1) - floor(0.75 * (t - 1) ** (2 / 3))):
        t += 1
    return t
for y in (25000, 25001, 33334, 60000, 10 ** 6):
    r0 = t0(y) - 1 - y
    print(f"y={y}: varrho_0={r0}, 상계 0.75(1.1y)^(2/3)+1={0.75*(1.1*y)**(2/3)+1:.2f}, 0.7993y^(2/3)+1={0.7993*y**(2/3)+1:.2f}")
n = 50001
print("10((n+1)/2)^(2/3) - (6n^(2/3)+2) at n=50001:", 10 * ((n + 1) / 2) ** (2 / 3) - (6 * n ** (2 / 3) + 2))

print("== 2b. 보조정리 5.30 상수 ==")
print("e^-1 =", exp(-1))
v1 = (2 * pi) ** -0.5 * sqrt(2) * 3 ** 1.5 * (1 + 1 / n) ** 1.5 * n ** -0.5 * exp(1 / (12 * (n + 1)))
print("y<=2n/3 top_pi 상계:", v1, "<=0.0133?", v1 <= 0.0133)
v2 = (2 * pi) ** -0.5 * (1.5 / 10) ** 1.5 * (1 + 1 / n) ** 1.5 * exp(1 / (12 * (n + 1)))
print("(1.5/10)^1.5 =", (1.5 / 10) ** 1.5, "; y>2n/3 top_pi 상계:", v2, "<=0.0232?", v2 <= 0.0232)
v3 = exp(-2) * ((n + 1) / (n - 1)) ** 1.5 * exp(1 / (12 * (n - 1)))
print("pi_n(n-1) 상계:", v3, "<0.1354?", v3 < 0.1354)
print("괄호 하계 e^-1-0.1354-0.0232 =", exp(-1) - 0.1354 - 0.0232)

print("== 2c. 5.5.6 척도 상수 ==")
h0 = 0.0342
print("h0^3 =", h0 ** 3, ">=1/25000?", h0 ** 3 >= 1 / 25000)
umax = sqrt(6 * h0); c1 = 1 / (2 * (1 - umax))
print("upsilon_max =", umax, " c1 =", c1)
c2 = 1 / sqrt(2) - umax / 3
print("c2 =", c2, ">=0.556?", c2 >= 0.556)
f12 = c2 * 12 ** 1.5 - 12 - log(sqrt(2) * (1 + 6 * h0) * 12 / c2)
print("f(12) =", f12, ">7?", f12 > 7, "; sqrt2(1+6h0)12/c2 =", sqrt(2) * (1 + 6 * h0) * 12 / c2)
print("f'(12) =", 1.5 * c2 * sqrt(12) - 1 - 1 / 12)
print("24^3 =", 24 ** 3, "(6Y^(2/3)<=Y/4 iff Y>=13824)")

print("== 2d. 보조정리 stop-lower 상수 ==")
print("1.5*0.95^-2.5 =", 1.5 * 0.95 ** -2.5, "<=1.706?", 1.5 * 0.95 ** -2.5 <= 1.706)
print("(0.8^-1.5-1)/0.2 =", (0.8 ** -1.5 - 1) / 0.2, "<=1.988?", (0.8 ** -1.5 - 1) / 0.2 <= 1.988)
print("(1+1.706*0.05)/11 =", (1 + 1.706 * 0.05) / 11, " (1+1.988*0.2)/11 =", (1 + 1.988 * 0.2) / 11)
print("4/sqrt(2pi) =", 4 / sqrt(2 * pi))

print("== 2e. 보조정리 right-part 상수 ==")
y = 33334; r = 10356
print("r 하한: 10*33334^(2/3)-1 =", 10 * y ** (2 / 3) - 1)
chi = 0.2 * r - 7.3
print("chi_w 하한 0.2r-7.3 =", chi)
hv = lambda ch: ch ** -0.5 * (2 / sqrt(pi) * (1 + 1 / ch) + 1 / sqrt(pi))
print("hv(2064)*sqrt(2064) =", hv(2064) * sqrt(2064), "<=1.6932?", hv(2064) * sqrt(2064) <= 1.6932)
t = y ** (1 / 3)
eps_hov = 1.6932 * (t / 10 + 1) * (2 * t ** 2 - 7.5) ** -0.5
print("eps_hov 상계 at y=33334:", eps_hov, "<=0.1573?", eps_hov <= 0.1573)
print("sqrt(2/pi)/sqrt(2064) =", sqrt(2 / pi) / sqrt(2064), "<=0.01757?", sqrt(2 / pi) / sqrt(2064) <= 0.01757)
print("0.75*1.1^(2/3) =", 0.75 * 1.1 ** (2 / 3))
print("(2pi)^-1/2 (1.50003/0.9199)^1.5 =", (2 * pi) ** -0.5 * (1.50003 / 0.9199) ** 1.5)
print("0.24924/sqrt(10357) =", 0.24924 / sqrt(10357), "<=0.00245?", 0.24924 / sqrt(10357) <= 0.00245)
print("1-0.01757-0.00245 =", 1 - 0.01757 - 0.00245)
rho0 = 0.07993 * (r + 1) + 1
print("(r+1)/(r-rho0) at r=10356:", (r + 1) / (r - rho0), "<=1.0872?", (r + 1) / (r - rho0) <= 1.0872)
print("(0.7993 y^(2/3)+2)^1.5 / y at y=33334:", (0.7993 * y ** (2 / 3) + 2) ** 1.5 / y, "<=0.7172?", (0.7993 * y ** (2 / 3) + 2) ** 1.5 / y <= 0.7172)
print("1.5 rho0/(r+1-rho0) =", 1.5 * rho0 / (r + 1 - rho0), "<=0.1305?", 1.5 * rho0 / (r + 1 - rho0) <= 0.1305)
print("(1+(0.7993y^(2/3)+1)/y)^1.5 =", (1 + (0.7993 * y ** (2 / 3) + 1) / y) ** 1.5, "<=1.0376?", (1 + (0.7993 * y ** (2 / 3) + 1) / y) ** 1.5 <= 1.0376)
W = (2 * pi) ** -0.5 * (2 / 3) * 0.7172 * 1.5 * 1.0872 * 1.0376 * exp(0.1305 + 1 / 400008)
print("(r+1)/y * W 상계:", W, "<=0.3678?", W <= 0.3678)
c4 = 1 / 156 + 1 / (12 * y) + 1 / (12 * (n + 1))
print("e^-c4 =", exp(-c4), ">=0.9936?", exp(-c4) >= 0.9936)
coef = (1 - 0.1573) * 0.71216 * 0.9936 * (2 * 0.9799 - 0.0232) - 0.3678
print("0.8427*0.71216*0.9936*1.9366-0.3678 =", coef, ">=0.7869?", coef >= 0.7869)
print("Psi_R at lambda=2/3:", 0.7869 * 2 / 3 - 0.3334 - 0.0001)

print("== 2f. 정리 5.33 범위: D'-l 최소 ==")
# m = Y+q+chi+1, D <= chi-1, l <= Y+q+1
Y_, q_, ch_ = 100, 7, 5
m_ = Y_ + q_ + ch_ + 1
print("m-chi-Y-q+1 =", m_ - ch_ - Y_ - q_ + 1, "(본문: 'D'-l>=1이 되게 하는 조건'; 실제 최소 2)")

print("== 2g. band-inequality 조건 at n=50001 ==")
n = 50001
yb = 2 * n / 3
print("0.4(n-y) at y=2n/3:", 0.4 * (n - yb), " 6y^(2/3)+1:", 6 * yb ** (2 / 3) + 1)
print("0.75(1.1y)^(2/3)+1 at y=2n/3:", 0.75 * (1.1 * yb) ** (2 / 3) + 1, " 0.7(n-y):", 0.7 * (n - yb))
