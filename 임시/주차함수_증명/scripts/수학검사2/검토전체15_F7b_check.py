# -*- coding: utf-8 -*-
"""F7b: 장7B 7.6–7.8절의 식·수치 검산.
정확 정수(Fraction)로 작은 k에서 항등식·부등식을 확인하고, 상수는 mpmath로 센다.
"""
from fractions import Fraction as Fr
from math import comb, log, exp, sqrt, floor, ceil
import mpmath as mp
mp.mp.dps = 40

def p(m):
    return (m + 1) ** (m - 1) if m >= 1 else 1

def make_A(nmax, ellmax):
    # A[n][ell] : 최대 변위 <= ell 인 길이 n 주차함수의 수 (마지막 차 재귀, 장2 old-2-6)
    A = [[0] * (ellmax + 2) for _ in range(nmax + 1)]
    for ell in range(-1, ellmax + 1):
        A[0][ell + 1] = 1
    for n in range(1, nmax + 1):
        for ell in range(-1, ellmax + 1):
            if ell < 0:
                A[n][0] = 0
                continue
            s = 0
            for j in range(1, n + 1):
                s += comb(n - 1, j - 1) * min(j, ell + 1) * A[j - 1][ell + 1] * A[n - j][ell + 1]
            A[n][ell + 1] = s
    def get(n, ell):
        if n < 0:
            raise ValueError
        if ell < 0:
            return 0 if n > 0 else 1
        return A[n][ell + 1]
    return get

