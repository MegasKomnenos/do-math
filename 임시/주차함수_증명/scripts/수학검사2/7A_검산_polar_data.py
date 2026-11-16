"""7A 부록 D.polar-blocks-488 「결과」·「범위」·「독립 재계산」 수치를 자료에서 다시 읽는다 (읽기 전용)."""
import json, math, sys
from collections import defaultdict
IV = 'C:/math/임시/주차함수_증명/원고_자료/세션_재계산/r89eb039_polar_iv/out/'
OLD = 'C:/math/임시/주차함수_증명/원고_자료/세션_재계산/r89eb039_polar/'
REC = 'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/r89eb039f714148a8b5c470572e07305f/'

def load(fn):
    out = []
    for l in open(fn, encoding='utf-8'):
        l = l.strip()
        if l:
            out.append(json.loads(l))
    return out

B = load(IV + 'NEW_blocks_merged.jsonl')
print('blocks', len(B), 'distinct', len({(r['k1'], r['k2']) for r in B}), 'ok', sum(1 for r in B if r.get('ok')))
B.sort(key=lambda r: r['k1'])
# coverage
cov = True
for a, b in zip(B[:-1], B[1:]):
    if b['k1'] != a['k2'] + 1 and b['k1'] > a['k2'] + 1: cov = False; print('GAP', a['k2'], b['k1'])
print('first k1', B[0]['k1'], 'last k2', B[-1]['k2'], 'contiguous', cov)
print('max k2/k1', max(r['k2']/r['k1'] for r in B), ' widths in [2087,5000]: min %.4f max %.4f' % (
    min(r['k2']/r['k1']-1 for r in B if 2087 <= r['k1'] <= 5000), max(r['k2']/r['k1']-1 for r in B if 2087 <= r['k1'] <= 5000)))
rows = [(2001, 2086), (2087, 5000), (5001, 20000), (20001, 150000), (150001, 400000), (400001, 1000000), (1000001, 3000000), (3000001, 10000000)]
print('\nrow | n | min eta | min eta0 | Vsqrtk1 min..max | max Gamma (Gamma-1) | min psi_lo | min eta/inf_max | max eps_n0 | min psi/((4-2Vsk1)/k2) | min psi/((4-2Vsk1)/k1)')
for lo, hi in rows:
    R = [r for r in B if lo <= r['k1'] <= hi]
    g = max(r['Gamma'] for r in R)
    print('%d-%d | %d | %.6g | %.6g | %.6f..%.6f | %.9f (%.3g) | %.6g | %.6g | %.4g | %.4f | %.4f' % (
        lo, hi, len(R), min(r['eta'] for r in R), min(r['eta0'] for r in R), min(r['Vsqrtk'] for r in R), max(r['Vsqrtk'] for r in R), g, g-1,
        min(r['psi_lo'] for r in R), min(r['eta']/r['inf_max'] for r in R), max(r['eps_n0'] for r in R),
        min(r['psi_lo']/((4-2*r['Vsqrtk'])/r['k2']) for r in R), min(r['psi_lo']/((4-2*r['Vsqrtk'])/r['k1']) for r in R)))
print('\nall: Vsqrtk1 [%.6f, %.6f]  min eta/inf_max %.6g  min eta0 %.8g  max eps_n0 %.6g  min psi_lo %.4g' % (
    min(r['Vsqrtk'] for r in B), max(r['Vsqrtk'] for r in B), min(r['eta']/r['inf_max'] for r in B), min(r['eta0'] for r in B), max(r['eps_n0'] for r in B), min(r['psi_lo'] for r in B)))
# sigma bracket margins
m1 = min(B, key=lambda r: r['loU'] - 1); m2 = min(B, key=lambda r: 1 - r['upL'])
print('tightest bracket: loU-1 = %.4g at [%d,%d];  1-upL = %.4g at [%d,%d]' % (m1['loU']-1, m1['k1'], m1['k2'], 1-m2['upL'], m2['k1'], m2['k2']))
# compare with old (binary64) recert for 3e-4 claim
O = {}
for fn in ['NEW_recert_P1', 'NEW_adaptive_2087_5000', 'NEW_recert_P2', 'NEW_recert_P3', 'NEW_recert_P4a', 'NEW_recert_P4b', 'NEW_recert_Q1', 'NEW_recert_Q2']:
    for r in load(OLD + fn + '.jsonl'):
        if r.get('ok'): O[(r['k1'], r['k2'])] = r
print('old ok blocks', len(O))
# record values (orig) vs old recert: relative 3e-4 claim is about old recert vs record ('orig')
worst_eta = 0; worst_v = 0
for key, r in O.items():
    o = r.get('orig') or {}
    if o.get('eta') and r.get('eta') and abs(r['delta'] - (o.get('delta') or r['delta'])) < 1e-12:
        worst_eta = max(worst_eta, abs(r['eta']/o['eta'] - 1))
    if o.get('Vsqrtk') and r.get('Vsqrtk'):
        worst_v = max(worst_v, abs(r['Vsqrtk']/o['Vsqrtk'] - 1))
