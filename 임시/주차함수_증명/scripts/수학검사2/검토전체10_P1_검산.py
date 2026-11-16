# 검토전체10 P1: 1장·2장 수치 검산 (python -I)
from fractions import Fraction as Fr
from math import comb, factorial, lgamma, log, exp, sqrt
import itertools

def p(n):
    return 1 if n == 0 else (n + 1) ** (n - 1)

# A_{n,l} via last-car recursion (정리 2-6)
NMAX = 24
A = {}
for l in range(0, NMAX + 1):
    A[(0, l)] = 1
    for n in range(1, NMAX + 1):
        A[(n, l)] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[(j, l)] * A[(n - 1 - j, l)] for j in range(n))

def Af(n, l):
    return 0 if l < 0 else A[(n, l)]

def b(n, l):
    return Af(n, l) - Af(n, l - 1)

print("== 1.3 table rows n<=10")
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    print(n, row, sum(row), p(n))

print("== smallest witness, sign of d_{n,k_n} for 1..24")
for n in range(1, 25):
    row = [b(n, l) for l in range(n)]
    peak = row.index(max(row))
    uni = all(row[i] <= row[i + 1] for i in range(peak)) and all(row[i] >= row[i + 1] for i in range(peak, n - 1))
    kn = -(-n // 2)
    d = (b(n, kn) - b(n, kn - 1)) if n >= 2 else None
    print(n, "uni", uni, "l*", peak, "d_{n,k_n}", d)

print("== 2.2 fiber row sigma=(1,2,3,5,4,6,7)")
def caps(sig):
    n = len(sig)
    h = []
    for i in range(1, n + 1):
        z = max([j for j in range(1, i) if sig[j - 1] > sig[i - 1]] + [0])
        h.append(i - z)
    return h

sig = (1, 2, 3, 5, 4, 6, 7)
h = caps(sig)
print("h", h)
As = [1]
for l in range(7):
    v = 1
    for hi in h:
        v *= min(hi, l + 1)
    As.append(v)
print("A^sigma", As[1:], "row", [As[i + 1] - As[i] for i in range(7)])

print("== n<=6 all fibers unimodal? ; 2-28/2-29 brute force n<=7")
def park(a):
    n = len(a)
    occ = [0] * (n + 2)
    pos = [0] * n
    for i, ai in enumerate(a):
        j = ai
        while j <= n and occ[j]:
            j += 1
        if j > n:
            return None
        occ[j] = i + 1
        pos[i] = j
    return pos

for n in range(1, 8):
    fibers = {}
    E = {}
    E2 = {}
    B = {}
    bn = {}
    for a in itertools.product(range(1, n + 1), repeat=n):
        pos = park(a)
        if pos is None:
            continue
        sigma = tuple(sorted(range(1, n + 1), key=lambda c: pos[c - 1]))
        d = [pos[i] - a[i] for i in range(n)]
        M = max(d)
        cnt = d.count(M)
        bn[M] = bn.get(M, 0) + 1
        if cnt % 2 == 0:
            E[M] = E.get(M, 0) + 1
        if cnt == 2:
            E2[M] = E2.get(M, 0) + 1
        hh = caps(sigma)
        blocked = all(hh[pos[i] - 1] == M + 1 for i in range(n) if d[i] == M)
        if blocked:
            B[M] = B.get(M, 0) + 1
        fibers.setdefault(sigma, {})
        fibers[sigma][M] = fibers[sigma].get(M, 0) + 1
    if n <= 6:
        allu = True
        for s, dist in fibers.items():
            row = [dist.get(l, 0) for l in range(n)]
            pk = row.index(max(row))
            u = all(row[i] <= row[i + 1] for i in range(pk)) and all(row[i] >= row[i + 1] for i in range(pk, n - 1))
            if not u:
                allu = False
        print(n, "all fibers unimodal:", allu)
    ok = True
    for k in range(1, n + 1):
        lhs = bn.get(k, 0) - bn.get(k - 1, 0)
        rhs = 2 * E.get(k, 0) - B.get(k - 1, 0)
        if lhs != rhs:
            ok = False
            print("2-28 FAIL", n, k, lhs, rhs)
        if 2 * E2.get(k, 0) - B.get(k - 1, 0) > lhs:
            ok = False
            print("2-29 FAIL", n, k)
    print(n, "2-28/2-29 ok:", ok, "B_{n,0}=", B.get(0), ("E_{3,1}=%s" % E.get(1)) if n == 3 else "")
    if n == 7:
        row = [fibers[sig].get(l, 0) for l in range(7)]
        print("fiber row n=7 brute", row)

print("== 2-30: J_n(k-1)-B_{n,k-1} vs Xi; J-egf recursion, small n,k")
def Jn(n, k, z):
    tot = Fr(0)
    for s in itertools.permutations(range(1, n + 1)):
        hh = caps(s)
        H = hh.count(k)
        Z = sum(1 for x in hh if x > k)
        pr = 1
        for x in hh:
            if x < k:
                pr *= x
        if H > 0:
            tot += H * k ** (H - 1) * Fr(z) ** Z * pr
    return tot

def Bn(n, k):
    tot = 0
    for s in itertools.permutations(range(1, n + 1)):
        hh = caps(s)
        H = hh.count(k)
        Z = sum(1 for x in hh if x > k)
        pr = 1
        for x in hh:
            if x < k:
                pr *= x
        tot += pr * (k - 1) ** Z * (k ** H - (k - 1) ** H)
    return tot

for k in range(2, 4):
    for n in range(1, 2 * k + 2):
        J = Jn(n, k, k - 1)
        Bv = Bn(n, k)
        Xi = comb(2 * k - 1, k - 1) * p(k - 1) ** 2 if n == 2 * k else 0
        tag = "eq" if (n <= 2 * k and J - Bv == Xi) else ("(n>2k)" if n > 2 * k else "MISMATCH")
        print(k, n, "J-B", J - Bv, "Xi", Xi, tag)
z = Fr(5, 3)
for k in range(2, 4):
    Js = [Jn(n, k, z) for n in range(0, 2 * k + 1)]
    for n in range(0, 2 * k):
        rhs = sum(comb(n, i) * (z + i + 1) * p(i) * Js[n - i] for i in range(n + 1)) + (comb(n, k - 1) * p(k - 1) * p(n - k + 1) if n >= k - 1 else 0)
        print("J-egf rec k", k, "n+1", n + 1, Js[n + 1] == rhs)

print("== 2-13 chain formula check")
def pi0(n, y):
    coef = [Fr(0)] * (n + 1)
    coef[0] = Fr(1)
    T = [Fr(0)] * (n + 1)
    for t in range(1, min(y, n) + 1):
        T[t] = Fr(t ** (t - 1), factorial(t))
    for m in range(1, n + 1):
        coef[m] = sum(Fr(j, 1) * T[j] * coef[m - j] for j in range(1, m + 1)) / m
    return coef[n] * factorial(n) / p(n)

bad = False
for l in range(0, 4):
    y = l + 1
    for n in range(1, 2 * l + 4):
        rhs = p(n) * pi0(n, y) + sum(comb(n, m) * (l + 1) * Af(m - 1, l) * p(n - m) for m in range(l + 2, n + 1))
        if rhs != Af(n, l):
            bad = True
            print("2-13 FAIL", n, l, rhs, Af(n, l))
print("2-13 ok" if not bad else "2-13 has failures")

print("== b-top: b_{k,k-1}=k^(k-2)")
print(all(b(k, k - 1) == k ** (k - 2) for k in range(2, 20)))

print("== 2-40 five-part decomposition, k=3..6")
def Ncount(t, l):
    return (min(t, l + 1) * Af(t - 1, l)) if l >= 0 else 0

def bT(t, l):
    return Ncount(t, l) - Ncount(t, l - 1)

for k in range(3, 7):
    for n in range(2 * k + 1, 3 * k):
        d = b(n, k) - b(n, k - 1)
        Th = comb(n, k) * k ** (k - 2) * Af(n - k, k - 1)
        FL = sum(comb(n, t) * (bT(t, k) - bT(t, k - 1)) * Af(n - t, k - 1) for t in range(k + 1, 2 * k + 2))
        BV = sum(comb(n, m + 1) * p(n - 1 - m) * (b(m, k) + b(m, k - 1)) for m in range(2 * k + 1, n))
        KD = sum(comb(n, m + 1) * p(n - 1 - m) * k * (b(m, k) - b(m, k - 1)) for m in range(2 * k + 1, n))
        PAIR = Fr(1, 2) * sum(Fr(factorial(n), factorial(t1) * factorial(t2) * factorial(n - t1 - t2)) * (bT(t1, k) * bT(t2, k) + bT(t1, k - 1) * bT(t2, k - 1)) * p(n - t1 - t2) for t1 in range(1, n) for t2 in range(1, n - t1 + 1))
        print(k, n, "d", d, "sum", -Th + FL + BV + KD + PAIR, d == -Th + FL + BV + KD + PAIR)

print("== 2-20 finite-n bounds (floats, 3 digits)")
def lgf(x):
    return lgamma(x + 1)

def lp(n):
    return (n - 1) * log(n + 1)

def bound(n, bb):
    tot1 = 0.0
    tot2 = 0.0
    for c in range(n // 2 + 1, n + 1):
        kap = n - c - bb + 1
        if kap < 0:
            continue
        base = lgf(n) - lgf(c) + (c - 1) * log(c) - lp(n)
        t1 = exp(base + log(bb) + (n - c - bb) * log(n - c + 1) - lgf(kap))
        t2 = exp(base + log(2) + (n - c - bb) * log(n - c - bb + 3) - lgf(kap))
        tot1 += t1
        tot2 += t2
    return 1 - tot1 + tot2

def vneg(k, Z, H):
    return (1 + 1 / k) ** Z + (1 - 1 / k) ** (Z + H) - 2

for n in (17, 100, 1000, 10000):
    best = None
    for bb in range(3, 80):
        if not all(vneg(k, i - 1, 1) < 0 for i in range(3, bb + 1) for k in range(n // 2 + 1, n + 1)):
            break
        val = bound(n, bb)
        if best is None or val < best[0]:
            best = (val, bb)
    print(n, best)

print("== 2-26 bounds g, 2-37(라), 2-38(iv) checks")
g = lambda x: (x - 1) * log(1 + 1 / x)
print(all(1 - 3 / (2 * x) + 1 / (2 * x * x) <= g(x) <= 1 - 3 / (2 * x) + 5 / (6 * x * x) for x in [1, 1.5, 2, 3, 10, 100]))
Ren = lambda j: 1.0 if j == 0 else exp(j * log(j) - j - lgf(j))
Psi = lambda q: sum(Ren(j) for j in range(1, q + 1))
print(all(Psi(q) <= 0.7979 * sqrt(q) for q in range(1, 2000)))
Bor = lambda m: exp(-m + (m - 1) * log(m) - lgf(m))
def theta(t, k):
    return exp(lgf(t) - lgf(k) - lgf(t - k) + (k - 1) * log(k) + ((t - k) * log(t - k) if t > k else 0) - (t - 1) * log(t))
print(all(Ren(q) <= theta(k + q, k) * (1 + 1e-12) and theta(k + q, k) <= Ren(q) * (1 + q / k) ** 1.5 * (1 + 1e-12) for k in (2, 5, 50, 500) for q in range(0, 3 * k)))
print("Bor ratio formula:", all(abs(Bor(m + 1) / Bor(m) - exp(g(m) - 1)) < 1e-12 for m in range(1, 50)))
print("v_k(2,1) = -1/k+4/k^2-1/k^3 check:", all(abs(vneg(k, 2, 1) - (-1 / k + 4 / k ** 2 - 1 / k ** 3)) < 1e-12 for k in range(2, 30)), "sign k=3:", vneg(3, 2, 1), "k=4:", vneg(4, 2, 1))
print("== moving-tail (아): D=2, n>=57 within table range")
for n in range(57, 25):
    pass
print("tail decreasing b_{n,n-2}>b_{n,n-1} for n in 3..24:", [(n, b(n, n - 2) > b(n, n - 1)) for n in range(3, 25) if not b(n, n - 2) > b(n, n - 1)])
print("done")
