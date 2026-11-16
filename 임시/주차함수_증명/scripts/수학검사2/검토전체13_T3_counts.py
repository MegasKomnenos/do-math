from fractions import Fraction
from math import ceil, e, factorial
# 5.1 counts
c2 = sum(ceil(n/2)-1 for n in range(10001,20001))
print("둘째 조각 비교 수", c2)
c4 = sum(n-3-ceil((n-1)/2)+1 for n in range(5,20001))
print("넷째 조각 위치 수", c4, 94192042+5777960)
c52 = sum(n-3-ceil((n-1)/2)+1 for n in range(20001,50001))
print("정리5-2 위치 수", c52)
# k thresholds
for k in (141,142): print(k, 2*ceil(k*k/4))
# cayley ratio values
for k in range(1,10):
    cr = Fraction(k+1,k)**(k-2)
    v = cr*(1+Fraction(5,2*k)+Fraction(2,k*k))
    print(k, float(v), v>Fraction(87,32))
print("e<65/24+1/100", e<65/24+1/100, 65/24+1/100, 87/32)
print("14365", sum(r-1 for r in range(2,171)))
# max m with m^1.5+9m<=n for n=20001
import math
for n in (20001,50000):
    m=171
    while (m+1)**1.5+9*(m+1)<=n: m+=1
    print(n, m)
