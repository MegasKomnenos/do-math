# -*- coding: utf-8 -*-
# 결정 K2 — C3: 착지 질량 Λ̂(Y)=Σ_{q=1}^{Q} Y/(Y+q+1) c_{Y+q}(Y), Q=floor(6Y^{2/3}) 의 하계를
#   2.34(가중 꼴, 장2:558–560)의 Abel 합 + 첫 층 생존 상계(10.21′: s_{Y+q}(Y)=𝔰_{q+1}(Y) ≤ min(1, 1.15(Y+q+1)/(q+1)^{3/2}), Y≥3130)
#   로 세운다.  하계: 1 - 2/Y - (1-(Q+1)/Y) s_Q - (1/Y) Σ_{q=1}^{Q-1} s_q   (심사 A4 (1)에서 정확 분수로 검산된 Abel 꼴).
# (a) 직접 합(배정밀도) Y=25000,…; (b) 닫힌 꼴(적분 비교) 전수 Y=25000..2e6 + 큰 Y 포락선 단조; (c) 𝗐0=4/5 의 여유와 임계 Y;
# (d) 비교: 6.1 꼴(상수 3) 하계.  실행: python -I 결정_K2_C3_착지질량.py
import sys
import numpy as np
from mpmath import mp, mpf, sqrt, floor
sys.stdout.reconfigure(encoding='utf-8')
mp.dps = 30
MS = 1.15

def Q_of(Y):
    lo, hi = 0, 6*int(round(Y**(2/3)))+5
    while lo < hi:
        mid = (lo+hi+1)//2
        if mid**3 <= 216*Y*Y: lo = mid
        else: hi = mid-1
    return lo

def s_up(Y, q):   # 10.21′: s_{Y+q}(Y) ≤ min(1, 1.15 (Y+q+1)/(q+1)^{3/2})
    return min(1.0, MS*(Y+q+1)/(q+1)**1.5)

def LB_direct(Y):
    Q = Q_of(Y)
    S = sum(s_up(Y, q) for q in range(1, Q))
    sQ = s_up(Y, Q)
    return 1 - 2/Y - (1-(Q+1)/Y)*sQ - S/Y, Q

# 닫힌 꼴: f(x)=min(1, 1.15(Y+x+1)/(x+1)^{3/2}) 는 x 에 비증가 → Σ_{q=1}^{Q-1} f(q) ≤ ∫_0^{Q-1} f(x)dx.
#   x0: (x0+1)^{3/2} = 1.15 (Y+x0+1)  (x0+1 =: z0, z0^{3/2}-1.15 z0 = 1.15 Y) ;  ∫_{x0}^{Q-1} 1.15(Y+x+1)(x+1)^{-3/2} dx = 2.3[ (z^{1/2} - Y z^{-1/2}) ]_{z0}^{Q}
def z0_of(Y):
    # z^{3/2} - 1.15 z = 1.15 Y 의 양근 (이분법)
    lo, hi = 1.0, (1.15*Y)**(2/3)*2+10
    for _ in range(200):
        mid = (lo+hi)/2
        if mid**1.5 - MS*mid < MS*Y: lo = mid
        else: hi = mid
    return hi   # 상계 쪽 (x0 를 크게 잡으면 ∫ 1 구간이 늘어 하계가 보수적)

def LB_closed(Y):
    Q = Q_of(Y)
    z0 = z0_of(Y)
    x0 = z0 - 1
    integ = x0 + 2*MS*((Q**0.5 - Y*Q**-0.5) - (z0**0.5 - Y*z0**-0.5))
    sQ = s_up(Y, Q)
    return 1 - 2/Y - (1-(Q+1)/Y)*sQ - integ/Y, Q

print("(a) 직접 합 대 닫힌 꼴 (10.21′, 𝗆_S=1.15)")
for Y in (25000, 25001, 30000, 33334, 50000, 100000, 10**6):
    d, Q = LB_direct(Y); c, _ = LB_closed(Y)
    print(f"   Y={Y:>8} Q={Q:>6}  직접합 하계={d:.6f}  닫힌 꼴 하계={c:.6f}  (닫힌≤직접: {c <= d + 1e-12})")

