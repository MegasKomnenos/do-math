# R3 검산: 작은 행의 정확 정수 계산(정리 2:old-2-6의 마지막 차 재귀)으로
# 5.1절의 주장(예외 n=5,7,9,11, b_{n,1} 하계, 증인 위치 상계의 차 구간)을 표본 확인한다.
import sys
from math import comb, factorial
from fractions import Fraction
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
# A[l][n] for l=0..N-1
rows = {n: [] for n in range(1, N+1)}
prevA = None
for l in range(0, N):
    A = [1]*(N+1)
    for n in range(1, N+1):
        s = 0
        for j in range(0, n):
            s += comb(n-1, j)*min(j+1, l+1)*A[j]*A[n-1-j]
        A[n] = s
    for n in range(1, N+1):
        if l <= n-1:
            rows[n].append(A[n] - (prevA[n] if prevA else 0))
    prevA = A
bad_chain = []
for n in range(1, N+1):
    b = rows[n]
    assert sum(b) == (n+1)**(n-1)
    # unimodal
    i = 0
    while i+1 < n and b[i] <= b[i+1]: i += 1
    j = i
    while j+1 < n and b[j] >= b[j+1]: j += 1
    assert j == n-1, ("not unimodal", n)
    kn = (n+1)//2
    if not all(b[t] < b[t+1] for t in range(0, kn-1)):
        bad_chain.append(n)
    if n >= 4:
        assert b[1] >= (n-1)*factorial(n)//2 and b[1] > b[0] == factorial(n)
print("unimodal for all n<=", N, "; strict-left-chain fails at", bad_chain)
# witness offset
import mpmath as mp
mp.mp.dps = 30
lo, hi = None, None
for n in range(50, N+1):
    b = rows[n]
    m = max(b); ls = b.index(m)
    assert b.count(m) == 1
    v = (n+1-ls) - mp.mpf('0.59963')*mp.mpf(n+1)**(mp.mpf(2)/3) - mp.mpf('1.24847')*mp.mpf(n+1)**(mp.mpf(1)/3)
    lo = v if lo is None else min(lo, v); hi = v if hi is None else max(hi, v)
    if n == 51: print("n=51 value", v)
print("offset range for 50<=n<=%d:" % N, lo, hi)
# small-n witnesses (1.3절 표와 대조)
print([(n, rows[n].index(max(rows[n]))) for n in range(1, 11)])
