# 심사 A4 — C4 이음 행 세 제안의 정수 검산
#  현행: t0(y) = min{t>=y+2 : y <= (t-1) - floor(3/4 (t-1)^{2/3})},  wid = t0-1-y <= 0.75(1.1y)^{2/3}+1 (y>=25000)
#  F4 : t~0(y) = 1 + min{m>=y+1 : y <= m - ceil(m^{2/3})},  폭 <= 1.03 y^{2/3} + 1  — 꼭대기 행 m 이 W(m)의 범위(r>=𝔪(m)+1) 안인가
#  F3 : r_a(m)=floor(.82 m^{2/3}), .73 < r_a^{3/2}/m < 1.2 (A 띠 범위) 인가;  F7: 13/16
#  𝔪(m) = max({170} ∪ {m'>=171 : m'^{3/2}+9m' <= m})  (5A 5.2.2)
import math
from fractions import Fraction as Fr

def ceil_pow23(m):  # ceil(m^{2/3}) = min j with j^3 >= m^2
    j = int(round(m**(2/3)))
    while j**3 < m*m: j += 1
    while (j-1)**3 >= m*m: j -= 1
    return j
def floor_a_pow23(m, a):  # floor(a m^{2/3}), a 유리수: max j with j^3 <= a^3 m^2
    a = Fr(a); j = int(float(a)*m**(2/3))+2
    while Fr(j)**3 > a**3*m*m: j -= 1
    while Fr(j+1)**3 <= a**3*m*m: j += 1
    return j
def frak_m(m):  # 𝔪(m)
    mp = int(m**(2/3))+2
    while not (mp**3 <= (m-9*mp)**2 and m-9*mp > 0): mp -= 1
    while (mp+1)**3 <= (m-9*(mp+1))**2 and m-9*(mp+1) > 0: mp += 1
    return mp if mp >= 171 else 170

# (a) 𝔪(m) < m^{2/3} 즉 𝔪(m)+1 <= ceil(m^{2/3}) — 모든 m>=20001 에서 (정수 논증: 𝔪^{3/2} < m). 전수 m=20001..300000
viol = 0
for m in range(20001, 300001):
    fm = frak_m(m)
    if not (fm**3 < m*m): viol += 1
print(f"(a) 𝔪(m)^3 < m^2 위반 수 (m=20001..300000): {viol};  예 m=20001: 𝔪={frak_m(20001)}, ceil(m^{2/3})={ceil_pow23(20001)}; m=50001: 𝔪={frak_m(50001)}, ceil={ceil_pow23(50001)}")

# (b) F4 폭: t~0(y)-1 = min{m>=y+1: m-ceil(m^{2/3}) >= y}.  m -> m-ceil(m^{2/3}) 은 비감소이므로 이분 탐색 가능.
def t0_F4_minus1(y):
    lo, hi = y+1, y+2*int(y**(2/3))+10
    assert hi - ceil_pow23(hi) >= y
    while lo < hi:
        mid = (lo+hi)//2
        if mid - ceil_pow23(mid) >= y: hi = mid
        else: lo = mid+1
    return lo
def t0_cur_minus1(y, a=Fr(3,4)):  # min{t-1>=y+1 : y <= (t-1)-floor(a (t-1)^{2/3})}
    lo, hi = y+1, y+2*int(y**(2/3))+10
    while lo < hi:
        mid = (lo+hi)//2
        if mid - floor_a_pow23(mid, a) >= y: hi = mid
        else: lo = mid+1
    return lo
# 단조성 확인(표본)
for m in range(25000, 26000):
    assert (m+1)-ceil_pow23(m+1) >= m-ceil_pow23(m)
worst = 0.0; worst_y = None; worst_ratio = 0
for y in list(range(25000, 60001)) + [10**5, 2*10**5, 5*10**5, 10**6, 10**7, 10**8]:
    wid = t0_F4_minus1(y) - 1 - y
    bound = 1.03*y**(2/3) + 1
    ratio = (wid-1)/y**(2/3)
    if ratio > worst_ratio: worst_ratio, worst_y = ratio, y
    if wid > bound: worst += 1
