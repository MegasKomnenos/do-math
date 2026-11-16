# 검토전체7 M1 검산: 1장·2장의 수치 주장을 정확 정수/유리수로 다시 센다.
from fractions import Fraction
from math import comb, factorial, lgamma, log, exp, cosh, sqrt, pi
from itertools import permutations
import sys

def pf_count(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

# --- A_{n,l} by last-car recursion (정리 2-6) ---
NMAX = 24
A = [[0] * (NMAX + 2) for _ in range(NMAX + 1)]
for l in range(NMAX + 2):
    A[0][l] = 1
for n in range(1, NMAX + 1):
    for l in range(NMAX + 2):
        s = 0
        for j in range(n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l]
        A[n][l] = s

def b(n, l):
    if l < 0:
        return 0
    return A[n][l] - (A[n][l - 1] if l >= 1 else 0)

def row(n):
    return [b(n, l) for l in range(n)]

# 1.1 p_n table, 1.3 row table
print("p_n:", [pf_count(n) for n in range(0, 5)])
table = {
    1: [1], 2: [2, 1], 3: [6, 7, 3], 4: [24, 51, 34, 16], 5: [120, 421, 377, 253, 125],
    6: [720, 3963, 4594, 3688, 2546, 1296],
    7: [5040, 42253, 62145, 57398, 46142, 32359, 16807],
    8: [40320, 505515, 929856, 979430, 865970, 702292, 497442, 262144],
    9: [362880, 6724381, 15298809, 18289811, 17520519, 15455851, 12587507, 8977273, 4782969],
    10: [3628800, 98618763, 275075236, 371706836, 385131546, 359973796, 318092120, 259627152, 186093442, 100000000],
}
for n, r in table.items():
    assert row(n) == r, (n, row(n))
    assert sum(r) == pf_count(n)
print("1.3 table OK; row sums OK")

def smallest_witness(r):
    m = max(r)
    return r.index(m)

def is_unimodal(r):
    i = 0
    while i + 1 < len(r) and r[i] <= r[i + 1]:
        i += 1
    while i + 1 < len(r) and r[i] >= r[i + 1]:
        i += 1
    return i == len(r) - 1

print("ell*_n:", {n: smallest_witness(row(n)) for n in range(1, 11)})
# d_{n,k_n} sign
for n in range(2, NMAX + 1):
    kn = (n + 1) // 2
    d = b(n, kn) - b(n, kn - 1)
    print(f"n={n} k_n={kn} d={'<0' if d < 0 else ('>0' if d > 0 else '=0')}", end="; ")
print()
# b_{k,k-1} = k^{k-2}
for k in range(2, NMAX + 1):
    assert b(k, k - 1) == k ** (k - 2)
print("b_{k,k-1}=k^{k-2} OK")
# A_{n,0}=n!, A_1 = 1/(2-e^x) check
for n in range(0, 10):
    assert A[n][0] == factorial(n)
print("A_{n,0}=n! OK")
# unimodality n<=NMAX
assert all(is_unimodal(row(n)) for n in range(1, NMAX + 1))
print("rows unimodal up to", NMAX)

# --- 2.1/2.2 fiber ---
def capacities(sigma):
    n = len(sigma)
    h = []
    for i in range(1, n + 1):
        z = 0
        for j in range(1, i):
            if sigma[j - 1] > sigma[i - 1]:
                z = j
        h.append(i - z)
    return h

sig = (1, 2, 3, 5, 4, 6, 7)
h = capacities(sig)
assert h == [1, 2, 3, 4, 1, 6, 7], h
As = [0]
for l in range(7):
    p = 1
    for hi in h:
        p *= min(hi, l + 1)
    As.append(p)
rowsig = [As[i + 1] - As[i] for i in range(7)]
assert rowsig == [1, 31, 130, 222, 216, 264, 144], rowsig
print("정리 2-5 fiber row OK", As[1:])
# sigma' for n=9
n = 9
sp = tuple([n - 6, n - 5, n - 4, n - 2, n - 3, n - 1, n] + list(range(n - 7, 0, -1)))
assert sorted(sp) == list(range(1, n + 1))
assert capacities(sp) == [1, 2, 3, 4, 1, 6, 7, 1, 1]
print("sigma' n=9 capacities OK")
# n<=6 all fibers unimodal; n=7 count of nonunimodal fibers
for n in range(1, 8):
    bad = 0
    for s in permutations(range(1, n + 1)):
        hh = capacities(s)
        Av = []
        for l in range(n):
            p = 1
            for hi in hh:
                p *= min(hi, l + 1)
            Av.append(p)
        r = [Av[0]] + [Av[i] - Av[i - 1] for i in range(1, n)]
        if not is_unimodal(r):
            bad += 1
    print(f"n={n}: nonunimodal fibers = {bad}")

# direct parking check for n=3 examples (1.2)
def park(a):
    n = len(a)
    occ = [0] * (n + 2)
    pos = []
    for i, ai in enumerate(a):
        p = ai
        while p <= n and occ[p]:
            p += 1
        if p > n:
            return None
        occ[p] = i + 1
        pos.append(p)
    return pos

for a, M in [((1, 1, 2), 1), ((1, 2, 1), 2), ((1, 3, 1), 1), ((3, 1, 1), 1), ((2, 1, 1), 2)]:
    pos = park(a)
    assert max(pos[i] - a[i] for i in range(3)) == M, a
# brute-force n=3 classes
cnt = {}
for a in __import__("itertools").product(range(1, 4), repeat=3):
    pos = park(a)
    if pos:
        M = max(pos[i] - a[i] for i in range(3))
        cnt[M] = cnt.get(M, 0) + 1
assert cnt == {0: 6, 1: 7, 2: 3}
print("1.2 n=3 examples OK")

# 2.4 tree example: shape with subtree sizes (1,2,3,4,1,6,7): chain 7-6-4-3-2-1 plus leaf on vertex of size 6
# vertices: 0(root,size7),1(size6),2(size4),3(size3),4(size2),5(size1),6(leaf on 1)
parent = {1: 0, 2: 1, 6: 1, 3: 2, 4: 3, 5: 4}
children = {v: [] for v in range(7)}
for c, p in parent.items():
    children[p].append(c)
def desc(v):
    out = []
    for c in children[v]:
        out.append(c)
        out += desc(c)
    return out
D = {v: desc(v) for v in range(7)}
assert sorted(len(D[v]) + 1 for v in range(7)) == [1, 1, 2, 3, 4, 6, 7]
hist = [0] * 7
for lab in permutations(range(1, 8)):
    M = 0
    for v in range(7):
        I = sum(1 for u in D[v] if lab[u] < lab[v])
        M = max(M, I)
    hist[M] += 1
assert hist == [5, 155, 650, 1110, 1080, 1320, 720], hist
print("2.4 tree example counts OK", hist)

# 2.5 명제 2-7 distribution sums to 1
for n in range(1, 12):
    s = sum(Fraction(comb(n - 1, j) * (j + 1) * pf_count(j) * pf_count(n - 1 - j), pf_count(n)) for j in range(n))
    assert s == 1
print("명제 2-7 law sums to 1")

# 2.5 보조정리 2-16 i=3: v_k(2,1) = -1/k+4/k^2-1/k^3
for k in range(1, 10):
    v = Fraction(k + 1, k) ** 2 + Fraction(k - 1, k) ** 3 - 2
    assert v == -Fraction(1, k) + Fraction(4, k * k) - Fraction(1, k ** 3)
    assert (v < 0) == (k >= 4)
print("v_k(2,1) formula OK, negative iff k>=4")
# v_k(Z,H)<0 when H>=1, k>=4Z^2 (spot check Z<=6)
for Z in range(0, 7):
    for H in range(1, 5):
        for k in range(max(1, 4 * Z * Z), 4 * Z * Z + 30):
            v = (1 + 1 / k) ** Z + (1 - 1 / k) ** (Z + H) - 2
            assert v < 0, (Z, H, k, v)
print("v_k(Z,H)<0 for k>=4Z^2 spot OK")

# --- 명제 2-20 finite-n bounds ---
def bound(n, bb, exact=True):
    # bb = 𝔟
    def term(c, which):
        kap = n - c - bb + 1
        if kap < 0:
            return Fraction(0) if exact else 0.0
        if exact:
            base = Fraction(factorial(n), factorial(c)) * c ** (c - 1) / ((n + 1) ** (n - 1))
            if which == 1:
                num = Fraction(bb * (n - c + 1) ** (kap - 1), factorial(kap)) if kap >= 1 else Fraction(1)
            else:
                num = Fraction(2 * (kap + 2) ** (kap - 1), factorial(kap)) if kap >= 1 else Fraction(1)
            return base * num
        else:
            lb = lgamma(n + 1) - lgamma(c + 1) + (c - 1) * log(c) - (n - 1) * log(n + 1)
            if which == 1:
                ln = log(bb) + (kap - 1) * log(n - c + 1) - lgamma(kap + 1) if kap >= 1 else 0.0
            else:
                ln = log(2) + (kap - 1) * log(kap + 2) - lgamma(kap + 1) if kap >= 1 else 0.0
            return exp(lb + ln)
    s1 = sum(term(c, 1) for c in range(n // 2 + 1, n + 1))
    s2 = sum(term(c, 2) for c in range(n // 2 + 1, n + 1))
    return 1 - s1 + s2

def admissible(n, bb):
    for i in range(3, bb + 1):
        for k in range(n // 2 + 1, n + 1):
            if (k + 1) ** (i - 1) * k + (k - 1) ** i - 2 * k ** i >= 0:
                return False
    return True

for n, exact in [(17, True), (100, True), (1000, False), (10000, False)]:
    best = None
    bb = 3
    while bb - 1 <= n // 2 and admissible(n, bb):
        v = bound(n, bb, exact)
        if best is None or v < best[0]:
            best = (v, bb)
        bb += 1
    v, bb0 = best
    print(f"n={n}: min bound = {float(v):.10f} at b={bb0}; first inadmissible b={bb}")

# 2.9 x_y(y) = -1/y via N
def Ncal(l, t):
    return min(t, l + 1) * A[t - 1][l]
for y in range(2, 12):
    x = Fraction(Ncal(y, y) - 2 * Ncal(y - 1, y) + Ncal(y - 2, y), y ** (y - 1))
    assert x == Fraction(-1, y)
print("x_y(y) = -1/y OK")
# theta_t(k) = Ren(t-k) Bor(k)/Bor(t) (float), (마)
def Bor(m):
    return exp(-m + (m - 1) * log(m) - lgamma(m + 1))
def Ren(j):
    return 1.0 if j == 0 else exp(j * log(j) - j - lgamma(j + 1))
for k in range(2, 8):
    for t in range(k, 15):
        th = comb(t, k) * k ** (k - 1) * (t - k) ** (t - k) / t ** (t - 1)
        assert abs(th - Ren(t - k) * Bor(k) / Bor(t)) < 1e-12
print("theta = Ren*Bor/Bor OK")
# Psi(q) <= 0.7979 sqrt q
assert all(sum(Ren(j) for j in range(1, q + 1)) <= 0.7979 * sqrt(q) for q in range(1, 400))
print("Psi bound OK; 2/sqrt(2pi) =", 2 / sqrt(2 * pi))
# (라) of moving-tail: sum Ren Ren <= 1/2, sum g2 Ren Ren <= m/4
for m in range(2, 200):
    s = sum(Ren(g) * Ren(m - g) for g in range(1, m))
    s2 = sum((m - g) * Ren(g) * Ren(m - g) for g in range(1, m))
    assert s <= 0.5 and s2 <= m / 4
print("moving-tail (라) sums OK")
# (바) e Ren(r+1) >= e^{-1/2} r^{-1/2} > 1/(2 sqrt(r+1))
for r in range(1, 300):
    v = exp(1) * Ren(r + 1)
    assert v <= 1 and v >= exp(-0.5) / sqrt(r) and exp(-0.5) / sqrt(r) > 1 / (2 * sqrt(r + 1))
print("moving-tail (바) OK")
# (사) |-d_{n,n-r}/n^{n-2} - e Ren(r+1)| <= 60(r+1)/n for n<=NMAX
worst = 0
for n in range(3, NMAX + 1):
    for r in range(1, (n - 1) // 2 + 1):
        d = b(n, n - r) - b(n, n - r - 1)
        lhs = abs(-d / n ** (n - 2) - exp(1) * Ren(r + 1))
        worst = max(worst, lhs / (60 * (r + 1) / n))
        assert lhs <= 60 * (r + 1) / n
print("moving-tail (사) OK up to", NMAX, "worst ratio", worst)
# (가) Q_{n,r,1} closed form >= b_{n,n-r-1}-b_{n,n-r} >= Q1 - Q2 (check upper only)
for n in range(3, NMAX + 1):
    for r in range(1, (n - 1) // 2 + 1):
        Q1 = comb(n, r) * (n - r) ** (n - r - 2) * (r + 1) ** r
        assert b(n, n - r - 1) - b(n, n - r) <= Q1
print("moving-tail (가) upper OK")
# 2-30: B_{n,k-1} vs J_n(k-1) via brute force over permutations, n<=7
def E_B_counts(n, k):
    # returns b_{n,k}-b_{n,k-1}, E_{n,k}, E2, B_{n,k-1}, J_n(k-1), Xi
    E = E2 = B = 0
    J = 0
    for s in permutations(range(1, n + 1)):
        hh = capacities(s)
        Z = sum(1 for x in hh if x > k)
        H = sum(1 for x in hh if x == k)
        prod_small = 1
        for x in hh:
            if x < k:
                prod_small *= x
        J += H * k ** (H - 1) * (k - 1) ** Z * prod_small if H >= 1 else 0
        # B: max disp k-1, all max at threshold positions: heavy positions 0..k-2, threshold at least one k-1
        B += prod_small * (k - 1) ** Z * (k ** H - (k - 1) ** H)
        # E_{n,k}: max disp k with even positive number of positions achieving it: only heavy positions can reach k
        # count assignments: heavy positions choose m of Z to be k (m even >=2), others 0..k-1; non-heavy any within capacity
        base = 1
        for x in hh:
            if x <= k:
                base *= x
        for m in range(2, Z + 1, 2):
            E += base * comb(Z, m) * k ** (Z - m)
        if Z >= 2:
            E2 += base * comb(Z, 2) * k ** (Z - 2)
    return E, E2, B, J

for n in range(2, 8):
    for k in range(1, n + 1):
        E, E2, B, J = E_B_counts(n, k)
        d = b(n, k) - b(n, k - 1)
        assert d == 2 * E - B, (n, k, d, E, B)
        assert 2 * E2 - B <= d
        if n <= 2 * k - 1:
            assert B == J, (n, k, B, J)
        if n == 2 * k:
            assert B == J - comb(2 * k - 1, k - 1) * pf_count(k - 1) ** 2, (n, k, B, J)
print("정리 2-28, 따름정리 2-29, 보조정리 2-30 brute-force OK n<=7")
print("DONE")
