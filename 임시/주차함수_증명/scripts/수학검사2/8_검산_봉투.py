# -*- coding: utf-8 -*-
"""수학 검사 2(태그 8): 8.2절 봉투 식 (8.13)(8.15)(8.16)(8.18)(8.19)을 글의 식대로 새로 구현해 기록 코드(window_lib.py,
fixes.py)와 점별로 맞추고, 저장된 표·시험 함수의 값(부록 D.window-mass-env)을 다시 읽는다.
 - Bp, Cr, E, R1, R2, D1, D2, D3 (글의 식) vs 기록 코드의 E3_parts, G_pieces
 - hat J (8.15) vs E_env_rigorous_fixed; s_G^env (8.19) vs E_envG_rigorous; 표값 z_i vs max(e^{-hat J}, s_G^env)
 - q_{6600,6600}(2), (2.1); 닫힌 꼴 s^cf와 z_i(표본); 표 좌표의 간격, xi_400, xi_12000
 - V, U의 경계(정리 closed-form-envelope (가), escape-y-monotone (라)(마))를 격자 표본으로 대조
 - 여섯 조각의 k-단조성(표본), (8.17) 우변 <= 정확한 탈출 하계(8.9)(k=6600, 표본 q)
 - Omega(0), Omega(0.5,...,6), max|Omega'|, sup s|Omega''|, L_T, TV(T')
실행: python -I scripts/수학검사2/8_검산_봉투.py
"""
import os, sys, math
import numpy as np
from fractions import Fraction as Fr
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, loggamma

REC = r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/r030ffaebcd164eb492cc4215ce1c2e56/evidence/peer/rerun"
WORK = os.path.join(REC, "work")
sys.path.insert(0, WORK)
os.chdir(REC)
import window_lib as WL                      # 기록 코드(읽기 전용)
from fixes import E_env_rigorous_fixed
from cert_lib_fixed import PchipW, make_W_pchip, QenvTable

mp.dps = 30
C2 = 1 / sqrt(2 * pi)
Z12, ZM12, Z32 = zeta(mpf(1) / 2), zeta(-mpf(1) / 2), zeta(mpf(3) / 2)
CPSI = -Z12 + Z32 / 12
fails = []


