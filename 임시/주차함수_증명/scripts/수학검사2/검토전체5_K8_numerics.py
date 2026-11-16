# -*- coding: utf-8 -*-
"""검토전체5 K8: 8.2–8.4절 본문에 적힌 수치 상수의 재계산 (mpmath 50자리)."""
from mpmath import mp, mpf, sqrt, exp, log, zeta, pi, floor, ceil, nsum, inf
mp.dps = 50
c2pi = 1 / sqrt(2 * pi)
z12 = zeta(mpf(1) / 2); zm12 = zeta(-mpf(1) / 2); z32 = zeta(mpf(3) / 2)
print("zeta:", z12, zm12, z32)
cPsi = -z12 + z32 / 12
print("c_Psi =", cPsi, " (text: 1.67805..., <1.678059)", cPsi < mpf('1.678059'))

def Bor(m): return exp(-m) * mpf(m) ** (m - 1) / mp.factorial(m)
def Ren(j): return mpf(j) ** j * exp(-j) / mp.factorial(j) if j >= 1 else mpf(1)
def Psi(q): return sum(Ren(j) for j in range(1, q + 1))
def Psilow(r):
    r = mpf(r)
    if r < 1: return mpf(0)
    return c2pi * (2 * sqrt(r) - cPsi + 1 / (2 * sqrt(r)) - r ** (-mpf(3) / 2) / 24)

print("\n== explicit-bounds (나)(다)(라) over r=1..3000 ==")
bad = []
S12 = mpf(0); Sm12 = mpf(0); S32 = mpf(0); BorLe = mpf(0); PsiAcc = mpf(0)
for r in range(1, 3001):
    rr = mpf(r)
    S12 += 1 / sqrt(rr); Sm12 += sqrt(rr); S32 += rr ** (-mpf(3) / 2)
    BorLe += Bor(r); PsiAcc += Ren(r)
    if not (S12 <= 2 * sqrt(rr) + z12 + 1 / (2 * sqrt(rr))): bad.append(("na1", r))
    if not (S12 >= 2 * sqrt(rr) + z12 + 1 / (2 * sqrt(rr)) - rr ** (-mpf(3) / 2) / 24): bad.append(("na2", r))
    if not (Sm12 >= mpf(2) / 3 * rr ** mpf(1.5) + sqrt(rr) / 2 + zm12): bad.append(("na3", r))
    if not (Sm12 <= mpf(2) / 3 * rr ** mpf(1.5) + sqrt(rr) / 2 + zm12 + 1 / (24 * sqrt(rr))): bad.append(("na4", r))
    if not (S32 <= z32): bad.append(("na5", r))
    if not (PsiAcc <= c2pi * (2 * sqrt(rr) - 1)): bad.append(("da1", r))
    if not (BorLe >= 1 - sqrt(2 / pi) / sqrt(rr)): bad.append(("da2", r))
    tail = 1 - BorLe
    if not (tail <= sqrt(2 / pi) / sqrt(rr)): bad.append(("da3", r))
    if not (tail >= 2 * c2pi * exp(-1 / (12 * (rr + 1))) / sqrt(rr + 1)): bad.append(("da4", r))
    if not (PsiAcc >= Psilow(r)): bad.append(("ra", r))
    # (가)
    if not (c2pi * rr ** (-mpf(3) / 2) * exp(-1 / (12 * rr)) <= Bor(r) <= c2pi * rr ** (-mpf(3) / 2) * exp(-1 / (12 * rr + 1))): bad.append(("ga_bor", r))
    if not (c2pi / sqrt(rr) * exp(-1 / (12 * rr)) <= Ren(r) <= c2pi / sqrt(rr) * exp(-1 / (12 * rr + 1))): bad.append(("ga_ren", r))
print("violations:", bad[:10], "count", len(bad))
# (라) derivative bracket and bounds at sample rho
for rho in [1, 1.5, 2, 10, 100, 1e4]:
    rho = mpf(rho)
    d = c2pi / sqrt(rho) * (1 - 1 / (4 * rho) + 1 / (16 * rho ** 2))
    assert 0 < d <= c2pi / sqrt(rho)
    assert c2pi * (2 * sqrt(rho) - cPsi) <= Psilow(rho) < 2 * c2pi * sqrt(rho)
