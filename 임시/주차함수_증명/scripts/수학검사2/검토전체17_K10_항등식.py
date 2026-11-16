# -*- coding: utf-8 -*-
"""K10 검산: 10장 10.1~10.2절의 항등식과 10.5절 사슬 표현을 작은 k에서 정확 유리수로 확인한다.
확인 대상
  (1) 보조정리 old-8-2 장부 항등식  (*)(n) = sum w_m f_m - u_n + Quad_n + Stem_n
  (2) 정리 7:old-6-21 항등식 A_{n,k-1}(*)(n) = d_{n,k} - KD'_n
  (3) 명제 old-8-6 꼬리합 꼴 (Abel 합)
  (4) 명제 old-8-8 머묾 꼴 (가)(나)
  (5) 보조정리 old-8-3 (a)(d)(e) 비 항등식, (c) 단조성
  (6) 명제 old-8-15 창의 생존 상계
  (7) 정리 old-8-28 수준 질량의 사슬 표현 (사슬 법칙 2:old-2-45로 DP)
  (8) 정리 old-8-18 나머지 공식 (얼린 생존 / Res_d) 수치 확인
"""
from fractions import Fraction as Fr
from math import comb, factorial, exp
import sys

def p(m):
    return 1 if m == 0 else (m + 1) ** (m - 1)

MAXN = 40
A = {}
def Acount(n, l):
    # 최대 변위가 l 이하인 길이 n 주차함수의 수 (정리 2:old-2-6 마지막 차 재귀)
    if l < 0:
        return 0
    if n == 0:
        return 1
    key = (n, l)
    if key in A:
        return A[key]
    s = 0
    for j in range(1, n + 1):
        s += comb(n - 1, j - 1) * min(j, l + 1) * Acount(j - 1, l) * Acount(n - j, l)
    A[key] = s
    return s

def b(n, l):
    return Acount(n, l) - Acount(n, l - 1)

def s(m, y):  # 생존 확률 s_m(y) = A_{m,y-1}/p_m
    return Fr(Acount(m, y - 1), p(m))

def c(m, Y):  # 수준 질량
    return Fr(b(m, Y), p(m))

def d(n, k):
    return b(n, k) - b(n, k - 1)

def P(n, k, j):  # 뿌리 자리 법칙
    return Fr(min(j, k) * comb(n - 1, j - 1) * Acount(j - 1, k - 1) * Acount(n - j, k - 1), Acount(n, k - 1))

def clp(m, k):
    return Fr(b(m, k), Acount(m, k - 1))

def clm(m, k):
    return Fr(b(m, k - 1), Acount(m, k - 1))

def mu(m, k):
    return Fr(d(m, k), Acount(m, k - 1))

def chi(n, k, j):
    lin = Fr(0)
    if j == k:
        lin -= (1 - clm(n - k, k))
    if j > k:
        lin += clp(j - 1, k) + clm(j - 1, k) + clp(n - j, k) + clm(n - j, k)
    lin = lin / k
    ind = 1 if j > k else 0
    quad = (1 + Fr(ind, k)) * clp(j - 1, k) * clp(n - j, k) + (1 - Fr(ind, k)) * clm(j - 1, k) * clm(n - j, k)
    return lin + quad

def src(n, k):
    return sum(P(n, k, j) * chi(n, k, j) for j in range(1, n + 1))

def inh(n, k):
    t = Fr(0)
    for j in range(1, n + 1):
        if k <= j - 1 <= 2 * k:
            t += P(n, k, j) * mu(j - 1, k)
        if k <= n - j <= 2 * k:
            t += P(n, k, j) * mu(n - j, k)
    return t

def w(n, k, m):
    return Fr(comb(n - 1, m) * p(m) * Acount(n - 1 - m, k - 1), Acount(n, k - 1))

