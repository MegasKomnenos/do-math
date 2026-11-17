# 검토전체24 R5: 정리 6:old-8-22 (6.37) DD(k+d-2,k-1) >= Res_d >= -H_d 를 작은 k 에서 확인
# 생존 확률은 정확 유리수, H_d 는 배정밀도.  또 (6.35)/(6.36) 의 Res_d 를 사슬 열거로 직접 계산해 맞춘다(아주 작은 k).
from fractions import Fraction as Fr
from math import comb, factorial, exp, log, lgamma, expm1, ceil
import itertools

NMAX = 90
cache = {}


def build(cap, nmax):
    A = [1]
    for N in range(nmax):
        A.append(sum(comb(N, i) * min(i + 1, cap) * A[i] * A[N - i] for i in range(N + 1)))
    return A


def A(n, l):
    if l < 0:
        return 0
    if l + 1 not in cache:
        cache[l + 1] = build(l + 1, NMAX)
    return cache[l + 1][n]


def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1


def s(m, y):
    return Fr(A(m, y - 1), p(m))


def DD(m, y):
    return (y + 2) * s(m + 2, y + 2) - 2 * (y + 1) * s(m + 1, y + 1) + y * s(m, y)


def g(x):
    return (x - 1) * log(1 + 1 / x)


def lB(n):
    return (n - 1) * log(n) - n - lgamma(n + 1)


def H(k, d):
    tot = 0.0
    for q in range(1, d):
        incm = g(k - 1 + d) - g(k - 1 + q)
        incp = g(k + d) - g(k + q)
        kk = expm1(incm) + expm1(-incp)
        acrit = (k - 1) * kk / (2 * (-expm1(-incp)))
        stp = acrit * (k + 1 + q) / q
        rho = (k - 1) / (k - 1 + q)
        inner = sum(j * (1 - j / stp) * rho ** j for j in range(1, int(ceil(stp))) if j < stp)
        tot += q * kk * exp(lB(k + q) - lB(k + d)) * exp(lB(d - q)) * min(d - q, inner)
    return tot


worst = None
negs = 0
for k in range(2, 41):
    for d in range(2, k + 2):
        dd = float(DD(k + d - 2, k - 1))
        h = H(k, d)
        if dd < 0:
            negs += 1
        m = dd + h
        if worst is None or m < worst:
            worst = m
            arg = (k, d, dd, h)
print("k=2..40: min(DD + H_d) =", worst, arg, "; DD<0 인 (k,d) 수", negs)


# Res_d 의 직접 계산: 얼린 법칙 Pr^{y0} 의 사슬을 열거 (작은 y0, d)
def Borr(n):
    # e^{-n} 을 뺀 유리수; 전이 확률에서는 e 의 거듭제곱이 약분된다
    return Fr(n ** (n - 1), factorial(n))


def trans(y, q, q2):
    return Borr(q - q2) * Borr(y + q2) / Borr(y + q)


def surv_true(d, y):
    return s(y + d - 1, y)


def frozen(d, y, y0):
    # E^{y0}[ prod y/(y+q_i) ]  (멈출 때의 생존 곱)
    memo = {}

    def val(q):
        if q in memo:
            return memo[q]
        stop = 1 - sum(trans(y0, q, q2) for q2 in range(1, q))
        v = stop + sum(trans(y0, q, q2) * Fr(y, y + q2) * val(q2) for q2 in range(1, q))
        memo[q] = v
        return v
    return val(d)


bad = 0
for y0 in range(2, 9):
    for d in range(2, y0 + 2):
        assert frozen(d, y0, y0) == surv_true(d, y0)
        res = (y0 + 1) * (surv_true(d, y0 + 1) - frozen(d, y0 + 1, y0)) + (y0 - 1) * (surv_true(d, y0 - 1) - frozen(d, y0 - 1, y0))
        fr2 = (y0 + 1) * frozen(d, y0 + 1, y0) - 2 * y0 * frozen(d, y0, y0) + (y0 - 1) * frozen(d, y0 - 1, y0)
        if fr2 < 0:
            bad += 1
        if DD(y0 + d - 2, y0 - 1) != res + fr2:
            bad += 1
        if float(res) < -H(y0, d) - 1e-15:
            bad += 1
print("얼린 볼록 몫 >= 0, DD = Res + 얼린 몫, Res >= -H_d : 위반", bad)