print('old recert vs record (same delta): max rel |d eta| %.3g, max rel |d Vsqrtk| %.3g' % (worst_eta, worst_v))
# also compare delta choices old vs record
nd = sum(1 for key, r in O.items() if (r.get('orig') or {}).get('delta') is not None and abs(r['delta'] - r['orig']['delta']) > 1e-12)
print('old recert blocks whose delta differs from record:', nd)
# new (iv) vs old: eta decrease, Vsqrtk, psi
same = 0; wd = []; worst_eta_dec = 0; worst_v2 = 0; worst_psi = 0; Lup = 0
for r in B:
    o = O.get((r['k1'], r['k2']))
    if not o: print('no old for', r['k1'], r['k2']); continue
    if abs(o['delta'] - r['delta']) < 1e-12:
        same += 1
        worst_eta_dec = min(worst_eta_dec, r['eta']/o['eta'] - 1)
        worst_v2 = max(worst_v2, abs(r['Vsqrtk']/o['Vsqrtk'] - 1))
        worst_psi = max(worst_psi, abs(r['psi_lo']/o['psi_lo'] - 1))
    else:
        wd.append((r['k1'], r['k2'], r['delta'], o['delta'], r['psi_lo'], o['psi_lo']))
    # same-delta candidates: compare eta across all_deltas
    od = {round(d[0], 12): d for d in o['all_deltas']}
    for d in r['all_deltas']:
        q = od.get(round(d[0], 12))
        if q and q[1] and d[1]:
            Lup = max(Lup, d[1]/q[1] - 1)
print('new vs old: same delta %d, differing %d %s' % (same, len(wd), wd))
print('  largest eta decrease (same delta) %.3g; max rel |dVsqrtk| %.3g; max rel |dpsi| %.3g; largest eta increase among same-delta candidates %.3g' % (worst_eta_dec, worst_v2, worst_psi, Lup))

# ---- sigma intervals ----
A = load(IV + 'achain_iv.jsonl')
print('\nsigma intervals', len(A), 'ok', sum(1 for r in A if r['ok']), 'aux_ok', sum(1 for r in A if r['aux_ok']), 'vacuous', sum(1 for r in A if r['vacuous']))
print('cover: first %s last %s' % (A[0]['sigma'], A[-1]['sigma']))
print('min eta_rel %.4f, min phi_a-1 %.4f, max Vsk %.5f, max T_up %.5f, max eps_half %.4g' % (
    min(r['eta_rel'] for r in A), min(r['phi_a'] for r in A)-1, max(r['Vsk'] for r in A), max(r['T_up'] for r in A), max(r['eps_half'] for r in A)))
print('L1 is the min of (L1,L2,L3) on all intervals:', all(r['L1'] <= min(r['L2'], r['L3']) for r in A), ' min L2-L1 %.4g min L3-L1 %.4g' % (min(r['L2']-r['L1'] for r in A), min(r['L3']-r['L1'] for r in A)))
print('max Lam_hi/sigma %.4f (sigma>=300 claim 2.54); min Lam_lo/sigma %.4f (claim 1.17 for sigma>=300); at last interval Lam_hi/s=%.4f Lam_lo/s=%.4f' % (
    max(r['Lam_hi']/r['sigma'][1] for r in A), min(r['Lam_lo']/r['sigma'][0] for r in A), A[-1]['Lam_hi']/300, A[-1]['Lam_lo']/A[-1]['sigma'][0]))
# compare with record sweep
S = load(REC + 'review/evidence/L15_fix/sweep3fixed_K10000000.jsonl')
print('record fixed sweep', len(S))
worst = defaultdict(float)
for r, s in zip(A, S):
    assert abs(r['sigma'][0] - s['sigma'][0]) < 1e-9
    for key in ('eta', 'phi_a', 'Vsk', 'T_up', 'A', 'Lam_lo', 'Lam_hi'):
        if s[key]: worst[key] = max(worst[key], abs(r[key]/s[key] - 1))
print('max rel diff iv vs record sweep:', {k: '%.3g' % v for k, v in worst.items()})
# log sigma check
for l in open(IV + 'achain_iv.log', encoding='utf-8'):
    if 'sigma lower check' in l: print(l.strip())
# k=1e7 point values from record l15_check
L = json.load(open(REC + 'evidence/peer/data/l15_check_10000000.json'))
c = L['chain']
print('k=1e7 record chain: eta %.5f phi_a %.4f Vsk %.4f eps_half %.3g' % (c['eta'], c['phi_a'], c['Vsk'], c['eps_half']))
