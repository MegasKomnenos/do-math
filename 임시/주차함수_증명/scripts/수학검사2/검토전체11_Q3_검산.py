from mpmath import mp, mpf, quad, exp, sqrt, pi, log, e, findroot, cot, sin
from fractions import Fraction as F
import math
mp.dps=30
# counts
c2=sum((n+1)//2 -1 for n in range(10001,20001)); print("둘째 조각 비교수",c2)
c4=sum(n-2-math.ceil((n-1)/2) for n in range(5,20001)); print("넷째 조각 위치수",c4)
c50=sum(n-2-math.ceil((n-1)/2) for n in range(20001,50001)); print("c50 위치수",c50)
pairs50=sum(n-1-math.ceil((n-1)/2) for n in range(20001,50001)); print("c50 인접쌍",pairs50)
pairs20=sum(n-1-math.ceil((n-1)/2) for n in range(5,20001)); print("재인증 인접쌍",pairs20)
print("14365:",sum(r-1 for r in range(2,171)), "9829:",9999-171+1)
# m(n)
def mfun(n):
    m=170
    for mm in range(171,100000):
        if mm**1.5+9*mm<=n: m=mm
        else: break
    return m
print("m(20001)",mfun(20001),"m(50001)",mfun(50001)); print("597^1.5+9*597",597**1.5+9*597)
# lemma L constants
G=lambda i: quad(lambda y: y**i*exp(-y-y*y/2),[0,mp.inf])
M=[G(i) for i in range(6)]; M26=quad(lambda y: y**2*exp(-y-y*y/2),[0,6])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y^2+y-i=0
    y=(-1+sqrt(1+4*i))/2; return y**i*exp(-y-y*y/2)
Ms={i:Mstar(i) for i in range(2,6)}
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
print("M",[mp.nstr(x,6) for x in M],"M2(6)",mp.nstr(M26,6)); print("C",mp.nstr(C1,6),mp.nstr(C2,6),mp.nstr(C3,6),mp.nstr(C4,6))
def Lr(r):
    s=sqrt(r); st=1/s
    return (M26-st*C1-st**2*C2-st**3*C3-st**4*C4)/(M[1]+st*(M[0]+exp(-mpf(1)/2))+st**2)
print("L(1e4)",mp.nstr(Lr(10**4),8),"L(2e4)",mp.nstr(Lr(2*10**4),6),"L(1e5)",mp.nstr(Lr(10**5),6))
print("sqrt(3pi/2)",mp.nstr(sqrt(3*pi/2),8), "0.5+2*0.845204-sqrt",mp.nstr(mpf('0.5')+2*mpf('0.845204')-sqrt(3*pi/2),8))
s=mpf(100); print("bracket at s=100",mp.nstr(1/(3*s)+8/(3*s*s)+mpf('2.507')/s**2+(1+mpf('2.1709')*s)/s**3,6))
# Cayley lemma expansion check with sympy
import sympy as sp
t=sp.symbols('t')
expr=sp.expand((2+sp.Rational(5,2)*t+2*t**2)*(-sp.Rational(5,2)*t+sp.Rational(4,3)*t**2-sp.Rational(11,12)*t**3+sp.Rational(1,2)*t**4)+5*t+4*t**2)
print("cayley poly:",expr, " claimed:", sp.expand(t**2*(sp.Rational(5,12)-sp.Rational(7,2)*t+sp.Rational(11,8)*t**2-sp.Rational(7,12)*t**3+t**4)))
print("(1/t-2)*(t - t^2/2 + t^3/3 - t^4/4) =",sp.expand((1/t-2)*(t-t**2/2+t**3/3-t**4/4)))
for k in range(1,10):
    v=F(k+1,k)**(k-2)*(1+F(5,2*k)+F(2,k*k)); print(k, float(v), end=" | ")
print(); print("e vs 65/24+1/100 vs 87/32:", math.e, 65/24+0.01, 87/32)
print("bracket min at theta=0.1:", 5/12-7/20+0.01*(11/8-7/12*0.1)+1e-4, ">=1/15?",1/15)
# et(1/2)
phi=mpf(1)/2; et=e*phi*exp(-phi*cot(phi))/sin(phi); print("log et(1/2)",mp.nstr(log(et),6))
# 5-11 constants
print("20001^(2/3)",20001**(2/3),"27.14^3",27.14**3,"(149/200)^3",(149/200)**3,"(16/25)^2",0.64**2,"(3/4)^3",0.75**3,"(13/20)^2",0.65**2)
print("0.64^(2/3),0.65^(2/3)",0.64**(2/3),0.65**(2/3))
print("1/(1+9/sqrt598)",1/(1+9/math.sqrt(598)), "(1.2*20001)^(2/3)",(1.2*20001)**(2/3), "(1.5*20001)^(2/3)",(1.5*20001)**(2/3))
print("rq vals",1.2/math.sqrt(598),1.5/math.sqrt(833),1.8/math.sqrt(966),2.1/math.sqrt(2164),2.4/100, "1/16",1/16)
print("rq*",0.65*(1+3/529)/23, "1/12",1/12)
print("(12/11)^1.5*(1+1/598)",(12/11)**1.5*(1+1/598),"12/(110e)",12/(110*math.e),"1/24",1/24)
print("log10(1.15*598^3)",math.log10(1.15*598**3),"598*log10(24)",598*math.log10(24))
print("2.4*(1+1/598)/sqrt598",2.4*(1+1/598)/math.sqrt(598))
print("(9/5)^(2/3)",1.8**(2/3),"10*(0.5)^(2/3)",10*0.5**(2/3))
print("2sqrt2/e",2*math.sqrt(2)/math.e,"181/174",181/174)
print("1-cos1",1-math.cos(1))
print("10001^(-1/3)",10001**(-1/3),"0.0015/1.25^12",0.0015/1.25**12)
print("142:",2*math.ceil(142**2/4),"141:",2*math.ceil(141**2/4))
