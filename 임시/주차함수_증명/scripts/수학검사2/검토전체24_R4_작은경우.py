# -*- coding: utf-8 -*-
# 검토 24차 R4: 장5B의 항등식·부등식을 작은 n에서 정확 유리수로 검산한다.
from fractions import Fraction as F
from math import comb
import sys
N = 46
# A[n][l] = 최대 변위 <= l 인 길이 n 주차함수 수 (마지막 차 재귀)
A = [[0]*(N+2) for _ in range(N+1)]
for l in range(N+2):
    A[0][l] = 1
for l in range(N+2):
    for n in range(1, N+1):
        s = 0
        for j in range(1, n+1):
            s += comb(n-1, j-1)*min(j, l+1)*A[j-1][l]*A[n-j][l]
        A[n][l] = s
def p(n): return (n+1)**(n-1) if n >= 1 else 1
for n in range(1, N+1):
    assert A[n][n-1] == p(n), n
def Acum(n, l):
    if l < 0: return 0
    if l >= n-1: return p(n)
    return A[n][l]
def s(m, y):           # 생존 확률 s_m(y)
    if y <= 0: return F(0)
    return F(Acum(m, y-1), p(m))
def c(m, Y):           # 수준 질량
    return s(m, Y+1) - s(m, Y)
def sT(t, Y): return F(min(t, Y), t)*s(t-1, Y)
def x(t, y): return sT(t, y+1) - 2*sT(t, y) + sT(t, y-1)
def pi(n, t): return F(comb(n, t)*t**(t-1)*p(n-t), p(n))
def bor_ratio_theta(t, k):   # theta_t(k) = C(t,k) k^(k-1) (t-k)^(t-k) / t^(t-1)
    return F(comb(t, k)*k**(k-1)*((t-k)**(t-k) if t > k else 1), t**(t-1))
