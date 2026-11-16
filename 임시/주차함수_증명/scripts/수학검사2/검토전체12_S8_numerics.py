# 8장 수치 상수 재계산 (S8, 2026-11-16)
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, floor

mp.dps = 30
c = 1 / sqrt(2 * pi)
z12, zm12, z32 = zeta(mpf(1) / 2), zeta(-mpf(1) / 2), zeta(mpf(3) / 2)
cPsi = -z12 + z32 / 12
k0 = mpf(6600)
eps0 = k0 ** (-mpf(1) / 3)
qmin = mpf('0.2') * k0 ** (mpf(2) / 3)
pmin = qmin - 1
mu = 1 / qmin
out = []


def P(name, val, claim=None):
    out.append(f"{name} = {mp.nstr(val, 15)}" + (f"   [claim {claim}]" if claim else ""))


P("zeta(1/2)", z12); P("zeta(-1/2)", zm12); P("zeta(3/2)", z32); P("cPsi", cPsi, "<1.678059, >3/2")
P("6600^(2/3)", k0 ** (mpf(2) / 3)); P("qmin", qmin, ">70.3708"); P("pmin", pmin, ">69.3708")
P("sqrt(pmin)", sqrt(pmin), ">=8.32891"); P("mu", mu, "<=0.0142105")
P("xi*eps max", mpf('6.001') * eps0, "<0.319921"); P("eps0", eps0, "<=0.0533113")
P("k^-2/3", k0 ** (-mpf(2) / 3), "<=0.00284209")
P("(1-mu)^-1/2", (1 - mu) ** (-mpf(1) / 2), "<=1.007182"); P("(1-mu)^-3/2", (1 - mu) ** (-mpf(3) / 2), "<=1.021701")
P("2/6600^(2/3)", 2 / k0 ** (mpf(2) / 3), "~0.005684")
# pieces-k-monotone
P("E cond lhs", eps0 * (1 + mpf('0.32')), "<0.0704")
P("R2 second", (1 + 1 / (4 * pmin)) / (1 - mu), "<=1.018072")
P("R2 third", mpf(3.5) * k0 / (k0 + 1), ">=3.49946")
P("R2 sum", mpf('2.5') + mpf('1.018072') - mpf('3.49946') - mpf(2) / 3, "<-0.64805")
P("1-mu", 1 - mu, ">=0.985789")
P("1-cPsi/(2sqrt p)", 1 - mpf('1.678059') / (2 * mpf('8.32891')), ">0.89926")
P("D3 sum", mpf('0.319921') / 3 + 1 / (3 * mpf('0.985789') * mpf('0.89926')) - mpf(2) / 3, "<-0.184")
# escape-y-monotone (나)
P("(na) min", mpf('0.2') - k0 ** (-mpf(2) / 3) - 3 * c * sqrt(mpf('0.2')) * eps0, ">0.168623")
xi = mpf('0.2'); k = k0
t1 = (mpf(1.5) * sqrt(xi) - mpf(0.5) / sqrt(xi) * k ** (-mpf(2) / 3)) / (2 * c)
t2 = mpf(0.75) * k ** (-mpf(1) / 3) * (1 + (1 - 1 / (xi * k ** (mpf(2) / 3))) ** (-mpf(1) / 2))
t3 = (k + 1) / (2 * k) * (1 - 1 / (xi * k ** (mpf(2) / 3))) ** (-mpf(3) / 2) / (xi ** 2 * k ** (mpf(2) / 3))
P("(ra) t1", t1, ">0.8367662"); P("(ra) t2", t2, "<0.0802540"); P("(ra) t3", t3, "<0.0363026"); P("(ra) U'", t1 - t2 - t3, ">0.7202096")
a1 = (1 + xi * eps0) / (12 * xi ** 2 * k ** (mpf(1) / 3)); a2 = 3 / (8 * sqrt(xi) * k ** (mpf(1) / 3))
P("(ma) a1", a1, "<0.112250"); P("(ma) a2", a2, "<0.044703"); P("(ma) sum", a1 + a2, "<0.156953")
# jensen-H-ii
P("Lambda'(1)", mpf('2.75') + z12, ">=1.28964"); P("bracket p=1", -mpf(1) / 6 - mpf(2) / 3 * z12 + zm12, ">0.599")


def jinf(x):
    return mpf(4) / 3 * c * x ** mpf(1.5)


def s_frak(q):
    return mpf(4) / 15 * q ** mpf(2.5) + mpf('0.385') * q ** mpf(1.5)


def Cr(q, k):
    return mpf(1.5) * c * (k + q) ** mpf(1.5) / (k + 1) ** mpf(3.5) * s_frak(q)


def Lam(q):
    p = q - 1
    return q * (2 * sqrt(p) + z12 + 1 / (2 * sqrt(p))) - (mpf(2) / 3 * p ** mpf(1.5) + mpf(0.5) * sqrt(p) + zm12)


