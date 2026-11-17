# 검토전체21 R2: 4장 보조정리 gauss-contraction·hermite-nu의 기호·수치 검산
import sympy as sp
from mpmath import mp, mpf, quad, exp, gamma, sqrt, pi
mp.dps=30
g,x,w,th,nu,k,io=sp.symbols('gamma x w theta nu k iota',positive=True)
# --- gauss-contraction ---
ups=(1+g)/2          # upsilon^circ as function of gamma, iota=(1-g^2)/4
C1=(1-ups)/g**2
C2=-(1-ups)*(2+ups)/g**5
C3=sp.Rational(5,1)*(1-ups)*(6+g-g**2)/(2*g**8)
print('C at gamma=1/3:',[sp.nsimplify(c.subs(g,sp.Rational(1,3))) for c in (C1,C2,C3)])
print('C forms:',[sp.simplify(C1-(1-g)/(2*g**2)), sp.simplify(C2+(1-g)*(5+g)/(4*g**5)), sp.simplify(C3-5*(1-g)*(6+g-g**2)/(4*g**8))])
# derivatives wrt iota: d/diota = (dgamma/diota) d/dgamma, dgamma/diota=-2/gamma
def Di(f): return sp.simplify(sp.diff(f,g)*(-2/g))
u4=Di(Di(Di(Di(ups)))); c1_3=Di(Di(Di(C1))); c2_2=Di(Di(C2)); c3_1=Di(C3)
print('ups4',sp.simplify(u4+120*g**-7),'C1_3',sp.simplify(c1_3-(192*g**-8-60*g**-7)),'C2_2',sp.simplify(c2_2+(175*g**-9-96*g**-8-15*g**-7)),'C3_1',sp.simplify(c3_1-sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7)))
# Taylor of uhat(iota - x): uhat(j)=ups+x C1+x^2 C2+x^3 C3 as function of iota; shift iota->iota-x
m1=sp.simplify(-Di(ups)+C1); m2=sp.simplify(Di(Di(ups))/2-Di(C1)+C2); m3=sp.simplify(-Di(Di(Di(ups)))/6+Di(Di(C1))/2-Di(C2)+C3)
print('m1',sp.simplify(m1-ups/g**2),'m2',sp.simplify(m2-(C2-2/g**4)),'m3',sp.simplify(m3-(C3+5*(5-g**2)/(2*g**7))))
print('m at 1/3',[sp.nsimplify(m.subs(g,sp.Rational(1,3))) for m in (m1,m2,m3)])
# monotonic? sample
import numpy as np
for name,f in (('C1',C1),('C2',C2),('C3',C3),('m1',m1),('m2',m2),('m3',m3)):
    vals=[abs(float(f.subs(g,t))) for t in np.linspace(1/3,1,200)]
    print(name,'max|.| on [1/3,1] =',max(vals),'at idx',int(np.argmax(vals)))
# residual expansion in x: gamma(iota-x)=sqrt(g^2+4x)
gs=sp.sqrt(g**2+4*x)
def at(f): return f.subs(g,gs)
uhat=ups+x*C1+x**2*C2+x**3*C3
uhat_sh=at(uhat)
iota=(1-g**2)/4
R=sp.series((uhat-1)*uhat_sh+iota,x,0,5).removeO()
R=sp.expand(R)
for j in range(5):
    cj=sp.simplify(R.coeff(x,j))
    print('x^%d coeff:'%j, cj if j<4 else sp.nsimplify(cj.subs(g,sp.Rational(1,3))))
