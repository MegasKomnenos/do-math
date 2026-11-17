from fractions import Fraction as F
from decimal import Decimal, getcontext
import math
getcontext().prec=40
# tail-half constants
r=(1+Decimal(100)/Decimal(10001))**Decimal('1.5')
print("(1+100/10001)^1.5 =",r)
print("1.0151*(2pi)^-1/2 =",Decimal('1.0151')/Decimal(2*math.pi).sqrt())
def h(q):
    q=Decimal(q); return Decimal('0.04')*q**Decimal('1.5')-Decimal('0.405')*(q+q.sqrt()-Decimal(2)/3-Decimal(2)/(3*q.sqrt()))
print("h(2)=",h(2)," h(101)=",h(101))
# direct check: for q in 2..101, k=10000 bound 0.405*[4/3(q-1)^1.5+sqrt(q-1)-q+2/3] <= q^1.5/2 ?
worst=None
for q in range(2,102):
    lhs=0.405*(4/3*(q-1)**1.5+math.sqrt(q-1)-q+2/3); rhs=q**1.5/2
    if worst is None or rhs-lhs<worst[0]: worst=(rhs-lhs,q)
print("min margin q^1.5/2 - 0.405*bracket:",worst)
# exact union-bound value for k=10000, q=2..101: k(1-s)<= (2pi)^-1/2 ((k+q)/(k+1))^1.5 k/(k+1) bracket
worst=None
for q in range(2,102):
    k=10000
    v=(2*math.pi)**-0.5*((k+q)/(k+1))**1.5*k/(k+1)*(4/3*(q-1)**1.5+math.sqrt(q-1)-(q-1)-1/3)
    if worst is None or q**1.5/2-v<worst[0]: worst=(q**1.5/2-v,q)
print("min margin exact:",worst)
# C_{K,L}
for K,L in [(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)]:
    C=(1+(L-1)/K)/(2*(1-(L-1)**1.5/(2*K)))
    br=L**2/3+8/25*math.sqrt(2/5)*21/40*L**2.5
    print(K,L,"C=",C,"bracket=",br)
print("8/25*sqrt(2/5)=",8/25*math.sqrt(2/5)," 2/5*(3/5)^1.5=",2/5*(3/5)**1.5, " (1/sqrt2)(2/5)(4/5)^1.5=",(1/math.sqrt(2))*(2/5)*(4/5)**1.5)
# brute force pair-loss-bound check for L up to 102 with C=21/40 vs closed form
C=21/40
for L in [50,58,79,99,102]:
    mx=0
    for q in range(1,L):
        for qp in range(1,L-q+1):
            j=L-q-qp
            ex=lambda x:x+C*x**1.5
            v=j*(ex(q)+ex(qp))+(ex(q)*(qp-1)+ex(qp)*(q-1))/2
            mx=max(mx,v)
    print("L",L,"brute max",mx,"closed",L**2/3+8/25*math.sqrt(2/5)*C*L**2.5)
# integer strips counts
c=sum(2*k+40-max(20001,2*k+1)+1 for k in range(9981,11100))
d=sum(2*k+102-max(2*k+41,20001)+1 for k in range(9950,12000))+1000*44+1000*23+1000*7
print("counts (가)",c,"(나)+(다)",d)
# k lower bound
print("k>=",math.ceil((20001-102)/2), math.ceil((20001-40)/2))