print("(라) ok; Psilow(1)=", Psilow(1), " 59/24-cPsi=", mpf(59) / 24 - cPsi)
# (마)
def g(x): return (x - 1) * log(1 + 1 / mpf(x))
for i in range(1, 2000):
    assert mpf(3) / (2 * i) - mpf(5) / (6 * i * i) <= 1 - g(i) <= mpf(3) / (2 * i)
for ip in [10, 50, 200, 1000]:
    for j in range(1, ip - 1):
        ratio = Bor(ip - j) / Bor(ip)
        assert ratio <= (mpf(ip - 1) / (ip - 1 - j)) ** mpf(1.5), (ip, j)
        assert ratio >= (mpf(ip) / (ip - j)) ** mpf(1.5) * exp(-mpf(5) * j / (6 * (ip - j) ** 2)), (ip, j)
print("(마) ok")

print("\n== 8.2 상수 (k>=6600, 0.2<=xi<=6.001) ==")
k0 = mpf(6600)
qmin = mpf('0.2') * k0 ** (mpf(2) / 3); pmin = qmin - 1
print("q_min", qmin, " (70.3708)"); print("p_min", pmin, " sqrt", sqrt(pmin), " (8.32891)")
mu = 1 / qmin; print("mu", mu, " (0.0142105)")
xe = mpf('6.001') * k0 ** (-mpf(1) / 3); print("xi*eps max", xe, " (0.319921)")
eps0 = k0 ** (-mpf(1) / 3); print("eps0", eps0, " (0.0533113)"); print("k^-2/3", k0 ** (-mpf(2) / 3), " (0.00284209)")
print("(1-mu)^-1/2", (1 - mu) ** (-mpf(1) / 2), " (1.007182)"); print("(1-mu)^-3/2", (1 - mu) ** (-mpf(3) / 2), " (1.021701)")
print("2/6600^(2/3) =", 2 / k0 ** (mpf(2) / 3))

print("\n== pieces-k-monotone 수치 ==")
print("E: eps0*1.32 =", eps0 * mpf('1.32'), " <0.0704?", eps0 * mpf('1.32') < mpf('0.0704'))
print("R2 second term:", (1 + 1 / (4 * pmin)) / (1 - mu), " (<=1.018072)")
print("R2 third:", mpf(7) / 2 * k0 / (k0 + 1), " (3.49946)")
print("R2 sum:", mpf('2.5') + (1 + 1 / (4 * pmin)) / (1 - mu) - mpf(7) / 2 * k0 / (k0 + 1) - mpf(2) / 3)
d3 = xe / 3 + 1 / (3 * (1 - mu) * (1 - cPsi / (2 * sqrt(pmin)))) - mpf(2) / 3
print("D3: 1-cPsi/(2 sqrt pmin) =", 1 - cPsi / (2 * sqrt(pmin)), " (>0.89926); total", d3, " (<-0.184)")

print("\n== escape-y-monotone 수치 ==")
xi = mpf('0.2')
print("(나) min:", xi - k0 ** (-mpf(2) / 3) - 3 * c2pi * sqrt(xi) * k0 ** (-mpf(1) / 3), " (0.168623)")
print("(나) 1.5*c2pi*eps0 =", mpf('1.5') * c2pi * eps0, " (<=0.032)")
t1 = (mpf(1.5) * sqrt(xi) - sqrt(xi) ** -1 / 2 * k0 ** (-mpf(2) / 3)) / (2 * c2pi)
t2 = mpf(3) / 4 * k0 ** (-mpf(1) / 3) * (1 + (1 - 1 / (xi * k0 ** (mpf(2) / 3))) ** (-mpf(1) / 2))
t3 = (k0 + 1) / (2 * k0) * (1 - 1 / (xi * k0 ** (mpf(2) / 3))) ** (-mpf(3) / 2) / (xi ** 2 * k0 ** (mpf(2) / 3))
print("(라) U' terms:", t1, t2, t3, " sum", t1 - t2 - t3, " (0.7202096)")
a1 = (1 + xi * eps0) / (12 * xi ** 2 * k0 ** (mpf(1) / 3)); a2 = 3 / (8 * sqrt(xi) * k0 ** (mpf(1) / 3))
print("(마) terms:", a1, a2, " sum", a1 + a2, " (0.156953) -> V' <=", -mpf(0.5) + a1 + a2)

