# H2: 보조정리 gauss-coeff (4.3절) — g(kappa) 전개, (4.9), M4/M0 식 검산
import sympy as sp
kap,th,nu=sp.symbols('kappa theta nu')
Nt=3+(nu+1-th)*kap
x=(1-th*kap)*kap/Nt**2
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
nfun=1+(2*nu+10+2*th)*kap+((nu+1)**2+2*(nu-3)*th+th**2)*kap**2
print("n(kappa) check:",sp.simplify(sp.expand(Nt**2-4*(2+(nu-1)*kap)*(1-th*kap))-sp.expand(nfun)))
gam=sp.sqrt(nfun)/Nt
ups=(1+gam)/2
C1=(1-ups)/gam**2; C2=-(1-ups)*(2+ups)/gam**5; C3=sp.Rational(5,2)*(1-ups)*(6+gam-gam**2)/gam**8
uhat=ups+x*C1+x**2*C2+x**3*C3
gfun=(Nt*uhat-2-nu*kap)/kap
ser=sp.series(gfun,kap,0,5).removeO()
coeffs=[sp.simplify(sp.expand(ser.coeff(kap,i))) for i in range(5)]
print("g0:",coeffs[0]); print("g1:",sp.factor(coeffs[1])); print("g2:",sp.expand(coeffs[2]))
print("g2 target diff:",sp.simplify(coeffs[2]-(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2)))
import numpy as np
for nv in (0,-1):
    for i in (3,4):
        f=sp.lambdify(th,coeffs[i].subs(nu,nv),'numpy'); v=f(np.linspace(0,1,2001)); print("nu",nv,"g%d max|.|"%i,np.abs(v).max())
# (4.9): M2/M0 and M4/M0 via recurrence
n,y,vt=sp.symbols('n y vartheta')
N=n+y+1
h=n+vt   # He_n/He_{n-1}
# ratios r_i = He_{n-i}/He_{n-1}
r={0:h,1:sp.Integer(1)}
# He_{m} = N He_{m-1} - (m-1) y He_{m-2}  =>  He_{m-2} = (N He_{m-1} - He_m)/((m-1) y)
for i in range(2,6):
    # He_{n-i} = (N He_{n-i+1} - He_{n-i+2})/((n-i+1) y)
    r[i]=sp.simplify((N*r[i-1]-r[i-2])/((n-i+1)*y))
def num(rr):  # n! [Y^n] (1-Y)^{rr+1} B(Y) / He_{n-1}
    return sum(sp.binomial(rr+1,i)*(-1)**i*sp.ff(n,i)*r[i] for i in range(rr+2))
M2M0=sp.simplify(num(2)/num(0))
print("(4.9):",sp.simplify(M2M0-(vt*((n-y)**2+n)-n*(n+1))/(y**2*vt)))
M4M0=sp.simplify(num(4)/num(0))
k=sp.symbols('k',positive=True)
for nv,target,center in [(0,1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/vt,4-26/k+506/k**2),(-1,1+12/k-6/k**2-(4+26/k-14/k**2)/vt,4-22/k+414/k**2)]:
    e=sp.simplify(M4M0.subs({n:2*k+nv,y:k}))
    print("M4/M0 nu=%d:"%nv, sp.simplify(e-target))
    s=sp.series(sp.simplify(e.subs(vt,center)),k,sp.oo,4)
    print("  with center:",s)
# P and denominators
for nv in (0,-1):
    vtc=4-(26+4*nu+8*th)/k+(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2)/k**2
    P=sp.expand((vtc*((n-y)**2+n)-n*(n+1)).subs({n:2*k+nv,y:k-th,nu:nv}))
    print("nu",nv,"P:",sp.collect(P,k))
    den=sp.expand((y**2*vtc).subs({n:2*k+nv,y:k-th,nu:nv}))
    print("   kP+5den:",sp.collect(sp.expand(k*P+5*den),k))
    print("   100kP+499den k^2 coeff:",sp.expand(100*k*P+499*den).coeff(k,2))
