import sympy as sp
n,y,N,th,Hn,Hn1 = sp.symbols('n y N vartheta He_n He_n1', positive=True)
# He_{n-1}=Hn1, He_n = Hn = (n+th)*Hn1 ; N = n+y+1
Hn = (n+th)*Hn1
Nv = n+y+1
Hn2 = (Nv*Hn1 - Hn)/((n-1)*y)
Hn3 = (Nv*Hn2 - Hn1)/((n-2)*y)
num2 = Hn - 3*n*Hn1 + 3*n*(n-1)*Hn2 - n*(n-1)*(n-2)*Hn3
den = Hn - n*Hn1
r2 = sp.simplify(num2/den)
target = (th*((n-y)**2+n) - n*(n+1))/(y**2*th)
print("(4.9) ok:", sp.simplify(r2-target)==0)
# M4/M0: numerator n![Y^n](1-Y)^5 B = sum_{i} C(5,i)(-1)^i n!/(n-i)! He_{n-i}
Hn4 = (Nv*Hn3 - Hn2)/((n-3)*y)
Hn5 = (Nv*Hn4 - Hn3)/((n-4)*y)
Hs=[Hn,Hn1,Hn2,Hn3,Hn4,Hn5]
num4 = sum(sp.binomial(5,i)*(-1)**i*sp.ff(n,i)*Hs[i] for i in range(6))
r4 = sp.simplify(num4/den)
k=sp.symbols('k',positive=True)
for nu in (0,-1):
    expr = sp.simplify(r4.subs({n:2*k+nu, y:k}))
    # write as A + B/th
    A = sp.simplify(sp.limit(expr, th, sp.oo))
    B = sp.simplify(sp.expand((expr - A)*th))
    print("nu=",nu," A=",sp.expand(A)," B=",sp.expand(B))
    # plug central value
    thc = {0: 4-26/k+506/k**2, -1: 4-22/k+414/k**2}[nu]
    val = sp.series(sp.simplify(expr.subs(th,thc)), k, sp.oo, 4)
    print("   expansion with center:", val)
# a0,a1
import mpmath as mp
mp.mp.dps=30
a0 = mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1 = mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
print("a0",a0,"a1",a1, 3**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3), 3**(-mp.mpf(1)/3)*mp.gamma(mp.mpf(2)/3))
# 0.39893 = 1/sqrt(2pi)?
print(1/mp.sqrt(2*mp.pi))
# fraction check
from fractions import Fraction
print(Fraction(495594511,240250000)>2, float(Fraction(495594511,240250000)))
# check constants at gamma=1/3
g=sp.Rational(1,3)
C1=(1-g)/(2*g**2); C2=-(1-g)*(5+g)/(4*g**5); C3=5*(1-g)*(6+g-g**2)/(4*g**8)
print(C1,C2,C3)
