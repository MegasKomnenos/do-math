# S2b 검산 2: 보조정리 gauss-contraction·gauss-coeff의 기호 계산 확인(sympy)
import sympy as sp
out=[]
g,x,i=sp.symbols('gamma x iota',positive=True)
ups=(1+g)/2
C1=(1-ups)/g**2; C2=-(1-ups)*(2+ups)/g**5; C3=sp.Rational(5,2)*(1-ups)*(6+g-g**2)/g**8
out.append("C1=%s C2=%s C3=%s"%(sp.simplify(C1-(1-g)/(2*g**2)),sp.simplify(C2+(1-g)*(5+g)/(4*g**5)),sp.simplify(C3-5*(1-g)*(6+g-g**2)/(4*g**8))))
# values at gamma=1/3
out.append("C at 1/3: %s %s %s"%(C1.subs(g,sp.Rational(1,3)),C2.subs(g,sp.Rational(1,3)),C3.subs(g,sp.Rational(1,3))))
# log derivatives wrt gamma
for name,C in [("C1",C1),("C2",-C2),("C3",C3)]:
    ld=sp.simplify(sp.diff(sp.log(C),g))
    out.append(f"logder {name}: {sp.factor(ld)}")
# derivatives wrt iota: gamma=sqrt(1-4 iota), d/diota gamma^j = -2j gamma^(j-2)
def diota(expr):
    return sp.simplify(sp.diff(expr,g)*(-2/g))
u4=diota(diota(diota(diota(ups))))
C1_3=diota(diota(diota(C1))); C2_2=diota(diota(C2)); C3_1=diota(C3)
out.append("ups''''=%s"%sp.simplify(u4))
out.append("C1'''=%s"%sp.expand(C1_3))
out.append("C2''=%s"%sp.expand(C2_2))
out.append("C3'=%s"%sp.expand(C3_1))
tgt=[-120*g**-7, 192*g**-8-60*g**-7, -(175*g**-9-96*g**-8-15*g**-7), sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7)]
out.append("derivative formulas match: %s"%[sp.simplify(a-b)==0 for a,b in zip([u4,C1_3,C2_2,C3_1],tgt)])
third=sp.Rational(1,3)
vals=[abs(t.subs(g,third)) for t in tgt]
out.append("sup at 1/3: %s ; sum/24,/6,/2,/1 = %s"%(vals, vals[0]/24+vals[1]/6+vals[2]/2+vals[3]))
# m1,m2,m3 : hatups(iota - x) Taylor in x
upsd1=diota(ups); upsd2=diota(upsd1); upsd3=diota(upsd2)
C1d1=diota(C1); C1d2=diota(C1d1); C2d1=diota(C2)
m1=sp.simplify(C1-upsd1); m2=sp.simplify(C2-C1d1+upsd2/2); m3=sp.simplify(C3-C2d1+C1d2/2-upsd3/6)
out.append("m1-ups/g^2=%s ; m2-(C2-2/g^4)=%s ; m3-(C3+5(5-g^2)/(2g^7))=%s"%(sp.simplify(m1-ups/g**2),sp.simplify(m2-(C2-2/g**4)),sp.simplify(m3-(C3+5*(5-g**2)/(2*g**7)))))
import numpy as np
gs=np.linspace(1/3,1,2001)
for name,m in [("m1",m1),("m2",m2),("m3",m3)]:
    f=sp.lambdify(g,m,'numpy'); v=f(gs); out.append(f"max|{name}| on [1/3,1] = {np.max(np.abs(v))}")
# residual expansion: R(iota) = (hatups(iota)-1) hatups(iota-x) + iota, coefficients x^0..x^3 vanish
I=sp.symbols('I')
gI=sp.sqrt(1-4*I)
def ups_f(t): return (1+sp.sqrt(1-4*t))/2
def hat(t):
    gg=sp.sqrt(1-4*t); u=(1+gg)/2
    c1=(1-u)/gg**2; c2=-(1-u)*(2+u)/gg**5; c3=sp.Rational(5,2)*(1-u)*(6+gg-gg**2)/gg**8
    return u+x*c1+x**2*c2+x**3*c3
