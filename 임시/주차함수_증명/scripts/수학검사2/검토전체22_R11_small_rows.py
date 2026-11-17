# R11 검산: D.central-gap-integer (ㄴ) — n<=60의 행에서 d_{n,k_n}의 부호와 오른쪽 절반의 비증가
from math import comb
N=60
A=[[0]*N for _ in range(N+1)]
for l in range(N):
    col=[1]
    for n in range(1,N+1):
        col.append(sum(comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j] for j in range(n)))
    for n in range(N+1): A[n][l]=col[n]
neg=[];pos=[];bad=[]
for n in range(1,N+1):
    b=[A[n][l]-(A[n][l-1] if l else 0) for l in range(n)]
    assert sum(b)==(n+1)**(n-1)
    kn=(n+1)//2
    if kn<=n-1:
        d=b[kn]-b[kn-1]
        (neg if d<0 else pos if d>0 else bad).append(n)
        if d<0:
            if not all(b[j]>=b[j+1] for j in range(kn,n-1)): bad.append(('rightnoninc',n))
    # unimodality
    i=0
    while i+1<n and b[i]<=b[i+1]: i+=1
    while i+1<n and b[i]>=b[i+1]: i+=1
    if i!=n-1: bad.append(('unimodal',n))
print("d<0:",neg); print("d>0:",pos[0],"..",pos[-1],len(pos)); print("bad:",bad)
