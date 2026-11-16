# -*- coding: utf-8 -*-
"""검토전체5 K8: 8장 진술의 정확 산술 검산 (작은 k).

A_{n,l} 을 지수 공식 재귀 A_{n,l} = sum_t C(n-1,t-1) N_l(t) A_{n-t,l},
N_l(t) = min(t,l+1) A_{t-1,l} 로 정확 정수로 만들고,
s_m(y)=A_{m,y-1}/p_m, c_m(Y)=(A_{m,Y}-A_{m,Y-1})/p_m 으로
8.1 (8.2)(8.3), 8.2 (8.10), 명제 U(가), 8.3 보조정리 C0, 사실 1·2(마), 보조정리 K,
그리고 (8.1) 의 Theta/BV 식을 확인한다.
"""
from fractions import Fraction as Fr
from math import comb, factorial, exp
import sys

NMAX = 20
# A[l][n]
A = {}
def getA(n, l):
    if n == 0:
        return 1
    if l < 0:
        return 0
    key = (n, l)
    if key in A:
        return A[key]
    tot = 0
    for t in range(1, n + 1):
        Nl = min(t, l + 1) * getA(t - 1, l)
        tot += comb(n - 1, t - 1) * Nl * getA(n - t, l)
    A[key] = tot
    return tot

def p(m):
    return (m + 1) ** (m - 1) if m >= 1 else 1

def s(m, y):
    if y <= 0:
        return Fr(0)
    return Fr(getA(m, y - 1), p(m))

def c(m, Y):
    return Fr(getA(m, Y) - getA(m, Y - 1), p(m))

def pi(n, m):
    return Fr(comb(n, m) * m ** (m - 1) * p(n - m), p(n))

def pi0(n, y):
    # Pr_n(G<=y): all trees size <= y; count = forests of trees of size <=y
    # = n![x^n] exp(sum_{t<=y} t^{t-1} x^t/t!)
    # compute via recursion F(n) = sum_t C(n-1,t-1) t^{t-1} F(n-t), t<=y
    memo = {0: 1}
    def F(nn):
        if nn in memo:
            return memo[nn]
        tot = 0
        for t in range(1, min(y, nn) + 1):
            tot += comb(nn - 1, t - 1) * t ** (t - 1) * F(nn - t)
        memo[nn] = tot
        return tot
    return Fr(F(n), p(n))

ok = True
def chk(cond, msg):
    global ok
    if not cond:
        ok = False
        print("FAIL", msg)

# sanity: A_{n,n-1} = p_n
for n in range(1, 12):
    chk(getA(n, n - 1) == p(n), f"A_{n},{n-1} != p_{n}")

# (8.2) one-tree recursion: equality for k+1<=m<=2k+1, lower bound (with env) for m>=2k+2
for k in range(2, 7):
    for m in range(k + 1, min(NMAX, 3 * k) + 1):
        rhs = sum(pi(m, t) / t * (s(t - 1, k + 1) + k * c(t - 1, k)) * s(m - t, k)
                  for t in range(k + 1, m + 1))
        if m <= 2 * k + 1:
            chk(rhs == c(m, k), f"(8.2) eq k={k} m={m}: {rhs} vs {c(m,k)}")
            # also env factor should be 1 there
        else:
            chk(rhs <= c(m, k), f"(8.2) lb k={k} m={m}")
            # (8.3) dup>=0 is same statement
    # level k-1 version
    for m in range(k, min(NMAX, 3 * k) + 1):
        rhs = sum(pi(m, t) / t * (s(t - 1, k) + (k - 1) * c(t - 1, k - 1)) * s(m - t, k - 1)
                  for t in range(k, m + 1))
        if m <= 2 * k - 1:
            chk(rhs == c(m, k - 1), f"(8.2) k-1 eq k={k} m={m}")
        else:
            chk(rhs <= c(m, k - 1), f"(8.2) k-1 lb k={k} m={m}")
print("(8.2) checked")

# (8.1): Theta_n/p_n = pi_n(k) s_N(k)/k ; BV_n/p_n = sum pi_n(m+1)/(m+1) (c_m(k)+c_m(k-1))
for k in range(2, 6):
    for n in range(2 * k + 1, min(NMAX, 3 * k - 1) + 1):
        Theta = comb(n, k) * k ** (k - 2) * getA(n - k, k - 1)
        chk(Fr(Theta, p(n)) == pi(n, k) * s(n - k, k) / k, f"(8.1) Theta k={k} n={n}")
        BV = sum(comb(n, m + 1) * p(n - 1 - m) * (getA(m, k) - getA(m, k - 1) + getA(m, k - 1) - getA(m, k - 2))
                 for m in range(2 * k + 1, n))
        rhs = sum(pi(n, m + 1) / (m + 1) * (c(m, k) + c(m, k - 1)) for m in range(2 * k + 1, n))
        chk(Fr(BV, p(n)) == rhs, f"(8.1) BV k={k} n={n}")
print("(8.1) checked")

# theta_{N+1}(m) = (N+1-m) pi_N(m) and lowest violation (8.10)
def theta(t, kk):
    return Fr(comb(t, kk) * kk ** (kk - 1) * (t - kk) ** (t - kk), t ** (t - 1)) if t > kk else Fr(1)
