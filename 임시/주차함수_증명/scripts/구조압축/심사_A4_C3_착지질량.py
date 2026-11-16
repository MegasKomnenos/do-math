# 심사 A4 — C3 착지 질량 직접 하계의 재계산
# 주장(F4 §4, F7 §2): hatLambda(Y) = sum_{q=1}^{Q} Y/(Y+q+1) c_{Y+q}(Y), Q = floor(6 Y^{2/3}),
#   2.35(항별) c_m(Y) >= s_{m-1}(Y) - s_m(Y),  6.1: s_{Y+q}(Y) <= min(1, 3 Y q^{-3/2}) (Y>=4000, q<=Y)
#   => hatLambda(Y) >= 1 - 2/Y - (1-(Q+1)/Y) s_Q - (1/Y) sum_{q=1}^{Q-1} s_q  >= 7/10 (Y>=25000).
# 이 스크립트는 (1) Abel 합 항등식을 기호 없이 작은 Y에서 임의 수열로 검산하고,
# (2) 적분 비교까지 넣은 닫힌 하계 LB(Y)를 mpmath 30자리로 Y=25000..2e6 전부와 그 위 표본에서 평가하며,
# (3) 상수 3 대신 10.21의 1.15를 넣었을 때의 값, (4) 하계가 0.7을 처음 넘는 Y를 찾는다.
import sys, random
from fractions import Fraction as Fr
from mpmath import mp, mpf, floor, sqrt, cbrt
mp.dps = 30

def Q_of(Y):
    # floor(6 Y^{2/3}) 를 정수 산술로: 최대 Q with Q^3 <= 216 Y^2
    lo, hi = 0, 6*int(round(Y**(2/3)))+5
    while lo < hi:
        mid = (lo+hi+1)//2
        if mid**3 <= 216*Y*Y: lo = mid
        else: hi = mid-1
    return lo

# (1) Abel 합 항등식 검산: 임의의 비증가 수열 s_0=1>=s_1>=...>=s_Q>=0 과 c_q := s_{q-1}-s_q 에 대해
#     sum w_q c_q = w_1 s_0 + sum_{q=1}^{Q-1} (w_{q+1}-w_q) s_q - w_Q s_Q  (w_q = Y/(Y+q+1))
#     그리고 w'_q = 1-(q+1)/Y <= w_q 로 바꾼 하계 1-2/Y-(1-(Q+1)/Y)s_Q-(1/Y)sum s_q 가 실제로 하계인지.
random.seed(4)
for trial in range(200):
    Y = random.randint(30, 200); Q = random.randint(2, Y-1)
    s = [Fr(1)]
    for q in range(1, Q+1):
        s.append(s[-1]*Fr(random.randint(0, 1000), 1000))
    c = [None]+[s[q-1]-s[q] for q in range(1, Q+1)]
    w = [None]+[Fr(Y, Y+q+1) for q in range(1, Q+1)]
    lhs = sum(w[q]*c[q] for q in range(1, Q+1))
    abel = w[1]*s[0] + sum((w[q+1]-w[q])*s[q] for q in range(1, Q)) - w[Q]*s[Q]
    assert lhs == abel, (Y, Q)
    lb = 1 - Fr(2, Y) - (1-Fr(Q+1, Y))*s[Q] - Fr(1, Y)*sum(s[q] for q in range(1, Q))
    assert lhs >= lb, (Y, Q, float(lhs), float(lb))
print("(1) Abel 합 항등식과 w'_q 치환 하계: 200회 정확 분수 검산 통과")

# (2) 닫힌 하계. S(Y) := sum_{q=1}^{Q-1} min(1, 3Y q^{-3/2}) <= int_0^{Q-1} min(1, C Y x^{-3/2}) dx
#     = q0 + 2 C Y (q0^{-1/2} - (Q-1)^{-1/2}),  q0 = (C Y)^{2/3}  (피적분함수가 비증가이므로 f(q) <= int_{q-1}^q f)
def LB(Y, C=mpf(3), Q=None):
    Y = mpf(Y)
    if Q is None: Q = Q_of(int(Y))
    Q = mpf(Q)
    q0 = (C*Y)**(mpf(2)/3)
    assert q0 <= Q-1
    S = q0 + 2*C*Y*(1/sqrt(q0) - 1/sqrt(Q-1))
    sQ = min(mpf(1), C*Y/Q**mpf('1.5'))
    return 1 - 2/Y - (1-(Q+1)/Y)*sQ - S/Y

