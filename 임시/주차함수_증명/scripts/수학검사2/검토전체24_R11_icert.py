# -*- coding: utf-8 -*-
# R11 검산: D.central-gap-integer 의 네 재귀를 정의(순열 전수)와 대조, (ㄴ) 작은 행, 근사 비
from itertools import permutations
from fractions import Fraction
from math import comb, factorial

def brute(n, k):
    A = D1 = E = J = 0
    for s in permutations(range(1, n + 1)):
        prod = 1; H = Z = 0
        for i in range(n):
            j = i - 1
            while j >= 0 and s[j] < s[i]:
                j -= 1
            h = i - j
            if h < k: prod *= h
            elif h == k: H += 1
            else: Z += 1
        A += prod * k ** (H + Z)
        D1 += prod * k ** H * Z * k ** (Z - 1) if Z >= 1 else 0
        E += prod * k ** H * Z * (Z - 1) * k ** (Z - 2) if Z >= 2 else 0
        J += prod * H * k ** (H - 1) * (k - 1) ** Z if H >= 1 else 0
    return A, D1, E, J

def p(i): return (i + 1) ** (i - 1) if i >= 1 else 1

def rec(k, s=Fraction(2918732888, 2 ** 30)):
    # returns unnormalized A, K', e, J for n=0..2k by the D recursions
    r = [Fraction(p(i), factorial(i)) / s ** i for i in range(2 * k + 2)]
    a = {}; d = {}; z = {}; j = {}
    for i in range(k + 1):
        a[i] = r[i]; d[i] = Fraction(0); z[i] = Fraction(0); j[i] = Fraction(0)
    j[k] = r[k - 1] / (s * k)
    for n in range(k + 1, 2 * k + 1):
        rr = n - k
        a[n] = (sum((k + i + 1) * r[i] * a[n - 1 - i] for i in range(0, rr - 1)) + sum(min(i + 1, k) * r[i] * r[n - 1 - i] for i in range(rr - 1, k + 1))) / (s * n)
        d[n] = (sum((k + i + 1) * r[i] * d[n - 1 - i] for i in range(0, rr - 1)) + sum(r[i] * a[n - 1 - i] for i in range(0, rr))) / (s * n)
        z[n] = (sum((k + i + 1) * r[i] * z[n - 1 - i] for i in range(0, rr - 1)) + 2 * sum(r[i] * d[n - 1 - i] for i in range(0, rr - 1))) / (s * n)
        j[n] = (sum((k + i) * r[i] * j[n - 1 - i] for i in range(0, rr)) + r[k - 1] * r[n - k]) / (s * n)
    un = lambda x, n: x * factorial(n) * s ** n
    return {n: (un(a[n], n), un(d[n], n), un(z[n], n), un(j[n], n)) for n in range(k, 2 * k + 1)}

ok = True
for k in range(2, 5):
    R = rec(k)
    for n in range(k, min(2 * k, 8) + 1):
        b = brute(n, k)
        if tuple(R[n]) != tuple(Fraction(x) for x in b):
            ok = False; print("MISMATCH", n, k, R[n], b)
print("recursions vs brute force (k=2..4, n<=min(2k,8)):", ok)

# exact rows
N = 80
B = {}
for l in range(0, N):
    A = [1]
    for n in range(1, N + 1):
        A.append(sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j] for j in range(n)))
    B[l] = A
def b(n, l): return B[l][n] - (B[l - 1][n] if l >= 1 else 0)
neg = []; nonincr_ok = True
for n in range(2, 61):
    kn = (n + 1) // 2
    dd = b(n, kn) - b(n, kn - 1)
    if dd < 0:
        neg.append(n)
        if not all(b(n, j) >= b(n, j + 1) for j in range(kn, n - 1)): nonincr_ok = False
    elif dd == 0: print("ZERO", n)
print("d_{n,k_n}<0 exactly for n in", neg, "; right half nonincreasing there:", nonincr_ok)

# e_n - J_n(k-1) <= d_{n,k}; ratios
mn = None
for k in range(8, 41):
    R = rec(k)
    for n in (2 * k - 1, 2 * k):
        if n < 16: 
            print("n=15: e/J =", float(R[n][2] / R[n][3])); continue
        A_, D_, E_, J_ = R[n]
        dd = b(n, k) - b(n, k - 1)
        assert A_ == B[k - 1][n]
        assert dd >= E_ - J_, (n, k)
        if n == 2 * k - 1: assert b(n, k - 1) - 0 >= 0
        ratio = E_ / J_
        if mn is None or ratio < mn[0]: mn = (ratio, n)
print("min e/J over 16<=n<=80:", float(mn[0]), "at n=", mn[1])
