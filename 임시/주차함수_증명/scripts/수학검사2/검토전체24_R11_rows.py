# -*- coding: utf-8 -*-
# R11 검산: D.exact-n20000 (ㅁ) 작은 행(정확 정수): 단봉성, 왼쪽 엄격 증가가 깨지는 n, (ㄹ)의 분류 성질
from math import comb
N = 160
B = []
for l in range(0, N):
    A = [1]
    for n in range(1, N + 1):
        A.append(sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j] for j in range(n)))
    B.append(A)
def row(n): return [B[l][n] - (B[l - 1][n] if l else 0) for l in range(n)]
bad_inc = []; nonuni = []; qr_bad = []; order_bad = []
for n in range(1, N + 1):
    b = row(n); kn = (n + 1) // 2
    if not all(b[i] < b[i + 1] for i in range(0, kn - 1)): bad_inc.append(n)
    # unimodal: no decrease followed by increase
    dec = False; ok = True
    for i in range(n - 1):
        if b[i] > b[i + 1]: dec = True
        elif b[i] < b[i + 1] and dec: ok = False
    if not ok: nonuni.append(n)
    if n >= 5:
        kinds = []
        for l in range(-(-(n - 1) // 2), n - 2):
            if b[l] <= b[l + 1]: kinds.append('I')
            elif b[l + 1] ** 2 > b[l] * b[l + 2] and b[l] + b[l + 2] < 2 * b[l + 1]: kinds.append('Q')
            else: kinds.append('X')
        if 'X' in kinds: qr_bad.append(n)
        s = ''.join(kinds)
        if 'QI' in s: order_bad.append(n)
print("strict left increase fails at n:", bad_inc)
print("non-unimodal n:", nonuni, " (ㄹ) classification failures:", qr_bad, order_bad)
