# -*- coding: utf-8 -*-
"""D8 검산: DD(7,6) = 8 s_9(8) - 14 s_8(7) + 6 s_7(6) (장10:133의 정의 DD_m := DD(m-1,k-1) = (k+1)s_{m+1}(k+1) - 2k s_m(k) + (k-1)s_{m-1}(k-1), m=8, k=7).
s_m(y) = A_{m,y-1}/p_m, A는 마지막 차 재귀(정리 2.6), p_m=(m+1)^(m-1)."""
from fractions import Fraction as F
from math import comb
N = 40
A = [[0]*(N+2) for _ in range(N+2)]
for l in range(N+2): A[0][l] = 1
for n in range(1, N+1):
    for l in range(N+2):
        A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
p = lambda m: (m+1)**(m-1) if m >= 1 else 1
def s(m, y):
    if y <= 0: return F(0)
    return F(A[m][y-1], p(m))
def DD(nn, kk):  # DD(n,k) with m-1=n, k-1=k  -> m=n+1, K=k+1
    m, K = nn+1, kk+1
    return (K+1)*s(m+1, K+1) - 2*K*s(m, K) + (K-1)*s(m-1, K-1)
v = DD(7, 6)
print('DD(7,6) =', v, '=', float(v))
print('피드백 값 =', F(-2460175598381, 244888012800000000), '=', float(F(-2460175598381, 244888012800000000)))
print('일치:', v == F(-2460175598381, 244888012800000000))
# 다른 읽기: DD(n,k)를 m=n, K=k로 읽으면
def DD2(m, K): return (K+1)*s(m+1, K+1) - 2*K*s(m, K) + (K-1)*s(m-1, K-1)
print('다른 읽기 DD2(7,6) =', DD2(7, 6), float(DD2(7,6)))
# 작은 범위 전수: 음인 자리 (결손 d=m-k+1)
neg = []
for K in range(2, 16):
    for m in range(K+1, 2*K+1):
        val = DD2(m, K)
        if val < 0: neg.append((m, K, m-K+1, float(val)))
print('DD2(m,K)<0 인 (m,K,d=m-K+1):', neg[:30], '총', len(neg))
