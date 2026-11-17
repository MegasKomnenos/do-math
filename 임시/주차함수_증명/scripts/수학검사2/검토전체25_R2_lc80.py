# R2 검산: 행 b_{n,l} (n<=81) 정확 정수, 로그오목성 첫 실패, 3장 수치
from math import comb
from fractions import Fraction
N = 82
def col(l, N):
    A = [1] + [0]*N
    for n in range(1, N+1):
        s = 0
        for j in range(n):
            s += comb(n-1, j) * min(j+1, l+1) * A[j] * A[n-1-j]
        A[n] = s
    return A
cols = [col(l, N) for l in range(N+1)]
def b(n, l):
    return cols[l][n] - (cols[l-1][n] if l >= 1 else 0)
fails = []
for n in range(1, N+1):
    row = [b(n, l) for l in range(n)]
    assert sum(row) == (n+1)**(n-1), n
    assert all(x >= 1 for x in row)
    for l in range(1, n-1):
        if row[l]**2 < row[l-1]*row[l+1]:
            fails.append((n, l))
print("fails n<=82:", fails)
r = [b(80, l) for l in range(80)]
print(r[39] < r[40] < r[41], r[40]**2 < r[39]*r[41])
print(float(Fraction(r[40], r[39])), float(Fraction(r[41], r[40])))
# witnesses n<=10
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    m = max(row); w = [i for i, x in enumerate(row) if x == m]
    print(n, w, -(-n//2), row if n <= 5 else '')
