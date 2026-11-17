# R8 (review 24): re-check of the explicit constants quoted in chapter 8.
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta
mp.dps = 40
k0 = mpf(6600)
eps0 = k0 ** (-mpf(1) / 3)
c = 1 / sqrt(2 * pi)            # (2 pi)^(-1/2)
print("zeta(1/2)", zeta(mpf(1) / 2), "zeta(-1/2)", zeta(-mpf(1) / 2), "zeta(3/2)", zeta(mpf(3) / 2))
qmin = mpf("0.2") * k0 ** (mpf(2) / 3)
pmin = qmin - 1
mu = 1 / qmin
print("q_min", qmin, "p_min", pmin, "sqrt p", sqrt(pmin), "mu", mu)
print("xi eps max", mpf("6.001") * eps0, "eps0", eps0, "k^-2/3", k0 ** (-mpf(2) / 3))
print("(1-mu)^-1/2", (1 - mu) ** (-mpf(1) / 2), "(1-mu)^-3/2", (1 - mu) ** (-mpf(3) / 2))
# pieces-k-monotone (ga)
print("(ga) lhs<=", mpf("0.0533113") * mpf("1.32"))
# (na)
t2 = (1 + 1 / (4 * pmin)) / (1 - mu)
print("(na) second", t2, "third", mpf(7) / 2 * k0 / (k0 + 1), "sum", mpf("2.5") + mpf("1.018072") - mpf("3.49946") - mpf("0.666667"))
# (da)
cpsi_up = mpf("1.46036") + mpf("2.61238") / 12
print("c_Psi upper", cpsi_up, "true", -zeta(mpf(1) / 2) + zeta(mpf(3) / 2) / 12)
f2 = 1 - mpf("1.678059") / (2 * mpf("8.32891"))
print("(da) 1-c/(2sqrt p)", f2, "total", mpf("0.319921") / 3 + 1 / (3 * mpf("0.985789") * mpf("0.89926")) - mpf(2) / 3)
# escape-y-monotone first fact
print("first fact", mpf("0.2") - k0 ** (-mpf(2) / 3) - 3 * c * sqrt(mpf("0.2")) * eps0,
      "with rounded", mpf("0.2") - mpf("0.00284209") - 3 * c * sqrt(mpf("0.2")) * mpf("0.0533113"))
print("3/2 c eps0", mpf(3) / 2 * c * eps0)
# third fact
xi = mpf("0.2")
a1 = (1 + xi * eps0) / (12 * xi ** 2 * k0 ** (mpf(1) / 3))
a2 = 3 / (8 * sqrt(xi) * k0 ** (mpf(1) / 3))
print("third fact terms", a1, a2, a1 + a2, -mpf(1) / 2 + a1 + a2)
# (na) U'
T1 = (mpf(3) / 2 * sqrt(xi) - mpf(1) / 2 / sqrt(xi) * k0 ** (-mpf(2) / 3)) / (2 * c)
w = 1 - 1 / (xi * k0 ** (mpf(2) / 3))
T2 = mpf(3) / 4 * eps0 * (1 + w ** (-mpf(1) / 2))
T3 = (k0 + 1) / (2 * k0) * w ** (-mpf(3) / 2) / (xi ** 2 * k0 ** (mpf(2) / 3))
print("U' terms", T1, T2, T3, T1 - T2 - T3)
# closed-form (ga)
print("phi>=", exp(-1 / (12 * qmin)))
print("rho1<", mpf(3) / 2 * mpf("6.001") * eps0)
xi = mpf("6.001")
rho2 = mpf(5) / 8 * (1 + 3 / (4 * pmin)) * (1 + xi * eps0) ** (mpf(5) / 2) * xi ** 2 * k0 ** (-mpf(2) / 3)
print("rho2<=", rho2)
print("V>=", mpf("0.998816") - mpf("0.4798811") - mpf("0.129421"))
print("U<=", xi ** (mpf(3) / 2) / (2 * c), (k0 + 1) / k0 * (1 - mu) ** (-mpf(1) / 2))
print("ratio", mpf("0.3895139") / mpf("19.43183"))
# closed-form (na)
xi = mpf("0.1")
br = (mpf("0.4") * xi ** (mpf(3) / 2) + mpf("0.5775") * sqrt(xi) * k0 ** (-mpf(2) / 3)) * (1 + xi * eps0) ** (mpf(3) / 2)
print("(na) case1", mpf("0.20789") / 2, mpf(1) / 24, br, mpf("1.46035") - mpf("0.20789") / 2 - mpf(1) / 24 - br)
q = mpf("0.1") * k0 ** (mpf(2) / 3)
p = q - 1
xi = mpf("2.1")
br = (mpf("0.4") * xi ** (mpf(3) / 2) + mpf("0.5775") * sqrt(xi) * k0 ** (-mpf(2) / 3)) * (1 + xi * eps0) ** (mpf(3) / 2)
print("(na) case2 q,p", q, p, mpf("0.20789") / q, p ** (-mpf(3) / 2) / (12 * q), br,
      mpf("1.46035") - mpf("0.20789") / q - p ** (-mpf(3) / 2) / (12 * q) - br)