def f(n, k, m):
    N = n - k
    if m <= N:
        return 2 * ((k + 1) * c(m, k) - (k - 1) * c(m, k - 1))
    return (k + n - m + 1) * c(m, k) - (k + n - m - 1) * c(m, k - 1)

def T(n, k, m):
    return sum(f(n, k, i) for i in range(m, 2 * k + 1))

def Quad(n, k):
    return sum(P(n, k, j) * ((1 + Fr(1, k)) * clp(j - 1, k) * clp(n - j, k) + (1 - Fr(1, k)) * clm(j - 1, k) * clm(n - j, k)) for j in range(k + 1, n + 1))

def Stem(n, k):
    t = Fr(0)
    for j in range(k + 1, n + 1):
        if j - 1 > 2 * k:
            t += P(n, k, j) * (clp(j - 1, k) + clm(j - 1, k)) / k
        if n - j > 2 * k:
            t += P(n, k, j) * (clp(n - j, k) + clm(n - j, k)) / k
    return t

def vs(m, l):  # 머묾 질량
    return s(m + 1, l + 1) - s(m, l)

def DD(n, k, m):
    return (k + 1) * s(m + 1, k + 1) - 2 * k * s(m, k) + (k - 1) * s(m - 1, k - 1)

def omega(n, k, m):
    N = n - k
    return Fr(2) if m <= N + 1 else 2 - Fr(m - N, k)

def Stays(n, k):
    N = n - k
    t = 2 * vs(N + 1, k)
    for m in range(N + 2, 2 * k + 1):
        t += (2 - Fr(m - N, k)) * (vs(m, k) + vs(m - 1, k - 1))
    return t

def BdS(n, k):
    nu = n - 2 * k
    return -(k + nu) * (vs(2 * k, k) + c(2 * k, k - 1)) - s(2 * k, k - 1)

fails = []
def check(name, ok):
    if not ok:
        fails.append(name)

for k in range(3, 8):
    for n in range(2 * k + 1, 3 * k + 1):
        nu = n - 2 * k
        N = n - k
        star = src(n, k) + inh(n, k)
        # (1)
        rhs = sum(w(n, k, m) * f(n, k, m) for m in range(k, 2 * k + 1)) - w(n, k, N) * s(N, k + 1) + Quad(n, k) + Stem(n, k)
        check(f"old-8-2 k={k} n={n}", star == rhs)
        # (2)
        KD = sum((k + n - m) * comb(n - 1, m) * p(n - 1 - m) * d(m, k) for m in range(2 * k + 1, n))
        check(f"old-6-21 k={k} n={n}", Acount(n, k - 1) * star == d(n, k) - KD)
        # (3)
        abel = w(n, k, k) * T(n, k, k) + sum((w(n, k, m) - w(n, k, m - 1)) * T(n, k, m) for m in range(k + 1, 2 * k + 1))
        check(f"old-8-6 k={k} n={n}", abel == sum(w(n, k, m) * f(n, k, m) for m in range(k, 2 * k + 1)))
        # (5c) 단조
        check(f"old-8-3c k={k} n={n}", all(w(n, k, m + 1) >= w(n, k, m) for m in range(k, 2 * k)))
        # (5d)
        for m in range(N, n):
            lhs = w(n, k, m) / w(n, k, N)
            # Bor 비는 유리수로: Bor(j) = e^{-j} j^{j-1}/j!  -> e 인자는 분자 분모 (m+1)+(n-m) = (N+1)+k = n+1 에서 지워진다
            def borq(j):
                return Fr(j ** (j - 1), factorial(j))
            rhs = borq(m + 1) * borq(n - m) / (borq(N + 1) * borq(k))
            check(f"old-8-3d k={k} n={n} m={m}", lhs == rhs)
        # (4) 머묾 꼴 (ν ≤ k-1)
        if nu <= k - 1:
            for m0 in range(k, 2 * k + 1):
                if m0 <= N:
                    rhs = (2 * k * c(m0, k) + 2 * s(m0, k + 1) + 2 * s(m0, k) + (2 * k + 2) * vs(m0, k)
                           - 2 * s(N + 1, k + 1) - s(N + 2, k + 1) + BdS(n, k)
                           + sum(omega(n, k, m) * DD(n, k, m) for m in range(m0 + 1, 2 * k + 1)) - Stays(n, k))
                    check(f"old-8-8ga k={k} n={n} m0={m0}", T(n, k, m0) == rhs)
                else:
                    mf = 3 * k + nu - m0
                    rhs = (mf * c(m0, k) + s(m0, k) + (s(m0, k + 1) - s(m0 + 1, k + 1)) + (mf + 1) * vs(m0, k) + BdS(n, k)
                           + sum(omega(n, k, m) * DD(n, k, m) for m in range(m0 + 1, 2 * k + 1))
                           - sum((2 - Fr(m - N, k)) * (vs(m, k) + vs(m - 1, k - 1)) for m in range(m0 + 1, 2 * k + 1)))
                    check(f"old-8-8na k={k} n={n} m0={m0}", T(n, k, m0) == rhs)
        # 10.3 old-8-10 증명의 Stem 표현: A_{n,k-1} Stem_n = sum_{m>2k} C(n-1,m) p_{n-1-m} b2_m
        check(f"Stem-ledger k={k} n={n}", Acount(n, k - 1) * Stem(n, k) == sum(comb(n - 1, m) * p(n - 1 - m) * (b(m, k) + b(m, k - 1)) for m in range(2 * k + 1, n)))
        # Theta_n 식: Theta = (n/k) A_{n,k-1} u_n A_{N,k-1}/A_{N,k}
        Theta = comb(n, k) * k ** (k - 2) * Acount(n - k, k - 1)
        u = w(n, k, N) * s(N, k + 1)
        check(f"Theta k={k} n={n}", Fr(Theta) == Fr(n, k) * Acount(n, k - 1) * u * Fr(Acount(N, k - 1), Acount(N, k)))

