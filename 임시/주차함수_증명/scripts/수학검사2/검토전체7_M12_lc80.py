# D.logconcavity-failure-n80 재계산 + 작은 행 검사(4장 (ㄴ), QL n<=15, crossing n<=60)
from math import comb, factorial
NMAX=120
p=[(n+1)**(n-1) if n>=1 else 1 for n in range(NMAX+1)]
# A[l][n]
def column(l, nmax):
    A=[1]
    for n in range(1,nmax+1):
        if l>=n-1: A.append(p[n]); continue
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A.append(s)
    return A
cols=[column(l,NMAX) for l in range(NMAX)]
def b(n,l):
    if l<0: return 0
    return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
viol=[]
for n in range(1,NMAX+1):
    row=[b(n,l) for l in range(n)]
    assert sum(row)==p[n], n
    assert row[0]==factorial(n)
    for l in range(1,n-1):
        if row[l]**2<row[l-1]*row[l+1]: viol.append((n,l))
print("violations n<=120:",viol[:10],"count",len(viol))
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print(b39); print(b40); print(b41)
print("b39*b41-b40^2>0:",b39*b41-b40**2>0, "inc:",b39<b40<b41)
print("ratios:",b40/b39,b41/b40)
print("separator:", b40*25000<25928*b39, 25928*b40<25000*b41)
# chapter 4 (ㄴ): d_{n,k_n}<0 exactly for 2<=n<=15, right half nonincreasing
import math
for n in range(1,61):
    kn=math.ceil(n/2)
    d=b(n,kn)-b(n,kn-1)
    noninc=all(b(n,j)>=b(n,j+1) for j in range(kn,n-1))
    if n<=16 or d<=0: print("n",n,"k_n",kn,"d<0:",d<0,"right half nonincreasing:",noninc)
# crossing: b_{n,k_n} < b_{n,k_n+1} for 5<=n<=120
bad=[n for n in range(5,121) if not (b(n,math.ceil(n/2))<b(n,math.ceil(n/2)+1))]
print("crossing false for n in:",bad)
# QL(n) 3<=n<=15: 2l<=n-2, b_l>b_{l+1} -> b_{l+1}^2>=b_l b_{l+2}
for n in range(3,16):
    dec=[l for l in range(0,n-2) if 2*l<=n-2 and b(n,l)>b(n,l+1)]
    okq=all(b(n,l+1)**2>=b(n,l)*b(n,l+2) for l in dec)
    print("QL n",n,"dec levels",dec,"ok",okq)
# strict unimodal and no ties n<=120
for n in range(1,121):
    row=[b(n,l) for l in range(n)]
    ties=any(row[i]==row[i+1] for i in range(n-1))
    if ties or not (lambda z: (lambda i: i+1==len(z))((lambda z: (lambda i:(i))(0))(z)))(row): pass
    i=0
    while i+1<n and row[i]<row[i+1]: i+=1
    while i+1<n and row[i]>row[i+1]: i+=1
    if i+1!=n or ties: print("not strictly unimodal / tie at n",n)
print("done")
