# T12: exact rows n<=60 (last-car recursion): check (L) of D.central-gap-integer and D.QL-small-n;
# complement recursion for crossing b_{n,k_n} < b_{n,k_n+1}, 5<=n<=NMAX
import sys, time
from math import comb
t0=time.time()
N=60
A={}
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
def b(n,l): return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
neg=[]; viol=[]
for n in range(2,N+1):
    k=(n+1)//2
    d=b(n,k)-b(n,k-1)
    if d<0:
        neg.append(n)
        if not all(b(n,j)>=b(n,j+1) for j in range(k,n-1)): viol.append(n)
    elif d==0: print("d=0 at",n)
print("d_{n,k_n}<0 for n in:",neg,"; right half not nonincreasing among them:",viol)
# QL(n) for 3<=n<=15 and up to 60
bad=[]
for n in range(3,N+1):
    for l in range(0,n-2):
        if 2*l<=n-2 and b(n,l)>b(n,l+1):
            if not b(n,l+1)**2>=b(n,l)*b(n,l+2): bad.append((n,l))
print("Q_L failures n<=60:",bad)
# strict unimodality / adjacent ties n<=60
ties=[(n,l) for n in range(2,N+1) for l in range(n-1) if b(n,l)==b(n,l+1)]
print("adjacent ties n<=60:",ties)
# crossing via complement recursion
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 1000
p=[ (m+1)**(m-1) if m>=1 else 1 for m in range(NMAX+1)]
def Ac_column(l,nmax):
    Ac=[0]*(nmax+1)
    for n in range(l+2,nmax+1):
        s=0
        for j in range(l+1,n):
            s+=comb(n-1,j)*(j-l)*p[j]*p[n-1-j]
        for i in range(l+2,n):
            s+=Ac[i]*comb(n-1,i)*p[n-1-i]*((l+1)+min(n-i,l+1))
        Ac[n]=s
    return Ac
# need b_{n,k_n}, b_{n,k_n+1} => Ac at l=k_n-1,k_n,k_n+1 ; valid while n<=2l+4
res_false=[]; res_true=0
cols={}
for n in range(5,NMAX+1):
    k=(n+1)//2
    for l in (k-1,k,k+1):
        if l not in cols: cols[l]=Ac_column(l, min(NMAX,2*l+4))
    bk=cols[k-1][n]-cols[k][n]; bk1=cols[k][n]-cols[k+1][n]
    if n<=N:
        assert bk==b(n,k) and bk1==b(n,k+1),(n)
    if bk<bk1: res_true+=1
    else: res_false.append(n)
print("crossing false for n in:",res_false,"; true count:",res_true, "elapsed",round(time.time()-t0,1))
