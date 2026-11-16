# L12 ch5/ch6 numeric checks
import functools; print = functools.partial(print, flush=True)
import mpmath as mp, math
from fractions import Fraction
from math import comb
mp.mp.dps=40
kn=lambda n:(n+1)//2
# counts
print("(ㄴ) count", sum(kn(n)-1 for n in range(10001,20001)))
print("(ㄹ) count", sum(n-3-math.ceil((n-1)/2)+1 for n in range(5,20001)))
print("c50 QR positions", sum(n-3-math.ceil((n-1)/2)+1 for n in range(20001,50001)), "adjacent", sum(n-2-math.ceil((n-1)/2)+1 for n in range(20001,50001)))
print("re QR", sum(n-3-math.ceil((n-1)/2)+1 for n in range(5,20001)), "adj", sum(n-2-math.ceil((n-1)/2)+1 for n in range(5,20001)))
def mfrak(n):
    best=170
    m=171
    while m**3<=(n-9*m)**2 and n-9*m>0: best=m; m+=1
    return best
print("m(20001)",mfrak(20001),"m(50001)",mfrak(50001))
print("newton coeff count", sum((r-1)*(2*r+3) for r in range(2,41)))
# tail T1 constants
M0=mp.quad(lambda y: mp.e**(-y-y*y/2),[0,mp.inf]); M=[M0,1-M0]
for q in range(1,5): M.append(q*M[q-1]-M[q])
Ms={}
for q in range(2,6):
    ys=(-1+mp.sqrt(1+4*q))/2; Ms[q]=ys**q*mp.e**(-ys-ys*ys/2)
M26=mp.quad(lambda y: y*y*mp.e**(-y-y*y/2),[0,6])
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
print("M0..M5",[mp.nstr(x,6) for x in M],"C",[mp.nstr(x,6) for x in (C1,C2,C3,C4)])
def Lr(r):
    s=mp.sqrt(r); return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+mp.e**-0.5)/s+1/s**2)
print("L(1e4)",Lr(10**4),"L(2e4)",Lr(2*10**4),"L(1e5)",Lr(10**5))
print("1/2+2L-sqrt(3pi/2)", 0.5+2*mp.mpf('0.845204')-mp.sqrt(3*mp.pi/2), "sqrt(3pi/2)",mp.sqrt(3*mp.pi/2),"sqrt(pi/2)",mp.sqrt(mp.pi/2))
def tm(r,rho):
    bt=mp.mpf(1); Nu=mp.mpf(0); De=mp.mpf(0)
    for j in range(0,r):
        w=(j+1)*rho**j*bt; Nu+=j*w; De+=w
        bt*= (1-mp.mpf(j+1)/r)
        if w<mp.mpf(10)**-60 and j>10: break
    return Nu/De
for r in (10**4,2*10**4,10**5):
    print("r",r,"tm/sqrt r", mp.nstr(tm(r,mp.e**(-1/mp.sqrt(r)))/mp.sqrt(r),5))
