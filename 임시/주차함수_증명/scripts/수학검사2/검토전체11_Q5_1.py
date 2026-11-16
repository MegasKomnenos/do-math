# Q5 검산 1: 6.1–6.4 앞부분의 수치
from fractions import Fraction as Fr
from math import exp, log, sqrt, pi, e, ceil, factorial

# (6.8) 상수
C=3; k=4000
qs=ceil((C*k)**(2/3)); print("q*(4000)=",qs, (C*k)**(2/3))
lhs=1-1.6/sqrt(525)+0.8/525; print("lhs(525)=",1-1.6/sqrt(525), lhs)
b1=0.8*sqrt(2)/3*(1+1/(2*524)); b2=3.923*3**(-4/3)*4000**(-1/3); b3=1.5/(3*sqrt(525))
print("bracket terms",b1,b2,b3,b1+b2+b3, 2*(b1+b2+b3))
print("1.2(1-2/525)^-2.5=",1.2*(1-2/525)**-2.5, "1.2(1+2/525)^.5=",1.2*(1+2/525)**0.5, "1.5(1-1/525)^-2.5=",1.5*(1-1/525)**-2.5)
print("(2pi)^-1/2=",(2*pi)**-0.5, "2(2pi)^-1/2=",2*(2*pi)**-0.5)
# B_2
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)=",B2(43),"B2(2000)=",B2(2000),"B2(42)=",B2(42))
# tilt-sum small k exact
def Bor(n): return Fr(n**(n-1),factorial(n))*Fr(1)  # times e^{-n} handled separately
# sum_{n=2}^{k+1} Bor(n) q^n with q=e x_k : Bor(n)q^n = n^{n-1}/n! e^{-n} e^n x_k^n = n^{n-1}/n! x_k^n  (exact rational)
mx=(0,0)
for k in range(2,43):
    x=Fr(k,k+1)**(k-1)
    s=sum(Fr(n**(n-1),factorial(n))*x**n for n in range(2,k+2))
    if s>mx[0]: mx=(s,k)
    assert s<1,(k,s)
print("tilt-sum small k max:",mx, float(mx[0]))
# 1-B2(2000)
print("1-B2(2000)=",1-B2(2000))
# u(3131)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(3131)=",u(3131), (0.65-1/3131)**-1.5, 3131**-0.5)
# witness bound at n=20000
n=20000; print("witness bound 20000:",1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3))
print("(6262)^(2/3)=",6262**(2/3), "0.65*3131-1=",0.65*3131-1, "1.35*3131=",1.35*3131)
# lemma-omega constants
X=(5-sqrt(7))/6; print("X*=",X, X*(1-X)*(3-2*X), (10+7*sqrt(7))/54)
print("tl^-1:",1/(1-0.75/51), "e^(1/24+1/612)=",exp(1/24+1/612), "1+1/51=",1+1/51)
print("u<=",1.0443*1.0150*1.01961*4/3, "M/G<=",0.5282*1.449)
print("L/G V>=2:",1.5/53*4/3*0.5*1.01961*1.0150, " V=1:",1.5/52*2.02*0.51*1.01961*1.0150)
# d=2 case
print("e^-2=",exp(-2),"1.545/e=",1.545/e,"e^(3/102)=",exp(1.5/51))
print("2e^-2+e^-1-1.03e^-2/51=",2*exp(-2)+exp(-1)-1.03*exp(-2)/51, "0.2/e*0.6=",0.2/e*0.6)
y=50; print("ratio d=3 at y=50:",0.0441*(y-1)/(y+3)**2/(1.2*(y+1)/((y+2)**2*(y+3))))
print("1.03/e/2=",1.03/e/2)
# old-8-12 constants
print("9*(1.5)^1.5=",9*1.5**1.5, 16.54*4/3)
print("1.5*(8001)^(2/3)=",1.5*8001**(2/3), (4601)**(1/3))
