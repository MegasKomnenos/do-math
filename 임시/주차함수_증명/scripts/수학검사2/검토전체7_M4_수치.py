# 검토전체7 M4: 장5B의 수치 상수와 작은 경우의 항등식·부등식을 다시 센다.
# python -I 로 돌린다. 외부 패키지 없음.
import math
from fractions import Fraction
from functools import lru_cache

LG = math.lgamma

def logBor(m):  # log Bor(m) = -m + (m-1) log m - log m!
    return -m + (m - 1) * math.log(m) - LG(m + 1)

def Bor(m):
    return math.exp(logBor(m))

def logBT(z, D):  # Borel–Tanner: (z/D) e^{-D} D^{D-z}/(D-z)!
    return math.log(z) - math.log(D) - D + (D - z) * math.log(D) - LG(D - z + 1)

def logpi(n, t):  # pi_n(t) = Bor(n+1-t)Bor(t)/Bor(n+1)
    return logBor(n + 1 - t) + logBor(t) - logBor(n + 1)

def g(x):
    return (x - 1) * math.log(1 + 1 / x)

print("=== 5.5.2: varrho_0 <= 0.75(1.1y)^{2/3}+1, and t_0 <= n for W# positions ===")
def t0(y):
    t = y + 2
    while not (y <= (t - 1) - math.floor(0.75 * (t - 1) ** (2 / 3))):
        t += 1
    return t
for y in [25001, 25002, 30000, 33334, 40000, 100000, 10**6]:
    r0 = t0(y) - 1 - y
    print(f"y={y}: varrho0={r0}, bound={0.75*(1.1*y)**(2/3)+1:.2f}, ok={r0 <= 0.75*(1.1*y)**(2/3)+1}")
# y>=25000: t-1 <= 1.1 y with t = y+1+ceil(0.75(1.1y)^{2/3})
y = 25000
print("ceil(0.75(1.1*25000)^{2/3}) =", math.ceil(0.75 * (1.1 * y) ** (2 / 3)), "<= 0.1y =", 0.1 * y)
n = 50001
print("10((n+1)/2)^{2/3} =", 10 * ((n + 1) / 2) ** (2 / 3), "> 6n^{2/3}+2 =", 6 * n ** (2 / 3) + 2)

