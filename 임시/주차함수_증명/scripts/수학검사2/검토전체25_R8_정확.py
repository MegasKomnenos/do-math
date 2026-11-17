# 검토전체25 R8: 장8.md의 진술을 작은 k에서 정확한 유리수로 대조
# (8.1), (8.2), 보조정리 8:old-6-23, (8.3) dup>=0, (8.4), 8:old-6-24, 8:escape-lower (8.8),
# 8:envelope-H 첫 주장, 8:old-6-30 (가)(나), 8:old-6-31 (가)(나)(다), 8:old-6-32,
# 띠 정리 둘째 단계의 생존 1 착지 하계(임의의 q_w, q_fb)
from fractions import Fraction as Fr
from math import comb, exp, pi, sqrt, e
import sys

NMAX = 46
def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1
A = {}
def build(l):
    a = [1]
    for n in range(1, NMAX + 1):
        s = 0
        for t in range(1, n + 1):
            s += comb(n - 1, t - 1) * min(t, l + 1) * a[t - 1] * a[n - t]
        a.append(s)
    return a
for l in range(-1, NMAX + 1):
    A[l] = build(l) if l >= 0 else [1] + [0] * NMAX
def Aa(n, l):
    if l < 0: return 1 if n == 0 else 0
    if l >= NMAX: return p(n)
    return A[l][n]
for n in range(0, 12):
    assert Aa(n, n) == p(n) and Aa(n, max(n - 1, 0)) == p(n)
def s(m, y): return Fr(Aa(m, y - 1), p(m))            # s_m(y)
def c(m, Y): return Fr(Aa(m, Y) - Aa(m, Y - 1), p(m))  # c_m(Y)
def b(m, Y): return Aa(m, Y) - Aa(m, Y - 1)
def pi_(n, m): return Fr(comb(n, m) * m ** (m - 1) * p(n - m), p(n))
def pi0(n, y): return 1 - sum(pi_(n, m) for m in range(y + 1, n + 1)) if n <= 2 * y + 1 else None
def sT(t, y): return Fr(min(t, y), t) * s(t - 1, y)
from math import factorial
def Bor(m): return Fr(m ** (m - 1), factorial(m))      # times e^{-m}: handled by ratios only
def Borf(m): return exp(-m) * m ** (m - 1) / factorial(m)

bad = 0
def chk(cond, msg):
    global bad
    if not cond:
        bad += 1; print("FAIL", msg)

