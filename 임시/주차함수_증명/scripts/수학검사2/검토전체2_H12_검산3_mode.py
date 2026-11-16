# -*- coding: utf-8 -*-
"""H12 검산 3: 명제 witness-position-bound / D.exact-n20000(ㅂ)의 차를 방향 반올림 구간으로 다시 계산."""
import sys, io, csv
import mpmath as mp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mp.mp.dps = 30
iv = mp.iv
rows = {int(r['n']): int(r['mode_ell_mid']) for r in csv.DictReader(open(sys.argv[1], encoding='utf-8'), delimiter='\t')}
c1 = iv.mpf('0.59963'); c2 = iv.mpf('1.24847')
lo_all = None; hi_all = None; res = {}
for (a, b) in [(50, 900), (901, 20000)]:
    lo = None; hi = None
    for n in range(a, b + 1):
        m = iv.mpf(n + 1)
        v = iv.mpf(n + 1 - rows[n]) - c1 * m ** (mp.mpf(2) / 3) - c2 * m ** (mp.mpf(1) / 3)
        lo = v.a if lo is None else min(lo, v.a); hi = v.b if hi is None else max(hi, v.b)
    res[(a, b)] = (lo, hi); print((a, b), mp.nstr(lo, 12), mp.nstr(hi, 12))
print("all in [0.85,1.99]:", all(r[0] >= mp.mpf('0.85') and r[1] <= mp.mpf('1.99') for r in res.values()))