print("\n=== 5.5.5 (old-5-30): top_pi bounds and bracket > 0.2 ===")
n = 50001
v1 = (2 * math.pi) ** -0.5 * math.sqrt(2) * 3 ** 1.5 * (1 + 1 / n) ** 1.5 * n ** -0.5 * math.exp(1 / (12 * (n + 1)))
print("case y<=2n/3 bound:", v1, "<= 0.0133:", v1 <= 0.0133)
v2 = (2 * math.pi) ** -0.5 * (0.15) ** 1.5 * (1 + 1 / n) ** 1.5 * math.exp(1 / (12 * (n + 1)))
print("(0.15)^{3/2} =", 0.15 ** 1.5, "<= 0.0581:", 0.15 ** 1.5 <= 0.0581)
print("case y>2n/3 bound:", v2, "<= 0.0232:", v2 <= 0.0232)
v3 = math.exp(-2) * ((n + 1) / (n - 1)) ** 1.5 * math.exp(1 / (12 * (n - 1)))
print("pi_n(n-1) bound:", v3, "< 0.1354:", v3 < 0.1354)
print("e^-1 - 0.1354 - 0.0232 =", math.exp(-1) - 0.1354 - 0.0232)
# direct check of top_pi = (y-1) pi_n(y) over W# positions at n=50001 and a larger n
for n in [50001, 200000]:
    worst = 0
    for y in range((n + 1) // 2 + (n % 2 == 0), n):
        if n - y + 1 <= 10 * y ** (2 / 3):
            break
        tp = (y - 1) * math.exp(logpi(n, y))
        worst = max(worst, tp)
    print(f"n={n}: max top_pi over W# =", worst)

print("\n=== 5.5.8 right-part constants ===")
y = 33334
r_lo = 10 * y ** (2 / 3) - 1
print("10 y^{2/3}-1 at y=33334 =", r_lo, "-> r >= 10356:", r_lo >= 10355)  # r > 10y^{2/3}-1 so r>=ceil
r = 10356
print("0.2r-7.3 =", 0.2 * r - 7.3)
chi = 2064
hv = chi ** -0.5 * (2 / math.sqrt(math.pi) * (1 + 1 / chi) + 1 / math.sqrt(math.pi))
print("hv_chi * sqrt(chi) =", hv * math.sqrt(chi), "<= 1.6932:", hv * math.sqrt(chi) <= 1.6932)
t = y ** (1 / 3)
eh = 1.6932 * (t / 10 + 1) * (2 * t * t - 7.5) ** -0.5
print("eps_hov at y=33334:", eh, "<= 0.1573:", eh <= 0.1573)
print("sqrt(2/pi)/sqrt(2064) =", math.sqrt(2 / math.pi) / math.sqrt(2064), "<= 0.01757")
print("0.75*1.1^{2/3} =", 0.75 * 1.1 ** (2 / 3), "<= 0.7993")
rp1 = 10357
print("0.92007(r+1)-1 >= 0.9199(r+1) at r+1=10357:", 0.92007 * rp1 - 1 >= 0.9199 * rp1)
n = 50001
print("(n+1)/y max: (n/3+1)/(2n/3) =", (n / 3 + 1) / (2 * n / 3), "<= 1.50003")
c = (2 * math.pi) ** -0.5 * (1.50003 / 0.9199) ** 1.5
print("(2pi)^{-1/2}(1.50003/0.9199)^{3/2} =", c, "* e^{1/(12*50002)} =", c * math.exp(1 / (12 * 50002)), "<= 0.8308")
print("0.3*0.8308 =", 0.3 * 0.8308, "; 0.24924/sqrt(10357) =", 0.24924 / math.sqrt(10357), "<= 0.00245")
print("1-0.01757-0.00245 =", 1 - 0.01757 - 0.00245, ">= 0.9799")
print("e^{-c4} >= exp(-(1/156+1/(12*33334)+1/(12*50002))) =", math.exp(-(1 / 156 + 1 / (12 * 33334) + 1 / (12 * 50002))), ">= 0.9936")
# fourth constant
y = 33334
v = (0.7993 * y ** (2 / 3) + 2) ** 1.5 / y
print("(0.7993 y^{2/3}+2)^{3/2}/y at y=33334 =", v, "<= 0.7172:", v <= 0.7172)
rp1 = 10357
rho = 0.07993 * rp1 + 1
print("(r+1)/(r-varrho0) <=", rp1 / (rp1 - 1 - rho), "<= 1.0872")
print("eps0 <= 1.5 varrho0/(r+1-varrho0) <=", 1.5 * rho / (rp1 - rho), "<= 0.1305")
v = (1 + (0.7993 * y ** (2 / 3) + 1) / y) ** 1.5
print("(1+varrho0/y)^{3/2} <=", v, "<= 1.0376")
W = (2 * math.pi) ** -0.5 * (2 / 3) * 0.7172 * 1.5 * 1.0872 * 1.0376 * math.exp(0.1305 + 1 / 400008)
print("(r+1)/y * W <=", W, "<= 0.3678:", W <= 0.3678)
P = 0.8427 * 0.71216 * 0.9936 * 1.9366 - 0.3678
print("0.8427*0.71216*0.9936*1.9366-0.3678 =", P, ">= 0.7869:", P >= 0.7869)
lam = 2 / 3
print("0.7869*2/3 =", 0.7869 * lam, "; -(1-lam) =", -(1 - lam), "; total-2.5e-5 =", 0.7869 * lam - (1 - lam) - 2.5e-5, "> 0.191")

print("\n=== hover-tail / scaled-integrand constants ===")
print("4*sqrt2/sqrt(pi) =", 4 * math.sqrt(2) / math.sqrt(math.pi), "> 1")
h0 = 0.0342
print("h0^3 =", h0 ** 3, ">= 1/25000:", h0 ** 3 >= 1 / 25000)
umax = math.sqrt(6 * h0)
c2 = 1 / math.sqrt(2) - umax / 3
print("upsilon_max =", umax, "; c2 =", c2, ">= 0.556:", c2 >= 0.556)
f12 = c2 * 12 ** 1.5 - 12 - math.log(math.sqrt(2) * (1 + 6 * h0) * 12 / c2)
print("f(12) =", f12, "> 7:", f12 > 7, "; log arg =", math.sqrt(2) * (1 + 6 * h0) * 12 / c2)
print("f'(12) =", 1.5 * c2 * math.sqrt(12) - 1 - 1 / 12)
# bar_varrho(theta) <= e^{-theta} check for theta in [12, 60]
def ybar(th):
    return max(th / 2, th - h0)
def barrho(th):
    yy = ybar(th)
    num = math.sqrt(2) * th ** 1.5 * math.exp(-th * math.sqrt(yy) + min(th * th * h0, umax * th ** 1.5) / 3) * (1 + min(th * h0 * h0, 6 * h0))
    den = math.sqrt(yy) - min(th * h0, umax * math.sqrt(th)) / 3
    return num / den
ok = all(barrho(12 + i * 0.01) <= math.exp(-(12 + i * 0.01)) for i in range(0, 4800))
print("bar_varrho(theta) <= e^{-theta} on [12,60]:", ok, " at 12:", barrho(12), math.exp(-12))

print("\n=== stop-lower constants ===")
print("1.5*0.95^{-2.5} =", 1.5 * 0.95 ** -2.5, "<= 1.706")
print("(1+1.706*0.05)/11 =", (1 + 1.706 * 0.05) / 11, "<= 0.099")
print("(0.8^{-1.5}-1)/0.2 =", (0.8 ** -1.5 - 1) / 0.2, "<= 1.988")
print("(1+1.988*0.2)/11 =", (1 + 1.988 * 0.2) / 11, "<= 0.128")
print("4/sqrt(2pi) =", 4 / math.sqrt(2 * math.pi), "< 1.596")
# direct: Bor(U-i)/Bor(U) <= 1+2i/Y for Y=25000, j<=Y/4
Y = 25000
bad = 0
for j in [1, 10, 100, 1000, 3000, 6250]:
    U = Y + j + 1
    for i in range(1, j + 1):
        if math.exp(logBor(U - i) - logBor(U)) > 1 + 2 * i / Y:
            bad += 1
print("violations of Bor(U-i)/Bor(U)<=1+2i/Y at Y=25000:", bad)

print("\n=== band-inequality conditions at n=50001, lambda=2/3 ===")
n = 50001
y = 2 * n / 3
print("0.4(n-y) =", 0.4 * (n - y), ">= 6y^{2/3}+1 =", 6 * y ** (2 / 3) + 1)
print("0.75(1.1y)^{2/3}+1 =", 0.75 * (1.1 * y) ** (2 / 3) + 1, "<= 0.7(n-y) =", 0.7 * (n - y))
lb = 2 / 3
print("c4 denominator derivative 0.4(1-lb)-4 lb^{2/3} n^{-1/3} =", 0.4 * (1 - lb) - 4 * lb ** (2 / 3) * n ** (-1 / 3))
# reproduce the first-subinterval envelope values of D.band-check (n=50001)
la, lb = 0.5, 0.5 + 1 / 24000
w0 = 0.71216
rb = 0.75 * (1.1 * lb * n) ** (2 / 3) + 1
chi_lo = math.floor(0.3 * (1 - lb) * n - 1) - 1
hov = 0.0
z = 0
while True:
    term = (la - 1 / n) ** z * max(0.0, 1 - 2 / math.sqrt(math.pi) * z ** 1.5 * chi_lo ** -0.5)
    if term <= 0 and z > 0:
        break
    hov += term
    z += 1
second = 1 - math.sqrt(2 / math.pi) * (0.3 * (1 - lb) * n - 1) ** -0.5 - 0.3 * (1 - la) * n * (2 * math.pi) ** -0.5 * ((n + 1) / (la * n * ((1 - lb) * n - rb))) ** 1.5 * math.exp(1 / (12 * (n + 1)))
toppi = (2 * math.pi) ** -0.5 * (1 + 1 / n) ** 1.5 * la ** -0.5 * (1 - lb) ** -1.5 * n ** -0.5 * math.exp(1 / (12 * n))
K = la * math.exp(-1 / (12 * (0.4 * (1 - lb) * n - 6 * (lb * n) ** (2 / 3) + 1)) - 1 / (12 * la * n) - 1 / (12 * (n + 1)))
cb = 1.5 * ((2 * lb - 1) * n + 2 * rb) / (la * n * ((1 - lb) * n - rb))
eb = 1.5 * rb * ((2 * lb - 1) * n + 2 * rb) / ((la * n - 1) * ((1 - lb) * n - rb))
Wb = (2 * math.pi) ** -0.5 * (2 / 3) * (rb + 1) ** 1.5 * cb * (1 + rb / (la * n)) ** 1.5 * math.exp(eb + 1 / (12 * la * n))
print(f"hov>={hov:.7f} second>={second:.7f} top_pi<={toppi:.7f} K>={K:.7f} W<={Wb:.7f}")
print("ratio lower bound (first subinterval) =", hov * w0 * K * (2 * second - toppi) - Wb)

print("\n=== 5.5.3 (old-5-26) direct check at n=50001: WIN^V_0 vs closed bound ===")
for n, y in [(50001, 25001), (50001, 30000), (50001, 33334), (50001, 33335), (200000, 100001), (200000, 133334)]:
    T0 = t0(y)
    rho0 = T0 - 1 - y
    piy = math.exp(logpi(n, y))
    win = 0.0
    for t in range(y + 1, T0):
        win += (math.exp(logpi(n, t)) - piy) * math.exp(math.log(t - y) + logBor(t - y) + logBor(y) - logBor(t))
    win /= y
    c0 = 1.5 * (2 * y + 2 * rho0 - n) / (y * (n - y - rho0))
    e0 = 1.5 * rho0 * (2 * y + 2 * rho0 - 2 - n) / ((y + rho0 - 1) * (n - y - rho0 + 1))
    bound = piy / y * (2 * math.pi) ** -0.5 * (2 / 3) * (rho0 + 1) ** 1.5 * c0 * (1 + rho0 / y) ** 1.5 * math.exp(e0 + 1 / (12 * y))
    inW = (n - y + 1 > 10 * y ** (2 / 3))
    print(f"n={n} y={y} W#={inW} varrho0={rho0} WIN^V={win:.4e} bound={bound:.4e} ok={win <= bound}  ratio bound/(pi_n(y)/y)={bound/(piy/y):.4f}")

print("\n=== exact small cases: A_{n,l} via recurrence; old-5-19, old-5-27, old-5-22 identity, old-5-28, cor-L, old-5-25 ===")
@lru_cache(maxsize=None)
def A(n, l):
    if l < 0:
        return 0
    if n == 0:
        return 1
    s = 0
    for j in range(n):
        s += math.comb(n - 1, j) * min(j + 1, l + 1) * A(j, l) * A(n - 1 - j, l)
    return s

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

def s(m, y):  # survival prob
    if y <= 0:
        return Fraction(0)
    return Fraction(A(m, y - 1), p(m))

def c(m, Y):
    return Fraction(A(m, Y), p(m)) - Fraction(A(m, Y - 1), p(m))

def sT(t, Y):  # tree survival
    if t <= Y:
        return Fraction(1)
    return Fraction(Y, t) * s(t - 1, Y)

def x(t, y):
    return sT(t, y + 1) - 2 * sT(t, y) + sT(t, y - 1)

def piF(n, t):
    return Fraction(math.comb(n, t) * t ** (t - 1) * p(n - t), p(n))

# old-5-19
bad = 0
for n in range(5, 26):
    for y in range((n + 2) // 2, n):
        lhs = c(n, y) - c(n, y - 1)
        rhs = sum(piF(n, t) * x(t, y) for t in range(y, n + 1))
        if lhs != rhs:
            bad += 1
print("old-5-19 identity violations (5<=n<=25):", bad)
# old-5-27
bad = 0
for n in range(5, 26):
    for y in range((n + 2) // 2, n):
        P = sum(x(t, y) for t in range(y, n + 1))
        rhs = Fraction(-1, y) + sum(((y + 1) * c(m, y) - (y - 1) * c(m, y - 1)) / (m + 1) for m in range(y, n))
        if P != rhs:
            bad += 1
print("old-5-27 identity violations:", bad)
# old-5-22: check the Abel identity (equality form) and the inequality when IH holds
bad_id = 0; bad_ineq = 0; tested = 0
for n in range(6, 26):
    for y in range((n + 2) // 2, n):
        T0 = t0(y)
        if T0 > n:
            continue
        lhs = c(n, y) - c(n, y - 1)
        P = sum(x(t, y) for t in range(y, n + 1))
        tail = lambda s_: sum(x(t, y) for t in range(s_ + 1, n + 1))
        abel = piF(n, y) * P + sum((piF(n, s_ + 1) - piF(n, s_)) * tail(s_) for s_ in range(y, n))
        if abel != lhs:
            bad_id += 1
        IH = all(Fraction(A(m, y), 1) - A(m, y - 1) >= A(m, y - 1) - A(m, y - 2) for m in range(T0 - 1, n))
        if IH:
            tested += 1
            win = sum((piF(n, t) - piF(n, y)) * max(-x(t, y), 0) for t in range(y + 1, T0))
            pos = sum((piF(n, m + 1) - piF(n, T0 - 1)) * (c(m, y) + c(m, y - 1)) / (m + 1) for m in range(T0 - 1, n))
            if lhs < piF(n, y) * P - win + pos:
                bad_ineq += 1
print("old-5-22: Abel identity violations:", bad_id, "; inequality violations under IH:", bad_ineq, "of", tested)
# old-5-28
bad = 0; tested = 0
for m in range(2, 31):
    for d in range(1, m // 2 + 1):
        w = m - d
        z = Fraction(math.exp((d - 1) / w)) / (w + 1) + Fraction(3 * d, 2 * (w + 1) * (m + 1))
        if c(m + 1, w + 1) < (1 - z) * c(m, w) - Fraction(1, 10**12):
            bad += 1
        tested += 1
print("old-5-28 violations:", bad, "of", tested)
# cor-L
bad = 0
for y in range(2, 20):
    for n in range(y + 1, 2 * y + 2):
        P = sum(x(t, y) for t in range(y, n + 1))
        if y * P < -1 - Fraction(y * (y - 1), n) * c(n - 1, y - 1):
            bad += 1
print("cor-L violations (y<20):", bad)
# old-5-25: (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t)) = theta_t(y)/y, theta_t(y)=C(t,y) y^{y-1}(t-y)^{t-y}/t^{t-1}
bad = 0
for y in range(2, 16):
    for t in range(y + 1, 2 * y):
        theta = Fraction(math.comb(t, y) * y ** (y - 1) * (t - y) ** (t - y), t ** (t - 1))
        if max(-x(t, y), 0) > theta / y:
            bad += 1
print("old-5-25 violations:", bad)
# old-5-23/old-5-24 visit probability = theta_t(s) for s>t/2 (expected # of size-s subtrees): exact check that
# sum over chains is the same is implicit in old-5-25 check above.

print("\n=== exact moderate case Y=300: stop-lower upper bound, old-5-31, old-5-33 ===")
import sys
sys.setrecursionlimit(10000)
Y = 300
qmax = math.floor(6 * Y ** (2 / 3))
chiw = 2
mmax = 2 * Y + 1
# A_{j,l} for l in {Y-1, Y}, j<=mmax, iterative
def A_table(l, N):
    arr = [1] * (N + 1)
    for n_ in range(1, N + 1):
        s_ = 0
        for j in range(n_):
            s_ += math.comb(n_ - 1, j) * min(j + 1, l + 1) * arr[j] * arr[n_ - 1 - j]
        arr[n_] = s_
    return arr
AY = A_table(Y, mmax)
AYm1 = A_table(Y - 1, mmax)
_cY = [float(Fraction(AY[m] - AYm1[m], p(m))) if m >= 1 else 0.0 for m in range(mmax + 1)]
def cY(m):  # c_m(Y)
    return _cY[m]
# pi^0_n(Y): forests with all trees of size <= Y
F = [1] * (mmax + 1)
for n_ in range(1, mmax + 1):
    s_ = 0
    for t in range(1, min(n_, Y) + 1):
        s_ += math.comb(n_ - 1, t - 1) * t ** (t - 1) * F[n_ - t]
    F[n_] = s_
_pi0 = [float(Fraction(F[n_], p(n_))) for n_ in range(mmax + 1)]
def pi0(n_):
    return _pi0[n_]
_BT = {}
def BT(z, D):
    k_ = (z, D)
    if k_ not in _BT:
        _BT[k_] = math.exp(logBT(z, D))
    return _BT[k_]
# stop-lower upper bound: pi0_{Y+j}(Y) <= Pr(beta>j)
def Prbeta_gt(j):
    return 1 - sum(Bor(i) for i in range(1, j + 1))
bad = 0
for j in range(0, Y + 1):
    if pi0(Y + j) > Prbeta_gt(j) + 1e-12:
        bad += 1
print("stop-lower upper bound violations at Y=300, j<=300:", bad)
# old-5-31
def Lc(Y, r):
    tot = 0.0
    for z in range(1, r + 1):
        for D in range(z, r + 1):
            tot += z * BT(z, D) * math.exp(logBor(Y + r + 1 - D) - logBor(Y + r + 1)) * pi0(Y + r - D) * math.exp(-(z * (r + 1) - D * (z + 1) / 2) / Y)
    return tot / Y
_Lc = {r: Lc(Y, r) for r in range(1, Y + 2)}
bad = 0; worst = 1e9
for r in range(1, Y + 2):
    cv = cY(Y + r); lc = _Lc[r]
    if cv < lc:
        bad += 1
    worst = min(worst, cv / lc if lc > 0 else 1e9)
print("old-5-31 violations at Y=300 (1<=r<=Y+1):", bad, "; min c/Lc =", worst)
_Lc = {r: Lc(Y, r) for r in range(1, Y + 2)}
Lam = sum(Y / (Y + r + 1) * _Lc[r] for r in range(1, qmax + 1))
print("Lambda_w(300) =", Lam, " qmax =", qmax)
# old-5-33: c_m(Y) >= hov(Y/(m+1),chi) V(m,Y,chi,qmax) Lambda
def PrR_le(z, c_):  # Pr(R_z <= c_)
    if z == 0:
        return 1.0
    return sum(BT(z, D) for D in range(z, c_ + 1))
def hov(rho, chi):
    tot = 0.0
    for z in range(0, chi):
        tot += rho ** z * PrR_le(z, chi - 1)
    return tot
def V(m, Y, chi, q):
    return (2 * math.pi) ** -0.5 * ((m + 1) / ((Y + 1) * (m - Y))) ** 1.5 * math.exp(-1 / (12 * (m - chi - Y - q + 1)) - 1 / (12 * (Y + 1)))
for chiw in [2, 5, 20]:
    bad = 0; worst = 1e9
    for m in range(Y + qmax + chiw + 1, 2 * Y + 2):
        lhs = cY(m)
        rhs = hov(Y / (m + 1), chiw) * V(m, Y, chiw, qmax) * Lam
        if lhs < rhs:
            bad += 1
        worst = min(worst, lhs / rhs)
    print(f"old-5-33 at Y=300, chi_w={chiw}: violations={bad}, min lhs/rhs={worst:.4f}")
# hover-tail second bound sanity: Pr(R_z >= chi) <= z hv_chi for chi>=4
bad = 0
for chi in range(4, 60):
    hvv = chi ** -0.5 * (2 / math.sqrt(math.pi) * (1 + 1 / chi) + 1 / math.sqrt(math.pi))
    for z in range(1, 30):
        if 1 - PrR_le(z, chi - 1) > z * hvv + 1e-12:
            bad += 1
print("hover-tail second bound violations:", bad)
bad = 0
for chi in range(2, 60):
    for z in range(1, 30):
        if PrR_le(z, chi - 1) < max(0, 1 - 2 / math.sqrt(math.pi) * z ** 1.5 * (chi - 1) ** -0.5) - 1e-12:
            bad += 1
print("hover-tail first bound violations:", bad)
