# R2 검산: 보조정리 4:gauss-contraction 의 기호 항등식과 수치 상계
import sympy as sp
g, x, io = sp.symbols('gamma x iota', positive=True)
# gamma = sqrt(1-4 iota); d/d iota = -(2/gamma) d/d gamma
def D(f, n=1):
    for _ in range(n):
        f = sp.simplify(-2/g*sp.diff(f, g))
    return f
u0 = (1+g)/2
C1 = (1-u0)/g**2
C2 = -(1-u0)*(2+u0)/g**5
C3 = 5*(1-u0)*(6+g-g**2)/(2*g**8)
print('C at 1/3:', [c.subs(g, sp.Rational(1,3)) for c in (C1, C2, C3)])
print("u0'''' :", sp.simplify(D(u0,4) - (-120*g**-7)))
print("C1''' :", sp.simplify(D(C1,3) - (192*g**-8-60*g**-7)))
print("C2'' :", sp.simplify(D(C2,2) + (175*g**-9-96*g**-8-15*g**-7)))
print("C3' :", sp.simplify(D(C3,1) - sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7)))
m1 = sp.simplify(C1 - D(u0))
m2 = sp.simplify(C2 - D(C1) + D(u0,2)/2)
m3 = sp.simplify(C3 - D(C2) + D(C1,2)/2 - D(u0,3)/6)
print('m1:', sp.simplify(m1-u0/g**2), 'm2:', sp.simplify(m2-(C2-2/g**4)), 'm3:', sp.simplify(m3-(C3+5*(5-g**2)/(2*g**7))))
# residual: (uhat(iota)-1)*uhat(iota-x)+iota ; coefficients of x^0..x^3
iota = (1-g**2)/4
A = (u0-1) + x*C1 + x**2*C2 + x**3*C3
Bser = u0 + x*m1 + x**2*m2 + x**3*m3
prod = sp.expand(A*Bser)
for j in range(4):
    cj = prod.coeff(x, j) + (iota if j == 0 else 0)
    print('R coeff x^%d:' % j, sp.simplify(cj))
# sup over gamma in [1/3,1] of |m_i|, |C_i| numerically
import mpmath as mp
for name, f in (('m1', m1), ('m2', m2), ('m3', m3), ('C1', C1), ('C2', C2), ('C3', C3)):
    fl = sp.lambdify(g, f, 'mpmath')
    vals = [abs(fl(mp.mpf(1)/3 + (mp.mpf(2)/3)*i/20000)) for i in range(20001)]
    mono = all(vals[i] >= vals[i+1] for i in range(20000))
    print(name, 'sup|.|=', max(vals), 'at 1/3:', vals[0], 'monotone decreasing:', mono)
# log-derivative formulas
for name, f, ld in (('C1', C1, -1/(1-g)-2/g), ('C2', -C2, -1/(1-g)+1/(5+g)-5/g), ('C3', C3, -1/(1-g)+(1-2*g)/(6+g-g**2)-8/g)):
    print(name, 'logderiv diff:', sp.simplify(sp.diff(sp.log(f), g) - ld))
# numeric totals
t = 10935+231822+2053593+9032310
print('t sum', t, 468018 + 291 + 1 + (sp.Rational(1,3)+sp.Rational(4,10**5))*t)
xm = sp.Rational(112, 10**7)
print('x5 term', float((216*60750+34020*378)*xm), 'x6 term', float(34020*60750*xm**2))
print('contraction', float(sp.Rational(2,9)/(sp.Rational(4,9)-144*xm**2)), 'resid', float(4.25e6/(2/3-216*float(xm)**2)))
print('k/(3k-1)^2 at 1e4', 10000/29999**2)
