# O1: 1.3절 표(n<=10), 1.2절 n=3 분류, 1.4절 가운데 비교 주장(n>=16에서 증가, 2..15에서 감소)을 직접 센다.
import itertools, functools
from math import comb
def park(a):
    n=len(a); occ=[False]*(n+2); pos=[0]*n
    for i,ai in enumerate(a):
        p=ai
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=True; pos[i]=p
    return [pos[i]-a[i] for i in range(n)]
def row_brute(n):
    b=[0]*n
    for a in itertools.product(range(1,n+1),repeat=n):
        d=park(a)
        if d is not None: b[max(d)]+=1
    return b
@functools.lru_cache(None)
def A(n,l):
    # 결과 순열을 최댓값 자리에서 가르는 재귀: 최댓값 자리의 용량은 (왼쪽 조각 크기)+1
    if n==0: return 1
    if l<0: return 0
    return sum(comb(n-1,m)*A(m,l)*A(n-1-m,l)*min(m+1,l+1) for m in range(n))
def row(n): return [A(n,l)-A(n,l-1) for l in range(n)]
for n in range(1,8):
    assert row_brute(n)==row(n), n
print("brute 검증 n<=7 통과")
for n in range(1,11):
    r=row(n); print(n, r, sum(r), (n+1)**(n-1), sum(r)==(n+1)**(n-1))
# 봉우리(가장 작은 증인)
for n in range(1,11):
    r=row(n); print(n, "l*=", r.index(max(r)))
# 가운데 비교 d_{n,k_n}
import math
for n in range(2,41):
    k=math.ceil(n/2); r=row(n); d=r[k]-r[k-1]
    print(n,k,"d_{n,k_n}=",d, "증가" if d>0 else "감소/0")
# n=3 분류
cls={0:[],1:[],2:[]}
for a in itertools.product(range(1,4),repeat=3):
    d=park(a)
    if d is not None: cls[max(d)].append(a)
print(cls)
