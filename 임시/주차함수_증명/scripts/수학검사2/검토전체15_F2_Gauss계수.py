# F2 검산: 보조정리 gauss-coeff 증명의 g(kappa) 전개 계수, (4.9), M4/M0 식, P의 k-계수
import sympy as sp
kap,nu,th,n,y,N,vt=sp.symbols('kappa nu theta n y N vartheta')
Nt=3+(nu+1-th)*kap
xx=(1-th*kap)*kap/Nt**2
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
g=sp.sqrt(1-4*xn)
u0=(1+g)/2
C1=(1-u0)/g**2; C2=-(1-u0)*(2+u0)/g**5; C3=sp.Rational(5,2)*(1-u0)*(6+g-g**2)/g**8
uhat=u0+xx*C1+xx**2*C2+xx**3*C3
gk=(Nt*uhat-2-nu*kap)/kap
ser=sp.series(gk,kap,0,5).removeO()
for m in range(0,5):
    c=sp.simplify(sp.expand(ser.coeff(kap,m)))
    print("g_%d ="%m, sp.factor(c) if m<3 else c)
    if m>=3:
        for nv in (0,-1):
            cc=sp.expand(c.subs(nu,nv))
            vals=[abs(float(cc.subs(th,t))) for t in [i/50 for i in range(51)]]
            print("   nu=%d: max|g_%d| over theta in [0,1] (grid) ="%(nv,m), max(vals))
# (4.9): M2/M0 via Hermite recursion
He_n, He_n1 = sp.symbols('He_n He_n1')
He_n2=(N*He_n1-He_n)/((n-1)*y)
He_n3=(N*He_n2-He_n1)/((n-2)*y)
num2=He_n-3*n*He_n1+3*n*(n-1)*He_n2-n*(n-1)*(n-2)*He_n3
den=He_n-n*He_n1
ratio=sp.simplify((num2/den).subs(He_n,(n+vt)*He_n1).subs(N,n+y+1))
target=(vt*((n-y)**2+n)-n*(n+1))/(y**2*vt)
print("(4.9) check:", sp.simplify(ratio-target))
# M4/M0
He_n4=(N*He_n3-He_n2)/((n-3)*y)
num4=He_n-5*n*He_n1+10*n*(n-1)*He_n2-10*n*(n-1)*(n-2)*He_n3+5*n*(n-1)*(n-2)*(n-3)*He_n4
k=sp.symbols('k')
for nv in (0,-1):
    r4=sp.simplify((num4/den).subs(He_n,(n+vt)*He_n1).subs(N,n+y+1).subs({y:k,n:2*k+nv}))
    r4=sp.simplify(r4)
    if nv==0: tgt=1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/vt
    else: tgt=1+12/k-6/k**2-(4+26/k-14/k**2)/vt
    print("M4/M0 nu=%d check:"%nv, sp.simplify(r4-tgt))
    center = 4-26/k+506/k**2 if nv==0 else 4-22/k+414/k**2
    print("   with center vartheta, series:", sp.series(tgt.subs(vt,center),k,sp.oo,4))
# P = vartheta[(n-y)^2+n]-n(n+1) with center
for nv in (0,-1):
    center=4-(26+4*nu+8*th)/k+(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2)/k**2
    P=sp.expand((center*((n-y)**2+n)-n*(n+1)).subs({n:2*k+nv,y:k-th,nu:nv}))
    print("P nu=%d:"%nv, sp.collect(P,k))
    Q=sp.expand((k*P+5*(k-th)**2*center.subs(nu,nv)))
    print("  kP+5y^2vt coeff k^2:",sp.simplify(Q.coeff(k,2)),"k^1:",sp.factor(Q.coeff(k,1)))
    Q2=sp.expand((100*k*P+499*(k-th)**2*center.subs(nu,nv)))
    print("  100kP+499y^2vt coeff k^2:",sp.simplify(Q2.coeff(k,2)))
