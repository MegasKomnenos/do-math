# H2: 보조정리 two-corrections — (4.14), 중앙 상쇄 항등식, F1 적분, 호 상계 수치 점검
from mpmath import mp, mpf, mpc, exp, sqrt, pi, log, quad, factorial, fabs, re, im, erfi, inf
mp.dps=25
import math
def logBor(j): return -j+(j-1)*log(j)-log(factorial(j))
def dawson(b): # e^{-b^2/2} int_0^b e^{v^2/2} dv
    return quad(lambda v: exp((v*v-b*b)/2),[0,b])
def BorldR(b): return exp(b*b/2)*(2-2*b*dawson(b))
def TR(b): return mpf(3)/5+mpf(12)/5*b**2+mpf(3)/2*b**4+b**6/25
def TI(b): return mpf(1)/100+mpf(201)/100*b+mpf(7)/10*b**3+b**4/500+b**5/50000+b**7/500000
def check414(k,betas):
    eps=1/sqrt(k)
    lb=[logBor(j) for j in range(1,k+1)]
    for b in betas:
        Z=1+1j*b*eps
        Zm=mpc(Z.real,Z.imag)
        # Bor^tail_k(Z) = 1 - sum_{j<=k} Bor(j;Z), Bor(j;Z)=Bor(j) Z^{-1} (Z e^{1-Z})^j
        lw=log(Zm)+1-Zm
        s=sum(exp(lb[j-1]+j*lw) for j in range(1,k+1))/Zm
        tail=sqrt(k)*(1-s)
        c=1/sqrt(2*pi)
        eR=fabs(re(tail)-c*BorldR(mpf(b))-mpf(4)/3*b*b*eps); bR=c*eps**2*exp(b*b/2)*TR(mpf(b))
        eI=fabs(im(tail)-b); bI=c*eps*exp(b*b/2)*TI(mpf(b))
        print("k",k,"beta",b," ReErr",mp.nstr(eR,6),"<=",mp.nstr(bR,6),eR<=bR," ImErr",mp.nstr(eI,6),"<=",mp.nstr(bI,6),eI<=bI)
check414(10000,[0.1,0.5,1,2,3,4,5,6.25])
check414(30000,[0.3,1,2,4,6,8,10,10.8])
# central cancellation: int F0 = 0, int F1 = 46 sqrt2 - 12
ninf=2/sqrt(pi); c=1/sqrt(2*pi)
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z): return -ninf*z**4*exp(-z*z)*quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z,r)*c*BorldR(r*z),[0,1])
def F1(z): return -ninf*z**4*exp(-z*z)*quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z,r)*(mpf(4)/3*r*r*z*z-mpf(2)/3*r*z**4),[0,1])
mp.dps=15
I0=quad(F0,[-12,0,12]); I1=quad(F1,[-12,0,12])
print("int F0 =",I0," int F1 =",I1," target",46*sqrt(2)-12)
# J side leading integral: int z^3 e^{-z^2/2} int_0^1 rho c_rho(z) drho dz = 3 sqrt(2 pi)
IJ=quad(lambda z: z**3*exp(-z*z/2)*quad(lambda r: r*((2-r**3)/3*z**3-r*z),[0,1]),[-inf,inf])
print("J leading:",IJ," target",3*sqrt(2*pi))
# arc bound values
for k in (10000,30000):
    print("k",k," k^5 e^{-k/520} =",mpf(k)**5*exp(-mpf(k)/520), " 130(k/256)^6 e^{-k/512}=",130*(mpf(k)/256)**6*exp(-mpf(k)/512))
print("46sqrt2-12-5000/173-0.02 =",46*sqrt(2)-12-mpf(5000)/173-mpf(2)/100)
print("Bn bound sqrt2/pi e^{1e-4}:",sqrt(2)/pi*exp(mpf(1)/10000))
