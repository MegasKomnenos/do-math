# -*- coding: utf-8 -*-
"""검토전체6 L1: 1.3절 표(b_{n,l}, n<=10), 1.4절 가운데 비교 부호(n<=20), 명제 old-2-20의 유한 n 상계 네 값 재계산.
python -I 로 돌린다. 표준 라이브러리만 쓴다."""
from fractions import Fraction
from math import comb, factorial, exp, log
import itertools

def A_table(N):
    # 마지막 차 재귀 (정리 old-2-6): A[n][l]
    A = [[0]*(N+1) for _ in range(N+1)]
    for l in range(N+1):
        A[0][l] = 1
    for n in range(1, N+1):
        for l in range(N+1):
            s = 0
            for j in range(n):
                s += comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l]
            A[n][l] = s
    return A

def b_row(A, n):
    return [A[n][l] - (A[n][l-1] if l >= 1 else 0) for l in range(n)]

def brute_row(n):
    # 주차 과정을 직접 돌려 b_{n,l}을 센다 (n<=7)
    row = [0]*n
    for a in itertools.product(range(1, n+1), repeat=n):
        occ = [False]*(n+2)
        ok = True; M = 0
        for i in range(n):
            p = a[i]
            while p <= n and occ[p]:
                p += 1
            if p > n:
                ok = False; break
            occ[p] = True
            M = max(M, p - a[i])
        if ok:
            row[M] += 1
    return row

N = 20
A = A_table(N)
print("== 1.3절 표 (n<=10) ==")
for n in range(1, 11):
    r = b_row(A, n)
    print(n, r, sum(r), (n+1)**(n-1), "합일치" if sum(r) == (n+1)**(n-1) else "합불일치")
print("== 무차별 대조 (n<=7) ==")
for n in range(1, 8):
    print(n, brute_row(n) == b_row(A, n))
print("== 가장 작은 증인 ell*_n (n<=10) ==")
for n in range(1, 11):
    r = b_row(A, n)
    print(n, r.index(max(r)))
print("== 가운데 비교 d_{n,k_n}, k_n=ceil(n/2) (2<=n<=20) ==")
for n in range(2, N+1):
    r = b_row(A, n)
    k = -(-n//2)
    d = r[k] - r[k-1]
    print(n, k, d, "증가" if d > 0 else "감소/같음")

# 명제 old-2-20 유한 n 상계
def v(k, Z, H):
    return (1+1/k)**Z + (1-1/k)**(Z+H) - 2

def bound(n, b):
    # 조건: 3<=i<=b, n/2<k<=n 에서 v_k(i-1,1)<0
    for i in range(3, b+1):
        for k in range(n//2+1, n+1):
            if not (v(k, i-1, 1) < 0):
                return None
    tot1 = Fraction(0); tot2 = Fraction(0)
    pn = Fraction((n+1)**(n-1))
    for c in range(n//2+1, n+1):
        kap = n - c - b + 1
        if kap < 0:
            continue
        base = Fraction(factorial(n), factorial(c)) * c**(c-1) / pn
        t1 = base * b * Fraction(n-c+1)**(n-c-b) / factorial(kap)
        t2 = base * 2 * Fraction(n-c-b+3)**(n-c-b) / factorial(kap)
        tot1 += t1; tot2 += t2
    return 1 - tot1 + tot2

print("== 명제 old-2-20 유한 n 상계 ==")
for n in (17, 100, 1000, 10000):
    best = None
    for b in range(3, 40):
        val = bound(n, b)
        if val is None:
            continue
        if best is None or val < best[1]:
            best = (b, val)
    print(n, "최적 b =", best[0], "상계 =", float(best[1]))
