# -*- coding: utf-8 -*-
# 결정 K2 — 6장 첫 층: (S2) Ren(n+1)/Ren(n) ≥ 1-1/(2n) (정확 유리수 n≤2000 + 해석 꼴), 한 칸 손실 D_{n,k} ≥ -(k-1)/(2n)·Bor(n)c_{n-1}(k-1) (수치, k=2001·3131),
#   (S1) 𝔚0 = Σ_{n=k+1}^{2k} Bor(n) c_{n-1}(k-1) < (2/e)𝗌_B k^{-3/2} = 2(2π)^{-1/2} k^{-3/2} (수치), 새 𝔡(k)=1/e+𝗎(k)/(e 2^{3/2}) 대 현행 𝔡(k),
#   (추가 1) 절단점 하계: 𝒱_k(m) ≥ (k-1)/(R+1)[1 - U(m) - s_R^{up}] - 𝗎♭(k), R=⌊3(k-1)/2⌋, 0 ≤ d=m-k ≤ m^{2/3}/2,
#       U(m) ≤ (2π)^{-1/2}(1+d/k)^{3/2}((4/3)d^{3/2}+2√d)/(k-1) (합집합 상계의 닫힌 꼴), s_R^{up}=1.15(R+1)/(q+1)^{3/2} (q=⌊(k-1)/2⌋; 10.21′),
#       𝗎♭(k)=(1.15/0.35)(2+1/k)(0.65-1/k)^{-3/2}k^{-1/2}  — k=2001·3131 의 참값과 나란히; k≥3131 격자에서 균일 하계.
#   배정밀도 재귀는 심사 A5 의 모듈(심사_A5_2_float.py)의 surv 를 쓴다.  실행: python -I 결정_K2_6장_S1S2_절단점.py
import sys, os, importlib.util
from fractions import Fraction as F
from math import sqrt, pi, exp, log, floor
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('a5', os.path.join(here, '심사_A5_2_float.py'))
a5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a5)
surv, Bor, Ren = a5.surv, a5.Bor, a5.Ren
sB = exp(1)/sqrt(2*pi); gamma_W = 2*exp(0.0031)/exp(1)

print("(S2-a) Ren(n+1)/Ren(n) = (1+1/n)^n/e ≥ 1-1/(2n): 해석 꼴  n log(1+1/n) - 1 ≥ -1/(2n)+1/(3n^2)-1/(4n^3) > log(1-1/(2n)) (n≥1)")
from mpmath import mp, mpf, log as mlog
mp.dps = 60
bad = 0; minmargin = None; fails = []
for n in list(range(1, 2001)) + [10**4, 10**5, 10**6, 10**9]:
    n_ = mpf(n)
    lhs = n_*mlog(1+1/n_) - 1
    taylor = -1/(2*n_) + 1/(3*n_**2) - 1/(4*n_**3)
    rhs = mlog(1 - 1/(2*n_))
    if not (lhs >= taylor and taylor > rhs): bad += 1; fails.append(n)
    mg = float(lhs - rhs)
    if minmargin is None or mg < minmargin[0]: minmargin = (mg, n)
print(f"   위반 0? {bad == 0} (실패 n: {fails});  최소 여유 log 차 {minmargin[0]:.3e} at n={minmargin[1]}")
# 정확 유리수 확인: (1+1/n)^n ≥ e(1-1/(2n)) 는 e 때문에 유리수로 못 하므로 (n+1)^n·2n ≥ e·n^n(2n-1) 를 e 의 유리 상계 2.7182818285 로
E_UP = F(27182818285, 10**10)
ok = all(F((n+1)**n*2*n) >= E_UP*F(n**n*(2*n-1)) for n in range(1, 301))
print(f"   정확 유리수(e 상계) n=1..300: {ok}")