def LB_F4(Y):
    # F4가 적은 꼴: 1 - 2/Y - 3Y/Q^{3/2} - 3^{5/3} Y^{-1/3} + 9/sqrt(Q) + 3/Q^{3/2}
    Y = mpf(Y); Q = mpf(Q_of(int(Y)))
    return 1 - 2/Y - 3*Y/Q**mpf('1.5') - mpf(3)**(mpf(5)/3)/cbrt(Y) + 9/sqrt(Q) + 3/Q**mpf('1.5')

def S_direct(Y, C=3.0):
    Q = Q_of(Y)
    return sum(min(1.0, C*Y*q**-1.5) for q in range(1, Q)), Q

for Y in (25000, 25001, 30000, 33334, 50000, 100000):
    Sd, Q = S_direct(Y)
    print(f"Y={Y} Q={Q}  LB(내 셈)={LB(Y)}  LB(F4식)={LB_F4(Y)}  이산합 S={Sd:.4f} 적분상계={float(LB(Y)) and float((3*Y)**(2/3)+6*Y*((3*Y)**(-1/3)-(Q-1)**-0.5)):.4f}")

# 전수: Y=25000..2,000,000 (mpmath는 느리므로 numpy 배정밀도로 전수, mpmath로 최솟값 자리 재확인)
import numpy as np
Ys = np.arange(25000, 2_000_001, dtype=np.int64)
Qs = np.floor(6*np.power(Ys.astype(float), 2/3)).astype(np.int64)
# floor 보정(부동소수 오차): Q^3 <= 216 Y^2 < (Q+1)^3 를 정수로 강제
bad = (Qs**3 > 216*Ys*Ys); Qs[bad] -= 1
bad2 = ((Qs+1)**3 <= 216*Ys*Ys); Qs[bad2] += 1
assert np.all(Qs**3 <= 216*Ys*Ys) and np.all((Qs+1)**3 > 216*Ys*Ys)
Yf = Ys.astype(float); Qf = Qs.astype(float)
q0 = (3*Yf)**(2/3)
S = q0 + 6*Yf*(q0**-0.5 - (Qf-1)**-0.5)
sQ = np.minimum(1.0, 3*Yf/Qf**1.5)
LBs = 1 - 2/Yf - (1-(Qf+1)/Yf)*sQ - S/Yf
i = int(np.argmin(LBs))
print(f"(2) Y=25000..2e6 전수(배정밀도): 최솟값 LB={LBs[i]:.6f} at Y={Ys[i]}, Q={Qs[i]};  Y=25000의 값 {LBs[0]:.6f};  mpmath 재확인 {LB(int(Ys[i]))}")
print(f"    LB<0.7 인 Y 개수: {int(np.sum(LBs<0.7))};  LB의 최댓값(Y=2e6 근처): {LBs[-1]:.6f}")
# 큰 Y: Q >= 6Y^{2/3}-1 을 음의 항에, Q <= 6Y^{2/3} 을 양의 항에 넣은 포락선이 증가함을 표본으로
def env(Y):
    Y = mpf(Y); Qm = 6*Y**(mpf(2)/3)-1; Qp = 6*Y**(mpf(2)/3)
    q0 = (3*Y)**(mpf(2)/3)
    S = q0 + 6*Y*(1/sqrt(q0) - 1/sqrt(Qp-1))
    sQ = 3*Y/Qm**mpf('1.5')
    return 1 - 2/Y - (1-(Qm+1)/Y)*sQ - S/Y
prev = None
for e in range(0, 41):
    Y = int(2_000_000*(mpf(10)**(mpf(e)/10)))
    v = env(Y)
    assert prev is None or v > prev
    prev = v
print(f"(2') Y>=2e6 포락선(Q를 불리한 쪽으로 둔 것)은 2e6..2e10 로그 표본에서 단조 증가; env(2e6)={env(2_000_000)}  env(2e10)={env(20_000_000_000)}")

# (3) 10.21의 상수 1.15 (y>=6666 또는 S3대로 4000)를 넣으면
for Y in (25000, 50000):
    print(f"(3) C=1.15: Y={Y}  LB={LB(Y, C=mpf('1.15'))}")

# (4) 0.7을 넘는 최소 Y (C=3): 아래로 훑기
Ymin = None
for Y in range(25000, 3999, -1):
    if Q_of(Y)+1 > Y: break
    if LB(Y) < mpf('0.7'):
        Ymin = Y+1; break
print(f"(4) C=3: LB(Y)>=0.7 이 Y>={Ymin} 부터 (6.1의 범위 Y>=4000 안; 그 아래 첫 실패 Y={Ymin-1}, 값 {LB(Ymin-1)})")
# 0.7 대신 가능한 상수: Y>=25000 전체의 최솟값
print(f"(4') Y>=25000 에서 쓸 수 있는 상수(내림): {float(LBs.min()):.4f}")
