# R2 검산: 행의 정확 계산 (마지막 차 재귀) — n=80 로그오목성, n<=10 표·증인, 2<=n<=15 가운데 부호, n<=60 오른쪽 절반
from math import comb
N = 80
def rows(N):
    # A[l][n]
    b = {}
    for l in range(0, N):
        A = [1] + [0]*N
        for n in range(1, N+1):
            s = 0
            for j in range(0, n):
                s += comb(n-1, j)*min(j+1, l+1)*A[j]*A[n-1-j]
            A[n] = s
        b[l] = A
    return b
A = rows(N)
def row(n):
    r = []
    for l in range(n):
        r.append(A[l][n] - (A[l-1][n] if l >= 1 else 0))
    return r
bad = []
for n in range(1, N+1):
    r = row(n)
    assert sum(r) == (n+1)**(n-1), n
    assert all(x >= 1 for x in r)
    for l in range(1, n-1):
        if r[l]**2 < r[l-1]*r[l+1]:
            bad.append((n, l))
print('log-concavity failures n<=80:', bad)
r = row(80)
print('b80,39<b80,40<b80,41:', r[39] < r[40] < r[41], ' ratios', r[40]/r[39], r[41]/r[40])
# 증인과 ceil(n/2)
for n in range(1, 11):
    r = row(n)
    m = max(r); wit = [i for i, x in enumerate(r) if x == m]
    # unimodal check
    i0 = wit[0]
    uni = all(r[i] <= r[i+1] for i in range(i0)) and all(r[i] >= r[i+1] for i in range(i0, n-1))
    print(n, 'witness', wit, 'ceil(n/2)=', -(-n//2), 'unimodal', uni, 'all witnesses < ceil:', all(w < -(-n//2) for w in wit))
# 가운데 부호
neg = []; pos = []
for n in range(2, 61):
    r = row(n); k = -(-n//2)
    d = r[k] - r[k-1] if k <= n-1 else None
    if d is None: continue
    (neg if d < 0 else pos).append(n) if d != 0 else print('zero at', n)
    if d < 0:
        assert all(r[j] >= r[j+1] for j in range(k, n-1)), n
print('d_{n,k_n}<0 for n in', neg)
print('d>0 from', min(pos), 'to', max(pos), 'count', len(pos))