# crossover 0.019 check: min over ag in (0,1] of max(Im xi, et(1/2)-|xi|)
et12=mp.e**(sum((2+mp.mpf(1)/m)*mp.zeta(2*m)/mp.pi**(2*m)*mp.mpf('0.5')**(2*m) for m in range(1,30)))
print("et(1/2)",et12,"log",mp.log(et12))
f=lambda a: max(mp.e**(1-mp.cos(a))*mp.sin(a-mp.sin(a)), et12-mp.e**(1-mp.cos(a)))
print("min max over ag:", min(f(mp.mpf(i)/10000) for i in range(1,10001)))
print("1-cos(1)",1-mp.cos(1))
# band first subinterval n=50001
def band(la,lb,n,w0):
    la=mp.mpf(la); lb=mp.mpf(lb); n=mp.mpf(n)
    rho0=mp.mpf('0.75')*(mp.mpf('1.1')*lb*n)**(mp.mpf(2)/3)+1
    c0=mp.mpf('1.5')*((2*lb-1)*n+2*rho0)/(la*n*((1-lb)*n-rho0))
    e0=mp.mpf('1.5')*rho0*((2*lb-1)*n+2*rho0)/((la*n-1)*((1-lb)*n-rho0))
    hov=mp.mpf(0); z=0
    while True:
        t=(la-1/n)**z*(1-2/mp.sqrt(mp.pi)*mp.mpf(z)**1.5*(mp.floor(mp.mpf('0.3')*(1-lb)*n-1)-1)**-0.5)
        if t<=0: break
        hov+=t; z+=1
    sec=1-mp.sqrt(2/mp.pi)*(mp.mpf('0.3')*(1-lb)*n-1)**-0.5-mp.mpf('0.3')*(1-la)*n*(2*mp.pi)**-0.5*((n+1)/(la*n*((1-lb)*n-rho0)))**1.5*mp.e**(1/(12*(n+1)))
    top=(2*mp.pi)**-0.5*(1+1/n)**1.5*la**-0.5*(1-lb)**-1.5*n**-0.5*mp.e**(1/(12*n))
    K=la*mp.e**(-1/(12*(mp.mpf('0.4')*(1-lb)*n-6*(lb*n)**(mp.mpf(2)/3)+1))-1/(12*la*n)-1/(12*(n+1)))
    W=(2*mp.pi)**-0.5*mp.mpf(2)/3*(rho0+1)**1.5*c0*(1+rho0/(la*n))**1.5*mp.e**(e0+1/(12*la*n))
    return hov,sec,top,K,W, hov*w0*K*(2*sec-top)-W
r=band(mp.mpf(1)/2,mp.mpf(1)/2+mp.mpf(1)/24000,50001,mp.mpf('0.71216'))
print("band first cell:",[mp.nstr(x,8) for x in r])
r2=band(mp.mpf(2)/3-mp.mpf(1)/24000,mp.mpf(2)/3,50001,mp.mpf('0.71216')); print("band last cell ratio",mp.nstr(r2[-1],8))
# prop W thirteen
def eRen(r): return mp.mpf(r)**(r-1)/(mp.e**(r-1)*mp.factorial(r-1))  # e*Ren(r) = r^{r-1}/(e^{r-1}(r-1)!)
for d in range(1,15):
    L=3130*(eRen(d+1)-60*(d+1)/mp.mpf(3131+d)); R=2*(1+sum(eRen(r+1)+60*(r+1)/mp.mpf(3131+d) for r in range(1,d)))
    print(" d",d,mp.nstr(L,6),mp.nstr(R,5), L>R)
# tilt sum
def tilt(k):
    q=Fraction(k,k+1)**(k-1)
    return sum(Fraction(n**(n-1),math.factorial(n))*q**n for n in range(2,k+2))
vals={k:tilt(k) for k in range(2,61)}
print("tilt max", max(vals.items(), key=lambda x:x[1]), "all<1", all(v<1 for v in vals.values()))
for k in (2,3,10,20,42,43): print(" k",k,float(vals[k]))
# theorem D base
def p(m): return (m+1)**(m-1) if m>=1 else 1
def Ac_col(l,N):
    Ac=[0]*(N+1)
    for n in range(l+2,N+1):
        s=sum(comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))
        s+=sum(Ac[i]*comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        Ac[n]=s
    return Ac
Psi={d: mp.fsum(mp.mpf(j)**j*mp.e**(-j)/mp.factorial(j) for j in range(1,d+1)) for d in range(1,42)}
cols={}
def Acv(n,l):
    if l>=n-1: return 0
    if l not in cols: cols[l]=Ac_col(l,min(700,l+41,2*l+4))
    return cols[l][n]
cnt=0; mn=(10,None); mx=(0,None)
for m in range(3,701):
    for d in range(1,int(mp.floor(mp.mpf(m)**(mp.mpf(2)/3)/2))+1):
        if m<4 and d>1: continue
        if m>=4: cnt+=1
        b=Acv(m,m-d-1)-Acv(m,m-d)
        q=m*mp.mpf(b)/(mp.mpf(p(m))*Psi[d])
        if m==3: print("m=3 d",d,"q",q); continue
        if q<mn[0]: mn=(q,(m,d))
        if q>mx[0]: mx=(q,(m,d))
print("pairs",cnt,"min",mn,"max",mx)
