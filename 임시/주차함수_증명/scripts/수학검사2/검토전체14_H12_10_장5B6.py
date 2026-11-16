# H12 검산 10: 부록 D 5B·6장 항목의 독립 재계산
import math, time
from fractions import Fraction as Fr
import mpmath as mp
t0 = time.time()
mp.mp.dps = 40

def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1

# ---------- D.theorem-U-constant 산술 ----------
c = 1 / mp.sqrt(2 * mp.pi)
G, m_ = mp.mpf('2.7323'), mp.mpf('0.8051')
A1 = 3 * c * (mp.mpf('8.133') + mp.mpf('10.301') * c); A2 = mp.mpf('1.5') * G * m_ * c * (mp.mpf('17.951') + mp.mpf('23.462') * c)
print("theorem-U: 3c(J_I+cY_I)=", mp.nstr(A1, 8), " 1.5 G m c(J_X+cY_X)=", mp.nstr(A2, 8), " sum=", mp.nstr(A1 + A2, 8), " (<=14.653, 35.952, 50.62)")
B1 = 3 * c * (mp.mpf('8.13091') + mp.mpf('10.29939') * c); B2 = mp.mpf('1.5') * G * m_ * c * (mp.mpf('17.94855') + mp.mpf('23.46002') * c)
print("   with computed bounds:", mp.nstr(B1, 8), mp.nstr(B2, 8), mp.nstr(B1 + B2, 8), " (14.6489, 35.9473, 50.5962)")
V0 = mp.mpf(1) / 3130
print("   T_max=(1+3V0)/(2+2V0)=", mp.nstr((1 + 3 * V0) / (2 + 2 * V0), 8), " <0.5004")

# ---------- D.theorem-D-base: b_{m,m-d} via excess-count recurrence ----------
M = 700; DMAX = 41
Ac = {}  # Ac[(n,l)] for l in 0..M-1, n in l+2..min(l+DMAX+1, M)
binom_cache = {}
def comb(n, k):
    return math.comb(n, k)
for l in range(1, M):
    for n in range(l + 2, min(l + DMAX + 2, M) + 1):
        s = sum(comb(n - 1, j) * (j - l) * p(j) * p(n - 1 - j) for j in range(l + 1, n))
        s += sum(Ac[(i, l)] * comb(n - 1, i) * p(n - 1 - i) * ((l + 1) + min(n - i, l + 1)) for i in range(l + 2, n))
        Ac[(n, l)] = s
print("excess columns done", round(time.time() - t0, 1), "s")
def Acf(n, l):
    if l >= n - 1: return 0
    return Ac[(n, l)]
def b_md(m, d):  # b_{m,m-d} = A^c_{m,m-d-1} - A^c_{m,m-d}
    return Acf(m, m - d - 1) - Acf(m, m - d)
# sanity vs last-car recurrence for small m
N = 40
cols = {}
for l in range(0, N):
    col = [1]
    for n in range(1, N + 1):
        col.append(sum(comb(n - 1, j) * min(j + 1, l + 1) * col[j] * col[n - 1 - j] for j in range(n)))
    cols[l] = col
def A_(n, l):
    if l < 0: return 0
    if l >= n - 1: return p(n)
    return cols[l][n]
