# 검토전체9 O3: 5.1절·5.2절 수치 검산 (counts, Cayley ratio, tilted birthday constants)
from fractions import Fraction
from math import ceil, comb, factorial, exp, e, pi, sqrt, log
import mpmath as mp

def kn(n): return (n + 1) // 2  # ceil(n/2)

# 둘째 조각 비교 수: 10001<=n<=20000, k=2..k_n
c2 = sum(kn(n) - 1 for n in range(10001, 20001))
print("second piece comparisons:", c2, "(text 74,995,000)")

# 넷째 조각 위치 수: 5<=n<=20000, ceil((n-1)/2)<=ell<=n-3
c4 = sum(max(0, (n - 3) - ceil((n - 1) / 2) + 1) for n in range(5, 20001))
print("fourth piece positions:", c4, "(text 99,970,002)")

# 정리 5-2: 20001<=n<=50000 positions same range; adjacent pairs ell..n-2
c5 = sum((n - 3) - ceil((n - 1) / 2) + 1 for n in range(20001, 50001))
c5p = sum((n - 2) - ceil((n - 1) / 2) + 1 for n in range(20001, 50001))
print("5-2 positions:", c5, "(text 524,955,000); adjacent pairs:", c5p, "(D 524,985,000)")
c4p = sum((n - 2) - ceil((n - 1) / 2) + 1 for n in range(5, 20001))
print("n<=20000 adjacent pairs:", c4p, "(D 99,989,998)")

# 첫째 조각: 행 인증 501<=k<=4999, n<=10000
c1row = sum(max(0, min(kn(n) - 1, 4999) - 500) for n in range(12, 10001))
print("row cert 501..4999:", c1row, "(D 20,245,500)")
# 열 2..120 direct
c1col = sum(10000 - max(2 * k + 1, 12) + 1 for k in range(2, 121))
print("col 2..120 direct:", c1col, "(D 1,175,466)")
# 열 인증 121..500
def B(k): return ceil(k * k / 4)
d161 = sum(2 * B(k) - 2 * k for k in range(161, 501))
r161 = sum(B(k) + 1 for k in range(161, 501))
d121 = sum(2 * B(k) - 2 * k for k in range(121, 161))
r121 = sum(B(k) + 1 for k in range(121, 161))
print("col cert 161..500 direct/ratio:", d161, r161, "(D 19,982,310 / 10,103,865)")
print("col cert 121..160 direct/ratio:", d121, r121, "(D 386,260 / 198,790)")
# k>=142 covers n<=10000?
print("2B(141)=", 2 * B(141), " 2B(142)=", 2 * B(142), " 2B(121)=", 2 * B(121))

# Newton polynomial count
print("Newton count:", sum(r - 1 for r in range(2, 171)), "(text 14,365)")

# Cayley ratio small k
for k in range(1, 10):
    cr = Fraction(k + 1, k) ** (k - 2)
    val = cr * (1 + Fraction(5, 2 * k) + Fraction(2, k * k))
    print(k, float(val), val > Fraction(87, 32))
print("e < 65/24+1/100 =", e < 65 / 24 + 0.01, 65 / 24 + 0.01, "< 87/32:", 65 / 24 + 0.01 < 87 / 32)

# m(n)
def mfun(n):
    m = 170
    for mm in range(171, 100000):
        if mm ** 1.5 + 9 * mm <= n:
            m = mm
        else:
            break
    return m
print("m(20001)=", mfun(20001), " m(50001)=", mfun(50001))

# tw log-convexity
def tw(j): return Fraction(1) if j == 1 else Fraction((j - 1) ** (j - 1), factorial(j))
rat = [tw(j + 1) / tw(j) for j in range(1, 15)]
print("tw ratios nondecreasing:", all(rat[i] <= rat[i + 1] for i in range(len(rat) - 1)), [float(x) for x in rat[:5]])
# e^{-T} coefficients check via series
mp.mp.dps = 30
N = 10
# T(x) = sum j^{j-1} x^j / j!
T = [mp.mpf(0)] + [mp.mpf(j) ** (j - 1) / mp.factorial(j) for j in range(1, N + 1)]
# exp(-T) series
def series_exp(a, N):
    # a[0]=0
    out = [mp.mpf(0)] * (N + 1); out[0] = mp.mpf(1)
    # exp via recurrence: b' = a' b
    for n in range(1, N + 1):
        s = mp.mpf(0)
        for k in range(1, n + 1):
            s += k * a[k] * out[n - k]
        out[n] = s / n
    return out
negT = [-t for t in T]
E = series_exp(negT, N)
print("e^{-T} coeffs vs -tw:", [mp.nstr(E[j] + tw(j), 8) for j in range(1, 7)])

# hb_d coefficient formula check: hb_d(rho)=V_d(rho,...,rho)
def hb_coeffs(d):
    # recursion hb_d = (1+rho) hb_{d-1} + sum_{j>=2} tw_j hb_{d-j}; as polynomials in rho (list of Fractions)
    H = [[Fraction(1)]]
    for dd in range(1, d + 1):
        poly = [Fraction(0)] * (dd + 1)
        prev = H[dd - 1]
        for i, c in enumerate(prev):
            poly[i] += c; poly[i + 1] += c
        for j in range(2, dd + 1):
            for i, c in enumerate(H[dd - j]):
                poly[i] += tw(j) * c
        H.append(poly)
    return H[d]
