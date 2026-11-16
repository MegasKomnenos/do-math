# -*- coding: utf-8 -*-
"""E12 검산 6: 장6 항목. (1) (6.50)의 L(d),R(d) d=1..14. (2) 기울인 Borel 합 k=2..60 정확 유리수. (3) 16229쌍 수. (4) 정리 U 상수 조립."""
from fractions import Fraction as F
from math import factorial, e, sqrt, pi
def eRen(m): return (m)**(m-1)/(e**(m-1)*factorial(m-1))  # e*Ren(m) = m^{m-1}/(e^{m-1}(m-1)!)
k=3131
for d in range(1,15):
    L=(k-1)*(eRen(d+1)-60*(d+1)/(k+d)); Rr=2*(1+sum(eRen(r+1)+60*(r+1)/(k+d) for r in range(1,d)))
    print(d, round(L,2), round(Rr,2), L>Rr)
mx=0
for kk in range(2,61):
    s=sum(F(n**(n-1),factorial(n))*F(kk,kk+1)**((kk-1)*n) for n in range(2,kk+2))
    if kk in (2,3,10,20,42,43): print(kk, float(s))
    assert s<1
print("all k<=60 sums <1")
print("pairs", sum(int((m**(2/3))/2+1e-9) for m in range(4,701)), [ (m,int(round(m**(2/3),9)//2)) for m in (700,689)])
c=1/sqrt(2*pi)
print("assembly", 3*c*(8.133+10.301*c), 1.5*2.7323*0.8051*c*(17.951+23.462*c))
