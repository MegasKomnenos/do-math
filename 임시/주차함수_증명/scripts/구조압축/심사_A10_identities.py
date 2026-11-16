# -*- coding: utf-8 -*-
"""심사 A10 — 항등식 검산 (정확 산술).

(1) N1 (F3 §7): regen_n - A_{n,k-1}(*)(n) = sum_{m=2k+1}^{n-1} L_{n,m} d_{m,k},
    L_{n,m} = [1 + (n-m-1)(1 - k/(m+1))] C(n-1,m) A_{n-m-1,k-1}.
    원고: regen_n = d_{n,k} - k sum C(n,m+1) A_{n-m-1,k-1} d_{m,k} (9장 9.4절),
          A_{n,k-1}(*)(n) = d_{n,k} - KD'_n,  KD'_n = sum_{m>2k} (k+n-m) C(n-1,m) p_{n-1-m} d_{m,k} (7:old-6-21; n<=3k 라 A_{n-1-m,k-1}=p_{n-1-m}).
    그러므로 L_{n,m} = C(n-1,m) p_{n-1-m} [ (k+n-m) - k n/(m+1) ] 이어야 한다. 두 꼴이 같은지를 유리수로 확인한다.
(2) R4 (10.3(d)): N <= m <= n-1 에서 w_m A_{n,k-1} = C(n-1,m) p_m p_{n-1-m} = (p_n/n) pi_n(m+1),
    pi_n(t) = Bor(t) Bor(n+1-t)/Bor(n+1) (2.5절). e 가 지워지므로 정수 항등식 C(n-1,m)(m+1)^{m-1}(n-m)^{n-m-2} = (n-1)! (m+1)^m (n-m)^{n-m-1} / ((m+1)! (n-m)!).
(3) S9 (F2 §8.1): frak w_n(m+1) = n A_{n,k-1} w_m  <=>  C(n,m+1)(m+1)^m = n C(n-1,m) (m+1)^{m-1}.
(4) 10.3(e) 의 망원: frak g^L_N = e^{g(N)-g(k)}  (지수의 합이 정확히 g(N)-g(k) 인지; 유리수 로그 대신 지수 인자를 유리수로).
"""
from fractions import Fraction as Fr
from math import comb, factorial
import random

random.seed(1117)

print("== (1) N1: L_{n,m} 두 꼴의 일치 ==")
bad = 0
for _ in range(2000):
    k = random.randint(2, 40)
    n = random.randint(2 * k + 2, 3 * k)
    m = random.randint(2 * k + 1, n - 1)
    F3 = Fr(1) + (n - m - 1) * (1 - Fr(k, m + 1))
    mine = (k + n - m) - Fr(k * n, m + 1)
    if F3 != mine:
        bad += 1
    if F3 <= 0:
        bad += 1
print(f"  2000 표본에서 불일치 {bad}건; (양수성 포함)  -> L_{{n,m}} = C(n-1,m) p_{{n-1-m}} [ (k+n-m) - kn/(m+1) ] = F3 의 꼴")

print("\n== (2) R4: w_m A_{n,k-1} = (p_n/n) pi_n(m+1) 의 정수 항등식 (m >= N 이면 A_{n-1-m,k-1} = p_{n-1-m}) ==")
bad = 0
for n in range(3, 40):
    for m in range(1, n):
        lhs = comb(n - 1, m) * (m + 1) ** (m - 1) * (n - m) ** (n - m - 2) if n - m >= 2 else None
        if lhs is None:
            # n-m = 1: p_0 = 1, Bor(1) = e^{-1}; 식은 (n-m)^{n-m-2} = 1^{-1} = 1 로 읽는다
            lhs = comb(n - 1, m) * (m + 1) ** (m - 1)
            rhs = Fr(factorial(n - 1) * (m + 1) ** m * 1, factorial(m + 1) * factorial(1))
        else:
            rhs = Fr(factorial(n - 1) * (m + 1) ** m * (n - m) ** (n - m - 1), factorial(m + 1) * factorial(n - m))
        if Fr(lhs) != rhs:
            bad += 1
print(f"  n<40 전수: 불일치 {bad}건  -> w_m = pi_n(m+1) / (n s_n(k))  (N <= m <= n-1)")

print("\n== (3) S9: frak w_n(m+1) = n A_{n,k-1} w_m ==")
bad = 0
for n in range(2, 60):
    for m in range(0, n):
        if comb(n, m + 1) * (m + 1) ** m != n * comb(n - 1, m) * (m + 1) ** (m - 1) * (m + 1) // (m + 1) * 1 and comb(n, m + 1) * (m + 1) ** m != n * comb(n - 1, m) * (m + 1) ** (m - 1):
            bad += 1
print(f"  n<60 전수: 불일치 {bad}건  -> 6.17 (t=m+1) 과 10.3(a) 는 같은 비, 6.9 와 10.3(d) 는 같은 Borel 꼴")

print("\n== (4) 10.3(e): prod_{i=k}^{N-1} e^{g(i+1)}/e^{g(n-1-i)} = e^{g(N)-g(k)} (n = k+N) ==")
# e^{g(x)} = (1+1/x)^{x-1} 은 유리수
def eg(x):
    return Fr(x + 1, x) ** (x - 1)
bad = 0
for k in range(2, 15):
    for nu in range(1, k + 1):
        n = 2 * k + nu
        N = k + nu
        prod = Fr(1)
        for i in range(k, N):
            prod *= eg(i + 1) / eg(n - 1 - i)
        if prod != eg(N) / eg(k):
            bad += 1
print(f"  k<15 전수: 불일치 {bad}건")
