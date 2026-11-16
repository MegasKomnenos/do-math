# -*- coding: utf-8 -*-
"""심사 A10 — E6 검산: 10장 대각선 손실 DDL_2(k) <= 1/4 (k >= 6667) 주장 (F4 §6, F7 §1).

(1) 정리 10:old-8-22 의 증명 1단계가 주는 (d,q) 항의 상계
      3 (2pi)^{-1/2} q_d sqrt(k-1+d) / k^{3/2} * min{ q sqrt j / k^2 , c_d / (q sqrt j) },  c_d = 0.16696 q_d^2,
    에서 q_d <= 1.3751, sqrt(k-1+d) <= sqrt(2k) 로 F4 의 (21/(5 sqrt(pi) k)) * min{ q sqrt j/k^2, 1/(3 q sqrt j) } 가 나오는지.
(2) F4 의 합-적분 비교와 닫힌 꼴 14(1+log 3k)/(5 sqrt(pi k)) + 42/(5 sqrt(3 pi) k) 를 k=6667 에서 셈하고,
    유한합 2 * (21/(5 sqrt(pi) k)) * sum_j [ int_0^{k+1-j} f_j + 1/(sqrt3 k) ] 와 대조한다.
(3) 1단계 상계를 q_d 그대로 두고 (d,q) 전부 더한 값 B1(k) 와, 정의 그대로의 DDL_2(k) (배정밀도, 안쪽 합은 닫힌 꼴) 를 k=6667, 6668 에서 셈해
    명제 10:old-8-23 의 DDL^natural(6668) < 0.13237 과 비교한다.
(4) DDL 을 1/4 로 바꿨을 때 네 가족 검사의 여유 (부록 D.four-families 의 구간에서 선형으로 계산).
"""
import math
import numpy as np

SQ2PI_INV = 1 / math.sqrt(2 * math.pi)

print("== (1) 1단계 상수 -> F4 상수 ==")
qd_max = 1 + 0.7501 / 2
pref = 3 * SQ2PI_INV * qd_max * math.sqrt(2)  # * 1/k
print(f"  q_d <= {qd_max}; 3(2pi)^(-1/2) q_d sqrt(2k)/k^(3/2) = {pref:.5f}/k ;  21/(5 sqrt(pi)) = {21/(5*math.sqrt(math.pi)):.5f}/k ;  ok={pref <= 21/(5*math.sqrt(math.pi))}")
cd_max = 0.16696 * qd_max ** 2
print(f"  c_d <= 0.16696 * {qd_max}^2 = {cd_max:.5f} <= 1/3: {cd_max <= 1/3}")
k0 = 6667
print(f"  (1.00057^2 (1+2/k)^2 / 6 at k=6667 = {1.00057**2*(1+2/k0)**2/6:.6f} <= 0.16696)")

print("\n== (2) F4 닫힌 꼴과 유한 합-적분 비교 (k = 6667, 6668, 20000) ==")
def F4_closed(k):
    return 14 * (1 + math.log(3 * k)) / (5 * math.sqrt(math.pi * k)) + 42 / (5 * math.sqrt(3 * math.pi) * k)
def U_finite(k):
    # sum over j=1..k of [ int_0^{M} f_j + 1/(sqrt3 k) ], M = k+1-j, f_j(x)=min{x sqrt j/k^2, 1/(3 x sqrt j)}
    j = np.arange(1, k + 1, dtype=float)
    M = k + 1 - j
    x0 = k / np.sqrt(3 * j)
    small = M <= x0
    integ = np.where(small, M ** 2 * np.sqrt(j) / (2 * k * k),
                     1 / (6 * np.sqrt(j)) + np.log(np.maximum(M / x0, 1)) / (3 * np.sqrt(j)))
    s = np.sum(integ + 1 / (math.sqrt(3) * k))
    return 2 * 21 / (5 * math.sqrt(math.pi) * k) * s
def U_sum(k):
    # the actual double sum 2 * 21/(5 sqrt(pi) k) * sum_{d=2}^{k+1} sum_{q=1}^{d-1} min{ q sqrt(d-q)/k^2, 1/(3 q sqrt(d-q)) }
    tot = 0.0
    for d in range(2, k + 2):
        q = np.arange(1, d, dtype=float)
        jj = d - q
        tot += np.sum(np.minimum(q * np.sqrt(jj) / k ** 2, 1 / (3 * q * np.sqrt(jj))))
    return 2 * 21 / (5 * math.sqrt(math.pi) * k) * tot
for k in (6667, 6668, 20000):
    print(f"  k={k}: F4 닫힌 꼴 = {F4_closed(k):.6f} (<1/4: {F4_closed(k)<0.25});  유한 합-적분 상계 = {U_finite(k):.6f};  이중합 자체 = {U_sum(k):.6f}")

print("\n== (3) 1단계 상계 B1(k) 와 정의 그대로의 DDL_2(k) (배정밀도) ==")
def g(x):
    return (x - 1) * math.log1p(1 / x)
def g_arr(x):
    return (x - 1) * np.log1p(1 / x)
def log_bor(j):
    # Bor(j) = e^{-j} j^{j-1}/j!
    return -j + (j - 1) * np.log(j) - np.array([math.lgamma(v + 1) for v in j])
