# L12 ch4 symbolic/numeric checks for the rational audit item
import sympy as sp, mpmath as mp
from fractions import Fraction
mp.mp.dps=30
# (ㅅ) rational
v=Fraction(699,100)-Fraction(7,2)-(6*Fraction(699,100)+Fraction(3,4))/31-(13*Fraction(699,100)/2)/961-12*Fraction(699,100)/30000
print("(나) value",v, v==Fraction(495594511,240250000), float(v))
a0=mp.mpf(3)**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3); a1=mp.mpf(3)**(-mp.mpf(1)/3)*mp.gamma(mp.mpf(2)/3)
print("a0",a0,"a1",a1)
k=mp.mpf(10000); print("(다)",mp.mpf('6.98')-mp.mpf('3.5')-(4*mp.mpf('6.98')+mp.mpf('0.5'))*mp.mpf('1.2879')*k**(-mp.mpf(1)/3)-13*mp.mpf('6.98')/2*mp.mpf('0.939')*k**(-mp.mpf(2)/3)-12*mp.mpf('6.98')/k)
print("final margin", mp.mpf('5.642')*mp.mpf('1.6809')*mp.mpf('0.39893')-mp.mpf('0.0163')-mp.mpf('3.554'))
print("14.653 check", 3/mp.sqrt(2*mp.pi)*(mp.mpf('8.133')+mp.mpf('10.301')/mp.sqrt(2*mp.pi)))
# (ㄴ) residual coefficients
x,g=sp.symbols('x gamma',positive=True)
def ups(gm): return (1+gm)/2
def C1(gm): return (1-ups(gm))/gm**2
def C2(gm): return -(1-ups(gm))*(2+ups(gm))/gm**5
def C3(gm): return sp.Rational(5,2)*(1-ups(gm))*(6+gm-gm**2)/gm**8
def uhat(gm): return ups(gm)+x*C1(gm)+x**2*C2(gm)+x**3*C3(gm)
iota=(1-g**2)/4
gm2=g*sp.sqrt(1+4*x/g**2)
R=(uhat(g)-1)*uhat(gm2)+iota
ser=sp.series(R,x,0,5).removeO()
for j in range(5):
    c=sp.simplify(sp.expand(ser.coeff(x,j)))
    print("x^%d coeff:"%j, c if j<4 else sp.nsimplify(c.subs(g,sp.Rational(1,3))))
# (ㄷ) g(kappa) series
kap,th,nu=sp.symbols('kappa theta nu')
Nt=3+(nu+1-th)*kap
xx=(1-th*kap)*kap/Nt**2
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
gam=sp.sqrt(1-4*xn)
def uhat2(gm,xv): return (1+gm)/2+xv*(1-(1+gm)/2)/gm**2-xv**2*(1-(1+gm)/2)*(2+(1+gm)/2)/gm**5+xv**3*sp.Rational(5,2)*(1-(1+gm)/2)*(6+gm-gm**2)/gm**8
G=(Nt*uhat2(gam,xx)-2-nu*kap)/kap
gs=sp.series(G,kap,0,5).removeO()
for j in range(5):
    c=sp.factor(sp.expand(sp.simplify(gs.coeff(kap,j))))
    print("g coeff kappa^%d:"%j, sp.expand(c))
    if j in (3,4):
        for nv in (0,-1):
            cc=sp.expand(c.subs(nu,nv)); f=sp.lambdify(th,cc,'mpmath')
            vals=[abs(f(mp.mpf(t)/1000)) for t in range(0,1001)]
            print("   nu",nv,"max|coef| on [0,1]:", max(vals))
