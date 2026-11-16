# 검토전체17 K7b: 7.6–7.7절의 항등식·부등식을 작은 k에서 정확 유리수로 재현하고 상수를 다시 센다.
from fractions import Fraction as Fr
from math import comb, log, exp, sqrt, pi
import sys

out = []
def P(*a):
    out.append(" ".join(str(x) for x in a))

def build(M, L):
    A = [[0] * (L + 1) for _ in range(M + 1)]
    for l in range(L + 1):
        A[0][l] = 1
    for m in range(1, M + 1):
        for l in range(L + 1):
            A[m][l] = sum(comb(m - 1, j - 1) * min(j, l + 1) * A[j - 1][l] * A[m - j][l] for j in range(1, m + 1))
    return A

def pf(m):
    return (m + 1) ** (m - 1) if m >= 1 else 1

def g_exp(x):  # e^{g(x)} = (1+1/x)^{x-1}, exact rational for integer x
    return Fr(x + 1, x) ** (x - 1)

bad = 0
def chk(name, cond):
    global bad
    if not cond:
        bad += 1
        P("FAIL", name)

for k in [3, 4, 5, 6]:
    NMAX = 3 * k + 3
    A = build(NMAX, k + 1)
    for m in range(NMAX + 1):
        chk(f"p_m k={k} m={m}", A[m][min(m, k + 1)] == pf(m) if m - 1 <= k + 1 else True)
    def Aml(m, l):
        if l < 0:
            return 0
        return A[m][l] if l <= k + 1 else pf(m)
    def s(m, y):
        if y <= 0:
            return Fr(0)
        return Fr(Aml(m, y - 1), pf(m))
    def c(m, y):
        return s(m, y + 1) - s(m, y)
    def clp(m):
        return c(m, k) / s(m, k)
    def clm(m):
        return c(m, k - 1) / s(m, k)
    def mu(m):
        return clp(m) - clm(m)
    def Pn(n, j):
        return Fr(j * comb(n - 1, j - 1) * pf(j - 1) * pf(n - j), pf(n))
    def Pk(n, j):
        return Fr(min(j, k) * comb(n - 1, j - 1) * Aml(j - 1, k - 1) * Aml(n - j, k - 1), Aml(n, k - 1))
    def chi(n, j):
        v = Fr(0)
        if j == k:
            v += -Fr(1, k) * (1 - clm(n - k))
        if j > k:
            v += Fr(1, k) * (clp(j - 1) + clm(j - 1) + clp(n - j) + clm(n - j))
        ind = 1 if j > k else 0
        v += (1 + Fr(ind, k)) * clp(j - 1) * clp(n - j) + (1 - Fr(ind, k)) * clm(j - 1) * clm(n - j)
        return v
    def src(n):
        return sum(Pk(n, j) * chi(n, j) for j in range(1, n + 1))
    def inh(n):
        return sum(Pk(n, j) * (mu(j - 1) * (1 if k <= j - 1 <= 2 * k else 0) + mu(n - j) * (1 if k <= n - j <= 2 * k else 0)) for j in range(1, n + 1))
    def inh_lin(n):
        return Fr(1, k) * sum(Pk(n, j) * ((clp(j - 1) + clm(j - 1)) * (1 if k <= j - 1 <= 2 * k else 0) + (clp(n - j) + clm(n - j)) * (1 if k <= n - j <= 2 * k else 0)) for j in range(1, n + 1))
    def d(m):
        return Aml(m, k) - 2 * Aml(m, k - 1) + Aml(m, k - 2)
    def b(m, y):
        return Aml(m, y) - Aml(m, y - 1)
    def hz(N):
        return 1 - s(N + 1, k) / s(N, k)

    for n in range(2 * k + 1, NMAX + 1):
        nu = n - 2 * k
        # (7.13)
        chk(f"(7.13) k={k} n={n}", mu(n) == src(n) + sum(Pk(n, j) * (mu(j - 1) + mu(n - j)) for j in range(1, n + 1)))
        # Pk via s and Pn (7.4절 꼴)
        for j in range(1, n + 1):
            chk(f"Pk-form k={k} n={n} j={j}", Pk(n, j) == Fr(min(j, k), j) * Pn(n, j) * s(j - 1, k) * s(n - j, k) / s(n, k))
        # rw
        def rw(q):
            return Fr(k, k + 1 + q) * Pn(n, k + 1 + q) / Pn(n, k)
        chk(f"rw(nu)=1 k={k} n={n}", rw(nu) == 1)
        for q in range(0, k + nu - 1):
            chk(f"rw ratio k={k} n={n} q={q}", rw(q + 1) / rw(q) == g_exp(k + 1 + q) / g_exp(k + nu - 1 - q))
        chk(f"rw>=1 k={k} n={n}", all(rw(q) >= 1 for q in range(nu, k + nu)))
        # (7.22)
        lhs = k * s(n, k) * src(n)
        r22 = sum(Fr(k, j) * Pn(n, j) * ((c(j - 1, k - 1) + c(j - 1, k)) * s(n - j, k) + s(j - 1, k) * (c(n - j, k - 1) + c(n - j, k))) for j in range(k + 1, n + 1)) - Pn(n, k) * s(n - k, k - 1)
        chk(f"(7.22) k={k} n={n}", lhs >= r22)
        # (7.23)
        br1 = sum(rw(q) * (c(k + q, k - 1) + c(k + q, k)) for q in range(nu, k + nu)) - s(k + nu, k - 1)
        br2 = c(k + nu, k - 1) + s(k + nu, k + 1) - s(n, k) - s(n, k + 1)
        chk(f"(7.23a) k={k} n={n}", r22 >= Pn(n, k) * br1)
        chk(f"(7.23b) k={k} n={n}", br1 >= br2)
        # top-roots
        for U0 in range(0, k):
            mid = br2 + sum((rw(k + nu - 1 - U) - 1) * (s(n - 1 - U, k) - s(n - U, k)) for U in range(0, U0 + 1))
            last = s(n, k) * (sum((rw(k + nu - 1 - U) - 1) * hz(n - 1 - U) for U in range(0, U0 + 1)) - 1)
            chk(f"top-roots k={k} n={n} U0={U0}", br1 >= mid >= last)
        # apex^H identity
        apex = Fr(1, k) * (sum(Pk(n, j) * (clp(j - 1) + clm(j - 1)) for j in range(n - k + 1, n + 1)) - Pk(n, k) * (1 - clm(n - k)))
        chk(f"apex k={k} n={n}", k * s(n, k) * apex == Pn(n, k) * br1)
        # 7.7절: 분할 무게, Left, (7.24)
        def w(m):
            return Fr(comb(n - 1, m) * pf(m) * Aml(n - 1 - m, k - 1), Aml(n, k - 1))
        def pm(m):
            return Fr((k + 1) * b(m, k) - (k - 1) * b(m, k - 1), pf(m))
        Left = sum(w(m) * pm(m) for m in range(k, 2 * k + 1))
        for m in range(k, 2 * k + 1):
            chk(f"Pk=k s w k={k} n={n} m={m}", Pk(n, m + 1) == k * s(m, k) * w(m) if m + 1 <= n else True)
        chk(f"w nondecreasing k={k} n={n}", all(w(m + 1) >= w(m) for m in range(k, 2 * k)))
        if n >= 3 * k + 1:
            chk(f"(7.24) k={k} n={n}", inh_lin(n) + inh(n) == 2 * Left)
        if n <= 3 * k:
            KD = sum((k + n - m) * comb(n - 1, m) * pf(n - 1 - m) * d(m) for m in range(2 * k + 1, n))
            chk(f"(7.25) k={k} n={n}", Aml(n, k - 1) * (src(n) + inh(n)) == d(n) - KD)
        if n == 3 * k:
            u = w(n - k) * s(n - k, k + 1)
            Quad = sum(Pk(n, j) * ((1 + Fr(1, k)) * clp(j - 1) * clp(n - j) + (1 - Fr(1, k)) * clm(j - 1) * clm(n - j)) for j in range(k + 1, n + 1))
            Stem = Fr(1, k) * sum(Pk(n, j) * ((clp(j - 1) + clm(j - 1)) * (1 if j - 1 > 2 * k else 0) + (clp(n - j) + clm(n - j)) * (1 if n - j > 2 * k else 0)) for j in range(k + 1, n + 1))
            chk(f"(7.26) k={k}", src(n) + inh(n) == 2 * Left - u + Quad + Stem)
            chk(f"u/w_k telescope k={k}", u / w(k) == g_exp(2 * k) / g_exp(k) * s(2 * k, k + 1) / s(2 * k - 1, k))
            chk(f"Pk(3k,k)=k w A/p k={k}", Pk(n, k) == k * w(2 * k) * Fr(Aml(2 * k, k - 1), pf(2 * k)))
    P(f"k={k} done")