print(f"(b) F4 폭 wid <= 1.03 y^(2/3)+1 위반 수: {worst};  (wid-1)/y^(2/3) 최댓값 {worst_ratio:.5f} at y={worst_y};  y=25000: wid={t0_F4_minus1(25000)-1-25000}, 1.03y^(2/3)+1={1.03*25000**(2/3)+1:.1f}, 현행 wid={t0_cur_minus1(25000)-1-25000}, 현행 상계 0.75(1.1y)^(2/3)+1={0.75*(1.1*25000)**(2/3)+1:.1f}")
# 꼭대기 행 m>=t~0-1 이 W(m)의 범위인가: r=m-y >= 𝔪(m)+1 ?  (y=25000..60000 전수, m 은 t~0-1 자체 — 그 위는 단조성)
viol = 0
for y in range(25000, 60001):
    m = t0_F4_minus1(y)
    if not (m - y >= frak_m(m)+1): viol += 1
print(f"(b') F4: 첫 꼭대기 행 m=t~0-1 에서 m-y >= 𝔪(m)+1 위반 수 (y=25000..60000): {viol}")

# (c) F3 a=.82, F7 a=13/16 : r_a(m)=floor(a m^{2/3}) 이 A 띠 (r>=598, 0.73 <= r^{3/2}/m <= 1.2) 안이고 𝔪(m) 이하(T1 범위)인가, m>=20001
for name, a in (("F3 .82", Fr(82,100)), ("F7 13/16", Fr(13,16)), ("현행 3/4", Fr(3,4))):
    minr = None; minratio = None; maxratio = 0; viol_T1 = 0; viol_598 = 0
    for m in list(range(20001, 120001)) + [2*10**5, 10**6, 10**7, 10**8, 10**9]:
        r = floor_a_pow23(m, a)
        ratio_sq = Fr(r**3, m*m)   # (r^{3/2}/m)^2
        if minratio is None or ratio_sq < minratio: minratio, minr = ratio_sq, (m, r)
        if ratio_sq > maxratio: maxratio = ratio_sq
        if r > frak_m(m): viol_T1 += 1
        if r < 598: viol_598 += 1
    print(f"(c) {name}: min r^(3/2)/m = {math.sqrt(minratio):.5f} at (m,r)={minr}; max = {math.sqrt(maxratio):.5f}; A띠 하한 0.73 {'충족' if minratio >= Fr(73,100)**2 else '위반'}; r<598 위반 {viol_598}; r_a>𝔪(m) 위반 {viol_T1}")
    # EI 창 [16/25, 13/20] 과의 관계(현행만 뜻이 있음)
    if a == Fr(3,4):
        print(f"    현행 3/4 의 r0(m)^(3/2)/m 범위 [{math.sqrt(minratio):.5f},{math.sqrt(maxratio):.5f}] — EI 창 [0.64,0.65]")

# (d) 세 폭의 창 항 배율 (wid+1)^{3/2} 비: 현행 상계 0.75(1.1y)^{2/3} 대비
for name, c in (("F3 .82", 0.82*1.1**(2/3)), ("F7 13/16", 0.8125*1.1**(2/3)), ("F4 1.03", 1.03)):
    print(f"(d) {name}: wid 계수 {c:.4f}, 창 항 배율 (c/0.7993)^(3/2) = {(c/(0.75*1.1**(2/3)))**1.5:.3f}")

# (e) 최초 귀납 행 n=50001: 꼭대기 행 m∈[t~0(y)-1, 50000] 은 모두 20001 <= m <= 50000 (정리 5:old-5-2의 범위) — y>=25001
ok = all(t0_F4_minus1(y) >= 20001 for y in range(25001, 50000, 997))
print(f"(e) n=50001 의 꼭대기 행이 모두 [20001,50000] 안: {ok}  (t~0-1 >= y+1 >= 25002 이므로 자명)")
# W# 위치에서 t~0(y) <= n 인가: n-y > 10 y^{2/3}-1 >= ceil((n-1)^{2/3})+1 ?  (n=50001, y=25001)
n=50001; y=25001
print(f"(e') n={n}, y={y}: n-1-ceil((n-1)^(2/3)) = {n-1-ceil_pow23(n-1)} >= y={y}: {n-1-ceil_pow23(n-1) >= y};  W# 조건 n-y+1>10y^(2/3): {n-y+1 > 10*y**(2/3)}")