def B1(k):
    tot = 0.0
    for d in range(2, k + 2):
        q = np.arange(1, d, dtype=float)
        jj = d - q
        qd = 1 + 0.7501 * (d - 1) / (k - 1 + d)
        cd = 0.16696 * qd * qd
        pre = 3 * SQ2PI_INV * qd * math.sqrt(k - 1 + d) / k ** 1.5
        tot += pre * np.sum(np.minimum(q * np.sqrt(jj) / k ** 2, cd / (q * np.sqrt(jj))))
    return 2 * tot
def inner_sum(n, t):
    """sum_{1<=z<n} z (1 - z/n) t^z  with closed forms (t<1)."""
    Z = int(math.ceil(n)) - 1  # z = 1..Z where Z < n
    if Z < 1:
        return 0.0
    # S1 = sum_{z=1}^Z z t^z, S2 = sum z^2 t^z
    tZ = t ** Z
    S1 = t * (1 - (Z + 1) * tZ + Z * tZ * t) / (1 - t) ** 2
    S2 = t * (1 + t - (Z + 1) ** 2 * tZ + (2 * Z * Z + 2 * Z - 1) * tZ * t - Z * Z * tZ * t * t) / (1 - t) ** 3
    return S1 - S2 / n
def DDL2(k, dmax=None):
    y0 = k
    tot = 0.0
    dmax = k + 1 if dmax is None else dmax
    for d in range(2, dmax + 1):
        q = np.arange(1, d, dtype=float)
        jj = d - q
        inc_m = g_arr(y0 - 1 + d) - g_arr(y0 - 1 + q)
        inc_p = g_arr(y0 + d) - g_arr(y0 + q)
        kk = np.exp(inc_m) + np.exp(-inc_p) - 2
        # tilt_d(q) = Bor(y0+q)/Bor(y0+d) = exp(sum_{m=y0+q}^{y0+d-1} (1-g(m)))
        ms = np.arange(y0 + 1, y0 + d, dtype=float)  # m = y0+1 .. y0+d-1
        cum = np.concatenate(([0.0], np.cumsum(1 - g_arr(ms))))  # cum[i] = sum_{m=y0+1}^{y0+i} (1-g(m))
        # sum_{m=y0+q}^{y0+d-1} (1-g(m)) = cum[d-1] - cum[q-1]
        tilt = np.exp(cum[d - 1] - cum[q.astype(int) - 1])
        borj = np.exp(log_bor(jj))
        Acrit = (y0 - 1) * kk / (2 * (1 - np.exp(-inc_p)))
        nq = Acrit * (y0 + 1 + q) / q
        tq = (y0 - 1) / (y0 - 1 + q)
        inner = np.array([inner_sum(nq[i], tq[i]) for i in range(len(q))])
        H = np.sum(q * kk * tilt * borj * np.minimum(jj, inner))
        tot += H
    return 2 * tot
for k in (6667, 6668):
    b1 = B1(k)
    print(f"  k={k}: B1(k) [1단계 상계, q_d 그대로] = {b1:.6f}")
import time
t0 = time.time()
for k in (6668,):
    v = DDL2(k)
    print(f"  k={k}: DDL_2(k) 정의 그대로 (배정밀도) = {v:.6f}   (명제 10.20: DDL^natural(6668) < 0.13237; F4: 1/4)   [{time.time()-t0:.1f}s]")

print("\n== (4) DDL -> 1/4 로 바꾼 네 가족 여유 (부록 D.four-families 의 구간 아래 끝; DDL 은 계수 1 로 선형) ==")
fam = {
    '벌크': dict(ddl=0.1323659370, na=0.5893564528, ga_a=2.681725398, ga_b=2.025920231),
    '2':   dict(ddl=0.1223300121, na=0.5045530811, ga_a=1.363140247, ga_b=0.9970739439),
    '1b':  dict(ddl=0.1140391119, na=0.4673235422, ga_a=0.7267559405, ga_b=0.6343807960, ga_a2=3.164348629, ga_b2=0.3372578939),
    '1a':  dict(ddl=0.1132841417, na=0.2047101516, ga_a=0.2354722037, ga_b=2.877022281, ga_a2=3.232078853, ga_b2=0.3947510707),
}
F4_claim = {'벌크': 0.4717223898, '2': 0.3768830931, '1b': 0.3313626540, '1a': 0.06799429334}
for name, v in fam.items():
    sh = 0.25 - v['ddl']
    s = f"  {name}: (나) 여유 {v['na']:.6f} -> {v['na']-sh:.6f} (F4 주장 {F4_claim[name]:.6f}); (가)(a) {v['ga_a']:.4f} -> {v['ga_a']-sh:.4f}; (가)(b) {v['ga_b']:.4f} -> {v['ga_b']-sh:.4f}"
    if 'ga_a2' in v:
        s += f"; m0>N (a) {v['ga_a2']:.4f} -> {v['ga_a2']-sh:.4f}, (b) {v['ga_b2']:.4f} -> {v['ga_b2']-sh:.4f}"
    print(s)
print("  벌크 합 abar+bbar+DDL+dbar+ebar: 3.410643548 -> %.6f (<=4)" % (3.410643548 + 0.25 - 0.1323659370))
