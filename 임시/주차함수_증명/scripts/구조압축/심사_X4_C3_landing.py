# -*- coding: utf-8 -*-
"""심사 X4 — C3(착지 질량의 직접 하계 Λ̂(Y) > 7/10)의 검산.

Λ̂(Y) = Σ_{q=1}^{Q} Y/(Y+q+1) c_{Y+q}(Y),  Q = floor(6 Y^{2/3}).
입력: c_{Y+q}(Y) >= s_{Y+q-1}(Y) - s_{Y+q}(Y)  (2:old-2-34),  s_{Y+q}(Y) <= min(1, 3Y q^{-3/2}) (6:old-7-13; Y>=4000, q<=Y).
Abel 합(가중치 w_q = Y/(Y+q+1) >= 1-(q+1)/Y, 생존 감소):
  Λ̂ >= 1 - 2/Y - (1-(Q+1)/Y) s_Q - (1/Y) Σ_{q=1}^{Q-1} s_q.
(A) 이 하계를 Y=25000부터 격자에서 정확 합으로 계산(상계 s_q <= min(1, 3Y q^{-3/2})를 넣음; 모두 mpmath 고정밀).
(B) F4의 닫힌 꼴 1 - 2/Y - 3Y/Q^{3/2} - 3^{5/3} Y^{-1/3} + 9/sqrt Q + 3/Q^{3/2} 와 비교.
(C) 작은 Y(=4000, 10000)에서 실제 Λ̂(Y)를 s/c 재귀(부록 D.c50의 식)로 배정밀도 계산해 7/10과 견준다(정합성 확인용; 증명 입력 아님).
(D) Abel 합 자체의 산술 검증: 임의의 감소 수열 s_q에 대해 Σ w_q (s_{q-1}-s_q) >= 1-2/Y-(1-(Q+1)/Y)s_Q-(1/Y)Σ s_q 를 수치로 확인.
"""
import mpmath as mp
from math import floor, lgamma, log, exp
import random

mp.mp.dps = 30
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

def LB_exact(Y):
    Y = mp.mpf(Y)
    Q = int(mp.floor(6 * Y**(mp.mpf(2) / 3)))
    sQ = min(mp.mpf(1), 3 * Y * mp.mpf(Q)**(-1.5))
    S = mp.mpf(0)
    # 합: q=1..Q-1 of min(1, 3Y q^{-3/2}); q0 = (3Y)^{2/3}
    q0 = int(mp.floor((3 * Y)**(mp.mpf(2) / 3)))
    S += min(q0, Q - 1)
    for q in range(q0 + 1, Q):
        S += 3 * Y * mp.mpf(q)**(-1.5)
    return 1 - 2 / Y - (1 - mp.mpf(Q + 1) / Y) * sQ - S / Y, Q

def LB_F4(Y):
    Y = mp.mpf(Y)
    Q = mp.floor(6 * Y**(mp.mpf(2) / 3))
    return 1 - 2 / Y - 3 * Y / Q**1.5 - mp.mpf(3)**(mp.mpf(5) / 3) * Y**(-mp.mpf(1) / 3) + 9 / mp.sqrt(Q) + 3 / Q**1.5

P("== (A)(B) Y별 하계: 정확 합 / F4 닫힌 꼴")
mn = None
for Y in [25000, 25001, 25500, 26000, 30000, 40000, 60000, 100000, 200000, 500000, 1000000]:
    lb, Q = LB_exact(Y)
    f4 = LB_F4(Y)
    P(f"Y={Y}: Q={Q} 하계(정확합)={mp.nstr(lb,7)}  F4식={mp.nstr(f4,7)}  >7/10: {lb > mp.mpf(7)/10}")
    if mn is None or lb < mn[0]:
        mn = (lb, Y)
# 25000..26000 전부
mn2 = None
for Y in range(25000, 26001):
    lb, Q = LB_exact(Y)
    if mn2 is None or lb < mn2[0]:
        mn2 = (lb, Y)
P(f"Y=25000..26000 전수: 최소 하계 {mp.nstr(mn2[0],7)} at Y={mn2[1]}")
# 큰 Y 극한: 1 - 3/6^{1.5} = 1 - 0.2041
P("Y→∞ 극한 1-3/6^1.5 =", mp.nstr(1 - 3 / mp.mpf(6)**1.5, 7))
# 단조성 근거: 거친 꼴 LB >= 1 - 2/Y - 3Y/(6Y^{2/3}-1)^{1.5} - 3^{5/3}Y^{-1/3} + 9/sqrt(6Y^{2/3}) ; Y>=25000에서 증가하는지 확인
def LB_crude(Y):
    Y = mp.mpf(Y)
    Qm = 6 * Y**(mp.mpf(2) / 3) - 1
    Qp = 6 * Y**(mp.mpf(2) / 3)
    return 1 - 2 / Y - 3 * Y / Qm**1.5 - mp.mpf(3)**(mp.mpf(5) / 3) * Y**(-mp.mpf(1) / 3) + 9 / mp.sqrt(Qp)