def check_identities(k, nmax):
    A = make_A(nmax, k + 1)
    def s(m, y):  # 생존 확률 s_m(y) = A_{m,y-1}/p_m
        return Fr(A(m, y - 1), p(m))
    def c(m, Y):  # 수준 질량 c_m(Y) = b_{m,Y}/p_m
        return Fr(A(m, Y) - A(m, Y - 1), p(m))
    def b(m, Y):
        return A(m, Y) - A(m, Y - 1)
    def d(m):
        return b(m, k) - b(m, k - 1)
    def Pn(n, j):
        return Fr(j * comb(n - 1, j - 1) * p(j - 1) * p(n - j), p(n))
    def Pk(n, j):
        return Fr(min(j, k) * comb(n - 1, j - 1) * A(j - 1, k - 1) * A(n - j, k - 1), A(n, k - 1))
    def clp(m):
        return Fr(b(m, k), A(m, k - 1))
    def clm(m):
        return Fr(b(m, k - 1), A(m, k - 1))
    def mu(m):
        return Fr(d(m), A(m, k - 1))
    def chi(n, j):
        lin = Fr(0)
        if j == k:
            lin -= (1 - clm(n - k))
        if j > k:
            lin += clp(j - 1) + clm(j - 1) + clp(n - j) + clm(n - j)
        lin /= k
        hv = 1 if j > k else 0
        quad = (1 + Fr(hv, k)) * clp(j - 1) * clp(n - j) + (1 - Fr(hv, k)) * clm(j - 1) * clm(n - j)
        return lin + quad
    def src(n):
        return sum(Pk(n, j) * chi(n, j) for j in range(1, n + 1))
    def inh(n):
        tot = Fr(0)
        for j in range(1, n + 1):
            if k <= j - 1 <= 2 * k:
                tot += Pk(n, j) * mu(j - 1)
            if k <= n - j <= 2 * k:
                tot += Pk(n, j) * mu(n - j)
        return tot
    def inhlin(n):
        tot = Fr(0)
        for j in range(1, n + 1):
            t = Fr(0)
            if k <= j - 1 <= 2 * k:
                t += clp(j - 1) + clm(j - 1)
            if k <= n - j <= 2 * k:
                t += clp(n - j) + clm(n - j)
            tot += Pk(n, j) * t
        return tot / k
    def rw(n, q):
        return Fr(k, k + 1 + q) * Pn(n, k + 1 + q) / Pn(n, k)
    def g(x):
        return (x - 1) * log(1 + 1 / x)

    print(f"== k={k}")
    # 한 걸음 항등식 (7.13) 확인
    for n in range(1, nmax + 1):
        rhs = src(n) + sum(Pk(n, j) * (mu(j - 1) + mu(n - j)) for j in range(1, n + 1))
        assert mu(n) == rhs, ("7.13 fail", n)
    print("  (7.13) 한 걸음 항등식: OK up to n=", nmax)

    for n in range(2 * k + 1, nmax + 1):
        nu = n - 2 * k
        # (7.22)
        lhs = k * s(n, k) * src(n)
        rhs = Fr(0)
        for j in range(k + 1, n + 1):
            rhs += Fr(k, j) * Pn(n, j) * ((c(j - 1, k - 1) + c(j - 1, k)) * s(n - j, k) + s(j - 1, k) * (c(n - j, k - 1) + c(n - j, k)))
        rhs -= Pn(n, k) * s(n - k, k - 1)
        assert lhs >= rhs, ("7.22 fail", n)
        # 7.22 의 차 = k s_n(k) * 이차 몫 인지 확인
        quadpart = sum(Pk(n, j) * ((1 + Fr(1 if j > k else 0, k)) * clp(j - 1) * clp(n - j) + (1 - Fr(1 if j > k else 0, k)) * clm(j - 1) * clm(n - j)) for j in range(1, n + 1))
        assert lhs - rhs == k * s(n, k) * quadpart, ("7.22 diff", n)
        # rw 대칭 (가)
        assert rw(n, nu) == 1, ("rw(nu)!=1", n)
        # rw 비 (나)
        for q in range(0, k + nu - 1):
            ratio = rw(n, q + 1) / rw(n, q)
            j = k + 1 + q
            expect = Fr((j + 1) ** (j - 1), j ** (j - 1)) * Fr((n - j) ** (n - j - 1), (n - j + 1) ** (n - j - 1))
            assert ratio == expect, ("rw ratio", n, q)
        for q in range(nu, k + nu):
            assert rw(n, q) >= 1, ("rw>=1 fail", n, q)
        # (7.23) 첫 대괄호
        br1 = sum(rw(n, q) * (c(k + q, k - 1) + c(k + q, k)) for q in range(nu, k + nu)) - s(k + nu, k - 1)
        assert lhs >= Pn(n, k) * br1, ("7.23 first", n)
        br2 = c(k + nu, k - 1) + s(k + nu, k + 1) - s(n, k) - s(n, k + 1)
        assert br1 >= br2, ("7.23 second", n)
        # apex^H 와 (7.23) 첫 대괄호의 등식
        apex = Fr(0)
        for j in range(n - k + 1, n + 1):
            apex += Pk(n, j) * (clp(j - 1) + clm(j - 1))
        apex -= Pk(n, k) * (1 - clm(n - k))
        apex /= k
        assert k * s(n, k) * apex == Pn(n, k) * br1, ("apex identity", n)
        # top-roots 둘째·셋째 부등식 (U0 = 0 .. k-1)
        for U0 in range(0, k):
            extra = sum((rw(n, k + nu - 1 - U) - 1) * (s(n - 1 - U, k) - s(n - U, k)) for U in range(0, U0 + 1))
            assert br1 >= br2 + extra, ("top-roots 2nd", n, U0)
            hz = lambda N: 1 - s(N + 1, k) / s(N, k)
            br3 = s(n, k) * (sum((rw(n, k + nu - 1 - U) - 1) * hz(n - 1 - U) for U in range(0, U0 + 1)) - 1)
            assert br2 + extra >= br3, ("top-roots 3rd", n, U0)
        # (7.25) 둘째 층 항등식
        if n <= 3 * k:
            KDp = sum((k + n - m) * comb(n - 1, m) * p(n - 1 - m) * d(m) for m in range(2 * k + 1, n))
            assert A(n, k - 1) * (src(n) + inh(n)) == d(n) - KDp, ("7.25", n)
        # (7.24) n >= 3k+1
        if n >= 3 * k + 1:
            w = lambda m: Fr(comb(n - 1, m) * p(m) * A(n - 1 - m, k - 1), A(n, k - 1))
            pp = lambda m: Fr((k + 1) * b(m, k) - (k - 1) * b(m, k - 1), p(m))
            Left = sum(w(m) * pp(m) for m in range(k, 2 * k + 1))
            assert inhlin(n) + inh(n) == 2 * Left, ("7.24", n)
            for m in range(k, 2 * k):
                assert w(m + 1) >= w(m), ("w nondecreasing", n, m)
            # Fold/Eu 셈 (𝔩 = 1 로 두고 n>=3k+1 에서 확인; 식 자체는 𝔩에 무관)
            e = mp.e
            Eu = None
        # (7.26) n = 3k
        if n == 3 * k:
            w = lambda m: Fr(comb(n - 1, m) * p(m) * A(n - 1 - m, k - 1), A(n, k - 1))
            pp = lambda m: Fr((k + 1) * b(m, k) - (k - 1) * b(m, k - 1), p(m))
            Left = sum(w(m) * pp(m) for m in range(k, 2 * k + 1))
            u3k = w(2 * k) * s(2 * k, k + 1)
            Quad = sum(Pk(n, j) * ((1 + Fr(1, k)) * clp(j - 1) * clp(n - j) + (1 - Fr(1, k)) * clm(j - 1) * clm(n - j)) for j in range(k + 1, n + 1))
            Stem = Fr(0)
            for j in range(k + 1, n + 1):
                t = Fr(0)
                if j - 1 > 2 * k:
                    t += clp(j - 1) + clm(j - 1)
                if n - j > 2 * k:
                    t += clp(n - j) + clm(n - j)
                Stem += Pk(n, j) * t
            Stem /= k
            star = src(n) + inh(n)
            assert star == 2 * Left - u3k + Quad + Stem, ("7.26", n)
            # 문턱 단위/분할 무게 비의 망원 꼴: u/w_k = e^{g(2k)-g(k)} * s_{2k}(k+1)/s_{2k-1}(k)
            ratio = u3k / w(k)
            rr = s(2 * k, k + 1) / s(2 * k - 1, k)
            expect = mp.mpf(exp(g(2 * k) - g(k))) * (mp.mpf(rr.numerator) / rr.denominator)
            assert abs(mp.mpf(ratio.numerator) / ratio.denominator - expect) < mp.mpf(10) ** -12, ("u/w", ratio, expect)
            print(f"  n=3k={n}: (7.26) OK, u_3k/w_k = {float(ratio):.6f}, 2Left/w_k = {float(2*Left/w(k)):.6f}, star/w_k={float(star/w(k)):.6f}")
    print("  (7.22)(7.23) rw 대칭, top-roots, (7.25), (7.24), apex 등식: OK")

