# -*- coding: utf-8 -*-
"""2장의 항등식 몇을 작은 n에서 수치로 확인한다: 2-13, 2-28, 2-30, 2-37(마), 2-40, 2-41."""
import io, sys, itertools
from fractions import Fraction as Fr
from math import comb, factorial
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

N = 14
def p(n): return (n+1)**(n-1) if n >= 1 else 1
A = [[0]*(N+2) for _ in range(N+1)]
for l in range(N+2):
    A[0][l] = 1
    for n in range(1, N+1):
        A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
def Aget(n, l):
    if l < 0: return 0
    return A[n][min(l, N+1)]
def b(n, l): return Aget(n, l) - Aget(n, l-1)
def d(n, k): return b(n, k) - b(n, k-1)

# --- 2-28, 2-30 by brute force over parking functions (n<=6)
def park(a):
    n = len(a); occ = [0]*(n+2); pos = [0]*n
    for i, ai in enumerate(a):
        q = ai
        while q <= n and occ[q]: q += 1
        if q > n: return None
        occ[q] = i+1; pos[i] = q
    return pos, occ[1:n+1]
def h_of(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        js = [j for j in range(1, i) if sigma[j-1] > sigma[i-1]]
        h.append(i - (max(js) if js else 0))
    return h
for n in range(1, 7):
    E = {}; B = {}; E2 = {}
    for a in itertools.product(range(1, n+1), repeat=n):
        r = park(a)
        if r is None: continue
        pos, sigma = r
        disp = [pos[i]-a[i] for i in range(n)]
        M = max(disp); Msh = disp.count(M)
        h = h_of(sigma)
        if Msh % 2 == 0: E[M] = E.get(M, 0) + 1
        if Msh == 2: E2[M] = E2.get(M, 0) + 1
        # blocked: every car with displacement M sits at position i with h_i = M+1
        blocked = all(h[pos[i]-1] == M+1 for i in range(n) if disp[i] == M)
        if blocked: B[M] = B.get(M, 0) + 1
    for k in range(1, n+1):
        assert d(n, k) == 2*E.get(k, 0) - B.get(k-1, 0), (n, k)
        assert 2*E2.get(k, 0) - B.get(k-1, 0) <= d(n, k)
    # 2-30: B_{n,k-1} = J_n(k-1) - Xi for n in {2k-1, 2k}
    for k in range(1, n+1):
        if n not in (2*k-1, 2*k): continue
        J = 0
        for sigma in itertools.permutations(range(1, n+1)):
            h = h_of(sigma); H = h.count(k); Z = sum(1 for x in h if x > k)
            pr = 1
            for x in h:
                if x < k: pr *= x
            J += H * k**(H-1) * (k-1)**Z * pr if H >= 1 else 0
        Xi = comb(2*k-1, k-1)*p(k-1)**2 if n == 2*k else 0
        assert B.get(k-1, 0) == J - Xi, (n, k, B.get(k-1, 0), J, Xi)
print("2-28, 2-29 inequality, 2-30 verified for n<=6")

# --- 2-13 first formula: A_{n,l} = p_n pi0_n(l+1) + sum_{m=l+2}^n C(n,m)(l+1)A_{m-1,l} p_{n-m}, for n<=2l+3
# pi0_n(y) = Pr(largest tree <= y): count forests with all trees <= y via EGF of trees of size<=y
def forests_maxtree_le(n, y):
    # exponential formula with truncated tree series; exact integers via Fractions
    T = [Fr(0)]*(n+1)
    for t in range(1, min(y, n)+1): T[t] = Fr(t**(t-1), factorial(t))
    # exp(T) coefficients
    E = [Fr(0)]*(n+1); E[0] = Fr(1)
    # E' = T' E  => (m+1)E[m+1] = sum_{i} (i+1) T[i+1] E[m-i]
    for m in range(n):
        s = sum((i+1)*T[i+1]*E[m-i] for i in range(m+1) if i+1 <= n)
        E[m+1] = s/(m+1)
    return E[n]*factorial(n)
for l in range(0, 6):
    for n in range(1, min(2*l+3, N)+1):
        y = l+1
        lhs = Aget(n, l)
        rhs = forests_maxtree_le(n, y) + sum(comb(n, m)*(l+1)*Aget(m-1, l)*p(n-m) for m in range(l+2, n+1))
        assert lhs == rhs, (n, l, lhs, rhs)
print("2-13 first formula verified for l<=5, n<=2l+3")

# --- 2-37(마): theta_t(k) = Ren(t-k)Bor(k)/Bor(t) (symbolically e cancels; check rational part)
for k in range(2, 8):
    for t in range(k, 15):
        theta = Fr(comb(t, k)*k**(k-1)*(t-k)**(t-k) if t > k else 1, t**(t-1) if t > k else 1)
        if t == k: theta = Fr(1)
        ren = Fr((t-k)**(t-k), factorial(t-k)) if t > k else Fr(1)
        rhs = ren*Fr(k**(k-1), factorial(k))/Fr(t**(t-1), factorial(t))
        assert theta == rhs, (k, t)
print("2-37(마) verified")

# --- 2-40 five-part decomposition, 2-41 integer form, for k=2..4, 2k+1<=n<=3k-1
def bT(t, l):  # trees of size t with max displacement exactly l
    def Ncal(t, l): return min(t, l+1)*Aget(t-1, l) if t >= 1 else 0
    return Ncal(t, l) - (Ncal(t, l-1) if l >= 1 else 0)
for k in range(2, 5):
    for n in range(2*k+1, 3*k):
        Theta = comb(n, k)*k**(k-2)*Aget(n-k, k-1)
        FL = sum(comb(n, t)*(bT(t, k)-bT(t, k-1))*Aget(n-t, k-1) for t in range(k+1, 2*k+2))
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
        KD = sum(comb(n, m+1)*p(n-1-m)*k*d(m, k) for m in range(2*k+1, n))
        PAIR2 = Fr(0)
        for t1 in range(1, n+1):
            for t2 in range(1, n+1-t1):
                PAIR2 += Fr(factorial(n), factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1, k)*bT(t2, k)+bT(t1, k-1)*bT(t2, k-1))*p(n-t1-t2)
        PAIR = PAIR2/2
        assert PAIR.denominator == 1
        assert d(n, k) == -Theta + FL + BV + KD + int(PAIR), (k, n, d(n, k), -Theta+FL+BV+KD+PAIR)
        print(f"k={k} n={n}: d={d(n,k)}  Theta={Theta} FL={FL} BV={BV} KD={KD} PAIR={int(PAIR)}")
print("2-40 / 2-41 verified for k=2..4")
