import sympy as sp
x,i=sp.symbols('x iota')
g=sp.sqrt(1-4*i); u=(1+g)/2
C1=(1-u)/g**2; C2=-(1-u)*(2+u)/g**5; C3=sp.Rational(5,1)*(1-u)*(6+g-g**2)/(2*g**8)
def uhat(t): 
    gg=sp.sqrt(1-4*t); uu=(1+gg)/2
    c1=(1-uu)/gg**2; c2=-(1-uu)*(2+uu)/gg**5; c3=5*(1-uu)*(6+gg-gg**2)/(2*gg**8)
    return uu+x*c1+x**2*c2+x**3*c3
R=(uhat(i)-1)*uhat(i-x)+i
ser=sp.series(R,x,0,5).removeO()
for j in range(5):
    c=sp.simplify(ser.coeff(x,j))
    val=sp.nsimplify(sp.simplify(c.subs(i,sp.Rational(2,9))))  # gamma=1/3 <-> iota=2/9
    print(j, 'identically zero:' , sp.simplify(c)==0, ' at gamma=1/3:', val)
