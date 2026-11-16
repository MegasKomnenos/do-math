# K4: 5.5.3, 5.5.6-5.5.8의 닫힌 꼴 하·상계를 부동소수점으로 중간 크기 Y에서 검산 (5-26, 5-31, 5-33, stop-lower 상계, rig-int 첫 부등식, bt-tail, hover-tail, borel-gf(다), stirling-bor(나))
from math import *
import sys
def lBor(m): return (m-1)*log(m)-m-lgamma(m+1)
def Bor(m): return exp(lBor(m))
def BT(z,D):  # Borel-Tanner
    if D<z: return 0.0
    return exp(log(z)-log(D)-D+(D-z)*log(D)-lgamma(D-z+1)) if D>0 else 0.0
def pi_n(n,t): return exp(lBor(n+1-t)+lBor(t)-lBor(n+1))
Y0=int(sys.argv[1]) if len(sys.argv)>1 else 300
res=[]
def prt(*a):
    res.append(a); print(a, flush=True)
# survival probabilities for Y in {Y0, Y0+1}, n<=2Y+1
S={}
def s(n,Y):
    if n<=Y: return 1.0
    if (n,Y) in S: return S[(n,Y)]
    assert n<=2*Y+1
    pi0=1.0-sum(pi_n(n,t) for t in range(Y+1,n+1))
    v=pi0+sum(pi_n(n,t)*Y/t*s(t-1,Y) for t in range(Y+1,n+1))
    S[(n,Y)]=v; return v
_P0={}
def pi0(n,Y):
    if n<=Y: return 1.0
    if (n,Y) in _P0: return _P0[(n,Y)]
    v=1.0-sum(pi_n(n,t) for t in range(Y+1,n+1)); _P0[(n,Y)]=v; return v
_BT={}
def BT(z,D):
    if D<z: return 0.0
    k=(z,D)
    if k in _BT: return _BT[k]
    v=exp(log(z)-log(D)-D+(D-z)*log(D)-lgamma(D-z+1)); _BT[k]=v; return v
_LB={}
def lBor(m):
    if m in _LB: return _LB[m]
    v=(m-1)*log(m)-m-lgamma(m+1); _LB[m]=v; return v
def c(n,Y): return s(n,Y+1)-s(n,Y)
Y=Y0
qmax=floor(6*Y**(2/3))
# stop-lower upper bound
def Ptail(j): return 1.0-sum(Bor(i) for i in range(1,j+1))
worst=max(pi0(Y+j,Y)-Ptail(j) for j in range(0,Y+1))
prt(("stop-lower upper: max(pi0 - Pr(beta>j)) <=0", worst))
# 5-31 Lc
def Lc(Y,q):
    tot=0.0
    for z in range(1,q+1):
        for D in range(z,q+1):
            tot+=z*BT(z,D)*exp(lBor(Y+q+1-D)-lBor(Y+q+1))*pi0(Y+q-D,Y)*exp(-(z*(q+1)-D*(z+1)/2)/Y)
    return tot/Y
viol=[(q,c(Y+q,Y),Lc(Y,q)) for q in range(1,Y+2) if c(Y+q,Y)<Lc(Y,q)*(1-1e-12)]
prt(("5-31 violations q<=Y+1", viol[:5], len(viol)))
prt(("5-31 ratio range c/Lc (q<=qmax)", min(c(Y+q,Y)/Lc(Y,q) for q in range(1,qmax+1)), max(c(Y+q,Y)/Lc(Y,q) for q in range(1,qmax+1))))
Lam=sum(Y/(Y+q+1)*Lc(Y,q) for q in range(1,qmax+1))
prt(("Lambda_w(Y)", Lam))
# 5-33
def hov(rho,chi):
    tot=0.0
    for z in range(0,chi):
        pz=1.0 if z==0 else sum(BT(z,D) for D in range(z,chi))
        tot+=rho**z*pz
    return tot
def V(m,Y,chi,q): return (2*pi)**-0.5*((m+1)/((Y+1)*(m-Y)))**1.5*exp(-1/(12*(m-chi-Y-q+1))-1/(12*(Y+1)))
v33=[]
for chi in (2,5,20):
    for m in range(Y+qmax+chi+1, 2*Y+2):
        lhs=c(m,Y); rhs=hov(Y/(m+1),chi)*V(m,Y,chi,qmax)*Lam
        if lhs<rhs: v33.append((chi,m,lhs,rhs))
prt(("5-33 violations", v33[:5], len(v33)))
prt(("5-33 sample ratio chi=5,m=2Y+1", c(2*Y+1,Y)/(hov(Y/(2*Y+2),5)*V(2*Y+1,Y,5,qmax)*Lam)))
# rig-int first inequality: Lambda_w >= o_rig
def T_of(x):  # tree function T(x) for 0<=x<=1/e via iteration
    t=0.0
    for _ in range(2000): t=x*exp(t)
    return t
def ti(vs,b,W0):
    T1=sqrt(vs*W0); T2=sqrt(b/W0)
    return 0.5*sqrt(pi/b)*(exp(-2*sqrt(vs*b))*erfc(T1-T2)-exp(2*sqrt(vs*b))*erfc(T1+T2))
