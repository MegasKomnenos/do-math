# -*- coding: utf-8 -*-
"""외부 피드백 셋째 묶음 12.1·12.3의 검산 (ZV7, 2026-11-16).

(A) 12.1 — 보조정리 7:vertical-nu의 정규화 상수 n_k = (n!/p_n) e^{n+1}/(2 pi k^{3/2}), p_n=(n+1)^{n-1}.
    피드백의 반례 k=2, nu=2, n=6의 값을 다시 세고, 증명의 두 단계
      (i) (3/2+1/(2k))^{3/2} e^{1/(24k)} < 1.84,  (ii) n_k < 2.08 (1<=nu<=k 전부)
    가 성립하기 시작하는 k를 찾는다. k=10000에서의 성립과 Bn_k 상계도 확인한다.
(B) 12.3 — 보조정리 2:old-2-34의 항별 부등식 c_m(Y) >= s_{m-1}(Y) - s_m(Y) (m>=Y+1)를
    정확 유리수(A_{m,ell}의 마지막 차 재귀; 정리 2:old-2-6)로 m<=40, Y<=12에서 전수 확인하고,
    (DM0) s_m(y) <= s_{m+1}(y+1)과 w==1의 망원합 sum c_m(Y) >= 1 - s_K(Y)도 확인한다.
    또 단조가 아닌 음이 아닌 무게에 대해서도 가중 부등식이 성립함을 보기로 확인한다.
실행: python -I scripts/수학검사2/검토_외부피드백_1116_ZV7_검산.py
"""
from fractions import Fraction
from functools import lru_cache
from math import comb
import random

from mpmath import mp, mpf, e, pi, sqrt, factorial, exp

mp.dps = 30


def n_k(k, nu):
    n = 2 * k + nu
    return factorial(n) / mpf(n + 1) ** (n - 1) * e ** (n + 1) / (2 * pi * mpf(k) ** mpf(1.5))


def part_A():
    print("=== (A) 12.1 정규화 상수 n_k")
    v = n_k(2, 2)
    print("n_k(k=2, nu=2, n=6) =", mp.nstr(v, 15), " (피드백: 2.64349691448...)  >2.08:", v > mpf("2.08"))
    n_inf = 2 / sqrt(pi)
    print("n_inf = 2/sqrt(pi) =", mp.nstr(n_inf, 12), "; 1.84*n_inf =", mp.nstr(mpf("1.84") * n_inf, 12), "(<2.08)")

    def bound(k):
        return (mpf(3) / 2 + mpf(1) / (2 * k)) ** mpf(1.5) * exp(mpf(1) / (24 * k))

    k = 2
    while bound(k) >= mpf("1.84"):
        k += 1
    print("증명의 단계 (i) (3/2+1/(2k))^{3/2} e^{1/(24k)} < 1.84 가 처음 성립하는 k =", k)
    k = 2
    while not all(n_k(k, nu) < mpf("2.08") for nu in range(1, k + 1)):
        k += 1
    print("n_k < 2.08 이 1<=nu<=k 전부에서 처음 성립하는 k =", k)
    for kk in (2, 10, 100, 155, 156, 345, 346, 10000):
        print(f"  k={kk}: bound(i)={mp.nstr(bound(kk), 8)}  max_nu n_k={mp.nstr(max(n_k(kk, nu) for nu in range(1, kk + 1)), 8)}")
    # (라)의 명시 조건
    print("(라)의 조건 (n+1)/(2k)/128 <= 1/100  <=>  (n+1)/(2k) <= 1.28  <=>  nu <= 0.56k - 1 (nu<=k 전부를 덮지 않음; 진술에 적힌 별도 조건)")
    # (마)에서 쓰는 두 수
    print("2.08/sqrt(2pi) =", mp.nstr(mpf("2.08") / sqrt(2 * pi), 8), "< 0.83 < 2*0.451 =", 0.902)
    # 7B 7.4의 적용 범위 (명제 analytic-transfer): k>=10000 — 보조정리 4:two-corrections (나)와 같음
    print("적용 자리(명제 7:analytic-transfer)의 범위: k>=10000 (가), k>=11100 (나), K_1>=12000 (다) — 모두 k>=10000")