R=(hat(I)-1)*hat(I-x)+I
ser=sp.series(R,x,0,4).removeO()
coeffs=[sp.simplify(ser.coeff(x,j)) for j in range(4)]
out.append("residual coeffs x^0..x^3: %s"%coeffs)
# x^4 coefficient of product (without Taylor remainder t) = C1 m3 + C2 m2 + C3 m1 : check bound numerically
f4=sp.lambdify(g,C1*m3+C2*m2+C3*m1,'numpy'); out.append("max|x^4 coeff| = %s"%np.max(np.abs(f4(gs))))
# integrals in (다)
Fint1=I*sp.log(ups_f(I))+(1-ups_f(I))**2/2
out.append("d/diota [iota log ups + (1-ups)^2/2] - log ups = %s"%sp.simplify(sp.diff(Fint1,I)-sp.log(ups_f(I))))
Fint2=sp.log(ups_f(I))-sp.log(gI)/2
c1I=(1-ups_f(I))/gI**2
out.append("d/diota [log ups - log gamma/2] - C1/ups = %s"%sp.simplify(sp.diff(Fint2,I)-c1I/ups_f(I)))
out.append("C1/ups at iota=2/9: %s ; -1/(gamma ups) at 2/9: %s"%(sp.nsimplify((c1I/ups_f(I)).subs(I,sp.Rational(2,9))), sp.nsimplify((-1/(gI*ups_f(I))).subs(I,sp.Rational(2,9)))))
# ---- gauss-coeff: g(kappa) expansion
kap,nu,th=sp.symbols('kappa nu theta')
Nt=3+(nu+1-th)*kap
xx=(1-th*kap)*kap/Nt**2
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
nk=1+(2*nu+10+2*th)*kap+((nu+1)**2+2*(nu-3)*th+th**2)*kap**2
out.append("n(kappa) check: %s"%sp.simplify(sp.expand(Nt**2*(1-4*xn))-nk))
gam=sp.sqrt(nk)/Nt
u=(1+gam)/2
c1=(1-u)/gam**2; c2=-(1-u)*(2+u)/gam**5; c3=sp.Rational(5,2)*(1-u)*(6+gam-gam**2)/gam**8
hatu=u+xx*c1+xx**2*c2+xx**3*c3
gk=(Nt*hatu-2-nu*kap)/kap
sg=sp.series(gk,kap,0,5).removeO()
for j in range(5):
    out.append("g_%d = %s"%(j,sp.factor(sp.simplify(sg.coeff(kap,j)))))
g3=sp.simplify(sg.coeff(kap,3)); g4=sp.simplify(sg.coeff(kap,4))
for nuv in [0,-1]:
    f3=sp.lambdify(th,g3.subs(nu,nuv),'numpy'); f4=sp.lambdify(th,g4.subs(nu,nuv),'numpy')
    ts=np.linspace(0,1,1001)
    out.append("nu=%d: max|g3|=%s max|g4|=%s"%(nuv,np.max(np.abs(f3(ts))),np.max(np.abs(f4(ts)))))
# (4.9): M2/M0 from He recursion
n,y,He_n,He_n1,vt=sp.symbols('n y He_n He_nm1 vartheta')
N=n+y+1
He_n2=(N*He_n1-He_n)/((n-1)*y)
He_n3=(N*He_n2-He_n1)/((n-2)*y)
num2=He_n-3*n*He_n1+3*n*(n-1)*He_n2-n*(n-1)*(n-2)*He_n3
den=He_n-n*He_n1
ratio=sp.simplify((num2/den).subs(He_n,(n+vt)*He_n1))
target=1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*vt)
out.append("(4.9) check: %s"%sp.simplify(ratio-target))
out.append("(4.9) second form: %s"%sp.simplify(target-(vt*((n-y)**2+n)-n*(n+1))/(y**2*vt)))
# M4/M0
He_n4=(N*He_n3-He_n2)/((n-3)*y)
He_n5=(N*He_n4-He_n3)/((n-4)*y)
ff=sp.ff
num4=sum((-1)**j*sp.binomial(5,j)*sp.ff(n,j)*[He_n,He_n1,He_n2,He_n3,He_n4,He_n5][j] for j in range(6))
r4=sp.simplify((num4/den).subs(He_n,(n+vt)*He_n1))
k=sp.symbols('k')
for nuv,expr in [(0,1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/vt),(-1,1+12/k-6/k**2-(4+26/k-14/k**2)/vt)]:
    diff=sp.simplify(r4.subs({n:2*k+nuv,y:k})-expr)
    out.append("M4/M0 nu=%d check: %s"%(nuv,diff))
    center={0:4-26/k+506/k**2,-1:4-22/k+414/k**2}[nuv]
    out.append("  with center: series %s"%sp.series(expr.subs(vt,center),k,sp.oo,4))
# P polynomial: k^2,k coefficients
thv=sp.symbols('theta')
for nuv in [0,-1]:
    nn=2*k+nuv; yy=k-thv
    center=4-(26+4*nuv+8*thv)/k+(506+97*nuv+5*nuv**2+(168+16*nuv)*thv+12*thv**2)/k**2
    P=sp.expand(center*((nn-yy)**2+nn)-nn*(nn+1))
    out.append("nu=%d: P k^2 coef=%s, k coef=%s, const=%s"%(nuv,P.coeff(k,2),P.coeff(k,1),sp.factor(P.coeff(k,0))))
    D=sp.expand(yy**2*center)
    out.append("   y^2 vt: k^2=%s k=%s"%(D.coeff(k,2),D.coeff(k,1)))
    Q1=sp.expand(k*P+5*D); out.append("   kP+5y^2vt: k^2=%s k=%s"%(Q1.coeff(k,2),sp.factor(Q1.coeff(k,1))))
    Q2=sp.expand(100*k*P+499*D); out.append("   100kP+499y^2vt: k^2=%s"%(Q2.coeff(k,2)))
open("C:/math/임시/주차함수_증명/대조v2/수학검사2/_S2b_2_out.txt","w",encoding="utf-8").write("\n".join(map(str,out)))
print("\n".join(map(str,out)))
