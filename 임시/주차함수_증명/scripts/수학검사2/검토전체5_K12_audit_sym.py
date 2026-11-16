# K12: D.central-gap-rational-audit (ㄴ)(ㄷ) -- symbolic checks with sympy
import sympy as sp
g, x = sp.symbols('gamma x', positive=True)
# (ㄴ): residual R(iota) = (uhat(iota)-1) uhat(iota-x) + iota, in terms of gamma=sqrt(1-4 iota)
def coeffs(gm):
    u = (1+gm)/2
    C1 = (1-u)/gm**2
    C2 = -(1-u)*(2+u)/gm**5
    C3 = 5*(1-u)*(6+gm-gm**2)/(2*gm**8)
    return u, C1, C2, C3
u, C1, C2, C3 = coeffs(g)
uhat = u + x*C1 + x**2*C2 + x**3*C3
gm2 = g*sp.sqrt(1+4*x/g**2)          # gamma(iota - x)
u2, D1, D2, D3 = coeffs(gm2)
uhat2 = u2 + x*D1 + x**2*D2 + x**3*D3
iota = (1-g**2)/4
R = (uhat-1)*uhat2 + iota
ser = sp.series(R, x, 0, 5).removeO()
for j in range(0, 5):
    c = sp.simplify(sp.expand(ser.coeff(x, j)))
    print("x^%d coefficient:" % j, c if j < 4 else "(Laurent poly) value at gamma=1/3 =", c.subs(g, sp.Rational(1, 3)) if j == 4 else "")
# also check the body's identities C1=(1-g)/(2g^2), C2=-(1-g)(5+g)/(4g^5), C3=5(1-g)(6+g-g^2)/(4g^8)
print("C1 id:", sp.simplify(C1-(1-g)/(2*g**2)) == 0, " C2 id:", sp.simplify(C2+(1-g)*(5+g)/(4*g**5)) == 0, " C3 id:", sp.simplify(C3-5*(1-g)*(6+g-g**2)/(4*g**8)) == 0)
print("C1,C2,C3 at gamma=1/3:", [c.subs(g, sp.Rational(1, 3)) for c in (C1, C2, C3)])
# (ㄷ): g(kappa) Taylor coefficients
k, th, nu = sp.symbols('kappa theta nu')
Nt = 3 + (nu+1-th)*k
xx = (1-th*k)*k/Nt**2
xn = (2+(nu-1)*k)*(1-th*k)/Nt**2
gam = sp.sqrt(1-4*xn)
uo, E1, E2, E3 = coeffs(gam)
uh = uo + xx*E1 + xx**2*E2 + xx**3*E3
gk = (Nt*uh - 2 - nu*k)/k
s = sp.series(gk, k, 0, 5).removeO()
for j in range(0, 5):
    c = sp.factor(sp.simplify(s.coeff(k, j)))
    print("g_%d =" % j, sp.expand(c))
g3 = sp.expand(s.coeff(k, 3)); g4 = sp.expand(s.coeff(k, 4))
import itertools
for nv in (-1, 0):
    p3 = sp.Poly(g3.subs(nu, nv), th); p4 = sp.Poly(g4.subs(nu, nv), th)
    m3 = max(abs(float(p3.eval(sp.Rational(i, 200)))) for i in range(201))
    m4 = max(abs(float(p4.eval(sp.Rational(i, 200)))) for i in range(201))
    print(f"nu={nv}: max|g3| on grid {m3:.1f}, max|g4| {m4:.1f}; g3(0)={float(p3.eval(0)):.1f}, g3(1)={float(p3.eval(1)):.1f}, g4(0)={float(p4.eval(0)):.1f}, g4(1)={float(p4.eval(1)):.1f}")