# (6) 명제 old-8-15: Pr_m(M<=y-1) <= 1 - sum_{r=0}^{q-1} Bor(r+1)(q-r)/(m-r)  (부동소수점)
def Bor(j):
    return exp(-j) * j ** (j - 1) / factorial(j)
for y in range(2, 10):
    for m in range(y, 2 * y + 2):
        q = m - y
        bound = 1 - sum(Bor(r + 1) * (q - r) / (m - r) for r in range(0, q))
        check(f"old-8-15 y={y} m={m}", float(s(m, y)) <= bound + 1e-12)

# (7) 정리 old-8-28 사슬 표현: DP over excess with Pr^y(q->q') = Bor(q-q')Bor(y+q')/Bor(y+q)
#     c_{k+q0}(k) = E^y[Pi_L(y)(1-(1-1/y)^{L+1ch})], y=k+1, 1<=q0<=k+1
def BorF(j):
    return Fr(j ** (j - 1), factorial(j))  # e^{-j} 인자는 비에서 지워진다 (전이: Bor(q-q')Bor(y+q')/Bor(y+q): e 지수 -(q-q')-(y+q')+(y+q)=0)
for k in range(2, 9):
    y = k + 1
    for q0 in range(1, k + 2):
        # 상태: (q, L) 가중치 = Pr^y(경로) * Pi_L(y)
        # 재귀: val(q, L) = 끝날 때 기여 + sum_{q'<q} Pr(q->q') * y/(y+q') * val(q', L+1)
        # 끝날 때: 쪼개짐 확률 pi0 = 1 - sum Pr(q->q'); 그 가운데 1ch=1 부분은 pi_{y+q-1}(y) = Bor(y)Bor(q)/Bor(y+q)
        from functools import lru_cache
        @lru_cache(None)
        def val(q, L):
            tot = Fr(0)
            ps = Fr(0)
            for qp in range(1, q):
                pr = BorF(q - qp) * BorF(y + qp) / BorF(y + q)
                ps += pr
                tot += pr * Fr(y, y + qp) * val(qp, L + 1)
            pi0 = 1 - ps
            pich = BorF(y) * BorF(q) / BorF(y + q)
            # 끝: 1ch=1 몫 pich, 1ch=0 몫 pi0-pich
            tot += pich * (1 - (Fr(y - 1, y)) ** (L + 1)) + (pi0 - pich) * (1 - (Fr(y - 1, y)) ** L)
            return tot
        val.cache_clear()
        lhs = c(k + q0, k)
        check(f"old-8-28 k={k} q0={q0}", lhs == val(q0, 0))
        # 사슬 공식 자체: s_{k+q0}(y) = E^y[Pi_L(y)]
        @lru_cache(None)
        def surv(q):
            tot = Fr(0); ps = Fr(0)
            for qp in range(1, q):
                pr = BorF(q - qp) * BorF(y + qp) / BorF(y + q)
                ps += pr
                tot += pr * Fr(y, y + qp) * surv(qp)
            return tot + (1 - ps)
        check(f"chain-formula y={y} q0={q0}", s(y + q0 - 1, y) == surv(q0))

