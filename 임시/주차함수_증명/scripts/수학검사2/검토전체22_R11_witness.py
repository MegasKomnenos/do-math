# R11 검산: D.exact-n20000 (ㅁ)(ㅂ) — 작은 행의 정확 계산, 봉우리 열과 두 항 공식의 차
import sys, csv
from math import comb
from mpmath import mp, mpf
mp.dps = 40
tsv = sys.argv[1]
rows = {}
with open(tsv, newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        rows[int(r['n'])] = r
print("rows:", len(rows), min(rows), max(rows))
# exact rows n<=160
N = 160
A = [[0]*N for _ in range(N+1)]
for l in range(N):
    col = [1]
    for n in range(1, N+1):
        col.append(sum(comb(n-1, j)*min(j+1, l+1)*col[j]*col[n-1-j] for j in range(n)))
    for n in range(N+1): A[n][l] = col[n]
bad_chain = []; mism = []; nonuni = []
for n in range(1, N+1):
    b = [A[n][l]-(A[n][l-1] if l else 0) for l in range(n)]
    kn = (n+1)//2
    if not all(b[i] < b[i+1] for i in range(0, kn-1)): bad_chain.append(n)
    mx = max(b); peaks = [i for i, x in enumerate(b) if x == mx]
    i = 0
    while i+1 < n and b[i] <= b[i+1]: i += 1
    while i+1 < n and b[i] >= b[i+1]: i += 1
    if i != n-1: nonuni.append(n)
    if n >= 5 and (len(peaks) != 1 or peaks[0] != int(rows[n]['mode_ell_mid'])): mism.append((n, peaks, rows[n]['mode_ell_mid']))
print("chain b0<...<b_{kn-1} fails at n =", bad_chain, " non-unimodal:", nonuni, " peak mismatches vs TSV (5<=n<=160):", mism)
c1 = mpf('0.59963'); c2 = mpf('1.24847')
def v(n):
    l = int(rows[n]['mode_ell_mid'])
    return (n+1-l) - c1*mpf(n+1)**(mpf(2)/3) - c2*mpf(n+1)**(mpf(1)/3)
for lo, hi in ((50, 900), (901, 20000)):
    vals = [(v(n), n) for n in range(lo, hi+1)]
    print(lo, hi, len(vals), "min", min(vals), "max", max(vals))
# totals of TSV
print("sum positions", sum(int(r['positions']) for r in rows.values()), "I", sum(int(r['I']) for r in rows.values()), "Q", sum(int(r['Q']) for r in rows.values()))
print("rows with firstQ <= lastI:", sum(1 for r in rows.values() if int(r['lastI_ell']) >= int(r['firstQ_ell'])))
print("mode != firstQ:", sum(1 for r in rows.values() if r['mode_ell_mid'] != r['firstQ_ell']))
