# 검토전체18 L2: 보조정리 gauss-coeff 검산 — g(kappa) 계수, (4.9), M4/M0, P의 계수
import sympy as sp, sys
out=[]
k_,nu,th,ka=sp.symbols('kappa nu theta kappa_', real=True)
kap=sp.symbols('kappa',positive=True)
# g(kappa)
Nt=3+(nu+1-th)*kap
x=(1-th*kap)*kap/Nt**2
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
def hat_u(iota, xx):
    g=sp.sqrt(1-4*iota); u=(1+g)/2
    C1=(1-u)/g**2; C2=-(1-u)*(2+u)/g**5; C3=5*(1-u)*(6+g-g**2)/(2*g**8)
    return u+xx*C1+xx**2*C2+xx**3*C3
gfun=(Nt*hat_u(xn,x)-2-nu*kap)/kap
ser=sp.series(gfun,kap,0,5).removeO()
coeffs=[sp.factor(sp.expand(ser.coeff(kap,p))) for p in range(5)]
for p,c in enumerate(coeffs): out.append(f"g_{p} = {sp.expand(c)}")
# bounds of g3,g4 over theta in [0,1], nu in {-1,0}
for p in (3,4):
    for nv in (-1,0):
        poly=sp.Poly(sp.expand(coeffs[p].subs(nu,nv)),th)
        vals=[abs(float(poly.eval(sp.Rational(i,200)))) for i in range(201)]
        out.append(f"max|g_{p}| nu={nv}: {max(vals):.1f}")
# (4.9): M2/M0 in terms of theta_ (vartheta), n, y
n,y,vt,He_n1=sp.symbols('n y vartheta He_n1',positive=True)
N=n+y+1
He_n=(n+vt)*He_n1
He_n2=(N*He_n1-He_n)/((n-1)*y)
He_n3=(N*He_n2-He_n1)/((n-2)*y)
num2=He_n-3*n*He_n1+3*n*(n-1)*He_n2-n*(n-1)*(n-2)*He_n3
den=He_n-n*He_n1
r2=sp.simplify(num2/den)
claim=(vt*((n-y)**2+n)-n*(n+1))/(y**2*vt)
out.append(f"(4.9) check: {sp.simplify(r2-claim)}")
# M4/M0: numerator from (1-Y)^5 B
He_n4=(N*He_n3-He_n2)/((n-3)*y)
He_n5=(N*He_n4-He_n3)/((n-4)*y)
num4=He_n-5*n*He_n1+10*n*(n-1)*He_n2-10*n*(n-1)*(n-2)*He_n3+5*n*(n-1)*(n-2)*(n-3)*He_n4-n*(n-1)*(n-2)*(n-3)*(n-4)*He_n5
r4=sp.simplify(num4/den)
kk=sp.symbols('k',positive=True)
for nv,claimed in ((0, 1+16/kk+18/kk**2+2/kk**3-(4+38/kk+22/kk**2+2/kk**3)/vt),(-1, 1+12/kk-6/kk**2-(4+26/kk-14/kk**2)/vt)):
    r4s=sp.simplify(r4.subs({n:2*kk+nv,y:kk}))
    out.append(f"M4/M0 nu={nv} diff: {sp.simplify(r4s-claimed)}")
    center={0:4-26/kk+506/kk**2,-1:4-22/kk+414/kk**2}[nv]
    val=sp.series(sp.simplify(r4s.subs(vt,center)),kk,sp.oo,4)
    out.append(f"M4/M0 nu={nv} with center: {val}")
# P polynomial
theta=sp.symbols('theta',real=True)
for nv in (0,-1):
    nn=2*kk+nv; yy=kk-theta
    center=4-(26+4*nv+8*theta)/kk+(506+97*nv+5*nv**2+(168+16*nv)*theta+12*theta**2)/kk**2
    P=sp.expand(center*((nn-yy)**2+nn)-nn*(nn+1))
    Pp=sp.Poly(sp.expand(P*kk**2),kk)
    out.append(f"nu={nv}: P*k^2 coeffs (k^4,k^3,k^2..): {[sp.factor(c) for c in Pp.all_coeffs()]}")
    Q1=sp.Poly(sp.expand((kk*P+5*yy**2*center)*kk**2),kk); out.append(f"  kP+5y^2vt *k^2 coeffs: {[sp.factor(c) for c in Q1.all_coeffs()]}")
    Q2=sp.Poly(sp.expand((100*kk*P+499*yy**2*center)*kk**2),kk); out.append(f"  100kP+499y^2vt *k^2 coeffs: {[sp.factor(c) for c in Q2.all_coeffs()]}")
    D=sp.Poly(sp.expand(yy**2*center*kk**2),kk); out.append(f"  y^2 vt *k^2 coeffs: {[sp.factor(c) for c in D.all_coeffs()]}")
open(sys.argv[1],'w',encoding='utf-8').write("\n".join(out))
