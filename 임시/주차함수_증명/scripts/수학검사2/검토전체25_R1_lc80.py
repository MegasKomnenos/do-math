# R1 검산: 1.4절이 옮긴 "로그오목성은 n=80에서 처음 깨진다"
from math import comb
N=81
A={}
for l in range(-1,N+1):
    A[(0,l)]=1 if l>=0 else 0
    for n in range(1,N+1):
        A[(n,l)]=0 if l<0 else (A[(n,n-1)] if l>=n else sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n)))
first=None
for n in range(1,N+1):
    row=[A[(n,l)]-A[(n,l-1)] for l in range(n)]
    bad=[l for l in range(1,n-1) if row[l]**2<row[l-1]*row[l+1]]
    if bad and first is None: first=(n,bad)
    # 단봉성도 확인
    m=len(row)-1
    assert any(all(row[i]<=row[i+1] for i in range(ls)) and all(row[i]>=row[i+1] for i in range(ls,m)) for ls in range(m+1)),n
print("first log-concavity failure:",first)
