# -*- coding: utf-8 -*-
"""심사 A5 — 정확 산술 검산 (작은 k).
S1 망원곱 부등식, S2 합산 손실 -1/2, S10 (6.23)=(8.2), S12 V-핵심 하계식, 판정 V(2<=k<=K0) 정확 성립,
S6 6.21이 5.50을 지배(손실률 비교).
실행: python -I 심사_A5_1_exact.py > 심사_A5_1_exact_out.txt
"""
from fractions import Fraction as Fr
from math import comb, exp, log, sqrt, pi, factorial
import sys

def A_seq(k, M):
    """A_{m,k-1} (m=0..M): 용량 k 아래(최대 변위 <= k-1) 주차함수 수. 정리 2.6 재귀."""
    A = [0]*(M+1); A[0] = 1
    for m in range(1, M+1):
        s = 0
        for j in range(1, m+1):
            s += comb(m-1, j-1)*min(j, k)*A[j-1]*A[m-j]
        A[m] = s
    return A

def p(n):
    return (n+1)**(n-1) if n >= 1 else 1

def Bor(n):  # float
    return exp(-n + (n-1)*log(n) - sum(log(i) for i in range(1, n+1))) if n > 0 else 0.0

def g(x):
    return (x-1)*log(1+1/x)

K0 = int(sys.argv[1]) if len(sys.argv) > 1 else 60
sB = exp(1)/sqrt(2*pi)
gamma_W = 2*exp(0.0031)/exp(1)

print("# S1/S2/S12/V 정확 검산, k=2..%d" % K0)
fails_S1 = fails_S2 = fails_S2b = fails_S12 = fails_V = fails_W0 = 0
W0_ratio_max = 0.0
S2_min_ratio = 10.0
Vmin_overall = None
for k in range(2, K0+1):
    M = 2*k+1
    Acap = {cap: A_seq(cap, M) for cap in range(k-1, 2*k+1)}   # Acap[cap][m] = A_{m,cap-1} (용량 cap)
    s_km1 = [Fr(Acap[k-1][m], p(m)) for m in range(M+1)]
    s_k   = [Fr(Acap[k][m], p(m)) for m in range(M+1)]
    s_kp1 = [Fr(Acap[k+1][m], p(m)) for m in range(M+1)]
    c_k   = [s_kp1[m]-s_k[m] for m in range(M+1)]    # c_m(k)
    c_km1 = [s_k[m]-s_km1[m] for m in range(M+1)]    # c_m(k-1)
    # S1: c_{k-1+d}(k-1) <= U_d c_{2k-1}(2k-1-d), U_d=(k+d)(2k-1-d)(2k-d)/(2k^2(k-1))
    def c_level(m, w):   # c_m(w) = s_m(w+1)-s_m(w), 용량 w+1, w 가 Acap 에 있어야 함
        return Fr(Acap[w+1][m] - Acap[w][m], p(m))
    W0 = 0.0
    Hmono_fail = 0
    for d in range(1, k+1):
        lhs = c_km1[k-1+d]
        rhs = Fr((k+d)*(2*k-1-d)*(2*k-d), 2*k*k*(k-1)) * c_level(2*k-1, 2*k-1-d)
        if lhs > rhs:
            fails_S1 += 1
        W0 += Bor(k+d)*float(lhs)
        # H_m(d) 단조: m=k-1+d..2k-2
        prev = None
        for m in range(k-1+d, 2*k):
            H = Fr((m-d)*(m-d+1), m+1)*c_level(m, m-d)
            if prev is not None and H < prev:
                Hmono_fail += 1
            prev = H
    bound_new = 2/sqrt(2*pi)*k**-1.5
    W0_ratio_max = max(W0_ratio_max, W0/bound_new)
    if W0 >= bound_new:
        fails_W0 += 1
    # S2: D_{n,k} >= -(k-1)/(2n) Bor(n) c_{n-1}(k-1)
    for n in range(k+1, 2*k+1):
        base = Bor(n)*float(c_km1[n-1])
        D = (k+1)*Bor(n+1)*float(c_k[n]) - (k-1)*base
        if base > 0:
            r = D/base
            S2_min_ratio = min(S2_min_ratio, r)
            if r < -(k-1)/(2*n) - 1e-12:
                fails_S2 += 1
            if r < -0.5:
                fails_S2b += 1
    # V_k(m)
    V = [sum((k+1)*c_k[mm]-(k-1)*c_km1[mm] for mm in range(m, 2*k+1)) for m in range(k, 2*k+1)]
    vmin = min(V)
    if vmin <= 0:
        fails_V += 1
    if Vmin_overall is None or vmin < Vmin_overall[0]:
        Vmin_overall = (vmin, k)
    # S12: V_k(k) >= (k-1)/(R+1)(1-s_R(k-1)) - (k-1)c_{2k}(k-1), R=floor(3(k-1)/2)
    R = (3*(k-1))//2
    low = Fr(k-1, R+1)*(1-s_km1[R]) - (k-1)*c_km1[2*k]
    if V[0] < low:
        fails_S12 += 1
    if k in (2, 3, 5, 10, 20, 40, 60, K0):
        print("k=%d V_k(k)=%.6f minV=%.6f S12하계=%.6f W0=%.6e 새상계=%.6e 비=%.4f 현상계비=%.4f Hmono_fail=%d" % (
            k, float(V[0]), float(vmin), float(low), W0, bound_new, W0/bound_new, W0/(gamma_W*sB*k**-1.5), Hmono_fail))
