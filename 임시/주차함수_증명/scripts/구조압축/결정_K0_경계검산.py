# -*- coding: utf-8 -*-
# 결정 K0 — 경계 항목을 하나로 닫는 데 쓴 검산.
#   (A) S3: 정리 10.21 증명 7단계의 닫힌 꼴 네 경우를 y 의 함수로 다시 센다(상위해 상수 1.15, 𝔞'=⌊(1.15y)^{2/3}⌋, q≥𝔞'+1).
#       — 1–6단계는 y 조건을 쓰지 않음(장10 468–491행 원문 정독). y=2000·1289·1288 의 값과, 2.82/q 경우가 1.15 아래로 떨어지는 q 의 문턱.
#   (B) 절단점 하계(K1 N4 와 K2 (차)의 통합): K2 의 닫힌 꼴(합집합 상계의 닫힌 꼴 U, 10.21′ 의 s_R 상계, 𝗎♭(k))로
#       k≥2001 격자에서 하계의 최솟값과 k-단조 포락선을 세어 통합 상수를 고른다(K2 스크립트 lb_uniform·lb_env 의 식을 그대로 옮김).
#   (C) 6.45 의 셋째 단계: 10.19′ 의 R(k)=DDL♮(k) 에 대해 R(k)/2 ≤ 50.62/√(k−1) (k≥3131) 과 R 의 감소 — 𝗏(k) 의 값이 바뀌지 않음.
#   (D) 10.21′ 의 따름 6.1 (상수 3): 1.15(k+q+1)/(q+1)^{3/2} ≤ 3k q^{-3/2} 가 k≥2, 1≤q≤k 에서 서는지(비의 최댓값).
#   실행: python -I 결정_K0_경계검산.py (출력 _out.txt)
import os, sys, io
from math import sqrt, pi, log, floor
sys.stdout.reconfigure(encoding='utf-8')
out = io.StringIO()
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.write(s + '\n')

# ---------- (A) ----------
P('== (A) 정리 10.21 7단계의 네 경우를 y 의 함수로 ==')
def step7(y):
    a = floor((1.15*y)**(2/3)); q = a + 1
    c1 = 1.1284 + 2.82/q            # υ≤0.9
    c2 = 1.044 + 9.3/q              # υ∈(0.9,0.99]
    c3 = 0.34 + 85/q                # υ∈(0.99,0.9999]
    c4 = 0.19                        # υ>0.9999 (q≥109 조건: q/50-1/2 ≥ 0.77 q/50 ⇔ q ≥ 108.7)
    ok = max(c1, c2, c3, c4) < 1.15 and q >= 109
    return a, q, c1, c2, c3, ok
for y in [6666, 4000, 3130, 2000, 1500, 1289, 1288, 1200]:
    a, q, c1, c2, c3, ok = step7(y)
    P(f'  y={y}: 𝔞\'={a}, q≥{q}; 경우값 {c1:.5f} / {c2:.5f} / {c3:.5f} / 0.19 ; 모두<1.15 이고 q≥109: {ok}')
qmin = 2.82/(1.15-1.1284)
P(f'  첫째 경우가 1.15 아래가 되는 조건 q > 2.82/(1.15−1.1284) = {qmin:.1f}  →  (1.15y)^(2/3) ≥ 131 ⇔ y ≥ {131**1.5/1.15:.0f}')
P('  → y≥2000 (q≥175) 은 네 경우 모두 닫히고 여유는 첫째 경우 1.15−1.14444=0.0056 (닫힌 꼴의 값이지 수치 표본이 아님).')

# ---------- (B) ----------
P('\n== (B) 절단점 하계의 통합 — K2 닫힌 꼴로 k≥2001 ==')
def lb_uniform(k):
    R = (3*(k-1))//2; q = R-(k-1)
    sR_up = min(1.0, 1.15*(R+1)/(q+1)**1.5)
    ub = (1.15/0.35)*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
    d = 0
    while (k+d+1)**(2/3)/2 >= d+1: d += 1
    U = (2*pi)**-0.5*(1+d/k)**1.5*((4/3)*d**1.5+2*sqrt(d))/(k-1)
    return (k-1)/(R+1)*((1-U)-sR_up) - ub, d, U, sR_up, ub