bad = 0
# (1) 열 재귀 5:old-5-19, 곡률 꼴(2:curvature-level-mass), 핵의 단조성 5:old-5-20
for n in range(3, N+1):
    for y in range((n+2)//2, n):
        assert 2*y >= n+1
        lhs = c(n, y) - c(n, y-1)
        rhs = sum(pi(n, t)*x(t, y) for t in range(y, n+1))
        if lhs != rhs: bad += 1; print('열 재귀 불일치', n, y)
        assert x(y, y) == F(-1, y)
        for t in range(y+1, n+1):
            assert x(t, y) == (F(y+1)*c(t-1, y) - (y-1)*c(t-1, y-1))/t
    for t in range((n+2)//2, n):
        assert pi(n, t+1) > pi(n, t), (n, t)
print('(1) 열 재귀·곡률·핵 단조성: 불일치', bad)
# (2) 2:old-2-38  y x_t(y) >= -theta_t(y)  (y>=2, t>=y)
cnt = 0
for y in range(2, 24):
    for t in range(y, N+1):
        cnt += 1
        assert y*x(t, y) >= -bor_ratio_theta(t, y), (y, t)
print('(2) 문턱 부분나무 상계 확인', cnt)
# (3) 6:cor-L  y P_n(y) >= -1 - y(y-1)c_{n-1}(y-1)/n,  y>=2, y+1<=n<=2y+1
cnt = 0
for y in range(2, 23):
    for n in range(y+1, min(2*y+1, N)+1):
        P = sum(x(t, y) for t in range(y, n+1))
        assert y*P >= -1 - F(y*(y-1))*c(n-1, y-1)/n, (y, n)
        cnt += 1
print('(3) 기저량 하계 확인', cnt)
# (4) Abel 환원 5:old-5-22 (임의의 t0에 대해 IH가 성립하는 경우), 흡수 항등식
cnt = 0; viol = 0
for n in range(6, N+1):
    for y in range((n+2)//2, n):
        for t0 in range(y+2, n+1):
            if not all(c(m, y) >= c(m, y-1) for m in range(t0-1, n)): continue
            P = sum(x(t, y) for t in range(y, n+1))
            WIN = sum((pi(n, t)-pi(n, y))*max(-x(t, y), 0) for t in range(y+1, t0))
            POS = sum((pi(n, m+1)-pi(n, t0-1))*(c(m, y)+c(m, y-1))/(m+1) for m in range(t0-1, n))
            lhs = c(n, y) - c(n, y-1)
            if lhs < pi(n, y)*P - WIN + POS: viol += 1
            # (5.1)
            top = F(y*(y-1))*c(n-1, y-1)/n
            if lhs < POS - WIN - pi(n, y)/y*(1+top): viol += 1
            # 흡수 항등식
            toppi = (y-1)*pi(n, y)
            POSp = sum((pi(n, m+1)-pi(n, t0-1))*(c(m, y)+c(m, y-1))/(m+1) for m in range(t0-1, n-1)) \
                 + (pi(n, n)-pi(n, t0-1))*c(n-1, y)/n + (pi(n, n)-pi(n, t0-1)-toppi)*c(n-1, y-1)/n
            assert POS - pi(n, y)/y*top == POSp
            # 창 항의 항별 상계
            WINV = sum((pi(n, t)-pi(n, y))*bor_ratio_theta(t, y) for t in range(y+1, t0))/y
            assert WIN <= WINV
            cnt += 1
print('(4) Abel 환원·(5.1)·흡수·항별 상계: 경우', cnt, '위반', viol)
# (5) 수준 방문 보존으로 얻는 착지 질량의 첫 하계(일반 Y, 창 폭 Q, Q+1<=Y)
cnt = 0
for Y in range(3, 22):
    for Q in range(1, min(Y-1, N-Y)+1):
        if Y+Q > N: break
        Lam = sum(F(Y, Y+q+1)*c(Y+q, Y) for q in range(1, Q+1))
        low = (1-F(Q+1, Y))*(1-s(Y+Q, Y)) + F(1, Y)*sum(1-s(Y+q, Y) for q in range(1, Q))
        assert Lam >= low, (Y, Q)
        alt = 1 - F(2, Y) - (1-F(Q+1, Y))*s(Y+Q, Y) - F(1, Y)*sum(s(Y+q, Y) for q in range(1, Q))
        assert low == alt
        cnt += 1
print('(5) 착지 질량 Abel 하계 확인', cnt)
# (6) 정리 5:old-5-33 의 꼴: c_m(Y) >= hov(Y/(m+1),chi) * (착지 핵 정확값의 최소) * Lam   (일반 Y, Q, chi)
#     hov 는 정확히 계산(유한 합), 착지 핵은 Robbins 하계 V 대신 정확값의 최소와 V 를 둘 다 본다.
import math
from fractions import Fraction
def Bor(m): return Fraction(m**(m-1), math.factorial(m))   # e^{-m} 을 뺀 값; 비에서 e 는 소거
# 자유 Borel 보행: Pr(R_z = D) 는 float 로
def borf(i): return math.exp(-i + (i-1)*math.log(i) - math.lgamma(i+1))
def hov(rho, chi):
    # sum_z rho^z Pr(R_z <= chi-1)
    dist = [1.0] + [0.0]*(chi-1)   # R_0 = 0
    tot = 1.0; z = 0
    while True:
        z += 1
        new = [0.0]*chi
        for a in range(chi):
            if dist[a] == 0: continue
            for i in range(1, chi-a):
                new[a+i] += dist[a]*borf(i)
        dist = new
        sm = sum(dist)
        if sm == 0: break
        tot += rho**z*sm
    return tot
def Vlow(m, Y, chi, Q):
    return (2*math.pi)**-0.5*((m+1)/((Y+1)*(m-Y)))**1.5*math.exp(-1/(12*(m-chi-Y-Q+1)) - 1/(12*(Y+1)))
cnt = 0; worst = 1e9
for Y in range(8, 23):
    for Q in range(1, 6):
        for chi in range(2, 6):
            for m in range(Y+Q+chi+1, min(2*Y+1, N)+1):
                Lam = sum(F(Y, Y+q+1)*c(Y+q, Y) for q in range(1, Q+1))
                rhs = hov(Y/(m+1), chi)*Vlow(m, Y, chi, Q)*float(Lam)
                lhs = float(c(m, Y))
                cnt += 1
                worst = min(worst, lhs/rhs)
                if lhs < rhs: print('정리 T 위반', Y, Q, chi, m, lhs, rhs)
print('(6) 꼭대기 행 하계 꼴 확인', cnt, '최소 비 lhs/rhs =', worst)
# (7) 떠돌기 인자 보조정리: Pr(R_z >= chi) <= z*hv_chi
def hv(chi): return chi**-0.5*(2/math.sqrt(math.pi)*(1+1/chi) + 1/math.sqrt(math.pi))
cnt = 0; worst = 0
for chi in range(4, 80):
    dist = [1.0] + [0.0]*(chi-1)
    for z in range(1, 40):
        new = [0.0]*chi
        for a in range(chi):
            if dist[a] == 0: continue
            for i in range(1, chi-a):
                new[a+i] += dist[a]*borf(i)
        dist = new
        tail = 1 - sum(dist)
        cnt += 1
        worst = max(worst, tail/(z*hv(chi)))
        assert tail <= z*hv(chi) + 1e-12, (chi, z)
print('(7) 떠돌기 꼬리 확인', cnt, '최대 비 =', worst)