bad = 0
for m in range(4, N + 1):
    for d in range(1, (m + 1) // 2 + 1):
        if m - d - 1 >= 1 and m <= 2 * (m - d - 1) + 4:
            if b_md(m, d) != A_(m, m - d) - A_(m, m - d - 1): bad += 1
print("b_{m,m-d} vs last-car (m<=40):", "OK" if bad == 0 else f"MISMATCH {bad}")
mp.mp.dps = 40
Psi = {}
acc = mp.mpf(0)
for j in range(1, DMAX + 1):
    acc += mp.mpf(j) ** j * mp.e ** (-j) / mp.factorial(j); Psi[j] = acc
pairs = 0; qmin = (mp.inf, None); qmax = (-mp.inf, None)
for m in range(4, M + 1):
    for d in range(1, DMAX + 1):
        if 8 * d ** 3 > m * m: break
        pairs += 1
        q = mp.mpf(m) * mp.mpf(b_md(m, d)) / (mp.mpf(p(m)) * Psi[d])
        if q < qmin[0]: qmin = (q, (m, d))
        if q > qmax[0]: qmax = (q, (m, d))
print("theorem-D base: pairs", pairs, "(16229); min q", mp.nstr(qmin[0], 12), qmin[1], "(0.85613376342.. (689,39)); max q", mp.nstr(qmax[0], 12), qmax[1], "(1.39176029617.. (4,1))")
q31 = mp.mpf(3) * mp.mpf(b_md(3, 1)) / (mp.mpf(p(3)) * Psi[1]); print("   (3,1): q=", mp.nstr(q31, 10), "(1.529033528)", " d_max(700)=", int((700 ** (2 / 3)) / 2))
print("time", round(time.time() - t0, 1))

# ---------- D.prop-W-thirteen ----------
def eRen(r1):  # e*Ren(r+1) = (r+1)^r/(e^r r!)
    r = r1 - 1
    return mp.mpf(r1) ** r / (mp.e ** r * mp.factorial(r))
k = 3131
mind = mp.inf
for d in range(1, 15):
    L = (k - 1) * (eRen(d + 1) - mp.mpf(60) * (d + 1) / (k + d))
    Rr = 2 * (1 + mp.fsum(eRen(r + 1) + mp.mpf(60) * (r + 1) / (k + d) for r in range(1, d)))
    if d <= 13: mind = min(mind, L - Rr)
    print("  d=%2d L=%9.2f R=%6.2f" % (d, float(L), float(Rr)))
print("prop-W: min(L-R) d<=13 =", mp.nstr(mind, 5), "(>=49.6)")

# ---------- D.tilt-sum-small-k ----------
def tilt_sum(k):
    base = Fr(k, k + 1) ** (k - 1)
    return sum(Fr(n ** (n - 1), math.factorial(n)) * base ** n for n in range(2, k + 2))
vals = {k: tilt_sum(k) for k in range(2, 61)}
print("tilt-sum: all<1:", all(v < 1 for v in vals.values()), " max at k=", max(vals, key=vals.get), vals[2], float(vals[2]))
for k in (3, 10, 20, 42, 43): print("   k=%d: %.6f" % (k, float(vals[k])))

# ---------- D.band-check 첫 셀 다섯 포락선 ----------
mp.mp.dps = 30
n = 50001; w0 = mp.mpf('0.71216')
la = mp.mpf(1) / 2; lb = mp.mpf(1) / 2 + mp.mpf(1) / 24000
rho0 = mp.mpf('0.75') * (mp.mpf('1.1') * lb * n) ** (mp.mpf(2) / 3) + 1
c1 = mp.mpf('1.5') * ((2 * lb - 1) * n + 2 * rho0) / (la * n * ((1 - lb) * n - rho0))
eps0 = mp.mpf('1.5') * rho0 * ((2 * lb - 1) * n + 2 * rho0) / ((la * n - 1) * ((1 - lb) * n - rho0))
hov = mp.mpf(0); z = 0
den = mp.sqrt(mp.floor(mp.mpf('0.3') * (1 - lb) * n - 1) - 1)
while True:
    term = (la - mp.mpf(1) / n) ** z * (1 - 2 / mp.sqrt(mp.pi) * mp.mpf(z) ** mp.mpf(1.5) / den)
    if term <= 0: break
    hov += term; z += 1
second = 1 - mp.sqrt(2 / mp.pi) * (mp.mpf('0.3') * (1 - lb) * n - 1) ** (-mp.mpf(1) / 2) - mp.mpf('0.3') * (1 - la) * n * (2 * mp.pi) ** (-mp.mpf(1) / 2) * ((n + 1) / (la * n * ((1 - lb) * n - rho0))) ** mp.mpf(1.5) * mp.e ** (mp.mpf(1) / (12 * (n + 1)))
top = (2 * mp.pi) ** (-mp.mpf(1) / 2) * (1 + mp.mpf(1) / n) ** mp.mpf(1.5) * la ** (-mp.mpf(1) / 2) * (1 - lb) ** (-mp.mpf(1.5)) * n ** (-mp.mpf(1) / 2) * mp.e ** (mp.mpf(1) / (12 * n))
Kt = la * mp.e ** (-1 / (12 * (mp.mpf('0.4') * (1 - lb) * n - 6 * (lb * n) ** (mp.mpf(2) / 3) + 1)) - 1 / (12 * la * n) - 1 / (12 * (n + 1)))
W = (2 * mp.pi) ** (-mp.mpf(1) / 2) * mp.mpf(2) / 3 * (rho0 + 1) ** mp.mpf(1.5) * c1 * (1 + rho0 / (la * n)) ** mp.mpf(1.5) * mp.e ** (eps0 + 1 / (12 * la * n))
ratio = hov * w0 * Kt * (2 * second - top) - W
print("band-check first cell: hov=", mp.nstr(hov, 8), " second=", mp.nstr(second, 8), " top=", mp.nstr(top, 6), " K=", mp.nstr(Kt, 8), " W=", mp.nstr(W, 6), " ratio=", mp.nstr(ratio, 10), "(1.3558739652)")
print("   cond 0.4(1-lb)n >= 6(lb n)^{2/3}+1:", mp.mpf('0.4') * (1 - lb) * n, ">=", 6 * (lb * n) ** (mp.mpf(2) / 3) + 1)
# O(25000)
Y = mp.mpf(25000)
O = 1 / Y ** 2 * mp.sqrt(12 / mp.pi) * Y ** (mp.mpf(1) / 3) * mp.sqrt(2 / Y) * (Y + 1)
print("O(25000)=", mp.nstr(O, 8), "  h0=0.0342 vs 25000^{-1/3}=", mp.nstr(mp.mpf(25000) ** (-mp.mpf(1) / 3), 6), " v_max=sqrt(6h0)=", mp.nstr(mp.sqrt(6 * mp.mpf('0.0342')), 6))
