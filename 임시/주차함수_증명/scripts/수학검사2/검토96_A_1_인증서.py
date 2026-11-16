# -*- coding: utf-8 -*-
"""검토 96 A: (1) 기록 인증서 cert2/cert3의 저장 xa·xb가 orig/rig_cert.py의 float 격자와 같은지 전수 확인,
(2) boxes.py의 u 끝이 기록 인증서의 u(float)와 같은지, (3) A00.json의 u_top^3*10001>=1 (Fraction), 53비트 반올림 방향,
(4) verify_exact_cover.main을 임시 사본 폴더(A00.json만)에서 실행, (5) 기록 코드의 양 끝 미덮음 폭(셀·Taylor 영역)."""
import os, sys, json, glob, shutil
from fractions import Fraction as Fr
import mpmath
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CWR = os.path.join(ROOT, '원고_자료', '세션_재계산', 'critical_window_rerun')
REC = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/ra4c01fca85d24f5cb35be1ec80d8e1c8/evidence/certificates'
sys.path.insert(0, CWR)
from boxes import all_boxes
from verify_exact_cover import ex

# (1) float grid of the record's certify (orig/rig_cert.py): m = ceil((x_hi-x_lo)/h), hh=(x_hi-x_lo)/m, xa = x_lo + k*hh, xb = xa+hh
x_lo, x_hi, h = 1.4, 10.0, 0.2
import math
m = int(math.ceil((x_hi - x_lo) / h)); hh = (x_hi - x_lo) / m
xa = [x_lo + k * hh for k in range(m)]; xb = [a + hh for a in xa]
print('m =', m, 'hh =', repr(hh))
files = sorted(glob.glob(os.path.join(REC, 'cert2', 'ubox_??.json'))) + sorted(glob.glob(os.path.join(REC, 'cert3', 'ubox_??.json')))
print('record certificates:', len(files))
nsame = 0; bad = []
rec_u = []
for p in files:
    D = json.load(open(p))
    recs = D['records']
    ok = ([r['xa'] for r in recs] == xa) and ([r['xb'] for r in recs] == xb) and len(recs) == 43
    nsame += ok
    if not ok: bad.append((p, len(recs), recs[0]['xa'], recs[-1]['xb']))
    rec_u.append((os.path.relpath(p, REC), D['u'], D.get('c_lo'), D.get('c_hi'), D.get('nray'), D.get('x_lo'), D.get('x_hi'), D.get('h'), D['worst_margin']))
print('xa/xb lists identical to float grid in', nsame, 'of', len(files), 'certificates; mismatches:', bad)
# recert_first certificates of the record
for p in sorted(glob.glob(os.path.join(REC, 'cert*', '*recert_first.json'))):
    D = json.load(open(p)); recs = D['records']
    print('  recert', os.path.relpath(p, REC), 'x', D['x_lo'], D['x_hi'], 'h', D['h'], 'nsubW', D.get('nsubW'), 'cells', [(r['xa'], r['xb']) for r in recs], 'worst', D['worst_margin'])
# ends and gaps of the record grid, exact
xm = [(a + b) / 2 for a, b in zip(xa, xb)]
r = Fr(hh) / 2
print('record: first cell xa - 1.4 =', float(Fr(xa[0]) - Fr(7, 5)), '; Taylor low end - 1.4 =', float(Fr(xm[0]) - r - Fr(7, 5)))
print('record: 10 - last cell xb =', float(10 - Fr(xb[-1])), '; 10 - Taylor high end =', float(10 - (Fr(xm[-1]) + r)))
gaps = [(k, float((Fr(xm[k + 1]) - r) - (Fr(xm[k]) + r))) for k in range(m - 1) if (Fr(xm[k + 1]) - r) > (Fr(xm[k]) + r)]
print('record: Taylor gaps', len(gaps), 'max', max(g for _, g in gaps))
cgaps = [(k, float(Fr(xa[k + 1]) - Fr(xb[k]))) for k in range(m - 1) if Fr(xa[k + 1]) > Fr(xb[k])]
print('record: stored-cell gaps', len(cgaps), 'max', max(g for _, g in cgaps))
# grid points 1.4+0.2i not inside any Taylor region (exact)
miss = [i for i in range(m + 1) if not any(Fr(xm[k]) - r <= Fr(7, 5) + Fr(i, 5) <= Fr(xm[k]) + r for k in range(m))]
print('record: exact grid points 1.4+0.2i not in any Taylor region:', len(miss), miss)
# which gap points are of the form 2.0, 3.0,... (any cube k works) vs need 5|c
print('gap boundary points:', [1.4 + 0.2 * (k + 1) for k, _ in gaps])

