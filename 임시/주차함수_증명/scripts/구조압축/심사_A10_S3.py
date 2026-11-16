# -*- coding: utf-8 -*-
"""심사 A10 — S3 검산: 정리 10:old-8-25 (첫 층 생존의 상계, m_S = 1.15)의 증명 7단계에서
y >= 6666 이 실제로 어떻게 쓰이는지와, y >= 4000 (q >= 277) 에서도 네 경우의 오차 계수가 서는지를 다시 센다.

(1) 문턱: q >= floor((m_S y)^{2/3}) + 1 의 값 (y = 6666, 4000, 그 밖).
(2) 7단계의 계수:  E(q, rho) = 2(2pi)^{-1/2} [ (1/4)(1-1/(2q))^{-3/2} + (1+u+u^2)(1-u)^{-1/2}(1+u)^{-3/2} ] / q
    - u <= 0.9      : 계수 <= 2.82 ?      F = 2(2pi)^{-1/2}(1+2u^2)sqrt(1-u^2) <= 2/sqrt(pi) = 1.1284
    - 0.9 < u <= 0.99: F <= 1.044,  계수 <= 9.3 ?
    - 0.99 < u <= 0.9999: F <= 0.34, 계수 <= 85 ?
    - u > 0.9999   : 직접 셈 (0.8(1-rho) + 0.182 + 6.5(1-rho) < 0.19 ; 조건 q/50 - 1/2 >= 0.77 q/50, v(theta) <= 1.6 theta)
(3) 네 경우가 1.15 아래인지, q >= 277 과 q >= 389 에서, 그리고 닫히는 최소 q 와 그에 해당하는 최소 y.
(4) 닫힌 꼴 I(rho) (6단계) 를 수치 적분과 대조.
(5) 직접 수치 확인(증명 아님): y = 4000 에서 상위해 조건 phi(q) >= Pr(Bor>=q) + sum_j Bor(j) y/(y+q-j) phi(q-j) 를
    모든 2 <= q <= y+2 에서 배정밀도로 평가하고 최소 여유를 적는다. 또 6.1 의 따름 부등식과 10.11 = T[1] 을 확인한다.
"""
import math
import numpy as np
from mpmath import mp, mpf, quad, log, sqrt, exp

mp.dps = 30
mS = 1.15
C2 = 2 / math.sqrt(2 * math.pi)  # 2(2pi)^{-1/2} = 0.7979

print("== (1) 문턱 q >= floor((1.15 y)^{2/3}) + 1 ==")
for y in (6666, 4000, 3131, 1300, 1289, 1000):
    a = math.floor((mS * y) ** (2 / 3))
    print(f"  y={y}: (1.15y)^(2/3) = {(mS*y)**(2/3):.3f}, a' = {a}, q >= {a+1}")

def coef(u, q):
    """E(q,rho)*q 의 계수 (증명 7단계의 대괄호에 2(2pi)^{-1/2} 를 곱한 것)."""
    return C2 * (0.25 * (1 - 1 / (2 * q)) ** (-1.5) + (1 + u + u * u) * (1 - u) ** (-0.5) * (1 + u) ** (-1.5))

def F(u):
    return C2 * (1 + 2 * u * u) * math.sqrt(1 - u * u)

print("\n== (2) 7단계의 계수와 F 의 상계 (u = rho^{1/3}) ==")
bands = [(0.0, 0.9, 2.82, None), (0.9, 0.99, 9.3, 1.044), (0.99, 0.9999, 85.0, 0.34)]
for q in (389, 277, 236, 131):
    print(f"  q = {q}:")
    for lo, hi, ccl, Fcl in bands:
        us = np.linspace(lo, hi, 200001)[1:]
        cmax = max(coef(u, q) for u in us)
        Fmax = max(F(u) for u in us)
        tot = Fmax + cmax / q
        print(f"    u in ({lo},{hi}]: max coef = {cmax:.4f} (주장 {ccl}) ok={cmax<=ccl};  max F = {Fmax:.5f}"
              + (f" (주장 {Fcl}) ok={Fmax<=Fcl}" if Fcl else f" (= 2/sqrt(pi) = {2/math.sqrt(math.pi):.5f})")
              + f";  F + coef/q <= {tot:.5f}  (<1.15: {tot<1.15})")
    # 넷째 경우: u > 0.9999, 1-rho < 0.0003
    rho_min = 0.9999 ** 3
    one_minus = 1 - rho_min
    cond = q / 50 - 0.5 >= 0.77 * q / 50
    direct = 0.8 * one_minus + 0.182 + 6.5 * one_minus
    print(f"    u > 0.9999: 1-rho <= {one_minus:.6f} (<0.0003: {one_minus<0.0003}); 조건 q/50-1/2 >= 0.77q/50: {cond}; "
          f"좌변*sqrt(q) <= {direct:.5f} (<0.19: {direct<0.19})")

