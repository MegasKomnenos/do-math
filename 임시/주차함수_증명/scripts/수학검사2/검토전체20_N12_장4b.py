# N12 검산: D.crossing-small-n의 넘는 수 재귀를 전체 표와 대조하고 20<=n<=200에서 b_{n,k_n}<b_{n,k_n+1}을 확인; D.QL-small-n의 3<=n<=15 검사
from math import comb
import time
t0=time.time()
def p(m): return (m+1)**(m-1) if m>=1 else 1
N=60
A={}
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        A[(n,l)]=(n+1)**(n-1) if l>=n-1 else sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
def b(n,l): return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
def Ac_column(l,nmax):
    # A^c_{n,l} for n<=min(nmax, 2l+4)
    Ac={n:0 for n in range(0,l+2)}
    for n in range(l+2,min(nmax,2*l+4)+1):
        s=sum(comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))
        s+=sum(Ac[i]*comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        Ac[n]=s
    return Ac
# 1. 재귀 vs 전체 표 (n<=60)
bad=0;cnt=0
for l in range(0,N):
    Ac=Ac_column(l,N)
    for n in Ac:
        if n<=N and n>=1:
            cnt+=1
            if Ac[n]!=p(n)-A[(n,l)]: bad+=1
print("A^c recursion vs full table: compared",cnt,"values, mismatches",bad)
# 2. crossing: b_{n,kn} < b_{n,kn+1} for 5<=n<=200 via A^c recursion
M=200
cols={}
def Ac_val(n,l):
    if l not in cols: cols[l]=Ac_column(l,M)
    return cols[l][n]
holds=[];fails=[]
for n in range(5,M+1):
    kn=(n+1)//2
    bk=Ac_val(n,kn-1)-Ac_val(n,kn); bk1=Ac_val(n,kn)-Ac_val(n,kn+1)
    # cross-check with full table for n<=60
    if n<=N: assert bk==b(n,kn) and bk1==b(n,kn+1)
    (holds if bk<bk1 else fails).append(n)
print("b_{n,kn}<b_{n,kn+1} false for n in:",fails)
print("holds for all 20<=n<=200:", holds==list(range(20,M+1)))
# 3. Q_L(n), 3<=n<=15
viol=[]
for n in range(3,16):
    for l in range(0,n):
        if 2*l<=n-2 and l+2<=n-1 and b(n,l)>b(n,l+1):
            if not b(n,l+1)**2>b(n,l)*b(n,l+2): viol.append((n,l,b(n,l+1)**2-b(n,l)*b(n,l+2)))
print("Q_L violations 3<=n<=15 (strict):",viol)
dec=[(n,l) for n in range(3,16) for l in range(0,n-1) if 2*l<=n-2 and b(n,l)>b(n,l+1)]
print("decreasing levels with 2l<=n-2 in 3<=n<=15:",len(dec),dec[:12])
# strict unimodality and no adjacent ties n<=60
ties=[(n,l) for n in range(1,N+1) for l in range(0,n-1) if b(n,l)==b(n,l+1)]
print("adjacent ties n<=60:",ties)
print("elapsed %.1fs"%(time.time()-t0))
