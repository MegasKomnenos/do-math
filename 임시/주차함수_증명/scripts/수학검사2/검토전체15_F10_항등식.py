# -*- coding: utf-8 -*-
"""검토전체15 F10: 10장의 정확 항등식을 작은 k에서 정확 유리수로 검산한다.

검산 대상
  (1) 정리 7:old-6-21 (7.25)  A_{n,k-1}(star)(n) = d_{n,k} - KD'_n
  (2) 보조정리 10:old-8-2 장부 항등식, Stem_n 의 합 꼴
  (3) 보조정리 10:old-8-3 (a)(d)(e)
  (4) 명제 10:old-8-6 꼬리합 꼴
  (5) 명제 10:old-8-8 (가)(나) 머묾 꼴
  (6) 정리 2:old-2-13 사슬 공식 (무거운 사슬 구현의 검증)
  (7) 정리 10:old-8-18 나머지의 수준별 공식 (두 식)
  (8) 정리 10:old-8-28 수준 질량의 사슬 표현 (첫 식)
  (9) 보조정리 10:old-8-31 둘째 길 E[Pi_L L] = sum_q G^y(q) s_q(y)
"""
from fractions import Fraction as Fr
from math import comb, factorial
from functools import lru_cache
import sys

sys.setrecursionlimit(10000)

@lru_cache(None)
def p(m):
    return 1 if m == 0 else (m + 1) ** (m - 1)

@lru_cache(None)
def A(m, l):
    if l < 0:
        return 0
    if m == 0:
        return 1
    if l >= m - 1:
        return p(m)
    return sum(comb(m - 1, j - 1) * min(j, l + 1) * A(j - 1, l) * A(m - j, l) for j in range(1, m + 1))

def s(m, y):      # 생존 확률 s_m(y) = A_{m,y-1}/p_m
    return Fr(A(m, y - 1), p(m))

def c(m, Y):      # 수준 질량 c_m(Y)
    return Fr(A(m, Y) - A(m, Y - 1), p(m))

def d(m, k):
    return A(m, k) - 2 * A(m, k - 1) + A(m, k - 2)

def BorR(j):      # Bor(j) 에서 e^{-j} 를 뺀 유리수 부분 j^{j-1}/j!
    return Fr(j ** (j - 1), factorial(j))

def eg(m):        # e^{g(m)} = (1+1/m)^{m-1}
    return (Fr(m + 1, m)) ** (m - 1)

fails = 0
def check(name, ok):
    global fails
    if not ok:
        fails += 1
    print(("OK  " if ok else "FAIL") + "  " + name)

# 기본 검증
check("A(m,0)=m!", all(A(m, 0) == factorial(m) for m in range(1, 9)))

