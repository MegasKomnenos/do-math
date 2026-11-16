from fractions import Fraction as F
from math import comb, factorial
from itertools import permutations
import math

# exact A_{n,l} via last-car recursion (정리 old-2-6)
def A_table(nmax, lmax):
    A = {}
    for l in range(-1, lmax + 1):
        A[(0, l)] = 1 if l >= 0 else 0
        for n in range(1, nmax + 1):
            if l < 0:
                A[(n, l)] = 0
                continue
            A[(n, l)] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[(j, l)] * A[(n - 1 - j, l)] for j in range(n))
    return A

def p(n):
    if n < 0:
        return 0
    if n == 0:
        return 1
    return (n + 1) ** (n - 1)

def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h.append(i - j)
    return h

def brute(n, k):
    Z1 = 0; H1 = 0; Z2 = 0; tot = 0
    Kpoly = {}
    for sig in permutations(range(1, n + 1)):
        h = caps(sig); w = 1
        for c in h:
            w *= min(c, k)
        Z = sum(1 for c in h if c > k); H = sum(1 for c in h if c == k)
        tot += w; Z1 += w * Z; H1 += w * H; Z2 += w * Z * (Z - 1)
        wf = 1
        for c in h:
            if c <= k:
                wf *= c
        Kpoly[Z] = Kpoly.get(Z, 0) + wf
    return tot, F(Z1, tot), F(H1, tot), F(Z2, tot), Kpoly

# ---- (7.3) moment recursion vs brute force; bd_t values; heavy-block (가) ----
ok = True
for k in (2, 3):
    nmax = 7
    A = A_table(nmax + 1, k + 1)
    a = lambda m: F(A[(m, k - 1)], factorial(m))
    Zf = {0: F(0)}; ZH = {0: F(0)}; ZZ = {0: F(0)}
    for n in range(1, nmax + 1):
        P = lambda j: min(j, k) * a(j - 1) * a(n - j) / (n * a(n))
        assert sum(P(j) for j in range(1, n + 1)) == 1
        Zf[n] = sum(P(j) * ((1 if j > k else 0) + Zf[j - 1] + Zf[n - j]) for j in range(1, n + 1))
        ZH[n] = sum(P(j) * ((1 if j == k else 0) + ZH[j - 1] + ZH[n - j]) for j in range(1, n + 1))
        ZZ[n] = sum(P(j) * (ZZ[j - 1] + ZZ[n - j] + 2 * Zf[j - 1] * Zf[n - j] + 2 * (1 if j > k else 0) * (Zf[j - 1] + Zf[n - j])) for j in range(1, n + 1))
        tot, z1, h1, z2, Kp = brute(n, k)
        if not (tot == A[(n, k - 1)] and z1 == Zf[n] and h1 == ZH[n] and z2 == ZZ[n]):
            ok = False; print("FAIL (7.3)", n, k)
        t = n + 1
        Kz = lambda z: sum(c * z ** e for e, c in Kp.items())
        Kz1 = lambda z: sum(c * e * z ** (e - 1) for e, c in Kp.items() if e >= 1)
        Kz2 = lambda z: sum(c * e * (e - 1) * z ** (e - 2) for e, c in Kp.items() if e >= 2)
        bd = k * Kz(k) - t ** (t - 1); bd1 = Kz(k) + k * Kz1(k); bd2 = 2 * Kz1(k) + k * Kz2(k)
        At = A[(n, k - 1)]
        ex = F(t * p(t - 1), At) - k
        if not (bd == -At * ex and bd1 == At * (1 + z1) and bd2 == F(At, k) * (2 * z1 + z2)):
            ok = False; print("FAIL bd", n, k)
        q = t - k
        if q >= 1 and not (z1 <= q - 1 and z2 <= (q - 1) * (q - 2)):
            ok = False; print("FAIL heavy(ga)", n, k)
print("(7.3), bd values, heavy-block(ga):", "ok" if ok else "FAIL")

