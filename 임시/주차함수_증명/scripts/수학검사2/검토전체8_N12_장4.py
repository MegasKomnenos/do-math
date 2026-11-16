# N12: chapter 4 appendix D items recheck: small rows (n<=60), QL(n) for 3<=n<=15, crossing b_{n,k}<b_{n,k+1} for 5<=n<=1000 via A^c recurrence
import sys,io,math,time
from fractions import Fraction
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
t0=time.time()
N=60
p=[(m+1)**(m-1) if m>0 else 1 for m in range(1001)]
# binomials
from math import comb
def columns(N):
    A=[[1]*(N+1) for l in range(N)]  # A[l][m]
    for l in range(N):
        A[l][0]=1
        for m in range(1,N+1):
            if m<=l+1: A[l][m]=p[m]; continue
            A[l][m]=sum(comb(m-1,j)*min(j+1,l+1)*A[l][j]*A[l][m-1-j] for j in range(m))
    return A
A=columns(N)
rows={}
for n in range(1,N+1):
    b=[A[0][n]]+[A[l][n]-A[l-1][n] for l in range(1,n)]
    assert sum(b)==p[n]
    rows[n]=b
def kn(n): return (n+1)//2
neg=[]; 
for n in range(2,N+1):
    k=kn(n); d=rows[n][k]-rows[n][k-1]
    if d<0:
        neg.append(n)
        assert all(rows[n][j]>=rows[n][j+1] for j in range(k,n-1)),n
    elif d==0: print('d=0 at',n)
print('d_{n,k_n}<0 for n =',neg)
# QL(n) 3<=n<=15
for n in range(3,16):
    b=rows[n]; ok=True; cnt=0
    for l in range(0,n-2):
        if 2*l<=n-2 and b[l]>b[l+1]:
            cnt+=1
            if not b[l+1]**2>=b[l]*b[l+2]: ok=False
    print('QL',n,ok,'decreasing levels in left half:',cnt)
# crossing n<=60 from exact rows
print('crossing false (b_k>=b_{k+1}) for n in 5..60:',[n for n in range(5,N+1) if not rows[n][kn(n)]<rows[n][kn(n)+1]])
# A^c recurrence check vs exact rows for n<=60 and crossing n<=1000
def Ac_level(l,Nmax):
    # A^c_{n,l} for n<=min(Nmax,2l+4)
    Ac=[0]*(Nmax+1)
    for n in range(l+2,min(Nmax,2*l+4)+1):
        s=0
        for j in range(l+1,n):
            s+=comb(n-1,j)*(j-l)*p[j]*p[n-1-j]
        for i in range(l+2,n):
            s+=Ac[i]*comb(n-1,i)*p[n-1-i]*((l+1)+min(n-i,l+1))
        Ac[n]=s
    return Ac
# check vs exact for n<=60
bad=0
for l in range(0,N):
    Ac=Ac_level(l,N)
    for n in range(l+2,min(N,2*l+4)+1):
        if p[n]-A[l][n]!=Ac[n]: bad+=1
print('A^c recurrence mismatches n<=60:',bad)
# crossing n<=1000: need levels k-1,k,k+1 -> Ac at those levels
t1=time.time()
cache={}
def Ac(l,n):
    if l not in cache: cache[l]=Ac_level(l,1000)
    return cache[l][n]
fails=[]
for n in range(5,1001):
    k=kn(n)
    bk=Ac(k-1,n)-Ac(k,n); bk1=Ac(k,n)-Ac(k+1,n)
    if not bk<bk1: fails.append(n)
print('crossing false for n in 5..1000:',fails,'time',time.time()-t1)
print('total',time.time()-t0)