print("\n== closed-form-envelope 수치 ==")
print("(가) phi>= e^{-1/(12 qmin)} =", exp(-1 / (12 * qmin)), " (0.998816)")
print("(가) rho1 < 1.5*xe =", mpf(1.5) * xe, " (0.4798811)")
xi = mpf('6.001')
rho2 = mpf(5) / 8 * (1 + 3 / (4 * pmin)) * (1 + xe) ** mpf(2.5) * xi ** 2 * k0 ** (-mpf(2) / 3)
print("(가) rho2 <=", rho2, " (0.129421)")
V = exp(-1 / (12 * qmin)) - mpf(1.5) * xe - rho2; print("V>=", V, " (0.3895139)")
U = xi ** mpf(1.5) / (2 * c2pi) + (k0 + 1) / k0 * (1 - mu) ** (-mpf(1) / 2); print("U<=", U, " (19.43183)", " theta1", xi ** mpf(1.5) / (2 * c2pi))
print("q>=", V / U, " (0.020044)")
# (나)
print("(나) xi<=0.1:", mpf('1.46035') - mpf('0.20789') / 2 - mpf(1) / 24 - (mpf('0.4') * mpf('0.1') ** mpf(1.5) + mpf('0.5775') * sqrt(mpf('0.1')) * k0 ** (-mpf(2) / 3)) * (1 + mpf('0.1') * eps0) ** mpf(1.5))
q21 = mpf('2.1') * k0 ** (mpf(2) / 3); p21 = q21 - 1
print("(나) q at 0.1:", mpf('0.1') * k0 ** (mpf(2) / 3), " (35.1854)")
br = (mpf('0.4') * mpf('2.1') ** mpf(1.5) + mpf('0.5775') * sqrt(mpf('2.1')) * k0 ** (-mpf(2) / 3)) * (1 + mpf('2.1') * eps0) ** mpf(1.5)
print("(나) 0.1..2.1:", mpf('0.20789') / (mpf('0.1') * k0 ** (mpf(2) / 3)), (mpf('0.1') * k0 ** (mpf(2) / 3) - 1) ** (-mpf(1.5)) / (12 * mpf('0.1') * k0 ** (mpf(2) / 3)), br, " total", mpf('1.46035') - mpf('0.20789') / (mpf('0.1') * k0 ** (mpf(2) / 3)) - (mpf('0.1') * k0 ** (mpf(2) / 3) - 1) ** (-mpf(1.5)) / (12 * mpf('0.1') * k0 ** (mpf(2) / 3)) - br, " (>0.0243)")
# (다)
q2 = 2 * k0 ** (mpf(2) / 3); p2 = q2 - 1; mu2 = 1 / q2
print("(다) q>=", q2, " (703.708)")
v1 = mpf(0.5) * (sqrt(1 - mu2) - (1 + p2 ** (-mpf(0.5))) * k0 ** (-mpf(1) / 3) / sqrt(2)); print("(다) rho1' coef", v1, " (0.480085)")
print("(다) dV/dk coef", v1 - mpf(1) / 3, " (0.146751)")
print("(다) theta1' coef", k0 ** (-mpf(1) / 3) / sqrt(2) / (3 * c2pi), " (0.0314973)")
print("(다) theta3 coef", mpf(0.5) * (1 + 1 / (4 * p2)), " (0.5001779)")
print("(다) V<1 coef", mpf(0.5) - mpf(1.5) * mu2 - mpf(0.75) * k0 ** (-mpf(1) / 3) / sqrt(2), " (0.46959)")
xi = mpf(2)
Ulow = 1 + (xi ** mpf(1.5) - sqrt(xi) * k0 ** (-mpf(2) / 3)) / (2 * c2pi) - mpf(1.5) * xi * k0 ** (-mpf(1) / 3); print("(다) U>", Ulow, " (4.37993)")
print("(다) final", v1 - mpf(1) / 3 - mpf('0.5316752') / Ulow, " (0.02536)")
# (라) seams: compute q_{6600,6600}(xi) from six pieces
def pieces(xi, k):
    xi = mpf(xi); k = mpf(k)
    q = xi * k ** (mpf(2) / 3); p = q - 1; n = k + q; kk = k + 1; eps = k ** (-mpf(1) / 3)
    E = 2 * c2pi * exp(-1 / (12 * q)) / sqrt(xi) * (1 + xi * eps)
    R1 = mpf(1.5) * c2pi * (2 * sqrt(p) - 1) * k ** (-mpf(2) / 3)
    H = mpf(2) / 3 * p ** mpf(1.5) + sqrt(p) / 2 + zm12 + 1 / (24 * sqrt(p))
    R2 = mpf(15) / 8 * c2pi * n ** mpf(2.5) * H / (kk ** mpf(3.5) * k ** (mpf(2) / 3))
    D1 = p / k ** (mpf(2) / 3)
    D2 = kk * sqrt(2 / pi) / sqrt(p) / k ** (mpf(2) / 3)
    D3 = mpf(1.5) * kk * Psilow(p) / ((n + 1) * k ** (mpf(2) / 3))
    return E, R1, R2, D1, D2, D3