for k, nmax in [(2, 8), (3, 11), (4, 14), (5, 17)]:
    check_identities(k, nmax)

# ---- explicit-bounds 수치 확인 ----
def Bor(d):
    return mp.e ** (-d) * mp.mpf(d) ** (d - 1) / mp.factorial(d)
def Ren(j):
    return mp.mpf(j) ** j * mp.e ** (-j) / mp.factorial(j)
def Pm(m, j):
    return mp.mpf(j) * mp.binomial(m - 1, j - 1) * mp.mpf(p(j - 1)) * mp.mpf(p(m - j)) / mp.mpf(p(m))
def sg(m):
    return m * mp.log(mp.mpf(m) / (m + 1)) + 1
worst = 0
for m in [1, 2, 3, 5, 10, 30, 100, 300]:
    assert 0 <= sg(m) <= mp.mpf(1) / (2 * (m + 1)) + mp.mpf(1) / (6 * m * (m + 1)), ("sg", m)
    for U in range(0, m):
        lhs = Pm(m, m - U)
        rhs = Bor(U + 1) * mp.e ** sg(m) * mp.mpf(m + 1) / (m - U)
        assert lhs <= rhs * (1 + mp.mpf(10) ** -30), ("explicit (나) first", m, U)
    for j in range(1, m + 1):
        lhs = Pm(m, j)
        rhs = Ren(j) * mp.e ** sg(m) * mp.mpf(m + 1) / (m + 1 - j) ** 2
        assert lhs <= rhs * (1 + mp.mpf(10) ** -30), ("explicit (나) second", m, j)
for dd in range(1, 400):
    assert Bor(dd) <= (2 * mp.pi) ** mp.mpf(-0.5) * mp.mpf(dd) ** mp.mpf(-1.5)
for mm in [1, 5, 50, 301]:
    tail = 1 - sum(Bor(dd) for dd in range(1, mm + 1))
    assert tail <= mp.mpf(0.8) / mp.sqrt(mm), ("tail", mm, tail)
print("explicit-bounds (가)(나), sg 상하계: OK")
print("1-0.8/sqrt(301) =", mp.nstr(1 - mp.mpf(0.8) / mp.sqrt(301), 8), " sum_{U<=300} Bor(U+1) =", mp.nstr(sum(Bor(dd) for dd in range(1, 302)), 8))
print("0.9538/0.398943 =", mp.nstr(mp.mpf('0.9538') / mp.mpf('0.398943'), 8), " (2pi)^-1/2 =", mp.nstr((2 * mp.pi) ** mp.mpf(-0.5), 8))
print("0.14*2.38*0.9999 =", mp.nstr(mp.mpf('0.14') * mp.mpf('2.38') * mp.mpf('0.9999'), 8), " 0.14*301 =", 0.14 * 301)

