# 검토전체24 R9: 정리 9:old-8-28의 첫 식(수준 질량의 사슬 표현)과 pi^two, 갱신 다리 식의 정확 유리수 검산
from fractions import Fraction as F
from math import comb, factorial
from functools import lru_cache

@lru_cache(None)
def A(m, l):
    if m == 0: return 1
    if l < 0: return 0
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))
def p(m): return F(m+1)**(m-1) if m >= 1 else F(1)
def s(m, y): return F(A(m, y-1))/p(m)
def c(m, l): return F(A(m, l)-A(m, l-1))/p(m)
def B(m): return F(m**(m-1), factorial(m))   # Bor(m) e^m
def tr(y, q, q2): return B(q-q2)*B(y+q2)/B(y+q)          # Pr^y(q -> q')
ok = 0
for k in range(2, 9):
    y = k+1
    th = F(1, y)
    S = {}; H = {}
    for q in range(1, y+3):
        tot = sum(tr(y, q, q2) for q2 in range(1, q))
        pi0 = 1-tot
        S[q] = pi0 + sum(tr(y, q, q2)*F(y, y+q2)*S[q2] for q2 in range(1, q))
        assert S[q] == s(y+q-1, y), ("chain recursion", k, q)
        if q <= y:
            pich = B(y)*B(q)/B(y+q)                        # pi_{y+q-1}(y)
            assert pich <= pi0
            H[q] = (pi0-pich) + pich*(1-th) + sum(tr(y, q, q2)*F(y, y+q2)*(1-th)*H[q2] for q2 in range(1, q))
            # c_{k+q0}(k) = E[Pi (1-(1-1/y)^{L+1ch})] = S - H
            assert S[q]-H[q] == c(k+q, k), ("chain repr", k, q)
            ok += 1
    # pi^two
    for nu in range(2, k):
        N = k+nu
        lhs = F(comb(N-1, k)*k**(k-1)*(nu-1)**max(nu-2, 0), N**(N-2))
        assert lhs == B(k)*B(nu-1)*B(1)/B(N), ("pi two", k, nu)
        assert lhs <= s(N-1, k)
print("사슬 재귀·사슬 표현·pi^two 통과:", ok)