# 넷째 경우의 보조 상수
th = 0.02
print(f"  v(0.02) = (0.98)^(-3/2)-1 = {0.98**-1.5-1:.5f} <= 1.6*0.02 = {1.6*th:.4f}: {0.98**-1.5-1 <= 1.6*th}")
print(f"  2(2pi)^(-1/2) sqrt(50/0.77) = {C2*math.sqrt(50/0.77):.4f} (<6.43)")
print(f"  1.28/sqrt(50) = {1.28/math.sqrt(50):.5f}")

print("\n== (3) 네 경우가 닫히는 최소 q (계수는 q=277 의 것을 그대로) ==")
def closes(q):
    ok = True
    for lo, hi, _, _ in bands:
        us = np.linspace(lo, hi, 20001)[1:]
        if max(F(u) + coef(u, q) / q for u in us) >= 1.15:
            ok = False
    if not (q / 50 - 0.5 >= 0.77 * q / 50):
        ok = False
    return ok
qmin = None
for q in range(100, 400):
    if closes(q):
        qmin = q
        break
print(f"  최소 q = {qmin}")
# 그 q 가 floor((1.15y)^{2/3})+1 로 보장되는 최소 y
ymin = None
for y in range(100, 7000):
    if math.floor((mS * y) ** (2 / 3)) + 1 >= qmin:
        ymin = y
        break
print(f"  floor((1.15 y)^(2/3))+1 >= {qmin} 이 되는 최소 y = {ymin}")

print("\n== (4) 6단계의 닫힌 꼴 I(rho) 대조 ==")
def I_num(rho):
    v = lambda t: (1 - t) ** (-1.5) - 1
    f = lambda t: t ** (-1.5) * min(1 - rho, rho * v(t))
    th_r = 1 - rho ** (2 / 3)
    return quad(f, [0, th_r, 1])
def I_cf(rho):
    u = rho ** (mpf(1) / 3)
    return 2 * (1 + 2 * u * u) * sqrt(1 - u * u) - 2 * (1 - u ** 3)
for rho in (0.05, 0.2, 2 ** -1.5, 0.6, 0.9):
    a, b = I_num(mpf(rho)), I_cf(mpf(rho))
    print(f"  rho={rho:.4f}: 수치 {float(a):.10f}, 닫힌 꼴 {float(b):.10f}, 차 {float(a-b):.1e}")
print(f"  max_u 2(2pi)^(-1/2)(1+2u^2)sqrt(1-u^2) = {2/math.sqrt(math.pi):.6f} at u^2=1/2")

print("\n== (5) 직접 수치 확인 (증명 아님): y=4000 과 y=1300 에서 상위해 조건의 최소 여유 ==")
def bor(J):
    j = np.arange(1, J + 1, dtype=float)
    # log Bor(j) = -j + (j-1) log j - lgamma(j+1)
    lg = np.array([math.lgamma(x + 1) for x in j])
    return np.exp(-j + (j - 1) * np.log(j) - lg)
def check_super(y):
    D = y + 2
    B = bor(D + 5)
    tail = 1 - np.cumsum(B)  # tail[q-1] = Pr(Bor > q) ; Pr(Bor >= q) = tail[q-2]
    d = np.arange(1, D + 1, dtype=float)
    phi = np.minimum(1.0, mS * (y + d) / d ** 1.5)  # phi(q) at index q-1
    worst = (None, 1e9)
    for q in range(2, D + 1):
        j = np.arange(1, q)
        rhs = tail[q - 2] + np.sum(B[j - 1] * y / (y + q - j) * phi[q - j - 1])
        marg = phi[q - 1] - rhs
        if marg < worst[1]:
            worst = (q, marg)
    return worst
for y in (4000, 1300, 1000, 500):
    q, m = check_super(y)
    print(f"  y={y}: 최소 여유 {m:.6f} at q={q}  (>=0: {m>=0})")

print("\n== (6) 6.1 의 따름: 1.15(y+q+1)/(q+1)^{3/2} <= 3y/q^{3/2} (1<=q<=y) ==")
for y in (4000, 6667):
    q = np.arange(1, y + 1, dtype=float)
    r = (mS * (y + q + 1) / (q + 1) ** 1.5) / (3 * y / q ** 1.5)
    print(f"  y={y}: max 비 = {r.max():.5f} (<1: {r.max()<1}); 1.15(2y+1)/(3y) = {mS*(2*y+1)/(3*y):.5f}")

print("\n== (7) 10.11 (s^W) = 상위해 연산자 T 를 phi=1 에 한 번 적용한 값 ==")
def sW(q, y):
    m = y + q
    r = np.arange(0, q, dtype=float)
    B = bor(q + 1)
    return 1 - np.sum(B[(r + 1).astype(int) - 1] * (q - r) / (m - r))
def T1(d, y):
    B = bor(d + 5)
    tail = 1 - np.cumsum(B)
    j = np.arange(1, d, dtype=float)
    return tail[d - 2] + np.sum(B[j.astype(int) - 1] * y / (y + d - j))
for y, q in ((50, 7), (4000, 300), (6667, 1000)):
    a, b = sW(q, y), T1(q + 1, y)
    print(f"  y={y}, q={q}: s^W_q(y+q,y) = {a:.12f}, T[1](d=q+1) = {b:.12f}, 차 {a-b:.1e}")
