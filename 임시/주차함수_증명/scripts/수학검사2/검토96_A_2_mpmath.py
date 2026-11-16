# -*- coding: utf-8 -*-
"""검토 96 A: mpmath 변환의 손실 여부, exact_str의 정확성, H1 재인증 격자(nint)와 기록 recert 격자(ceil)의 셀 수,
ivio 캐시 왕복(repr 17자리)의 손실·축소 여부, tails의 x̂ 단조성(캐시 A00 읽기만)."""
import os, sys, random
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CWR = os.path.join(ROOT, '원고_자료', '세션_재계산', 'critical_window_rerun')
sys.path.insert(0, CWR)
import mpmath
import rig_W, common                       # same import environment as rerun_boxes.py
from rig_common import iv
from rig_cert import exact_str
from rig_pipeline import load_ub, tails
import ivio
from verify_exact_cover import ex

print('mp.dps after imports =', mpmath.mp.dps, ' mp.prec =', mpmath.mp.prec, ' iv.dps =', iv.dps, ' iv.prec =', iv.prec)
print('repr digits of mp:', mpmath.mp._repr_digits if hasattr(mpmath.mp, '_repr_digits') else '?')

# (1) iv.mpf(mpf) exactness and mpf(ivmpf) exactness; type of .a
x = mpmath.mpf('0.1')            # 53-bit
X = iv.mpf(x)
print('iv.mpf(53-bit mpf) exact:', X._mpi_[0] == x._mpf_ == X._mpi_[1], '; type(X.a) =', type(X.a).__name__)
with mpmath.workdps(iv.dps):
    y = mpmath.mpf(iv.mpf('1.4').a)     # 103-bit endpoint -> mp (inside workdps 30)
print('mpf(ivmpf endpoint) inside workdps(30) lossless:', y._mpf_ == iv.mpf('1.4')._mpi_[0])
y2 = mpmath.mpf(iv.mpf('1.4').a)        # outside workdps (mp.dps 15)
print('mpf(ivmpf endpoint) outside workdps lossless:', y2._mpf_ == iv.mpf('1.4')._mpi_[0])
# exact_str correctness vs Fraction
for v in [iv.mpf('1.4').a, iv.mpf('1.4').b, mpmath.mpf('-0.3'), mpmath.mpf(0), (iv.mpf('10') - iv.mpf('1.4')).a]:
    s = exact_str(v); t = v._mpi_[0] if hasattr(v, '_mpi_') else v._mpf_
    sign, man, e, bc = t
    assert ex(s) == (-1) ** sign * Fr(man) * Fr(2) ** e
print('exact_str == Fraction reconstruction for 5 samples: True; e.g.', exact_str(iv.mpf('1.4').a))

# (2) H1 grid for recert windows (replicating certify lines 134-150) vs record's ceil grid
def h1_cells(x_lo, x_hi, h):
    XL = iv.mpf(str(x_lo)); XH = iv.mpf(str(x_hi)); HS = iv.mpf(str(h))
    with mpmath.workdps(iv.dps):
        m = int(mpmath.nint(mpmath.mpf((XH - XL).a) / mpmath.mpf(HS.a)))
    step = (XH - XL) / m
    cells = []
    for k in range(m):
        lo = (XL + k * step).a; hi = (XL + (k + 1) * step).b
        with mpmath.workdps(iv.dps):
            lo_f = mpmath.mpf(lo); hi_f = mpmath.mpf(hi); xm_f = (lo_f + hi_f) / 2
        cell = iv.mpf([lo_f, hi_f]); XM = iv.mpf(xm_f)
        with mpmath.workdps(iv.dps):
            r_f = max(mpmath.mpf((XM - cell.a).b), mpmath.mpf((cell.b - XM).b))
        cells.append((ex(exact_str(lo_f)), ex(exact_str(hi_f)), ex(exact_str(xm_f)), ex(exact_str(r_f))))
    return m, cells
import math
for (a, b, h) in [(1.4, 1.8, 0.1), (1.4, 1.6, 0.1), (1.4, 10, 0.2)]:
    m, cells = h1_cells(a, b, h)
    m_rec = int(math.ceil((b - a) / h)); hh_rec = (b - a) / m_rec
    A = Fr(str(a)); B = Fr(str(b)); H = Fr(str(h))
    cover = all(c[0] <= A + k * H and c[1] >= A + (k + 1) * H and c[2] - c[3] <= c[0] and c[2] + c[3] >= c[1] for k, c in enumerate(cells))
    print(f'window [{a},{b}] h={h}: H1 nint m={m} (cells cover exact grid & Taylor region covers cell: {cover}); record ceil m={m_rec}, hh={hh_rec!r}')

# (3) ivio cache round trip: lossy? can it shrink an interval?
random.seed(1)
shrink = 0; lossy = 0; maxrel = Fr(0)
for _ in range(2000):
    with mpmath.workdps(iv.dps):
        a = mpmath.mpf(random.random()) * mpmath.mpf(10) ** random.randint(-6, 3)
        a = a + mpmath.mpf(random.random()) * mpmath.mpf(2) ** -70   # make it a genuine 103-bit number
        b = a * (1 + mpmath.mpf(random.random()) * mpmath.mpf(10) ** -random.randint(2, 20))
    X = iv.mpf([a, b])
    Y = ivio.dec(ivio.enc(X))
    if Y._mpi_ != X._mpi_: lossy += 1
    if Y.a > X.a or Y.b < X.b: shrink += 1
    ra = abs(ex(exact_str(Y.a)) - ex(exact_str(X.a))) / ex(exact_str(X.a))
    maxrel = max(maxrel, ra)
print(f'ivio round trip of 2000 random 103-bit intervals: changed {lossy}, shrunk (lost enclosure at an endpoint) {shrink}, max relative endpoint error {float(maxrel):.2e}')
X = iv.mpf([iv.mpf('1.4').a, iv.mpf('1.4').b]); Y = ivio.dec(ivio.enc(X))
print('example: iv("1.4") -> cache -> ', ivio.enc(X), '-> back equals? ', Y._mpi_ == X._mpi_, '; contains 7/5?', ex(exact_str(Y.a)) <= Fr(7, 5) <= ex(exact_str(Y.b)))

# (4) cache A00: strings' digits and the loaded intervals are 53-bit?
ub = load_ub(os.path.join(CWR, 'cache', 'A00.json'))
bits = set()
for w in ub.W + [ub.J, ub.U]:
    for t in w._mpi_:
        bits.add(t[3])
print('A00 cache: bit counts of W/J/U endpoints after load (<=53 means 53-bit):', sorted(bits))
# (5) tails monotone in xhat: tails at cell [a,b] uses cell.a; compare with point evaluations
cell = iv.mpf([iv.mpf('1.4').a, iv.mpf('1.6').b])
tB_c, tE_c = tails(ub, cell, common.SMAX)
tB_p, tE_p = tails(ub, iv.mpf('1.5'), common.SMAX)
tB_q, tE_q = tails(ub, iv.mpf('1.6'), common.SMAX)
print('tails(cell [1.4,1.6]) >= tails(1.5) >= tails(1.6):', tE_c >= tE_p >= tE_q and tB_c >= tB_p >= tB_q, [float(mpmath.mpf(t)) for t in (tE_c, tE_p, tE_q)])