# integrals
q=sp.symbols('q',positive=True)
upsi=(1+sp.sqrt(1-4*io))/2
gam=sp.sqrt(1-4*io)
F1=io*sp.log(upsi)+(1-upsi)**2/2
F2=sp.log(upsi)-sp.log(gam)/2
print('int1',sp.simplify(sp.diff(F1,io)-sp.log(upsi)),'int2',sp.simplify(sp.diff(F2,io)-((1-upsi)/gam**2)/upsi))
# --- hermite-nu ---
# nm identity
N_k=3+(nu+1-th)/k
nm=sp.expand(sp.simplify(N_k**2-4*(2+(nu-1)/k)*(1-th/k)))
print('nm',sp.simplify(nm-(1+(2*nu+10+2*th)/k+((nu+1)**2+2*(nu-3)*th+th**2)/k**2)))
# identity 2N^2-9(2k+nu)(k-theta)
Nn=3*k+nu+1-th
print('id',sp.expand(2*Nn**2-9*(2*k+nu)*(k-th)-((3*nu+12+6*th)*k+2*(nu+1-th)**2+9*nu*th)))
# H expansion: w=1/k
wv=sp.symbols('w')
Nt=3+(nu+1-th)*wv
xn=(2+(nu-1)*wv)*(1-th*wv)/Nt**2
xx=(1-th*wv)*wv/Nt**2
gm=sp.sqrt(1-4*xn)
up=(1+gm)/2
c1=(1-up)/gm**2; c2=-(1-up)*(2+up)/gm**5; c3=5*(1-up)*(6+gm-gm**2)/(2*gm**8)
uh=up+xx*c1+xx**2*c2+xx**3*c3
H=(Nt*uh-2-nu*wv)/wv
Hs=sp.series(H,wv,0,3).removeO()
for j in range(3):
    print('H_%d ='%j, sp.factor(sp.expand(sp.simplify(Hs.coeff(wv,j)))))
# U_i, V_i: coefficient [Y^n](1-Y)^{i+1}exp(N Y - y Y^2/2) in terms of He_n, He_{n-1}
# use backward recurrence He_{j-1}=(N He_j - He_{j+1})/(y j)
n,y,Hn,Hn1,vt=sp.symbols('n y He_n He_nm1 vartheta')
Nsym=n+y+1
He={n:Hn, n-1:Hn1}
def Hm(m):  # He_{n-m}
    if m in (0,1): return He[n-m]
    # He_{n-m} = (N He_{n-m+1} - He_{n-m+2})/(y (n-m+1))
    return sp.simplify((Nsym*Hm(m-1)-Hm(m-2))/(y*(n-m+1)))
def coef(i):
    # n! [Y^n] (1-Y)^{i+1} exp(...) = sum_m C(i+1,m)(-1)^m He_{n-m} n!/(n-m)!
    s=0
    for m in range(i+2):
        ff=1
        for t in range(m): ff*= (n-t)
        s+=sp.binomial(i+1,m)*(-1)**m*Hm(m)*ff
    return sp.simplify(s)
M0=coef(0); M2=coef(2); M4=coef(4)
# substitute He_n=(n+vt) He_{n-1}
sub={Hn:(n+vt)*Hn1}
r2=sp.simplify((M2/M0).subs(sub)); r4=sp.simplify((M4/M0).subs(sub))
# general y check for (마): 1-2n/y+n(n+1)/y^2-n(n+1)/(y^2 vt)
print('M2/M0 general:',sp.simplify(r2-(1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*vt))))
# y=k, n=2k+nu
subs2={y:k,n:2*k+nu}
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
print('U2-V2/vt check:',sp.simplify(r2.subs(subs2)-(U2-V2/vt)))
print('U4-V4/vt check:',sp.simplify(r4.subs(subs2)-(U4-V4/vt)))
# k-coefficient 20 in n(n+1)-vt[(n-y)^2+n] with vt=4+H1/k+..., y=k-theta
H1=-(26+4*nu)-8*th
expr=sp.expand((2*k+nu)*(2*k+nu+1)-(4+H1/k)*((k+nu+th)**2+2*k+nu))
print('k^2 coeff',sp.simplify(expr.coeff(k,2)),'k coeff',sp.simplify(expr.coeff(k,1)))
# numeric constants a0,a1
a0=quad(lambda t: exp(-t**3/3),[0,mp.inf]); a1=quad(lambda t: t*exp(-t**3/3),[0,mp.inf])
print('a0',a0,'a1',a1, 'Gamma(1/3)/3^(2/3)',gamma(mpf(1)/3)/mpf(3)**(mpf(2)/3))
# (라) numerics
K=mpf(10000)
print('k/(3k-1)^2 at 1e4:',K/(3*K-1)**2, '9.26*(1-1/(3k))^-4:',mpf('9.26')*(1-1/(3*K))**-4)
print('2e7*3.07*k^5/(3k-1)^8 *k^3 at 1e4:',2e7*mpf('3.07')*K**5/(3*K-1)**8*K**3)
