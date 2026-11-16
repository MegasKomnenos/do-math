# 보조정리 tilt-sum: 2<=k<=42에서 sum_{n=2}^{k+1} Bor(n) q^n <1 (q = e x_k) 를 유리수+고정밀 e로 확인
from fractions import Fraction
from decimal import Decimal, getcontext
getcontext().prec = 60
import math
E = Decimal(1).exp()
mx = None
for k in range(2, 43):
    xk = Fraction(k, k+1)**(k-1)
    # sum Bor(n) q^n = sum e^{-n} n^{n-1}/n! * e^n xk^n = sum n^{n-1}/n! xk^n  (e cancels!)
    s = sum(Fraction(n**(n-1), math.factorial(n)) * xk**n for n in range(2, k+2))
    if mx is None or s > mx[1]: mx = (k, s)
    print(k, float(s), s < 1)
print("max", mx[0], mx[1], float(mx[1]))
