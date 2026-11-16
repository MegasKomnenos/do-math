# 검토전체19 M3: 장5A 수치 검산
# 실행: python -I 검토전체19_M3_5A검산.py > 출력파일
import math
from fractions import Fraction
from mpmath import mp, mpf, quad, exp, sqrt, pi, e as E_, findroot, inf

mp.dps = 30
out = []
def P(*a):
    out.append(" ".join(str(x) for x in a))

# (a) 위치 수 5.1
cnt1 = sum(n - 2 - (-(-(n - 1) // 2)) for n in range(5, 20001))
cnt2 = sum(n - 2 - (-(-(n - 1) // 2)) for n in range(20001, 50001))
P("positions 5..20000:", cnt1, "(claim 99,970,002)")
P("positions 20001..50000:", cnt2, "(claim 524,955,000)")
P("sum 94192042+5777960 =", 94192042 + 5777960)
# 둘째 조각 비교 수
cmp2 = sum((-(-n // 2)) - 1 for n in range(10001, 20001))
P("comparisons 10001..20000:", cmp2, "(claim 74,995,000)")

# (c) cr_k (1+5/(2k)+2/k^2), k=1..9
vals = []
for k in range(1, 10):
    cr = Fraction(k + 1, k) ** (k - 2)
    v = cr * (1 + Fraction(5, 2 * k) + Fraction(2, k * k))
    vals.append(float(v))
P("cr_k*(1+5/2k+2/k^2) k=1..9:", [round(v, 5) for v in vals], "all > 87/32=", 87 / 32, all(v > 87 / 32 for v in vals))
P("e < 65/24+1/100 ?", math.e < 65 / 24 + 0.01, " 65/24+0.01 < 87/32 ?", 65 / 24 + 0.01 < 87 / 32)

# (d) L(10^4)
def M(i):
    return quad(lambda y: y**i * exp(-y - y**2 / 2), [0, inf])
M26 = quad(lambda y: y**2 * exp(-y - y**2 / 2), [0, 6])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y^2+y-i=0
    y0 = (-1 + sqrt(1 + 4 * i)) / 2
    return y0**i * exp(-y0 - y0**2 / 2)
Ms = [M(i) for i in range(6)]
C1 = 2 * Mstar(2) + Ms[3] / 2 + Ms[5] / 3
C2 = Mstar(3) / 2 + Mstar(5) / 3 + Ms[4] / 2
C3 = Mstar(4) / 2 + Ms[3] / 6
C4 = Mstar(3) / 6
def L(r):
    s = sqrt(r)
    num = M26 - C1 / s - C2 / s**2 - C3 / s**3 - C4 / s**4
    den = Ms[1] + (Ms[0] + exp(-mpf(1) / 2)) / s + 1 / s**2
    return num / den
P("L(10^4) =", L(10**4), "(claim >= 0.845204)")
P("M_i:", [mp.nstr(m, 8) for m in Ms], "M2^(6):", mp.nstr(M26, 8))

# Pc constants
P("sqrt(3pi/2) =", sqrt(3 * pi / 2), " 1/2+1.690408-sqrt(3pi/2) =", mpf(1) / 2 + mpf("1.690408") - sqrt(3 * pi / 2))
s = mpf(100)
br = 1 / (3 * s) + 8 / (3 * s**2) + mpf("2.507") / s**2 + (1 + mpf("2.1709") * s) / s**3
P("bracket at s=100:", br, "(claim < 0.0041)")
P("sqrt(pi/2) =", sqrt(pi / 2))

# (f) m(n)
def mfun(n):
    best = 170
    m = 171
    while m**1.5 + 9 * m <= n:
        best = m
        m += 1
    return best
P("m(20001)=", mfun(20001), " m(50001)=", mfun(50001))
P("597^1.5+9*597 =", 597**1.5 + 9 * 597, " 598:", 598**1.5 + 9 * 598)

# (g) 0.28 product (old-5-7), omitted-tail analog
r = 529
prod = (9 / 16) * (169 / 400) * (144 / 121) * (88 / 1443) * (5 / 2 + 9 / (2 * r))**3
P("ratio bound old-5-7:", prod, "(claim < 0.28)")
P("27.14^3 =", 27.14**3, " 27.14^2 =", 27.14**2, " floor(0.75*736.58)=", math.floor(0.75 * 27.14**2))
P("(149/200)^3 =", (149 / 200)**3, " (16/25)^2 =", (16 / 25)**2, " (3/4)^3=", 0.75**3, " (13/20)^2=", 0.65**2)
P("(3/4)^1.5 =", 0.75**1.5, " 27/4/27.14 =", 27 / 4 / 27.14)
P("3/4 - 1/736.5 =", 0.75 - 1 / 736.5, " 149/200=", 149 / 200)

# (h) parity-tail rq_*
rqs = (13 / 20) * (1 + 3 / 529) / 23
P("rq_* =", rqs, "< 1/12 =", 1 / 12, rqs < 1 / 12)

# (i) kernel-bounds m=1
P("2sqrt2/e =", 2 * math.sqrt(2) / math.e, " 26/25=", 1.04, " 181/174=", 181 / 174, " sqrt2>181/128?", math.sqrt(2) > 181 / 128)
# 312m^2-374m+25 at m=2
P("312*4-374*2+25 =", 312 * 4 - 374 * 2 + 25)

# (j) omitted-tail (나) constants
P("(9/5)(1+1/598)/sqrt(598) =", 1.8 * (1 + 1 / 598) / math.sqrt(598))
P("12/(110e) =", 12 / (110 * math.e), " 1/24=", 1 / 24)
P("(12/11)^1.5*(1+1/598) =", (12 / 11)**1.5 * (1 + 1 / 598))
P("log10(1.15*598^3)=", math.log10(1.15 * 598**3), " 598*log10(24)=", 598 * math.log10(24))

# (k) 5.4 theorem old-5-12 constants
P("966^1.5=", 966**1.5, " 965^1.5=", 965**1.5, " 1.5*20001=", 1.5 * 20001)
P("(5/9)sqrt(598)=", 5 / 9 * math.sqrt(598))
P("rq bounds:", 1.2 / math.sqrt(598), 1.5 / math.sqrt(833), 1.8 / math.sqrt(966), " 1/16=", 1 / 16)
P("1/sqrt(598)=", 1 / math.sqrt(598))
P("833^1.5=", 833**1.5, " 832^1.5=", 832**1.5, " 1.2*20001=", 1.2 * 20001)
P("1/(1+9/sqrt(598))=", 1 / (1 + 9 / math.sqrt(598)))
P("(9/5)^(2/3)=", 1.8**(2 / 3), " 10*(1/2)^(2/3)=", 10 * 0.5**(2 / 3))

# (l) 14365, 9829
P("sum r-1, r=2..170:", sum(r - 1 for r in range(2, 171)), " 9999-171+1=", 9999 - 171 + 1)

# (m) Bernoulli check e^{1/(24m-1)} <= 1+1/(24m-2)
P("exp(1/23)=", math.exp(1 / 23), " 1+1/22=", 1 + 1 / 22)

# (n) hb coefficient check for small d: V_d(rho,...,rho) vs formula
tw = {1: Fraction(1)}
for j in range(2, 12):
    tw[j] = Fraction((j - 1)**(j - 1), math.factorial(j))
# hb_d(rho) polynomial via recursion hb_d = (1+rho) hb_{d-1} + sum_{j>=2} tw_j hb_{d-j}
# represent as list of Fraction coefficients
def padd(a, b):
    n = max(len(a), len(b)); return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]
def pscale(a, c):
    return [c * x for x in a]
hb = {0: [Fraction(1)]}
for d in range(1, 9):
    cur = padd(hb[d - 1], [Fraction(0)] + hb[d - 1])  # (1+rho) hb_{d-1}
    for j in range(2, d + 1):
        cur = padd(cur, pscale(hb[d - j], tw[j]))
    hb[d] = cur
ok = True
for d in range(1, 9):
    for j in range(0, d + 1):
        f = Fraction((j + 1) * (d + 1)**(d - j - 1), math.factorial(d - j)) if d - j - 1 >= 0 else Fraction(1)
        if hb[d][j] != f:
            ok = False
            P("hb mismatch", d, j, hb[d][j], f)
P("hb_d coefficient formula check d<=8:", ok)

# (o) Gamma_d(y;n) recursion vs tile sum identity, small case
def pf(m):
    return (m + 1)**(m - 1) if m >= 1 else 1
def Gamma(d, y, n):
    G = [Fraction(1)]
    for dd in range(1, d + 1):
        val = Fraction(math.comb(n, dd) * pf(dd))
        for j in range(0, dd):
            val += y * math.comb(n - dd + j, j) * pf(j) * G[dd - 1 - j]
        G.append(val)
    return G[d]
def Vd(cos):
    d = len(cos)
    V = [Fraction(1)]
    for dd in range(1, d + 1):
        val = (1 + cos[dd - 1]) * V[dd - 1]
        for j in range(2, dd + 1):
            val += tw[j] * V[dd - j]
        V.append(val)
    return V[d]
ok2 = True
for n in range(3, 9):
    for d in range(0, n):
        y = Fraction(7, 3)
        lhs = Gamma(d, y, n)
        falling = Fraction(math.perm(n, d))
        rhs = falling * Vd([y / (n - i) for i in range(0, d)])
        if lhs != rhs:
            ok2 = False
            P("Gamma/tile mismatch", n, d, lhs, rhs)
P("Gamma_d = (n)_d V_d check n<=8:", ok2)

# (p) cut-rep 뒤 준비 문단의 급수 상수, 5.4.2 상자 배치
from mpmath import zeta, log as mlog
lm = lambda m: (2 + mpf(1) / m) * zeta(2 * m) / pi**(2 * m)
P("sum_{m>=5} 2m l_m 2^{2-2m} =", sum(2 * m * lm(m) * mpf(2)**(2 - 2 * m) for m in range(5, 40)), "(claim < 1e-6)")
P("log et(1/2) =", sum(lm(m) * mpf(4)**(-m) for m in range(1, 60)), "(claim < 0.127, D: 0.126775)")
P("l_1,l_2,l_3 =", lm(1), lm(2), lm(3), " 1/36=", 1 / mpf(36), " 1/405=", 1 / mpf(405))
P("10001^(-1/3) =", mpf(10001)**(-mpf(1) / 3), " -29*0.0015 =", mpf(10001)**(-mpf(1) / 3) - 29 * mpf("0.0015"))
P("0.0015/1.25^12 =", mpf("0.0015") / mpf("1.25")**12)
P("x range of old-5-7: 0.64^(2/3), 0.65^(2/3) =", mpf("0.64")**(mpf(2) / 3), mpf("0.65")**(mpf(2) / 3))

with open(__file__.replace(".py", "_출력.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n".join(out))
