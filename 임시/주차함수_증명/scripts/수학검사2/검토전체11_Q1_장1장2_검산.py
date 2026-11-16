# -*- coding: utf-8 -*-
"""검토전체11 Q1: 장1·장2의 수치·항등식 검산.

1) 1.3절 표(n<=10)와 가장 작은 증인 ell*_n: 마지막 차 재귀(정리 2-6)와 n<=7의 완전 열거로 교차 확인.
2) 2.2절: sigma=(1,2,3,5,4,6,7)의 섬유 행, n<=6의 모든 섬유 행이 단봉인지(정리 2-5 마지막 문장).
3) 2.7절: 동률-막힘 항등식 d=2E-B(정리 2-28), 2E2-B<=d(따름 2-29), B<=J_n(k-1)와 n<=2k-1 등식, n=2k의 Xi(보조 2-30) -- n<=8 완전 열거.
4) 2.10절: 다섯 몫 분해(정리 2-40)를 k=2..5, 2k+1<=n<=3k-1에서 직접 계산과 대조; b_{k,k-1}=k^{k-2}(보조 b-top).
5) 명제 2-20의 유한 n 상계값(n=17,100,1000,10^4): 닫힌 꼴을 mpmath 50자리로 재계산.
6) 2-37(라)·moving-tail(아)의 상수.
"""
from fractions import Fraction
from itertools import product, permutations
from math import comb, factorial, log, exp, pi, sqrt, cosh
import mpmath as mp

mp.mp.dps = 50

# ---------- 1) 재귀와 완전 열거 ----------
def A_rec(N):
    A = {}
    for l in range(0, N + 1):
        A[(0, l)] = 1
        for n in range(1, N + 1):
            A[(n, l)] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[(j, l)] * A[(n - 1 - j, l)] for j in range(n))
    return A

def park(alpha):
    n = len(alpha); occ = [False] * (n + 2); pos = []
    for a in alpha:
        p = a
        while p <= n and occ[p]:
            p += 1
        if p > n:
            return None
        occ[p] = True; pos.append(p)
    return pos

def brute(n):
    rows = {}
    for alpha in product(range(1, n + 1), repeat=n):
        pos = park(alpha)
        if pos is None:
            continue
        M = max(p - a for p, a in zip(pos, alpha))
        rows[M] = rows.get(M, 0) + 1
    return [rows.get(l, 0) for l in range(n)]

table = {1: [1], 2: [2, 1], 3: [6, 7, 3], 4: [24, 51, 34, 16], 5: [120, 421, 377, 253, 125],
         6: [720, 3963, 4594, 3688, 2546, 1296], 7: [5040, 42253, 62145, 57398, 46142, 32359, 16807],
         8: [40320, 505515, 929856, 979430, 865970, 702292, 497442, 262144],
         9: [362880, 6724381, 15298809, 18289811, 17520519, 15455851, 12587507, 8977273, 4782969],
         10: [3628800, 98618763, 275075236, 371706836, 385131546, 359973796, 318092120, 259627152, 186093442, 100000000]}
A = A_rec(10)
print("== 1) 1.3절 표 ==")
for n in range(1, 11):
    row = [A[(n, l)] - (A[(n, l - 1)] if l else 0) for l in range(n)]
    ok = row == table[n] and sum(row) == (n + 1) ** (n - 1)
    peak = min(i for i in range(n) if row[i] == max(row))
    print(n, "recursion==table:", ok, "ell*_n(최소 증인)=", peak, "sum=", sum(row))
for n in range(1, 8):
    print("  brute n=%d ==table:" % n, brute(n) == table[n])

# ---------- 2) 섬유 ----------
def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n + 1):
        z = max([j for j in range(1, i) if sigma[j - 1] > sigma[i - 1]] + [0])
        h.append(i - z)
    return h

def fiber_row(h):
    n = len(h); Acum = [1]
    for l in range(n):
        p = 1
        for hi in h:
            p *= min(hi, l + 1)
        Acum.append(p)
    return [Acum[l + 1] - Acum[l] for l in range(n)]

def unimodal(z):
    i = 0
    while i + 1 < len(z) and z[i] <= z[i + 1]:
        i += 1
    while i + 1 < len(z) and z[i] >= z[i + 1]:
        i += 1
    return i == len(z) - 1

