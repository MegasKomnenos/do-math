# R3 (22차): 5.1절 수치의 재계산 - 정확 정수 행, 위치 수, 증인 위치 상계(작은 n)
import sys, math
from math import comb, factorial
from fractions import Fraction

N = int(sys.argv[1]) if len(sys.argv) > 1 else 160

# A[l][n] = A_{n,l}  (정리 2:old-2-6)
def column(l, N):
    A = [1] * (N + 1)
    for n in range(1, N + 1):
        s = 0
        for j in range(n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j]
        A[n] = s
    return A

cols = [column(l, N) for l in range(N)]
def b(n, l):
    return cols[l][n] - (cols[l - 1][n] if l >= 1 else 0)

# 행 합 = p_n
for n in range(1, N + 1):
    assert sum(b(n, l) for l in range(n)) == (n + 1) ** (n - 1), n
print("row sums ok up to", N)
print("row 3:", [b(3, l) for l in range(3)], " row 5:", [b(5, l) for l in range(5)])

kn = lambda n: (n + 1) // 2
broken = []
uni_fail = []
mid_fail = []
QR_fail = []
first_cmp_fail = []
for n in range(1, N + 1):
    row = [b(n, l) for l in range(n)]
    # 단봉
    j = 0
    while j + 1 < n and row[j] <= row[j + 1]:
        j += 1
    if any(row[i] < row[i + 1] for i in range(j, n - 1)):
        uni_fail.append(n)
    # 첫째 조각의 사슬 b_{n,0}<...<b_{n,k_n-1}
    if n >= 2 and not all(row[i] < row[i + 1] for i in range(0, kn(n) - 1)):
        broken.append(n)
    if n >= 2 and not row[kn(n) - 1] < row[kn(n)] if kn(n) < n else False:
        mid_fail.append(n)
    if n >= 4 and not row[1] >= (n - 1) * factorial(n) // 2:
        first_cmp_fail.append(n)
    # Q_R(n): (n-1)/2 <= l <= n-3
    for l in range(n):
        if 2 * l >= n - 1 and l <= n - 3:
            if row[l] > row[l + 1] and not row[l + 1] ** 2 >= row[l] * row[l + 2]:
                QR_fail.append((n, l))
print("unimodality failures:", uni_fail)
print("chain b_0<...<b_{k_n-1} broken at n =", broken)
print("middle increase fails at n =", mid_fail)
print("b_{n,1} >= (n-1) n!/2 fails:", first_cmp_fail)
print("Q_R failures:", QR_fail[:10])

# 증인 위치 상계 (50 <= n <= N)
lo, hi = 10, -10
for n in range(50, N + 1):
    row = [b(n, l) for l in range(n)]
    m = max(row)
    ls = row.index(m)
    v = n + 1 - ls - 0.59963 * (n + 1) ** (2 / 3) - 1.24847 * (n + 1) ** (1 / 3)
    if v < lo: lo, nlo = v, n
    if v > hi: hi, nhi = v, n
if N >= 50:
    print("witness offset range for 50<=n<=%d: [%.6f (n=%d), %.6f (n=%d)]" % (N, lo, nlo, hi, nhi))

# 위치 수
def cnt(n0, n1):
    t = 0
    for n in range(n0, n1 + 1):
        lo_ = -(-(n - 1) // 2)
        t += max(0, n - 3 - lo_ + 1)
    return t
print("positions 5..20000:", cnt(5, 20000), " positions 20001..50000:", cnt(20001, 50000))
print("second piece comparisons:", sum(kn(n) - 1 for n in range(10001, 20001)))
print("94192042+5777960 =", 94192042 + 5777960)
# 열 범위
print("2*ceil(141^2/4) =", 2 * math.ceil(141 ** 2 / 4), " 2*ceil(142^2/4) =", 2 * math.ceil(142 ** 2 / 4))
