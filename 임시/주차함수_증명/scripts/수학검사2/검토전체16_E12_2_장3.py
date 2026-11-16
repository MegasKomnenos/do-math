# -*- coding: utf-8 -*-
"""E12 검산 2: 부록 D 장3 항목. (1) n<=80 모든 열의 로그오목성 판정과 n=80 세 정수·분리자. (2) n=780 열 572..581, n=779 최소 상대 크기."""
from math import comb, factorial
import time
t0=time.time()
N=80
A=[[0]*(N+1) for _ in range(N+1)]  # A[l][n]
for l in range(N):
    col=A[l]; col[0]=1
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j]
        col[n]=s
# saturation check: A[l][n] for l>=n-1 equals (n+1)^(n-1)
for n in range(1,N+1):
    assert A[n-1][n]==(n+1)**(n-1), n
    assert A[0][n]==factorial(n)
fails=[]
for n in range(3,N+1):
    b=[A[0][n]]+[A[l][n]-A[l-1][n] for l in range(1,n)]
    assert sum(b)==(n+1)**(n-1)
    for l in range(1,n-1):
        if b[l]**2 < b[l-1]*b[l+1]: fails.append((n,l))
print("row LC failures n<=80:",fails)
n=80; b39=A[39][80]-A[38][80]; b40=A[40][80]-A[39][80]; b41=A[41][80]-A[40][80]
print(b39);print(b40);print(b41)
print("b39<b40<b41",b39<b40<b41, "25000*b40<25928*b39",25000*b40<25928*b39,"25928*b40<25000*b41",25928*b40<25000*b41)
print("ratios %.11f %.11f"%(b40/b39,b41/b40), "time",time.time()-t0)
# (2) columns 572..581 to n=780
M=780
C=[comb(M-1,j) for j in range(M)]
cols={}
for l in range(572,582):
    col=[0]*(M+1); col[0]=1
    for n in range(1,M+1):
        if l>=n-1:
            col[n]=(n+1)**(n-1); continue
        s=0; cn=[comb(n-1,j) for j in range(n)] if n!=M else C
        for j in range(n):
            s+=cn[j]*min(j+1,l+1)*col[j]*col[n-1-j]
        col[n]=s
    cols[l]=col
    print("col",l,"done",round(time.time()-t0),"s; digits A_780 =",len(str(col[M])),flush=True)
from fractions import Fraction
for nn in (779,780):
    for l in range(573,581):
        D=cols[l][nn]**2-cols[l-1][nn]*cols[l+1][nn]
        print(nn,l,"sign",(D>0)-(D<0),"rel %.4e"%(D/cols[l][nn]**2))
