# D.exact-n20000 (ㅁ) 작은 행: b_{n,0}<...<b_{n,k_n-1} 깨지는 n, 자리 (5,2),(7,3),(9,4),(11,5); b_{n,1}>=(n-1)n!/2; B_2(k)
import math
from math import comb, factorial
import mpmath as mp
NMAX=60
p=[1]+[(n+1)**(n-1) for n in range(1,NMAX+1)]
def column(l):
    A=[1]
    for n in range(1,NMAX+1):
        if l>=n-1: A.append(p[n]); continue
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
cols=[column(l) for l in range(NMAX)]
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
bad=[]
for n in range(2,NMAX+1):
    kn=math.ceil(n/2)
    if not all(b(n,l)<b(n,l+1) for l in range(0,kn-1)): bad.append(n)
print("strict left increase fails at n:",bad)
for (n,k) in [(5,2),(7,3),(9,4),(11,5)]:
    print((n,k),"d_{n,k}=",b(n,k)-b(n,k-1))
print("b_{n,1}>=(n-1)n!/2 for n<=60:",all(b(n,1)*2>=(n-1)*factorial(n) for n in range(2,61)))
# unimodal n<=60 and ties
for n in range(1,61):
    row=[b(n,l) for l in range(n)]
    i=0
    while i+1<n and row[i]<row[i+1]: i+=1
    while i+1<n and row[i]>row[i+1]: i+=1
    if i+1!=n: print("not strictly unimodal n",n)
mp.mp.dps=20
B2=lambda k: (1-1/mp.e)+(mp.e**(mp.mpf(3)/2+mp.mpf(1)/k)-1)*2*(mp.sqrt(k+1)-1)/(mp.sqrt(2*mp.pi)*(k+1))
print("B2(42)=",B2(42),"B2(43)=",B2(43),"B2(2000)=",B2(2000))
