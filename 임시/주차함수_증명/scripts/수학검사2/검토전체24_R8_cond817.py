# R8 (review 24): sample evaluation (binary64 sanity check) of condition (8.17) as printed, and of
# the theorem (8.21) against the exact recursion (8.4) at a small sample of k (exact s via (8.2)-type recursion is
# too heavy at k>=6600, so only (8.17) is sampled here).
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "원고_자료", "세션_재계산", "r030ffae_window", "work")
z = np.load(os.path.join(base, "qenv_fix_v.npy")); wK = np.load(os.path.join(base, "wKrig.npy"))
That = lambda x: np.interp(x, 0.0005 * np.arange(len(z)), z)
h = 1.0 / (1e5) ** (2.0 / 3.0)
xi = np.arange(len(wK)) * h
ramp = lambda s: np.where(s <= -0.1, 0.0, np.where(s < 0.1, (s + 0.1) ** 2 / 0.4, s))
y = np.minimum.accumulate((1.0 - np.minimum(1.0, 0.04 + 0.12 * ramp(xi - 1.0))) * wK)
d = np.diff(y) / h
m = np.zeros(len(y)); m[1:-1] = np.where(d[:-1] * d[1:] > 0, 2 * d[:-1] * d[1:] / (d[:-1] + d[1:]), 0.0)
m[0] = min(0.0, 1.5 * d[0] - 0.5 * d[1]); m[-1] = min(0.0, 1.5 * d[-1] - 0.5 * d[-2])
def Omega(x):
    x = np.asarray(x, dtype=float); i = np.clip((x / h).astype(int), 0, len(y) - 2); t = (x - i * h) / h
    return (1 + 2 * t) * (1 - t) ** 2 * y[i] + t * (1 - t) ** 2 * h * m[i] + t * t * (3 - 2 * t) * y[i + 1] + t * t * (t - 1) * h * m[i + 1]
NB = 3001
jj = np.arange(1, NB + 1, dtype=float)
Bor = np.exp(-jj + (jj - 1) * np.log(jj) - np.array([math.lgamma(j + 1) for j in range(1, NB + 1)]))
BorLe = np.concatenate(([0.0], np.cumsum(Bor))); Psi = np.concatenate(([0.0], np.cumsum(jj * Bor)))
def phi(q, x):
    j = np.arange(1, q, dtype=float)
    lhs = BorLe[q] * (1 - Omega(x)) + np.sum(Bor[:q - 1] * Psi[q - 1:0:-1] * (Omega(x * (1 - j / q)) - Omega(x)))
    jq = np.arange(1, q + 1, dtype=float)
    rhs = x ** 1.5 * q ** -0.5 * Psi[q] * Omega(x) + np.sum(Bor[:q] * (1 - That(x * (1 - jq / q))))
    return float(lhs), float(rhs)
worst = (9, None)
for q in (1, 2, 3, 5, 10, 50, 200, 1000, 2000, 2999):
    top = min(6.0, q / 6600 ** (2 / 3))
    for x in np.concatenate((np.linspace(1e-6, top, 4000), [top])):
        l, r = phi(q, float(x))
        rel = (l - r) / r if r > 0 else 9
        if rel < worst[0]: worst = (rel, (q, float(x), l, r))
    print("q=%d: xi range (0, %.4f]; checked" % (q, top))
print("smallest relative margin (lhs-rhs)/rhs over the sample:", worst)