print("(b) 닫힌 꼴 전수 Y=25000..2,000,000 (배정밀도 벡터화)")
Ys = np.arange(25000, 2_000_001, dtype=np.int64)
Qs = np.floor(6*np.power(Ys.astype(float), 2/3)).astype(np.int64)
bad = (Qs**3 > 216*Ys*Ys); Qs[bad] -= 1
bad2 = ((Qs+1)**3 <= 216*Ys*Ys); Qs[bad2] += 1
assert np.all(Qs**3 <= 216*Ys*Ys) and np.all((Qs+1)**3 > 216*Ys*Ys)
Yf = Ys.astype(float); Qf = Qs.astype(float)
# z0: 뉴턴 몇 번 (z^{1.5}-1.15z-1.15Y=0), 시작 (1.15Y)^{2/3}+1.15
z = (MS*Yf)**(2/3) + MS
for _ in range(60):
    z = z - (z**1.5 - MS*z - MS*Yf)/(1.5*z**0.5 - MS)
z0 = z*(1+1e-12)  # 보수적으로 조금 크게
integ = (z0-1) + 2*MS*((Qf**0.5 - Yf*Qf**-0.5) - (z0**0.5 - Yf*z0**-0.5))
sQ = np.minimum(1.0, MS*(Yf+Qf+1)/(Qf+1)**1.5)
LBs = 1 - 2/Yf - (1-(Qf+1)/Yf)*sQ - integ/Yf
i = int(np.argmin(LBs))
print(f"   최솟값 {LBs[i]:.6f} at Y={Ys[i]} (Q={Qs[i]}); Y=25000 값 {LBs[0]:.6f}; Y=2e6 값 {LBs[-1]:.6f}; 0.8 미만 개수 {int((LBs<0.8).sum())}; 0.82 미만 개수 {int((LBs<0.82).sum())}")
# 큰 Y 포락선: Q 를 불리한 쪽(음의 항엔 6Y^{2/3}-1, 양의 항엔 6Y^{2/3})으로 둔 함수가 Y>=2e6 에서 증가하는지 로그 표본
def env(Y):
    Y = mpf(Y); Qm = 6*Y**(mpf(2)/3)-1; Qp = 6*Y**(mpf(2)/3)
    # z0 (mp)
    lo, hi = mpf(1), (MS*Y)**(mpf(2)/3)*2+10
    for _ in range(300):
        mid = (lo+hi)/2
        if mid**mpf(1.5) - MS*mid < MS*Y: lo = mid
        else: hi = mid
    z0 = hi
    integ = (z0-1) + 2*MS*((sqrt(Qp) - Y/sqrt(Qp)) - (sqrt(z0) - Y/sqrt(z0)))
    sQ = MS*(Y+Qm+1)/(Qm+1)**mpf(1.5)
    return 1 - 2/Y - (1-(Qm+1)/Y)*sQ - integ/Y
prev = None; mono = True
for e in range(0, 41):
    Y = int(2_000_000*(mpf(10)**(mpf(e)/10)))
    v = env(Y)
    if prev is not None and v <= prev: mono = False
    prev = v
print(f"   Y≥2e6 포락선 로그 표본(2e6..2e10) 단조 증가: {mono}; env(2e6)={float(env(2_000_000)):.6f}, env(2e10)={float(env(20_000_000_000)):.6f}")

print("(c) 𝗐0 후보")
Ymin = None
for Y in range(25000, 3129, -1):
    if Q_of(Y)+1 > Y: break
    v, _ = LB_closed(Y)
    if v < 0.8:
        Ymin = Y+1; break
print(f"   닫힌 꼴 하계 ≥ 4/5 가 되는 첫 Y = {Ymin} (그 아래 첫 실패 Y={Ymin-1}: {LB_closed(Ymin-1)[0]:.5f});  Y≥25000 전체의 최솟값(내림 4자리) = {np.floor(LBs.min()*10000)/10000:.4f}")
# 10.21′의 적용 조건: q+1 ≤ Y+2 ⇔ Q ≤ Y+1 (Y≥216 에서 6Y^{2/3} ≤ Y); Y≥3130 — 조립의 Y≥25000 안.
print(f"   적용 조건: Q(25000)={Q_of(25000)} ≤ 25001 ✓;  Y≥25000 ≥ 3130 ✓")

print("(d) 비교: 6.1 꼴(상수 3; s_{Y+q}(Y) ≤ 3Y q^{-3/2}) 닫힌 꼴 — 심사 A4 의 0.708 재현")
def LB_C3(Y, C=3.0):
    Q = Q_of(Y); q0 = (C*Y)**(2/3)
    S = q0 + 2*C*Y*(q0**-0.5 - (Q-1)**-0.5)
    sQ = min(1.0, C*Y/Q**1.5)
    return 1 - 2/Y - (1-(Q+1)/Y)*sQ - S/Y
print(f"   Y=25000: 상수 3 꼴 {LB_C3(25000):.6f};  10.21′ 꼴 {LB_closed(25000)[0]:.6f};  현행 𝗐0=0.71216")