# (2) boxes.py vs record u
bx = all_boxes()
A = bx[:30]; G = bx[30:]
mism = []
for (n, a, b), (rp, u, clo, chi, nray, xl, xh, hh_, wm) in zip(A + G, rec_u):
    if (float(a), float(b)) != tuple(u): mism.append((n, rp, float(a), float(b), u))
print('boxes.py u-edges equal record u floats:', not mism, mism[:5])
print('record nray values:', sorted(set(t[4] for t in rec_u)), 'x_lo/x_hi/h:', sorted(set((t[5], t[6], t[7]) for t in rec_u)))
print('G12, G13 of boxes.py:', [(n, mpmath.nstr(a, 12), mpmath.nstr(b, 12)) for n, a, b in G[12:]], '; record cert3 ubox_12/13 u:', rec_u[-2][1], rec_u[-1][1])

# (3) u_top
D = json.load(open(os.path.join(CWR, 'cert', 'A00.json')))
top = ex(D['u_exact'][1]); bot = ex(D['u_exact'][0])
print('A00 u_exact top =', D['u_exact'][1], ' top^3*10001 - 1 =', float(top ** 3 * 10001 - 1), '>=0 ?', top ** 3 * 10001 >= 1)
with mpmath.workdps(60):
    true_top = mpmath.mpf(10001) ** (-mpmath.mpf(1) / 3)
    print('true 10001^(-1/3) - 53-bit top =', mpmath.nstr(true_top - mpmath.mpf(top.numerator) / top.denominator, 5))
print('A00 u bottom = top - 0.0015 exactly?', top - bot == Fr(15, 10000), float(top - bot - Fr(15, 10000)))
print('A00 x_lo/x_hi/h types:', repr(D['x_lo']), repr(D['x_hi']), repr(D['h']))

# (4) verify_exact_cover on a temp copy containing only A00.json
import verify_exact_cover as V
tmp = os.path.join(HERE, '_tmp96A_cert'); os.makedirs(tmp, exist_ok=True)
shutil.copy(os.path.join(CWR, 'cert', 'A00.json'), tmp)
print('--- verify_exact_cover.main on copy of A00.json (expected: only the 44-count/tiling checks fail)')
rc = V.main(tmp)
print('rc =', rc)
# per-cell exact facts on A00
X0 = Fr(7, 5); S = Fr(1, 5)
over_lo = max(X0 + k * S - ex(r_['xa_exact']) for k, r_ in enumerate(D['records']))
over_hi = max(ex(r_['xb_exact']) - (X0 + (k + 1) * S) for k, r_ in enumerate(D['records']))
print('A00: max outward slack left %.3e right %.3e' % (float(over_lo), float(over_hi)))
# margin_exact vs components: equality or rounded-down?
dif = [float(ex(r_['D0lo_exact']) - ex(r_['lin_exact']) - ex(r_['quad_exact']) - ex(r_['tailE_exact']) - ex(r_['tailB_exact']) - ex(r_['margin_exact'])) for r_ in D['records']]
print('A00: comp - margin_exact: min %.3e max %.3e' % (min(dif), max(dif)))
# worst margin consistency
print('A00: worst_margin == min float margin:', D['worst_margin'] == min(r_['margin'] for r_ in D['records']), '; min exact', float(min(ex(r_['margin_exact']) for r_ in D['records'])))
# xm in cell? r >= max?
for k, r_ in enumerate(D['records']):
    a, b, xm_, rad = ex(r_['xa_exact']), ex(r_['xb_exact']), ex(r_['xm_exact']), ex(r_['r_exact'])
    assert a <= xm_ <= b and rad >= max(xm_ - a, b - xm_)
print('A00: xm in cell and r >= max(xm-a, b-xm) for all 43 cells: True')
