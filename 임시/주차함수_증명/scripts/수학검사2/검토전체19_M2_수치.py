from fractions import Fraction as Fr
from decimal import Decimal, getcontext
getcontext().prec=30
l=Decimal(751)/Decimal(1000)
t1=l**8
s1=sum(i*l**(i-1) for i in range(1,9))
s2=sum((i-1)*l**(i-1) for i in range(1,9))
print('lambda^8',t1); print('sum i l^(i-1)',s1,'/31=',s1/31); print('sum (i-1) l^(i-1)',s2,'/1000=',s2/1000)
print('total',t1+s1/31+s2/1000)
print('(3/4)^1.5',Decimal(0.75).sqrt()*Decimal(0.75), '3^1.5/8', Decimal(3).sqrt()*3/8)
# E_n omega_n for n=1..5 exactly
from math import comb
def p(m): return (m+1)**(m-1) if m>=1 else 1
for n in range(1,7):
    s=sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    print(n,s,float(s),'sqrt n',n**0.5, 'bound', (2/3.141592653589793)**0.5*((n+1)*(n+2)/n)**0.5)
# quadratic 9n^2-48n-32 at n=6
print('quad6',9*36-48*6-32)
# lambda bound
print('3/4+3/4000',Fr(3,4)+Fr(3,4000), float(Fr(3,4)+Fr(3,4000)))
# Legendre duplication check
from math import gamma,pi,sqrt
print(gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
