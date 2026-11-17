# R8 (review 24): point evaluation (binary64, no rounding control - a sanity check only) of the
# formula (8.23) exactly as printed in chapter 8, with the stored table and test function read
# from the data folder (read-only).  Also: Omega(0), max|Omega'|, the window integral 0.744,
# and a sample of the table inequality z_i <= s^cf(xi_{i+1}).
import math, sys, os
import numpy as np
from mpmath import mp, mpf, zeta, sqrt as msqrt, exp as mexp, pi as mpi

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "원고_자료", "세션_재계산", "r030ffae_window", "work")
z = np.load(os.path.join(base, "qenv_fix_v.npy"))
xT = np.load(os.path.join(base, "qenv_fix_x.npy"))
wK = np.load(os.path.join(base, "wKrig.npy"))
xK = np.load(os.path.join(base, "xKrig.npy"))
print("table:", len(z), "points; x[0], x[-1] =", xT[0], xT[-1], " z[0], z[-1] =", z[0], z[-1])
print("Omega grid:", len(wK), "nodes; last node", xK[-1], " w[0] =", wK[0])
print("strictly decreasing table:", bool(np.all(np.diff(z) < 0)), " max z:", z.max())

def That(x):
    return np.interp(x, 0.0005 * np.arange(len(z)), z)

# test function: nodes (1-g) w, cumulative min, harmonic-mean slopes, one-sided three-point ends
def ramp(s):
    return np.where(s <= -0.1, 0.0, np.where(s < 0.1, (s + 0.1) ** 2 / 0.4, s))
h = 1.0 / (1e5) ** (2.0 / 3.0)
xi = np.arange(len(wK)) * h
g = np.minimum(1.0, 0.04 + 0.12 * ramp(xi - 1.0))
y = (1.0 - g) * wK
ycm = np.minimum.accumulate(y)
print("cumulative minimum changes entries:", int(np.sum(ycm != y)))
d = np.diff(ycm) / h
m = np.zeros(len(y))
m[1:-1] = np.where(d[:-1] * d[1:] > 0, 2 * d[:-1] * d[1:] / (d[:-1] + d[1:]), 0.0)
m[0] = 1.5 * d[0] - 0.5 * d[1]; m[-1] = 1.5 * d[-1] - 0.5 * d[-2]
if m[0] >= 0: m[0] = 0.0
if m[-1] >= 0: m[-1] = 0.0
def Omega(x):
    x = np.asarray(x, dtype=float)
    i = np.clip((x / h).astype(int), 0, len(y) - 2)
    t = (x - i * h) / h
    h00 = (1 + 2 * t) * (1 - t) ** 2; h10 = t * (1 - t) ** 2; h01 = t * t * (3 - 2 * t); h11 = t * t * (t - 1)
    return h00 * ycm[i] + h10 * h * m[i] + h01 * ycm[i + 1] + h11 * h * m[i + 1]
print("Omega(0) =", float(Omega(0.0)), " Omega(0.5,1,2,3,4,6) =", [round(float(Omega(v)), 3) for v in (0.5, 1, 2, 3, 4, 6)])
xs = np.linspace(0, 6, 600001)
om = Omega(xs)
print("Omega decreasing on sample:", bool(np.all(np.diff(om) <= 1e-15)), " max |Omega'| (sample secants):", float(np.max(-np.diff(om) / (xs[1] - xs[0]))))
print("window integral int_0^6 Omega sqrt(2x/pi) dx ~", float(np.sum(om * np.sqrt(2 * xs / math.pi)) * (xs[1] - xs[0])))

# sample of the table inequality with mpmath
mp.dps = 40
c = 1 / msqrt(2 * mpi)
z12, zm12, z32 = zeta(mpf(1) / 2), zeta(-mpf(1) / 2), zeta(mpf(3) / 2)
cpsi = -z12 + z32 / 12
def psilow(x): return c * (2 * msqrt(x) - cpsi + 1 / (2 * msqrt(x)) - x ** (-mpf(3) / 2) / 24)
def esc6600(x):
    k = mpf(6600); q = x * k ** (mpf(2) / 3); p = q - 1; n = k + q; kk = k + 1
    H = mpf(2) / 3 * p ** (mpf(3) / 2) + msqrt(p) / 2 + zm12 + 1 / (24 * msqrt(p))
    E = 2 * c * mexp(-1 / (12 * q)) * x ** (-mpf(1) / 2) * (1 + x * k ** (-mpf(1) / 3))
    R1 = mpf(3) / 2 * c * (2 * msqrt(p) - 1) * k ** (-mpf(2) / 3)
    R2 = mpf(15) / 8 * c * n ** (mpf(5) / 2) * H / (kk ** (mpf(7) / 2) * k ** (mpf(2) / 3))
    D1 = p / k ** (mpf(2) / 3); D2 = kk * msqrt(2 / mpi) / msqrt(p) / k ** (mpf(2) / 3)
    D3 = mpf(3) / 2 * kk * psilow(p) / ((n + 1) * k ** (mpf(2) / 3))
    return (E - R1 - R2) / (D1 + D2 - D3)
