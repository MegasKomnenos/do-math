# -*- coding: utf-8 -*-
# 검토 24차 R4: 보조정리 5:landing-mass 를 Y=25000 (과 Y=25001, 40000) 에서 배정밀도로 직접 세어 본다.
# 생존 확률은 정리 2:old-2-13(나)의 열 재귀 s_n(y)=pi0_n(y)+sum_{t=y+1}^n pi_n(t) (y/t) s_{t-1}(y) 로 센다(n<=2y+1).
import math
import numpy as np


def lbor_arr(a):
    a = np.asarray(a, dtype=float)
    from math import lgamma
    lg = np.array([lgamma(v + 1.0) for v in a])
    return -a + (a - 1.0) * np.log(a) - lg


def survival_column(y, nmax):
    # s[n] for n = y .. nmax  (index n-y); s_y(y) = 1
    s = np.ones(nmax - y + 1)
    lb_cache = lbor_arr(np.arange(1, nmax + 3))  # lbor(1..nmax+2), index i-1

    def lb(i):
        return lb_cache[np.asarray(i) - 1]

    for n in range(y + 1, nmax + 1):
        t = np.arange(y + 1, n + 1)
        lpi = lb(t) + lb(n + 1 - t) - lb(n + 1)
        pi = np.exp(lpi)
        pi0 = 1.0 - pi.sum()
        s[n - y] = pi0 + np.dot(pi * (y / t), s[t - 1 - y])
    return s


def landing(Y):
    qmax = math.floor(6 * Y ** (2 / 3))
    nmax = Y + qmax
    sY = survival_column(Y, nmax)        # s_m(Y), m=Y..nmax
    sY1 = survival_column(Y + 1, nmax)   # s_m(Y+1), m=Y+1..nmax
    lam = 0.0
    for q in range(1, qmax + 1):
        m = Y + q
        c = sY1[m - (Y + 1)] - sY[m - Y]
        lam += Y / (Y + q + 1) * c
    # 본문 첫째 하계
    def phi(d):
        return 1.15 * (Y + d) / d ** 1.5
    first = 1 - 2 / Y - (1 - (qmax + 1) / Y) * phi(qmax + 1) - sum(min(1.0, phi(q + 1)) for q in range(1, qmax)) / Y
    # 수준 방문 보존으로 얻는 하계(생존 확률의 참값을 넣은 것)
    abel = (1 - (qmax + 1) / Y) * (1 - sY[qmax]) + sum(1 - sY[q] for q in range(1, qmax)) / Y
    # 정리 6:old-8-25 의 상계가 표본에서 맞는지
    okS = all(sY[q] <= min(1.0, phi(q + 1)) + 1e-12 for q in range(1, qmax + 1))
    u = Y ** (1 / 3)
    closed = 0.9217 - 2.3541 / u - 0.4074 / u ** 2 - 2 / u ** 3
    return qmax, lam, abel, first, closed, okS


for Y in (25000, 25001, 40000):
    qmax, lam, abel, first, closed, okS = landing(Y)
    print("Y=%d qmax=%d  착지 질량=%.6f  >= Abel 하계(참 생존)=%.6f  >= 본문 첫째 하계=%.6f  >= 닫힌 꼴=%.6f  >= 0.8 ; 생존 상계 %s"
          % (Y, qmax, lam, abel, first, closed, "OK" if okS else "FAIL"))
    assert lam >= abel - 1e-9 >= first - 1e-9 and first >= closed - 1e-12 and closed > 0.8
