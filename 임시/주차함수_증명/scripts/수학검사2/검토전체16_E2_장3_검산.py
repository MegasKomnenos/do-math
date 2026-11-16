# 검토전체16 E2: 3장 수치 검산 (정확 정수·유리수)
# (1) 정리 3-6의 유리수 상계, (2) 1.3절 표의 증인(n<=10), (3) E_n omega_n (n<=5),
# (4) 정리 3-4: n<=80 행의 로그오목성과 b_{80,39..41}, (5) Legendre 배가 공식 수치 점검.
from fractions import Fraction as Fr
from math import comb, gamma, pi, sqrt, ceil, floor
import sys

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

# (1) 정리 3-6 상계
lam = Fr(751, 1000); J = 8
val = lam**J + Fr(1, 31) * sum(i * lam**(i - 1) for i in range(1, J + 1)) + Fr(1, 1000) * sum((i - 1) * lam**(i - 1) for i in range(1, J + 1))
print("3-6 상계:", val, float(val), "< 0.4716:", val < Fr(4716, 10000))
print("  분자/분모 일치:", val == Fr(7309649993107890414228499, 15500000000000000000000000))
# lambda <= 3/4 + 3/(4n) 확인 (n=1000..1100)
print("  lam bound:", all(Fr(ceil(Fr(3*n,4)), n) <= Fr(751,1000) for n in range(1000, 5000)))

# (4) A_{n,l} 일반 재귀: A_{m+1,l} = sum_j C(m,j) min(j+1,l+1) A_{j,l} A_{m-j,l}
def column(l, N):
    A = [0] * (N + 1); A[0] = 1
    for m in range(N):
        s = 0
        for j in range(m + 1):
            s += comb(m, j) * min(j + 1, l + 1) * A[j] * A[m - j]
        A[m + 1] = s
    return A

N = 80
cols = [column(l, N) for l in range(N)]  # cols[l][n] = A_{n,l}
def A(n, l):
    if l < 0: return 0
    if l >= n - 1: return p(n)
    return cols[l][n]
def b(n, l):
    return A(n, l) - A(n, l - 1)
# 검증: 합이 p_n
assert all(sum(b(n, l) for l in range(n)) == p(n) for n in range(1, N + 1))
# (2) 1.3절 표의 증인: 최댓값 첨자 전부
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    mx = max(row); wit = [l for l in range(n) if row[l] == mx]
    print(f"n={n} row={row} 증인={wit} ceil(n/2)={ceil(n/2)} 모두 작다: {all(w < ceil(n/2) for w in wit)}")
# 로그오목성 검사
first_fail = None
for n in range(1, N + 1):
    row = [b(n, l) for l in range(n)]
    assert all(x > 0 for x in row), n
    bad = [l for l in range(1, n - 1) if row[l]**2 < row[l-1]*row[l+1]]
    if bad:
        print(f"n={n} LC 실패 l={bad}")
        if first_fail is None: first_fail = n
print("첫 실패 n =", first_fail)
r = [b(80, l) for l in range(80)]
print("b80,39<b80,40<b80,41:", r[39] < r[40] < r[41], " b40^2<b39*b41:", r[40]**2 < r[39]*r[41])
print("n=80 증인:", [l for l in range(80) if r[l] == max(r)])
# 단봉성 n<=80
for n in range(1, N + 1):
    row = [b(n, l) for l in range(n)]
    wit = row.index(max(row))
    assert all(row[i] <= row[i+1] for i in range(wit)) and all(row[i] >= row[i+1] for i in range(wit, n-1)), n

# (3) E_n omega_n
for n in range(1, 6):
    w = sum(Fr(comb(n, j) * j**j * p(n - j), p(n)) for j in range(1, n // 2 + 1))
    print(f"E_{n} omega = {w}  <= sqrt n: {float(w) <= sqrt(n)}")
# 9n^2-48n-32 at n=6
print("9*36-48*6-32 =", 9*36 - 48*6 - 32)
# (5) Legendre: Gamma(1/3)Gamma(5/6) = 2^{1/3} sqrt(pi) Gamma(2/3)
print("Legendre:", gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
# 꼬리 상수 (3/4)^{3/2}
print("(3/4)^1.5 =", 0.75**1.5, " 2^-3*3^1.5 =", 2**-3 * 3**1.5)
# E_n(n-G) <= sqrt n 직접 확인 (n<=40): 가장 큰 나무 분포
# Pr_n(G<=y) 계산: 숲을 나무 크기<=y 로 제한한 EGF
def forests_max_tree_le(y, N):
    # f[n] = number of rooted forests on n labeled vertices with all trees of size <= y
    f = [0]*(N+1); f[0] = 1
    for m in range(N):
        f[m+1] = sum(comb(m, j) * (j+1)**j * f[m-j] for j in range(min(m, y-1)+1))
    return f
Nn = 40
tabs = [forests_max_tree_le(y, Nn) for y in range(0, Nn+1)]
for n in [1,2,3,4,5,6,10,20,40]:
    # E(n-G) = sum_y Pr(G<=y) for y=0..n-1  (n-G = sum_{y=0}^{n-1} 1[G<=y])
    e = sum(Fr(tabs[y][n], p(n)) for y in range(0, n))
    print(f"E_{n}(n-G) = {float(e):.4f} <= sqrt n {sqrt(n):.4f}: {float(e) <= sqrt(n)}")
