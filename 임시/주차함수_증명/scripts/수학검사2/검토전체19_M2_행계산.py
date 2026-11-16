# 마지막 차 재귀(정리 2-6)로 n<=24의 행을 정확 정수로 구해 4장 정리 4-5의 작은 n 주장과 1.3절 표, 증인 위치를 확인한다.
from math import comb, ceil
NMAX=24
A={}
for l in range(0,NMAX):
    A[(0,l)]=1
    for n in range(1,NMAX+1):
        A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
def b(n,l):
    if l<0: return 0
    return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
for n in range(1,NMAX+1):
    row=[b(n,l) for l in range(n)]
    assert sum(row)==(n+1)**(n-1), n
    kn=ceil(n/2)
    d=row[kn]-row[kn-1] if kn<=n-1 else None
    mx=max(row); wit=[l for l in range(n) if row[l]==mx]
    tail_dec = all(row[j]>=row[j+1] for j in range(kn,n-1))
    logc = all(row[l]**2>=row[l-1]*row[l+1] for l in range(1,n-1))
    print(n, 'd_mid', d, 'sign', (None if d is None else (d>0)), 'witness', wit, 'ceil(n/2)', kn, 'tail_nonincr_from_kn', tail_dec, 'logconcave', logc)
    if n<=10: print('   row', row)
