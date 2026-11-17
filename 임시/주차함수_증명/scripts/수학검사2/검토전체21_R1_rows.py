# R1: 1.3절 표(n<=10 행), 1.4절 가운데 비교 부호(2<=n<=16), 마지막 차 재귀(정리 2.6)와 전수 조사의 일치
from math import comb
from itertools import product
from functools import lru_cache

def brute_rows(n):
    rows=[0]*n
    for a in product(range(1,n+1), repeat=n):
        slots=[0]*(n+2); ok=True; md=0
        for i,ai in enumerate(a):
            p=ai
            while p<=n and slots[p]: p+=1
            if p>n: ok=False; break
            slots[p]=1; md=max(md,p-ai)
        if ok: rows[md]+=1
    return rows

@lru_cache(None)
def A(n,l):
    if n==0: return 1
    if l<0: return 0
    return sum(comb(n-1,j)*min(j+1,l+1)*A(j,l)*A(n-1-j,l) for j in range(n))

def rows(n): return [A(n,l)-A(n,l-1) for l in range(n)]

for n in range(1,8):
    b=brute_rows(n); r=rows(n)
    print(n, b==r, r, sum(r), (n+1)**(n-1))
for n in range(8,11):
    r=rows(n); print(n, r, sum(r), (n+1)**(n-1))
print('--- d_{n,k_n} sign, k_n=ceil(n/2)')
for n in range(2,21):
    k=(n+1)//2; r=rows(n); d=r[k]-r[k-1]
    print(n,k,d, '>0' if d>0 else '<0' if d<0 else '=0')
print('--- minimal witness')
for n in range(1,11):
    r=rows(n); w=min(i for i in range(n) if all(r[j]<=r[j+1] for j in range(i)) and all(r[j]>=r[j+1] for j in range(i,n-1)))
    print(n,w)