# (8) 정리 old-8-18: Res_d = DD_m - Delta^2[y s^fr_d(y)] 와 수준별 공식 (유리수, 작은 k)
for k in range(3, 8):
    y0 = k
    for dd in range(2, k + 2):
        m = k + dd - 1
        # 얼린 사슬 Pr^{y0}, 생존 인자는 용량 y
        def frozen(q, L, y, path_sum=None):
            pass
        from functools import lru_cache
        @lru_cache(None)
        def sfr(q, y):
            tot = Fr(0); ps = Fr(0)
            for qp in range(1, q):
                pr = BorF(q - qp) * BorF(y0 + qp) / BorF(y0 + q)
                ps += pr
                tot += pr * Fr(y, y + qp) * sfr(qp, y)
            return tot + (1 - ps)
        @lru_cache(None)
        def G(q, y):  # E^{y0}[Pi_j(y); q_j = q], 시작 dd
            # 방문 측도: 시작에서 q까지 가는 모든 경로의 Pr^{y0} * Pi(y)
            if q == dd:
                return Fr(1)
            tot = Fr(0)
            for qq in range(q + 1, dd + 1):
                pr = BorF(qq - q) * BorF(y0 + q) / BorF(y0 + qq)
                tot += G(qq, y) * pr * Fr(y, y + q)
            return tot
        DDm = (k + 1) * s(m + 1, k + 1) - 2 * k * s(m, k) + (k - 1) * s(m - 1, k - 1)
        frz = (k + 1) * sfr(dd, k + 1) - 2 * k * sfr(dd, k) + (k - 1) * sfr(dd, k - 1)
        Res = DDm - frz
        def h(y, q):
            return BorF(y + q) / BorF(y0 + q)
        for y in (k - 1, k + 1):
            lhs = s(y + dd - 1, y) - sfr(dd, y)
            rhs = -sum(Fr(q, y) * G(q, y) * (h(y, q) / h(y, dd) - 1) for q in range(1, dd))
            check(f"old-8-18 first k={k} d={dd} y={y}", lhs == rhs)
        rhs2 = sum(q * (G(q, k + 1) * (1 - h(k + 1, q) / h(k + 1, dd)) - G(q, k - 1) * (h(k - 1, q) / h(k - 1, dd) - 1)) for q in range(1, dd))
        check(f"old-8-18 Res k={k} d={dd}", Res == rhs2)
        check(f"old-8-17 DD>=Res k={k} d={dd}", DDm >= Res)

print("검사 수:", "실패", len(fails))
for x in fails[:40]:
    print("FAIL", x)
if not fails:
    print("모든 항등식·부등식 통과 (k=3..7 전체 둘째 층 행, 사슬 표현 k=2..8)")
