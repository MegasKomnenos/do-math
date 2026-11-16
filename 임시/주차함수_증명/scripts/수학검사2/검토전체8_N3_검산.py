# -*- coding: utf-8 -*-
"""검토전체8 N3: 장5A.md 수치·항등식 검산 (python -I 로 실행)."""
from fractions import Fraction as Fr
from math import comb, factorial, ceil, floor, e as E, log, sqrt, pi, exp
from itertools import permutations, product
import sys

sys.setrecursionlimit(10000)

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

# ---------- (a) 행 전체: 정리 old-2-6 재귀로 A_{n,l} (n<=NMAX) ----------
NMAX = 300
A = {}  # A[(n,l)]
for l in range(0, NMAX):
    col = [1]  # A_{0,l}=1
    for n in range(1, NMAX + 1):
        s = 0
        for j in range(0, n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * col[j] * col[n - 1 - j]
        col.append(s)
    for n in range(0, NMAX + 1):
        A[(n, l)] = col[n]

def b(n, l):
    if l < 0 or l > n - 1:
        return 0
    return A[(n, l)] - (A[(n, l - 1)] if l >= 1 else 0)

# 1.3절 표 대조 (n<=10)
table = {3: [6, 7, 3], 4: [24, 51, 34, 16], 5: [120, 421, 377, 253, 125],
         10: [3628800, 98618763, 275075236, 371706836, 385131546, 359973796, 318092120, 259627152, 186093442, 100000000]}
for n, row in table.items():
    assert [b(n, l) for l in range(n)] == row, n
print("1.3절 표(n=3,4,5,10) 일치")

# 첫째 조각 사슬 b_{n,0}<...<b_{n,k_n-1} 이 깨지는 n (n<=300)
bad = []
for n in range(1, NMAX + 1):
    kn = ceil(n / 2)
    if any(not (b(n, l) < b(n, l + 1)) for l in range(0, kn - 1)):
        bad.append(n)
print("사슬 b_{n,0}<...<b_{n,k_n-1} 깨지는 n(<=300):", bad)

# 단봉성, 증인, 명제 witness-position-bound 의 값 (50<=n<=300)
def smallest_witness(n):
    row = [b(n, l) for l in range(n)]
    # 단봉 확인
    l = 0
    while l + 1 < n and row[l] <= row[l + 1]:
        l += 1
    peak = l
    for i in range(peak, n - 1):
        assert row[i] >= row[i + 1], ("not unimodal", n)
    # 가장 작은 증인 = 최댓값이 처음 나오는 첨자
    m = max(row)
    return row.index(m)

vals = []
for n in range(50, NMAX + 1):
    ls = smallest_witness(n)
    v = n + 1 - ls - 0.59963 * (n + 1) ** (2 / 3) - 1.24847 * (n + 1) ** (1 / 3)
    vals.append(v)
print("증인 상계 잔차 (50<=n<=300): min=%.4f max=%.4f" % (min(vals), max(vals)))
# n<=15 단봉, n=1..300 단봉 확인은 위 assert 로 됨
for n in range(1, NMAX + 1):
    smallest_witness(n)
print("n<=300 모든 행 단봉 확인")
# 정리 old-4-5: 2<=n<=15 d_{n,k_n}<0, n>=16 >0 (n<=300)
for n in range(2, NMAX + 1):
    kn = ceil(n / 2)
    d = b(n, kn) - b(n, kn - 1)
    if n <= 15:
        assert d < 0, n
    else:
        assert d > 0, n
print("정리 old-4-5 유한 범위(n<=300) 일치")
# 4째 조각의 n=5..300: Q_R 위치에서 전제 배제 또는 (엄격감소·오목·로그오목)
for n in range(5, NMAX + 1):
    first_dec = None
    for l in range(ceil((n - 1) / 2), n - 2):
        if b(n, l) <= b(n, l + 1):
            assert first_dec is None, ("재증가", n, l)
        else:
            if first_dec is None:
                first_dec = l
            assert b(n, l + 1) ** 2 > b(n, l) * b(n, l + 2), ("lc", n, l)
            assert b(n, l) + b(n, l + 2) < 2 * b(n, l + 1), ("concave", n, l)
print("넷째 조각 성질(n<=300) 일치")

# ---------- (b) 세기 ----------
c2 = sum(ceil(n / 2) - 1 for n in range(10001, 20001))
c4 = sum(n - 2 - ceil((n - 1) / 2) for n in range(5, 20001))
c5 = sum(n - 2 - ceil((n - 1) / 2) for n in range(20001, 50001))
print("둘째 조각 비교 수:", c2, "(74,995,000)")
print("넷째 조각 위치 수:", c4, "(99,970,002)", 94192042 + 5777960)
print("정리 5-2 위치 수:", c5, "(524,955,000)")
print("k=142: 2ceil(k^2/4)=", 2 * ceil(142 ** 2 / 4), " k=141:", 2 * ceil(141 ** 2 / 4))
print("Newton 다항식 수:", sum(r - 1 for r in range(2, 171)), "(14,365)")
print("r 범위 171..9999 개수:", 9999 - 171 + 1)

# ---------- (c) Cayley 비 ----------
vals = []
for k in range(1, 10):
    cr = Fr(k + 1, k) ** (k - 2)
    v = cr * (1 + Fr(5, 2 * k) + Fr(2, k * k))
    vals.append(float(v))
    assert v > Fr(87, 32)
print("Cayley 아홉 값:", ["%.5f" % v for v in vals])
print("e<65/24+1/100<87/32:", E < 65 / 24 + 0.01 < 87 / 32, 65 / 24 + 0.01, 87 / 32)
# 보조정리 cayley-ratio 부등식 k>=10 수치
assert all(((k + 1) / k) ** (k - 2) > E * k * k / (k * k + 2.5 * k + 2) for k in range(1, 3000))
print("cr_k > e k^2/(k^2+5k/2+2) (k<3000) 수치 확인")

# ---------- (d) m(n) ----------
def mfun(n):
    m = 170
    mm = 171
    while mm ** 1.5 + 9 * mm <= n:
        m = mm
        mm += 1
    return m
print("m(20001)=", mfun(20001), " m(50001)=", mfun(50001), " 597^1.5+9*597=", 597 ** 1.5 + 9 * 597)

# ---------- (e) 경계 응답 다항식과 항등식 (작은 n 전수) ----------
def Gamma(d, y, n):
    # Fraction/정수 y
    g = [Fr(1)]
    for dd in range(1, d + 1):
        s = Fr(comb(n, dd) * p(dd))
        for j in range(0, dd):
            s += y * comb(n - dd + j, j) * p(j) * g[dd - 1 - j]
        g.append(s)
    return g[d]

def caps(sigma):
    n = len(sigma)
    h = []
    for i in range(n):
        z = 0
        for j in range(i - 1, -1, -1):
            if sigma[j] > sigma[i]:
                z = j + 1
                break
        h.append((i + 1) - z)
    return h

def K(n, k, y):
    s = Fr(0)
    for sigma in permutations(range(1, n + 1)):
        h = caps(sigma)
        pr = Fr(1)
        for hi in h:
            pr *= hi if hi <= k else y
        s += pr
    return s

def Acount(n, l):
    s = 0
    for sigma in permutations(range(1, n + 1)):
        pr = 1
        for hi in caps(sigma):
            pr *= min(hi, l + 1)
        s += pr
    return s

for n in range(1, 8):
    for l in range(0, n):
        assert Acount(n, l) == A[(n, l)]
print("따름정리 2-4 (n<=7) 일치")

# green-connection (다): K_{n,k}(y)-K_{n,k+1}(y) = (y-k-1) p_k Gamma_{n-k-1}(y;n), k+1<=n<=2k+1
for k in range(1, 5):
    for n in range(k + 1, min(2 * k + 1, 7) + 1):
        for y in [Fr(0), Fr(1), Fr(3, 2), Fr(7), Fr(-2)]:
            lhs = K(n, k, y) - K(n, k + 1, y)
            rhs = (y - k - 1) * p(k) * Gamma(n - k - 1, y, n)
            assert lhs == rhs, (k, n, y)
print("green-connection (다) 차 공식 (n<=7) 일치")
# (라): b_{n,l} = sum_{m=l}^{n-1} A_{m,l} Gamma_{n-m-1}(l;n), l+1<=n<=2l+1
for l in range(1, 8):
    for n in range(l + 1, min(2 * l + 1, 14) + 1):
        rhs = sum(A[(m, l)] * Gamma(n - m - 1, Fr(l), n) for m in range(l, n))
        assert rhs == b(n, l), (l, n)
print("green-connection (라) 첫 식 (n<=14) 일치")
# B_{n,l} = p_l Gamma_{n-l-1}(l;n) 과 2-30 첫 식 (n<=7)
def Bcount(n, k):  # B_{n,k-1}
    s = 0
    for sigma in permutations(range(1, n + 1)):
        h = caps(sigma)
        pr = 1
        H = 0
        for hi in h:
            if hi < k:
                pr *= hi
            elif hi == k:
                H += 1
            else:
                pr *= (k - 1)
        s += pr * (k ** H - (k - 1) ** H)
    return s
for l in range(1, 5):
    for n in range(l + 1, min(2 * l + 1, 7) + 1):
        assert Bcount(n, l + 1) == p(l) * Gamma(n - l - 1, Fr(l), n), (l, n)
print("B_{n,l}=p_l Gamma_{n-l-1}(l;n) (n<=7) 일치")

# source-rep (가): K_{n,k}(y) = phi_n + y sum_{m=k}^{n-1} phi_m Gamma_{n-m-1}(y;n), n<=2k+1
def phi_list(k, N):
    # exp(T_{<=k}) 계수 * m! : 모든 나무 크기 <=k 인 뿌리 숲 수
    # 나무 함수 절단: t_j = j^{j-1}/j!
    t = [Fr(0)] + [Fr(j ** (j - 1), factorial(j)) for j in range(1, N + 1)]
    for j in range(k + 1, N + 1):
        t[j] = Fr(0)
    # exp 급수 F' = T' F
    F = [Fr(1)] + [Fr(0)] * N
    for m in range(1, N + 1):
        s = Fr(0)
        for j in range(1, m + 1):
            s += j * t[j] * F[m - j]
        F[m] = s / m
    return [F[m] * factorial(m) for m in range(N + 1)]
for k in range(1, 5):
    phi = phi_list(k, 2 * k + 1)
    for n in range(0, min(2 * k + 1, 7) + 1):
        for y in [Fr(0), Fr(2), Fr(5, 3)]:
            rhs = phi[n] + y * sum(phi[m] * Gamma(n - m - 1, y, n) for m in range(k, n))
            lhs = K(n, k, y) if n >= 1 else Fr(1)
            assert lhs == rhs, (k, n, y)
print("source-rep (가) (n<=7) 일치")

# 2E_{n,k} 직접 세기 (n<=6) vs 둘째 차분
def E_count(n, k):
    cnt = 0
    for a in product(range(1, n + 1), repeat=n):
        # 주차
        spots = [0] * (n + 1)
        disp = []
        ok = True
        for car, pref in enumerate(a, 1):
            s = pref
            while s <= n and spots[s]:
                s += 1
            if s > n:
                ok = False
                break
            spots[s] = car
            disp.append(s - pref)
        if not ok:
            continue
        M = max(disp)
        if M == k:
            Mn = disp.count(M)
            if Mn % 2 == 0:
                cnt += 1
    return cnt
for n in range(2, 7):
    for k in range(1, n + 1):
        sd = K(n, k, Fr(k + 1)) - 2 * K(n, k, Fr(k)) + K(n, k, Fr(k - 1))
        assert sd == 2 * E_count(n, k), (n, k)
print("둘째 차분 = 2E_{n,k} (n<=6) 일치")

# ---------- (f) 타일 모형 ----------
def tw(j):
    return Fr(1) if j == 1 else Fr((j - 1) ** (j - 1), factorial(j))
def V_tile(q):  # q: 좌표 리스트 (길이 d), 재귀
    d = len(q)
    V = [Fr(1)]
    for dd in range(1, d + 1):
        s = (1 + q[dd - 1]) * V[dd - 1]
        for j in range(2, dd + 1):
            s += tw(j) * V[dd - j]
        V.append(s)
    return V[d]
for n in range(3, 9):
    for d in range(0, n):
        for y in [Fr(1), Fr(3), Fr(7, 2)]:
            q = [y / (n - i + 1) for i in range(1, d + 1)]
            lhs = Gamma(d, y, n)
            rhs = Fr(factorial(n), factorial(n - d)) * V_tile(q)
            assert lhs == rhs, (n, d, y)
print("inverse-renewal: Gamma_d = (n)_d V_d (n<=8) 일치")
# hb_d 계수식, hb_d(1), bd 꼬리
for d in range(1, 8):
    # 동질 좌표 다항식: 숫자로 확인 (rho=1,2,3 에서 값)
    for rho in [Fr(1), Fr(2), Fr(3)]:
        val = V_tile([rho] * d)
        form = sum(Fr((j + 1) * (d + 1) ** (d - j - 1), factorial(d - j)) * rho ** j for j in range(0, d)) + rho ** d
        assert val == form, (d, rho)
    assert V_tile([Fr(1)] * d) == Fr((d + 1) ** d, factorial(d))
print("hb_d 계수식·hb_d(1) (d<=7) 일치")
# 로그볼록 tw
for j in range(1, 30):
    assert tw(j + 1) / tw(j) <= tw(j + 2) / tw(j + 1)
print("tw 로그볼록 (j<30) 확인")
# suff-cond (가) 끝점 비 수치: V_r(k-1) <= (1+1/r)^r V_{r-1}(k)
for r in range(2, 9):
    for k in range(r + 1, r + 12):
        n = k + r
        lhs = V_tile([Fr(k - 1, n - i + 1) for i in range(1, r + 1)])
        rhs = Fr(r + 1, r) ** r * V_tile([Fr(k, n - i + 1) for i in range(1, r)])
        assert lhs <= rhs, (r, k)
print("suff-cond (가) 끝점 비 (r<=8, k<r+12) 확인")

# ---------- (g) 보조정리 lemma-L (나) L(10^4) ----------
try:
    from mpmath import mp, quad, mpf, exp as mexp, findroot, sqrt as msqrt
    mp.dps = 30
    def M(q):
        return quad(lambda y: y ** q * mexp(-y - y * y / 2), [0, mp.inf])
    def Mstar(q):
        # max of y^q e^{-y-y^2/2}: y^2 + y - q = 0
        y0 = (-1 + msqrt(1 + 4 * q)) / 2
        return y0 ** q * mexp(-y0 - y0 * y0 / 2)
    M26 = quad(lambda y: y ** 2 * mexp(-y - y * y / 2), [0, 6])
    C1 = 2 * Mstar(2) + M(3) / 2 + M(5) / 3
    C2 = Mstar(3) / 2 + Mstar(5) / 3 + M(4) / 2
    C3 = Mstar(4) / 2 + M(3) / 6
    C4 = Mstar(3) / 6
    s = mpf(100)
    L = (M26 - C1 / s - C2 / s ** 2 - C3 / s ** 3 - C4 / s ** 4) / (M(1) + (M(0) + mexp(-0.5)) / s + 1 / s ** 2)
    print("L(10^4) =", L, " (>=0.845204 ?)", L >= mpf("0.845204"))
    print("M0..M5:", [M(q) for q in range(6)], "M2^(6):", M26)
except Exception as ex:
    print("mpmath 없음:", ex)

# Pc 하계 상수
print("1/2+2*0.845204-sqrt(3pi/2) =", 0.5 + 2 * 0.845204 - sqrt(3 * pi / 2), " sqrt(3pi/2)=", sqrt(3 * pi / 2), " sqrt(pi/2)=", sqrt(pi / 2))
s = 100.0
print("대괄호(s=100) =", 1 / (3 * s) + 8 / (3 * s * s) + 2.507 / (s * s) + (1 + 2.1709 * s) / s ** 3)

# ---------- (h) 5.2.3·5.4 상수 ----------
print("2sqrt2/e =", 2 * sqrt(2) / E, " 181/174=", 181 / 174, " 26/25=", 1.04)
print("312m^2-374m+25 at m=1,2:", 312 - 374 + 25, 312 * 4 - 374 * 2 + 25)
print("(0.65)(1+3/529)/23 =", 0.65 * (1 + 3 / 529) / 23, " <1/12:", 0.65 * (1 + 3 / 529) / 23 < 1 / 12)
print("27.14^3=", 27.14 ** 3, " 0.745^3=", 0.745 ** 3, " 0.64^2=", 0.64 ** 2, " 0.75^3=", 0.75 ** 3, " 0.65^2=", 0.65 ** 2)
print("27/(4*27.14)=", 27 / (4 * 27.14), " (3/4)^1.5=", 0.75 ** 1.5)
print("1/(1+9/sqrt598)=", 1 / (1 + 9 / sqrt(598)), " 833^1.5=", 833 ** 1.5, " 832^1.5=", 832 ** 1.5, " 1.2*20001=", 1.2 * 20001)
print("966^1.5=", 966 ** 1.5, " 965^1.5=", 965 ** 1.5, " 1.5*20001=", 1.5 * 20001)
print("rq 다섯 값:", 1.2 / sqrt(598), 1.5 / sqrt(833), 1.8 / sqrt(966), 2.1 / sqrt(2164), 2.4 / 100, " 1/16=", 1 / 16)
print("(12/5)(1+1/598)/sqrt598=", 2.4 * (1 + 1 / 598) / sqrt(598), " 12/(110e)=", 12 / (110 * E), " 1/24=", 1 / 24)
print("(12/11)^1.5*(1+1/598)=", (12 / 11) ** 1.5 * (1 + 1 / 598), " log10(1.15*598^3)=", log(1.15 * 598 ** 3, 10), " 598log10(24)=", 598 * log(24, 10))
print("(9/5)^(2/3)=", 1.8 ** (2 / 3), " 10/2^(2/3)=", 10 / 2 ** (2 / 3), " 10001^(-1/3)=", 10001 ** (-1 / 3), " 0.0015/1.25^12=", 0.0015 / 1.25 ** 12)
print("1-cos(1)=", 1 - __import__('math').cos(1))
print("1/sqrt(598)=", 1 / sqrt(598), " (0.65)^(2/3)=", 0.65 ** (2 / 3), " (0.64)^(2/3)=", 0.64 ** (2 / 3))
print("597^1.5+9*597=", 597 ** 1.5 + 9 * 597, " 598^1.5+9*598=", 598 ** 1.5 + 9 * 598)
print("1160^1.5+9*1160=", 1160 ** 1.5 + 9 * 1160, " 1161:", 1161 ** 1.5 + 9 * 1161)
# 5-4 증명 e_15
e15 = sum(Fr(1, factorial(j)) for j in range(16))
print("e15 < e:", float(e15) < E, " 15!e15 정수:", (e15 * factorial(15)).denominator == 1)
