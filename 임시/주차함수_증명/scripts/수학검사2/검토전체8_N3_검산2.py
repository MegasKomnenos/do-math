# -*- coding: utf-8 -*-
"""검토전체8 N3: 장5A.md 수치·항등식 검산 (python -I 로 실행)."""
from fractions import Fraction as Fr
from math import comb, factorial, ceil, floor, e as E, log, sqrt, pi, exp
from itertools import permutations, product
import sys

sys.setrecursionlimit(10000)

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

# ---------- (e') 경계 응답 다항식 ----------
def Gamma(d, y, n):
    # Fraction/정수 y
    g = [Fr(1)]
    for dd in range(1, d + 1):
        s = Fr(comb(n, dd) * p(dd))
        for j in range(0, dd):
            s += y * comb(n - dd + j, j) * p(j) * g[dd - 1 - j]
        g.append(s)
    return g[d]


# ---------- (f) 타일 모형 ----------
def tw(j):
    return Fr(1) if j == 1 else Fr((j - 1) ** (j - 1), factorial(j))
def V_tile(q):  # q: 좌표 리스트 (길이 d), 재귀
    d = len(q)
    V = [Fr(1)]
    for dd in range(1, d + 1):
        s = (1 + q[dd - 1]) * V[dd - 1]
        for j in range(2, dd + 1):
            s += tw(j) * V[dd - j]
        V.append(s)
    return V[d]
for n in range(3, 9):
    for d in range(0, n):
        for y in [Fr(1), Fr(3), Fr(7, 2)]:
            q = [y / (n - i + 1) for i in range(1, d + 1)]
            lhs = Gamma(d, y, n)
            rhs = Fr(factorial(n), factorial(n - d)) * V_tile(q)
            assert lhs == rhs, (n, d, y)
print("inverse-renewal: Gamma_d = (n)_d V_d (n<=8) 일치")
# hb_d 계수식, hb_d(1), bd 꼬리
for d in range(1, 8):
    # 동질 좌표 다항식: 숫자로 확인 (rho=1,2,3 에서 값)
    for rho in [Fr(1), Fr(2), Fr(3)]:
        val = V_tile([rho] * d)
        form = sum(Fr((j + 1) * (d + 1) ** (d - j - 1), factorial(d - j)) * rho ** j for j in range(0, d)) + rho ** d
        assert val == form, (d, rho)
    assert V_tile([Fr(1)] * d) == Fr((d + 1) ** d, factorial(d))
print("hb_d 계수식·hb_d(1) (d<=7) 일치")
# 로그볼록 tw
for j in range(1, 30):
    assert tw(j + 1) / tw(j) <= tw(j + 2) / tw(j + 1)
print("tw 로그볼록 (j<30) 확인")
# suff-cond (가) 끝점 비 수치: V_r(k-1) <= (1+1/r)^r V_{r-1}(k)
for r in range(2, 9):
    for k in range(r + 1, r + 12):
        n = k + r
        lhs = V_tile([Fr(k - 1, n - i + 1) for i in range(1, r + 1)])
        rhs = Fr(r + 1, r) ** r * V_tile([Fr(k, n - i + 1) for i in range(1, r)])
        assert lhs <= rhs, (r, k)
print("suff-cond (가) 끝점 비 (r<=8, k<r+12) 확인")

# ---------- (g) 보조정리 lemma-L (나) L(10^4) ----------
try:
    from mpmath import mp, quad, mpf, exp as mexp, findroot, sqrt as msqrt
    mp.dps = 30
    def M(q):
        return quad(lambda y: y ** q * mexp(-y - y * y / 2), [0, mp.inf])
    def Mstar(q):
        # max of y^q e^{-y-y^2/2}: y^2 + y - q = 0
        y0 = (-1 + msqrt(1 + 4 * q)) / 2
        return y0 ** q * mexp(-y0 - y0 * y0 / 2)
    M26 = quad(lambda y: y ** 2 * mexp(-y - y * y / 2), [0, 6])
    C1 = 2 * Mstar(2) + M(3) / 2 + M(5) / 3
    C2 = Mstar(3) / 2 + Mstar(5) / 3 + M(4) / 2
    C3 = Mstar(4) / 2 + M(3) / 6
    C4 = Mstar(3) / 6
    s = mpf(100)
    L = (M26 - C1 / s - C2 / s ** 2 - C3 / s ** 3 - C4 / s ** 4) / (M(1) + (M(0) + mexp(-0.5)) / s + 1 / s ** 2)
    print("L(10^4) =", L, " (>=0.845204 ?)", L >= mpf("0.845204"))
    print("M0..M5:", [M(q) for q in range(6)], "M2^(6):", M26)
