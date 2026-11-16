# T1: 1.4절이 인용한 정리 3-4의 n=80 첫 실패를 정확 정수로 재확인
from math import comb
NMAX=80
# A[l][n]
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1):
    A[l][0]=1
    for n in range(1,NMAX+1):
        A[l][n]=sum(comb(n-1,j)*min(j+1,l+1)*A[l][j]*A[l][n-1-j] for j in range(n))
def b(n,l): return A[l][n]-(A[l-1][n] if l>=1 else 0)
first=None
for n in range(1,NMAX+1):
    row=[b(n,l) for l in range(n)]
    bad=[l for l in range(1,n-1) if row[l]**2<row[l-1]*row[l+1]]
    if bad:
        print(n,"로그오목 실패 수준",bad, "증가구간?", [(row[l-1]<row[l]<row[l+1]) for l in bad]); 
        if first is None: first=n
print("첫 실패 n =",first)
