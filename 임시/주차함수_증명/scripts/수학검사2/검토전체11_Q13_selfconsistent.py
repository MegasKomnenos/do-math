from fractions import Fraction as F
from math import factorial, exp, log
def ao(m): return F((m+1)**(m-1), factorial(m)) if m>=1 else F(1)
def jstar(L):
    m=0
    while ao(m+1)/ao(m) < L: m+=1
    return m-1
def kR(L):
    j=jstar(L)
    import math
    v=L**(j+2)/ao(j+1)
    return max(2*j+2, math.ceil(v)), j
for L in (F(267,100),F(27,10),F(271,100)):
    k,j=kR(L); print("L",L,"j*",j,"kR",k)
# three values with rounded table constants
for (k0,y,A0,B0) in ((501,F(13,100),F(14708,10**4),F(98505,10**6)),(1855,F(2,25),F(25335,10**4),F(60259,10**6)),(6098,F(11,200),F(27354,10**4),F(422,10**4))):
    xi=F(1,k0)
    v=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    vert=(3*xi+xi*xi)/2+(1+xi)**2*B0/2
    print(k0, float(v), float(vert), float((3*xi+xi*xi)/2), float((1+xi)**2*B0/2), float(y*k0*k0-2*k0-1))
