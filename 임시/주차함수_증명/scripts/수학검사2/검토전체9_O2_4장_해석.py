# O2 검산: 4장 4.3절 해석 연쇄 (4.9), M4/M0, g(kappa) 전개, Hermite 수치, Borel 합 전개, (4.11), F0·F1 적분, 따름정리 수치
import sympy as sp
from fractions import Fraction
import mpmath as mp

# --- (4.9) and M4/M0 via Hermite recursion, symbolic ---
n, y, th = sp.symbols('n y vartheta', positive=True)
N = n + y + 1
Hn1 = sp.Integer(1); Hn = n + th
Hn2 = (N*Hn1 - Hn)/((n-1)*y); Hn3 = (N*Hn2 - Hn1)/((n-2)*y)
Hn4 = (N*Hn3 - Hn2)/((n-3)*y); Hn5 = (N*Hn4 - Hn3)/((n-4)*y)
Hs = [Hn, Hn1, Hn2, Hn3, Hn4, Hn5]
def numer(r): return sum(sp.binomial(r+1, i)*(-1)**i*sp.ff(n, i)*Hs[i] for i in range(r+2))
ratio2 = sp.cancel(numer(2)/numer(0))
target2 = (th*((n-y)**2 + n) - n*(n+1))/(y**2*th)
print("(4.9) check:", sp.cancel(ratio2 - target2) == 0, flush=True)
ratio4 = sp.cancel(numer(4)/numer(0))
k = sp.symbols('k', positive=True)
for nu in (0, -1):
    r4 = sp.cancel(ratio4.subs({n: 2*k+nu, y: k}))
    tgt = (1 + 16/k + 18/k**2 + 2/k**3 - (4 + 38/k + 22/k**2 + 2/k**3)/th) if nu == 0 else (1 + 12/k - 6/k**2 - (4 + 26/k - 14/k**2)/th)
    print("M4/M0 nu=%d check:" % nu, sp.cancel(r4 - tgt) == 0, flush=True)
    vth = (4 - 26/k + 506/k**2) if nu == 0 else (4 - 22/k + 414/k**2)
    e = sp.symbols('e')  # e = 1/k
    expr = sp.cancel(tgt.subs(th, vth).subs(k, 1/e))
    print("  central: series in 1/k:", sp.series(expr, e, 0, 4), flush=True)

# --- g(kappa) Taylor coefficients at rational nu, theta (numeric-symbolic) ---
ka = sp.symbols('kappa')
def gcoeffs(nu_v, th_v):
    Nt = 3 + (nu_v + 1 - th_v)*ka
    x = (1 - th_v*ka)*ka/Nt**2
    xn = (2 + (nu_v - 1)*ka)*(1 - th_v*ka)/Nt**2
    gam = sp.sqrt(1 - 4*xn); ups = (1 + gam)/2
    C1 = (1 - ups)/gam**2; C2 = -(1 - ups)*(2 + ups)/gam**5; C3 = 5*(1 - ups)*(6 + gam - gam**2)/(2*gam**8)
    uhat = ups + x*C1 + x**2*C2 + x**3*C3
    g = (Nt*uhat - 2 - nu_v*ka)/ka
    s = sp.series(g, ka, 0, 3).removeO()
    return [sp.nsimplify(sp.simplify(s.coeff(ka, d))) for d in range(3)]
for nu_v in (0, -1):
    for th_v in (0, sp.Rational(1, 2), 1):
        c = gcoeffs(nu_v, th_v)
        pred = [4, -(26 + 4*nu_v + 8*th_v), 506 + 97*nu_v + 5*nu_v**2 + (168 + 16*nu_v)*th_v + 12*th_v**2]
        print("g coeffs nu=%d theta=%s:" % (nu_v, th_v), c, "match:", [sp.simplify(a-b) == 0 for a, b in zip(c, pred)], flush=True)

# --- Hermite numerics at k=10000 (y=k, theta=0) ---
mp.mp.dps = 50
for nn in (20000, 19999):
    kk = 10000; Nn = mp.mpf(nn + kk + 1)
    He_prev, He = mp.mpf(1), Nn
    for j in range(2, nn+1):
        He_prev, He = He, Nn*He - (j-1)*kk*He_prev
    vth = He/He_prev - nn; nu = nn - 2*kk
    center = 4 - (26 + 4*nu)/mp.mpf(kk) + (506 + 97*nu + 5*nu**2)/mp.mpf(kk)**2
    h0 = nn + vth; h1 = mp.mpf(1)
    h2 = (Nn*h1 - h0)/((nn-1)*kk); h3 = (Nn*h2 - h1)/((nn-2)*kk); h4 = (Nn*h3 - h2)/((nn-3)*kk); h5 = (Nn*h4 - h3)/((nn-4)*kk)
    hs = [h0, h1, h2, h3, h4, h5]
    def num(r): return sum(mp.binomial(r+1, i)*(-1)**i*mp.ff(nn, i)*hs[i] for i in range(r+2))
    logM0 = -mp.mpf(kk)/2 + mp.log(He_prev) + mp.log(vth) - (nn-1)*mp.log(nn+1)
    print("k=10000 nu=%d: vartheta=%s k^2(vth-center)=%s  kM2/M0=%s  k^2M4/M0=%s  M0=%s  g_k=%s" % (
        nu, mp.nstr(vth, 12), mp.nstr(kk**2*(vth-center), 5), mp.nstr(num(2)/num(0)*kk, 8), mp.nstr(num(4)/num(0)*kk**2, 8),
        mp.nstr(mp.e**logM0, 8), mp.nstr(2 - kk*num(2)/num(0), 7)), flush=True)
