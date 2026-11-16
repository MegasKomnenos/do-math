# -*- coding: utf-8 -*-
"""T7a 검산: (마)의 k-계수 20과 (다)의 M_0 하계·d 구간의 수치 확인."""
import sympy as sp
k, nu, th = sp.symbols('k nu theta')
dy = 4 - (26+4*nu+8*th)/k
expr = sp.expand(k*((2*k+nu)*(2*k+nu+1) - dy*(((2*k+nu)-(k-th))**2 + (2*k+nu))))  # times k
P = sp.Poly(expr, k)
print("k^3 coeff (=k^2 of original):", P.coeff_monomial(k**3), "; k^2 coeff (=k of original):", sp.factor(P.coeff_monomial(k**2)))
import mpmath as mp
mp.mp.dps = 50
def M0_exact(kk, nuv):
    nn = 2*kk+nuv; NN = mp.mpf(nn+kk+1)
    h0, h1 = mp.mpf(1), NN
    for j in range(2, nn+1):
        h0, h1 = h1, NN*h1 - (j-1)*kk*h0
    dd = h1/h0 - nn
    logM0 = -mp.mpf(kk)/2 + mp.log(h1) + mp.log(dd) - mp.log(nn+dd) - (nn-1)*mp.log(nn+1)
    return mp.e**logM0, dd
for kk, nuv in [(10000, 1), (10000, 19), (10000, 100), (10000, 600), (12000, 59), (10000, 0), (10000, -1)]:
    M0, dd = M0_exact(kk, nuv)
    lb = 4*mp.sqrt(2)*(1-(mp.mpf('23.75')+mp.mpf('2.5')*nuv)/kk)
    dlb = 4 - (26+4*nuv)/mp.mpf(kk)
    H2 = 506+97*nuv+5*nuv**2
    approx = 4 - (26+4*nuv)/mp.mpf(kk) + H2/mp.mpf(kk)**2
    print("k=%d nu=%d: M0=%s lb=%s ok=%s ; d=%s  approx(H0..H2)=%s  dlb=%s ok=%s" % (kk, nuv, mp.nstr(M0, 10), mp.nstr(lb, 10), M0 >= lb, mp.nstr(dd, 12), mp.nstr(approx, 12), mp.nstr(dlb, 10), dlb <= dd < 4))
# M2/M0 and g_k at k=10000, nu=1..40: check k*M2/M0 < -(omega-2) with omega=6.98 (nu<=27), 6.975 (28..38), 6.97 (39,40)
for nuv in (1, 19, 27, 28, 38, 40):
    kk = 10000 if nuv <= 19 else 11100
    M0, dd = M0_exact(kk, nuv)
    U2 = 1 + (2*nuv+2)/mp.mpf(kk) + nuv*(nuv+1)/mp.mpf(kk)**2
    V2 = 4 + (4*nuv+2)/mp.mpf(kk) + nuv*(nuv+1)/mp.mpf(kk)**2
    r = U2 - V2/dd
    om = 6.98 if nuv <= 27 else (6.975 if nuv <= 38 else 6.97)
    print("k=%d nu=%d: k*M2/M0=%s  need < %s : %s" % (kk, nuv, mp.nstr(kk*r, 8), -(om-2), kk*r < -(om-2)))