print("S1 실패 쌍:", fails_S1, "| W0 새상계 위반 k 수:", fails_W0, "| max W0/새상계:", round(W0_ratio_max, 5))
print("S2 실패( -(k-1)/(2n) 기준):", fails_S2, "| -1/2 기준:", fails_S2b, "| min D/(Bor c):", round(S2_min_ratio, 6))
print("V 양성 실패 k 수:", fails_V, "| 최소 V_k(m):", float(Vmin_overall[0]), "at k=", Vmin_overall[1])
print("S12 하계식 위반 k 수:", fails_S12)

# S10: (6.23) 와 (8.2) 가 같은 식 — 수치로 두 우변과 c 를 비교 (y=5..12, d=1..y+1)
print("\n# S10: (6.23) vs (8.2)")
def pi_kernel(N, t):  # pi_N(t) = C(N,t) t^{t-1} p_{N-t}/p_N = C(N,t) t^{t-1} (N+1-t)^{N-t-1} / (N+1)^{N-1}  (2.5절; 6.48(가) 증명)
    return Fr(comb(N, t)*t**(t-1), (N+1)**(N-1)) * Fr(N+1-t)**(N-t-1)
maxdiff = Fr(0)
for y in range(3, 13):
    M = 2*y+3
    Ay = A_seq(y, M); Ayp1 = A_seq(y+1, M)
    s_y = [Fr(Ay[m], p(m)) for m in range(M+1)]      # s_m(y)
    s_yp1 = [Fr(Ayp1[m], p(m)) for m in range(M+1)]  # s_m(y+1)
    c_y = [s_yp1[m]-s_y[m] for m in range(M+1)]      # c_m(y)
    for d in range(1, y+2):
        # (6.23)
        rhs623 = pi_kernel(y+d, y+1)/(y+1) + sum(pi_kernel(y+d, y+1+q)*((y+1)*c_y[y+q] + s_y[y+q])/(y+1+q) for q in range(1, d))
        # (8.2) with k=y, m=y+d: sum_{t=y+1}^{m} pi_m(t)/t [s_{t-1}(y+1) + y c_{t-1}(y)]
        m = y+d
        rhs82 = sum(pi_kernel(m, t)/t*(s_yp1[t-1] + y*c_y[t-1]) for t in range(y+1, m+1))
        maxdiff = max(maxdiff, abs(rhs623-c_y[y+d]), abs(rhs82-c_y[y+d]), abs(rhs623-rhs82))
print("max |(6.23)-c|, |(8.2)-c|, |(6.23)-(8.2)| =", float(maxdiff))

# S6: 6.21의 손실률 (m+d+2)/((w+2)(m+1)) <= 5.50의 z_m(d) ?
print("\n# S6: 6.21 손실률 <= 5.50 손실률 z_m(d), 2<=m<=400, 1<=d<=m/2")
bad = 0; minslack = 1e9
for m in range(2, 401):
    for d in range(1, m//2+1):
        w = m-d
        l621 = (m+d+2)/((w+2)*(m+1))
        z = exp((d-1)/w)/(w+1) + 3*d/(2*(w+1)*(m+1))
        minslack = min(minslack, z-l621)
        if l621 > z: bad += 1
print("위반 쌍:", bad, "| 최소 여유 z - 6.21손실률:", minslack)

# S2 해석 부등식: (1+1/n) e^{g(n)-1} >= 1 - 1/(2n)
print("\n# S2 해석: (1+1/n)e^{g(n)-1} - (1-1/(2n)) 최소 (n=1..10^5)")
mn = min(((1+1/n)*exp(g(n)-1) - (1-1/(2*n)), n) for n in range(1, 100001))
print("min =", mn)
