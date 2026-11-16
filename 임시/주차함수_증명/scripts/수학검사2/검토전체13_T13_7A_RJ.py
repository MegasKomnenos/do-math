from mpmath import mp, mpf, e as E, iv
from fractions import Fraction as F
from math import factorial
mp.dps=40
def ao(m): return F((m+1)**(m-1), factorial(m))
for L,J,k0,jstar in [(F(267,100),25,501,82),(F(27,10),70,1855,220),(F(271,100),100,6098,490)]:
    EJ=sum(mpf(ao(J+i).numerator)/ao(J+i).denominator/ (mpf(ao(J).numerator)/ao(J).denominator) * E**(-i) for i in range(1,k0-jstar+1))
    Lf=mpf(L.numerator)/L.denominator
    Einf=(Lf/E)*(1-(Lf/E)**k0)/(1-Lf/E)
    R=max(1/(1+EJ),1/(1+Einf))
    print(float(L), mp.nstr(1/(1+EJ),12), mp.nstr(1/(1+Einf),12), "R=",mp.nstr(R,12))
