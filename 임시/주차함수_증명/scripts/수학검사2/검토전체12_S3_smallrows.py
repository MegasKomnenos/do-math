# S3 검산: 작은 행의 정확 계산으로 5.1절의 서술(첫째 조각 사슬이 n=5,7,9,11에서만 깨짐, n<=15 단봉, b_{n,1} 하계)을 확인한다.
from math import comb, factorial, ceil
from functools import lru_cache
@lru_cache(None)
def A(n,l):
    if l<0: return 0
    if n==0: return 1
    return sum(comb(n-1,j-1)*min(j,l+1)*A(j-1,l)*A(n-j,l) for j in range(1,n+1))
def row(n): return [A(n,l)-A(n,l-1) for l in range(n)]
assert all(A(n,n-1)==(n+1)**(n-1) for n in range(1,12))
for n in range(3,31):
    b=row(n); kn=ceil(n/2)
    chain_ok = all(b[l]<b[l+1] for l in range(kn-1))
    peak=b.index(max(b))
    unimodal = all(b[i]<=b[i+1] for i in range(peak)) and all(b[i]>=b[i+1] for i in range(peak,n-1))
    mid = b[kn]-b[kn-1] if kn<n else None
    print(n, "chain_ok",chain_ok, "ell*",peak, "unimodal",unimodal, "d_mid>0", (mid>0) if mid is not None else None, "b1>=(n-1)n!/2", b[1]>=(n-1)*factorial(n)//2)
