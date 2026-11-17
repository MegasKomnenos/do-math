# R2 check: d_{n,k_n} sign for 2<=n<=300; right-half monotone for n<=15; LH+ ; Q_R range equivalence
from math import comb
N=120
def col(l,N):
    a=[1]
    for n in range(1,N+1):
        a.append(sum(comb(n-1,j)*min(j+1,l+1)*a[j]*a[n-1-j] for j in range(n)))
    return a
cols=[col(l,N) for l in range(N)]
def row(n): return [cols[l][n]-(cols[l-1][n] if l>0 else 0) for l in range(n)]
neg=[];pos=[]
for n in range(2,N+1):
    r=row(n); k=-(-n//2)
    d=(r[k] if k<n else 0)-r[k-1]
    (neg if d<0 else pos).append(n) if d!=0 else print('zero',n)
print('d<0 at n=',neg)
print('min n with d>0:',min(pos), 'all n>=16 positive up to',N, all(n in pos for n in range(16,N+1)))
ok=True
for n in range(2,16):
    r=row(n);k=-(-n//2)
    for j in range(k,n-1):
        if not r[j]>=r[j+1]: ok=False
print('right half nonincreasing for 2<=n<=15:',ok)
