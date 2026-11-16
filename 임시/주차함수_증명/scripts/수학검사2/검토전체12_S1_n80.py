# 정리 2-6(마지막 차 재귀)로 A_{n,l} (n<=80) 계산 -> 행 로그오목성 첫 실패 n 확인 (장1 1.4 서술 "n=80"), 그리고 n<=16 표와 교차 검증
from math import comb
N = 80
p = [(n+1)**(n-1) if n>=1 else 1 for n in range(N+1)]
rows = {}
first_fail = None
for n in range(1, N+1):
    A = {}
    for l in range(-1, n):
        if l < 0: A[l] = 0; continue
        # A_{m,l} for m<=n via recursion; recompute table per l (small)
        T = [1]*(n+1)
        for m in range(1, n+1):
            s = 0
            for j in range(m):
                s += comb(m-1, j)*min(j+1, l+1)*T[j]*T[m-1-j]
            T[m] = s
        A[l] = T[n]
    b = [A[l]-A[l-1] for l in range(n)]
    rows[n] = b
    lc = all(b[i]*b[i] >= b[i-1]*b[i+1] for i in range(1, n-1))
    if not lc and first_fail is None:
        first_fail = n
        bad = [i for i in range(1, n-1) if b[i]*b[i] < b[i-1]*b[i+1]]
        print('first log-concavity failure n =', n, 'at levels', bad, 'b[39]<b[40]<b[41]:', b[39] < b[40] < b[41])
print('n=10 row', rows[10])