except Exception as ex:
    print("mpmath 없음:", ex)

# Pc 하계 상수
print("1/2+2*0.845204-sqrt(3pi/2) =", 0.5 + 2 * 0.845204 - sqrt(3 * pi / 2), " sqrt(3pi/2)=", sqrt(3 * pi / 2), " sqrt(pi/2)=", sqrt(pi / 2))
s = 100.0
print("대괄호(s=100) =", 1 / (3 * s) + 8 / (3 * s * s) + 2.507 / (s * s) + (1 + 2.1709 * s) / s ** 3)

# ---------- (h) 5.2.3·5.4 상수 ----------
print("2sqrt2/e =", 2 * sqrt(2) / E, " 181/174=", 181 / 174, " 26/25=", 1.04)
print("312m^2-374m+25 at m=1,2:", 312 - 374 + 25, 312 * 4 - 374 * 2 + 25)
print("(0.65)(1+3/529)/23 =", 0.65 * (1 + 3 / 529) / 23, " <1/12:", 0.65 * (1 + 3 / 529) / 23 < 1 / 12)
print("27.14^3=", 27.14 ** 3, " 0.745^3=", 0.745 ** 3, " 0.64^2=", 0.64 ** 2, " 0.75^3=", 0.75 ** 3, " 0.65^2=", 0.65 ** 2)
print("27/(4*27.14)=", 27 / (4 * 27.14), " (3/4)^1.5=", 0.75 ** 1.5)
print("1/(1+9/sqrt598)=", 1 / (1 + 9 / sqrt(598)), " 833^1.5=", 833 ** 1.5, " 832^1.5=", 832 ** 1.5, " 1.2*20001=", 1.2 * 20001)
print("966^1.5=", 966 ** 1.5, " 965^1.5=", 965 ** 1.5, " 1.5*20001=", 1.5 * 20001)
print("rq 다섯 값:", 1.2 / sqrt(598), 1.5 / sqrt(833), 1.8 / sqrt(966), 2.1 / sqrt(2164), 2.4 / 100, " 1/16=", 1 / 16)
print("(12/5)(1+1/598)/sqrt598=", 2.4 * (1 + 1 / 598) / sqrt(598), " 12/(110e)=", 12 / (110 * E), " 1/24=", 1 / 24)
print("(12/11)^1.5*(1+1/598)=", (12 / 11) ** 1.5 * (1 + 1 / 598), " log10(1.15*598^3)=", log(1.15 * 598 ** 3, 10), " 598log10(24)=", 598 * log(24, 10))
print("(9/5)^(2/3)=", 1.8 ** (2 / 3), " 10/2^(2/3)=", 10 / 2 ** (2 / 3), " 10001^(-1/3)=", 10001 ** (-1 / 3), " 0.0015/1.25^12=", 0.0015 / 1.25 ** 12)
print("1-cos(1)=", 1 - __import__('math').cos(1))
print("1/sqrt(598)=", 1 / sqrt(598), " (0.65)^(2/3)=", 0.65 ** (2 / 3), " (0.64)^(2/3)=", 0.64 ** (2 / 3))
print("597^1.5+9*597=", 597 ** 1.5 + 9 * 597, " 598^1.5+9*598=", 598 ** 1.5 + 9 * 598)
print("1160^1.5+9*1160=", 1160 ** 1.5 + 9 * 1160, " 1161:", 1161 ** 1.5 + 9 * 1161)
# 5-4 증명 e_15
e15 = sum(Fr(1, factorial(j)) for j in range(16))
print("e15 < e:", float(e15) < E, " 15!e15 정수:", (e15 * factorial(15)).denominator == 1)