# ---- theorem-W (나) 수치 ----
k = 3131
D2 = mp.mpf('0.08329') * mp.sqrt(k) - 2 - mp.mpf('42.14') / k
print("D_k(2) at k=3131 =", mp.nstr(D2, 8))
u = mp.mpf(k) ** (mp.mpf(1) / 6)
right = mp.mpf('0.33316') * (mp.sqrt(k) - 2 * u + 1 / u) - mp.mpf('1.0005') * k ** (mp.mpf(1) / 3) - mp.mpf('1.0145')
print("k^(1/6) =", mp.nstr(u, 8), " right-end lower value =", mp.nstr(right, 8))
deriv = mp.mpf('0.33316') * (3 * k ** (mp.mpf(1) / 3) - 2 - k ** (-mp.mpf(1) / 3)) - mp.mpf('2.001') * u
print("derivative at k=3131 =", mp.nstr(deriv, 8))
print("(1+1/3131)^(4/3) =", mp.nstr((1 + mp.mpf(1) / 3131) ** (mp.mpf(4) / 3), 8), " 2/3131 =", 2 / 3131)
print("e^{-sg_6263} =", mp.nstr(mp.e ** (-sg(6263)), 10))
def nPD(k):
    return int(mp.ceil((k + 1) ** (mp.mpf(4) / 3))) + k + 1
def G(k, n):
    return mp.mpf('0.14') / n * (mp.mpf('2.38') * mp.mpf(k) ** 1.5 * (n - k + 1) ** 2 / (mp.e ** sg(n) * n * (n + 1)) - 301)
for k in [3131, 4000, 6667, 10000, 20000]:
    nP = nPD(k)
    vals = [(G(k, n), n) for n in range(2 * k + 1, nP, max(1, (nP - 2 * k) // 2000))]
    vals += [(G(k, nP - 1), nP - 1), (G(k, 2 * k + 1), 2 * k + 1)]
    mn = min(vals)
    print(f"k={k}: n_PD={nP}, n_PD/k={nP/k:.4f}, min G over sample = {mp.nstr(mn[0],6)} at n={mn[1]}")
# k=2000, 3000 에서 (나)가 깨지는지 (범위 밖) 참고
for k in [2000, 2500, 3000, 3100, 3130]:
    nP = nPD(k)
    print(f"  참고 k={k}: G(2k+1)={mp.nstr(G(k,2*k+1),6)}, G(n_PD-1)={mp.nstr(G(k,nP-1),6)}")

# ---- threshold-unit-ratio 상수 ----
k = 6667
j0 = floor(0.3 * k)
val = -(0.3 * k - 1) * (0.3 * k) / (2 * (1.3 * k + 1))
print("j0 =", j0, " -(0.3k-1)(0.3k)/(2(1.3k+1)) =", val)
print("exact -sum_{i<=j0} i/(k+1+i) =", mp.nstr(-sum(mp.mpf(i) / (k + 1 + i) for i in range(1, j0 + 1)), 8))
print("1 + 1.5 log k + val =", 1 + 1.5 * log(k) + val)
print("e^0.3 =", mp.nstr(mp.e ** mp.mpf('0.3'), 10), " e^{3/(2k)} =", mp.nstr(mp.e ** (mp.mpf(3) / (2 * k)), 10), " 1.00023*1.34986 =", 1.00023 * 1.34986)
print("2*0.7654-1.3502 =", 2 * 0.7654 - 1.3502)
# 하계 s_{2k-1}(k) >= e^-1 k^-3/2 의 중간 단계: C(2k-1,k) >= 4^k/(4 sqrt k) 와 (1-1/k)^{k-2} >= 1/e
for kk in [2, 3, 10, 100, 6667]:
    assert mp.binomial(2 * kk - 1, kk) >= mp.mpf(4) ** kk / (4 * mp.sqrt(kk))
    assert (1 - mp.mpf(1) / kk) ** (kk - 2) >= 1 / mp.e
print("C(2k-1,k) >= 4^k/(4 sqrt k), (1-1/k)^{k-2} >= 1/e: OK")

# ---- old-6-22 증명의 수치: 16.5, 368 ----
print("e^-1 * 1003 =", 1003 / exp(1))
# 𝔳_k 상계식: (𝔪♯)^2 < 4, (𝔪♯ + x n/k)^2/2 < 12.5
# ---- 7.7 끝 문단: 표 열 K1 >= 2e4 에서 nu_P = nu_max 확인은 본문 표 대조로 함
print("done")
