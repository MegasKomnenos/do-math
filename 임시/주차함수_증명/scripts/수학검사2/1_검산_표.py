# -*- coding: utf-8 -*-
"""태그 1 검산: 1.1절 p_n, n=2 보기, 1.2절 n=3 세 무리, 1.3절 표(n<=10)의 b_{n,l}를
(가) 선형 탐사 전수 모의, (나) 마지막 차 재귀(정리 2:old-2-6)로 각각 계산해 대조하고,
가장 작은 증인 l*_n(n=1..10)을 구한다."""
from itertools import product
from math import comb
from functools import lru_cache

def park(alpha):
    n=len(alpha); occ=[False]*(n+1); disp=[]
    for a in alpha:
        p=a
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=True; disp.append(p-a)
    return disp

def brute_row(n):
    row=[0]*n
    for alpha in product(range(1,n+1),repeat=n):
        d=park(alpha)
        if d is not None: row[max(d)]+=1
    return row

@lru_cache(None)
def A(n,l):
    if n==0: return 1
    if l<0: return 0
    return sum(comb(n-1,j)*min(j+1,l+1)*A(j,l)*A(n-1-j,l) for j in range(n))

def rec_row(n):
    return [A(n,l)-A(n,l-1) for l in range(n)]

table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],
6:[720,3963,4594,3688,2546,1296],7:[5040,42253,62145,57398,46142,32359,16807],
8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
sums={1:1,2:3,3:16,4:125,5:1296,6:16807,7:262144,8:4782969,9:100000000,10:2357947691}

print("p_n=(n+1)^(n-1), n=0..4:",[(n+1)**(n-1) if n>0 else 1 for n in range(5)])
print("A(n,n-1) vs p_n, n=1..10:",all(A(n,n-1)==(n+1)**(n-1) for n in range(1,11)))
# n=2 보기
print("PF_2 =",[a for a in product(range(1,3),repeat=2) if park(a) is not None])
# n=3 세 무리
groups={0:[],1:[],2:[]}
for a in product(range(1,4),repeat=3):
    d=park(a)
    if d is not None: groups[max(d)].append(a)
for m in groups: print("n=3, M=%d: %d개 %s"%(m,len(groups[m]),groups[m]))
print("(1,1,2):",park((1,1,2)),"(1,2,1):",park((1,2,1)))
ok=True
for n in range(1,11):
    r=rec_row(n)
    b=brute_row(n) if n<=7 else None
    same=(r==table[n]) and (b is None or b==r) and sum(r)==sums[n]
    ok&=same
    # 가장 작은 증인: 첫 감소 직전, 즉 row[i]<=row[i+1]인 최대 접두 구간
    i=0
    while i<n-1 and r[i]<=r[i+1]: i+=1
    # i는 첫 감소 자리(또는 n-1). 가장 작은 증인 = 가장 왼쪽 최댓값 자리
    lstar=r.index(max(r))
    # 단봉 확인
    j=lstar
    while j<n-1 and r[j]>=r[j+1]: j+=1
    print("n=%2d 재귀==표:%s 전수==재귀:%s 합==p_n:%s 단봉:%s 가장 작은 증인 l*=%d"%(n,r==table[n],(b==r) if b is not None else "-",sum(r)==sums[n],j==n-1,lstar))
    if r!=table[n]: print("  재귀:",r); print("  표  :",table[n])
print("전체 일치:",ok)
