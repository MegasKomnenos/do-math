# R2 검산: 4.2절 경계 응답 다항식 정의식이 5장의 쓰임(Γ^- = B_{n,k-1}, d_{n,k}=2E-Γ^-)과 맞는지 (작은 n 전수)
import itertools
from math import comb
def p(n): return 1 if n == 0 else (n+1)**(n-1)
def Gam(d, y, n, memo={}):
    key = (d, y, n)
    if key in memo: return memo[key]
    if d == 0: return 1
    v = comb(n, d)*p(d) + y*sum(comb(n-d+j, j)*p(j)*Gam(d-1-j, y, n) for j in range(d))
    memo[key] = v; return v
def Jb(n, k, z):
    tot = 0
    for sigma in itertools.permutations(range(1, n+1)):
        h = []
        for i in range(1, n+1):
            js = [j for j in range(1, i) if sigma[j-1] > sigma[i-1]]
            h.append(i - (max(js) if js else 0))
        H = sum(1 for v in h if v == k); Z = sum(1 for v in h if v > k)
        if H == 0: continue
        pr = 1
        for v in h:
            if v < k: pr *= v
        tot += H*k**(H-1)*z**Z*pr
    return tot
for (n, k) in [(5, 3), (6, 4), (7, 4), (7, 5), (8, 5), (8, 6)]:
    r = n - k
    print(n, k, "Gamma^- =", p(k-1)*Gam(r, k-1, n), " J_n(k-1) =", Jb(n, k, k-1))
