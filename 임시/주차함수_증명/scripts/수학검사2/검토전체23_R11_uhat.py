import sympy as sp
g,x=sp.symbols('g x',positive=True)
def uhat(gam):
    u=(1+gam)/2
    C1=(1-u)/gam**2; C2=-(1-u)*(2+u)/gam**5; C3=5*(1-u)*(6+gam-gam**2)/(2*gam**8)
    return u+x*C1+x**2*C2+x**3*C3
iota=(1-g**2)/4
gm=g*sp.sqrt(1+4*x/g**2)
R=(uhat(g)-1)*uhat(gm)+iota
ser=sp.series(R,x,0,5).removeO()
for j in range(5):
    c=sp.simplify(ser.coeff(x,j))
    print(j, c if j<4 else sp.factor(c), (c.subs(g,sp.Rational(1,3)) if j==4 else ''))