for y in range(2, 7):
    for N in range(y + 1, min(NMAX, 2 * y + 1) + 1):
        for m in range(y + 1, N + 1):
            chk(theta(N + 1, m) == (N + 1 - m) * pi(N, m), f"theta id N={N} m={m}")
        rhs = sum(theta(N + 1, m) * Fr(m - y, m) * s(m - 1, y) for m in range(y + 1, N + 1))
        chk(rhs == 1 - s(N, y), f"(8.10) y={y} N={N}: {float(rhs)} vs {float(1-s(N,y))}")
        # prop U (가)
        B = sum(theta(N + 1, m) * Fr(m - y, m) for m in range(y + 1, N + 1))
        chk(s(N, y) <= 1 / (1 + B), f"propU y={y} N={N}")
        # escape lower (8.9)
        km = sum(pi(N, m) * Fr(y, m) for m in range(y + 1, N + 1))
        chk(s(N, y) >= pi0(N, y) / (1 - km), f"(8.9) first y={y} N={N}")
        chk(pi0(N, y) / (1 - km) >= pi0(N, y) / (1 - Fr(y, N) + Fr(y, N) * pi0(N, y)), f"(8.9) second y={y} N={N}")
        # chain formula recursion
        rec = pi0(N, y) + sum(pi(N, m) * Fr(y, m) * s(m - 1, y) for m in range(y + 1, N + 1))
        chk(rec == s(N, y), f"chain recursion y={y} N={N}")
print("(8.10), U, (8.9) checked")

# 보조정리 C0 (old-6-30): k>=2, k<=N<=2k-1
for k in range(3, 8):
    for N in range(k, min(NMAX, 2 * k - 1) + 1):
        ratio = s(N, k - 1) / s(N, k)
        chk(ratio >= Fr(k - 1, k) ** (N - k + 1), f"C0(가) k={k} N={N}")
        mx = max(1 / (k * pi0(Np, k - 1)) for Np in range(k, N + 1))
        chk(ratio >= 1 - mx, f"C0(나) k={k} N={N}: {float(ratio)} vs {float(1-mx)}")
        if N <= 2 * k - 2:
            lb3 = 1 - exp(7 / 6) * N ** 1.5 / (4 * (2 * 3.141592653589793) ** -0.5 * k * (2 * k - 1 - N))
            chk(float(ratio) >= lb3 - 1e-12, f"C0(다) k={k} N={N}: {float(ratio)} vs {lb3}")
            # also check the pi0 lower bound itself
            for Np in range(k, N + 1):
                lbpi = 4 * (2 * 3.141592653589793) ** -0.5 * exp(-7 / 6) * (2 * k - 1 - Np) * Np ** -1.5
                chk(float(pi0(Np, k - 1)) >= lbpi - 1e-12, f"pi0 lb k={k} N'={Np}")
print("C0 checked")

# 사실 1·2 (old-6-31)(마): N/2<j<=N: pi0_N(j)-pi0_{N+1}(j) <= pi_N(j)
for N in range(2, 16):
    for j in range(N // 2 + 1, N + 1):
        chk(pi0(N, j) - pi0(N + 1, j) <= pi(N, j), f"(마) N={N} j={j}")
        # (가)
        chk(pi(N, j) == pi0(N, j) - pi0(N, j - 1), f"(가) N={N} j={j}")
print("old-6-31 checked")

# 보조정리 K (old-6-32): k+1<=t<=2k+1: eps_cap(t) >= eps_size(t)/2
def sT(t, y):
    return Fr(min(t, y), t) * s(t - 1, y)
for k in range(1, 8):
    for t in range(k + 1, min(NMAX, 2 * k + 1) + 1):
        ecap = sT(t, k + 1) - sT(t, k)
        esize = sT(t, k) - sT(t + 1, k)
        chk(ecap >= esize / 2, f"K k={k} t={t}: {float(ecap)} vs {float(esize/2)}")
        chk(ecap == (s(t - 1, k + 1) + k * c(t - 1, k)) / t, f"eps_cap formula k={k} t={t}")
print("old-6-32 checked")

# (8.4)/(8.5): R_q recursion and lower bound for small k (Bor needs float)
from math import pi as PI, e as E
def Bor(m):
    return exp(-m) * m ** (m - 1) / factorial(m)
for k in range(3, 7):
    for q in range(1, min(k + 1, NMAX - k) + 1):
        R = lambda qq: float(k * c(k + qq, k)) if qq >= 1 else 0.0
        rhs = sum(float(pi(k + q, k + j)) * k / (k + j) * (float(s(k + j - 1, k + 1)) + R(j - 1)) for j in range(1, q + 1))
        chk(abs(rhs - R(q)) < 1e-12, f"(8.4) k={k} q={q}")
        lb = k / (k + q) * sum(Bor(j) * (float(s(k + q - j, k + 1)) + R(q - j)) for j in range(1, q + 1))
        chk(R(q) >= lb - 1e-12, f"(8.5) k={k} q={q}")
        for j in range(1, q + 1):
            chk(float(pi(k + q, k + j)) >= Bor(q + 1 - j) - 1e-15, f"D1 k={k} q={q} j={j}")
print("(8.4)(8.5) checked")

print("ALL OK" if ok else "SOME FAILED")
