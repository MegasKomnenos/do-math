# -*- coding: utf-8 -*-
"""ZV8: 피드백 12.4의 사실 확인 — band_check/band_iv.py(기록 코드의 사본)가 구간 끝을 mpf로 바꾸는 자리(lo/hi)에서
최근접 반올림이 일어나 방향이 보존되지 않는지, 그 크기가 얼마인지, 그리고 band_cells.py의 셀별 하계와 얼마나 다른지를 잰다.
band_iv.py의 루프를 그대로 옮기되 lo/hi 변환마다 (변환값 - 원래 끝점)의 부호와 크기를 기록한다.
python -I scripts/수학검사2/검토_외부피드백_1116_ZV8_bandiv.py"""
import os, sys
from fractions import Fraction
from mpmath import iv, mp, mpf

ROOT = r"C:\math\임시\주차함수_증명"
TSV = os.path.join(ROOT, "원고_자료", "세션_재계산", "band_check", "band_cells_CE0.tsv")

iv.dps = 30
print("iv.dps =", iv.dps, " iv.prec =", iv.prec, " mp.dps(기본) =", mp.dps, " mp.prec =", mp.prec)
s0 = iv.mpf('0.71216'); CE = iv.mpf('0'); NSUB = 4000
N0 = 50001; n = iv.mpf(N0)
c = 1 / iv.sqrt(2 * iv.pi); TWO_SQPI = 2 / iv.sqrt(iv.pi)

stats = {"lo_up": 0, "lo_exact": 0, "lo_down": 0, "hi_down": 0, "hi_exact": 0, "hi_up": 0}
maxrel = [0.0]

def _cmp(conv, end):
    # conv: 53비트 mpf, end: 구간 끝점(iv 정밀도의 mpf). 정확 비교는 유리수로.
    a = Fraction(*conv.as_integer_ratio()) if hasattr(conv, 'as_integer_ratio') else None
    with mp.workprec(300):
        d = mp.mpf(conv) - mp.mpf(end)
        rel = abs(d) / abs(mp.mpf(end)) if end != 0 else abs(d)
    maxrel[0] = max(maxrel[0], float(rel))
    return d

def lo(x):
    v = mpf(x.a)
    d = _cmp(v, x.a)
    if d > 0: stats["lo_up"] += 1
    elif d == 0: stats["lo_exact"] += 1
    else: stats["lo_down"] += 1
    return v

def hi(x):
    v = mpf(x.b)
    d = _cmp(v, x.b)
    if d < 0: stats["hi_down"] += 1
    elif d == 0: stats["hi_exact"] += 1
    else: stats["hi_up"] += 1
    return v

def H_lower(rho, Q):
    s = iv.mpf(1); k = 1
    while True:
        f = 1 - TWO_SQPI * iv.mpf(k) ** iv.mpf('1.5') / iv.sqrt(iv.mpf(Q - 1))
        if hi(f) <= 0: break
        s += rho ** k * iv.mpf(max(mpf(0), lo(f)))
        k += 1
    return s

# band_cells.py의 셀별 하계
cells = {}
with open(TSV, encoding='ascii') as fh:
    fh.readline()
    for line in fh:
        f = line.rstrip('\n').split('\t')
        cells[int(f[0])] = (Fraction(f[1]), Fraction(f[2]), mpf(f[3]))