def lb_env(k):
    d = (k**(2/3))/2
    for _ in range(100): d = ((k+d)**(2/3))/2
    sR_up = 1.15*(1.5*(k-1)+1)/((k-1)/2)**1.5
    ub = (1.15/0.35)*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
    U = (2*pi)**-0.5*(1+d/k)**1.5*((4/3)*d**1.5+2*sqrt(d))/(k-1)
    return 2*(k-1)/(3*(k-1)+2)*((1-U)-sR_up) - ub, d, U, sR_up, ub
ks = list(range(2001, 2301)) + list(range(2301, 20001, 97)) + list(range(20001, 10**6, 9973)) + [10**6, 10**7, 10**8]
vals = [(lb_uniform(k)[0], k) for k in ks]
envs = [(lb_env(k)[0], k) for k in ks]
mn = min(vals); me = min(envs)
dec_v = sum(1 for i in range(len(vals)-1) if vals[i+1][0] < vals[i][0])
dec_e = sum(1 for i in range(len(envs)-1) if envs[i+1][0] < envs[i][0])
for k in [2001, 2002, 2100, 2500, 3131, 4001, 6668, 10**4, 10**5, 10**8]:
    v = lb_uniform(k); e = lb_env(k)
    P(f'  k={k}: 격자 하계 {v[0]:.4f} (d={v[1]}, U≤{v[2]:.4f}, s_R≤{v[3]:.4f}, 𝗎♭={v[4]:.4f}); 포락선 {e[0]:.4f} (d*={e[1]:.2f})')
P(f'  격자 최솟값 {mn[0]:.4f} at k={mn[1]} (인접 감소 횟수 {dec_v}); 포락선 최솟값 {me[0]:.4f} at k={me[1]} (인접 감소 횟수 {dec_e})')
P(f'  → 통합 상수: 포락선이 k 에 단조 증가이면 k=2001 포락선 값 {lb_env(2001)[0]:.4f} 이 모든 k≥2001 의 하계; 1/6={1/6:.4f} 와 0.17 의 성립: {lb_env(2001)[0] >= 1/6}, {lb_env(2001)[0] >= 0.17}')
# k=3131 부터의 값(K2 의 0.24) 도 함께
P(f'  k≥3131 격자 최솟값 {min(v for v,k in vals if k>=3131):.4f}; 포락선 k=3131 {lb_env(3131)[0]:.4f} (K2: 0.2456)')

# ---------- (C) ----------
P('\n== (C) 6.45 셋째 단계: R(k)/2 ≤ 50.62/√(k−1), R 감소 ==')
def R(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k)) + 37.6/(5*sqrt(pi)*k)
prev = None; okall = True; dec_ok = True
for k in list(range(3130, 3200)) + list(range(3200, 10**6, 997)) + [10**6, 10**7, 10**8, 10**10]:
    r = R(k)
    if not (r/2 <= 50.62/sqrt(k-1)): okall = False
    if prev is not None and r > prev: dec_ok = False
    prev = r
for k in [3130, 3131, 6667, 6668, 9705, 10**4, 10**5]:
    P(f'  k={k}: R(k)={R(k):.5f}, R/2={R(k)/2:.5f}, 50.62/√(k−1)={50.62/sqrt(k-1):.5f}')
P(f'  R(k)/2 ≤ 50.62/√(k−1) 격자 전부: {okall};  R 감소(격자): {dec_ok}  → 𝗏(k) 의 식·값은 그대로, 셋째 단계의 인용만 바뀐다')

# ---------- (D) ----------
P('\n== (D) 따름 6.1 (상수 3): 1.15(k+q+1)/(q+1)^{3/2} ≤ 3k q^{-3/2} ==')
worst = 0; arg = None
for k in list(range(2, 3000)) + [10**4, 10**5, 10**6]:
    for q in [1, 2, 3, 5, 10, 50, k//2, k-1, k]:
        if q < 1 or q > k: continue
        ratio = 1.15*(k+q+1)/(q+1)**1.5 / (3*k*q**-1.5)
        if ratio > worst: worst = ratio; arg = (k, q)
P(f'  비의 최댓값 {worst:.5f} at (k,q)={arg} (<1 이면 성립); 극한 q=k: 1.15(2k+1)/(3k)→0.7667')
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '결정_K0_경계검산_out.txt'), 'w', encoding='utf-8').write(out.getvalue())