def qkk(xi, k):
    E, R1, R2, D1, D2, D3 = pieces(xi, k)
    return (E - R1 - R2) / (D1 + D2 - D3)
jinf = lambda xi: mpf(4) / 3 * c2pi * mpf(xi) ** mpf(1.5)
print("(라) q(2)=", qkk(2, 6600), " e^-j(2)=", exp(-jinf(2)))
print("(라) q(2.1)=", qkk('2.1', 6600), " e^-j(2.1)=", exp(-jinf('2.1')))
print("q(0.2,6600)=", qkk('0.2', 6600), "  E/(0.168623+E0) bound:", pieces('0.2', 6600)[0], "/", mpf('0.168623') + 2 * c2pi / sqrt(mpf('0.2')))
print("E(0.2,6600) (without exp factor) =", 2 * c2pi / sqrt(mpf('0.2')) * (1 + mpf('0.2') * eps0), " (1.803147); denom", mpf('0.168623') + 2 * c2pi / sqrt(mpf('0.2')), " (1.952747); ratio", 2 * c2pi / sqrt(mpf('0.2')) * (1 + mpf('0.2') * eps0) / (mpf('0.168623') + 2 * c2pi / sqrt(mpf('0.2'))))
print("sanity: min over xi grid of q_{6600,6600} positivity & (가) bound 0.020044:")
mn = min(qkk(mpf(i) / 100, 6600) for i in range(20, 601))
print("  min q_{6600,6600} on [0.2,6] =", mn)

print("\n== table-lower-bound (가) 수치 ==")
def Cr(q, k):
    q = mpf(q); k = mpf(k)
    s = mpf(4) / 15 * q ** mpf(2.5) + mpf('0.385') * q ** mpf(1.5)
    return mpf(1.5) * c2pi * (k + q) ** mpf(1.5) / (k + 1) ** mpf(3.5) * s
print("j_inf(0.2)=", jinf('0.2'), " (0.0475767)"); print("Cr(qmin,6600)=", Cr(qmin, 6600), " (1.578e-4)")
print("e^-0.0477345=", exp(-mpf('0.0477345')), " (0.953386)")

print("\n== envelope-code-monotone 수치 ==")
print("2 c2pi sqrt(0.0005)*0.0005 =", 2 * c2pi * sqrt(mpf('0.0005')) * mpf('0.0005'), " (8.9206e-6)")
print("(2/0.0055)^1.5 =", (2 / mpf('0.0055')) ** mpf(1.5), " (6934.2)")
print("s(2)=", mpf(4) / 15 * mpf(2) ** mpf(2.5) + mpf('0.385') * mpf(2) ** mpf(1.5), " (2.59744)")
print("Cr(2,6934.2)=", Cr(2, (2 / mpf('0.0055')) ** mpf(1.5)), " (<=3.24e-8)")
print("Cr(2e4,6.6e9)=", Cr(20000, mpf('6.6e9')), " (<=2.08e-10)")
print("xi K^(2/3) at K=6.6e9, xi=0.005684:", mpf('0.005684') * mpf('6.6e9') ** (mpf(2) / 3))