# explicit-bounds (나) numeric check
from math import lgamma
def Bor(dd):
    return exp(-dd + (dd - 1) * log(dd) - lgamma(dd + 1))
def Ren(j):
    return exp(j * log(j) - j - lgamma(j + 1))
for m in [5, 20, 100, 400]:
    sg = m * log(m / (m + 1)) + 1
    chk(f"sg bounds m={m}", 0 <= sg <= 1 / (2 * (m + 1)) + 1 / (6 * m * (m + 1)))
    for U in range(0, m):
        j = m - U
        from math import lgamma
        lPmU = (lgamma(m) - lgamma(U + 1) - lgamma(m - U)) + (m - U - 1) * log(m - U) + (U - 1) * log(U + 1) - (m - 1) * log(m + 1)
        lBor = -(U + 1) + (U) * log(U + 1) - lgamma(U + 2)
        lRen = j * log(j) - j - lgamma(j + 1)
        chk(f"EB-na1 m={m} U={U}", lPmU <= lBor + sg + log((m + 1) / (m - U)) + 1e-9)
        chk(f"EB-na2 m={m} j={j}", lPmU <= lRen + sg + log(m + 1) - 2 * log(m + 1 - j) + 1e-9)
        chk(f"old-2-32 m={m} U={U}", lPmU >= lBor - 1e-9)

