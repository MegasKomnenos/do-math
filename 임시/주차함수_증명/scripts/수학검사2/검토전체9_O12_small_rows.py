# 작은 n의 행을 마지막 차 재귀(정리 2:old-2-6)로 정확히 만들어 부록 D 장4·장5A의 작은-n 주장을 다시 센다.
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from math import comb, ceil
N = 120
# A[l][n]
A = [[0]*(N+1) for _ in range(N+1)]
for l in range(N+1):
    A[l][0] = 1
    for n in range(1, N+1):
        s = 0
        for j in range(n):
            s += comb(n-1, j) * min(j+1, l+1) * A[l][j] * A[l][n-1-j]
        A[l][n] = s
def b(n, l):
    if l < 0: return 0
    if l > n-1: return 0
    return A[l][n] - (A[l-1][n] if l >= 1 else 0)
# checks
for n in range(1, N+1):
    assert sum(b(n,l) for l in range(n)) == (n+1)**(n-1), n
    assert A[0][n] == 1 if n==0 else True
print("row sums ok up to", N)
# (1) central-gap-integer (ㄴ): d_{n,k_n} < 0 exactly for 2<=n<=15; right half nonincreasing there
neg = []
for n in range(2, 61):
    k = ceil(n/2)
    d = b(n,k) - b(n,k-1)
    if d < 0:
        neg.append(n)
        assert all(b(n,j) >= b(n,j+1) for j in range(k, n-1)), ("right half not nonincreasing", n)
    elif d == 0: print("d=0 at", n)
print("d_{n,k_n}<0 for n in", neg)
# (2) crossing-small-n: b_{n,k_n} < b_{n,k_n+1}
tr = [n for n in range(5, N+1) if b(n, ceil(n/2)) < b(n, ceil(n/2)+1)]
fl = [n for n in range(5, N+1) if not (b(n, ceil(n/2)) < b(n, ceil(n/2)+1))]
print("crossing true for n in [5,120]:", tr[:5], "...", "false:", fl)
# (3) QL(n) for 3<=n<=15 and 3<=n<=120: 2l<=n-2, b_l>b_{l+1} => b_{l+1}^2 >= b_l b_{l+2}
bad = []
cnt_dec = 0
for n in range(3, N+1):
    for l in range(0, n-2):
        if 2*l <= n-2 and b(n,l) > b(n,l+1):
            cnt_dec += 1
            if not (b(n,l+1)**2 > b(n,l)*b(n,l+2)):
                bad.append((n,l))
print("QL violations (strict) for 3<=n<=120:", bad, "decreasing levels in QL range:", cnt_dec)
# (4) exact-n20000 (ㅁ): strict increase b_{n,0}<...<b_{n,k_n-1} fails exactly at n in {5,7,9,11}; all rows unimodal n<=120
fails = []
for n in range(1, N+1):
    k = ceil(n/2)
    if not all(b(n,l) < b(n,l+1) for l in range(0, k-1)):
        fails.append(n)
print("strict left increase fails at:", fails)
def unimodal(seq):
    i = 0
    while i+1 < len(seq) and seq[i] <= seq[i+1]: i += 1
    while i+1 < len(seq) and seq[i] >= seq[i+1]: i += 1
    return i+1 == len(seq)
print("all rows unimodal n<=120:", all(unimodal([b(n,l) for l in range(n)]) for n in range(1,N+1)))
# strict unimodal & no adjacent ties
ties = [(n,l) for n in range(1,N+1) for l in range(n-1) if b(n,l)==b(n,l+1)]
print("adjacent ties n<=120:", ties[:10])
# decreasing levels count for n<=120 in whole row (for QL-small-n '43860' sanity: not comparable) 
# (5) n=7 row
print("row 7:", [b(7,l) for l in range(7)])
print("row 4:", [b(4,l) for l in range(4)], "row 5:", [b(5,l) for l in range(5)])
# (6) b_{n,1} >= (n-1) n!/2 ?
from math import factorial
print("b_{n,1} >= (n-1)n!/2 for n<=120:", all(2*b(n,1) >= (n-1)*factorial(n) for n in range(2,N+1)))
print("b_{n,0}=n! < b_{n,1} for 2<=n<=120:", all(b(n,0) < b(n,1) for n in range(2,N+1)))
