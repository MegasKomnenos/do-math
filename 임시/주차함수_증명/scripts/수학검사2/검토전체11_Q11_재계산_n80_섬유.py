# -*- coding: utf-8 -*-
"""11.2 표(부록 D.logconcavity-failure-n80, D.fiber-enumeration)의 셀 수 있는 수를 다시 센다.
(1) 정리 2:old-2-6의 마지막 차 재귀로 A_{n,l}(n<=80)을 정확 정수로 만들어 행의 로그오목성 첫 실패와 n=80의 세 정수·분리자 교차곱을 본다.
(2) n<=7의 모든 순열에서 용량 다중집합의 수, 곱 공식 행의 단봉성, n=7의 비단봉 섬유 수와 사전식 첫째를 센다.
(3) n<=7의 선호 수열을 모두 직접 주차시켜 p_n과 섬유 행(첫 비단봉 섬유)을 대조한다."""
from math import comb
from fractions import Fraction
from itertools import permutations, product
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NMAX = 80
A = [[0] * (NMAX + 1) for _ in range(NMAX + 1)]  # A[n][l]
for l in range(NMAX + 1):
    A[0][l] = 1
for n in range(1, NMAX + 1):
    for l in range(NMAX + 1):
        s = 0
        for j in range(n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l]
        A[n][l] = s
# 검산: 행 합 (n+1)^{n-1}, A_{n,0}=n!
from math import factorial
assert all(A[n][n - 1] == (n + 1) ** (n - 1) for n in range(1, NMAX + 1))
assert all(A[n][0] == factorial(n) for n in range(1, NMAX + 1))
def b(n, l): return A[n][l] - (A[n][l - 1] if l >= 1 else 0)
first = None
for n in range(1, NMAX + 1):
    for l in range(1, n - 1):
        if b(n, l) ** 2 < b(n, l - 1) * b(n, l + 1):
            first = (n, l); break
    if first: break
print('first log-concavity failure (n,l):', first)
n = 80
b39, b40, b41 = b(80, 39), b(80, 40), b(80, 41)
print('b_80,39 < b_80,40 < b_80,41 ?', b39 < b40 < b41)
print('b40^2 - b39*b41 =', b40 ** 2 - b39 * b41, '(negative expected)')
sep = Fraction(25928, 25000)
print('b40/b39 vs 25928/25000 vs b41/b40:', float(Fraction(b40, b39)), float(sep), float(Fraction(b41, b40)))
print('cross products: 25000*b40 - 25928*b39 =', 25000 * b40 - 25928 * b39, '; 25928*b40 - 25000*b41 =', 25928 * b40 - 25000 * b41)
print('digits of b_80,40:', len(str(b40)))

# (2) 섬유
def caps(sig):
    h = []
    for i, s in enumerate(sig, 1):
        last = 0
        for j in range(i - 1, 0, -1):
            if sig[j - 1] > s: last = j; break
        h.append(i - last)
    return h
def unimodal(row):
    i = 0
    while i + 1 < len(row) and row[i] <= row[i + 1]: i += 1
    while i + 1 < len(row) and row[i] >= row[i + 1]: i += 1
    return i == len(row) - 1
counts = []
for m in range(1, 8):
    seen = set(); bad = []
    for sig in permutations(range(1, m + 1)):
        h = caps(sig); key = tuple(sorted(h)); seen.add(key)
        Acum = [1]
        for l in range(m):
            p = 1
            for hi in h: p *= min(hi, l + 1)
            Acum.append(p)
        row = [Acum[l + 1] - Acum[l] for l in range(m)]
        if not unimodal(row): bad.append((sig, tuple(h), tuple(row)))
    counts.append(len(seen))
    if bad: print(f'n={m}: non-unimodal fibers {len(bad)}; lexicographic first:', min(bad))
    else: print(f'n={m}: all fibers unimodal')
print('distinct capacity multisets n=1..7:', counts)

# (3) 직접 주차 (n<=7)
def park(pref):
    n = len(pref); spots = [0] * (n + 1); disp = [0] * n; order = []
    for c, a in enumerate(pref):
        p = a
        while p <= n and spots[p]: p += 1
        if p > n: return None
        spots[p] = c + 1; disp[c] = p - a
    return spots[1:], max(disp)
for m in (6, 7):
    cnt = 0; fib = {}
    for pref in product(range(1, m + 1), repeat=m):
        r = park(pref)
        if r is None: continue
        cnt += 1
        sig, M = r
        fib.setdefault(tuple(sig), [0] * m)[M] += 1
    print(f'n={m}: parking functions {cnt} (expected {(m+1)**(m-1)}); all permutations appear: {len(fib)==factorial(m)}')
    if m == 7:
        tgt = (1, 2, 3, 5, 4, 6, 7)
        print('  fiber row of sigma=(1,2,3,5,4,6,7) by direct parking:', fib[tgt], ' caps:', caps(tgt))
        print('  non-unimodal fibers by direct parking:', sum(1 for r in fib.values() if not unimodal(r)))
