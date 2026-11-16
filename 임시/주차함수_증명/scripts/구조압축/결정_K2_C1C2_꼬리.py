# -*- coding: utf-8 -*-
# 결정 K2 — C1·C2: 꼬리 정리 하나로. (a) eb=0 분기 Pc(k;0)>0 (2<=r<=170, k>=19831) 정확 유리수(√는 유리 상계);
# (b) eb=(6/7)√r 분기 Pc(𝔨_r) > √r/70+7/20 (64<=r<=3000) 정확 유리수(√r 는 유리 상계, 3π/2 는 유리 상계);
# (c) 𝔪(n)의 두 정의(현행 / {m>=171} 만)가 n>=20001에서 같은 값; (d) 정확 항등식 E[J^2]+(3+r^2/k)μ+2=2r 과 E[J(J-1)]<=1.5μ^2 표본.
import sys
from fractions import Fraction as F
from math import isqrt
sys.stdout.reconfigure(encoding='utf-8')

def sqrt_upper(x):  # 유리수 x>=0 의 √ 유리 상계 (분모 10^12)
    N = 10**12
    num = x.numerator * N * N
    den = x.denominator
    s = isqrt(num // den) + 1
    return F(s, N)
def sqrt_lower(x):
    N = 10**12
    num = x.numerator * N * N
    den = x.denominator
    s = isqrt(num // den)
    return F(s, N)

PI_UP = F(3141592653589794, 10**15)  # π 상계
def Pc(k, r, eb_lower):
    # Pc(k)=k(1/(2r)-1/(3r^2)) - 5/2 + 2 eb (1-1/k) - k/(k-1) (1+√(3π(r-1)/2))  ; 하계: eb 하계, √ 상계
    k = F(k); r = F(r)
    root = sqrt_upper(F(3) * PI_UP * (r - 1) / 2)
    return k * (1/(2*r) - 1/(3*r*r)) - F(5, 2) + 2*eb_lower*(1 - 1/k) - (k/(k-1))*(1 + root)

print("(a) eb=0: 2<=r<=170, k=19831 (n>=20001, r<=170 => k>=19831)")
mn = None
for r in range(2, 171):
    v = Pc(19831, r, F(0))
    if mn is None or v < mn[0]:
        mn = (v, r)
    assert v > 0
print(f"   모두 양; 최솟값 Pc={float(mn[0]):.4f} at r={mn[1]};  (참고) k=49831, r=170: {float(Pc(49831,170,F(0))):.3f}")
# k 에 증가 확인 (r=170): k=19831..19831+5000 표본
vals = [Pc(k, 170, F(0)) for k in (19831, 20000, 25000, 30000, 49831, 10**6)]
print("   k 증가 표본(r=170):", [round(float(v),3) for v in vals], "증가:", all(vals[i] < vals[i+1] for i in range(len(vals)-1)))

print("(b) eb=(6/7)√r (하계), k=𝔨_r=ceil(r^{3/2}+8r): 64<=r<=3000, Pc > √r/70+7/20 ?")
worst = None
for r in range(64, 3001):
    rr = F(r)
    # 𝔨_r = ceil(r^{3/2}+8r)
    s32 = isqrt(r**3)
    kr = (s32 if s32*s32 == r**3 else s32 + 1) + 8*r
    eb_lo = F(6, 7) * sqrt_lower(rr)
    v = Pc(kr, r, eb_lo)
    target = sqrt_upper(rr)/70 + F(7, 20)
    margin = v - target
    if worst is None or margin < worst[0]:
        worst = (margin, r, v, target)
    assert margin > 0, (r, float(margin))
print(f"   모두 통과; 최소 여유 {float(worst[0]):.4f} at r={worst[1]} (Pc={float(worst[2]):.4f}, 목표={float(worst[3]):.4f})")

print("(c) 𝔪(n): 현행 max({170}∪{m>=171: m^{3/2}+9m<=n}) 대 {m>=171:...}의 최댓값 — n=20001..60000 표본 & 경계")
def frak_m_cur(n):
    best = 170
    m = 171
    while m**3 <= (n - 9*m)**2 and 9*m <= n:
        best = m; m += 1
    return best
def frak_m_new(n):
    best = None
    m = 171
    while 9*m <= n and m**3 <= (n - 9*m)**2:
        best = m; m += 1
    return best
diff = 0
for n in list(range(20001, 20101)) + list(range(20101, 60001, 997)) + [50001, 10**5, 10**6]:
    a, b = frak_m_cur(n), frak_m_new(n)
    if a != b: diff += 1
print(f"   불일치 수: {diff}; 𝔪(20001)={frak_m_cur(20001)}, 𝔪(50001)={frak_m_cur(50001)}, 𝔪(10^6)={frak_m_cur(10**6)}")

print("(d) 기울인 생일 법칙 정확 항등식·모멘트 상계 표본 (정확 유리수)")
def bd(r, k):
    rho = F(k, k + r)
    a = []
    prod = F(1)
    for j in range(0, r):
        # a_j = rho^j (r-1)_j / r^j ; weight (j+1) a_j
        if j > 0:
            prod *= rho * F(r - j, r)   # (r-1)_j/(r^j) 누적: 인자 (r-1-(j-1))/r = (r-j)/r
        a.append((j + 1) * prod)
    Z = sum(a)
    mu = sum(F(j) * a[j] for j in range(r)) / Z
    m2 = sum(F(j*j) * a[j] for j in range(r)) / Z
    return mu, m2
for (r, k) in [(5, 20), (10, 100), (64, 1024), (170, 2217), (200, 4429), (300, 7600)]:
    mu, m2 = bd(r, k)
    lhs = m2 + (3 + F(r*r, k)) * mu + 2
    ok_id = (lhs == 2*r)
    ok_mom = (m2 - mu <= F(3, 2) * mu * mu)
    print(f"   r={r} k={k}: 항등식 {ok_id}; E[J(J-1)]/μ^2={float((m2-mu)/(mu*mu)):.4f} <=1.5 {ok_mom}; μ/√r={float(mu)/r**0.5:.4f}")

print("(e) 닫힌 꼴 하계 μ_lb(r) := [-(4+a)+√((4+a)^2+12(r-1))]/3, a := r^2/𝔨_r (E[J(J-1)]<=1.5μ^2 와 항등식에서; 정확 유리수, √ 는 하계), r=64..20000")
def mu_lb(r):
    s32 = isqrt(r**3); kr = (s32 if s32*s32 == r**3 else s32+1) + 8*r
    a = F(r*r, kr)
    root = sqrt_lower((4+a)**2 + 12*(r-1))
    return (-(4+a) + root)/3, kr, a
worst67 = None; worst84 = None; worstPc = None
for r in range(64, 20001):
    mu, kr, a = mu_lb(r)
    sr_up = sqrt_upper(F(r)); sr_lo = sqrt_lower(F(r))
    m67 = mu - F(6,7)*sr_up; m84 = mu - F(84,100)*sr_up
    if worst67 is None or m67 < worst67[0]: worst67 = (m67, r)
    if worst84 is None or m84 < worst84[0]: worst84 = (m84, r)
    pc = Pc(kr, r, mu)
    if worstPc is None or pc < worstPc[0]: worstPc = (pc, r)
print(f"   μ_lb - (6/7)√r 최소 {float(worst67[0]):.4f} at r={worst67[1]};  μ_lb - 0.84√r 최소 {float(worst84[0]):.4f} at r={worst84[1]};  Pc(𝔨_r; eb=μ_lb) 최소 {float(worstPc[0]):.4f} at r={worstPc[1]}")
# 해석적 마무리(수리 지시용): s=√r>=8 에서 Pc(𝔨_r; eb=(6/7)√r) >= 0.0435 s + 1/2 - [1/(3s)+8/(3s^2)+12/(7s^2)+(1+2.1709 s)/(s^3+8s^2-1)]
from mpmath import mp as _mp, mpf as _mpf, sqrt as _sqrt, pi as _pi
_mp.dps = 30
coef = _mpf(1)/2 + _mpf(12)/7 - _sqrt(3*_pi/2)
def tail_lb(s):
    s = _mpf(s)
    return coef*s + _mpf(1)/2 - (1/(3*s) + 8/(3*s*s) + 12/(7*s*s) + (1+_sqrt(3*_pi/2)*s)/(s**3+8*s*s-1))
print(f"   계수 1/2+12/7-√(3π/2) = {float(coef):.5f};  해석 하계 at r=64 (s=8): {float(tail_lb(8)):.4f}; s=10: {float(tail_lb(10)):.4f}; s=100: {float(tail_lb(100)):.3f} (s 에 증가)")
# 큰 r 의 μ_lb >= (6/7)√r: 28(s^2-1) - 6s[(4+a)+√((4+a)^2+12(s^2-1))] > 0 with a <= s^2/(s+8), s>=8  (표본 s=8..10^4)
def gap(s):
    s = _mpf(s); a = s*s/(s+8)
    return 28*(s*s-1) - 6*s*((4+a) + _sqrt((4+a)**2 + 12*(s*s-1)))
print(f"   28(s^2-1)-6s[(4+a)+√(...)] (a=s^2/(s+8)): s=8 {float(gap(8)):.2f}, s=9 {float(gap(9)):.2f}, s=20 {float(gap(20)):.1f}, s=100 {float(gap(100)):.0f}, s=10^4 {float(gap(10**4)):.0f}  (모두 양; s^2 계수 28-6(1+√13)=0.364)")