for d in [1, 2, 3, 5, 8]:
    hc = hb_coeffs(d)
    formula = [Fraction((j + 1) * (d + 1) ** (d - j - 1), factorial(d - j)) if j < d else Fraction(1) for j in range(d + 1)]
    print("hb", d, hc == formula, sum(hc) == Fraction((d + 1) ** d, factorial(d)))

# Gamma_d(y;n) vs (n)_d V_d(y/n,...,y/(n-d+1)) check
def Gamma(d, y, n):
    p = lambda m: (m + 1) ** (m - 1) if m >= 1 else 1
    G = [Fraction(1)]
    for dd in range(1, d + 1):
        s = Fraction(comb(n, dd) * p(dd))
        for j in range(dd):
            s += y * comb(n - dd + j, j) * p(j) * G[dd - 1 - j]
        G.append(s)
    return G[d]
def Vd(cos):
    d = len(cos)
    V = [Fraction(1)]
    for dd in range(1, d + 1):
        s = (1 + cos[dd - 1]) * V[dd - 1]
        for j in range(2, dd + 1):
            s += tw(j) * V[dd - j]
        V.append(s)
    return V[d]
def falling(n, d):
    r = 1
    for i in range(d): r *= (n - i)
    return r
for (d, y, n) in [(3, 5, 9), (4, 7, 12), (6, 11, 20)]:
    lhs = Gamma(d, Fraction(y), n)
    rhs = falling(n, d) * Vd([Fraction(y, n - i + 1) for i in range(1, d + 1)])
    print("Gamma=V", d, y, n, lhs == rhs)

# lemma-L constants and L(10^4)
mp.mp.dps = 30
f = lambda i: (lambda y: y ** i * mp.exp(-y - y * y / 2))
M = [mp.quad(f(i), [0, mp.inf]) for i in range(6)]
M26 = mp.quad(f(2), [0, 6])
Mstar = [None] + [mp.findroot(lambda y: i - y - y * y, 1.0) for i in range(1, 6)]
Mstar = [None] + [f(i)(Mstar[i]) for i in range(1, 6)]
C1 = 2 * Mstar[2] + M[3] / 2 + M[5] / 3
C2 = Mstar[3] / 2 + Mstar[5] / 3 + M[4] / 2
C3 = Mstar[4] / 2 + M[3] / 6
C4 = Mstar[3] / 6
def L(r):
    s = mp.sqrt(r)
    num = M26 - C1 / s - C2 / s ** 2 - C3 / s ** 3 - C4 / s ** 4
    den = M[1] + (M[0] + mp.exp(-0.5)) / s + 1 / s ** 2
    return num / den
print("M:", [mp.nstr(x, 10) for x in M], "M2^(6):", mp.nstr(M26, 10))
print("Mstar:", [mp.nstr(x, 10) for x in Mstar[1:]])
print("L(10^4)=", mp.nstr(L(10 ** 4), 10), " (text >= 0.845204)")
print("sqrt(3pi/2)=", mp.nstr(mp.sqrt(3 * mp.pi / 2), 10), " sqrt(pi/2)=", mp.nstr(mp.sqrt(mp.pi / 2), 10))
print("1/2+2*0.845204-sqrt(3pi/2)=", mp.nstr(mp.mpf('0.5') + 2 * mp.mpf('0.845204') - mp.sqrt(3 * mp.pi / 2), 10))
s = 100
br = 1 / (3 * s) + 8 / (3 * s * s) + 2.507 / (s * s) + (1 + 2.1709 * s) / s ** 3
print("bracket at s=100:", br)

# tilted birthday mean direct for r=171 at rho_r, compare with Pc
def tm(r, rho):
    d = r - 1
    Nu = mp.mpf(0); De = mp.mpf(0); bt = mp.mpf(1)
    for j in range(0, d + 1):
        w = (j + 1) * rho ** j * bt
        Nu += j * w; De += w
        bt *= (1 - mp.mpf(j + 1) / r)
    return Nu / De
def Pc(k, r, eb):
    return k * (mp.mpf(1) / (2 * r) - mp.mpf(1) / (3 * r * r)) - mp.mpf(5) / 2 + 2 * eb * (1 - mp.mpf(1) / k) - mp.mpf(k) / (k - 1) * (1 + mp.sqrt(3 * mp.pi * (r - 1) / 2))
for r in [171, 200, 500, 1000, 5000, 9999, 10000, 20000]:
    kr = int(mp.ceil(mp.mpf(r) ** 1.5 + 8 * r))
    rho = mp.mpf(kr) / (kr + r)
    t = tm(r, rho)
    print("r", r, "k_r", kr, "tm", mp.nstr(t, 8), "tm/s", mp.nstr(t / mp.sqrt(r), 8), "Pc", mp.nstr(Pc(kr, r, t), 8))
# r=170 check: does Pc fail?
for r in [100, 150, 170]:
    kr = int(mp.ceil(mp.mpf(r) ** 1.5 + 8 * r))
    rho = mp.mpf(kr) / (kr + r)
    t = tm(r, rho)
    print("r", r, "k_r", kr, "Pc", mp.nstr(Pc(kr, r, t), 8))