worst = None; maxdiff = (0, None); cell_end_err = 0.0; cover_gap = []
for i in range(NSUB):
    la = mpf(1) / 2 + (mpf(2) / 3 - mpf(1) / 2) * i / NSUB
    lb = mpf(1) / 2 + (mpf(2) / 3 - mpf(1) / 2) * (i + 1) / NSUB
    # 셀 끝점의 반올림 오차(정확 유리수 대비)
    ea, eb = Fraction(1, 2) + Fraction(1, 6) * Fraction(i, NSUB), Fraction(1, 2) + Fraction(1, 6) * Fraction(i + 1, NSUB)
    with mp.workprec(300):
        cell_end_err = max(cell_end_err, float(abs(mp.mpf(la) - mp.mpf(ea.numerator) / ea.denominator)),
                           float(abs(mp.mpf(lb) - mp.mpf(eb.numerator) / eb.denominator)))
    LA = iv.mpf(la); LB = iv.mpf(lb)
    rho = iv.mpf(lo(LA - 1 / n))
    Qmin = 3 * (1 - LB) * n / 10 - 1
    Q = int(mp.floor(lo(Qmin)))
    Hm = H_lower(rho, Q)
    assert lo(iv.mpf('0.4') * (1 - LB) * n - 6 * (LB * n) ** (iv.mpf(2) / 3) - 1) >= 0
    Rbar = iv.mpf('0.75') * (iv.mpf('1.1') * LB * n) ** (iv.mpf(2) / 3) + 1
    Upi = 3 * (1 - LA) * n / 10 * c * ((n + 1) / ((LA * n) * ((1 - LB) * n - Rbar))) ** iv.mpf('1.5') * iv.exp(1 / (12 * (n + 1)))
    wmin = 1 - iv.sqrt(2 / iv.pi) / iv.sqrt(iv.mpf(lo(Qmin))) - Upi
    topmax = c * (1 + 1 / n) ** iv.mpf('1.5') / iv.sqrt(LA) * (1 - LB) ** iv.mpf('-1.5') / iv.sqrt(n) * iv.exp(1 / (12 * n))
    eta = 1 / (12 * (iv.mpf('0.4') * (1 - LB) * n - 6 * (LB * n) ** (iv.mpf(2) / 3) + 1)) + 1 / (12 * LA * n) + 1 / (12 * (n + 1))
    Kt = LA * iv.exp(-eta)
    y = LA * n
    k1 = iv.mpf('1.5') * ((2 * LB - 1) * n + 2 * Rbar) / (y * ((1 - LB) * n - Rbar))
    E0 = iv.mpf('1.5') * Rbar * ((2 * LB - 1) * n + 2 * Rbar) / ((y - 1) * ((1 - LB) * n - Rbar))
    Wt = c * (iv.mpf(2) / 3) * (Rbar + 1) ** iv.mpf('1.5') * k1 * (1 + Rbar / y) ** iv.mpf('1.5') * iv.exp(E0 + 1 / (12 * y))
    Eplus = CE * (LA * n - 1) ** (iv.mpf(-1) / 3)
    lhs = iv.mpf(lo(Hm)) * s0 * iv.mpf(lo(Kt)) * (2 * iv.mpf(lo(wmin)) - iv.mpf(hi(topmax))) - iv.mpf(hi(Wt))
    q = lhs / (1 + iv.mpf(hi(Eplus)))
    ratio = lo(q)            # band_iv.py가 쓰는 값(53비트 최근접)
    exact_end = q.a          # 변환 전 끝점
    if worst is None or ratio < worst[0]:
        worst = (ratio, i, exact_end)
    with mp.workprec(300):
        d = abs(mp.mpf(ratio) - mp.mpf(cells[i][2]))
    if d > maxdiff[0]: maxdiff = (d, i)

print("lo/hi 변환 통계:", stats)
print("변환 하나의 최대 상대 변화:", maxrel[0])
print("셀 끝점(53비트)의 정확 유리수 대비 최대 오차:", cell_end_err)
print("band_iv 방식 최소 비(53비트 변환값):", mp.nstr(worst[0], 20), " 셀", worst[1], " 변환 전 끝점:", mp.nstr(worst[2], 20))
print("band_cells.tsv 셀 0 하계:", mp.nstr(cells[0][2], 20))
print("두 구현의 셀별 하계 최대 차:", mp.nstr(maxdiff[0], 5), " 셀", maxdiff[1])
print("문턱 1.3558 대비 여유(band_cells 셀 0):", mp.nstr(cells[0][2] - mpf('1.3558'), 10))
