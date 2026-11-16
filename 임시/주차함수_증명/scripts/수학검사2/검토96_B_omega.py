# -*- coding: utf-8 -*-
"""검토 B(코드-Ω): ivbox_lib.py의 Ω 블록 검산.
(1) Hermite 기저 전개 → a0..a3 공식 검산(유리수), (2) 계수 괄호 폭, (3) 비증가 검사의 분기 통계,
(4) Om_lo(y) 대 ia.OmegaIA(y) 구간(임의 점·절점·절점 근방), (5) Om_lo 대 기록 binary64 PCHIP, (6) iv.dps 복구.
실행: python -I scripts/수학검사2/검토96_B_omega.py   (ivbox_lib import가 Ω 블록을 만든다; 약 2–3초)"""
import os, sys, time
from fractions import Fraction as Fr
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BP = os.path.join(ROOT, "원고_자료", "세션_재계산", "bprime_boxes")
sys.path.insert(0, BP)
import numpy as np
t0 = time.time()
import ivbox_lib as L
from mpmath import iv, mp
print("import %.1fs; iv.dps=%d mp.dps=%d (34여야 함)" % (time.time() - t0, iv.dps, mp.dps))
ia = L._ia
OM = L.OM

# (1) Hermite 기저: p(t) = y0 H00 + hd0 H10 + y1 H01 + hd1 H11
#  H00 = 2t^3-3t^2+1, H10 = t^3-2t^2+t, H01 = -2t^3+3t^2, H11 = t^3-t^2  (기록 PchipW.__call__ 와 같은 기저)
#  계수를 유리수 임의값으로 비교
import random
random.seed(1)
ok = True
for _ in range(50):
    y0, y1, m0, m1 = (Fr(random.randint(-999, 999), random.randint(1, 97)) for _ in range(4))
    # 기저 전개의 t^0..t^3 계수
    c = [y0, m0, -3 * y0 - 2 * m0 + 3 * y1 - m1, 2 * y0 + m0 - 2 * y1 + m1]
    # ivbox_lib 공식
    dy = y1 - y0
    a = [y0, m0, 3 * dy - 2 * m0 - m1, -2 * dy + m0 + m1]
    ok &= (c == a)
    # ia._piece 꼴: y0 + dy(3t^2-2t^3) + hd0 t(1-t)^2 - hd1 t^2(1-t) 도 같은지 (t=1/3,1/2,2/3,1 에서)
    for t in (Fr(1, 3), Fr(1, 2), Fr(2, 3), Fr(1), Fr(0)):
        p_coef = a[0] + a[1] * t + a[2] * t ** 2 + a[3] * t ** 3
        p_ia = y0 + dy * (3 * t ** 2 - 2 * t ** 3) + m0 * t * (1 - t) ** 2 - m1 * t ** 2 * (1 - t)
        p_rec = y0 * (2 * t ** 3 - 3 * t ** 2 + 1) + m0 * (t ** 3 - 2 * t ** 2 + t) + y1 * (-2 * t ** 3 + 3 * t ** 2) + m1 * (t ** 3 - t ** 2)
        ok &= (p_coef == p_ia == p_rec)
print("(1) a0..a3 공식 = Hermite 기저 전개 = ia._piece 꼴 = 기록 PchipW 꼴:", ok)

# (2) 계수 괄호 폭
w = L.OM_hi - L.OM_lo
print("(2) 계수 괄호 폭 max 행별 a0..a3:", ["%.3e" % x for x in w.max(axis=1)], " 전체 max %.3e" % w.max())
print("    |a| 크기 max 행별:", ["%.3e" % x for x in np.abs(L.OM_hi).max(axis=1)])
print("    조각 수 n-1 =", L.OM_lo.shape[1], " n =", OM.n, " h in [%r, %r]" % (L.OM_h_lo, L.OM_h_hi), " h 폭 %.3e" % (L.OM_h_hi - L.OM_h_lo))

# (3) 비증가 검사 분기 통계 (ivbox_lib._omega_coeffs 재현)
IA = ia.IA
lo, hi = L.OM_lo, L.OM_hi
A1 = IA(lo[1], hi[1]); A2 = IA(lo[2], hi[2]); A3 = IA(lo[3], hi[3])
neg = A3.hi < 0; pos = A3.lo > 0; amb = (A3.lo <= 0) & (A3.hi >= 0)
A3s = IA(np.where(neg, A3.lo, -1.0), np.where(neg, A3.hi, -1.0))
ts = (-A2) / (3.0 * A3s)
inside = neg & (ts.hi > 0) & (ts.lo < 1)
pv = A1 - (A2 * A2) / (3.0 * A3s)
end1 = (A1 + 2.0 * A2 + 3.0 * A3).hi
print("(3) a3<0(오목 p') %d, a3>0 %d, 0 걸침 %d; 꼭짓점 안쪽 %d; max p'(0).hi %.3e, max p'(1).hi %.3e, max 꼭짓점값.hi(안쪽) %s" % (
    neg.sum(), pos.sum(), amb.sum(), inside.sum(), A1.hi.max(), end1.max(), ("%.3e" % pv.hi[inside].max()) if inside.any() else "-"))
if amb.any():
    cons = A1.hi + 2.0 * np.maximum(A2.hi, 0.0) + 3.0 * np.maximum(A3.hi, 0.0)
    print("    0 걸침 조각의 보수 상계 max %.3e" % cons[amb].max())
