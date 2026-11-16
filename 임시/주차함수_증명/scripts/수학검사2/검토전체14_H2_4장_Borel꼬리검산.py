# H2: 보조정리 borel-tail-arc (4.11)의 수치 점검
from mpmath import mp, mpf, exp, sqrt, pi, log, quad, factorial, mpc, fabs
mp.dps=40
def Bor(j): return exp(-j)*mpf(j)**(j-1)/factorial(j)
def check_k(k):
    eps=1/sqrt(k)
    tail1=1-sum(Bor(j) for j in range(1,k+1))
    c=1/sqrt(2*pi)
    d1=2*c*eps-tail1
    S=sum(j*Bor(j) for j in range(1,k+1))
    d2=S-(2*c*sqrt(k)-mpf(2)/3)
    print("k",k," 2c eps - tail:",d1," bound",mpf(5)/9*c*eps**3, 0<=d1<=mpf(5)/9*c*eps**3,
          " | sum jBor - (..):",d2," bound",mpf(2)/3*c*eps, 0<=d2<=mpf(2)/3*c*eps)
    for phi in [mpc(-1,0), mpc(-2,1), mpc(-0.5,0.9), mpc(-3,-5)]:
        if not (phi.real<=0 and fabs(phi)<=2*(-phi.real)): continue
        Bsum=sum(Bor(j)*exp(-phi*j/k) for j in range(1,k+1))
        Bld=2+quad(lambda w: w**(-1.5)*(1-exp(-phi*w)),[0,1])
        center=1-c*eps*Bld+mpf(2)/3*phi/k
        err=fabs(Bsum-center); bound=c*eps**3*exp(-phi.real)*(mpf(5)/9+mpf(2)/3*fabs(phi)+mpf(13)/12*fabs(phi)**2)
        print("   phi",phi," err",err," bound",bound, err<=bound)
for k in (10,100,1000,10000):
    check_k(k)
