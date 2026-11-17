# 검토전체25 R7a: 정리 7:old-6-13 증명의 접합점 수치, 보조정리 7:tail-half·7:pair-loss-bound 수치 재계산
from fractions import Fraction as F
from decimal import Decimal, getcontext
import math
getcontext().prec = 50
J = [(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)]
for K,L in J:
    kap = (1+(L-1)/K)/(2*(1-(L-1)**1.5/(2*K)))
    br = L*L/3 + (8/25)*math.sqrt(2/5)*(21/40)*L**2.5
    print(K,L,'kappa=%.6f'%kap,'bracket=%.3f'%br, 'bracket<K', br<K, 'nhat<1', (L-1)**1.5/(2*K))
print('21/40=',21/40)
# tail-half
print((1+100/10001)**1.5, 1.0151*(2*math.pi)**-0.5)
f=lambda q: 0.04*q**1.5-0.405*(q+math.sqrt(q)-2/3-2/(3*math.sqrt(q)))
print(f(2),f(101), max(f(q) for q in range(2,102)))
# 직접: 0.405*bracket <= q^{3/2}/2
g=lambda q: 0.405*(4/3*(q-1)**1.5+math.sqrt(q-1)-q+2/3)-q**1.5/2
print(max(g(q) for q in range(2,102)))
# pair-loss-bound brute force: 정수 q,q',j, q+q'+j<=L, kappa=21/40
def lhs(q,qp,j,kap):
    return j*(q+qp+kap*(q**1.5+qp**1.5))+((q+kap*q**1.5)*(qp-1)+(qp+kap*qp**1.5)*(q-1))/2
for L in (2,3,5,10,50,58,79,99,102):
    kap=21/40
    m=0;arg=None
    for q in range(1,L):
        for qp in range(1,L-q+1):
            j=L-q-qp
            v=lhs(q,qp,j,kap)
            if v>m: m=v;arg=(q,qp,j)
    rhs=L*L/3+(8*kap/25)*math.sqrt(2/5)*L**2.5
    print(L,m,arg,rhs,m<=rhs)
print(0.4*(0.6)**1.5, (8/25)*math.sqrt(2/5), 0.4*0.8**1.5/math.sqrt(2))
# 비교 수
c=sum(2*k+40-max(20001,2*k+1)+1 for k in range(9981,11100))
d=sum(2*k+102-max(2*k+41,20001)+1 for k in range(9950,12000))
e=1000*(102-59+1)+1000*(102-80+1)+1000*(102-96+1)
print(c,d,e,d+e)
