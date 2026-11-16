# Q2: 4장 검산 — (4.9), M4/M0, P의 계수, a0/a1, 수치 귀결, 조립 수치 (기호·정확 산술)
import sympy as sp
from fractions import Fraction as Fr
n,y,th,k,nu,theta,H = sp.symbols('n y vartheta k nu theta H')
N = n+y+1
He = {}
He[-1] = H; He[0] = (n+th)*H           # He_{n-1}, He_n  (index = offset from n-1)
# backwards: He_{j-2} = (N He_{j-1} - He_j)/((j-1) y)
He[-2] = (N*He[-1]-He[0])/((n-1)*y)
He[-3] = (N*He[-2]-He[-1])/((n-2)*y)
He[-4] = (N*He[-3]-He[-2])/((n-3)*y)
He[-5] = (N*He[-4]-He[-3])/((n-4)*y)
def ff(m,i): # falling factorial n(n-1)...(n-i+1)
    r=1
    for t in range(i): r*= (m-t)
    return r
def num(r):  # n! [Y^n] (1-Y)^{r+1} B(Y) = sum_i (-1)^i C(r+1,i) n(n-1)..(n-i+1) He_{n-i}
    return sum((-1)**i*sp.binomial(r+1,i)*ff(n,i)*He[-i] for i in range(r+2))
ratio2 = sp.cancel(num(2)/num(0))
claim2 = (th*((n-y)**2+n)-n*(n+1))/(y**2*th)
print("(4.9) ok:", sp.cancel(ratio2-claim2)==0, flush=True)
ratio4 = sp.cancel(num(4)/num(0))
for nuv in (0,-1):
    r = sp.cancel(ratio4.subs({n:2*k+nuv, y:k}))
    cl = (1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/th) if nuv==0 else (1+12/k-6/k**2-(4+26/k-14/k**2)/th)
    print("M4/M0 nu=%d ok:"%nuv, sp.cancel(r-cl)==0, flush=True)
    center = 4-26/k+506/k**2 if nuv==0 else 4-22/k+414/k**2
    e = sp.cancel(cl.subs(th,center))
    print("  M4/M0 at center, k^-2 coeff:", sp.limit(e*k**2, k, sp.oo), flush=True)
thc = 4-(26+4*nu+8*theta)/k+(506+97*nu+5*nu**2+(168+16*nu)*theta+12*theta**2)/k**2
P = sp.expand((th*((n-y)**2+n)-n*(n+1)).subs({n:2*k+nu, y:k-theta, th:thc}))
print("P: k^2:", sp.expand(P.coeff(k,2)), " k^1:", sp.expand(P.coeff(k,1)), " k^0:", sp.expand(P.coeff(k,0)), flush=True)
den = sp.expand((y**2*th).subs({y:k-theta, th:thc}))
print("y^2 th: k^2:", den.coeff(k,2), " k^1:", sp.expand(den.coeff(k,1)), flush=True)
e1 = sp.expand(k*P+5*den); print("kP+5y^2th: k^2:", sp.expand(e1.coeff(k,2)), " k^1:", sp.expand(e1.coeff(k,1)), flush=True)
e2 = sp.expand(100*k*P+499*den); print("100kP+499y^2th: k^2:", sp.expand(e2.coeff(k,2)), flush=True)
a0 = 3**sp.Rational(1,3)*sp.gamma(sp.Rational(4,3)); a1 = 3**sp.Rational(-1,3)*sp.gamma(sp.Rational(2,3))  # int w e^{-w^3/3} dw
print("a0 =", sp.N(a0,12), " a1 =", sp.N(a1,12), flush=True)
w = Fr(699,100); val = w-Fr(7,2)-(6*w+Fr(3,4))/31-(13*w/2)/961-12*w/30000
print("(나):", val, float(val), val==Fr(495594511,240250000), flush=True)
w=Fr(698,100); c1=Fr(464159,10**7); v = w-Fr(7,2)-(4*w+Fr(1,2))*Fr(12879,10**4)*c1-(13*w/2)*Fr(939,1000)*c1**2-12*w/10**4
print("(다):", float(v), " 10000^(-1/3)=", 10000**(-1/3), flush=True)
from math import pi, sqrt
print("assembly k>=10000:", 5.642*1.6809*0.39893-0.0163-3.554, " Bor(k)k^1.5 >=", (2*pi)**-0.5*(1-1/120000), flush=True)
print("assembly k>=30000:", 5.5*0.39*2-3.5, flush=True)
print("46sqrt2-12 =", 46*sqrt(2)-12, " -5000/173-0.02 ->", 46*sqrt(2)-12-5000/173-0.02, flush=True)
print("(nа) 4장 two-corr (나): ", 46*sqrt(2)-12-54.6828, 0.4503*3*2.50663+0.16752, flush=True)
