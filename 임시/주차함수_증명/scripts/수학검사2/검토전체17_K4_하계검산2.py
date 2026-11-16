# K4: bt-tail, hover-tail, borel-gf(다), stirling-bor(나), 5-20, 5-26 의 수치 검산 (하계검산.py의 뒷부분; 로그 영역으로 넘침 방지)
from math import *
def lBor(m): return (m-1)*log(m)-m-lgamma(m+1)
def Bor(m): return exp(lBor(m))
def lBT(z,D): return log(z)-log(D)-D+(D-z)*log(D)-lgamma(D-z+1)
def BT(z,D): return 0.0 if D<z else exp(lBT(z,D))
def pi_n(n,t): return exp(lBor(n+1-t)+lBor(t)-lBor(n+1))
def T_of(x):
    t=0.0
    for _ in range(3000): t=x*exp(t)
    return t
def ti(vs,b,W0):
    T1=sqrt(vs*W0); T2=sqrt(b/W0)
    return 0.5*sqrt(pi/b)*(exp(-2*sqrt(vs*b))*erfc(T1-T2)-exp(2*sqrt(vs*b))*erfc(T1+T2))
def Tz(z,Scut,vs):
    W0=Scut-z+1
    if W0<z*z/3: return None
    b=z*z/2
    return z/sqrt(2*pi)*exp(-vs*z)*exp(z**3/(3*W0**2))*(W0**-1.5*exp(-vs*W0-b/W0)+ti(vs,b,W0))
# bt-tail (가) in log domain
vbt=[(z,D) for z in range(1,40) for D in range(z+1,400)
     if lBT(z,D) > log(z)-0.5*log(2*pi)-log(D)-0.5*log(D-z)-z*z/(2*(D-z))+z**3/(3*(D-z)**2)+1e-12]
print(("bt-tail(가) violations", len(vbt)), flush=True)
vbt2=[]
for z in (1,2,3,5,8):
    for Scut in range(max(z,ceil(z*z/3)+z-1), 80):
        for vs in (0.0,0.01,0.1):
            tail=sum(BT(z,D)*exp(-vs*D) for D in range(Scut+1,4000))
            bd=Tz(z,Scut,vs)
            if bd is not None and tail>bd*(1+1e-10): vbt2.append((z,Scut,vs,tail,bd))
print(("bt-tail(나) violations", vbt2[:3], len(vbt2)), flush=True)
vh=[]
for chi in range(2,60):
    for z in range(1,60):
        pz=sum(BT(z,D) for D in range(z,chi))
        lo=max(1-2/sqrt(pi)*z**1.5*(chi-1)**-0.5,0.0)
        if pz<lo-1e-12: vh.append(("first",chi,z,pz,lo))
        if chi>=4:
            hv=chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi))
            if 1-pz>z*hv+1e-12: vh.append(("second",chi,z,1-pz,z*hv))
print(("hover-tail violations", vh[:3], len(vh)), flush=True)
vg=[]
for i in range(1,3000):
    vs=i/500
    u=1-T_of(exp(-vs)/e)
    if not (sqrt(2*vs)-2*vs/3-1e-12<=u<=sqrt(2*vs)+1e-12): vg.append((vs,u))
print(("borel-gf(다) violations", len(vg)), flush=True)
vs_=[]
tails={}
acc=0.0
B=[0.0]+[Bor(i) for i in range(1,40001)]
cum=0.0; C=[0.0]
for i in range(1,40001): cum+=B[i]; C.append(cum)
for j in range(1,2000):
    tail=1.0-C[j]   # exact tail (sum Bor=1)
    if tail>sqrt(2/pi)*j**-0.5*(1+1e-9) or tail<sqrt(2/pi)*(j+1)**-0.5*exp(-1/(12*(j+1)))*(1-1e-9): vs_.append(j)
print(("stirling-bor(나) violations j<2000", vs_[:5], len(vs_), "sum Bor to 40000 =", C[-1]), flush=True)
def g(x): return (x-1)*log(1+1/x)
for (n,y) in ((2001,1001),(2001,1200),(4001,2050),(4001,2500)):
    t=y+5
    print(("5-20 ratio",n,y,t,pi_n(n,t+1)/pi_n(n,t),exp(g(t)-g(n-t))), flush=True)
    T0=y+2
    while not y<=(T0-1)-floor(0.75*(T0-1)**(2/3)): T0+=1
    wid=T0-1-y
    if T0<=n:
        WINV=sum((pi_n(n,t)-pi_n(n,y))*(t-y)*Bor(t-y)*Bor(y)/Bor(t) for t in range(y+1,T0))/y
        c1=1.5*(2*y+2*wid-n)/(y*(n-y-wid)); e0=1.5*wid*(2*y+2*wid-2-n)/((y+wid-1)*(n-y-wid+1))
        CF=pi_n(n,y)/y/sqrt(2*pi)*(2/3)*(wid+1)**1.5*c1*(1+wid/y)**1.5*exp(e0+1/(12*y))
        print(("5-26 WIN^V <= closed form",n,y,wid,WINV,CF,WINV<=CF), flush=True)
        print(("wid <= 0.75(1.1y)^(2/3)+1", wid, 0.75*(1.1*y)**(2/3)+1), flush=True)
        # 5-30 bracket numerically: pi_n(n)-pi_n(T0-1)-(y-1)pi_n(y) > 0.2 ?
        print(("5-30 bracket", pi_n(n,n)-pi_n(n,T0-1)-(y-1)*pi_n(n,y)), flush=True)