def Bp(q, k):
    return c * Lam(q) / (k + 1)


P("jinf(0.2)", jinf(mpf('0.2')), "<=0.0475767"); P("Cr(qmin,6600)", Cr(qmin, k0), "<=1.578e-4")
P("exp(-0.0477345)", exp(-mpf('0.0477345')), ">=0.953386")
P("num 1.803147", 2 * c / sqrt(mpf('0.2')) * (1 + mpf('0.2') * eps0), "<1.803147")
P("den 1.952747", mpf('0.168623') + 2 * c / sqrt(mpf('0.2')), ">1.952747")
P("ratio", mpf('1.803147') / mpf('1.952747'), "<0.92339")
# envelope-code-monotone
P("2c sqrt(0.0005)*0.0005", 2 * c * sqrt(mpf('0.0005')) * mpf('0.0005'), ">8.92e-6")
P("Ks(0.0055)", (2 / mpf('0.0055')) ** mpf(1.5), ">=6934.2"); P("s(2)", s_frak(mpf(2)), "<2.59744")
P("Cr(2,6934.2)", Cr(mpf(2), mpf('6934.2')), "<=3.24e-8"); P("Cr(2e4,6.6e9)", Cr(mpf(2e4), mpf(6.6e9)), "<=2.08e-10")
# closed-form (가)
P("phi min", exp(-1 / (12 * qmin)), ">0.998816"); P("rho1 max", mpf(1.5) * mpf('6.001') * eps0, "<0.4798811")
xi = mpf('6.001')
P("rho2 max", mpf(5) / 8 * (1 + 3 / (4 * pmin)) * (1 + xi * eps0) ** mpf(2.5) * xi ** 2 * k0 ** (-mpf(2) / 3), "<=0.129421")
P("theta1 max", xi ** mpf(1.5) / (2 * c), "<=18.42449"); P("upsilon max", (k0 + 1) / k0 * (1 - mu) ** (-mpf(1) / 2), "<=1.00734")
P("V/U", mpf('0.3895139') / mpf('19.43183'), ">=0.020044")
# (나)
xi = mpf('0.1'); br = (mpf('0.4') * xi ** mpf(1.5) + mpf('0.5775') * sqrt(xi) * k0 ** (-mpf(2) / 3)) * (1 + xi * eps0) ** mpf(1.5)
P("(na) bracket xi=0.1", br, "<0.013274"); P("(na) total xi<=0.1", mpf('1.46035') - mpf('0.103945') - mpf('0.041667') - br, ">1.3014")
xi = mpf('2.1'); br = (mpf('0.4') * xi ** mpf(1.5) + mpf('0.5775') * sqrt(xi) * k0 ** (-mpf(2) / 3)) * (1 + xi * eps0) ** mpf(1.5)
q01 = mpf('0.1') * k0 ** (mpf(2) / 3)
P("q at xi=0.1", q01, ">=35.1854"); P("|z-1/2|/q", mpf('0.20789') / q01, "<=0.005909")
P("p^-3/2/(12q)", (q01 - 1) ** (-mpf(1.5)) / (12 * q01), "<=0.000012")
P("(na) bracket xi=2.1", br, "<=1.430101 ?"); P("(na) total", mpf('1.46035') - mpf('0.005909') - mpf('0.000012') - br, ">0.0243")
# (다)
q2 = 2 * k0 ** (mpf(2) / 3); P("2*6600^(2/3)", q2, ">703.708")
mu2 = 1 / q2; p2 = q2 - 1
P("(da) rho1' coeff", mpf(0.5) * (sqrt(1 - mu2) - (1 + p2 ** (-mpf(0.5))) * eps0 / sqrt(mpf(2))), ">=0.480085")
P("(da) dV", mpf('0.480085') - mpf(1) / 3, ">0.146751")
P("(da) theta1'", eps0 / sqrt(mpf(2)) / (3 * c), "<=0.0314973"); P("(da) theta3'", mpf(0.5) * (1 + 1 / (4 * p2)), "<=0.5001779")
P("(da) V<1 coeff", mpf(0.5) - mpf(1.5) * mu2 - mpf(0.75) * eps0 / sqrt(mpf(2)), ">=0.46959")
xi = mpf(2); P("(da) U>", 1 + (xi ** mpf(1.5) - sqrt(xi) * k0 ** (-mpf(2) / 3)) / (2 * c) - mpf(1.5) * xi * eps0, ">=4.37993")
P("(da) final", mpf('0.146751') - mpf('0.5316752') / mpf('4.37993'), ">=0.02536")


