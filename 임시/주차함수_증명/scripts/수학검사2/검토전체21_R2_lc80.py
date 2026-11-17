# 검토전체21 R2: 3장 정리 old-3-4의 n<=80 진술과 1.3절 표의 재계산
from math import comb
NMAX=80
# A[n][l] for 0<=n<=NMAX, 0<=l<=NMAX-1
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1):
    A[0][l]=1
for n in range(1,NMAX+1):
    for l in range(NMAX+1):
        if l>=n-1:
            A[n][l]=(n+1)**(n-1)
        else:
            s=0
            for j in range(n):
                s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
            A[n][l]=s
def b(n,l):
    return A[n][l]-(A[n][l-1] if l>=1 else 0)
# 1.3절 표
for n in range(1,11):
    print(n,[b(n,l) for l in range(n)], sum(b(n,l) for l in range(n)))
# 로그오목성 판정
first=None
for n in range(1,NMAX+1):
    row=[b(n,l) for l in range(n)]
    assert all(x>=1 for x in row)
    bad=[l for l in range(1,n-1) if row[l]**2<row[l-1]*row[l+1]]
    if bad:
        print('n=',n,'bad l=',bad)
        if first is None: first=(n,bad)
print('first failure',first)
r=[b(80,l) for l in range(80)]
print('b80,39..41',r[39],r[40],r[41])
print('b39<b40<b41',r[39]<r[40]<r[41])
print('b39*b41-b40^2>0',r[39]*r[41]-r[40]**2>0)
print('ratios',r[40]/r[39],r[41]/r[40])
print('separator check', r[40]*25000<25928*r[39], 25928*r[40]<25000*r[41])
# 1.3절의 가장 작은 증인
for n in range(1,11):
    row=[b(n,l) for l in range(n)]
    m=max(row); w=[l for l in range(n) if row[l]==m]
    print(n,'witnesses',w,'ceil(n/2)=',-(-n//2))
