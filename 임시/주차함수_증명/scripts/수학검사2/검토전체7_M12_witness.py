# D.exact-n20000 (ㅂ) 50<=n<=120 증인 위치 차, D.tail-T1 tm 검산
import math
from math import comb
import mpmath as mp
mp.mp.dps=30
NMAX=120
p=[1]+[(n+1)**(n-1) for n in range(1,NMAX+1)]
def column(l):
    A=[1]
    for n in range(1,NMAX+1):
        if l>=n-1: A.append(p[n]); continue
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
cols=[column(l) for l in range(NMAX)]
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
lo=(10,None); hi=(0,None)
for n in range(50,NMAX+1):
    row=[b(n,l) for l in range(n)]
    ls=max(range(n),key=lambda l:row[l])
    v=n+1-ls-mp.mpf('0.59963')*mp.mpf(n+1)**(mp.mpf(2)/3)-mp.mpf('1.24847')*mp.mpf(n+1)**(mp.mpf(1)/3)
    if v<lo[0]: lo=(v,n)
    if v>hi[0]: hi=(v,n)
print("n=50..120: min",mp.nstr(lo[0],10),"at",lo[1]," max",mp.nstr(hi[0],10),"at",hi[1])
# tail-T1 tm check
def tm(r,rho):
    bw=mp.mpf(1); num=mp.mpf(0); den=mp.mpf(1)
    for j in range(0,r-1):
        bw=bw*rho*mp.mpf(j+2)/(j+1)*mp.mpf(r-1-j)/r
        num+=(j+1)*bw; den+=bw
    return num/den
for r in (10**4,2*10**4):
    print("r",r,"tm/sqrt r =",mp.nstr(tm(r,mp.e**(-1/mp.sqrt(r)))/mp.sqrt(r),6))
