# -*- coding: utf-8 -*-
"""H12 검산 1: 부록 D 장2·장3·장4·장5·장6 항목의 작은 수치를 독립으로 다시 센다."""
import sys, io, itertools, math
from fractions import Fraction as F
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def unimodal(seq):
    i = 0
    while i + 1 < len(seq) and seq[i] <= seq[i + 1]:
        i += 1
    while i + 1 < len(seq) and seq[i] >= seq[i + 1]:
        i += 1
    return i == len(seq) - 1

# ---- (1) 섬유 전수 n<=7: 곱 공식
print("== D.fiber-enumeration ==")
for n in range(1, 8):
    ms = set(); nonuni = []
    for sig in itertools.permutations(range(1, n + 1)):
        h = []
        for i in range(1, n + 1):
            prev = [j for j in range(1, i) if sig[j - 1] > sig[i - 1]]
            h.append(i - (max(prev) if prev else 0))
        ms.add(tuple(sorted(h)))
        A = [math.prod(min(hi, l + 1) for hi in h) for l in range(n)]
        b = [A[0]] + [A[l] - A[l - 1] for l in range(1, n)]
        if not unimodal(b):
            nonuni.append((sig, tuple(h), tuple(b)))
    print(n, "multisets", len(ms), "nonunimodal fibers", len(nonuni), nonuni[0] if nonuni else "")

def park(pref):
    n = len(pref); spots = [0] * n; dmax = 0
    for car, a in enumerate(pref, 1):
        s = a
        while s <= n and spots[s - 1]:
            s += 1
        if s > n:
            return None
        spots[s - 1] = car; dmax = max(dmax, s - a)
    return tuple(spots), dmax

cnt = {}; total = 0
for pref in itertools.product(range(1, 8), repeat=7):
    r = park(pref)
    if r is None:
        continue
    total += 1
    if r[0] == (1, 2, 3, 5, 4, 6, 7):
        cnt[r[1]] = cnt.get(r[1], 0) + 1
print("n=7 parking functions", total, "= 8^6?", total == 8 ** 6, "target fiber row", [cnt.get(l, 0) for l in range(7)])

