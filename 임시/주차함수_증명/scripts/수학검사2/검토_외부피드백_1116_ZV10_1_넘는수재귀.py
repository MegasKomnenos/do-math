# -*- coding: utf-8 -*-
"""ZV10 검산 1 — 부록 D.exact-n20000 (ㄹ)의 넘는 수 선형 재귀가 정리 2.6(마지막 차 재귀)에서 나오는지 확인한다.

(1) 작은 n에서 모든 선호 수열을 전수 주차해 A_{n,l}(최대 변위 <= l)을 센다(정리 2.6과 독립).
(2) 정리 2.6의 마지막 차 재귀 A_{n,l} = sum_j C(n-1,j-1) min(j,l+1) A_{j-1,l} A_{n-j,l}로 A_{n,l}을 센다.
(3) (ㄹ)의 재귀 A^c_{n,k-1} = sum_{i=0}^{n-k-1} C(n-1,i)(n-k-i) p_i p_{n-1-i} + sum_{i=0}^{n-k-2} C(n-1,i)(k+i+1) p_i A^c_{n-1-i,k-1}
    (k+1 <= n <= 2k+1)을 돌려 p_n - A_{n,k-1}과 비교한다. 범위 밖(n >= 2k+2)에서는 어긋남을 보인다.
(4) 부록 D.crossing-small-n의 넘는 수 재귀(수준 l 고정)도 같은 값인지 비교한다.
실행: python -I scripts/수학검사2/검토_외부피드백_1116_ZV10_1_넘는수재귀.py
"""
from itertools import product
from math import comb

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

def brute_A(n):
    """A[l] = #{선호 수열이 주차함수이고 최대 변위 <= l}, l = 0..n-1"""
    A = [0] * n
    for pref in product(range(1, n + 1), repeat=n):
        occ = [False] * (n + 2)
        M = 0; ok = True
        for a in pref:
            s = a
            while s <= n and occ[s]:
                s += 1
            if s > n:
                ok = False; break
            occ[s] = True
            M = max(M, s - a)
        if ok:
            for l in range(M, n):
                A[l] += 1
    return A

def A_rec26(N, l):
    """정리 2.6의 마지막 차 재귀로 A_{n,l}, n = 0..N"""
    A = [1] + [0] * N
    for n in range(1, N + 1):
        A[n] = sum(comb(n - 1, j - 1) * min(j, l + 1) * A[j - 1] * A[n - j] for j in range(1, n + 1))
    return A

def Ac_rec_D5A(N, k):
    """(ㄹ)의 재귀. 초기값: n <= k 에서 A^c_{n,k-1} = 0 (최대 변위 <= n-1 <= k-1)."""
    Ac = [0] * (N + 1)
    for n in range(k + 1, N + 1):
        s1 = sum(comb(n - 1, i) * (n - k - i) * p(i) * p(n - 1 - i) for i in range(0, n - k))
        s2 = sum(comb(n - 1, i) * (k + i + 1) * p(i) * Ac[n - 1 - i] for i in range(0, n - k - 1))
        Ac[n] = s1 + s2
    return Ac

def Ac_rec_D4(N, l):
    """부록 D.crossing-small-n 「식」의 넘는 수 재귀(수준 l 고정, n<=2l+4; 계수 (l+1)+min(n-i,l+1))."""
    Ac = [0] * (N + 1)
    for n in range(l + 2, N + 1):
        s1 = sum(comb(n - 1, j) * (j - l) * p(j) * p(n - 1 - j) for j in range(l + 1, n))
        s2 = sum(Ac[i] * comb(n - 1, i) * p(n - 1 - i) * ((l + 1) + min(n - i, l + 1)) for i in range(l + 2, n))
        Ac[n] = s1 + s2
    return Ac

if __name__ == "__main__":
    # (1) vs (2)
    for n in range(1, 8):
        bA = brute_A(n)
        for l in range(n):
            rA = A_rec26(n, l)[n]
            assert bA[l] == rA, (n, l, bA[l], rA)
    print("[1·2] n<=7 전수 주차 = 정리 2.6 재귀: 일치")
    # (3) (ㄹ) vs 2.6 in range k+1<=n<=2k+1, and out of range
    N = 80
    bad_in, bad_out, tot_in = 0, 0, 0
    for k in range(1, 40):
        Ac = Ac_rec_D5A(N, k)
        A = A_rec26(N, k - 1)
        for n in range(k + 1, N + 1):
            true = p(n) - A[n]
            if n <= 2 * k + 1:
                tot_in += 1
                if Ac[n] != true: bad_in += 1
            else:
                if Ac[n] != true: bad_out += 1
    print(f"[3] (ㄹ) 재귀: 범위 k+1<=n<=2k+1 안 {tot_in}자리 가운데 어긋남 {bad_in}; 범위 밖(n>=2k+2) 어긋남 {bad_out}자리(겹침 항이 빠지므로 어긋나야 정상)")
    # (4) D.central-gap-integer formula
    bad4, tot4 = 0, 0
    for l in range(0, 30):
        Ac4 = Ac_rec_D4(N, l)
        A = A_rec26(N, l)
        for n in range(l + 2, min(N, 2 * l + 4) + 1):
            tot4 += 1
            if Ac4[n] != p(n) - A[n]: bad4 += 1
    print(f"[4] D.crossing-small-n 재귀(범위 l+2<=n<=2l+4): {tot4}자리 가운데 어긋남 {bad4}")
