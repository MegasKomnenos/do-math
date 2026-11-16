# -*- coding: utf-8 -*-
"""T7a 검산: 보조정리 hermite-nu의 H_0,H_1,H_2,H_3 전개, U_r/V_r 닫힌 꼴, M_0 하계."""
import sympy as sp
w, th, nu, d, n, y = sp.symbols('w theta nu d n y')
# w = 1/k
Nk = 3 + (nu+1-th)*w                      # N/k
x = w*(1-th*w)/Nk**2                       # frak x
xn = (2+(nu-1)*w)*(1-th*w)/Nk**2           # frak x_n
g = sp.sqrt(1-4*xn)                        # gamma
ups0 = (1+g)/2
C1 = (1-ups0)/g**2
C2 = -(1-ups0)*(2+ups0)/g**5
C3 = 5*(1-ups0)*(6+g-g**2)/(2*g**8)
uhat = ups0 + x*C1 + x**2*C2 + x**3*C3
H = (Nk*uhat - 2 - nu*w)/w
ser = sp.series(H, w, 0, 4).removeO()
ser = sp.expand(ser)
for j in range(0, 4):
    print("H_%d =" % j, sp.factor(sp.simplify(ser.coeff(w, j))))
H3 = sp.simplify(ser.coeff(w, 3))
# sign of H3 on nu in [1,600], theta in [0,1]
vals = [H3.subs({nu: a, th: b}) for a in (1, 50, 300, 600) for b in (0, 1)]
print("H_3 samples:", [float(v) for v in vals])

# U_r, V_r: M_r/M_0 via Hermite recurrence He_{j-1} = (N He_j - He_{j+1})/(y j), with He_n/He_{n-1} = n + d
N = n + y + 1
He_n, He_nm1 = sp.Symbol('Hn'), sp.Symbol('Hm')
He = {n: He_n, n-1: He_nm1}
def Hem(i):  # He_{n-i}
    if i == 0: return He_n
    if i == 1: return He_nm1
    return sp.simplify((N*Hem(i-1) - Hem(i-2))/(y*(n-i+1)))
def Mr_over_M0(r):
    num = sum(sp.binomial(r+1, i)*(-1)**i*sp.ff(n, i)*Hem(i) for i in range(r+2))
    den = He_n - n*He_nm1
    ratio = sp.simplify((num/den).subs(He_n, (n+d)*He_nm1))
    return sp.simplify(ratio)
k = sp.Symbol('k')
for r in (2, 4):
    R = Mr_over_M0(r).subs({y: k, n: 2*k+nu})
    R = sp.simplify(R)
    # write as U - V/d
    U = sp.simplify(R.subs(d, sp.oo)) if False else None
    Rd = sp.together(R)
    numR, denR = sp.fraction(Rd)
    # R = (A d + B)/(C d) form?
    polyd = sp.Poly(sp.expand(numR), d)
    A, B = polyd.coeff_monomial(d), polyd.coeff_monomial(1)
    C = sp.Poly(sp.expand(denR), d).coeff_monomial(d)
    Ur = sp.expand(sp.simplify(A/C)); Vr = sp.expand(sp.simplify(-B/C))
    print("U_%d =" % r, sp.collect(sp.expand(Ur), k)); print("V_%d =" % r, sp.collect(sp.expand(Vr), k))
# general y: M2/M0
R2 = Mr_over_M0(2)
print("M2/M0 general:", sp.simplify(R2 - (1 - 2*n/y + n*(n+1)/y**2 - n*(n+1)/(y**2*d))))
# k-coefficient 20 claim: n(n+1) - d_y[(n-y)^2+n] with d_y = 4 - (26+4nu+8theta)/k, y = k - theta, n = 2k+nu
dy = 4 - (26+4*nu+8*th)/k
expr = sp.expand((2*k+nu)*(2*k+nu+1) - dy*(((2*k+nu)-(k-th))**2 + (2*k+nu)))
print("k-coeff:", sp.Poly(expr, k).coeff_monomial(k), " k^2-coeff:", sp.Poly(expr, k).coeff_monomial(k**2))

# numeric M_0 check with mpmath
import mpmath as mp
mp.mp.dps = 60
def M0_exact(kk, nuv):
    nn = 2*kk+nuv; NN = mp.mpf(nn+kk+1)
    h0, h1 = mp.mpf(1), NN
    for j in range(2, nn+1):
        h0, h1 = h1, NN*h1 - (j-1)*kk*h0
    dd = h1/h0 - nn
    # M0 = e^{-k/2} He_n d /((n+d) p_n), p_n=(n+1)^{n-1}; compute via logs
    logM0 = -mp.mpf(kk)/2 + mp.log(h1) + mp.log(dd) - mp.log(nn+dd) - (nn-1)*mp.log(nn+1)
    return mp.e**logM0, dd
for kk, nuv in [(10000, 1), (10000, 19), (10000, 100), (10000, 600), (12000, 59)]:
    M0, dd = M0_exact(kk, nuv)
    lb = 4*mp.sqrt(2)*(1-(mp.mpf('23.75')+mp.mpf('2.5')*nuv)/kk)
    dlb = 4 - (26+4*nuv)/mp.mpf(kk)
    print("k=%d nu=%d: M0=%s lb=%s ok=%s ; d=%s in [%s,4) ok=%s" % (kk, nuv, mp.nstr(M0, 10), mp.nstr(lb, 10), M0 >= lb, mp.nstr(dd, 12), mp.nstr(dlb, 10), dlb <= dd < 4))
