# R2 검산: 경계 다항식 J_n(k-1)의 재귀(부록 D.central-gap-integer의 넷째 재귀)와 정의식 전수 비교
import itertools
from math import comb
def p(n): return 1 if n == 0 else (n+1)**(n-1)
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
def Jrec(N, k, yv):
    J = [0]*(N+1)
    for n in range(k, N+1):
        s = sum(comb(n-1, i)*(yv+i+1)*p(i)*J[n-1-i] for i in range(n) if n-1-i >= k)
        J[n] = s + comb(n-1, k-1)*p(k-1)*p(n-k)
    return J
for k in (2, 3, 4):
    J = Jrec(min(2*k+1, 8), k, k-1)
    print(k, [(n, J[n] == Jb(n, k, k-1)) for n in range(k, min(2*k+1, 8)+1)])