# 상수
P("sum_{d<=301} Bor =", sum(Bor(dd) for dd in range(1, 302)), " 1-0.8/sqrt(301)=", 1 - 0.8 / sqrt(301))
P("0.9538/0.398943 =", 0.9538 / 0.398943, " (2pi)^-1/2 =", (2 * pi) ** -0.5)
P("0.14*2.38*0.9999 =", 0.14 * 2.38 * 0.9999, " 0.14*301 =", 0.14 * 301)
n0 = 6263
sg0 = n0 * log(n0 / (n0 + 1)) + 1
P("sg_6263 =", sg0, " e^-sg =", exp(-sg0))
k0 = 3131
P("D_k(2) at 3131 =", 0.08329 * sqrt(k0) - 2 - 42.14 / k0, " 0.33316/4=", 0.33316 / 4)
P("(1+1/k)^(4/3) at 3131 =", (1 + 1 / k0) ** (4 / 3), " 2/k=", 2 / k0, " 1.001+42.14/k=", 1.001 + 42.14 / k0)
u = k0 ** (1 / 6)
P("k^(1/6) =", u)
P("right end value at 3131 =", 0.33316 * (sqrt(k0) - 2 * u + 1 / u) - 1.0005 * k0 ** (1 / 3) - 1.0145)
P("derivative in u at 3131 =", 0.33316 * (3 * k0 ** (1 / 3) - 2 - k0 ** (-1 / 3)) - 2.001 * u)
# 직접: D_k(x) on [2, nPD/k] for several k by sampling
import math
def nPD(k):
    return math.ceil((k + 1) ** (4 / 3)) + k + 1
def Gk(k, n):
    sg = n * log(n / (n + 1)) + 1
    return 0.14 / n * (2.38 * k ** 1.5 * (n - k + 1) ** 2 / (exp(sg) * n * (n + 1)) - 301)
for k in [3131, 3200, 5000, 10000, 100000]:
    mn = min(Gk(k, n) for n in range(2 * k + 1, nPD(k)))
    P(f"min G_k(n) on [2k+1,nPD-1] k={k}: {mn:.4f}  nPD={nPD(k)}  nPD/k={nPD(k)/k:.3f}  1.0005k^(1/3)+1.001={1.0005*k**(1/3)+1.001:.3f}  3k+2<=nPD: {3*k+2<=nPD(k)}")
# threshold-unit-ratio constants
k1 = 6667
j0 = int(0.3 * k1)
P("j0 =", j0, " exact -j0(j0+1)/(2(k+1+j0)) =", -j0 * (j0 + 1) / (2 * (k1 + 1 + j0)), " text bound -(0.3k-1)(0.3k)/(2(1.3k+1)) =", -(0.3 * k1 - 1) * (0.3 * k1) / (2 * (1.3 * k1 + 1)))
P("1+1.5 log k - ... =", 1 + 1.5 * log(k1) - (0.3 * k1 - 1) * (0.3 * k1) / (2 * (1.3 * k1 + 1)))
P("e^0.3 =", exp(0.3), " e^(3/(2k)) =", exp(3 / (2 * k1)), " 1.00023*1.34986 =", 1.00023 * 1.34986)
P("2*0.7654-1.3502 =", 2 * 0.7654 - 1.3502)
P("(1+1/k)^j0 =", (1 + 1 / k1) ** j0, " <= e^0.3:", (1 + 1 / k1) ** j0 <= exp(0.3))
# n^flat > 3k constants
P("1003/e =", 1003 / math.e)
# s_{2k+1}(k), s_{2k+1}(k+1), c_{k+1}(k-1) for the exposition remark
for k in [10, 20, 40, 60]:
    A = build(2 * k + 1, k)
    s1 = Fr(A[2 * k + 1][k - 1], pf(2 * k + 1))
    s2 = Fr(A[2 * k + 1][k], pf(2 * k + 1))
    s3 = Fr(A[k + 1][k], pf(k + 1))
    ck = Fr(A[k + 1][k - 1] - A[k + 1][k - 2], pf(k + 1))
    P(f"k={k}: s_(2k+1)(k)={float(s1):.4f} s_(2k+1)(k+1)={float(s2):.4f} s_(k+1)(k+1)={float(s3):.4f} c_(k+1)(k-1)={float(ck):.4f} bracket(7.23,nu=1)={float(ck+s3-s1-s2):.4f}")

P("BAD =", bad)
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out) + "\n")