for k in range(2, 13):
    # (8.1)
    for n in range(2 * k + 1, min(3 * k, NMAX) + 1):
        N = n - k
        Theta = comb(n, k) * k ** (k - 2) * Aa(n - k, k - 1)
        BV = sum(comb(n, m + 1) * p(n - 1 - m) * (b(m, k) + b(m, k - 1)) for m in range(2 * k + 1, n))
        chk(Fr(Theta, p(n)) == pi_(n, k) * s(N, k) / k, f"(8.1) Theta k={k} n={n}")
        chk(Fr(BV, p(n)) == sum(pi_(n, m + 1) / (m + 1) * (c(m, k) + c(m, k - 1)) for m in range(2 * k + 1, n)), f"(8.1) BV k={k} n={n}")
    # (8.2) and level k-1
    for m in range(k + 1, min(2 * k + 1, NMAX) + 1):
        rhs = sum(pi_(m, t) / t * (s(t - 1, k + 1) + k * c(t - 1, k)) for t in range(k + 1, m + 1))
        chk(c(m, k) == rhs, f"(8.2) k={k} m={m}")
    for m in range(k, min(2 * k - 1, NMAX) + 1):
        rhs = sum(pi_(m, t) / t * (s(t - 1, k) + (k - 1) * c(t - 1, k - 1)) for t in range(k, m + 1))
        chk(c(m, k - 1) == rhs, f"(8.2) level k-1 k={k} m={m}")
    # lemma 8:old-6-23 and dup>=0, strictness beyond range; upper bound with env M<=k
    for m in range(2 * k + 2, min(4 * k, NMAX) + 1):
        rhs = sum(pi_(m, t) / t * s(m - t, k) * (s(t - 1, k + 1) + k * c(t - 1, k)) for t in range(k + 1, m + 1))
        chk(c(m, k) >= rhs, f"old-6-23 k={k} m={m}")
        rhs_up = sum(pi_(m, t) / t * s(m - t, k + 1) * (s(t - 1, k + 1) + k * c(t - 1, k)) for t in range(k + 1, m + 1))
        chk(c(m, k) <= rhs_up, f"env M<=k gives upper bound k={k} m={m}")
    for m in range(2 * k, min(4 * k, NMAX) + 1):
        rhs = sum(pi_(m, t) / t * s(m - t, k - 1) * (s(t - 1, k) + (k - 1) * c(t - 1, k - 1)) for t in range(k, m + 1))
        chk(c(m, k - 1) >= rhs, f"old-6-23 level k-1 k={k} m={m}")
    # (8.4) window recursion and 8:old-6-24
    R = {0: Fr(0)}
    for q in range(1, k + 2):
        if k + q > NMAX: break
        R[q] = k * c(k + q, k)
        rhs = sum(pi_(k + q, k + j) * Fr(k, k + j) * (s(k + j - 1, k + 1) + R[j - 1]) for j in range(1, q + 1))
        chk(R[q] == rhs, f"(8.4) k={k} q={q}")
        for j in range(1, q + 1):
            chk(float(pi_(k + q, k + j)) >= Borf(q + 1 - j) * (1 - 1e-12), f"old-6-24 k={k} q={q} j={j}")
    # escape lower (8.8): y>=1, y+1<=N<=2y+1
    y = k
    for N in range(y + 1, min(2 * y + 1, NMAX) + 1):
        km = sum(pi_(N, m) * Fr(y, m) for m in range(y + 1, N + 1))
        p0 = pi0(N, y)
        chk(s(N, y) >= p0 / (1 - km) >= p0 / (1 - Fr(y, N) + Fr(y, N) * p0), f"(8.8) y={y} N={N}")
    # Jensen first claim: s_{k+q}(k+1) >= exp(-J(q,k)),  J via theta
    kk = k + 1
    for q in range(1, k + 4):
        if k + q > NMAX: break
        J = sum((q - r) * (r * Borf(r)) * Borf(kk + q - r) / Borf(kk + q) for r in range(1, q)) / kk
        chk(float(s(k + q, k + 1)) >= exp(-J) * (1 - 1e-12), f"Jensen k={k} q={q}")
    # old-6-30 (가)(나)
    for N in range(k, min(2 * k - 1, NMAX) + 1):
        ratio = s(N, k - 1) / s(N, k)
        mx = max(1 / (k * pi0(Np, k - 1)) for Np in range(k, N + 1))
        chk(ratio >= 1 - mx, f"old-6-30(가) k={k} N={N}")
        if N <= 2 * k - 2:
            lb = 1 - exp(7 / 6) * N ** 1.5 / (4 / sqrt(2 * pi) * k * (2 * k - 1 - N))
            chk(float(ratio) >= lb, f"old-6-30(나) k={k} N={N}")
        chk(ratio >= Fr(k - 1, k) ** (N - k + 1), f"capacity-shift k={k} N={N}")
    # old-6-32 and its two expansions
    def ecap(t): return sT(t, k + 1) - sT(t, k)
    def esize(t): return sT(t, k) - sT(t + 1, k)
    for t in range(k + 1, min(2 * k + 1, NMAX - 1) + 1):
        chk(ecap(t) == (s(t - 1, k + 1) + k * c(t - 1, k)) / t, f"ecap formula k={k} t={t}")
        chk(ecap(t) >= esize(t) / 2, f"old-6-32 k={k} t={t}")
        chk(esize(t) >= 0, f"esize>=0 k={k} t={t}")
        lhs = Fr(k, t * (t + 1)) * s(t - 1, k) + Fr(k, t + 1) * (Fr(1, k + 1) * (pi0(t - 1, k) - pi0(t, k)) + sum((pi0(t - 1, j) - pi0(t, j)) * esize(j) for j in range(k + 1, t)))
        chk(esize(t) == lhs, f"esize expansion k={k} t={t}")
    # old-6-31
    for m in range(2, min(3 * k, NMAX)):
        for t in range(1, m):
            if 2 * t >= m: chk(pi_(m, t + 1) >= pi_(m, t), f"old-6-31(가) m={m} t={t}")
        for t in range(1, m + 1):
            chk(pi_(m + 1, t) <= pi_(m, t), f"old-6-31(나) m={m} t={t}")
    for N in range(2, min(2 * k + 1, NMAX - 1)):
        for j in range(N // 2 + 1, N + 1):
            PN = sum(pi_(N, i) for i in range(j + 1, N + 1)); PN1 = sum(pi_(N + 1, i) for i in range(j + 1, N + 2))
            chk(PN1 - PN <= pi_(N, j), f"old-6-31(다) N={N} j={j}")
    # second step of the band theorem: survival-1 landing lower bound, arbitrary q_w, q_fb
    for nu in range(2, k + 1):
        n = 2 * k + nu; N = n - k
        if n > NMAX: break
        for qw in range(1, nu + 1):
            for qfb in range(1, k):
                for m in range(k + qw + 1, n):
                    a_ = max(m - k + 1, k + qw + 1); b_ = min(2 * k + 1, m - qfb)
                    if a_ > b_: continue
                    term = sum(pi_(m, t) * ecap(t) for t in range(a_, b_ + 1))
                    chk(all(m - t <= k - 1 for t in range(a_, b_ + 1)), "env")
                    lb = Fr(1, 2) * pi_(n, k) * s(N, k) * (Fr(k, a_) - Fr(k, b_ + 1))
                    chk(term >= lb, f"survival-1 landing k={k} nu={nu} qw={qw} qfb={qfb} m={m}")
                    # level k-1
                for m in range(k + qw, n):
                    a2 = max(m - k + 2, k + qw); b2 = min(2 * k - 1, m - qfb)
                    if a2 > b2 or k < 3: continue
                    def ecap1(t): return sT(t, k) - sT(t, k - 1)
                    term = sum(pi_(m, t) * ecap1(t) for t in range(a2, b2 + 1))
                    lb = Fr(1, 2) * pi_(n, k) * s(N, k - 1) * (Fr(k - 1, a2) - Fr(k - 1, b2 + 1))
                    chk(term >= lb, f"survival-1 landing level k-1 k={k} nu={nu} qw={qw} qfb={qfb} m={m}")
    print("k", k, "done; failures so far", bad)
print("TOTAL FAILURES", bad)
