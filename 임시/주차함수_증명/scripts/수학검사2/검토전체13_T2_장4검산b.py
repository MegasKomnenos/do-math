import sys, math
sys.set_int_max_str_digits(0)
import sympy as sp
from math import sqrt, log
# Hermite lower bound (다) check at k=10000, y=k, n=2k and n=2k-1 ; also y=k-1
def check(k,y,n):
    N=n+y+1
    He0,He1=1,N
    for j in range(2,n+1):
        He0,He1=He1,N*He1-(j-1)*y*He0
    s=str(He1); logHe=math.log(10)*(len(s)-1)+math.log(float(s[0]+'.'+s[1:16]))
    q=n*y/N**2; xx=y/N**2
    uo=(1+sqrt(1-4*q))/2
    U=N*uo; W=N*(2*uo-1)
    bound=0.5*log(U/W)+n*log(U)+(N-U)**2/(2*y)-5.5*xx-350*n*xx**2
    print(k,y,n,"logHe-bound=",logHe-bound,"ok",logHe>=bound,"q",q,"x",xx,"5.5x+350nx^2*k",(5.5*xx+350*n*xx**2)*k)
    return He1,He0,N
for (k,y,n) in [(10000,10000,20000),(10000,10000,19999),(10000,9999,20000),(10000,9999,19999)]:
    check(k,y,n)
# identity line 270
k,nu,th=sp.symbols('k nu theta')
N=3*k+nu+1-th
print("id270:",sp.expand(2*N**2-9*(2*k+nu)*(k-th)-((3*nu+12+6*th)*k+2*(nu+1-th)**2+9*nu*th)))
# integrals 263-264
io=sp.symbols('iota',positive=True)
g=sp.sqrt(1-4*io); uo=(1+g)/2; C1=(1-uo)/g**2
print("int1:",sp.simplify(sp.diff(io*sp.log(uo)+(1-uo)**2/2,io)-sp.log(uo)))
print("int2:",sp.simplify(sp.diff(sp.log(uo)-sp.log(g)/2,io)-C1/uo))
# g(kappa) expansion
ka=sp.symbols('kappa')
Nt=3+(nu+1-th)*ka
x=(1-th*ka)*ka/Nt**2
xn=(2+(nu-1)*ka)*(1-th*ka)/Nt**2
gam=sp.sqrt(1-4*xn)
uo=(1+gam)/2
C1=(1-uo)/gam**2; C2=-(1-uo)*(2+uo)/gam**5; C3=sp.Rational(5)*(1-uo)*(6+gam-gam**2)/(2*gam**8)
uhat=uo+x*C1+x**2*C2+x**3*C3
gfun=(Nt*uhat-2-nu*ka)/ka
ser=sp.series(gfun,ka,0,3).removeO()
for p in range(0,3):
    print("g coeff kappa^%d:"%p, sp.factor(sp.simplify(ser.coeff(ka,p))))