print("4sqrt2(1-26/10000) =", mp.nstr(4*mp.sqrt(2)*(1-mp.mpf(26)/10000), 8), flush=True)

# --- Borel sums ---
mp.mp.dps = 25
def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
for kk in (1000, 10000):
    Bs = [Bor(j) for j in range(1, kk+1)]
    S1 = mp.fsum((j+1)*Bs[j] for j in range(kk)); pred = 2*mp.sqrt(kk/(2*mp.pi)) - mp.mpf(2)/3
    print("k=%d: sum jBor - pred = %s (bound %s); 2(2pi)^-1/2k^-1/2 - tail = %s (bound %s)" % (
        kk, mp.nstr(S1-pred, 5), mp.nstr(mp.mpf(2)/3/mp.sqrt(2*mp.pi*kk), 5),
        mp.nstr(2/mp.sqrt(2*mp.pi*kk) - (1 - mp.fsum(Bs)), 5), mp.nstr(mp.mpf(5)/9/mp.sqrt(2*mp.pi)/mp.mpf(kk)**1.5, 5)), flush=True)
    if kk == 10000:
        def Bsum(phi): return mp.fsum(Bs[j-1]*mp.e**(-phi*j/kk) for j in range(1, kk+1))
        def Bld(phi): return 2 + mp.quad(lambda w: w**(-1.5)*(1 - mp.e**(-phi*w)), [0, 1])
        for phi in (mp.mpf(-2), mp.mpc(-2, 1), mp.mpc(-0.5, 0.3)):
            lhs = abs(Bsum(phi) - 1 + Bld(phi)/mp.sqrt(2*mp.pi*kk) - mp.mpf(2)/3*phi/kk)
            rhs = mp.e**(-mp.re(phi))*(mp.mpf(5)/9 + mp.mpf(2)/3*abs(phi) + mp.mpf(13)/12*abs(phi)**2)/mp.sqrt(2*mp.pi)/mp.mpf(kk)**1.5
            print("(4.11) phi=%s: lhs=%s rhs=%s ok=%s" % (phi, mp.nstr(lhs, 4), mp.nstr(rhs, 4), lhs <= rhs), flush=True)

# --- F0, F1 integrals (Dawson via erfi) ---
mp.mp.dps = 15
ninf = 2/mp.sqrt(mp.pi)
def Dawson(b): return mp.sqrt(mp.pi/2)*mp.e**(-b*b/2)*mp.erfi(b/mp.sqrt(2))
def BldR(b): return mp.e**(b*b/2)*(2 - 2*b*Dawson(b))
def Pq(z, r): mu = 1 - r*r; return mu*z*z + mu*mu*z**4/4
def F0(z): return -ninf*z**4*mp.e**(-z*z)*mp.quad(lambda r: r*r*mp.e**((1-r*r)*z*z/2)*Pq(z, r)*BldR(r*z)/mp.sqrt(2*mp.pi), [0, 1])
def F1(z): return -ninf*z**4*mp.e**(-z*z)*mp.quad(lambda r: r*r*mp.e**((1-r*r)*z*z/2)*Pq(z, r)*(mp.mpf(4)/3*r*r*z*z - mp.mpf(2)/3*r*z**4), [0, 1])
I0 = 2*mp.quad(F0, [0, 1, 2, 3, 5, 8]); I1 = 2*mp.quad(F1, [0, 1, 2, 3, 5, 8])
print("int F0 =", mp.nstr(I0, 6), " int F1 =", mp.nstr(I1, 8), " 46sqrt2-12 =", mp.nstr(46*mp.sqrt(2)-12, 8), flush=True)
b = mp.mpf('0.7'); direct = 2 + mp.quad(lambda w: w**(-1.5)*(1 - mp.e**(b*b*w/2)), [0, 1])
print("BldR identity at 0.7:", mp.nstr(direct, 10), mp.nstr(BldR(b), 10), flush=True)

# --- 따름정리 gauss-coeff-numeric ---
om = Fraction(699, 100)
val = om - Fraction(7, 2) - (4*om + Fraction(1, 2))*Fraction(3, 2)/31 - Fraction(13, 2)*om/961 - 12*om/30000
print("(나):", val, val == Fraction(495594511, 240250000), float(val))
om = Fraction(698, 100); a0 = Fraction(12879, 10000); a1 = Fraction(939, 1000); k13 = Fraction(464159, 10**7)
val2 = om - Fraction(7, 2) - (4*om + Fraction(1, 2))*a0*k13 - Fraction(13, 2)*om*a1*k13**2 - 12*om/10000
print("(다):", float(val2), ">=1.6809:", val2 >= Fraction(16809, 10000))
mp.mp.dps = 20
print("a0 =", mp.nstr(mp.quad(lambda w: mp.e**(-w**3/3), [0, mp.inf]), 10), " a1 =", mp.nstr(mp.quad(lambda w: w*mp.e**(-w**3/3), [0, mp.inf]), 10))
print("Bor(10000)k^1.5 =", mp.nstr(Bor(10000)*mp.mpf(10000)**1.5, 9), " (2pi)^-1/2(1-1/120000) =", mp.nstr((1-mp.mpf(1)/120000)/mp.sqrt(2*mp.pi), 9))