# closed-form (da)
q2 = 2 * k0 ** (mpf(2) / 3)
p2 = q2 - 1
mu2 = 1 / q2
xi = mpf(2)
b = sqrt(1 - mu2) - (1 + p2 ** (-mpf(1) / 2)) * eps0 / sqrt(xi)
print("(da) q>=", q2, "rho1 coeff", b / 2, "dV", b / 2 - mpf(1) / 3)
print("dtheta1", eps0 / sqrt(2) / (3 * c), "dtheta3", (1 + 1 / (4 * p2)) / 2, "dU", eps0 / sqrt(2) / (3 * c) + (1 + 1 / (4 * p2)) / 2)
print("V bracket", mpf(1) / 2 - mpf(3) / 2 * mu2 - mpf(3) / 4 * eps0 / sqrt(xi))
print("U>", 1 + (xi ** (mpf(3) / 2) - sqrt(xi) * k0 ** (-mpf(2) / 3)) / (2 * c) - mpf(3) / 2 * xi * eps0)
print("log-derivative", mpf("0.146751") - mpf("0.5316752") / mpf("4.37993"))
# j_inf at seams
for x in (mpf(2), mpf("2.1")):
    print("exp(-j_inf)", x, exp(-mpf(4) / 3 * c * x ** (mpf(3) / 2)))

# Esc_6600 at the seams, from (8.12)
z12 = zeta(mpf(1) / 2); zm12 = zeta(-mpf(1) / 2); z32 = zeta(mpf(3) / 2)
cpsi = -z12 + z32 / 12
def psilow(x):
    return c * (2 * sqrt(x) - cpsi + 1 / (2 * sqrt(x)) - x ** (-mpf(3) / 2) / 24) if x >= 1 else mpf(0)
def esc(xi, k):
    q = xi * k ** (mpf(2) / 3); p = q - 1; n = k + q; kk = k + 1; e = k ** (-mpf(1) / 3)
    H = mpf(2) / 3 * p ** (mpf(3) / 2) + sqrt(p) / 2 + zm12 + 1 / (24 * sqrt(p))
    E = 2 * c * exp(-1 / (12 * q)) * xi ** (-mpf(1) / 2) * (1 + xi * e)
    R1 = mpf(3) / 2 * c * (2 * sqrt(p) - 1) * k ** (-mpf(2) / 3)
    R2 = mpf(15) / 8 * c * n ** (mpf(5) / 2) * H / (kk ** (mpf(7) / 2) * k ** (mpf(2) / 3))
    D1 = p / k ** (mpf(2) / 3)
    D2 = kk * sqrt(2 / pi) * p ** (-mpf(1) / 2) * k ** (-mpf(2) / 3)
    D3 = mpf(3) / 2 * kk * psilow(p) / ((n + 1) * k ** (mpf(2) / 3))
    return (E - R1 - R2) / (D1 + D2 - D3)
for x in (mpf(2), mpf("2.1"), mpf("0.2"), mpf("6.001")):
    print("Esc_6600", x, esc(x, k0))
# K grid
K = mpf(10) ** 5
print("K^(2/3)", K ** (mpf(2) / 3), 12927 / K ** (mpf(2) / 3), 12926 / K ** (mpf(2) / 3))
# 4k>=30k^(2/3) threshold, 6k^(2/3)<=k+1
print("k thresh", mpf("7.5") ** 3)
# end of 8.2
print("1.15/6^1.5", mpf("1.15") / mpf(6) ** (mpf(3) / 2))
# hazard lemma
print("G(0.0537)", mpf("1.5") * (1 - mpf("0.0537")), log(2 / mpf("1.0537")), 1 / mpf("1.0537"),
      mpf("1.5") * (1 - mpf("0.0537")) - mpf("1.1935") * log(2 / mpf("1.0537")) - 1 / mpf("1.0537") + mpf("0.5"))
print("G(0.49)", log(2 / mpf("1.49")), 1 / mpf("1.49"),
      mpf("1.5") * mpf("0.51") - mpf("1.1935") * log(2 / mpf("1.49")) - 1 / mpf("1.49") + mpf("0.5"))
kk = mpf(6667)
print("1.1935 check", mpf("1.5") - mpf("0.307") * (1 - mpf(3) / (2 * kk)), "3.2/k", mpf("3.2") / kk, mpf(47) / 24 + mpf("1.1935"))
print("nu/k lower", mpf(3) / 32 - mpf(3) / 4 * kk ** (-mpf(1) / 3) + mpf("0.53") / kk)
# q_fb, q_max at k = 6668
import math
for k in (6668, 13824, 373248, 10**6):
    qmax = math.floor(6 * k ** (2 / 3))
    qfb = math.floor((3 * (k - 1) / 4 - qmax - 3) / 8)
    print("k", k, "qmax", qmax, "qfb", qfb, "k/4", k / 4, "mfb", math.ceil(5 * k / 4) + qmax, "2k+1-8qfb", 2 * k + 1 - 8 * qfb)