# ---- variance formula (7.4) and mom for k=3 ----
k = 3; nmax = 10; A = A_table(nmax + 1, k + 1); a = lambda m: F(A[(m, k - 1)], factorial(m))
Zf = {0: F(0)}; ZH = {0: F(0)}; ZZ = {0: F(0)}; Pm = {}
for n in range(1, nmax + 1):
    Pm[n] = {j: min(j, k) * a(j - 1) * a(n - j) / (n * a(n)) for j in range(1, n + 1)}
    Zf[n] = sum(Pm[n][j] * ((1 if j > k else 0) + Zf[j - 1] + Zf[n - j]) for j in Pm[n])
    ZH[n] = sum(Pm[n][j] * ((1 if j == k else 0) + ZH[j - 1] + ZH[n - j]) for j in Pm[n])
    ZZ[n] = sum(Pm[n][j] * (ZZ[j - 1] + ZZ[n - j] + 2 * Zf[j - 1] * Zf[n - j] + 2 * (1 if j > k else 0) * (Zf[j - 1] + Zf[n - j])) for j in Pm[n])
cnt = {}
for n in range(0, nmax + 1):
    cnt[n] = {}
    for m in range(1, nmax + 1):
        if m == n:
            cnt[n][m] = F(1)
        elif m > n:
            cnt[n][m] = F(0)
        else:
            cnt[n][m] = sum(Pm[n][j] * (cnt[j - 1].get(m, 0) + cnt[n - j].get(m, 0)) for j in Pm[n])

def yv(m):
    g = lambda q: (1 if q > k else 0) + Zf[q - 1] + Zf[m - q]
    return sum(Pm[m][q] * g(q) ** 2 for q in Pm[m]) - Zf[m] ** 2

def mom(m):
    return 2 * sum(Pm[m][q] * Zf[q - 1] * Zf[m - q] for q in Pm[m]) + 2 * sum(Pm[m][q] * (Zf[q - 1] + Zf[m - q]) for q in Pm[m] if q > k) - k * Pm[m].get(k, 0)

ok2 = True
for n in range(1, nmax + 1):
    Var = ZZ[n] + Zf[n] - Zf[n] ** 2
    T = ZZ[n] - k * ZH[n]
    if Var != sum(cnt[n][m] * yv(m) for m in range(1, n + 1)):
        ok2 = False; print("FAIL var", n)
    if k * ZH[n] != sum(cnt[n][m] * k * Pm[m].get(k, 0) for m in range(k, n + 1)):
        ok2 = False; print("FAIL ZH", n)
    if T != Zf[n] * (Zf[n] - 1) + sum(cnt[n][m] * (yv(m) - k * Pm[m].get(k, 0)) for m in range(k, n + 1)):
        ok2 = False; print("FAIL (7.4)", n)
    if T != sum(cnt[n][m] * mom(m) for m in range(k, n + 1)):
        ok2 = False; print("FAIL mom", n)
xk = F(k ** (k - 1), (k + 1) ** (k - 1))
print("(7.4) variance/mom:", "ok" if ok2 else "FAIL", " mom_k=-k x_k:", mom(k) == -k * xk)

# ---- (7.13), fold-A, fold-R, fold-L1 for k=4 ----
k = 4; nmax = 16; A = A_table(nmax + 2, k + 1)

def Afun(m, l):
    return A[(m, l)] if m >= 0 else 0

cl_p = lambda m: F(Afun(m, k) - Afun(m, k - 1), Afun(m, k - 1)) if m >= 0 else F(0)
cl_m = lambda m: F(Afun(m, k - 1) - Afun(m, k - 2), Afun(m, k - 1)) if m >= 0 else F(0)
mu = lambda m: F(Afun(m, k) - 2 * Afun(m, k - 1) + Afun(m, k - 2), Afun(m, k - 1))

def Pk(m, j):
    return F(min(j, k) * comb(m - 1, j - 1) * Afun(j - 1, k - 1) * Afun(m - j, k - 1), Afun(m, k - 1))

def chi(m, j):
    ind = 1 if j > k else 0
    v = F(1, k) * (-(1 if j == k else 0) * (1 - cl_m(m - k)) + ind * (cl_p(j - 1) + cl_m(j - 1) + cl_p(m - j) + cl_m(m - j)))
    v += (1 + F(ind, k)) * cl_p(j - 1) * cl_p(m - j) + (1 - F(ind, k)) * cl_m(j - 1) * cl_m(m - j)
    return v

src = lambda m: sum(Pk(m, j) * chi(m, j) for j in range(1, m + 1))
ok3 = all(mu(m) == src(m) + sum(Pk(m, j) * (mu(j - 1) + mu(m - j)) for j in range(1, m + 1)) for m in range(1, nmax + 1))
print("(7.13):", ok3)

# fold-A, fold-R, fold-L1 with e^{-1} replaced by a rational t (identities are homogeneous)
t = F(1, 3)

def at(m, y):
    return t ** m * F(Afun(m, y - 1), factorial(m)) if m >= 0 else F(0)

