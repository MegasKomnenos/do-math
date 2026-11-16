# -*- coding: utf-8 -*-
# 10차 독립 검토 P2: 3장 수치 검산 (정확 정수·유리수, 일부 mpmath 평가)
import sys, math
from fractions import Fraction as Fr
from math import comb, isqrt

def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1

# --- 마지막 차 재귀로 A_{n,l}, b_{n,l} (n <= NMAX) ---
NMAX = 80
A = [[0] * (NMAX + 1) for _ in range(NMAX + 1)]  # A[n][l]
for l in range(NMAX + 1):
    A[0][l] = 1
    for n in range(1, NMAX + 1):
        if l >= n - 1:
            A[n][l] = p(n)
        else:
            s = 0
            for j in range(n):
                s += comb(n - 1, j) * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l]
            A[n][l] = s
def b(n, l):
    return A[n][l] - (A[n][l - 1] if l >= 1 else 0)
rows = {n: [b(n, l) for l in range(n)] for n in range(1, NMAX + 1)}
for n in range(1, NMAX + 1):
    assert sum(rows[n]) == p(n), n

print("== 1.3절 표 n<=10 ==")
for n in range(1, 11):
    r = rows[n]
    w = r.index(max(r))
    print(n, r, "sum", sum(r), "min witness", w, "ceil(n/2)", -(-n // 2), "witness<ceil(n/2)", w < -(-n // 2))

print("== 중앙 틈 부호 d_{n,k_n} (n<=80) ==")
neg = []
for n in range(2, NMAX + 1):
    k = -(-n // 2)
    d = rows[n][k] - rows[n][k - 1]
    if d < 0:
        neg.append(n)
        # 오른쪽 절반 비증가 확인
        ok = all(rows[n][j] >= rows[n][j + 1] for j in range(k, n - 1))
        assert ok, n
print("d_{n,k_n}<0 인 n:", neg)

print("== 4.8(나) b_{n,k_n} < b_{n,k_n+1} ==")
bad = [n for n in range(5, NMAX + 1) if -(-n // 2) + 1 <= n - 1 and not (rows[n][-(-n // 2)] < rows[n][-(-n // 2) + 1])]
print("거짓인 n (5..80):", bad)

print("== 4.9 Q_L(n), 3<=n<=15 ==")
for n in range(3, 16):
    r = rows[n]
    for l in range(0, n - 2):
        if 2 * l <= n - 2 and r[l] > r[l + 1]:
            assert r[l + 1] ** 2 >= r[l] * r[l + 2], (n, l)
print("Q_L OK")

print("== 단봉성 n<=80, 로그오목 첫 실패 ==")
first = None
for n in range(1, NMAX + 1):
    r = rows[n]
    # unimodal check
    w = r.index(max(r))
    assert all(r[i] <= r[i + 1] for i in range(w)) and all(r[i] >= r[i + 1] for i in range(w, n - 1)), n
    for l in range(1, n - 1):
        if r[l] ** 2 < r[l - 1] * r[l + 1]:
            if first is None:
                first = (n, l)
            print("LC fail", n, l)
print("first failure", first)
r = rows[80]
print("b80,39<b80,40<b80,41:", r[39] < r[40] < r[41])
print(r[39]); print(r[40]); print(r[41])
print("ratios", r[40] / r[39], r[41] / r[40])
print("separator 25928/25000:", Fr(r[40], r[39]) < Fr(25928, 25000) < Fr(r[41], r[40]))

print("== 정리 3.6: E_n omega_n (n<=5) 와 sqrt n ==")
def Eomega(n):
    return sum(Fr(comb(n, j) * j ** j * p(n - j), p(n)) for j in range(1, n // 2 + 1))
for n in range(1, 6):
    e = Eomega(n)
    print(n, e, float(e), "<= sqrt n:", e * e <= n)
# n>=6 식: 9n^2-48n-32
print("9*36-48*6-32 =", 9 * 36 - 48 * 6 - 32)
# E_n omega_n <= sqrt(n) exact for n<=200 (sanity, not needed)
for n in range(6, 201):
    e = Eomega(n)
    assert e * e <= n, n
print("E omega <= sqrt n for n<=200 OK")

print("== 정리 3.6 유리수 ==")
lam = Fr(751, 1000); s = Fr(1, 31); t = Fr(1, 1000); J = 8
val = lam ** J + s * sum(i * lam ** (i - 1) for i in range(1, J + 1)) + t * sum((i - 1) * lam ** (i - 1) for i in range(1, J + 1))
print(val, val == Fr(7309649993107890414228499, 15500000000000000000000000), float(val), val < Fr(4716, 10000))
# lambda bound: ceil(3n/4)/n <= 751/1000 for n>=1000
print("max lambda n in 1000..4000:", max(Fr(-(-3 * n // 4), n) for n in range(1000, 4001)), "<=751/1000", max(Fr(-(-3 * n // 4), n) for n in range(1000, 4001)) <= lam)
# k=ceil(3n/4) <= n-1 for n>=4; 2k+1>n
print("k<=n-1, 2k+1>n for n in 4..100:", all(-(-3 * n // 4) <= n - 1 and 2 * (-(-3 * n // 4)) + 1 > n for n in range(4, 101)))
# 4.8(나) 2L >= n-k_n
print("2L>=n-k_n for n in 20..5000:", all(2 * (-(-3 * n // 4) - (-(-n // 2))) >= n - (-(-n // 2)) for n in range(20, 5001)))
# 3.6 둘째 문장 counts: ceil(3n/4)-ceil(n/2)+1 >= n-ceil(3n/4)
print("k-l* >= (n-l*)/2 with l*<=ceil(n/2)-1:", all(2 * (-(-3 * n // 4) - l) >= n - l for n in range(4, 3000) for l in [-(-n // 2) - 1]))

print("== 3.3절 상수 ==")
import mpmath as mp
mp.mp.dps = 30
print("(3/4)^{3/2} =", mp.mpf(3) / 4 ** mp.mpf(1) ** 1 if False else (mp.mpf(3) / 4) ** mp.mpf(1.5), " 3^{3/2}/8 =", mp.mpf(3) ** mp.mpf(1.5) / 8)
print("sqrt(2/pi) =", mp.sqrt(2 / mp.pi), " 3/sqrt(2pi)*2/3 =", 3 / mp.sqrt(2 * mp.pi) * mp.mpf(2) / 3)
# Legendre: Gamma(1/3)Gamma(5/6) = 2^{1/3} sqrt(pi) Gamma(2/3)
print("Legendre:", mp.gamma(mp.mpf(1) / 3) * mp.gamma(mp.mpf(5) / 6), 2 ** (mp.mpf(1) / 3) * mp.sqrt(mp.pi) * mp.gamma(mp.mpf(2) / 3))
# tail constant from Mellin pole at sigma=3/2: C = 3 * (3/2)^{1/2} Gamma(2) Gamma(1/3)/Gamma(5/6) * Gamma(2/3)/(Gamma(1/2)Gamma(1/6))
C = 3 * mp.sqrt(mp.mpf(3) / 2) * mp.gamma(mp.mpf(1) / 3) / mp.gamma(mp.mpf(5) / 6) * mp.gamma(mp.mpf(2) / 3) / (mp.gamma(mp.mpf(1) / 2) * mp.gamma(mp.mpf(1) / 6))
print("tail const from Mellin pole:", C, " 3/sqrt(2pi) =", 3 / mp.sqrt(2 * mp.pi))
# Mellin of product representation == Janson third formula form: check E[V^{-s/3}] identity numerically at s=0.7
s = mp.mpf('0.7')
lhs = mp.beta(mp.mpf(1) / 2 - s / 3, mp.mpf(1) / 6) / mp.beta(mp.mpf(1) / 2, mp.mpf(1) / 6)
rhs = mp.gamma(mp.mpf(1) / 2 - s / 3) * mp.gamma(mp.mpf(2) / 3) / (mp.gamma(mp.mpf(1) / 2) * mp.gamma(mp.mpf(2) / 3 - s / 3))
print("Beta moment identity:", lhs, rhs)
# Mellin at s=0 equals 1
s = mp.mpf(0)
M = (mp.mpf(3) / 2) ** (s / 3) * mp.gamma(1 + 2 * s / 3) * mp.gamma(mp.mpf(5) / 6 - s / 3) / mp.gamma(mp.mpf(5) / 6) * mp.gamma(mp.mpf(1) / 2 - s / 3) * mp.gamma(mp.mpf(2) / 3) / (mp.gamma(mp.mpf(1) / 2) * mp.gamma(mp.mpf(2) / 3 - s / 3))
print("Mellin at 0:", M)
# E X (mean of limit) for reference
s = mp.mpf(1)
M1 = (mp.mpf(3) / 2) ** (s / 3) * mp.gamma(1 + 2 * s / 3) * mp.gamma(mp.mpf(5) / 6 - s / 3) / mp.gamma(mp.mpf(5) / 6) * mp.gamma(mp.mpf(1) / 2 - s / 3) * mp.gamma(mp.mpf(2) / 3) / (mp.gamma(mp.mpf(1) / 2) * mp.gamma(mp.mpf(2) / 3 - s / 3))
print("E X =", M1)
