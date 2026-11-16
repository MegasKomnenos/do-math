from fractions import Fraction as F
import math
lam=F(751,1000); J=8
val=lam**J + F(1,31)*sum(i*lam**(i-1) for i in range(1,J+1)) + F(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print(val); print(float(val))
print(val==F(7309649993107890414228499,15500000000000000000000000))
# E_n omega_n for n=1..5
def p(n): return (n+1)**(n-1) if n>=1 else 1
for n in range(1,7):
    s=sum(F(math.comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    print(n,s,float(s),math.sqrt(n), float(math.sqrt(2/math.pi)*math.sqrt((n+1)*(n+2)/n)))
# tail ratio
print((3/4)**1.5, 3**1.5/8)
# Mellin tail constant check
from math import gamma,pi,sqrt
C=sqrt(1.5)*gamma(1/3)/gamma(5/6)*gamma(2/3)/(sqrt(pi)*gamma(1/6))
print(3*C, 3/sqrt(2*pi))
# E B check
s=1
EB=(1.5)**(-s/2)*gamma(5/6+s/2)/gamma(5/6)*gamma(0.5+s/2)*gamma(2/3)/(gamma(0.5)*gamma(2/3+s/2))
print(EB, sqrt(2/pi)*2/3)
