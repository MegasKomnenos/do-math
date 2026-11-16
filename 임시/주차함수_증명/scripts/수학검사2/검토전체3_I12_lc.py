# I12: D.logconcavity-failure-n80 / D.cumulative-logconcavity 재계산
import sys, time
from math import comb, factorial
from fractions import Fraction
def column(l, N):
    # A_{n,l} for n=0..N via last-car recursion
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
t=time.time()
N=80
cols={l:column(l,N) for l in range(38,42)}
b=lambda n,l: cols[l][n]-cols[l-1][n]
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print("b80,39 =",b39); print("b80,40 =",b40); print("b80,41 =",b41)
print("b39*b41-b40^2 >0 :", b39*b41-b40*b40>0)
print("ratios:", Fraction(b40,b39).__float__(), Fraction(b41,b40).__float__())
print("separator 25928/25000:", b40*25000<25928*b39, b41*25000>25928*b40)
print("time",time.time()-t)
# cumulative at n=780: columns 574..579 (need 574..579 for l=575..578), and 575..577 for n=779 l=576
t=time.time()
N=780
cols2={l:column(l,N) for l in range(574,580)}
print("time cols",time.time()-t)
for n in (779,780):
    for l in range(575,579):
        if l-1 in cols2 and l+1 in cols2:
            A0,A1,A2=cols2[l-1][n],cols2[l][n],cols2[l+1][n]
            d=A1*A1-A0*A2
            print(n,l,"sign",(d>0)-(d<0),"rel","%.4e"%(d/(A1*A1)),"digits",len(str(A1)))
