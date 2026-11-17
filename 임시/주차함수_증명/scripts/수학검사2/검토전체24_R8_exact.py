# R8 (review 24): exact small-k checks of the identities and inequalities of chapter 8
# (rational arithmetic; A_{n,l} from the last-car recursion of chapter 2).
from fractions import Fraction as Fr
from math import comb, factorial, exp, log
import sys

def build(nmax, lmax):
    # A[l][n] = number of parking functions of length n with max displacement <= l
    A = {}
    for l in range(-1, lmax + 1):
        a = [0] * (nmax + 1)
        if l >= 0:
            a[0] = 1
            for n in range(1, nmax + 1):
                a[n] = sum(comb(n - 1, t - 1) * min(t, l + 1) * a[t - 1] * a[n - t] for t in range(1, n + 1))
        else:
            a[0] = 1  # A_{0,l}=1 by convention; A_{n,-1}=0 for n>=1
        A[l] = a
    return A

def p(n): return 1 if n == 0 else (n + 1) ** (n - 1)
def pi(n, m): return Fr(comb(n, m) * m ** (m - 1) * p(n - m), p(n))

def run(k):
    nmax = 3 * k + 3
    A = build(nmax, k + 1)
    s = lambda m, y: Fr(A[y - 1][m], p(m))          # s_m(y) = Pr(M <= y-1)
    c = lambda m, Y: s(m, Y + 1) - s(m, Y)          # c_m(Y) = Pr(M = Y)
    bad = 0
    # (8.2) equality on k+1<=m<=2k+1 and the lower bound (lemma old-6-23) for m>=2k+2
    for m in range(k + 1, nmax + 1):
        rhs_eq = sum(pi(m, t) / t * (s(t - 1, k + 1) + k * c(t - 1, k)) for t in range(k + 1, m + 1))
        rhs_lb = sum(pi(m, t) / t * s(m - t, k) * (s(t - 1, k + 1) + k * c(t - 1, k)) for t in range(k + 1, m + 1))
        if m <= 2 * k + 1 and rhs_eq != c(m, k): bad += 1; print("FAIL (8.2)", k, m)
        if m >= 2 * k + 2 and not rhs_lb <= c(m, k): bad += 1; print("FAIL old-6-23", k, m)
        if m >= 2 * k + 2 and rhs_eq < c(m, k): bad += 1; print("FAIL upper-reading", k, m)
    for m in range(k, nmax + 1):   # level k-1
        rhs_lb = sum(pi(m, t) / t * s(m - t, k - 1) * (s(t - 1, k) + (k - 1) * c(t - 1, k - 1)) for t in range(k, m + 1))
        if m <= 2 * k - 1 and rhs_lb != c(m, k - 1): bad += 1; print("FAIL level k-1 eq", k, m)
        if not rhs_lb <= c(m, k - 1): bad += 1; print("FAIL level k-1 lb", k, m)
    # escape-lower (8.8): y=k
    for N in range(k + 1, 2 * k + 2):
        pi0 = 1 - sum(pi(N, m) for m in range(k + 1, N + 1))
        km = sum(pi(N, m) * Fr(k, m) for m in range(k + 1, N + 1))
        if not (s(N, k) >= pi0 / (1 - km) >= pi0 / (1 - Fr(k, N) + Fr(k, N) * pi0)): bad += 1; print("FAIL (8.8)", k, N)
    # old-6-30 (ga),(na) and the capacity-shift ratio
    def pi0f(N, y): return 1 - sum(pi(N, m) for m in range(y + 1, N + 1))
    for N in range(k, 2 * k):
        ratio = s(N, k - 1) / s(N, k)
        lb_a = 1 - max(1 / (k * pi0f(Np, k - 1)) for Np in range(k, N + 1))
        if not ratio >= lb_a: bad += 1; print("FAIL old-6-30(ga)", k, N)
        if not ratio >= Fr(k - 1, k) ** (N - k + 1): bad += 1; print("FAIL shift", k, N)
        if N <= 2 * k - 2:
            lb_b = 1 - exp(7 / 6) * N ** 1.5 / (4 * (2 * 3.141592653589793) ** -0.5 * k * (2 * k - 1 - N))
            if not float(ratio) >= lb_b: bad += 1; print("FAIL old-6-30(na)", k, N)
    # old-6-31 (da)
    for N in range(2, 2 * k + 1):
        for j in range(N // 2 + 1, N + 1):
            if not pi0f(N, j) - pi0f(N + 1, j) <= pi(N, j): bad += 1; print("FAIL old-6-31(da)", k, N, j)
    # old-6-32
    sT = lambda t, y: Fr(min(t, y), t) * s(t - 1, y)
    ecap = lambda t: sT(t, k + 1) - sT(t, k)
    esize = lambda t: sT(t, k) - sT(t + 1, k)
    worst = min(ecap(t) / esize(t) for t in range(k + 1, 2 * k + 2))
    if worst < Fr(1, 2): bad += 1; print("FAIL old-6-32", k)
    for t in range(k + 1, 2 * k + 2):
        if ecap(t) != (s(t - 1, k + 1) + k * c(t - 1, k)) / t: bad += 1; print("FAIL ecap form", k, t)
    # s_N(k) = E[s^T_G(k)] on N<=2k+1
    for N in range(k + 1, 2 * k + 2):
        v = pi0f(N, k) + sum(pi(N, t) * sT(t, k) for t in range(k + 1, N + 1))
        if v != s(N, k): bad += 1; print("FAIL E[sT_G]", k, N)
    # Jensen bound with the exact index (8.9): s_{k+q}(k+1) >= exp(-J(q,k))
    def Bor(m): return exp(-m) * m ** (m - 1) / factorial(m)
    def Ren(m): return m * Bor(m)
    for q in range(1, k + 4):
        K = k + 1
        J = sum((q - r) * Ren(r) * Bor(K + q - r) / Bor(K + q) for r in range(1, q)) / K
        if not float(s(k + q, k + 1)) >= exp(-J) - 1e-12: bad += 1; print("FAIL Jensen", k, q)
    # survival-1 landing inequality and feedback/window split for a toy window (qw) and feedback width (qfb)
    qw = max(1, k // 5); qfb = max(1, k // 6)
    for nu in range(qw + 1, k - 1):
        n = 2 * k + nu; N = k + nu
        for m in range(2 * k + 1 - qfb, n):
            a = max(m - k + 1, k + qw + 1); b = min(2 * k + 1, m - qfb)
            if a > b: continue
            lhs = sum(pi(m, t) * ecap(t) for t in range(a, b + 1))
            rhs = Fr(1, 2) * pi(n, k) * s(N, k) * (Fr(k, a) - Fr(k, b + 1))
            if not lhs >= rhs: bad += 1; print("FAIL survival-1", k, nu, m)
            # these terms are part of the one-tree lower bound together with window and feedback terms
            win = sum(pi(m, k + q) / (k + q) * s(m - k - q, k) * (s(k + q - 1, k + 1) + k * c(k + q - 1, k)) for q in range(1, qw + 1))
            fb = sum(pi(m, m + 1 - j) / (m + 1 - j) * s(j - 1, k) * (s(m - j, k + 1) + k * c(m - j, k)) for j in range(1, qfb + 1))
            if m + 1 - qfb > k + qw and not c(m, k) >= win + fb + lhs: bad += 1; print("FAIL split", k, nu, m)
            winlb = sum(pi(n - 1, k + q) / (k + q) * s(N, k) * (s(k + q - 1, k + 1) + k * c(k + q - 1, k)) for q in range(1, qw + 1))
            fblb = Fr(k, n) * sum(Fr(Bor(j)).limit_denominator(10**15) * c(m - j, k) for j in range(1, qfb + 1))
            if not win >= winlb: bad += 1; print("FAIL window lb", k, nu, m)
            if not float(fb) >= float(fblb) - 1e-13: bad += 1; print("FAIL feedback lb", k, nu, m)
    # (8.1): BV_n/p_n and Theta_n/p_n forms; ratio just reported
    nu = max(2, k // 3); n = 2 * k + nu; N = n - k
    Theta = comb(n, k) * k ** (k - 2) * A[k - 1][n - k]
    BV = sum(comb(n, m + 1) * p(n - 1 - m) * ((A[k][m] - A[k - 1][m]) + (A[k - 1][m] - A[k - 2][m])) for m in range(2 * k + 1, n))
    if Fr(Theta, p(n)) != pi(n, k) * s(N, k) / k: bad += 1; print("FAIL (8.1) Theta", k)
    if Fr(BV, p(n)) != sum(pi(n, m + 1) / (m + 1) * (c(m, k) + c(m, k - 1)) for m in range(2 * k + 1, n)): bad += 1; print("FAIL (8.1) BV", k)
    print("k=%d: failures=%d, min ecap/esize=%.4f, BV/Theta at nu=%d: %.4f" % (k, bad, float(worst), nu, BV / Theta))

for k in (4, 7, 12, 18):
    run(k)
