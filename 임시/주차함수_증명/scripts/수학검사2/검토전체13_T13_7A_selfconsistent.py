from fractions import Fraction as F
from math import factorial, ceil
def ao(m): return F((m+1)**(m-1), factorial(m))
for L,J,k0,y,A0,B0 in [(F(267,100),25,501,F(13,100),F(14708,10000),F(98505,10**6)),(F(27,10),70,1855,F(2,25),F(25335,10000),F(60259,10**6)),(F(271,100),100,6098,F(11,200),F(27354,10000),F(422,10**4))]:
    m=0
    while ao(m+2)/ao(m+1) < L: m+=1
    jstar=m  # max m with ao(m+1)/ao(m)<L
    # check: ao(jstar+1)/ao(jstar) < L and ao(jstar+2)/ao(jstar+1) >= L
    assert ao(jstar+1)/ao(jstar) < L <= ao(jstar+2)/ao(jstar+1)
    kR=max(2*jstar+2, ceil(L**(jstar+2)/ao(jstar+1)))
    xi=F(1,k0)
    g=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    v=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(float(L), jstar, kR, "g(table)=%.5e"%float(g), "vertex=%.5f"%float(v), float(v)<=float(y), "y k0^2-2k0-1=", float(y*k0*k0-2*k0-1))
