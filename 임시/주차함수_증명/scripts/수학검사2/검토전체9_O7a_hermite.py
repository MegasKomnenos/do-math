# (1) U_r, V_r closed forms vs exact Hermite numbers; (2) H_0,H_1,H_2 series; (3) H_3 sign
from fractions import Fraction as F
import math
def check_UV(k,nu):
    y=k; n=2*k+nu; N=n+y+1
    He=[F(1),F(N)]
    for j in range(2,n+1):
        He.append(N*He[j-1]-(j-1)*y*He[j-2])
    def M(r):
        # n! [Y^n] (1-Y)^{r+1} sum He_j Y^j/j!  (common factors e^{-y/2}/p_n dropped)
        s=F(0)
        for i in range(0,r+2):
            if n-i<0: continue
            s+=F(math.comb(r+1,i))*(-1)**i*He[n-i]*F(math.factorial(n),math.factorial(n-i))
        return s
    d=He[n]/He[n-1]-n
    M0,M2,M4=M(0),M(2),M(4)
    U2=1+F(2*nu+2,k)+F(nu*(nu+1),k*k); V2=4+F(4*nu+2,k)+F(nu*(nu+1),k*k)
    U4=1+F(4*nu+16,k)+F(6*nu*nu+30*nu+18,k**2)+F(4*nu**3+17*nu**2+15*nu+2,k**3)+F(nu*(nu+1)**3,k**4)
    V4=4+F(12*nu+38,k)+F(13*nu**2+49*nu+22,k**2)+F(6*nu**3+21*nu**2+17*nu+2,k**3)+F(nu*(nu+1)**3,k**4)
    print(k,nu,"M2/M0 ok:",M2/M0==U2-V2/d,"M4/M0 ok:",M4/M0==U4-V4/d, "d=",float(d))
    # (마) formula with y general: M2/M0 = 1-2n/y+n(n+1)/y^2-n(n+1)/(y^2 d)
    print("   (마) ok:", M2/M0==1-F(2*n,y)+F(n*(n+1),y*y)-F(n*(n+1),y*y)/d)
for k,nu in [(30,1),(30,5),(50,-1),(50,0),(80,7)]:
    check_UV(k,nu)
try:
    import sympy as sp
    w,nu,th=sp.symbols('w nu theta')
    Nk=3+(nu+1-th)*w
    x=w*(1-th*w)/Nk**2
    xn=(2+(nu-1)*w)*(1-th*w)/Nk**2
    g=sp.sqrt(1-4*xn)
    ups=(1+g)/2
    C1=(1-g)/(2*g**2); C2=-(1-g)*(5+g)/(4*g**5); C3=5*(1-g)*(6+g-g**2)/(4*g**8)
    uhat=ups+x*C1+x**2*C2+x**3*C3
    H=(Nk*uhat-2-nu*w)/w
    ser=sp.series(H,w,0,4).removeO()
    for j in range(0,4):
        print("H_%d ="%j, sp.factor(sp.expand(ser.coeff(w,j))))
    H3=sp.expand(ser.coeff(w,3))
    import itertools
    mx=max(float(H3.subs({nu:a,th:b})) for a in [1,2,5,10,50,100,300,600] for b in [0,0.5,1])
    print("max H3 over sample:",mx)
except Exception as e:
    print("sympy unavailable:",e)