def scf(x):
    vals = []
    if x <= mpf("2.1"): vals.append(mexp(-mpf(4) / 3 * c * x ** (mpf(3) / 2)))
    if x >= 2: vals.append(esc6600(x))
    return max(vals)
worst = None
for i in list(range(0, 12001, 37)) + [0, 1, 3999, 4000, 4147, 4148, 4199, 4200, 12000]:
    marg = scf(mpf(i + 1) / 2000) - mpf(float(z[i]))
    if worst is None or marg < worst[0]: worst = (marg, i)
print("table sample: min margin s^cf(xi_{i+1}) - z_i =", mp.nstr(worst[0], 8), "at i =", worst[1])

# Borel quantities
NB = 400000
lg = np.array([math.lgamma(j + 1) for j in range(1, NB + 1)])
jj = np.arange(1, NB + 1, dtype=float)
Bor = np.exp(-jj + (jj - 1) * np.log(jj) - lg)
BorLe = np.concatenate(([0.0], np.cumsum(Bor)))
Psi = np.concatenate(([0.0], np.cumsum(jj * Bor)))

def LB(k, nu, detail=False):
    n = 2 * k + nu; N = k + nu
    qmax = int(math.floor(6 * k ** (2 / 3)))
    while (qmax + 1) ** 3 <= 216 * k * k: qmax += 1
    while qmax ** 3 > 216 * k * k: qmax -= 1
    qfb = int(math.floor((3 * (k - 1) / 4 - qmax - 3) / 8))
    if nu >= qmax + 1: case, qw, qs, low = "i", qmax, 6 * k ** (2 / 3), True
    elif nu - 1 >= k / 4: case, qw, qs, low = "ii", nu - 1, nu - 1, True
    else: case, qw, qs, low = "iii", qmax, None, False
    def Rlow(kk, nn):
        q = np.arange(1, qw + 1, dtype=float)
        x = (q - 1) / kk ** (2 / 3)
        return float(np.sum((1 - q * nn / (kk * (kk + nn))) ** 1.5 * kk / (kk + q) * (That(x) + Psi[:qw] * Omega(x))) / kk)
    fb = lambda lam: sum((lam * BorLe[qfb]) ** i for i in range(8))
    c0 = max((1 - 1 / k) ** (N - k + 1), 1 - math.exp(7 / 6) * N ** 1.5 / (4 * (2 * math.pi) ** -0.5 * k * (2 * k - 1 - N)))
    hz = lambda kk, nn: kk / (kk + nn) - kk / (2 * kk - 1)
    LOWk = LOWk1 = 0.0
    if low:
        if nu >= qfb + 2:
            La = k / (n - k) - k / (2 * k + 2) * math.exp(-hz(k, nu))
            Lap = (k - 1) / (k + nu + 1) - (k - 1) / (2 * k) * math.exp(-hz(k - 1, nu + 2))
            Lc = k / (k + qfb + 1) - 0.5 if qfb >= qw else math.inf
            Lcp = (k - 1) / (k + qfb + 1) - 0.5 if qfb >= qw else math.inf
        else:
            La = k / (n - k) - max(0.5, k / (n - qfb)); Lap = (k - 1) / (k + nu + 1) - max(0.5, (k - 1) / (n - qfb))
            Lc = Lcp = math.inf
        for i in range(8):
            Li = k / (k + qs + 1) - k / (2 * k + 2 - (i + 1) * qfb)
            Lip = (k - 1) / (k + qs) - (k - 1) / (2 * k + 2 - (i + 1) * qfb)
            LOWk += (k / n * BorLe[qfb]) ** i * 0.5 * max(0.0, min(La, Lc, Li))
            LOWk1 += ((k - 1) / n * BorLe[qfb]) ** i * 0.5 * max(0.0, min(Lap, Lcp, Lip))
    val = BorLe[nu - 1] * math.exp(-1 / (12 * (n + 1))) * k / n * (
        math.exp(-5 / (12 * k)) * Rlow(k, nu) * fb(k / n) + LOWk + c0 * (math.exp(-5 / (12 * (k - 1))) * Rlow(k - 1, nu + 2) * fb((k - 1) / n) + LOWk1))
    return (val, case, qmax, qfb) if detail else val

for k in (6668, 6935, 8065, 10000, 13000, 13823, 20000, 100000, 373248):
    numax = int(math.floor(0.48 * k))
    nus = sorted(set([103, 104, 150, 300, 1000] + list(range(103, numax + 1, max(1, numax // 400))) + [numax - 1, numax]))
    nus = [v for v in nus if 103 <= v <= numax]
    vals = [(LB(k, v), v) for v in nus]
    mn = min(vals)
    d = LB(k, mn[1], True)
    print("k=%d: min over %d sampled nu of LB^low = %.5f at nu=%d (case %s, qmax=%d, qfb=%d); at nu=103: %.4f; at 0.48k: %.5f"
          % (k, len(nus), mn[0], mn[1], d[1], d[2], d[3], LB(k, 103), LB(k, numax)))
# neighbourhood of the case boundaries at k=6668 (qmax=2125, k/4=1667)
for nu in (1667, 1668, 1669, 2125, 2126, 2127, 3200):
    print("  k=6668 nu=%d:" % nu, LB(6668, nu, True))
