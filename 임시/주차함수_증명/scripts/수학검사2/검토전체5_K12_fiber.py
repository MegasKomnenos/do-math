# K12: D.fiber-enumeration -- n<=7 fibers via direct parking and via the product formula
import itertools

def park(pref):
    n = len(pref); spots = [0]*(n+1); disp = []
    for car, a in enumerate(pref, 1):
        p = a
        while p <= n and spots[p]: p += 1
        if p > n: return None
        spots[p] = car; disp.append(p-a)
    return tuple(spots[1:]), max(disp)

def hcap(sig):
    n = len(sig); h = []
    for i in range(1, n+1):
        m = 0
        for j in range(1, i):
            if sig[j-1] > sig[i-1]: m = j
        h.append(i-m)
    return h

def unimodal(z):
    i = 0
    while i+1 < len(z) and z[i] <= z[i+1]: i += 1
    while i+1 < len(z) and z[i] >= z[i+1]: i += 1
    return i+1 == len(z)

for n in range(1, 8):
    fib = {}; cnt = 0
    for pref in itertools.product(range(1, n+1), repeat=n):
        r = park(pref)
        if r is None: continue
        cnt += 1; sig, M = r
        fib.setdefault(sig, [0]*n)[M] += 1
    perms = list(itertools.permutations(range(1, n+1)))
    assert cnt == (n+1)**(n-1), (n, cnt)
    assert len(fib) == len(perms)
    mult = set(); nonuni = []
    for sig in perms:
        h = hcap(sig); mult.add(tuple(sorted(h)))
        A = [0]
        for l in range(n):
            v = 1
            for hi in h: v *= min(hi, l+1)
            A.append(v)
        row = tuple(A[l+1]-A[l] for l in range(n))
        assert row == tuple(fib[sig]), (n, sig)
        if not unimodal(row): nonuni.append((sig, tuple(h), row))
    nonuni.sort()
    print(f"n={n}: PF {cnt}, distinct h-multisets {len(mult)}, non-unimodal fibers {len(nonuni)}",
          ("first " + str(nonuni[0])) if nonuni else "")