print("== 2) 2.2절 ==")
h = caps((1, 2, 3, 5, 4, 6, 7)); print("h=", h, "row=", fiber_row(h), "unimodal:", unimodal(fiber_row(h)))
for n in range(1, 8):
    bad = [s for s in permutations(range(1, n + 1)) if not unimodal(fiber_row(caps(s)))]
    print("  n=%d 비단봉 섬유 수:" % n, len(bad), (bad[:3] if bad else ""))
# n=7 sigma' check for n=8,9
for n in (8, 9):
    s = tuple([n - 6, n - 5, n - 4, n - 2, n - 3, n - 1, n] + list(range(n - 7, 0, -1)))
    print("  sigma' n=%d:" % n, s, "row=", fiber_row(caps(s)))
# 숲: 모양 (1,2,3,4,1,6,7)의 7!/1008
print("  7!/1008 =", factorial(7) // 1008)

# ---------- 3) 2.7절 항등식 ----------
def pf_data(n):
    """모든 주차함수에 대해 (M, M#, blocked, Z-heavy info) 등 계산."""
    out = []
    for alpha in product(range(1, n + 1), repeat=n):
        pos = park(alpha)
        if pos is None:
            continue
        sigma = [0] * n
        for car, p in enumerate(pos, 1):
            sigma[p - 1] = car
        h = caps(sigma)
        d = [p - a for p, a in zip(pos, alpha)]
        M = max(d); Msharp = d.count(M)
        # blocked: every car with d_i=M stands at place i with h_i = M+1
        blocked = all(h[pos[i] - 1] == M + 1 for i in range(n) if d[i] == M)
        out.append((M, Msharp, blocked, tuple(h)))
    return out

def J_poly(n, k, z):
    tot = 0
    for s in permutations(range(1, n + 1)):
        h = caps(s)
        H = sum(1 for x in h if x == k); Z = sum(1 for x in h if x > k)
        pr = 1
        for x in h:
            if x < k:
                pr *= x
        tot += H * k ** (H - 1) * z ** Z * pr if H > 0 else 0
    return tot

print("== 3) 2.7절 ==")
for n in range(1, 8):
    data = pf_data(n)
    b = [sum(1 for M, _, _, _ in data if M == l) for l in range(n + 1)]
    allok = True
    for k in range(1, n + 1):
        d = b[k] - b[k - 1]
        E = sum(1 for M, s, _, _ in data if M == k and s % 2 == 0)
        E2 = sum(1 for M, s, _, _ in data if M == k and s == 2)
        B = sum(1 for M, s, bl, _ in data if M == k - 1 and bl)
        J = J_poly(n, k, k - 1)
        Xi = comb(2 * k - 1, k - 1) * ((k) ** (k - 2)) ** 2 if n == 2 * k else 0  # p_{k-1}^2 = (k^{k-2})^2
        ok = (d == 2 * E - B) and (2 * E2 - B <= d) and (B <= J) and ((n > 2 * k - 1) or B == J) and ((n not in (2 * k - 1, 2 * k)) or B == J - Xi)
        allok &= ok
        if not ok:
            print("  FAIL n=%d k=%d d=%d 2E-B=%d 2E2-B=%d B=%d J=%d Xi=%d" % (n, k, d, 2 * E - B, 2 * E2 - B, B, J, Xi))
    print("  n=%d: 2-28, 2-29, 2-30 모두 성립:" % n, allok, " B_{n,0}=", sum(1 for M, s, bl, _ in data if M == 0 and bl))

# ---------- 4) 다섯 몫 분해 ----------
def five_part(k, n, A):
    p = lambda m: (m + 1) ** (m - 1) if m >= 1 else 1
    b = lambda m, l: (A[(m, l)] - (A[(m, l - 1)] if l >= 1 else 0)) if m >= 0 else 0
    Theta = comb(n, k) * k ** (k - 2) * A[(n - k, k - 1)]
    def bT(t, l):  # 허용 나무 수의 차
        N = lambda t, l: min(t, l + 1) * A[(t - 1, l)]
        return N(t, l) - (N(t, l - 1) if l >= 1 else 0)
    FL = sum(comb(n, t) * (bT(t, k) - bT(t, k - 1)) * A[(n - t, k - 1)] for t in range(k + 1, 2 * k + 2))
    BV = sum(comb(n, m + 1) * p(n - 1 - m) * (b(m, k) + b(m, k - 1)) for m in range(2 * k + 1, n))
    KD = sum(comb(n, m + 1) * p(n - 1 - m) * k * (b(m, k) - b(m, k - 1)) for m in range(2 * k + 1, n))
    # PAIR by integer form (명제 2-41)
    PAIR2 = 0
    for t1 in range(1, n + 1):
        for t2 in range(1, n + 1 - t1):
            mult = factorial(n) // (factorial(t1) * factorial(t2) * factorial(n - t1 - t2))
            PAIR2 += mult * (bT(t1, k) * bT(t2, k) + bT(t1, k - 1) * bT(t2, k - 1)) * p(n - t1 - t2)
    assert PAIR2 % 2 == 0
    PAIR = PAIR2 // 2
    d = b(n, k) - b(n, k - 1)
    return d, -Theta + FL + BV + KD + PAIR, (Theta, FL, BV, KD, PAIR)

print("== 4) 2.10절 ==")
A = A_rec(16)
for k in range(2, 6):
    for n in range(2 * k + 1, 3 * k):
        d, s, parts = five_part(k, n, A)
        print("  k=%d n=%d d=%d 분해합=%d 일치:%s  (Theta,FL,BV,KD,PAIR)=%s" % (k, n, d, s, d == s, parts))
    print("  b_{k,k-1}=%d, k^{k-2}=%d" % (A[(k, k - 1)] - A[(k, k - 2)], k ** (k - 2)))

# ---------- 5) 명제 2-20 상계값 ----------
def v(k, Z, H):
    return (1 + mp.mpf(1) / k) ** Z + (1 - mp.mpf(1) / k) ** (Z + H) - 2

def bound_2_20(n):
    lg = lambda m: mp.loggamma(m + 1)  # log m!
    best = None
    for bb in range(3, 60):
        # 조건: 3<=i<=bb, n/2<k<=n 에서 v_k(i-1,1)<0
        ok = all(v(k, i - 1, 1) < 0 for i in range(3, bb + 1) for k in range(n // 2 + 1, n + 1))
        if not ok:
            break
        S1 = mp.mpf(0); S2 = mp.mpf(0)
        for c in range(n // 2 + 1, n + 1):
            kap = n - c - bb + 1
            if kap < 0:
                continue
            base = lg(n) - lg(c) + (c - 1) * mp.log(c) - (n - 1) * mp.log(n + 1) - lg(kap)
            t1 = mp.e ** (base + mp.log(bb) + (kap - 1) * mp.log(n - c + 1)) if kap >= 1 else mp.e ** base
            t2 = mp.e ** (base + mp.log(2) + (kap - 1) * mp.log(n - c - bb + 3)) if kap >= 1 else mp.e ** base
            S1 += t1; S2 += t2
        val = 1 - S1 + S2
        if best is None or val < best[0]:
            best = (val, bb, S1, S2)
    return best

print("== 5) 명제 2-20 ==")
for n in (17, 100, 1000, 10000):
    val, bb, S1, S2 = bound_2_20(n)
    print("  n=%d: 최적 b=%d, Pr(S_b>n/2)=%s, 둘째 항=%s, 상계=%s" % (n, bb, mp.nstr(S1, 8), mp.nstr(S2, 8), mp.nstr(val, 8)))

# ---------- 6) 상수 ----------
print("== 6) 상수 ==")
print("  2/sqrt(2pi) =", 2 / sqrt(2 * pi), " e*(20/19)^4 =", exp(1) * (20 / 19) ** 4, " cosh(1/4)/4 =", cosh(0.25) / 4)
print("  zeta(1/2), zeta(-1/2), zeta(3/2) =", mp.nstr(mp.zeta(0.5), 10), mp.nstr(mp.zeta(-0.5), 10), mp.nstr(mp.zeta(1.5), 10))
print("  v_k(2,1)<0 iff k>2+sqrt3=", 2 + sqrt(3), ":", [(k, float(v(k, 2, 1))) for k in (3, 4)])
