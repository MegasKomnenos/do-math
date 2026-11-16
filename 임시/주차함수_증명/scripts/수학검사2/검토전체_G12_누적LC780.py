# G12 검산: n=779,780에서 누적 개수 A_{n,l} (l=574..579)의 로그오목 판정 항 부호와 상대 크기.
import sys, io
from math import comb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
N=780
C=[[comb(n,j) for j in range(n+1)] for n in range(N)]
def column(l):
    A=[1]*(N+1)
    for n in range(1,N+1):
        if l>=n-1:
            A[n]=(n+1)**(n-1); continue
        s=0
        for j in range(n):
            s+=C[n-1][j]*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
cols={l:column(l) for l in range(574,580)}
for n in (779,780):
    for l in range(575,579):
        t=cols[l][n]**2-cols[l-1][n]*cols[l+1][n]
        print(n,l,'sign',(t>0)-(t<0),'rel',f"{t/cols[l][n]**2:.4e}")
print("digits A_780,575:",len(str(cols[575][780])))
