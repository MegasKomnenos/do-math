# -*- coding: utf-8 -*-
"""심사 X4 — C1(T1의 계산 없는 증명)·C2(Newton 인증 제거)의 검산.

(1) 기울인 생일 법칙 Pr(J=j) ∝ (j+1) a_j, a_j = rho^j (r-1)_j / r^j 가 원고의 bd_{r-1,rho}(j)와 같은지.
(2) 정확 항등식 E[J^2] + (3 + r^2/k) mu + 2 = 2r (유리수 정확 산술).
(3) E[J(J-1)] <= (3/2) mu^2 (수치).
(4) tm_{r-1}(k/(k+r)) > (6/7) sqrt r  (r>=64, k >= r^{3/2}+8r) — 정확 산술로 k = ceil(r^{3/2}+8r)에서 비교, 그리고 F4의 모순 논법의 산술.
(5) Pc(k) > sqrt r/70 + 7/20 (eb = 6 sqrt r/7, k >= r^{3/2}+8r) — 해석적 하계와 격자 검산.
(6) C2: 2<=r<=170, k>=19831(및 49831)에서 eb=0인 Pc(k) > 0 — 유리수 정확 산술(sqrt(3 pi (r-1)/2)는 유리 상계로).
"""
from fractions import Fraction as Fr
from math import isqrt, sqrt, pi, ceil
import mpmath as mp

mp.mp.dps = 40
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

# ---------- (1)(2)(3)(4) ----------
def birthday_weights(r, rho):
    # 원고: bd_{d,rho}(j) ∝ rho^j [rho^j]hb_d, [rho^j]hb_d = (j+1)(d+1)^{d-j-1}/(d-j)!, d=r-1
    d = r - 1
    from math import factorial
    w_manu = []
    w_f4 = []
    for j in range(0, d + 1):
        w_manu.append(rho**j * Fr((j + 1) * (d + 1)**(d - j - 1) if d - j - 1 >= 0 else Fr(j + 1, d + 1), factorial(d - j)))
        ff = 1
        for i in range(j):
            ff *= (r - 1 - i)
        w_f4.append((j + 1) * rho**j * Fr(ff, r**j))
    return w_manu, w_f4

def moments(w):
    Z = sum(w)
    mu = sum(j * x for j, x in enumerate(w)) / Z
    m2 = sum(j * j * x for j, x in enumerate(w)) / Z
    return mu, m2

P("== (1)(2)(3)(4) r, k=ceil(r^1.5+8r): 분포 일치 / 항등식 / E[J(J-1)]<=1.5mu^2 / mu vs 6sqrt(r)/7")
for r in [64, 65, 80, 100, 171, 300]:
    k = ceil(r**1.5 + 8 * r)
    # 정확히: k = ceil(sqrt(r^3) + 8r)
    k = isqrt(r**3) + (1 if isqrt(r**3)**2 < r**3 else 0) + 8 * r
    rho = Fr(k, k + r)
    wm, wf = birthday_weights(r, rho)
    Zm, Zf = sum(wm), sum(wf)
    same = all(wm[j] / Zm == wf[j] / Zf for j in range(len(wm)))
    mu, m2 = moments(wf)
    ident = m2 + (3 + Fr(r * r, k)) * mu + 2 - 2 * r
    ej2 = m2 - mu
    ok3 = ej2 <= Fr(3, 2) * mu * mu
    # mu > 6 sqrt r /7  <=> 49 mu^2 > 36 r
    ok4 = 49 * mu * mu > 36 * r
    P(f"r={r} k={k}: 분포일치={same} 항등식잔차={ident} E[J(J-1)]/mu^2={float(ej2/(mu*mu)):.5f} mu/sqrt r={float(mu)/sqrt(r):.5f} (6/7=0.857143) ok3={ok3} ok4={ok4}")

# (4) 모순 논법의 산술: r>=64, k>=r^{3/2}+8r => 4 + r^2/k <= sqrt r ; 96/49 r < 2(r-1) <=> r>49
P("== (4) 4 + r^2/k <= sqrt r 확인(정확): r=64..2000, k=ceil(r^1.5)+8r")
bad = []
for r in range(64, 2001):
    k = isqrt(r**3) + (1 if isqrt(r**3)**2 < r**3 else 0) + 8 * r
    # (4 + r^2/k)^2 <= r ?
    lhs = (4 + Fr(r * r, k))**2
    if lhs > r:
        bad.append(r)
P("위반 r:", bad[:10], "개수", len(bad))

