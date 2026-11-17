# R2 검산: 2<=n<=15에서 d_{n,k_n}<0 이고 k_n<=j<=n-2 비증가, 16<=n<=82에서 d_{n,k_n}>0; 경계 응답 다항식과 B_{n,k-1}
from math import comb
N = 82
def col(l, N):
    A = [1] + [0]*N
    for n in range(1, N+1):
        A[n] = sum(comb(n-1, j)*min(j+1, l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
cols = [col(l, N) for l in range(N+1)]
def b(n, l): return cols[l][n] - (cols[l-1][n] if l >= 1 else 0)
neg = []; bad = []
for n in range(2, N+1):
    kn = -(-n//2)
    d = b(n, kn) - b(n, kn-1)
    if d < 0:
        neg.append(n)
        if not all(b(n, j) >= b(n, j+1) for j in range(kn, n-1)): bad.append(n)
    if d == 0: print('zero at', n)
print('d<0 at n =', neg, 'bad:', bad)
# 경계 응답 다항식: Gamma^- = p_{k-1} Gamma_r(k-1;n) = K_{n,k}(k-1) - A_{n,k-2}  (k<=n<=2k-1) 을 d = 2E - B 로 간접 확인하지 않고
# Gamma 재귀 자체의 일관성만 본다: Gamma_d(y;n)의 계수 음이 아님
import sympy as sp
y = sp.symbols('y')
p = lambda m: (m+1)**(m-1) if m >= 1 else 1
def Gam(d, n, memo={}):
    if d == 0: return sp.Integer(1)
    key = (d, n)
    if key not in memo:
        memo[key] = sp.expand(comb(n, d)*p(d) + y*sum(comb(n-d+j, j)*p(j)*Gam(d-1-j, n) for j in range(d)))
    return memo[key]
ok = all(c >= 0 for n in range(1, 12) for d in range(0, n) for c in sp.Poly(Gam(d, n), y).all_coeffs())
print('Gamma coeffs nonneg (n<=11):', ok)
# Gamma^- = B_{n,k-1}: B via d_{n,k} = 2E_{n,k} - B 는 E를 모르므로, 5A의 등식 Gamma^- = K_{n,k}(k-1) - A_{n,k-2} 를 무차별 대입으로 확인 (n<=7)
from itertools import permutations
def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i-1
        while j >= 0 and sig[j] < sig[i]: j -= 1
        h.append(i-j if j >= 0 else i+1)
    return h
for n in range(2, 8):
    perms = [caps(s) for s in permutations(range(n))]
    for k in range(1, n+1):
        if not (k <= n <= 2*k-1): continue
        Kval = sum(sp.prod([hh if hh <= k else (k-1) for hh in h]) for h in perms)
        Akm2 = cols[k-2][n] if k >= 2 else 0
        Gm = p(k-1)*Gam(n-k, n).subs(y, k-1)
        if Kval - Akm2 != Gm: print('MISMATCH', n, k, Kval-Akm2, Gm)
print('Gamma^- check done')