def eBor(m):
    return t ** (m - 1) * F(m ** (m - 1), factorial(m))

okA = True; okR = True; okL = True
for n in range(k, nmax + 1):
    Eu = t / (n * at(n, k))
    thr = -eBor(k) * at(n - k, k - 1)
    heavy = sum(at(n - 1 - m, k) * (at(m, k + 1) - at(m, k - 1)) * (1 + (1 if n - 1 - m >= k else 0)) for m in range(k, n))
    quad = sum(min(j, k + 1) * (at(j - 1, k + 1) - at(j - 1, k)) * (at(n - j, k + 1) - at(n - j, k)) + min(j, k - 1) * (at(j - 1, k) - at(j - 1, k - 1)) * (at(n - j, k) - at(n - j, k - 1)) for j in range(1, n + 1))
    if src(n) != Eu * (thr + heavy + quad):
        okA = False; print("FAIL fold-A", n)
    if n >= 2 * k + 1:
        nu = n - 2 * k
        for B in range(nu + 1, n - 1 - k + 1):
            l = n - 1 - k - B
            sib = lambda q: eBor(n - k - q)
            lhs = sum(sib(q) * (at(k + q, k + 1) - at(k + q, k - 1)) for q in range(nu - 1, B + 1))
            ed1 = eBor(k + 1) * at(n - 1 - k, k + 1); ed2 = eBor(k) * at(n - k, k + 1)
            up = eBor(l + 2) * at(n - 2 - l, k - 1) + eBor(l + 1) * at(n - 1 - l, k - 1)
            inn = sum(sib(q + 1) * at(k + q + 1, k + 1) - sib(q - 1) * at(k + q - 1, k - 1) for q in range(nu, B))
            if lhs != ed1 + ed2 + inn - up:
                okR = False; print("FAIL fold-R", n, B)
            if any(at(n - 1 - k - q, k) != sib(q) for q in range(nu - 1, B + 1)):
                okR = False; print("FAIL sib", n)
        for l in range(0, k - 1):
            rhs = eBor(k + 1) * at(n - 1 - k, k + 1) + eBor(k) * (at(n - k, k + 1) - at(n - k, k - 1)) - eBor(l + 2) * at(n - 2 - l, k - 1) - eBor(l + 1) * at(n - 1 - l, k - 1)
            if not (src(n) / Eu >= rhs):
                okL = False; print("FAIL fold-L1", n, l)
print("fold-A:", okA, " fold-R:", okR, " fold-L1 (7.15):", okL, " (k=4, n<=%d)" % nmax)

# fold-T with real e (float on exact A)
ok4 = True
for k_ in (2, 3, 4, 5):
    A2 = A_table(30, k_ + 1)
    def atf(m, y):
        return math.exp(-m) * A2[(m, y - 1)] / math.factorial(m) if m >= 0 else 0.0
    for n in range(3, 26):
        for m in range(1, n - 1):
            if 2 * m >= n - 1:
                if atf(n - 2 - m, k_) * atf(m + 1, k_ + 1) < atf(n - m, k_) * atf(m - 1, k_ - 1) * (1 - 1e-12):
                    ok4 = False; print("FAIL fold-T", k_, n, m)
print("fold-T:", ok4)

# (7.10) and pi-sharp bound for k=4
k = 4; A = A_table(40, k + 1)
s = lambda m, y: F(A[(m, y - 1)], p(m))

def pi(m, j):
    return F(comb(m, j) * j ** (j - 1) * p(m - j), p(m))

ok5 = True
for q in range(2, k + 3):
    m = k + q - 1
    lhs = 1 - s(k + q - 1, k)
    rhs = sum(pi(m, j) * (F(j - k, j) + F(k, j) * (1 - s(j - 1, k))) for j in range(k + 1, k + q))
    if lhs != rhs:
        ok5 = False; print("FAIL (7.10)", q, lhs, rhs)
    pis = F(q * (q - 1), 2 * (k + 1))
    if lhs > pis:
        ok5 = False; print("FAIL pi-sharp", q)
print("(7.10) and pi-sharp bound:", ok5)

# borel-monotone (나): m^{3/2} Bor(m+1) increasing, check numerically
lBor = lambda m: -m + (m - 1) * math.log(m) - math.lgamma(m + 1)
print("borel (na):", all(1.5 * math.log(m + 1) + lBor(m + 2) > 1.5 * math.log(m) + lBor(m + 1) for m in range(1, 150)))
