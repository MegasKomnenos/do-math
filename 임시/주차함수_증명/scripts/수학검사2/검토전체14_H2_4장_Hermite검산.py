# H2: 보조정리 gauss-contraction (4.3절) 기호·수치 검산
import sympy as sp
g=sp.symbols('gamma',positive=True)
# iota = (1-g^2)/4, d gamma/d iota = -2/gamma
def D(expr):  # d/d iota
    return sp.simplify(sp.diff(expr,g)*(-2/g))
ups=(1+g)/2
C1=(1-ups)/g**2
C2=-(1-ups)*(2+ups)/g**5
C3=sp.Rational(5,1)*(1-ups)*(6+g-g**2)/(2*g**8)
print("C1,C2,C3 in gamma:",sp.simplify(C1-(1-g)/(2*g**2)),sp.simplify(C2+(1-g)*(5+g)/(4*g**5)),sp.simplify(C3-5*(1-g)*(6+g-g**2)/(4*g**8)))
print("values at 1/3:",[sp.nsimplify(c.subs(g,sp.Rational(1,3))) for c in (C1,C2,C3)])
# derivatives
print("ups'''' :",sp.simplify(D(D(D(D(ups))))+120*g**-7))
print("C1''' :",sp.simplify(D(D(D(C1)))-(192*g**-8-60*g**-7)))
print("C2'' :",sp.simplify(D(D(C2))+(175*g**-9-96*g**-8-15*g**-7)))
print("C3' :",sp.simplify(D(C3)-sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7)))
# Taylor coefficients of uhat(iota - x) in x
x=sp.symbols('x')
Cs=[ups,C1,C2,C3]
# uhat(iota-x) = sum_i x^i C_i(iota-x) ; expand to order 3
def taylor_shift(f,order):
    # f(iota - x) = sum_m (-x)^m f^{(m)}/m!
    out=0; d=f
    for m in range(order+1):
        out+= (-x)**m*d/sp.factorial(m); d=D(d)
    return out
uh_shift=sum(x**i*taylor_shift(Cs[i],3-i) for i in range(4))
uh_shift=sp.expand(uh_shift)
m=[sp.simplify(uh_shift.coeff(x,i)) for i in range(4)]
print("m1:",sp.simplify(m[1]-ups/g**2))
print("m2:",sp.simplify(m[2]-(C2-2/g**4)))
print("m3:",sp.simplify(m[3]-(C3+5*(5-g**2)/(2*g**7))))
# residual R = (uhat(iota)-1)*uhat(iota-x)+iota, coefficients x^0..x^3
uh=ups+x*C1+x**2*C2+x**3*C3
iota=(1-g**2)/4
R=sp.expand((uh-1)*uh_shift+iota)
for i in range(4):
    print("R coeff x^%d:"%i, sp.simplify(R.coeff(x,i)))
# bounds on m over gamma in [1/3,1]
import numpy as np
gs=np.linspace(1/3,1,20001)
for name,e in [("m1",m[1]),("m2",m[2]),("m3",m[3]),("C1",C1),("C2",C2),("C3",C3)]:
    f=sp.lambdify(g,e,'numpy'); v=f(gs); print(name,"max|.|=",np.abs(v).max(), "at 1/3:",float(e.subs(g,sp.Rational(1,3))))
# numeric totals
print(3*60750+216*378+34020*6, (216*60750+34020*378)*1.12e-5, 34020*60750*(1.12e-5)**2)
print(10935+231822+2053593+9032310)
tot=468018+291+1+(1/3+4e-5)*11328660; print("total",tot)
print("contraction",(2/9)/(4/9-144*(1.12e-5)**2), 4.25e6/(2/3-216*(1.12e-5)**2), 7e6/(1-0.51))
print("x at k=10000:",10000/29999**2)
print("nu=-1 sum:",(11/2/9+350*2/81)*(1-1/30000)**-4)
