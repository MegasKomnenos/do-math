# -*- coding: utf-8 -*-
"""외부 피드백 1116 (나) 검산 — band_LP/bandlib.py `_exp_series`의 나머지 상계 2|r|^{n+1}/(n+1)!.

확인하는 것:
 (1) 주석의 중간 부등식 「|r|≤0.7에서 e^{|r|}≤2」는 틀렸다(0.7 > log 2).
 (2) 그래도 반환 구간은 옳다: 꼬리 Σ_{j>n} a^j/j! ≤ a^{n+1}/(n+1)! · 1/(1-a/(n+2)), a≤0.7, n≥4에서 인자 ≤ 6/5.3 < 2.
     격자의 r에서 실제 꼬리(mpmath 50자리)와 코드의 R을 견준다. `_exp_series`의 구간이 참값을 담는지도 본다.
 (3) 실제 호출 범위: exp_enc는 |r| ≤ log2/2 + 반올림, expm1_enc는 part_ra.py의 가벼운·무거운 환경 인수.
     k=6668·9466에서 Col.rho_lo가 넘기는 인수의 최대 절댓값을 잰다(코드를 바꾸지 않고 함수를 감싸 기록).
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BL = os.path.join(ROOT, "원고_자료", "세션_재계산", "band_LP")
sys.path.insert(0, BL)
import numpy as np
from mpmath import mp, mpf, exp as mexp, factorial as mfact
import bandlib as B
mp.dps = 50

out = []
# (1)
out.append(f"log 2 = {float(mp.log(2)):.6f} < 0.7;  e^0.7 = {float(mexp(mpf('0.7'))):.6f} > 2  → 「e^{{|r|}}≤2」는 |r|∈(log2, 0.7]에서 거짓")
# (2) 꼬리 인자와 실제 꼬리
a = mpf('0.7')
for n in (4, 5, 6, 10):
    fac = 1 / (1 - a / (n + 2))
    out.append(f"n={n}: 1/(1-0.7/(n+2)) = {float(fac):.5f} (<2);  Lagrange e^0.7 = {float(mexp(a)):.5f} (>2)")
worst = 0.0; worst_lag = 0.0; bad = 0
rs = np.concatenate([np.linspace(-0.7, 0.7, 2001), np.array([0.7, -0.7, 0.69, -0.69, 0.35, -0.35])])
for r in rs:
    r = float(r); am = abs(r)
    n = B._taylor_terms(max(am, 1e-300), 4, 2.0 ** -75)
    rm = mpf(r)
    partial = sum(rm ** i / mfact(i) for i in range(0, n + 1))
    tail = abs(mexp(rm) - partial)
    bound_code = 2 * mpf(am) ** (n + 1) / mfact(n + 1)
    bound_geo = mpf(am) ** (n + 1) / mfact(n + 1) / (1 - mpf(am) / (n + 2))
    if am > 0:
        worst = max(worst, float(tail / bound_code))
        worst_lag = max(worst_lag, float(tail / (mpf(am) ** (n + 1) / mfact(n + 1))))
    assert tail <= bound_geo <= bound_code
    arr = np.array([r])
    lo_, hi_ = B._exp_series(arr, arr, 0)
    if not (mpf(float(lo_[0])) <= mexp(rm) <= mpf(float(hi_[0]))): bad += 1
    lo1, hi1 = B._exp_series(arr, arr, 1)
    if not (mpf(float(lo1[0])) <= mexp(rm) - 1 <= mpf(float(hi1[0]))): bad += 1
out.append(f"격자 {len(rs)}점: 실제 꼬리 / (2a^(n+1)/(n+1)!) 최대 {worst:.4f};  실제 꼬리 / (a^(n+1)/(n+1)!) 최대 {worst_lag:.4f};  구간이 참값을 놓친 수 {bad}")
# 구간 [rl, rh]가 폭을 가질 때도 확인 (rl≠rh)
bad2 = 0
for rl, rh in ((-0.7, -0.6), (-0.1, 0.1), (0.3, 0.7), (-0.7, 0.7)):
    lo_, hi_ = B._exp_series(np.array([rl]), np.array([rh]), 0)
    for r in np.linspace(rl, rh, 101):
        if not (mpf(float(lo_[0])) <= mexp(mpf(float(r))) <= mpf(float(hi_[0]))): bad2 += 1
out.append(f"폭 있는 구간 4개×101점: 놓친 수 {bad2}")
# (3) 실제 호출 범위
rec = {"exp_enc r": 0.0, "expm1_enc x": 0.0}
_orig_series = B._exp_series
def _wrap(rl, rh, first):
    am = float(np.maximum(np.abs(rl), np.abs(rh)).max()) if np.size(rl) else 0.0
    key = "exp_enc r" if first == 0 else "expm1_enc x"
    rec[key] = max(rec[key], am)
    return _orig_series(rl, rh, first)
B._exp_series = _wrap
import part_ra
part_ra.expm1_enc = B.expm1_enc  # part_ra는 `from bandlib import *`로 이름을 복사했으므로 같은 함수(내부에서 B._exp_series를 부름)
for k in (6668, 9466):
    M, cand, FM = B.nu1_cert(k)
    C = part_ra.Col(k)
    for a_, b_ in ((103, 103), (103, M - 1), (M - 1, M - 1)):
        C.rho_lo(a_, b_)
    out.append(f"k={k}, ν1 후보 M={M}: 지금까지 최대 |r| (exp_enc) = {rec['exp_enc r']:.6f}, 최대 |x| (expm1_enc) = {rec['expm1_enc x']:.6f}")
out.append(f"log2/2 = {math.log(2)/2:.6f};  e^(log2/2) = {math.sqrt(2):.4f} ≤ 2;  e^(최대 expm1 인수) = {math.exp(rec['expm1_enc x']):.4f} ≤ 2")
print("\n".join(out))
