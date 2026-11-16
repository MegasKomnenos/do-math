# 검토전체6 L2: 정리 3-5 (누적 로그오목성 n=780 실패) 재계산 — 열 573..580, n<=780
from math import comb
from fractions import Fraction as Fr
NMAX=780
p=[(n+1)**(n-1) if n>=1 else 1 for n in range(NMAX+1)]
C=[[comb(m,j) for j in range(m+1)] for m in range(NMAX)]
def column(l):
    A=[0]*(NMAX+1); A[0]=1
    for n in range(1,NMAX+1):
        if l>=n-1: A[n]=p[n]; continue
        s=0; Cn=C[n-1]
        for j in range(n):
            s+=Cn[j]*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
cols={l:column(l) for l in range(573,581)}
for n in (779,780):
    for l in range(574,580):
        d=cols[l][n]**2-cols[l-1][n]*cols[l+1][n]
        print(n,l,"부호",(d>0)-(d<0),"상대크기 %.4e"%(Fr(d,cols[l][n]**2)))
print("자릿수 A_780,576:", len(str(cols[576][780])))