# ---------- 7.5 / 10.1 의 양 ----------
def ledger_checks(k, n):
    nu = n - 2 * k
    N = n - k
    An = A(n, k - 1)
    def cl_plus(m):  return c(m, k) / s(m, k)
    def cl_minus(m): return c(m, k - 1) / s(m, k)
    def mu(m):       return Fr(d(m, k), A(m, k - 1))
    def P(j):        return Fr(min(j, k) * comb(n - 1, j - 1) * A(j - 1, k - 1) * A(n - j, k - 1), An)
    def chi(j):
        lin = Fr(0)
        if j == k:
            lin -= (1 - cl_minus(n - j))
        if j > k:
            lin += cl_plus(j - 1) + cl_minus(j - 1) + cl_plus(n - j) + cl_minus(n - j)
        lin /= k
        h = Fr(1 if j > k else 0, k)
        quad = (1 + h) * cl_plus(j - 1) * cl_plus(n - j) + (1 - h) * cl_minus(j - 1) * cl_minus(n - j)
        return lin + quad
    src = sum(P(j) * chi(j) for j in range(1, n + 1))
    inh = sum(P(j) * (mu(j - 1) * (1 if k <= j - 1 <= 2 * k else 0) + mu(n - j) * (1 if k <= n - j <= 2 * k else 0)) for j in range(1, n + 1))
    star = src + inh
    KDp = sum((k + n - m) * comb(n - 1, m) * p(n - 1 - m) * d(m, k) for m in range(2 * k + 1, n))
    check(f"(1) 7.25 identity k={k} n={n}", An * star == d(n, k) - KDp)

    def w(m): return Fr(comb(n - 1, m) * p(m) * A(n - 1 - m, k - 1), An)
    u_n = w(N) * s(N, k + 1)
    Quad = sum(P(j) * ((1 + Fr(1, k)) * cl_plus(j - 1) * cl_plus(n - j) + (1 - Fr(1, k)) * cl_minus(j - 1) * cl_minus(n - j)) for j in range(k + 1, n + 1))
    Stem = Fr(1, k) * sum(P(j) * ((cl_plus(j - 1) + cl_minus(j - 1)) * (1 if j - 1 > 2 * k else 0) + (cl_plus(n - j) + cl_minus(n - j)) * (1 if n - j > 2 * k else 0)) for j in range(k + 1, n + 1))
    def c2(m): return c(m, k) + c(m, k - 1)
    def f(m):
        if m <= N:
            return 2 * ((k + 1) * c(m, k) - (k - 1) * c(m, k - 1))
        return (k + n - m + 1) * c(m, k) - (k + n - m - 1) * c(m, k - 1)
    def T(m): return sum(f(i) for i in range(m, 2 * k + 1))
    check(f"(2) ledger identity k={k} n={n}", star == sum(w(m) * f(m) for m in range(k, 2 * k + 1)) - u_n + Quad + Stem)
    check(f"(2) Stem sum form k={k} n={n}", Stem == sum(w(m) * c2(m) for m in range(2 * k + 1, n)))
    # (3a)
    def r(Nn): return Fr(A(Nn + 1, k - 1), (Nn + 1) * A(Nn, k - 1))
    check(f"(3a) k={k} n={n}", all(w(m + 1) / w(m) == eg(m + 1) / r(n - 2 - m) for m in range(k, n - 1)))
    # (3d)  w_m/w_N = Bor(m+1)Bor(n-m)/(Bor(N+1)Bor(k))  (지수는 상쇄)
    check(f"(3d) k={k} n={n}", all(w(m) / w(N) == BorR(m + 1) * BorR(n - m) / (BorR(N + 1) * BorR(k)) for m in range(N, n)))
    # (3e)
    def gL(m):
        out = Fr(1)
        for i in range(k, m):
            out *= eg(i + 1) / eg(n - 1 - i)
        return out
    check(f"(3e) w_m/w_k k={k} n={n}", all(w(m) / w(k) == gL(m) * s(n - 1 - m, k) / s(N - 1, k) for m in range(k, N + 1)))
    check(f"(3e) u_n/w_k k={k} n={n}", u_n / w(k) == eg(N) / eg(k) * s(N, k + 1) / s(N - 1, k))
    # (4) Abel
    check(f"(4) Abel k={k} n={n}", sum(w(m) * f(m) for m in range(k, 2 * k + 1)) == w(k) * T(k) + sum((w(m) - w(m - 1)) * T(m) for m in range(k + 1, 2 * k + 1)))
    # (5) 머묾 꼴 (nu <= k-1)
    if nu <= k - 1:
        def vs(m, l): return s(m + 1, l + 1) - s(m, l)          # 머묾 질량
        def DD(m): return (k + 1) * s(m + 1, k + 1) - 2 * k * s(m, k) + (k - 1) * s(m - 1, k - 1)
        check(f"(5) DD=varsigma form k={k} n={n}", all(DD(m) == (k + 1) * vs(m, k) - (k - 1) * vs(m - 1, k - 1) for m in range(k + 1, 2 * k + 1)))
        def om(m):
            return Fr(2) if m <= N + 1 else 2 - Fr(m - N, k)
        Stays = 2 * vs(N + 1, k) + sum((2 - Fr(m - N, k)) * (vs(m, k) + vs(m - 1, k - 1)) for m in range(N + 2, 2 * k + 1))
        BdS = -(k + nu) * (vs(2 * k, k) + c(2 * k, k - 1)) - s(2 * k, k - 1)
        ok = True
        for m0 in range(k, N + 1):
            rhs = (2 * k * c(m0, k) + 2 * s(m0, k + 1) + 2 * s(m0, k) + (2 * k + 2) * vs(m0, k)
                   - 2 * s(N + 1, k + 1) - s(N + 2, k + 1) + BdS
                   + sum(om(m) * DD(m) for m in range(m0 + 1, 2 * k + 1)) - Stays)
            ok = ok and (T(m0) == rhs)
        check(f"(5가) k={k} n={n}", ok)
        ok = True
        for m0 in range(N + 1, 2 * k + 1):
            mflat = 3 * k + nu - m0
            rhs = (mflat * c(m0, k) + s(m0, k) + (s(m0, k + 1) - s(m0 + 1, k + 1)) + (mflat + 1) * vs(m0, k) + BdS
                   + sum(om(m) * DD(m) for m in range(m0 + 1, 2 * k + 1))
                   - sum((2 - Fr(m - N, k)) * (vs(m, k) + vs(m - 1, k - 1)) for m in range(m0 + 1, 2 * k + 1)))
            ok = ok and (T(m0) == rhs)
        check(f"(5나) k={k} n={n}", ok)

for k in (3, 4, 5, 6):
    for n in range(2 * k + 1, 3 * k + 1):
        ledger_checks(k, n)

# ---------- 무거운 사슬 (2.11절) ----------
def trans(y, q, qp):   # Pr^y(q -> q')
    return BorR(q - qp) * BorR(y + qp) / BorR(y + q)

