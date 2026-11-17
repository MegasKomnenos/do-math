# 검토전체24 R5: 장6 진술의 작은 범위 정확(정수·유리수) 검산
from fractions import Fraction as Fr
from math import comb, factorial, exp, log
import math

NMAX = 135


def build(cap, nmax):
    # A[n] = A_{n,cap-1}: 최대 변위 <= cap-1 인 길이 n 주차함수 수 (마지막 차 재귀)
    A = [1]
    for N in range(nmax):
        A.append(sum(comb(N, i) * min(i + 1, cap) * A[i] * A[N - i] for i in range(N + 1)))
    return A


cache = {}


def A(n, l):
    if l < 0:
        return 0
    cap = l + 1
    if cap not in cache:
        cache[cap] = build(cap, NMAX)
    return cache[cap][n]


def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1


def s(m, y):
    return Fr(A(m, y - 1), p(m))


def c(m, Y):
    return Fr(A(m, Y) - A(m, Y - 1), p(m))


def b(m, Y):
    return A(m, Y) - A(m, Y - 1)


assert all(A(n, n - 1) == p(n) for n in range(1, 12))
assert [b(3, l) for l in range(3)] == [6, 7, 3]
print("기초 OK")

# --- (6.26) 대각선 하계와 비의 하계
bad = 0
cnt = 0
minr = None
arg = None
for m in range(2, 61):
    for d in range(1, (m + 1) // 2 + 1):
        if m < 2 * d - 1:
            continue
        w = m - d
        if w < 1:
            continue
        lhs = (w + 2) * (m + 1) * c(m + 1, w + 1)
        rhs = w * (m + 2) * c(m, w)
        cnt += 1
        r = float(lhs / rhs) / exp(1 / (4 * (w + 1) * (w + 2)))
        if minr is None or r < minr:
            minr = r
            arg = (m, d)
        if not lhs > rhs or r < 1:
            bad += 1
print("(6.26) 검사", cnt, "위반", bad, "비/exp 최소", minr, arg)


# --- 명제 chain-count: b_{m,m-d}
def bor_c(g):
    return Fr(g ** (g - 1), factorial(g))


def forests_small(N, w):
    f = [0] * (N + 1)
    f[0] = 1
    for n in range(1, N + 1):
        f[n] = sum(comb(n - 1, t - 1) * t ** (t - 1) * f[n - t] for t in range(1, min(w, n) + 1))
    return f[N]


def falling(a, j):
    r = 1
    for i in range(j):
        r *= (a - i)
    return r


def chains(d, L):
    def rec(prev, left):
        if left == 0:
            yield ()
            return
        for q in range(prev - 1, -1, -1):
            if q < left - 1:
                break
            for rest in rec(q, left - 1):
                yield (q,) + rest
    return rec(d, L)


bad = 0
cnt = 0
for m in range(2, 15):
    for d in range(1, (m + 1) // 2 + 1):
        w = m - d
        t = m + 1
        y = w + 1
        tot = Fr(0)
        for L in range(1, d + 1):
            for qs in chains(d, L):
                j = d - qs[-1]
                prodc = Fr(1)
                prev = d
                for q in qs:
                    prodc *= bor_c(prev - q)
                    prev = q
                P1 = Fr(1)
                P2 = Fr(1)
                for q in qs:
                    P1 *= Fr(y, y + q)
                    P2 *= Fr(y - 1, y + q)
                tot += falling(t - 1, j) * prodc * forests_small(t - 1 - j, w) * (P1 - P2)
        cnt += 1
        if tot != b(m, w):
            bad += 1
            print("chain-count 불일치", m, d, tot, b(m, w))
print("chain-count 검사", cnt, "위반", bad)

assert all(sum(bor_c(i) * bor_c(g - i) for i in range(1, g)) == 2 * (1 - Fr(1, g)) * bor_c(g) for g in range(1, 30))
print("split-mass OK")


def pi_(N, m):
    return Fr(comb(N, m) * m ** (m - 1) * p(N - m), p(N))


def fs(d, y):
    return s(y + d - 1, y)


def tt(y):
    return Fr(comb(2 * y + 2, y + 1) * (y + 1) ** (2 * y), 2 * p(2 * y + 2))


bad = 0
for y in range(1, 9):
    for d in range(1, y + 4):
        N = y + d - 1
        S = sum(pi_(N, y + q) for q in range(1, d))
        rhs = (1 - S) + sum(pi_(N, y + q) * Fr(y, y + q) * fs(q, y) for q in range(1, d))
        if d == y + 3:
            rhs += tt(y) / (y + 1) ** 2
        if rhs != fs(d, y):
            bad += 1
            print("(6.21) 불일치", y, d)
print("(6.21) 위반", bad)


def stay(m, l):
    return s(m + 1, l + 1) - s(m, l)


def Er(y, d, q):
    return pi_(y + d - 1, y + q) - pi_(y + d, y + 1 + q)


def T(y, d):
    return sum(Er(y, d, q) * (1 - Fr(y, y + q) * fs(q, y)) for q in range(1, d))


bad = 0
for y in range(1, 9):
    for d in range(1, y + 3):
        rhs = pi_(y + d, y + 1) / (y + 1) + sum(pi_(y + d, y + 1 + q) * ((y + 1) * c(y + q, y) + fs(q + 1, y)) / (y + 1 + q) for q in range(1, d))
        if d == y + 2:
            rhs -= tt(y) / (y + 1) ** 2
        if rhs != c(y + d, y):
            bad += 1
            print("(6.22) 불일치", y, d)
        rhs = T(y, d) + sum(pi_(y + d, y + 1 + q) * (Fr(y, y + q) * stay(y + q - 1, y) + Fr(q, (y + q) * (y + 1 + q)) * fs(q, y + 1)) for q in range(1, d))
        if rhs != stay(y + d - 1, y):
            bad += 1
            print("(6.23) 불일치", y, d)
        if any(Er(y, d, q) < 0 for q in range(1, d)):
            bad += 1
print("(6.22)(6.23) 위반", bad)


def J(y, d):
    return (d - 1) * c(y + d, y) - (y + 1) * stay(y + d - 1, y)


def Cv(y, d, q):
    return (d - 1) * (y + 1) - Fr((q - 1) * y * (y + 1 + q), y + q) - Fr((y + 1) * q, y + q)


def Cs(y, d, q):
    return (d - 1) - Fr((y + 1) * q, y + q)


bad = 0
for y in range(1, 9):
    for d in range(2, y + 3):
        rhs = Fr(d - 1, y + 1) * pi_(y + d, y + 1) - (y + 1) * T(y, d) + sum(pi_(y + d, y + 1 + q) / (y + 1 + q) * (Cv(y, d, q) * c(y + q, y) + Cs(y, d, q) * fs(q + 1, y) + Fr(y * (y + 1 + q), y + q) * J(y, q)) for q in range(1, d))
        if d == y + 2:
            rhs -= tt(y) / (y + 1)
        if rhs != J(y, d):
            bad += 1
            print("(6.24) 불일치", y, d)
print("(6.24) 위반", bad)

bad = 0
cnt = 0
for y in range(50, 63):
    for d in range(2, y + 3):
        cnt += 1
        if not J(y, d) > 0:
            bad += 1
print("(6.20) y=50..62 검사", cnt, "위반", bad)
small_fail = [(y, d) for y in range(1, 50) for d in range(2, y + 3) if not J(y, d) >= 0]
print("(6.20) y<50 에서의 위반 수(참고)", len(small_fail), small_fail[:5])

bad = 0
minrat = None
for y in (50, 51):
    for d in range(2, y + 3):
        ers = [None] + [Er(y, d, q) for q in range(1, d)]
        for q in range(1, d):
            G = pi_(y + d, y + 1 + q) * Cv(y, d, q) / (y + 1 + q)
            Om = G - (y + 1) * (sum(ers[q + 1:d]) + ers[q] * Fr(q, y + q))
            rat = float(Om / G)
            if minrat is None or rat < minrat:
                minrat = rat
                arg = (y, d, q)
            if rat < 0.2:
                bad += 1
            Mg = pi_(y + d, y + 1 + q) * Cs(y, d, q) / (y + 1 + q) - (y + 1) * ers[q] * Fr(q, y + q)
            if Mg < 0 and (d, q) not in ((2, 1), (3, 2)):
                bad += 1
                print("Mg<0", y, d, q)
print("Omega/G 최소", minrat, arg, "위반", bad)
bad = 0
for y in range(10, 30):
    for d in range(2, y + 3):
        for q in range(1, d):
            Mg = pi_(y + d, y + 1 + q) * Cs(y, d, q) / (y + 1 + q) - (y + 1) * Er(y, d, q) * Fr(q, y + q)
            if Mg < 0 and (d, q) not in ((2, 1), (3, 2)):
                bad += 1
print("Mg y=10..29 위반", bad, "Mg(3,2) at y=10:", float(pi_(13, 13) * Cs(10, 3, 2) / 13 - 11 * Er(10, 3, 2) * Fr(2, 12)))


def g(x):
    return (x - 1) * log(1 + 1 / x)


for k in (43, 44):
    xk_inv = Fr(k + 1, k) ** (k - 1)
    viol = []
    eq = []
    for N in range(0, 130):
        r = Fr(A(N + 1, k - 1), (N + 1) * A(N, k - 1))
        if r > xk_inv:
            viol.append(N)
        if r == xk_inv:
            eq.append(N)
    print("k", k, "r_N>e^g(k):", viol, "등호:", eq)
    viol = []
    eq = []
    for n in range(k + 1, 131):
        for t in range(k, n):
            w0 = comb(n, t) * t ** (t - 1) * A(n - t, k - 1)
            w1 = comb(n, t + 1) * (t + 1) ** t * A(n - t - 1, k - 1)
            if w1 < w0:
                viol.append((t, n))
            if w1 == w0:
                eq.append((t, n))
    print("   w 증가 위반", viol[:3], "등호", eq)
    viol = 0
    for N in range(2 * k - 1, 129):
        hz = 1 - s(N + 1, k) / s(N, k)
        epsN = g(N + 1) - g(k)
        if not (float(hz) >= 1 - exp(-epsN) >= (0.75 - 11 / (6 * k)) / k >= 1 / (2 * k)):
            viol += 1
    print("   위험률 (다) 위반", viol)


def DD(m, y):
    return (y + 2) * s(m + 2, y + 2) - 2 * (y + 1) * s(m + 1, y + 1) + y * s(m, y)


for k in (3, 7, 12, 20):
    V = sum((k + 1) * c(m, k) - (k - 1) * c(m, k - 1) for m in range(k, 2 * k + 1))
    Bd = 2 - 2 * s(2 * k + 1, k + 1) - (k - 1) * stay(2 * k, k) - (k - 1) * c(2 * k, k - 1)
    assert V == Bd + sum(DD(m, k - 1) for m in range(k, 2 * k)), k
print("(6.40) OK")


def Borf(n):
    return math.exp((n - 1) * math.log(n) - n - math.lgamma(n + 1))


for k in (7, 12, 20):
    for m in range(k, 2 * k + 1):
        U = sum(math.e * Borf(mm + 1) * float((k + 1) * c(mm, k) - (k - 1) * c(mm, k - 1)) for mm in range(m, 2 * k + 1))
        rhs = (k + 1) * Borf(m + 1) * float(c(m, k)) + sum((k + 1) * Borf(n + 1) * float(c(n, k)) - (k - 1) * Borf(n) * float(c(n - 1, k - 1)) for n in range(m + 1, 2 * k + 1)) - (k - 1) * Borf(2 * k + 1) * float(c(2 * k, k - 1))
        assert abs(U / math.e - rhs) < 1e-12
print("(6.42) OK")

bad = 0
for y in range(2, 30):
    for n in range(y + 1, 2 * y + 2):
        P = Fr(-1, y) + sum(((y + 1) * c(t - 1, y) - (y - 1) * c(t - 1, y - 1)) / t for t in range(y + 1, n + 1))
        if not y * P >= -1 - Fr(y * (y - 1), n) * c(n - 1, y - 1):
            bad += 1
print("(6.34) 위반", bad)

bad = 0
for k in range(2, 40):
    W0 = sum(Borf(n) * float(c(n - 1, k - 1)) for n in range(k + 1, 2 * k + 1))
    if not W0 < 2 * (2 * math.pi) ** -0.5 * k ** -1.5:
        bad += 1
    for n in range(k + 1, 2 * k + 1):
        loss = (k + 1) * Borf(n + 1) * float(c(n, k)) - (k - 1) * Borf(n) * float(c(n - 1, k - 1))
        if not loss >= -(k - 1) / (2 * n) * Borf(n) * float(c(n - 1, k - 1)):
            bad += 1
print("first-layer-mass / one-step-loss 위반", bad)
