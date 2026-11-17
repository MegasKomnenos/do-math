# 정리 old-4-5의 작은 n 진술: 2<=n<=15에서 d_{n,k_n}<0, k_n<=j<=n-2에서 비증가; 16<=n<=80에서 d>0
from math import comb
NMAX=80
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1): A[0][l]=1
for n in range(1,NMAX+1):
    for l in range(NMAX+1):
        A[n][l]=(n+1)**(n-1) if l>=n-1 else sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
def b(n,l): return A[n][l]-(A[n][l-1] if l>=1 else 0)
for n in range(2,NMAX+1):
    kn=-(-n//2); d=b(n,kn)-b(n,kn-1)
    noninc=all(b(n,j)>=b(n,j+1) for j in range(kn,n-1))
    if n<=16 or d<=0 or (n<=15 and not noninc):
        print(n,'k_n',kn,'d',d,'noninc right',noninc, 'ell*=',max(range(n),key=lambda l:b(n,l)))
print('all n in 16..80 have d>0:',all(b(n,-(-n//2))-b(n,-(-n//2)-1)>0 for n in range(16,NMAX+1)))
