# H2: 4장 작은 n 주장 — d_{n,k_n} 부호(n<=120), 2<=n<=15 오른쪽 비증가, 20<=n: b_{n,k_n}<b_{n,k_n+1}, 3<=n<=15 Q_L(n)
from math import comb
NMAX=120
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1):
    A[0][l]=1
    for n in range(1,NMAX+1):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
def b(n,l): return A[n][l]-(A[n][l-1] if l>=1 else 0)
neg=[];bad15=[];bad20=[];badQL=[]
for n in range(2,NMAX+1):
    k=-(-n//2); row=[b(n,l) for l in range(n)]
    d=row[k]-row[k-1]
    if d<0: neg.append(n)
    if n<=15 and any(row[j]<row[j+1] for j in range(k,n-1)): bad15.append(n)
    if n>=20 and not (row[k]<row[k+1] and k+1<=n-2): bad20.append(n)
    if 3<=n<=15:
        for l in range(0,n-2):
            if 2*l<=n-2 and row[l]>row[l+1] and row[l+1]**2<row[l]*row[l+2]: badQL.append((n,l))
print("d_{n,k_n}<0 for n in",neg)
print("2<=n<=15 right-half not nonincreasing:",bad15)
print("20<=n<=120 failing b_{n,k_n}<b_{n,k_n+1}:",bad20)
print("Q_L(n) failures 3<=n<=15:",badQL)