def pieces(xi, k):
    q = xi * k ** (mpf(2) / 3); p = q - 1; n = k + q; kk = k + 1; e = k ** (-mpf(1) / 3)
    E = 2 * c * exp(-1 / (12 * q)) / sqrt(xi) * (1 + xi * e)
    R1 = mpf(1.5) * c * (2 * sqrt(p) - 1) * k ** (-mpf(2) / 3)
    H = mpf(2) / 3 * p ** mpf(1.5) + mpf(0.5) * sqrt(p) + zm12 + 1 / (24 * sqrt(p))
    R2 = mpf(15) / 8 * c * n ** mpf(2.5) * H / (kk ** mpf(3.5) * k ** (mpf(2) / 3))
    D1 = p / k ** (mpf(2) / 3)
    D2 = kk * sqrt(2 / pi) / sqrt(p) * k ** (-mpf(2) / 3)
    Psil = c * (2 * sqrt(p) - cPsi + 1 / (2 * sqrt(p)) - p ** (-mpf(1.5)) / 24)
    D3 = mpf(1.5) * kk * Psil / ((n + 1) * k ** (mpf(2) / 3))
    return E, R1, R2, D1, D2, D3


def qkk(xi, k):
    E, R1, R2, D1, D2, D3 = pieces(xi, k)
    return (E - R1 - R2) / (D1 + D2 - D3)


P("q6600(0.2)", qkk(mpf('0.2'), k0), "<0.92339"); P("q6600(2)", qkk(mpf(2), k0), "<=0.213721"); P("q6600(2.1)", qkk(mpf('2.1'), k0), ">=0.200904")
P("exp(-jinf(2))", exp(-jinf(mpf(2))), ">=0.222127"); P("exp(-jinf(2.1))", exp(-jinf(mpf('2.1'))), "<=0.198148")
P("exp(-(jinf+Cr)) at 0.2", exp(-(jinf(mpf('0.2')) + Cr(qmin, k0))), ">=0.953386?")
# table-tolerance
P("rG", mpf('0.38951') * mpf('0.7202') / mpf('19.4319') ** 2, ">=7.429e-4")
P("0.85 diff p=1", mpf('2.75') + z12 - mpf('0.85') * sqrt(mpf(2)), ">0.087")
P("0.85c k/(k+1)", mpf('0.85') * c * k0 / (k0 + 1), ">=0.339049")
P("case2a", mpf('0.020044') * mpf('0.169524') * sqrt(mpf('0.2')), ">=1.51e-3")
P("case2b", mpf('0.953386') * mpf('0.169524') * sqrt(mpf('0.0005')), ">=3.61e-3")
# hazard-H1
P("1.5-0.307(1-3/(2k))", mpf(1.5) - mpf('0.307') * (1 - mpf(1.5) / 6667), "<=1.1935")
k = mpf(6667); P("(qfb+2)/k lower", mpf(3) / 32 - mpf(0.75) * k ** (-mpf(1) / 3) + mpf('0.53') / k, ">=0.0537")
qmax = floor(6 * k ** (mpf(2) / 3)); qfb = floor((3 * (k - 1) / 4 - qmax - 3) / 8); P("qfb(6667)", qfb); P("(qfb+2)/k actual", (qfb + 2) / k)


def G(z):
    return mpf(1.5) * (1 - z) - mpf('1.1935') * log(2 / (1 + z)) - 1 / (1 + z) + mpf(0.5)


P("G(0.0537)", G(mpf('0.0537')), ">0.205"); P("G(0.571)", G(mpf('0.571')), ">0.218"); P("log(2/1.0537)", log(2 / mpf('1.0537')), "<0.64084")
P("1/1.0537", 1 / mpf('1.0537'), "<0.94904"); P("log(2/1.571)", log(2 / mpf('1.571')), "<0.24144"); P("1/1.571", 1 / mpf('1.571'), "<0.63654")
P("3.2/6667", mpf('3.2') / 6667, "<=0.0005")
# 8-29
k = mpf(6668); qmax = floor(6 * k ** (mpf(2) / 3)); P("qmax(6668)", qmax); P("k-2399-qmax-300", k - 2399 - qmax - 300, ">=0")
P("3k/4-2398-qmax", 3 * k / 4 - 2398 - qmax, ">=0")
P("(6600/6599)^(2/3)", (mpf(6600) / 6599) ** (mpf(2) / 3), "<=1.0002")
for kk_ in [412, 413, 421, 422]:
    kk_ = mpf(kk_); P(f"9(k+2)-5(k+6k^2/3+1) k={kk_}", 9 * (kk_ + 2) - 5 * (kk_ + 6 * kk_ ** (mpf(2) / 3) + 1))
P("6*216^(2/3)", 6 * mpf(216) ** (mpf(2) / 3), "<=217")
# 8-33 case (ii) existence: 6k^{2/3} >= k/4+1
for kk_ in [6668, 13824, 13825]:
    kk_ = mpf(kk_); P(f"6k^(2/3)-(k/4+1) k={kk_}", 6 * kk_ ** (mpf(2) / 3) - (kk_ / 4 + 1))
open("scripts/수학검사2/검토전체12_S8_numerics.out", "w", encoding="utf-8").write("\n".join(out))
print("done", len(out))
