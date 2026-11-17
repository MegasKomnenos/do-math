# 검토전체23 R7b: n>=3k+1에서 inh_k(n) 자신의 부호와 inh^lin+inh=2Left의 부호를 본다(정확 유리수)
from fractions import Fraction as F
from math import comb
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)
@lru_cache(None)
def A(m, l):
    if m == 0: return 1
    if l < 0: return 0
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))
def p(m): return (m+1)**(m-1) if m >= 1 else 1
def b(m, l): return A(m, l) - A(m, l-1)
def w(m, n, k): return F(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
for k in (3, 5, 8, 12, 20, 30):
    for n in (3*k+1, 4*k, 6*k):
        # inh = 2*sum_m k w_m d_{m,k}/p_m ; inhlin = 2*sum_m w_m (b_{m,k}+b_{m,k-1})/p_m
        inh = 2*sum(k*w(m, n, k)*F(b(m, k)-b(m, k-1), p(m)) for m in range(k, 2*k+1))
        lin = 2*sum(w(m, n, k)*F(b(m, k)+b(m, k-1), p(m)) for m in range(k, 2*k+1))
        left2 = 2*sum(w(m, n, k)*F((k+1)*b(m, k)-(k-1)*b(m, k-1), p(m)) for m in range(k, 2*k+1))
        assert inh+lin == left2
        print(k, n, "inh=%.4e" % float(inh), "inhlin=%.4e" % float(lin), "2Left=%.4e" % float(left2))