# ---------- (5) Pc(k) > sqrt r/70 + 7/20 ----------
def Pc(k, r, eb):
    k = mp.mpf(k); r = mp.mpf(r)
    return k * (1 / (2 * r) - 1 / (3 * r * r)) - mp.mpf(5) / 2 + 2 * eb * (1 - 1 / k) - k / (k - 1) * (1 + mp.sqrt(3 * mp.pi * (r - 1) / 2))

P("== (5) Pc(k_r) with eb=6sqrt r/7, k_r=ceil(r^1.5+8r): r=64..3000 격자, 목표 sqrt r/70+7/20")
worst = None
for r in range(64, 3001):
    k = isqrt(r**3) + (1 if isqrt(r**3)**2 < r**3 else 0) + 8 * r
    eb = 6 * mp.sqrt(r) / 7
    v = Pc(k, r, eb)
    tgt = mp.sqrt(r) / 70 + mp.mpf(7) / 20
    gap = v - tgt
    if worst is None or gap < worst[0]:
        worst = (gap, r, v, tgt)
P(f"최소 여유 Pc - (sqrt r/70+7/20) = {mp.nstr(worst[0],8)} at r={worst[1]} (Pc={mp.nstr(worst[2],8)}, 목표={mp.nstr(worst[3],8)})")
# 해석적 하계: Pc >= sqrt r (1/2 + 12/7 - sqrt(3pi/2)) + 3/2 - err(r), err 감소 → r=64에서 평가
r = mp.mpf(64); s = mp.sqrt(r)
err64 = 1 / (3 * s) + 8 / (3 * r) + 12 / (7 * r) + (1 + mp.sqrt(3 * mp.pi / 2) * s) / (r**1.5 + 8 * r - 1)
coef = mp.mpf(1) / 2 + mp.mpf(12) / 7 - mp.sqrt(3 * mp.pi / 2)
P(f"해석적: 계수 1/2+12/7-sqrt(3pi/2) = {mp.nstr(coef,8)} (>1/70=0.0142857 ✓); r=64 오차항 합 = {mp.nstr(err64,6)}; 하계 at r=64: {mp.nstr(coef*s+1.5-err64,6)} vs 목표 {mp.nstr(s/70+0.35,6)}")

# ---------- (6) C2: eb=0, 2<=r<=170, k=19831 및 49831 ----------
def Pc_lower_exact(k, r):
    # sqrt(3 pi (r-1)/2) 의 유리 상계: 사용 pi < 3.14159266, sqrt 상계는 isqrt 기반
    k = Fr(k); rr = Fr(r)
    x = Fr(3) * Fr(314159266, 100000000) * (rr - 1) / 2   # > 3 pi (r-1)/2
    # 유리 상계 of sqrt(x): q = ceil(sqrt(x)*10^6)/10^6
    num, den = x.numerator, x.denominator
    scale = 10**12
    q = isqrt(num * scale * scale // den) + 1
    sq = Fr(q, scale)
    return k * (1 / (2 * rr) - 1 / (3 * rr * rr)) - Fr(5, 2) - k / (k - 1) * (1 + sq)

P("== (6) C2: Pc(k; eb=0) 하계(정확 유리수) — 최소값 over 2<=r<=170")
for k in [19831, 49831]:
    vals = [(Pc_lower_exact(k, r), r) for r in range(2, 171)]
    mn = min(vals)
    P(f"k={k}: min Pc = {float(mn[0]):.4f} at r={mn[1]}; 57/2=28.5 보다 큰가: {mn[0] > Fr(57,2)}; r=170 값 {float(Pc_lower_exact(k,170)):.4f}; r=2 값 {float(Pc_lower_exact(k,2)):.4f}")
# F4의 식 49831/510 - 5/2 - 66 재계산
P("F4 식: 49831/510 - 5/2 - 66 =", float(Fr(49831, 510) - Fr(5, 2) - 66), "> 28.5 ?", Fr(49831, 510) - Fr(5, 2) - 66 > Fr(57, 2))
P("참고: 170*(1/(2r)-1/(3r^2)) 역수 =", float(1 / (Fr(1, 340) - Fr(1, 3 * 170 * 170))), " (F4의 510은 더 거친 분모)")

# n>=20001, r<=170 이면 k>=19831: 모든 r에서 k = 20001 - r 로도 확인
vals = [(Pc_lower_exact(20001 - r, r), r) for r in range(2, 171)]
mn = min(vals)
P(f"k=20001-r: min Pc = {float(mn[0]):.4f} at r={mn[1]}")

open(__file__.replace('.py', '_out.txt'), 'w', encoding='utf-8').write("\n".join(out) + "\n")
