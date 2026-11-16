# -*- coding: utf-8 -*-
# 10차 독립 검토 P2: 보조정리 e-integral (4.1)과 명제 old-4-6 의 Lagrange 계수를
# 순열 전수(얼린 용량 다항식·경계 다항식)와 정확 유리수 멱급수로 대조 (k=3,4,5)
from fractions import Fraction as Fr
from itertools import permutations
from math import comb, factorial

class PS:
    """truncated power series with Fraction coefficients, order N (coeffs 0..N)"""
    def __init__(self, c, N):
        self.N = N
        self.c = [Fr(x) for x in c][:N + 1] + [Fr(0)] * max(0, N + 1 - len(c))
    def __add__(self, o):
        o = o if isinstance(o, PS) else PS([o], self.N)
        return PS([a + b for a, b in zip(self.c, o.c)], self.N)
    __radd__ = __add__
    def __neg__(self):
        return PS([-a for a in self.c], self.N)
    def __sub__(self, o):
        return self + (-(o if isinstance(o, PS) else PS([o], self.N)))
    def __rsub__(self, o):
        return (-self) + o
    def __mul__(self, o):
        if not isinstance(o, PS):
            return PS([a * o for a in self.c], self.N)
        N = self.N
        r = [Fr(0)] * (N + 1)
        for i, a in enumerate(self.c):
            if a == 0:
                continue
            for j in range(N + 1 - i):
                r[i + j] += a * o.c[j]
        return PS(r, N)
    __rmul__ = __mul__
    def __pow__(self, m):
        r = PS([1], self.N)
        for _ in range(m):
            r = r * self
        return r
    def integ(self):
        return PS([Fr(0)] + [self.c[i] / (i + 1) for i in range(self.N)], self.N)
def exp_ps(s):
    # exp of series with zero constant term
    assert s.c[0] == 0
    N = s.N
    r = PS([1], N); term = PS([1], N)
    for m in range(1, N + 1):
        term = term * s * Fr(1, m)
        r = r + term
    return r
def X(N):
    return PS([0, 1], N)

def capacities(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h.append(i - j)
    return h

def e_n_bruteforce(n, k):
    # e_n = K''_{n,k}(k): K(y)=sum_sigma prod_{h<=k} h * y^{Z}; K''(k)=sum Z(Z-1)k^{Z-2} prod
    tot = 0
    for sig in permutations(range(1, n + 1)):
        h = capacities(sig)
        Z = sum(1 for hi in h if hi > k)
        pr = 1
        for hi in h:
            if hi <= k:
                pr *= hi
        if Z >= 2:
            tot += Z * (Z - 1) * k ** (Z - 2) * pr
    return tot
def J_bruteforce(n, k, z):
    tot = 0
    for sig in permutations(range(1, n + 1)):
        h = capacities(sig)
        H = sum(1 for hi in h if hi == k); Z = sum(1 for hi in h if hi > k)
        if H == 0:
            continue
        pr = 1
        for hi in h:
            if hi < k:
                pr *= hi
        tot += H * k ** (H - 1) * z ** Z * pr
    return tot

for k in (3, 4, 5):
    NM = min(2 * k + 1, 9)
    N = NM + 2
    x = X(N)
    # Bor^tail_k(Z) = 1 - sum_{j<=k} e^{-jZ}(jZ)^{j-1}/j!
    bt = PS([1], N)
    for j in range(1, k + 1):
        bt = bt - exp_ps(x * (-j)) * ((x * j) ** (j - 1)) * Fr(1, factorial(j))
    V = PS([Fr(1, 2), -1, Fr(1, 2)], N)  # (1-Z)^2/2
    ekV_red = exp_ps(x * (-k) + x * x * Fr(k, 2))      # e^{kV(Z)} / e^{k/2}
    one_minus_sq = PS([1, -2, 1], N)
    base = one_minus_sq * bt * ekV_red
    A = (base * (V * 2 + V * V * k)).integ()
    B = (base * (2 + V * (2 * k))).integ()
    C = base.integ()
    emkV_red = exp_ps(x * k - x * x * Fr(k, 2))        # e^{-kV(Y)} * e^{k/2}
    Phi = exp_ps(x) * emkV_red * (A - V * B + V * V * C * k)
    print("k=%d e-integral (4.1):" % k)
    for n in range(k + 2, NM + 1):
        coef = (Phi * PS([1, -1], N) * exp_ps(x * n)).c[n]
        en = e_n_bruteforce(n, k)
        print("   n=%d  [Y^n]Phi(1-Y)e^{nY} = %s ; e_n/n! = %s ; e_n=%d ; match=%s" % (n, coef, Fr(en, factorial(n)), en, coef == Fr(en, factorial(n))))
    # 명제 4.6: J_n(k-1)/n! = [Y^n] Bor(k) e^Y e^{-(k-1)V(Y)} int_0^Y (1-Z)Z^{k-1} e^{k(1-Z)+(k-1)V(Z)} dZ (1-Y)e^{nY}
    # constants: Bor(k)=e^{-k}k^{k-1}/k!; e^{k(1-Z)+(k-1)V(Z)} = e^{k+(k-1)/2} e^{-(2k-1)Z+(k-1)Z^2/2}; e^{-(k-1)V(Y)} = e^{-(k-1)/2} e^{(k-1)Y-(k-1)Y^2/2}
    inner = (PS([1, -1], N) * x ** (k - 1) * exp_ps(x * (-(2 * k - 1)) + x * x * Fr(k - 1, 2))).integ()
    G = exp_ps(x) * exp_ps(x * (k - 1) - x * x * Fr(k - 1, 2)) * inner * Fr(k ** (k - 1), factorial(k))
    print("k=%d 명제 4.6 Lagrange 계수 vs J_n(k-1)/n!:" % k)
    for n in range(k, min(2 * k, NM) + 1):
        coef = (G * PS([1, -1], N) * exp_ps(x * n)).c[n]
        Jn = J_bruteforce(n, k, k - 1)
        print("   n=%d  coef=%s ; J_n(k-1)/n!=%s ; J_n=%d ; match=%s" % (n, coef, Fr(Jn, factorial(n)), Jn, coef == Fr(Jn, factorial(n))))
print("done")
