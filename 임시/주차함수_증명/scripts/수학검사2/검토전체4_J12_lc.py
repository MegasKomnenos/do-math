# J12: D.logconcavity-failure-n80 / D.cumulative-logconcavity 재검산 (정확 정수)
import sys, time
from math import comb
from fractions import Fraction
sys.set_int_max_str_digits(0)
def column(ell, N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,ell+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
t=time.time()
# n<=80 all columns -> rows
N=80
cols=[column(l,N) for l in range(0,N)]
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
first=None; fails=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1): fails.append((n,l))
print("row LC failures n<=80:",fails)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print(b39);print(b40);print(b41)
print("b39*b41-b40^2>0:", b39*b41-b40**2>0)
print("ratios", float(Fraction(b40,b39)), float(Fraction(b41,b40)))
print("separator 25928/25000: b40/b39 < sep:", b40*25000 < 25928*b39, " sep < b41/b40:", 25928*b40 < 25000*b41)
print("time",time.time()-t)
# cumulative LC at n=780: columns 573..580, n<=780 ; n=779 at 575..577
t=time.time()
N=780
C={l:column(l,N) for l in range(573,581)}
for n in (779,780):
    for l in range(574,580):
        D=C[l][n]**2-C[l-1][n]*C[l+1][n]
        rel=Fraction(D, C[l][n]**2)
        print(n,l,"sign",(D>0)-(D<0),"rel %.4e"%float(rel))
print("digits of A_780,575:",len(str(C[575][780])))
print("time",time.time()-t)