def analyze(k):
    M = 2*k+1
    s_km1 = surv(k-1, M); s_k = surv(k, M); s_kp1 = surv(k+1, M)
    c_k = s_kp1 - s_k; c_km1 = s_k - s_km1
    n = np.arange(k+1, 2*k+1)
    # (S2-b) 한 칸 손실
    D = (k+1)*Bor(n+1)*c_k[n] - (k-1)*Bor(n)*c_km1[n-1]
    base = Bor(n)*c_km1[n-1]
    ratio = D/base; bound = -(k-1)/(2*n)
    print(f"\n==== k={k}")
    print(f"(S2-b) min_n [D_n/(Bor(n)c_(n-1)(k-1)) + (k-1)/(2n)] = {(ratio-bound).min():.5f} (≥0 이면 성립); 대각선 비 min_n [(k+1)c_n(k)/(n+1)] / [(k-1)c_(n-1)(k-1)/n] = {((k+1)*c_k[n]/(n+1)/((k-1)*c_km1[n-1]/n)).min():.6f} (6.21 꼴 ≥1?)")
    # (S1) 𝔚0
    W0 = (Bor(n)*c_km1[n-1]).sum()
    print(f"(S1)   𝔚0 = {W0:.6e};  𝔚0 / [2(2π)^(-1/2) k^(-3/2)] = {W0/(2/sqrt(2*pi)*k**-1.5):.4f};  𝔚0/[γ_W 𝗌_B k^(-3/2)] = {W0/(gamma_W*sB*k**-1.5):.4f};  Σ_n (k-1)c_(n-1)(k-1)/n = {((k-1)*c_km1[n-1]/n).sum():.4f}")
    # 𝔡(k)
    u = (3/0.35)*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
    ub = (1.15/0.35)*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
    d_old = gamma_W*(0.5+2.5/k+0.25/k**2) + u/(exp(1)*2**1.5)
    d_new = 1/exp(1) + u/(exp(1)*2**1.5)
    print(f"       𝗎(k)={u:.4f} (참 (k-1)c_2k(k-1)={(k-1)*c_km1[2*k]:.4f}; k c_2k(k-1)={k*c_km1[2*k]:.4f}), 𝗎♭(k)={ub:.4f};  𝔡 현행={d_old:.6f}, 새={d_new:.6f}, 새<현행: {d_new < d_old}")
    # (추가 1) 절단점 하계
    R = (3*(k-1))//2; q = R-(k-1)
    sR_true = s_km1[R]; sR_up = min(1.0, 1.15*(R+1)/(q+1)**1.5); sR_up3 = min(1.0, 3*(k-1)*q**-1.5)
    terms = (k+1)*c_k - (k-1)*c_km1
    def U_closed(d): return (2*pi)**-0.5*(1+d/k)**1.5*((4/3)*d**1.5+2*sqrt(d))/(k-1)
    def U_exact(m):   # Σ_{t=k}^{m-1} θ_m(t)(t-k+1)/t ,  θ_m(t)=Bor(t)Ren(m-t)/Bor(m)
        if m-1 < k: return 0.0
        t = np.arange(k, m)
        return float((Bor(t)*Ren(m-t)/Bor(m)*(t-k+1)/t).sum())
    dmax = 0
    while (k+dmax+1)**(2/3)/2 >= dmax+1: dmax += 1
    print(f"(추가1) R={R}, q={q}: s_R 참={sR_true:.4f}, 10.21′ 상계={sR_up:.4f}, 6.1 상계={sR_up3:.4f}; d 범위 0..{dmax} (=⌊m^(2/3)/2⌋)")
    print("        d | 𝒱_k(m) 참 | 세 줄 하계(참 s) | 증명 하계(정확 합집합·1.15) | 증명 하계(닫힌 U·1.15) | 증명 하계(닫힌 U·상수 3)")
    worst = None
    for d in [0, 1, 5, 13, 14, 30, 60, dmax//2, dmax]:
        m = k+d
        V = terms[m:2*k+1].sum()
        lb_true = (k-1)/(R+1)*(s_km1[m-1]-sR_true) - (k-1)*c_km1[2*k]
        lb_ex = (k-1)/(R+1)*((1-U_exact(m))-sR_up) - ub
        lb_cl = (k-1)/(R+1)*((1-U_closed(d))-sR_up) - ub
        lb_c3 = (k-1)/(R+1)*((1-U_closed(d))-sR_up3) - u
        print(f"      {d:4d} | {V:.5f} | {lb_true:.5f} | {lb_ex:.5f} | {lb_cl:.5f} | {lb_c3:.5f}")
    # 전 범위 최소(닫힌 U 는 d 에 증가 → d=dmax 가 최악)
    lb_all = min((k-1)/(R+1)*((1-U_closed(d))-sR_up) - ub for d in range(0, dmax+1))
    print(f"        닫힌 U·1.15 하계의 d∈[0,{dmax}] 최솟값 = {lb_all:.4f};  참 𝒱_k(m) 의 같은 범위 최솟값 = {min(terms[k+d:2*k+1].sum() for d in range(0, dmax+1)):.4f}")
    return lb_all

for k in (2001, 3131):
    analyze(k)

print("\n(추가1-균일) k≥3131 격자에서 닫힌 하계의 최솟값 (d=⌊m^(2/3)/2⌋ 최대에서 평가; 하계는 d 에 감소하므로 그 값이 범위 최솟값)")
def lb_uniform(k):
    R = (3*(k-1))//2; q = R-(k-1)
    sR_up = min(1.0, 1.15*(R+1)/(q+1)**1.5)
    ub = (1.15/0.35)*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
    d = 0
    while (k+d+1)**(2/3)/2 >= d+1: d += 1
    U = (2*pi)**-0.5*(1+d/k)**1.5*((4/3)*d**1.5+2*sqrt(d))/(k-1)
    return (k-1)/(R+1)*((1-U)-sR_up) - ub, d, U, sR_up, ub
ks = list(range(3131, 3231)) + list(range(3231, 20001, 97)) + list(range(20001, 10**6, 9973)) + [10**6, 10**7, 10**8]
vals = [(lb_uniform(k)[0], k) for k in ks]
mn = min(vals)
v3131 = lb_uniform(3131); v2001 = lb_uniform(2001); vinf = lb_uniform(10**8)
print(f"   최솟값 {mn[0]:.4f} at k={mn[1]};  k=3131: 하계 {v3131[0]:.4f} (d={v3131[1]}, U≤{v3131[2]:.4f}, s_R≤{v3131[3]:.4f}, 𝗎♭={v3131[4]:.4f});  k=2001: {v2001[0]:.4f} (d={v2001[1]});  k=1e8: {vinf[0]:.4f} (극한 2/3·(1-0.188)≈0.541)")
print(f"   k 에 증가(격자 표본, 인접 비교에서 감소 횟수): {sum(1 for i in range(len(vals)-1) if vals[i+1][0] < vals[i][0])}")
# 상수 3 꼴(6.1 그대로)로도 되는지
def lb_uniform3(k):
    R = (3*(k-1))//2; q = R-(k-1)
    sR_up = min(1.0, 3*(k-1)*q**-1.5)
    u = (3/0.35)*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
    d = 0
    while (k+d+1)**(2/3)/2 >= d+1: d += 1
    U = (2*pi)**-0.5*(1+d/k)**1.5*((4/3)*d**1.5+2*sqrt(d))/(k-1)
    return (k-1)/(R+1)*((1-U)-sR_up) - u
print(f"   (참고) 6.1 상수 3 꼴: k=3131 {lb_uniform3(3131):.4f}, k=4001 {lb_uniform3(4001):.4f}, k=10001 {lb_uniform3(10001):.4f}  — 양이지만 여유가 얇다")

# 균일 하계의 k-단조 포락선: d 를 실수 d*(k) (d=(k+d)^{2/3}/2 의 해)로 두면 각 항이 k 에 단조
def lb_env(k):
    d = (k**(2/3))/2
    for _ in range(100): d = ((k+d)**(2/3))/2
    R = 1.5*(k-1); q = (k-1)/2 - 1            # (k-1)/(R+1) >= 2(k-1)/(3(k-1)+2),  q >= (k-1)/2 - 1 (내림)
    sR_up = 1.15*(1.5*(k-1)+1)/((k-1)/2)**1.5 # (R+1) <= 1.5(k-1)+1, q+1 >= (k-1)/2
    ub = (1.15/0.35)*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
    U = (2*pi)**-0.5*(1+d/k)**1.5*((4/3)*d**1.5+2*sqrt(d))/(k-1)
    return 2*(k-1)/(3*(k-1)+2)*((1-U)-sR_up) - ub, d, U, sR_up
envs = [(lb_env(k), k) for k in ks]
dec = sum(1 for i in range(len(envs)-1) if envs[i+1][0][0] < envs[i][0][0])
e3131 = lb_env(3131)
print(f"   (포락선) 실수 d*(k) 와 바닥 상수로 둔 포락선: k=3131 값 {e3131[0]:.4f} (d*={e3131[1]:.2f}, U<={e3131[2]:.4f}, s_R<={e3131[3]:.4f}); 격자에서 감소 횟수 {dec} (0 이면 k 에 단조 증가 => k=3131 값이 모든 k>=3131 의 하계)")