def pi_kernel(nn, t):  # pi_n(t) = Bor(t)Bor(n+1-t)/Bor(n+1) (t > n/2)
    return BorR(t) * BorR(nn + 1 - t) / BorR(nn + 1)

def paths(y, d):
    """법칙 Pr^y 아래 시작 초과 d 의 모든 경로 (q_0=d>...>q_L>=1) 와 (경로 전이 확률의 곱, 멈춤 확률)."""
    out = []
    def rec(q, prob, path):
        stop = 1 - sum(trans(y, q, qp) for qp in range(1, q))
        out.append((tuple(path), prob, stop))
        for qp in range(1, q):
            rec(qp, prob * trans(y, q, qp), path + [qp])
    rec(d, Fr(1), [])
    return out

def Pi(path, y):
    out = Fr(1)
    for q in path:
        out *= Fr(y, y + q)
    return out

def s_chain(y, d):
    return sum(prob * stop * Pi(path, y) for path, prob, stop in paths(y, d))

# (6) 사슬 공식
check("(6) chain formula s_{y+d-1}(y)=E^y[Pi_L]", all(s_chain(y, dd) == s(y + dd - 1, y) for y in (2, 3, 4, 5) for dd in range(1, y + 3)))

# (7) 정리 10:old-8-18
def h(y, y0, q):   # 지수는 비 안에서 상쇄되므로 유리수 부분만
    return BorR(y + q) / BorR(y0 + q)

def thm18(y0, dd):
    base = paths(y0, dd)  # 얼린 법칙
    def s_fr(y): return sum(prob * stop * Pi(path, y) for path, prob, stop in base)
    def G(y, q):
        tot = Fr(0)
        for path, prob, stop in base:
            if len(path) and path[-1] == q:
                tot += prob * Pi(path, y)
        return tot
    ok = True
    for y in (y0 - 1, y0 + 1):
        def tr(q): return h(y, y0, q) / h(y, y0, dd) - 1
        lhs = s(y + dd - 1, y) - s_fr(y)
        rhs = -sum(Fr(q, y) * G(y, q) * tr(q) for q in range(1, dd))
        ok = ok and lhs == rhs
    # 둘째 식: Res_d = DD_m - Delta^2[y s^fr]
    k = y0
    m = k + dd - 1
    DDm = (k + 1) * s(m + 1, k + 1) - 2 * k * s(m, k) + (k - 1) * s(m - 1, k - 1)
    fr2 = (k + 1) * s_fr(k + 1) - 2 * k * s_fr(k) + (k - 1) * s_fr(k - 1)
    Res = DDm - fr2
    # inc^+ = g(y0+d)-g(y0+q): e^{-inc+} = e^{g(y0+q)}/e^{g(y0+d)}; e^{inc-} = e^{g(y0-1+d)}/e^{g(y0-1+q)}
    rhs2 = sum(q * (G(y0 + 1, q) * (1 - eg(y0 + q) / eg(y0 + dd)) - G(y0 - 1, q) * (eg(y0 - 1 + dd) / eg(y0 - 1 + q) - 1)) for q in range(1, dd))
    ok = ok and Res == rhs2
    check(f"(7) thm 18 y0={y0} d={dd}", ok)

for y0 in (3, 4, 5):
    for dd in range(2, y0 + 2):
        thm18(y0, dd)

# (8) 정리 10:old-8-28 첫 식
def thm28(k, q0):
    y = k + 1
    tot = Fr(0)
    for path, prob, stop in paths(y, q0):
        L = len(path)
        qL = path[-1] if L else q0
        pch = pi_kernel(y + qL - 1, y)          # 끝 꼭짓점 아래 크기 정확히 y 인 자식이 있을 확률
        # 멈춤(stop) 안에서 1_ch=1 인 몫이 pch, 나머지가 stop - pch
        tot += prob * Pi(path, y) * ((stop - pch) * (1 - (1 - Fr(1, y)) ** L) + pch * (1 - (1 - Fr(1, y)) ** (L + 1)))
    check(f"(8) thm 28 k={k} q0={q0}", tot == c(k + q0, k))

for k in (3, 4, 5):
    for q0 in range(1, k + 2):
        thm28(k, q0)

# (9) 보조정리 10:old-8-31 둘째 길
def lem31(y, q0):
    base = paths(y, q0)
    lhs = sum(prob * stop * Pi(path, y) * len(path) for path, prob, stop in base)
    def Gy(q):   # E^y[Pi_{j(q)}; q 를 지남]  (지나는 사건: 경로 접두사가 q 에 닿음)
        tot = Fr(0)
        for path, prob, stop in base:
            if len(path) and path[-1] == q:
                tot += prob * Pi(path, y)
        return tot
    rhs = sum(Gy(q) * s(y + q - 1, y) for q in range(1, q0))
    check(f"(9) lem 31 second route y={y} q0={q0}", lhs == rhs)

for y in (3, 4, 5):
    for q0 in range(2, y + 3):
        lem31(y, q0)

print("FAILS:", fails)