@lru_cache(maxsize=None)
def A(m, ell):
    """최대 변위가 ell 이하인 길이 m 주차함수의 수(ell<0이면 0). 마지막 차 재귀(정리 2:old-2-6):
    A_{m,y-1} = sum_j C(m-1,j-1) min(j,y) A_{j-1,y-1} A_{m-j,y-1}, y=ell+1."""
    if ell < 0:
        return 0
    if m == 0:
        return 1
    y = ell + 1
    return sum(comb(m - 1, j - 1) * min(j, y) * A(j - 1, ell) * A(m - j, ell) for j in range(1, m + 1))


def p(m):
    return (m + 1) ** (m - 1) if m >= 1 else 1


def s(m, y):
    return Fraction(A(m, y - 1), p(m))


def c(m, Y):
    return Fraction(A(m, Y) - A(m, Y - 1), p(m))


def part_B():
    print("\n=== (B) 12.3 수준 방문 보존의 항별 부등식")
    # 재귀 검증: A_{m, m-1} = p_m (모든 주차함수)
    assert all(A(m, m - 1) == p(m) for m in range(1, 15)), "재귀 검증 실패"
    print("재귀 검증: A_{m,m-1} = (m+1)^{m-1} (m<=14) 통과")
    M, YMAX = 40, 12
    bad_dm0 = bad_term = 0
    for y in range(1, YMAX + 1):
        for m in range(0, M):
            if not s(m, y) <= s(m + 1, y + 1):
                bad_dm0 += 1
    for Y in range(1, YMAX + 1):
        for m in range(Y + 1, M + 1):
            if not c(m, Y) >= s(m - 1, Y) - s(m, Y):
                bad_term += 1
    print(f"(DM0) s_m(y) <= s_(m+1)(y+1): m<{M}, y<={YMAX} 위반 {bad_dm0}")
    print(f"항별 c_m(Y) >= s_(m-1)(Y) - s_m(Y): Y<={YMAX}, Y+1<=m<={M} 위반 {bad_term}")
    # 망원합
    bad_tel = 0
    for Y in range(1, YMAX + 1):
        for K in range(Y + 1, M + 1):
            if not sum(c(m, Y) for m in range(Y + 1, K + 1)) >= 1 - s(K, Y):
                bad_tel += 1
    print(f"w==1 망원합 sum c_m(Y) >= 1 - s_K(Y): 위반 {bad_tel}")
    # s_Y(Y) = 1
    assert all(s(Y, Y) == 1 for Y in range(1, YMAX + 1))
    print("s_Y(Y) = 1 (Y<=12) 확인")
    # 단조가 아닌 음이 아닌 무게
    random.seed(1116)
    bad_w = 0
    for _ in range(300):
        Y = random.randint(1, YMAX)
        K = random.randint(Y + 1, M)
        w = {m: Fraction(random.randint(0, 20), 7) for m in range(Y + 1, K + 1)}
        lhs = sum(w[m] * c(m, Y) for m in w)
        rhs = sum(w[m] * (s(m - 1, Y) - s(m, Y)) for m in w)
        if not lhs >= rhs:
            bad_w += 1
    print(f"단조가 아닌 무작위 음이 아닌 무게 300벌: 가중 부등식 위반 {bad_w}")
    # 보기: 항별 부등식이 등식이 아닌 양(여유)의 최솟값
    gaps = [(c(m, Y) - (s(m - 1, Y) - s(m, Y)), m, Y) for Y in range(1, 6) for m in range(Y + 1, 20)]
    g, m, Y = min(gaps)
    print(f"항별 여유 c_m(Y)-(s_(m-1)(Y)-s_m(Y)) 의 최솟값(Y<=5, m<20): {float(g):.6g} at (m,Y)=({m},{Y}) ; 이 여유는 (DM0)의 여유 s_m(Y+1)-s_(m-1)(Y)")


if __name__ == "__main__":
    part_A()
    part_B()
