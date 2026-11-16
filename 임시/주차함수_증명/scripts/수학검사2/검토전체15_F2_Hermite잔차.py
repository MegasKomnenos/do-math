# F2 검산: 보조정리 gauss-contraction (나)의 잔차 R(iota)의 x^0..x^3 계수가 항등적으로 0인지, 도함수 식과 상수 확인
import sympy as sp
g,x=sp.symbols('gamma x',positive=True)
u0=(1+g)/2
C1=(1-u0)/g**2; C2=-(1-u0)*(2+u0)/g**5; C3=sp.Rational(5,1)*(1-u0)*(6+g-g**2)/(2*g**8)
def D(f):  # d/d iota via gamma' = -2/gamma
    return sp.diff(f,g)*(-2/g)
# uhat(iota) and uhat(iota - x) as series in x: expand each coefficient function around iota
def shift(f,order=7):  # f(iota - x) Taylor in x
    s=0; d=f
    for m in range(order+1):
        s+= (-x)**m/sp.factorial(m)*d
        d=D(d)
    return s
uhat = u0 + x*C1 + x**2*C2 + x**3*C3
uhat_sh = shift(u0) + x*shift(C1) + x**2*shift(C2) + x**3*shift(C3)
iota=(1-g**2)/4
R=sp.expand((uhat-1)*uhat_sh + iota)
for m in range(0,4):
    print("x^%d coeff:"%m, sp.simplify(R.coeff(x,m)))
# derivative formulas
print(sp.simplify(D(D(D(D(u0)))) - (-120*g**-7)))
print(sp.simplify(D(D(D(C1))) - (192*g**-8-60*g**-7)))
print(sp.simplify(D(D(C2)) + (175*g**-9-96*g**-8-15*g**-7)))
print(sp.simplify(D(C3) - sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7)))
# m1,m2,m3
m1=sp.simplify(-D(u0)+C1); m2=sp.simplify(D(D(u0))/2 - D(C1) + C2); m3=sp.simplify(-D(D(D(u0)))/6 + D(D(C1))/2 - D(C2) + C3)
print(sp.simplify(m1-u0/g**2), sp.simplify(m2-(C2-2/g**4)), sp.simplify(m3-(C3+sp.Rational(5,2)*(5-g**2)/g**7)))
third=sp.Rational(1,3)
print([sp.N(f.subs(g,third)) for f in (C1,C2,C3,m1,m2,m3)])