print("\n== table-tolerance 수치 ==")
print("r_G: 0.38951*0.7202/19.4319^2 =", mpf('0.38951') * mpf('0.7202') / mpf('19.4319') ** 2, " (7.429e-4)")
print("Lambda'(1)-0.85 sqrt2 =", mpf('2.75') + z12 - mpf('0.85') * sqrt(2), " (>0.087)")
print("0.85 c2pi 6600/6601 =", mpf('0.85') * c2pi * k0 / (k0 + 1), " (0.339049)")
print("coef case2 xi'>=0.2:", mpf('0.020044') * mpf('0.169524') * sqrt(mpf('0.2')), " (1.51e-3)")
print("coef case2 xi'<0.2:", mpf('0.953386') * mpf('0.169524') * sqrt(mpf('0.000499')), " (3.61e-3)")
print("r_G*0.0004999 =", mpf('7.429e-4') * mpf('0.0004999'), " (>3.713e-7)")
print("Lambda'(1) =", mpf('2.75') + z12, " 1.28964?")

print("\n== hazard-H1 수치 ==")
def G(z): z = mpf(z); return mpf(1.5) * (1 - z) - mpf('1.1935') * log(2 / (1 + z)) - 1 / (1 + z) + mpf(0.5)
print("G(0.0537)=", G('0.0537'), " (>=0.205); G(0.571)=", G('0.571'), " (>=0.218)")
print("1.5-0.307(1-3/(2*6667)) =", mpf(1.5) - mpf('0.307') * (1 - 3 / (2 * mpf(6667))), " (<=1.1935)")
print("47/24+1.1935 =", mpf(47) / 24 + mpf('1.1935'), " (<=3.2); 3.2/6667=", mpf('3.2') / 6667)
k = 6667; qmax = int(floor(6 * mpf(k) ** (mpf(2) / 3))); qfb = (3 * (k - 1) // 4 - qmax - 3) // 8
qfb_exact = int(floor((mpf(3) * (k - 1) / 4 - qmax - 3) / 8))
print("k=6667: qmax", qmax, " qfb", qfb_exact, " (qfb+2)/k", mpf(qfb_exact + 2) / k, " lower bound 3/32-0.75k^-1/3+0.53/k:", mpf(3) / 32 - mpf(0.75) * mpf(k) ** (-mpf(1) / 3) + mpf('0.53') / k)
print("log(2/1.0537)=", log(2 / mpf('1.0537')), " 1/1.0537=", 1 / mpf('1.0537'), " log(2/1.571)=", log(2 / mpf('1.571')), " 1/1.571=", 1 / mpf('1.571'))

print("\n== 8.4 범위 수치 ==")
for k in [6668, 6667, 10000]:
    qmax = int(floor(6 * mpf(k) ** (mpf(2) / 3)))
    qfb = int(floor((mpf(3) * (k - 1) / 4 - qmax - 3) / 8))
    mfb = int(ceil(mpf(5) * k / 4)) + qmax
    print(f"k={k}: qmax={qmax}, qfb={qfb}, qfb<k/4? {qfb < k/4}, 2k+1-8qfb={2*k+1-8*qfb} >= mfb={mfb}? {2*k+1-8*qfb >= mfb}, k-2399>=qmax+300? {k-2399 >= qmax+300}, 3k/4>=2398+qmax? {3*k/4 >= 2398+qmax}, 6k^(2/3)<=k+3? {6*mpf(k)**(mpf(2)/3) <= k+3}")
print("6*216^(2/3) =", 6 * mpf(216) ** (mpf(2) / 3), " vs 217")
k = 422; print("k=422: 9(k+2) =", 9 * (k + 2), " 5(k+6k^(2/3)+1) =", 5 * (k + 6 * mpf(k) ** (mpf(2) / 3) + 1))
k = 421; print("k=421: 9(k+2) =", 9 * (k + 2), " 5(k+6k^(2/3)+1) =", 5 * (k + 6 * mpf(k) ** (mpf(2) / 3) + 1))
print("(6600/6599)^(2/3) =", (mpf(6600) / 6599) ** (mpf(2) / 3), " 3.6*that", mpf('3.6') * (mpf(6600) / 6599) ** (mpf(2) / 3))
print("(5+sqrt5)/2 =", (5 + sqrt(5)) / 2, "; (2pi)^-1/3 =", (2 * pi) ** (-mpf(1) / 3), "; (4 c2pi)^(2/3) =", (4 * c2pi) ** (mpf(2) / 3))
print("2/(3 sqrt3) =", 2 / (3 * sqrt(3)))
print("12927/1e5^(2/3) =", 12927 / mpf(10) ** (mpf(10) / 3))
