# M1: 1.3절 표·가운데 비교 부호·섬유 단봉성(n<=7)·마지막 차 재귀 대 전수 셈 대조
from math import comb
from itertools import product, permutations
from functools import lru_cache

@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n-1, j)*min(j+1, l+1)*A(j, l)*A(n-1-j, l) for j in range(n))

def b(n, l): return A(n, l) - A(n, l-1)

def park(a):
    n = len(a); occ = [False]*(n+1); pos = [0]*n
    for i, ai in enumerate(a):
        p = ai
        while p <= n and occ[p]: p += 1
        if p > n: return None
        occ[p] = True; pos[i] = p
    return pos

# brute force n<=7
for n in range(1, 8):
    cnt = {}
    for a in product(range(1, n+1), repeat=n):
        pos = park(a)
        if pos is None: continue
        M = max(p-x for p, x in zip(pos, a))
        cnt[M] = cnt.get(M, 0)+1
    row = [cnt.get(l, 0) for l in range(n)]
    rec = [b(n, l) for l in range(n)]
    print("brute n=%d" % n, row, "recursion ok" if row == rec else ("MISMATCH", rec))

print("table n<=10:")
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    print(n, row, sum(row), (n+1)**(n-1))

print("center sign d_{n,k_n}, n=2..20:")
for n in range(2, 21):
    k = (n+1)//2
    d = b(n, k) - b(n, k-1)
    print(n, k, d, "pos" if d > 0 else "neg")

# witnesses
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    mx = max(row); print("n", n, "min witness", row.index(mx))

# fiber unimodality n<=7
def h_of(sig):
    n = len(sig); hs = []
    for i in range(1, n+1):
        z = max([j for j in range(1, i) if sig[j-1] > sig[i-1]] + [0])
        hs.append(i-z)
    return hs
for n in range(1, 8):
    bad = 0
    for sig in permutations(range(1, n+1)):
        hs = h_of(sig)
        As = [1]
        for l in range(n):
            p = 1
            for h in hs: p *= min(h, l+1)
            As.append(p)
        row = [As[i+1]-As[i] for i in range(n)]
        # unimodal?
        i = 0
        while i+1 < n and row[i] <= row[i+1]: i += 1
        while i+1 < n and row[i] >= row[i+1]: i += 1
        if i+1 < n: bad += 1
    print("n=%d non-unimodal fibers: %d" % (n, bad))
print("sigma=(1,2,3,5,4,6,7) h:", h_of((1,2,3,5,4,6,7)))
