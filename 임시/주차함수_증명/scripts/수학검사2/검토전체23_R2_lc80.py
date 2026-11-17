# R2 check: rows b_{n,l} via last-car recursion; log-concavity for n<=80; table n<=10; witnesses
from math import comb
N=82
A={}  # A[l][n]
def col(l,N):
    a=[1]
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*a[j]*a[n-1-j]
        a.append(s)
    return a
cols=[col(l,N) for l in range(N)]
def row(n):
    return [cols[l][n]-(cols[l-1][n] if l>0 else 0) for l in range(n)]
for n in range(1,11):
    r=row(n); assert sum(r)==(n+1)**(n-1)
    # witnesses
    m=max(r); w=[i for i,v in enumerate(r) if v==m]
    print(n,r if n<=6 else '...',"witness",w,"ceil(n/2)",-(-n//2))
fails=[]
for n in range(1,81):
    r=row(n); assert sum(r)==(n+1)**(n-1)
    for l in range(1,n-1):
        if r[l]**2<r[l-1]*r[l+1]: fails.append((n,l))
print("fails",fails)
r=row(80)
print(r[39]<r[40]<r[41], r[39]*r[41]-r[40]**2>0)
print(r[39]);print(r[40]);print(r[41])
# unimodality of all rows n<=80
for n in range(1,81):
    r=row(n); m=r.index(max(r))
    assert all(r[i]<=r[i+1] for i in range(m)) and all(r[i]>=r[i+1] for i in range(m,n-1))
print("unimodal ok")
