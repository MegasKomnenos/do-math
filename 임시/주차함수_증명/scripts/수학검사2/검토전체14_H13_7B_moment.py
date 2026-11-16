# H13 검산: D.moment-certification 범위의 위치 수와 n_M(k)
import json, glob, os
from fractions import Fraction as Fr
cnt1 = sum((13*k*k)//100 - 2*k for k in range(501, 841))
print("첫째 범위 위치 수:", cnt1)
rec = glob.glob("C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/r10ff8c2*/evidence/peer/block3_501_2000_all.json")
print(rec)
if rec:
    d = json.load(open(rec[0], encoding="utf-8"))
    # 구조 파악
    if isinstance(d, dict):
        ks = list(d.keys())[:3]; print("keys sample", ks, d[ks[0]] if ks else None)
    else:
        print("list len", len(d), d[0])

# n_M(k) 재계산 (저장된 여섯 자리 성분; 정확 유리수)
d = json.load(open(rec[0], encoding="utf-8"))
rows = {r['k']: r for r in d}
def nM(k):
    r = rows[k]
    PM = Fr(str(r['Gamma']))*Fr(str(r['P_U']))*(1+Fr(2,10**5))
    n = r['n0']
    while True:
        ms = Fr(n-k, k+1)
        if ms*(ms-1) > n*PM: return n, PM
        n += 1
import math
lo = 10; hi = 0; tot2 = 0; bad = []
for k in range(841, 2001):
    n, PM = nM(k)
    ms = Fr(n-k, k+1); Q = ms*(ms-1)-n*PM; Qp = (2*ms-1)/(k+1)-PM
    if not (Q > 0 and Qp > 0): bad.append(k)
    ratio = n/k**1.5; lo = min(lo, ratio); hi = max(hi, ratio)
    tot2 += n-10001
    if k in (841, 2000): print("n_M(%d)=%d ratio=%.5f" % (k, n, ratio))
print("ratio range [%.5f, %.5f], 둘째 범위 위치 수 %d, Q/Q' 위반 열 %s" % (lo, hi, tot2, bad))
print("max(n0,NE) at 840/841:", max(rows[840]['n0'], rows[840]['NE']), max(rows[841]['n0'], rows[841]['NE']))
print("max over k of max(n0,NE)/ceil(0.836k^1.5):", max(max(rows[k]['n0'], rows[k]['NE'])/math.ceil(0.836*k**1.5) for k in range(501, 2001)))
