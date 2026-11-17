# 검토전체25 R9: 정리 9:old-8-28의 사슬 표현(첫 식)과 9.5절 준비 문단의 사슬 꼴을 작은 용량에서 유리수로 검산
from fractions import Fraction as Fr
from math import comb, factorial

def Acount(l, nmax):
    a = [1]
    for m in range(1, nmax+1):
        a.append(sum(comb(m-1, j-1)*min(j, l+1)*a[j-1]*a[m-j] for j in range(1, m+1)))
    return a
def p(m): return 1 if m == 0 else (m+1)**(m-1)
def borratio(a, b):   # Bor(a)Bor(b)/Bor(a+b)
    return Fr(a**(a-1)*b**(b-1)*factorial(a+b), factorial(a)*factorial(b)*(a+b)**(a+b-1))

for k in range(2, 9):
    y = k+1
    A = {l: Acount(l, 2*y+2) for l in (k-1, k)}
    s = lambda m, yy: Fr(A[yy-1][m], p(m))
    # 용량 y 사슬: S[q] = E^y[Pi_L], F[q] = E^y[Pi_L (1-1/y)^(L+1ch)], G[q] = E^y[Pi_L (L+1ch)]
    S = {1: Fr(1)}; F = {}; G = {}
    for q in range(1, y+1):
        tr = {q1: borratio(q-q1, y+q1) for q1 in range(1, q)}       # Pr^y(q->q1)
        stop = 1-sum(tr.values())                                   # pi^0_{y+q-1}(y)
        ch = borratio(y, q)                                         # 끝나면서 크기 y인 자식이 있을 확률
        assert 0 <= ch <= stop
        S[q] = stop+sum(tr[q1]*Fr(y, y+q1)*S[q1] for q1 in tr)
        F[q] = (stop-ch)+ch*(1-Fr(1, y))+sum(tr[q1]*Fr(y, y+q1)*(1-Fr(1, y))*F[q1] for q1 in tr)
        G[q] = ch+sum(tr[q1]*Fr(y, y+q1)*(S[q1]+G[q1]) for q1 in tr)
        assert S[q] == s(y+q-1, y), ("S", k, q)
        c = s(k+q, k+1)-s(k+q, k)
        assert S[q]-F[q] == c, ("P", k, q)
        assert k*c >= Fr(y-1, y)*(1-Fr(q, 2*y))*G[q], ("P-ineq", k, q)
    print("k=%d: 사슬 표현 통과 (q0<=%d)" % (k, y))
