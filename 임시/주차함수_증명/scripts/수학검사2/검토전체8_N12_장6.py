# N12: chapter 6 appendix D items recheck
import sys,io,math,time
from fractions import Fraction
from math import comb
import mpmath
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
mpmath.mp.dps=40
def eRen(m): return mpmath.mpf(m)**(m-1)/(mpmath.e**(m-1)*mpmath.factorial(m-1))  # e*Ren(m), m=r+1
k=3131
for d in range(1,15):
    L=(k-1)*(eRen(d+1)-mpmath.mpf(60)*(d+1)/(k+d))
    R=2*(1+sum(eRen(r+1)+mpmath.mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print('d',d,mpmath.nstr(L,6),mpmath.nstr(R,5),'L>R',L>R, 'diff',mpmath.nstr(L-R,4))
def S(k):
    q=Fraction(k,k+1)**(k-1)
    return sum(Fraction(n**(n-1),math.factorial(n))*q**n for n in range(2,k+2))
vals={k:S(k) for k in range(2,61)}
print('tilt max at k=',max(vals.items(),key=lambda t:t[1])[0], float(vals[2]), [ (k,round(float(vals[k]),6)) for k in (3,10,20,42,43)], 'all<1',all(v<1 for v in vals.values()))
t0=time.time()
p=[(m+1)**(m-1) if m>0 else 1 for m in range(760)]
def Ac_level(l,Nmax):
    Ac={}
    for n in range(l+2,min(Nmax,2*l+4)+1):
        s=0
        for j in range(l+1,n): s+=comb(n-1,j)*(j-l)*p[j]*p[n-1-j]
        for i in range(l+2,n): s+=Ac[i]*comb(n-1,i)*p[n-1-i]*((l+1)+min(n-i,l+1))
        Ac[n]=s
    return Ac
cache={}
def Ac(l,n):
    if l<0: return p[n]
    if n<=l+1: return 0
    if l not in cache: cache[l]=Ac_level(l,700)
    return cache[l][n]
mpmath.mp.dps=35
def Psi(d): return sum(mpmath.mpf(j**j)/(mpmath.e**j*mpmath.factorial(j)) for j in range(1,d+1))
mn=(10,None); mx=(0,None); cnt=0
for m in range(3,701):
    D=max(d for d in range(0,60) if 8*d**3<=m*m)
    for d in range(1,D+1):
        l=m-d
        if m>2*l+4: continue
        b=Ac(l-1,m)-Ac(l,m)
        q=mpmath.mpf(m)*b/(mpmath.mpf(p[m])*Psi(d))
        if m>=4:
            cnt+=1
            if q<mn[0]: mn=(q,(m,d))
            if q>mx[0]: mx=(q,(m,d))
        elif m==3 and d==1: print('(3,1) q=',mpmath.nstr(q,12))
print('pairs m>=4:',cnt,'min',mpmath.nstr(mn[0],13),mn[1],'max',mpmath.nstr(mx[0],13),mx[1],'t',time.time()-t0)
