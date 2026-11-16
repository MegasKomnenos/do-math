import sympy as sp
e,nu,th=sp.symbols('epsilon nu theta')
Nk=3+(nu+1-th)*e              # N/k
x=e*(1-th*e)/Nk**2            # x = y/N^2 (y=k-theta), divided... x = (k-theta)/N^2 = e(1-th e)/(Nk^2)
xn=(2/e+nu-1)*x               # (n-1)x
g=sp.sqrt(1-4*xn)
u0=(1+g)/2
C1=(1-u0)/g**2; C2=-(1-u0)*(2+u0)/g**5; C3=sp.Rational(5,2)*(1-u0)*(6+g-g**2)/g**8
uh=u0+x*C1+x**2*C2+x**3*C3
H=(Nk*uh-2-nu*e)/e
ser=sp.series(H,e,0,3).removeO()
for j in range(3):
    print(j, sp.factor(sp.expand(ser.coeff(e,j))))