# 참고: 꼭짓점 공식 검산 — p'(t*) = a1 - a2^2/(3 a3), t* = -a2/(3 a3)
a1, a2, a3 = Fr(3, 7), Fr(-5, 11), Fr(-2, 13)
tstar = -a2 / (3 * a3)
print("    꼭짓점 공식: p'(t*) 직접 = %s, a1 - a2^2/(3a3) = %s, 같음 %s" % (a1 + 2 * a2 * tstar + 3 * a3 * tstar ** 2, a1 - a2 ** 2 / (3 * a3), a1 + 2 * a2 * tstar + 3 * a3 * tstar ** 2 == a1 - a2 ** 2 / (3 * a3)))
# 수치 점검: 중앙 계수로 p'(t)를 1001점에서 평가 → 최대값
tt = np.linspace(0, 1, 1001)
mid = 0.5 * (lo + hi)
pmax = (mid[1][:, None] + 2 * mid[2][:, None] * tt + 3 * mid[3][:, None] * tt ** 2).max()
print("    중앙 계수 p'(t) 격자 최댓값 %.3e (음수여야 자연스럽다)" % pmax)

# (4) Om_lo 대 OmegaIA 구간
rng = np.random.default_rng(3)
h = OM.hmid
ys = np.concatenate([
    rng.uniform(0, 6.0, 3000),
    np.arange(0, OM.n - 1) * h,                                  # 절점(중앙 h)
    (np.arange(0, OM.n - 1) + 1e-12) * h, (np.arange(1, OM.n - 1) - 1e-12) * h,   # 절점 근방
    np.arange(0, OM.n - 1) * L.OM_h_hi, np.arange(0, OM.n - 1) * L.OM_h_lo,
    np.array([6.0, 6.0001, 6.000181885211242, 6.5, 0.0, 1e-300]),
])
ys = ys[ys >= 0]
lo_b = L.Om_lo(ys)
V = OM(ys)
d_hi = lo_b - V.hi          # 양수면 위반(하계가 ia 구간 위 끝보다 큼)
d_lo = V.lo - lo_b          # Om_lo 가 ia 아래 끝보다 얼마나 낮은가
print("(4) 점 %d개: max(Om_lo - ia.hi) = %.3e (<=0 이어야 함), max(ia.lo - Om_lo) = %.3e, min(ia.lo - Om_lo) = %.3e, ia 폭 max %.3e" % (
    len(ys), d_hi.max(), d_lo.max(), d_lo.min(), (V.hi - V.lo).max()))
viol = ys[d_hi > 0]
print("    위반 점:", viol[:10], " 개수", len(viol))
# 단조성(구현): Om_lo 가 y 에 비증가인가(정렬 뒤 차분)
o = np.argsort(ys); dif = np.diff(lo_b[o]); print("    Om_lo 정렬 차분 max %.3e (≤ 수 ulp 여야)" % dif.max())
# 조각 끝 shift 통계
i0 = np.clip(np.floor(ys / L.OM_h_hi).astype(np.int64), 0, OM.n - 2)
t_hi = L.up(L.up(ys / L.OM_h_lo) - i0)
print("    shift(t_hi>1) 건수 %d, 최대 t_hi %.6f, t_hi>2 건수 %d" % (((t_hi > 1) & (i0 < OM.n - 2)).sum(), t_hi.max(), (t_hi > 2).sum()))

# (5) 기록 binary64 PCHIP 와의 차 (test_lib 과 같은 비교, 다른 난수)
WORK = L.WORK
os.chdir(os.path.dirname(WORK)); sys.path.insert(0, WORK)
import json
from cert_lib import make_W_pchip
design = json.load(open("work/design.json"))
W = make_W_pchip(np.load("work/xKrig.npy"), np.load("work/wKrig.npy"), design["eta0"], design["eta1"], design["x1"])
yy = np.sort(rng.uniform(0, 6, 200000)); a = L.Om_lo(yy); b = W(yy)
print("(5) 기록 PCHIP - Om_lo: max %.3e min %.3e; ia 구간이 기록값을 품지 못하는 점(기록 > ia.hi 또는 < ia.lo) 수:" % ((b - a).max(), (b - a).min()), end=" ")
Vy = OM(yy[::20]); by = b[::20]
print(int(((by > Vy.hi) | (by < Vy.lo)).sum()), "/", len(by), " (정의가 다른 두 함수이므로 0 일 필요 없음)")
# 절점에서의 차: 정확 정의 절점값(ia y) 대 기록 ys(binary64)
dy_knot = OM.y.lo - W.ys, OM.y.hi - W.ys
print("    절점값 차(기록 binary64 ys 대 ia 구간): 기록이 구간 아래 %d개, 위 %d개 / %d; 최대 |차| %.3e" % (
    (W.ys < OM.y.lo).sum(), (W.ys > OM.y.hi).sum(), OM.n, max(np.abs(dy_knot[0]).max(), np.abs(dy_knot[1]).max())))
# 상수 0.04, 0.12, 0.1 의 binary64 판 대 십진
print("    binary64(0.04)-0.04 = %s, binary64(0.12)-0.12 = %s, binary64(0.1)-0.1 = %s" % (Fr(0.04) - Fr(4, 100), Fr(0.12) - Fr(12, 100), Fr(0.1) - Fr(1, 10)))
print("(6) iv.dps=%d mp.dps=%d  changed=%s fc_ok=%s alpha_max=%.4f" % (iv.dps, mp.dps, "(assert 통과)", OM.fc_ok, OM.alpha_max))
