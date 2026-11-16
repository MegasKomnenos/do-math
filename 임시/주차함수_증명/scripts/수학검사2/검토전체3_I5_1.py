# I5 검산 1: 6.1 (6.8) 수치, 6.2 tilt-sum B_2 수치와 k=2..42 정확 합
from fractions import Fraction as Fr
from math import e, sqrt, pi, exp, log, factorial, ceil
C=3; k=4000
qs=ceil((C*k)**(2/3)); print("q*=",qs, (C*k)**(2/3))
print("LHS 1-1.6/sqrt(525)=",1-1.6/sqrt(525))
t1=0.8*sqrt(2)/3*(1+1/(2*524)); t2=(1.212+1.203+1.508)*3**(-4/3)*4000**(-1/3); t3=1.5/(3*sqrt(525))
print("bracket terms",t1,t2,t3,t1+t2+t3, 2*(t1+t2+t3))
print("1.2(1-2/525)^-2.5=",1.2*(1-2/525)**-2.5, "1.2(1+2/525)^.5=",1.2*(1+2/525)**.5, "1.5(1-1/525)^-2.5=",1.5*(1-1/525)**-2.5)
print("2/sqrt(2pi)=",2/sqrt(2*pi))
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)=",B2(43),"B2(2000)=",B2(2000), exp(1.5+1/43)-1, 2*(sqrt(44)-1), sqrt(2*pi)*44, exp(1.5+1/2000)-1, 2*(sqrt(2001)-1), sqrt(2*pi)*2001)
# exact: sum_{n=2}^{k+1} Bor(n) q^n with q = e x_k ; Bor(n) q^n = e^{-n} n^{n-1}/n! e^n x_k^n = n^{n-1} x_k^n / n!
mx=0
for k in range(2,43):
    xk=Fr(k,k+1)**(k-1)
    s=sum(Fr(n**(n-1),factorial(n))*xk**n for n in range(2,k+2))
    if s>=1: print("FAIL",k,float(s))
    mx=max(mx,s)
    if k in (2,3,42): print(k,s if k==2 else float(s))
print("max over 2..42 =",mx,float(mx))