# ---- (2) 섬유 상계
print("== D.fiber-nonunimodal-bound ==")
def v_ok(n, b):
    for i in range(3, b + 1):
        for k in range(n // 2 + 1, n + 1):
            if (k + 1) ** (i - 1) * k + (k - 1) ** i - 2 * k ** i >= 0:
                return False
    return True

def bound(n, b):
    tot1 = F(0); tot2 = F(0)
    for c in range(n // 2 + 1, n + 1):
        kap = n - c - b + 1
        if kap < 0:
            continue
        base = F(math.factorial(n), math.factorial(c)) * c ** (c - 1) / F(math.factorial(kap) * (n + 1) ** (n - 1))
        if kap > 0:
            t1 = base * b * F(n - c + 1) ** (n - c - b)
            t2 = base * 2 * F(n - c - b + 3) ** (n - c - b)
        else:
            t1 = base; t2 = base
        tot1 += t1; tot2 += t2
    return 1 - tot1 + tot2

for b in range(3, 9):
    ok = v_ok(17, b)
    print(17, b, "allowed", ok, float(bound(17, b)) if ok else "")
for n in [100, 1000, 10000]:
    first_bad = None
    for b in range(3, 100):
        if not v_ok(n, b):
            first_bad = b; break
    print(n, "first disallowed b:", first_bad)

def bound_f(n, b):
    s1 = s2 = 0.0
    for c in range(n // 2 + 1, n + 1):
        kap = n - c - b + 1
        if kap < 0:
            continue
        lb = math.lgamma(n + 1) - math.lgamma(c + 1) + (c - 1) * math.log(c) - math.lgamma(kap + 1) - (n - 1) * math.log(n + 1)
        if kap > 0:
            s1 += math.exp(lb + math.log(b) + (n - c - b) * math.log(n - c + 1))
            s2 += math.exp(lb + math.log(2) + (n - c - b) * math.log(n - c - b + 3))
        else:
            s1 += math.exp(lb); s2 += math.exp(lb)
    return 1 - s1 + s2

for n, bs in [(100, range(3, 9)), (1000, range(3, 24)), (10000, range(3, 72))]:
    vals = [(bound_f(n, b), b) for b in bs]
    print(n, "min bound (float)", min(vals))

# ---- (3) 마지막 차 재귀로 행 n<=80
print("== rows via last-car recursion ==")
N = 80
A = [[0] * (N + 1) for _ in range(N + 1)]
binom = [[math.comb(n, j) for j in range(n + 1)] for n in range(N + 1)]
for l in range(N + 1):
    A[0][l] = 1
    for n in range(1, N + 1):
        A[n][l] = sum(binom[n - 1][j] * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l] for j in range(n))

def row(n):
    return [A[n][0]] + [A[n][l] - A[n][l - 1] for l in range(1, n)]

rows = {n: row(n) for n in range(1, N + 1)}
for n in range(1, N + 1):
    assert sum(rows[n]) == (n + 1) ** (n - 1) and rows[n][0] == math.factorial(n)
fails = [(n, l) for n in range(1, N + 1) for l in range(1, n - 1) if rows[n][l] ** 2 < rows[n][l - 1] * rows[n][l + 1]]
print("logconcavity fails n<=80:", fails)
b39, b40, b41 = rows[80][39], rows[80][40], rows[80][41]
print("b80,39 digits", len(str(b39)), "prefix ok", str(b39).startswith("84023389540434452566"), "suffix ok", str(b39).endswith("46143312"))
print("b80,40 ok", str(b40).startswith("87142111475418532284"), str(b40).endswith("94082336"), "b80,41 ok", str(b41).startswith("90378331460121557700"), str(b41).endswith("47923974"))
print("ratios", b40 / b39, b41 / b40, "sep 25928/25000 ok:", b40 * 25000 < 25928 * b39 and 25928 * b40 < 25000 * b41)
print("b39<b40<b41", b39 < b40 < b41, "b39*b41-b40^2>0", b39 * b41 - b40 ** 2 > 0)
print("== D.central-gap-integer (ㄴ) / crossing / chain ==")
neg = []
for n in range(2, 61):
    k = (n + 1) // 2; b = rows[n]
    d = b[k] - b[k - 1] if k < n else None
    if d is not None and d < 0:
        neg.append(n)
    if n <= 15:
        rh = all(b[j] >= b[j + 1] for j in range(k, n - 1))
        if not rh:
            print("right half not nonincreasing at n=", n)
print("d_{n,k_n}<0 for n in", neg)
cross = [n for n in range(5, 61) if rows[n][(n + 1) // 2] < rows[n][(n + 1) // 2 + 1]]
print("b_{n,k_n}<b_{n,k_n+1} false set in 5..60:", [n for n in range(5, 61) if n not in cross])
chainbreak = [n for n in range(1, 61) if not all(rows[n][i] < rows[n][i + 1] for i in range((n + 1) // 2 - 1))]
print("chain b0<...<b_{k-1} breaks at", chainbreak)
for n in [5, 7, 9, 11]:
    b = rows[n]; k = (n + 1) // 2
    print(" n", n, "row", b[:k + 1], "capacities kk with b_kk<b_{kk-1}:", [kk for kk in range(1, k) if b[kk] < b[kk - 1]])
bad = [(n, l) for n in range(3, 16) for l in range(0, n - 2) if 2 * l <= n - 2 and rows[n][l] > rows[n][l + 1] and rows[n][l + 1] ** 2 < rows[n][l] * rows[n][l + 2]]
print("Q_L fails 3..15:", bad)
print("rows n<=15 unimodal:", all(unimodal(rows[n]) for n in range(1, 16)))
print("== D.crossing-small-n recurrence check ==")
p = [(m + 1) ** (m - 1) if m > 0 else 1 for m in range(N + 1)]
ok = True
for l in range(0, 20):
    Ac = {}
    for n in range(0, min(2 * l + 4, 60) + 1):
        if n <= l + 1:
            Ac[n] = 0; continue
        s = sum(binom[n - 1][j] * (j - l) * p[j] * p[n - 1 - j] for j in range(l + 1, n))
        s += sum(Ac[i] * binom[n - 1][i] * p[n - 1 - i] * ((l + 1) + min(n - i, l + 1)) for i in range(l + 2, n))
        Ac[n] = s
        if Ac[n] != p[n] - A[n][l]:
            ok = False; print("mismatch", n, l)
print("A^c recurrence matches for l<20, n<=min(2l+4,60):", ok)
print("== D.theorem-D-base pair count ==")
print(sum(1 for m in range(4, 701) for d in range(1, m) if 8 * d ** 3 <= m * m), "m=700 dmax", max(d for d in range(1, 100) if 8 * d ** 3 <= 700 * 700))
print("== D.tilt-sum-small-k ==")
for k in [2, 3, 10, 20, 42, 43]:
    s = sum(F(n ** (n - 1), math.factorial(n)) * F(k, k + 1) ** ((k - 1) * n) for n in range(2, k + 2))
    print(k, float(s), s < 1)
print("== D.prop-W-thirteen ==")
import mpmath as mp
mp.mp.dps = 30
def eRen(r1):
    return mp.mpf(r1) ** (r1 - 1) / (mp.e ** (r1 - 1) * mp.factorial(r1 - 1))
for d in range(1, 15):
    L = 3130 * (eRen(d + 1) - mp.mpf(60) * (d + 1) / (3131 + d))
    R = 2 * (1 + sum(eRen(r + 1) + mp.mpf(60) * (r + 1) / (3131 + d) for r in range(1, d)))
    print(d, mp.nstr(L, 6), mp.nstr(R, 5), L > R)
print("== D.theorem-U-constant arithmetic ==")
c = 1 / mp.sqrt(2 * mp.pi)
print("3c(J+cY)", 3 * c * (8.133 + c * 10.301), "1.5*G*c*c(JX+cYX)", 1.5 * 2.7323 * 0.8051 * c * (17.951 + c * 23.462))
print("with computed", 3 * c * (8.13091 + c * 10.29939), 1.5 * 2.7323 * 0.8051 * c * (17.94855 + c * 23.46002))
print("== D.zeta-constants ==")
print(mp.zeta(1.5), mp.zeta(0.5), mp.zeta(-0.5))
Nz = 2000; S = sum(mp.mpf(j) ** -1.5 for j in range(1, Nz))
print("S+2N^-1/2+N^-3/2/2", S + 2 / mp.sqrt(Nz) + mp.mpf(Nz) ** -1.5 / 2, "S+2(N-1/2)^-1/2", S + 2 / mp.sqrt(Nz - 0.5))
print("sum_{j<=N}+2(N+1)^-1/2", S + mp.mpf(Nz) ** -1.5 + 2 / mp.sqrt(Nz + 1), "sum_{j<N}+2(N+1)^-1/2", S + 2 / mp.sqrt(Nz + 1))
print("== D.tail-T1 (B) ==")
L = mp.mpf('0.845204'); slope = mp.mpf(1) / 2 + 2 * L - mp.sqrt(3 * mp.pi / 2); print("slope", slope)
t = mp.mpf(100)
lhs = t * slope + mp.mpf(1) / 2 - (1 / (3 * t) + 8 / (3 * t * t) + mp.mpf('2.507') / t ** 2 + (1 + mp.mpf('2.1709') * t) / t ** 3)
print("t=100 lhs", lhs, "rhs", mp.mpf('0.0196') * t + mp.mpf('0.496'))
print("== central-gap-rational-audit (ㅅ) ==")
print(F(495594511, 240250000) > 2, float(F(495594511, 240250000)), 5.642 * 1.6809 * 0.39893 - 0.0163 - 3.554)
print(F(699, 100) - F(7, 2) - F(6 * 699 + 75, 100 * 31) - F(13 * 699, 200 * 961) - F(12 * 699, 100 * 30000))
print("k^5 e^{-k/520} at 30000:", mp.mpf(30000) ** 5 * mp.exp(-mp.mpf(30000) / 520))
print("sum D(1/16)", 176 + 2304 + 118 + 935 + 533 + 455 + 243, "D(1/8)", 183.51 + 2303.07 + 203.57 + 983.74 + 920.70 + 454.86 + 418.83)
print("== D.band-check product ==")
print(1.9570106 * 0.71216 * 0.4999889 * (2 * 0.9885536 - 0.0071375) - 0.0168737)
print("== induction-rows m=10001 ==", 10001 - max(f for f in range(1000) if 64 * f ** 3 <= 27 * 10001 ** 2))
print("== counts ==", 120 * 121, 120 * 121 // 2, "19985:", len([n for k in range(8, 10001) for n in (2 * k - 1, 2 * k) if n >= 16]))
print("(ㄹ) positions 5..20000:", sum(n - 2 - (n - 1 + 1) // 2 for n in range(5, 20001)), "C50:", sum(n - 2 - n // 2 for n in range(20001, 50001)))
print("(ㄴ) comparisons:", sum((n + 1) // 2 - 1 for n in range(10001, 20001)))
print("newton counts:", sum(r - 1 for r in range(2, 171)), sum(r - 1 for r in range(2, 41)))
print("10001^(-1/3)=", 10001 ** (-1 / 3), "0.0015/1.25^12=", 0.0015 / 1.25 ** 12)
print("pi/0.019=", math.pi / 0.019, " 166*10001^(-1/6)*exp(-0.1267*10001) exponent:", math.log(166) - math.log(10001) / 6 - 0.1267 * 10001)
