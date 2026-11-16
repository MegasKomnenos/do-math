# Q2: 3장 수치 검산 — 정리 3.4(n<=80 로그오목성), 정리 3.6 수치, 1.3 표(n<=10) 증인
from fractions import Fraction as Fr
from math import comb, isqrt
import sys
NMAX = 80
L = NMAX  # columns 0..NMAX-1
# A[n][l]
A = [[0]*(L+1) for _ in range(NMAX+1)]
for l in range(L+1):
    A[0][l] = 1
for n in range(1, NMAX+1):
    pn = (n+1)**(n-1)
    for l in range(L+1):
        if l >= n-1:
            A[n][l] = pn
        else:
            s = 0
            for j in range(n):
                s += comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l]
            A[n][l] = s
def b(n, l):
    if l < 0: return 0
    return A[n][l] - (A[n][l-1] if l >= 1 else 0)
# row sums
for n in range(1, NMAX+1):
    assert sum(b(n, l) for l in range(n)) == (n+1)**(n-1), n
    assert A[n][0] == __import__('math').factorial(n)
# log-concavity
fails = []
for n in range(1, NMAX+1):
    for l in range(1, n-1):
        if b(n, l)**2 < b(n, l-1)*b(n, l+1):
            fails.append((n, l))
print("LC fails n<=80:", fails)
b39, b40, b41 = b(80, 39), b(80, 40), b(80, 41)
print("b80,39 =", b39); print("b80,40 =", b40); print("b80,41 =", b41)
print("increasing:", b39 < b40 < b41, " b39*b41-b40^2>0:", b39*b41 - b40**2 > 0)
print("ratios:", Fr(b40, b39).__float__(), Fr(b41, b40).__float__())
# witnesses n<=10
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    m = max(row); wit = [l for l in range(n) if row[l] == m]
    print(n, row, "witness", wit, "ceil(n/2)=", -(-n//2))
# 정리 3.6: E_n omega_n for n=1..5
def p(m): return (m+1)**(m-1) if m >= 1 else 1
for n in range(1, 6):
    s = sum(Fr(comb(n, j)*j**j*p(n-j), p(n)) for j in range(1, n//2+1))
    print("E omega", n, s, float(s), "<= sqrt n:", float(s)**2 <= n)
print("9n^2-48n-32 at 6:", 9*36-48*6-32)
lam = Fr(751, 1000); J = 8
val = lam**J + Fr(1, 31)*sum(i*lam**(i-1) for i in range(1, J+1)) + Fr(1, 1000)*sum((i-1)*lam**(i-1) for i in range(1, J+1))
print("bound:", val, float(val), val == Fr(7309649993107890414228499, 15500000000000000000000000))
# tail ratio
print("(3/4)^1.5 =", 0.75**1.5, " 2^-3*3^1.5=", 2**-3*3**1.5)
# residue check of Mellin at sigma=3/2 vs 3/sqrt(2pi)
from math import gamma, pi, sqrt
res = 3*sqrt(1.5)*gamma(1/3)/gamma(5/6)*gamma(2/3)/(sqrt(pi)*gamma(1/6))
print("residue", res, "3/sqrt(2pi)", 3/sqrt(2*pi))
# Legendre: Gamma(1/3)Gamma(5/6) = 2^{1/3} sqrt(pi) Gamma(2/3)
print(gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