def Tz(z,Scut,vs):
    W0=Scut-z+1
    if W0<z*z/3: return None
    b=z*z/2
    return z/sqrt(2*pi)*exp(-vs*z)*exp(z**3/(3*W0**2))*(W0**-1.5*exp(-vs*W0-b/W0)+ti(vs,b,W0))
orig=0.0
for z in range(1,qmax+1):
    vs=(z-1)/(2*Y); xi1=exp(-vs); xi2=exp(-z/Y)
    Tx=T_of(xi1/e)
    qz = z*Tx**z/(1-Tx) if z>=2 else sqrt(2*qmax/pi)
    inner=0.0
    for j in range(0,qmax-z+1):
        tz=Tz(z,qmax-j,vs)
        tgf = 0.0 if tz is None else max(Tx**z-tz,0.0)
        inner+=pi0(Y+j,Y)*xi2**(j+1)*max(tgf*(1-(j+1)/Y)-qz/Y,0.0)
    orig+=z*inner
orig/=Y
prt(("rig-int: Lambda_w >= o_rig ?", Lam, orig, Lam>=orig))
# bt-tail (가)
vbt=[(z,D) for z in range(1,40) for D in range(z+1,400) if BT(z,D)>z/sqrt(2*pi)/D/sqrt(D-z)*exp(-z*z/(2*(D-z))+z**3/(3*(D-z)**2))*(1+1e-12)]
prt(("bt-tail(가) violations", len(vbt)))
# bt-tail (나): tail sum <= bound, for a few (z, Scut, vs)
vbt2=[]
for z in (1,2,3,5,8):
    for Scut in range(max(z,ceil(z*z/3)+z), 60):
        for vs in (0.0,0.01,0.1):
            tail=sum(BT(z,D)*exp(-vs*D) for D in range(Scut+1,3000))
            bd=Tz(z,Scut,vs)
            if bd is not None and tail>bd*(1+1e-10): vbt2.append((z,Scut,vs,tail,bd))
prt(("bt-tail(나) violations", vbt2[:3], len(vbt2)))
# hover-tail
vh=[]
for chi in range(2,60):
    for z in range(1,60):
        pz=sum(BT(z,D) for D in range(z,chi))  # Pr(R_z<=chi-1)
        lo=max(1-2/sqrt(pi)*z**1.5*(chi-1)**-0.5,0.0)
        if pz<lo-1e-12: vh.append(("first",chi,z,pz,lo))
        if chi>=4:
            hv=chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi))
            if 1-pz>z*hv+1e-12: vh.append(("second",chi,z,1-pz,z*hv))
prt(("hover-tail violations", vh[:3], len(vh)))
# borel-gf (다)
vg=[]
for i in range(1,2000):
    vs=i/500
    u=1-T_of(exp(-vs)/e)
    if not (sqrt(2*vs)-2*vs/3-1e-12<=u<=sqrt(2*vs)+1e-12): vg.append((vs,u))
prt(("borel-gf(다) violations", len(vg)))
# stirling-bor (나)
vs_=[]
for j in range(1,500):
    tail=sum(Bor(i) for i in range(j+1,20000))
    if tail>sqrt(2/pi)*j**-0.5*(1+1e-9) or tail<sqrt(2/pi)*(j+1)**-0.5*exp(-1/(12*(j+1)))*(1-1e-6): vs_.append(j)
prt(("stirling-bor(나) violations (j<500, tail truncated at 20000)", vs_[:5], len(vs_)))
# 5-20 ratio and 5-26 closed form at (n,y)
def g(x): return (x-1)*log(1+1/x)
for (n,y) in ((2001,1001),(2001,1200),(4001,2050),(50001,25001),(50001,30000)):
    if n>6000: continue
    t=y+5
    r=pi_n(n,t+1)/pi_n(n,t); prt(("5-20 ratio check",n,y,t,r,exp(g(t)-g(n-t))))
    # t0, wid
    T0=y+2
    while not y<=(T0-1)-floor(0.75*(T0-1)**(2/3)): T0+=1
    wid=T0-1-y
    if T0<=n:
        WINV=sum((pi_n(n,t)-pi_n(n,y))*(t-y)*Bor(t-y)*Bor(y)/Bor(t) for t in range(y+1,T0))/y
        c1=1.5*(2*y+2*wid-n)/(y*(n-y-wid)); e0=1.5*wid*(2*y+2*wid-2-n)/((y+wid-1)*(n-y-wid+1))
        CF=pi_n(n,y)/y/sqrt(2*pi)*(2/3)*(wid+1)**1.5*c1*(1+wid/y)**1.5*exp(e0+1/(12*y))
        prt(("5-26 WIN^V <= closed form",n,y,wid,WINV,CF,WINV<=CF))
        prt(("wid <= 0.75(1.1y)^(2/3)+1", wid, 0.75*(1.1*y)**(2/3)+1))
for r_ in res: print(r_, flush=True)