prev = None; mono = True
for Y in sorted([25000 + 250 * i for i in range(0, 400)] + [10**5, 10**6, 10**7, 10**9]):
    v = LB_crude(Y)
    if prev is not None and v < prev:
        mono = False
    prev = v
P(f"거친 꼴(바닥 효과 제거) at Y=25000: {mp.nstr(LB_crude(25000),7)}; 격자에서 Y에 단조 증가: {mono}")

# ---------- (D) Abel 합 산술의 수치 검증 ----------
P("== (D) Abel 부등식 수치 검증(임의의 감소 수열)")
random.seed(1)
okD = True
for trial in range(200):
    Y = random.choice([25000, 30000, 50000])
    Q = floor(6 * Y**(2 / 3))
    s = [1.0]
    cur = 1.0
    for q in range(1, Q + 1):
        cur *= random.uniform(0.95, 1.0)
        s.append(cur)
    lhs = sum(Y / (Y + q + 1) * (s[q - 1] - s[q]) for q in range(1, Q + 1))
    rhs = 1 - 2 / Y - (1 - (Q + 1) / Y) * s[Q] - sum(s[1:Q]) / Y
    if lhs < rhs - 1e-12:
        okD = False
P("Abel 하계가 항상 성립:", okD)

# ---------- (C) 실제 Λ̂(Y) 배정밀도 ----------
P("== (C) 실제 Λ̂(Y) (s/c 재귀, 배정밀도; 정합성 확인용)")
def lamhat_true(Y):
    Q = floor(6 * Y**(2 / 3))
    N = Y + Q
    # Bor(j) = e^{-j} j^{j-1}/j!  (로그)
    def lbor(j):
        return -j + (j - 1) * log(j) - lgamma(j + 1)
    LB_ = [None] + [lbor(j) for j in range(1, N + 3)]
    def pi(n, t):  # 가장 큰 나무 핵, n/2 < t <= n
        return exp(LB_[n + 1 - t] + LB_[t] - LB_[n + 1])
    def run(y):
        # s_n(y), c_n(y) for n <= N (<= 2y+1 이어야 함)
        s = [1.0] * (N + 1)   # n <= y: 1
        c = [0.0] * (N + 1)
        # pi0_n(y) = 1 - sum_{t>y} pi_n(t)  (n <= 2y+1 에서 유효)
        for n in range(y + 1, N + 1):
            tot = 0.0; acc_s = 0.0; acc_c = 0.0
            for t in range(y + 1, n + 1):
                p = pi(n, t)
                tot += p
                acc_s += p * y / t * s[t - 1]
                acc_c += p / t * (sY1[t - 1] + y * c[t - 1]) if sY1 is not None else 0.0
            s[n] = (1 - tot) + acc_s
            c[n] = acc_c
        return s, c
    # c_n(y) 재귀는 s_{t-1}(y+1)을 요구 → 먼저 용량 y+1의 s를 계산
    sY1 = None
    s1, _ = run(Y + 1)
    sY1 = s1
    s0, c0 = run(Y)
    # 검산: c_n(y) = s_n(y+1) - s_n(y)
    maxdev = max(abs(c0[n] - (s1[n] - s0[n])) for n in range(Y + 1, N + 1))
    lam = sum(Y / (Y + q + 1) * c0[Y + q] for q in range(1, Q + 1))
    lam_from_s = sum(Y / (Y + q + 1) * (s0[Y + q - 1] - s0[Y + q]) for q in range(1, Q + 1))
    return lam, lam_from_s, maxdev, Q
for Y in [4000, 10000]:
    lam, lam2, dev, Q = lamhat_true(Y)
    P(f"Y={Y}: Q={Q} Λ̂(Y)={lam:.5f}; Σ w_q (s_{{q-1}}-s_q) = {lam2:.5f} (old-2-34 방향 확인: Λ̂ >= 이 값 → {lam >= lam2 - 1e-9}); c=s(y+1)-s(y) 최대 편차 {dev:.2e}")

open(__file__.replace('.py', '_out.txt'), 'w', encoding='utf-8').write("\n".join(out) + "\n")
