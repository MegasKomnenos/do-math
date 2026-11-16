# K12: 마지막 차 재귀로 b_{80,39..41}과 A_{780,573..580}, A_{779,573..579}를 독립 재계산
import sys, time
from math import comb
from fractions import Fraction
def column(l, N):
    # A_{m,l} for 0<=m<=N
    A=[1]*(N+1)
    C=[[0]*(N+1) for _ in range(1)]
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
t=time.time()
cols={l:column(l,80) for l in (38,39,40,41)}
b=lambda n,l: cols[l][n]-cols[l-1][n]
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print("b80,39 =",b39); print("b80,40 =",b40); print("b80,41 =",b41)
print("b39*b41-b40^2 >0:", b39*b41-b40*b40>0, " increasing:", b39<b40<b41)
print("ratios %.11f %.11f"%(b40/b39, b41/b40))
print("separator: ", Fraction(b40,b39) < Fraction(25928,25000) < Fraction(b41,b40))
# check A_{80,79}=81^79 sanity
A79=column(79,80); print("A_80,79 == 81^79:", A79[80]==81**79)
print("time",round(time.time()-t,1)); sys.stdout.flush()
t=time.time()
cols={l:column(l,780) for l in range(573,581)}
for n in (779,780):
    out=[]
    for l in range(574,580):
        if l-1<573 or l+1>580: continue
        D=cols[l][n]**2-cols[l-1][n]*cols[l+1][n]
        rel=D/cols[l][n]**2
        out.append((l, 'neg' if D<0 else 'pos', "%.4e"%rel))
    print(n, out)
print("digits of A_780,576:", len(str(cols[576][780])))
print("time",round(time.time()-t,1))
