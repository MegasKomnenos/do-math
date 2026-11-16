# -*- coding: utf-8 -*-
"""결정 K4 검산 1: E5(증인 위치 상계로 9.10 둘째 주장), N1(두 원천의 차 항등식), S9(무게 상수배), s^F 죽은 항.

E5: 3132<=k<=19403, q0=floor(0.75 k^{2/3}) 에서 q0 >= f(k+q0), f(i)=0.99+0.59963(i+1)^{2/3}+1.24847(i+1)^{1/3}
    (조건: 행 m=k+q 가 단봉이고 봉우리 ell*_m >= m+1-B(m+1) 이면 k <= ell*_m <=> q >= B(k+q+1)-1 = f(k+q)).
    q - f(k+q) 는 q 에 증가(f' < 1) 이므로 q0 에서의 확인으로 q0 <= q <= min(k-1, 20000-k) 전체가 덮인다.
N1: regen_n - A_{n,k-1}(*)(n) = sum_{m=2k+1}^{n-1} L_{n,m} d_{m,k}, L_{n,m} = [1+(n-m-1)(1-k/(m+1))] C(n-1,m) A_{n-m-1,k-1}
    정확 정수로 k=2..9, 2k+1<=n<=3k-1 전수 (마지막 차 재귀로 A_{n,l} 생성).
S9: frak w_n(m+1) = n A_{n,k-1} w_m  (정확 정수).
s^F: 103<=nu<=k 에서 s^up_{nu+1}(k+1) <= s^F(k,nu) (배정밀도 표본 + 해석 근거).
"""
from fractions import Fraction as Fr
from math import comb, floor
import sys

def f_witness(i):
    return 0.99 + 0.59963 * (i + 1) ** (2.0 / 3.0) + 1.24847 * (i + 1) ** (1.0 / 3.0)

def check_E5():
    worst = (1e9, None)
    fails = []
    for k in range(3132, 19404):
        q0 = floor(0.75 * k ** (2.0 / 3.0))
        qmax = min(k - 1, 20000 - k)
        if q0 > qmax:
            continue  # 범위 비어 있음(실제로는 k<=19403 에서 비지 않음)
        margin = q0 - f_witness(k + q0)
        if margin < 0:
            fails.append((k, q0, margin))
        if margin < worst[0]:
            worst = (margin, (k, q0))
    # 단조성: q - f(k+q) 증가 — f'(i) = 0.59963*(2/3)(i+1)^{-1/3} + 1.24847/3 (i+1)^{-2/3} < 1 for i>=1
    fp = lambda i: 0.59963 * (2 / 3) * (i + 1) ** (-1 / 3) + 1.24847 / 3 * (i + 1) ** (-2 / 3)
    print("E5: 실패 열 수 =", len(fails), fails[:5], "; 최소 여유 q0-f(k+q0) =", worst)
    print("E5: max f'(i) over i in [3132, 40000] =", max(fp(i) for i in range(3132, 40001)), "(<1 이면 q-f 증가)")
    # 증인 상계만으로 얻는 m_1(k)-k 의 상계 q* = min{q: q >= f(k+q)} 와 0.75 k^{2/3} 비교
    for k in (3132, 5000, 10000, 19403):
        q = 1
        while q < f_witness(k + q):
            q += 1
        print("  k=%d: q*=%d, q*/k^(2/3)=%.4f, floor(0.75k^(2/3))=%d" % (k, q, q / k ** (2 / 3), floor(0.75 * k ** (2 / 3))))

def A_table(nmax, lmax):
    # A[n][l] : 용량 l+1 ... 여기서는 정리 2.6 의 마지막 차 재귀 A_{m,l} = sum_j C(m-1,j-1) min(j,l+1) A_{j-1,l} A_{m-j,l}
    A = [[0] * (lmax + 1) for _ in range(nmax + 1)]
    for l in range(lmax + 1):
        A[0][l] = 1
        for m in range(1, nmax + 1):
            s = 0
            for j in range(1, m + 1):
                s += comb(m - 1, j - 1) * min(j, l + 1) * A[j - 1][l] * A[m - j][l]
            A[m][l] = s
    return A

def check_N1_S9():
    kmax = 9
    nmax = 3 * kmax
    A = A_table(nmax, kmax + 1)
    ok = True
    cnt = 0
    for k in range(2, kmax + 1):
        for n in range(2 * k + 1, 3 * k):
            d = lambda m: A[m][k] - 2 * A[m][k - 1] + A[m][k - 2]
            # regen_n = d_n - k sum C(n,m+1) A_{n-m-1,k-1} d_m
            regen = d(n) - k * sum(comb(n, m + 1) * A[n - m - 1][k - 1] * d(m) for m in range(2 * k + 1, n))
            # A_{n,k-1}(*)(n) = d_n - KD'_n,  KD'_n = sum_{m>2k} (k+n-m) C(n-1,m) p_{n-1-m} d_m  (n<=3k 라 A_{n-1-m,k-1}=p_{n-1-m})
            p = lambda t: (t + 1) ** (t - 1) if t >= 1 else 1
            KDp = sum((k + n - m) * comb(n - 1, m) * p(n - 1 - m) * d(m) for m in range(2 * k + 1, n))
            Astar = d(n) - KDp
            L = lambda m: Fr(1) + (n - m - 1) * (1 - Fr(k, m + 1))
            rhs = sum(L(m) * comb(n - 1, m) * A[n - m - 1][k - 1] * d(m) for m in range(2 * k + 1, n))
            lhs = Fr(regen - Astar)
            if lhs != rhs:
                ok = False
                print("N1 불일치", k, n, lhs, rhs)
            if any(L(m) <= 0 for m in range(2 * k + 1, n)):
                ok = False
                print("L<=0", k, n)
            cnt += 1
            # S9: frak w_n(m+1) = C(n,m+1)(m+1)^m A_{n-m-1,k-1} ; w_m = C(n-1,m) p_m A_{n-1-m,k-1}/A_{n,k-1}
            for m in range(k, n):
                lhsw = comb(n, m + 1) * (m + 1) ** m * A[n - m - 1][k - 1]
                rhsw = n * comb(n - 1, m) * p(m) * A[n - 1 - m][k - 1]
                if lhsw != rhsw:
                    ok = False
                    print("S9 불일치", k, n, m)
    print("N1·S9: 전수(k=2..%d, 2k+1<=n<=3k-1, 경우 %d) 일치 =" % (kmax, cnt), ok)

def check_sF():
    worst = 0.0
    for k in (6667, 6668, 8065, 9705, 20000, 10 ** 5, 10 ** 6):
        for nu in range(103, k + 1, max(1, k // 500)):
            sF = min(1.0, 3 * (k + 1) * (nu - 1) ** -1.5)
            sup = min(1.0, 1.15 * (k + nu + 2) * (nu + 1) ** -1.5)
            r = sup / sF
            worst = max(worst, r)
    print("s^F: max_(k,nu) s^up_{nu+1}(k+1)/s^F(k,nu) (표본) =", round(worst, 4), "(해석: <= 1.15*2/3 * ((nu-1)/(nu+1))^{3/2} < 0.7667 또는 둘 다 1)")

if __name__ == "__main__":
    check_E5()
    check_N1_S9()
    check_sF()