def rep(name, ok, detail=""):
    print(("OK   " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


# ---------- 글의 식 (mpmath) ----------
def Lam(q):
    p = q - 1
    return q * (2 * sqrt(p) + Z12 + 1 / (2 * sqrt(p))) - (mpf(2) / 3 * p ** mpf('1.5') + sqrt(p) / 2 + ZM12)


def Bp(q, k): return C2 * Lam(q) / (k + 1)


def Cr(q, k):
    n = k + q; kap = k + 1
    return mpf(3) / 2 * C2 * n ** mpf('1.5') / kap ** mpf('3.5') * (mpf(4) / 15 * q ** mpf('2.5') + mpf('0.385') * q ** mpf('1.5'))


def Psi_low(r):
    if r < 1: return mpf(0)
    return C2 * (2 * sqrt(r) - CPSI + 1 / (2 * sqrt(r)) - r ** mpf('-1.5') / 24)


def pieces(xi, k):
    k = mpf(k); xi = mpf(xi)
    q = xi * k ** (mpf(2) / 3); p = q - 1; n = k + q; kap = k + 1; eps = k ** (-mpf(1) / 3); k23 = k ** (mpf(2) / 3)
    E = 2 * C2 * exp(-1 / (12 * q)) / sqrt(xi) * (1 + xi * eps)
    R1 = mpf(3) / 2 * C2 * (2 * sqrt(p) - 1) / k23
    H = mpf(2) / 3 * p ** mpf('1.5') + sqrt(p) / 2 + ZM12 + 1 / (24 * sqrt(p))
    R2 = mpf(15) / 8 * C2 * n ** mpf('2.5') * H / (kap ** mpf('3.5') * k23)
    D1 = p / k23
    D2 = kap * sqrt(2 / pi) / sqrt(p) / k23
    D3 = mpf(3) / 2 * kap * Psi_low(p) / ((n + 1) * k23)
    return E, R1, R2, D1, D2, D3


def q_mixed(xi, k, kp):
    E, R1, R2, D1, D2, D3 = pieces(xi, k)
    if kp == 'inf':
        Ep, D1p, D3p = 2 * C2 / sqrt(mpf(xi)), mpf(xi), mpf(0)
    else:
        Ep, _, _, D1p, _, D3p = pieces(xi, kp)
    return (Ep - R1 - R2) / (D1p + D2 - D3p)


print("== 1. 글의 식 vs 기록 코드 (점별) ==")
ok = True; mx = 0.0
for xi in (0.01, 0.2, 0.5, 1.0, 2.0, 3.0, 6.0, 6.001):
    for k in (6600, 7000, 1e5, 1e8, 6.6e9):
        q = xi * k ** (2 / 3)
        if q < 2: continue
        bp_c, cr_c = WL.E3_parts(np.array([q]), np.array([float(k)]))
        mx = max(mx, abs(float(Bp(mpf(q), mpf(k))) / float(bp_c[0]) - 1), abs(float(Cr(mpf(q), mpf(k))) / float(cr_c[0]) - 1))
        if xi >= 0.2:
            P = WL.G_pieces(xi, np.array([float(k)]))
            mine = pieces(xi, k)
            for a, b in zip(mine, P):
                mx = max(mx, abs(float(a) / float(b[0]) - 1))
rep("(8.13) Bp,Cr = E3_parts;  (8.16) E,R1,R2,D1,D2,D3 = G_pieces", mx < 1e-12, f"max rel diff {mx:.2e}")

# hat J (8.15) vs E_env_rigorous_fixed, s_G (8.19) vs E_envG_rigorous
def hatJ(xi):
    xi = mpf(xi)
    Ks = max(mpf(6600), (2 / xi) ** mpf('1.5'))
    Kl = [Ks]
    while Kl[-1] < max(mpf(6600) * 1e6, Ks * 10): Kl.append(Kl[-1] * mpf('1.02'))
    vals = [Bp(xi * Kl[i + 1] ** (mpf(2) / 3), Kl[i + 1]) + Cr(xi * Kl[i] ** (mpf(2) / 3), Kl[i]) for i in range(len(Kl) - 1)]
    jinf = mpf(4) / 3 * C2 * xi ** mpf('1.5')
    last = max(jinf, Bp(xi * Kl[-1] ** (mpf(2) / 3), Kl[-1])) + Cr(xi * Kl[-1] ** (mpf(2) / 3), Kl[-1])
    return max(max(vals), last), len(Kl)


def sG(xi):
    if xi < 0.2: return mpf(0)
    Kl = [mpf(6600)]
    while Kl[-1] < mpf(6600) * 1e6: Kl.append(Kl[-1] * mpf('1.02'))
    vals = [q_mixed(xi, Kl[i], Kl[i + 1]) for i in range(len(Kl) - 1)]
    last = q_mixed(xi, Kl[-1], 'inf')
    return max(mpf(0), min(min(vals), last))


qx = np.load(os.path.join(WORK, "qenv_fix_x.npy")); qv = np.load(os.path.join(WORK, "qenv_fix_v.npy"))
ok = True; mx = 0.0; mxz = 0.0
for i in (0, 1, 10, 11, 12, 399, 400, 401, 1000, 3999, 4000, 4148, 4199, 4200, 6000, 11999, 12000):
    xi = qx[i + 1] if i + 1 <= 12000 else 6.0005
    xi_next = float(np.linspace(0, 6.0005, 12002)[i + 1])
    hj, L = hatJ(xi_next)
    mx = max(mx, abs(float(hj) / E_env_rigorous_fixed(xi_next, 6600) - 1))
    g = sG(xi_next)
    gc = WL.E_envG_rigorous(xi_next, 6600)
    if gc > 0: mx = max(mx, abs(float(g) / gc - 1))
    z = max(float(exp(-hj)), float(g))
    mxz = max(mxz, abs(z - qv[i]))
rep("(8.15) hat J = E_env_rigorous_fixed; (8.19) s_G = E_envG_rigorous (표본 xi)", mx < 1e-9, f"max rel diff {mx:.2e}")
rep("표값 z_i = max(e^{-hat J(xi_{i+1})}, s_G(xi_{i+1})) (표본 i, 30자리 재계산 vs binary64 저장값)", mxz < 1e-12, f"max |diff| {mxz:.2e}")
Ks0 = mpf(6600); L = 0
while Ks0 < mpf(6600) * 1e6: Ks0 *= mpf('1.02'); L += 1
print(f"   분할: K_{{L-1}} = {mp.nstr(Ks0, 10)} (>= 6.6e9), 점 수 L = {L+1}; K_s(xi)=6600 iff xi >= {mp.nstr(2/mpf(6600)**(mpf(2)/3), 8)}")

print("== 2. 이음새 값과 닫힌 꼴 ==")
jinf = lambda x: mpf(4) / 3 * C2 * mpf(x) ** mpf('1.5')
q2 = q_mixed(2, 6600, 6600); q21 = q_mixed('2.1', 6600, 6600)
print(f"   q_6600,6600(2) = {mp.nstr(q2, 12)}  (D: 0.2137204848... <= 0.213721);  e^-j(2) = {mp.nstr(exp(-jinf(2)), 12)} (>= 0.222127)")
print(f"   q_6600,6600(2.1) = {mp.nstr(q21, 12)} (>= 0.200904);  e^-j(2.1) = {mp.nstr(exp(-jinf('2.1')), 12)} (<= 0.198148)")
rep("이음새 부등식 (8.22)(라)", q2 <= mpf('0.213721') < mpf('0.222127') <= exp(-jinf(2)) and q21 >= mpf('0.200904') > mpf('0.198148') >= exp(-jinf('2.1')))


def s_cf(xi):
    xi = mpf(xi); a = exp(-jinf(xi)) if xi <= mpf('2.1') else mpf(-1); b = q_mixed(xi, 6600, 6600) if xi >= 2 else mpf(-1)
    return max(a, b)


ok = True; worst = mpf(1)
for i in (0, 1, 2, 100, 400, 1000, 2000, 3999, 4000, 4100, 4148, 4199, 4200, 5000, 8000, 11999, 12000):
    xi = Fr(float(np.linspace(0, 6.0005, 12002)[i + 1]))
    v = s_cf(mpf(xi.numerator) / xi.denominator) - mpf(Fr(float(qv[i])).numerator) / Fr(float(qv[i])).denominator
    ok &= v >= 0; worst = min(worst, v)
rep("z_i <= s^cf(xi_{i+1}) (표본 i)", ok, f"min margin {mp.nstr(worst, 6)}")
lin = np.linspace(0, 6.0005, 12002)
gaps = [Fr(float(lin[i + 1])) - Fr(float(lin[i])) for i in range(12001)]
print(f"   간격 [min,max] = [{float(min(gaps)):.17g}, {float(max(gaps)):.17g}]; xi_400 == 0.2: {lin[400] == 0.2}; xi_12000 == 6: {lin[12000] == 6.0}; xi_4200 > 2.1: {Fr(float(lin[4200])) > Fr(21, 10)}")
rep("좌표 간격 in [0.00049999999999972, 0.00050000000000062]", float(min(gaps)) >= 0.00049999999999972 and float(max(gaps)) <= 0.00050000000000062)
rep("저장값 엄격 감소, 최소 감소 >= 6.6438e-6 at i=11999", bool(np.all(np.diff(qv) < 0)) and float(Fr(float(qv[11999])) - Fr(float(qv[12000]))) >= 6.6438e-6 and int(np.argmin(-np.diff(qv))) == 11999, f"min decrease {float(np.min(-np.diff(qv))):.6e} at i={int(np.argmin(-np.diff(qv)))}; z_0={qv[0]!r}, z_12000={qv[12000]!r}")
LT = max(float(abs(Fr(float(qv[j])) - Fr(float(qv[j + 1]))) / (Fr(float(qx[j + 1])) - Fr(float(qx[j])))) for j in range(12000))
slopes = np.diff(qv) / np.diff(qx)
TV = float(np.sum(np.abs(np.diff(slopes))))
print(f"   L_T (max |slope| of hat T) = {LT:.6f} (D: <= 0.4894);  TV(T') on [0,6] = {TV:.6f} (D: 0.944)")
rep("L_T <= 0.4894 and TV(T') ~ 0.944", LT <= 0.4894 and abs(TV - 0.944) < 0.001)

print("== 3. 시험 함수 Omega ==")
import json
design = json.load(open(os.path.join(WORK, "design.json")))
xsK = np.load(os.path.join(WORK, "xKrig.npy")); wK = np.load(os.path.join(WORK, "wKrig.npy"))
W = make_W_pchip(xsK, wK, design["eta0"], design["eta1"], design["x1"])
print(f"   격자: {len(xsK)} 점, 마지막 {xsK[-1]:.6f} (D: 0<=i<=12927, 6.0002); 간격 {xsK[1]-xsK[0]:.9f} = 1e5^(-2/3)={1e5**(-2/3):.9f}")
vals = [round(float(W(x)), 3) for x in (0.0, 0.5, 1, 2, 3, 4, 6)]
print(f"   Omega(0,0.5,1,2,3,4,6) = {vals} (D: 0.96, 0.731,0.455,0.123,0.038,0.014,0.002)")
K2 = float(np.max(W.xs[1:len(W.M2) + 1] * W.M2))
print(f"   max|Omega'| = {float(W.M1.max()):.6f} (D 0.585), sup s|Omega''| <= {K2:.6f} (D 3.329)")
rep("Omega 표·도함수 상수", vals == [0.96, 0.731, 0.455, 0.123, 0.038, 0.014, 0.002] and abs(float(W.M1.max()) - 0.585) < 0.001 and K2 <= 3.329)
# 재귀 (D의 식) 재계산: r_i = K/(K+i) sum Bor(j)[T(xi_{i-j}) + r_{i-j}], w_i = r_i/Psi(i); 표 wK와 비교
LB, Psi, S0 = WL.exact_tables(len(wK) + 5)
Qf = lambda y: np.interp(y, qx, qv)
B = len(wK) - 1; Kg = design["K"]
R, w = WL.chain(Kg, 6.0, LB, Psi, Qf)
rep("D의 재귀 r_i, w_i (기록 chain) 재계산 = wKrig.npy (비트 단위)", len(w) >= len(wK) and bool(np.array_equal(w[:len(wK)], wK)), f"len {len(w)} vs {len(wK)}; max|diff| {float(np.max(np.abs(w[:len(wK)]-wK))):.2e}")
tab = (1 - np.minimum(1.0, design["eta0"] + design["eta1"] * np.where(xsK - 1 <= -0.1, 0.0, np.where(xsK - 1 >= 0.1, xsK - 1, (xsK - 1 + 0.1) ** 2 / 0.4)))) * wK
rep("안전 인자 g(xi)=min(1,0.04+0.12 e(xi-1)) 곱한 표가 이미 비증가(바뀌는 항 없음)", bool(np.all(np.diff(tab) <= 0)))
cap = float(np.sum(Psi[1:B + 1] * W(xsK[1:B + 1])) / Kg)
print(f"   포착 창 질량 sum Psi(i) Omega(xi_i)/K = {cap:.4f} (D: 0.729)")

print("== 4. V, U 경계(표본 격자)와 조각의 k-단조성 ==")
E0 = lambda xi: 2 * C2 / sqrt(mpf(xi))
Vmin, Umax = mpf(9), mpf(0); dUmin = mpf(9); dVmax = mpf(-9); okmono = True
xis = [mpf('0.2') + (mpf('6.001') - mpf('0.2')) * i / 40 for i in range(41)]
ks = [mpf(6600) * mpf('1.3') ** i for i in range(40)] + ['inf']
h = mpf('1e-6')
for xi in xis:
    for k in ks[:-1]:
        for kp in ks:
            if kp != 'inf' and kp < k: continue
            E, R1, R2, D1, D2, D3 = pieces(xi, k)
            if kp == 'inf': Ep, D1p, D3p = E0(xi), xi, mpf(0)
            else: Ep, _, _, D1p, _, D3p = pieces(xi, kp)
            V = (Ep - R1 - R2) / E0(xi); U = (D1p + D2 - D3p) / E0(xi)
            Vmin = min(Vmin, V); Umax = max(Umax, U)
            if kp == k or kp == 'inf':
                def VU(x):
                    E_, R1_, R2_, D1_, D2_, D3_ = pieces(x, k)
                    if kp == 'inf': Ep_, D1p_, D3p_ = E0(x), x, mpf(0)
                    else: Ep_, _, _, D1p_, _, D3p_ = pieces(x, kp)
                    return (Ep_ - R1_ - R2_) / E0(x), (D1p_ + D2_ - D3p_) / E0(x)
                V1, U1 = VU(xi - h); V2, U2 = VU(xi + h)
                dUmin = min(dUmin, (U2 - U1) / (2 * h)); dVmax = max(dVmax, k ** (mpf(1) / 3) * (V2 - V1) / (2 * h))
    # k-monotonicity of pieces at this xi
    prev = None
    for k in ks[:-1]:
        cur = pieces(xi, k)
        if prev is not None:
            okmono &= all(cur[j] < prev[j] for j in (0, 1, 2, 4, 5)) and cur[3] > prev[3]
        prev = cur
print(f"   min V = {mp.nstr(Vmin, 8)} (>= 0.38951), max U = {mp.nstr(Umax, 8)} (<= 19.4319), min dU/dxi = {mp.nstr(dUmin, 8)} (>= 0.7202), max k^(1/3) dV/dxi = {mp.nstr(dVmax, 8)} (<= -0.343)")
rep("closed-form (가), escape-y-monotone (라)(마) 표본 일치", Vmin >= mpf('0.38951') and Umax <= mpf('19.4319') and dUmin >= mpf('0.7202') and dVmax <= mpf('-0.343'))
rep("pieces-k-monotone: E,R1,R2,D2,D3 감소, D1 증가 (xi 격자, k 격자 1.3^i)", okmono)
# q_{k,k} increasing in k for xi>=2 (closed-form (다)) and Bp+Cr < j_inf for xi<=2.1 (나)
ok = True
for xi in [mpf(2), mpf('2.5'), mpf(3), mpf(4), mpf(6), mpf('6.001')]:
    prev = None
    for k in ks[:-1]:
        v = q_mixed(xi, k, k)
        if prev is not None: ok &= v > prev
        prev = v
rep("(다) q_{k,k}(xi) k에 증가 (xi>=2 표본)", ok)
ok = True
for xi in [mpf('0.001'), mpf('0.01'), mpf('0.1'), mpf('0.5'), mpf(1), mpf(2), mpf('2.1')]:
    for k in ks[:-1]:
        q = xi * k ** (mpf(2) / 3)
        if q < 2: continue
        ok &= Bp(q, k) + Cr(q, k) < jinf(xi)
rep("(나) Bp+Cr < j_inf (0<xi<=2.1 표본)", ok)

print("== 5. (8.17) 우변 <= 정확한 탈출 하계 (8.9) at k=6600 ==")
k = 6600; y = k + 1
def lBor(m): m = mpf(m); return (m - 1) * log(m) - m - loggamma(m + 1)
ok = True; worst = mpf(9)
for q in [71, 100, 200, 400, 800, 1200, 1600, 2000, 2111]:
    N = k + q
    pis = {m: exp(lBor(N + 1 - m) + lBor(m) - lBor(N + 1)) for m in range(y + 1, N + 1)}
    p0 = 1 - sum(pis.values())
    km = sum(pis[m] * mpf(y) / m for m in pis)
    exact_lb = p0 / (1 - km)
    xi = mpf(q) / mpf(k) ** (mpf(2) / 3)
    E, R1, R2, D1, D2, D3 = pieces(xi, k)
    six = (E - R1 - R2) / (D1 + D2 - D3)
    ok &= six <= exact_lb and D1 + D2 - D3 > 0
    worst = min(worst, exact_lb - six)
rep("(E-R1-R2)/(D1+D2-D3) <= pi0/(1-km) and denominator > 0 (k=6600, 표본 q)", ok, f"min gap {mp.nstr(worst, 6)}")
print("FAIL 수:", len(fails), fails)
