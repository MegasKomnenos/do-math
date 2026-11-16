# S12 검산: D.tilt-sum-small-k 의 유리수 합, D.prop-W-thirteen 의 L(d), R(d)
from fractions import Fraction as F
from math import factorial
from mpmath import mp, mpf, e, factorial as mpfact
mp.dps = 30
def bor_q_sum(k):
    s = F(0)
    for n in range(2, k+2):
        s += F(n**(n-1), factorial(n)) * F(k, k+1)**((k-1)*n)
    return s
for k in (2,3,10,20,42,43,60):
    s = bor_q_sum(k); print(k, float(s), s if k==2 else '')
print("max over 2..60:", max(float(bor_q_sum(k)) for k in range(2,61)))
def eRen(m): return mpf(m)**(m-1)/(e**(m-1)*mpfact(m-1))
k = 3131
for d in range(1, 15):
    L = (k-1)*(eRen(d+1) - mpf(60)*(d+1)/(k+d))
    Rr = 2*(1 + sum(eRen(r+1) + mpf(60)*(r+1)/(k+d) for r in range(1, d)))
    print(d, mp.nstr(L, 6), mp.nstr(Rr, 5), mp.nstr(L-Rr, 5))
