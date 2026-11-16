# 검토전체18 L2: (4.14) 직접 수치 시험(k=30000), 중앙 상쇄 항등식, b_{n,k_n}<b_{n,k_n+1} (16<=n<=60)
from mpmath import mp, mpf, mpc, exp, sqrt, pi, log, factorial, quad, erfi, re, im, nstr
from math import comb
import sys
mp.dps=18
out=[]
def BorldR(beta):   # e^{b^2/2}(2-2 b D(b)),  D(b)=sqrt(pi/2) e^{-b^2/2} erfi(b/sqrt2)
    D=sqrt(pi/2)*exp(-beta**2/2)*erfi(beta/sqrt(2))
    return exp(beta**2/2)*(2-2*beta*D)
c=1/sqrt(2*pi)
k=30000; eps=1/sqrt(mpf(k))
lf=[0]*(k+1); 
import math
B=[mpf(0)]*(k+1)
for j in range(1,k+1):
    B[j]=exp(-j+(j-1)*log(j)-math.lgamma(j+1))
def Bortail(Z):
    q=Z*exp(1-Z); s=mpc(0); p=mpc(1)
    for j in range(1,k+1):
        p*=q; s+=B[j]*p
    return 1-s/Z
for beta in (mpf('0.5'),mpf(2),mpf(6)):
    Z=1+1j*beta*eps
    val=sqrt(mpf(k))*Bortail(Z)
    TR=mpf(3)/5+mpf(12)/5*beta**2+mpf(3)/2*beta**4+beta**6/25
    TI=mpf(1)/100+mpf(201)/100*beta+mpf(7)/10*beta**3+beta**4/500+beta**5/50000+beta**7/500000
    errR=abs(re(val)-c*BorldR(beta)-mpf(4)/3*beta**2*eps); bR=c*eps**2*exp(beta**2/2)*TR
    errI=abs(im(val)-beta); bI=c*eps*exp(beta**2/2)*TI
    out.append(f"beta={beta}: Re err={nstr(errR,4)} bound={nstr(bR,4)} ok={errR<=bR}; Im err={nstr(errI,4)} bound={nstr(bI,4)} ok={errI<=bI}")
ninf=2/sqrt(pi)
def Pq(z,r): mu=1-r**2; return mu*z**2+mu**2*z**4/4
def F0(z): return -ninf*z**4*exp(-z**2)*quad(lambda r: r**2*exp((1-r**2)*z**2/2)*Pq(z,r)*c*BorldR(r*z),[0,1])
def F1(z): return -ninf*z**4*exp(-z**2)*quad(lambda r: r**2*exp((1-r**2)*z**2/2)*Pq(z,r)*(mpf(4)/3*r**2*z**2-mpf(2)/3*r*z**4),[0,1])
I0=quad(F0,[-10,-3,0,3,10]); I1=quad(F1,[-10,-3,0,3,10])
out.append(f"int F0 = {nstr(I0,6)} (claimed 0); int F1 = {nstr(I1,8)} vs 46*sqrt2-12 = {nstr(46*sqrt(2)-12,8)}")
def column(l,nmax):
    A=[0]*(nmax+1);A[0]=1
    for n in range(1,nmax+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
N=60; cols={l:column(l,N) for l in range(0,N)}
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
bad=[n for n in range(16,N+1) if not (b(n,-(-n//2))<b(n,-(-n//2)+1))]
out.append(f"16<=n<=60: n with b(n,k_n)>=b(n,k_n+1): {bad}")
open(sys.argv[1],'w',encoding='utf-8').write("\n".join(out))
