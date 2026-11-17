# 검토전체25 R8: 8.2절 봉투 사슬의 배정밀도 대조 (증명이 아니라 본문 식의 대조)
#   s_{k+q}(k+1) >= exp(-J(q,k)) >= exp(-Bp-Cr) >= exp(-j_inf(xi_q))  (xi<=2.1)
#   s_{k+q}(k+1) >= pi0/(1-km) >= Esc_k(xi_q) >= Esc_6600(xi_q)        (xi>=2; 앞 둘은 xi>=0.2)
#   s^cf(xi_q) <= s_{k+q}(k+1),  Esc_k의 xi-감소, 여섯 조각 E,R2,D3의 k-감소
import numpy as np, sys
from math import lgamma, log, exp, pi, sqrt, floor
z12, zm12, z32 = -1.4603545088095868, -0.2078862249773545, 2.6123753486854883
c2 = 1 / sqrt(2 * pi); cPsi = -z12 + z32 / 12
def Psilow(x): return c2 * (2 * sqrt(x) - cPsi + 1 / (2 * sqrt(x)) - x ** -1.5 / 24) if x >= 1 else 0.0
def pieces(xi, k):
    q = xi * k ** (2 / 3); p = q - 1; n = k + q; kk = k + 1; eps = k ** (-1 / 3)
    E = 2 * c2 * exp(-1 / (12 * q)) * xi ** -0.5 * (1 + xi * eps)
    R1 = 1.5 * c2 * (2 * sqrt(p) - 1) * k ** (-2 / 3)
    H = 2 / 3 * p ** 1.5 + 0.5 * sqrt(p) + zm12 + 1 / (24 * sqrt(p))
    R2 = 15 / 8 * c2 * n ** 2.5 * H / (kk ** 3.5 * k ** (2 / 3))
    D1 = p / k ** (2 / 3); D2 = kk * sqrt(2 / pi) / sqrt(p) / k ** (2 / 3)
    D3 = 1.5 * kk * Psilow(p) / ((n + 1) * k ** (2 / 3))
    return E, R1, R2, D1, D2, D3
def Esc(xi, k):
    E, R1, R2, D1, D2, D3 = pieces(xi, k); return (E - R1 - R2) / (D1 + D2 - D3)
def jinf(xi): return 4 / 3 * c2 * xi ** 1.5
def BpCr(q, k):
    p = q - 1; n = k + q; kk = k + 1
    Lam = q * (2 * sqrt(p) + z12 + 1 / (2 * sqrt(p))) - (2 / 3 * p ** 1.5 + 0.5 * sqrt(p) + zm12)
    s_ = 4 / 15 * q ** 2.5 + 0.385 * q ** 1.5
    return c2 * Lam / kk, 1.5 * c2 * n ** 1.5 / kk ** 3.5 * s_
def scf(xi):
    v = []
    if xi <= 2.1: v.append(exp(-jinf(xi)))
    if xi >= 2: v.append(Esc(xi, 6600.0))
    return max(v)

def run(k):
    qm = int(floor(6 * k ** (2 / 3) + 1e-9)); y = k + 1; M = k + qm + 2
    idx = np.arange(1, M + 1, dtype=np.float64)
    lB = -idx + (idx - 1) * np.log(idx) - np.array([lgamma(i + 1) for i in range(1, M + 1)])
    s = np.ones(k + qm + 1); p0 = np.ones(k + qm + 1); km = np.zeros(k + qm + 1)
    for nn in range(y + 1, k + qm + 1):
        m = np.arange(y + 1, nn + 1)
        pin = np.exp(lB[m - 1] + lB[nn - m] - lB[nn])
        p0[nn] = 1 - pin.sum(); km[nn] = (pin * (y / m)).sum()
        s[nn] = p0[nn] + (pin * (y / m) * s[m - 1]).sum()
    Ren = idx * np.exp(lB)
    w = dict(jens=9e9, bpcr=9e9, jinf=9e9, esc0=9e9, esc1=9e9, esc2=9e9, scf=9e9)
    for q in range(2, qm + 1):
        xi = q / k ** (2 / 3); sv = s[k + q]
        r = np.arange(1, q)
        J = float(np.sum((q - r) * Ren[r - 1] * np.exp(lB[y + q - r - 1] - lB[y + q - 1]))) / y
        Bp, Cr = BpCr(q, k)
        w["jens"] = min(w["jens"], sv - exp(-J)); w["bpcr"] = min(w["bpcr"], Bp + Cr - J)
        if xi <= 2.1: w["jinf"] = min(w["jinf"], jinf(xi) - Bp - Cr)
        if xi >= 0.2:
            g = p0[k + q] / (1 - km[k + q])
            w["esc0"] = min(w["esc0"], sv - g); w["esc1"] = min(w["esc1"], g - Esc(xi, k))
            if xi >= 2: w["esc2"] = min(w["esc2"], Esc(xi, k) - Esc(xi, 6600.0))
        w["scf"] = min(w["scf"], sv - scf(xi))
    print(f"k={k} qmax={qm}: min[s-e^-J]={w['jens']:.3e}, min[Bp+Cr-J]={w['bpcr']:.3e}, min[j_inf-Bp-Cr](xi<=2.1)={w['jinf']:.3e}, min[s-pi0/(1-km)]={w['esc0']:.3e}, min[pi0/(1-km)-Esc_k]={w['esc1']:.3e}, min[Esc_k-Esc_6600](xi>=2)={w['esc2']:.3e}, min[s-s^cf]={w['scf']:.3e}")
for k in (6600, 6668, 30000):
    run(k)
# Esc_k의 xi-감소와 세 조각의 k-감소 (격자)
xs = np.linspace(0.2, 6.001, 2000)
for k in (6600.0, 1e5, 1e8, 1e12):
    v = np.array([Esc(x, k) for x in xs]); print(f"k={k:g}: Esc_k xi-감소 {bool(np.all(np.diff(v) < 0))}, 최솟값 {v.min():.6f} (본문 하계 0.020044)")
ks = np.geomspace(6600, 1e13, 400)
ok = True
for x in (0.2, 1.0, 2.0, 6.001):
    P = np.array([pieces(x, k) for k in ks])
    ok &= bool(np.all(np.diff(P[:, 0]) < 0) and np.all(np.diff(P[:, 2]) < 0) and np.all(np.diff(P[:, 5]) < 0))
print("E, R2, D3의 k-감소(격자):", ok)
for x in (2.0, 3.0, 6.001):
    v = np.array([Esc(x, k) for k in ks]); print(f"xi={x}: Esc_k k-증가 {bool(np.all(np.diff(v) > 0))}")
