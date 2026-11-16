# -*- coding: utf-8 -*-
# 6.1-6.3절 상수 재계산
from mpmath import mp, mpf, sqrt, exp, log, pi, e, ceil, quad, factorial, power
mp.dps = 30
c = 1/sqrt(2*pi)
print("== 6.1 ==")
print("2c=", 2*c, "<=0.8", 2*c<=mpf('0.8')); print("3c=",3*c,"<=1.2",3*c<=mpf('1.2'))
print("q*=ceil(12000^(2/3))=", ceil(mpf(12000)**(mpf(2)/3)), 12000**(2/3))
print("1-1.6/sqrt525=", 1-mpf('1.6')/sqrt(525), ">=0.9301", 1-mpf('1.6')/sqrt(525)>=mpf('0.9301'))
print("1.2(1-2/525)^-2.5=", mpf('1.2')*(1-mpf(2)/525)**(-mpf(5)/2), "<=1.212")
print("1.2(1+2/525)^0.5=", mpf('1.2')*(1+mpf(2)/525)**mpf('0.5'), "<=1.203")
print("1.5(1-1/525)^-2.5=", mpf('1.5')*(1-mpf(1)/525)**(-mpf(5)/2), "<=1.508")
print("1.2 sqrt(q*+1)/q* vs 1.5/sqrt(q*) at 525:", mpf('1.2')*sqrt(526)/525, mpf('1.5')/sqrt(525))
print("0.8*sqrt2/3=", mpf('0.8')*sqrt(2)/3, "<=0.3772")
print("0.3772*(1+1/1048)=", mpf('0.3772')*(1+mpf(1)/1048), "<=0.3775")
print("3.923*3^(-4/3)*4000^(-1/3)=", mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3), "<=0.0572")
print("1.5/(3 sqrt525)=", mpf('1.5')/(3*sqrt(525)), "<=0.0219")
print("sum=", mpf('0.3775')+mpf('0.0572')+mpf('0.0219'), "2*0.4566=", 2*mpf('0.4566'))
print("Up(1/2)=", sqrt(mpf(1)/2)*2)
# (6.7): 1.2 * (2sqrt2/3) = 0.8 sqrt2 check; 1/(q-1) = (q/(q-1))/q -> q^{3/2} U^{-1/2} q*^{-3/2} <= (q/(q-1))^{1/2} q/(Ck)
print("1.2*2*sqrt2/3=", mpf('1.2')*2*sqrt(2)/3, "0.8sqrt2=", mpf('0.8')*sqrt(2))
# 2(k+1)/(k-2)? none. 6.1 ends.
print("== 6.2 ==")
def B2(k):
    k=mpf(k); return (1-1/e)+(exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
for k in (42,43,2000):
    print("B2(%d)="%k, B2(k))
print("pieces k=43: 1-1/e=",1-1/e," e^{3/2+1/43}-1=",exp(mpf(3)/2+mpf(1)/43)-1," 2(sqrt44-1)=",2*(sqrt(44)-1)," sqrt(2pi)*44=",sqrt(2*pi)*44)
print("0.63212+3.5871*11.266/110.29=", mpf('0.63212')+mpf('3.5871')*mpf('11.266')/mpf('110.29'))
print("pieces k=2000: e^{3/2+1/2000}-1=",exp(mpf(3)/2+mpf(1)/2000)-1," 2(sqrt2001-1)=",2*(sqrt(2001)-1)," sqrt(2pi)*2001=",sqrt(2*pi)*2001)
print("0.63212+3.4838*87.466/5015.8=", mpf('0.63212')+mpf('3.4838')*mpf('87.466')/mpf('5015.8'))
print("1-B2(2000)=",1-B2(2000),">=0.307",1-B2(2000)>=mpf('0.307'))
# upward-rounded pieces
up = lambda x,n: ceil(x*10**n)/mpf(10**n)
for k in (43,2000):
    k=mpf(k)
    a=up(1-1/e,5); b=up(exp(mpf(3)/2+1/k)-1,4); cc=up(2*(sqrt(k+1)-1),3); dd=sqrt(2*pi)*(k+1)
    print("k=",k," upper pieces:",a,b,cc," floor denom:", dd, " val=", a+b*cc/( (int(dd*100))/mpf(100) ))
# exact tilt sum small k
from fractions import Fraction
from math import factorial as fct
def tiltsum(k):
    s=Fraction(0)
    for n in range(2,k+2):
        bor_q = Fraction(n**(n-1), fct(n)) * Fraction(k, k+1)**((k-1)*n)
        s+=bor_q
    return s
for k in (2,3,10,20,42,43):
    v=tiltsum(k); print("tiltsum k=%d:"%k, float(v), "<1", v<1)
# g(k) bounds
g=lambda k:(k-1)*log(1+1/mpf(k))
for k in (2,5,50,3131):
    print("k=",k,"g=",g(k),"lower 1-3/2k+1/2k^2=",1-mpf(3)/(2*k)+1/(2*mpf(k)**2),"upper 1-3/2k+5/6k^2=",1-mpf(3)/(2*k)+mpf(5)/(6*mpf(k)**2))
print("(k+1)(3/2k-1/2k^2)=3/2+1/k-1/2k^2 check k=5:", 6*(mpf(3)/10-mpf(1)/50), mpf(3)/2+mpf(1)/5-mpf(1)/50)
print("5/6+9/8=", mpf(5)/6+mpf(9)/8, "47/24=", mpf(47)/24)
# (나): 5/(3j^3)+1/(4j^4) <= 1.8/j^3 for j>=2
print("5/3+1/(4*2)=", mpf(5)/3+mpf(1)/8, "<=1.8")
# g'(j) series check numerically
for j in (2,5,100):
    j=mpf(j); gp=log(1+1/j)-(j-1)/(j*(j+1)); print("j=",j,"g'=",gp," 3/2j^2-5/3j^3-1/4j^4=",mpf(3)/(2*j**2)-mpf(5)/(3*j**3)-1/(4*j**4), gp>=mpf(3)/(2*j**2)-mpf(5)/(3*j**3)-1/(4*j**4))
# k(1-g(k)) <= 3k/(2k+1)
for k in (2,10,2000):
    k=mpf(k); print("k(1-g)=",k*(1-g(k)),"3k/(2k+1)=",3*k/(2*k+1))
print("== 6.3 ==")
X=(5-sqrt(7))/6; print("X*=",X," max=",X*(1-X)*(3-2*X)," (10+7sqrt7)/54=",(10+7*sqrt(7))/54)
# 3/2 Y(X) = X(1-X)(3-2X) identity check
I5=lambda X: mpf(2)/3*sqrt(X)*(1-X)**(-mpf(3)/2)+mpf(4)/3*sqrt(X)*(1-X)**(-mpf(1)/2)
for X0 in (mpf('0.1'),mpf('0.3'),mpf('0.5')):
    Yv=sqrt(X0)*(1-X0)**(mpf(5)/2)*I5(X0); print("X=",X0," 3/2Y=",1.5*Yv," X(1-X)(3-2X)=",X0*(1-X0)*(3-2*X0), " I5 num=", quad(lambda v: v**-0.5*(1-v)**-2.5,[0,X0]), I5(X0))
y=mpf(50)
print("tl^-1 <= 1/(1-3/(4*51))=", 1/(1-mpf(3)/(4*51)))
print("e^{1/24+1/612}=",exp(mpf(1)/24+mpf(1)/612),"<=1.0443")
print("1+1/51=",1+mpf(1)/51,"<=1.01961")
print("u<=1.0443*1.0150*1.01961*4/3=",mpf('1.0443')*mpf('1.0150')*mpf('1.01961')*4/3,"<=1.449")
print("0.5282*1.449=",mpf('0.5282')*mpf('1.449'),"<=0.766")
print("L/G V>=2: 1.5/53*(4/3)*(1/2)*1.01961*1.0150=",mpf('1.5')/53*mpf(4)/3/2*mpf('1.01961')*mpf('1.0150'),"<=0.020")
print("L/G V=1: 1.5/52*2.02*0.51*1.01961*1.0150=",mpf('1.5')/52*mpf('2.02')*mpf('0.51')*mpf('1.01961')*mpf('1.0150'),"<=0.031")
print("(2y+1)/y y=50:",mpf(101)/50," (y+1)/(2y+1)=",mpf(51)/101)
print("1-0.766-0.020=",1-mpf('0.766')-mpf('0.020'))
# lemma-phi: y>=10, 3/4 y^2 >= 6(y+1)
print("3/4*100=75 >= 66", 75>=66, " tl_1>=1-3/(4*11)=",1-mpf(3)/44,">=0.93")
# d=2: e^{3/(2*51)}
print("e^{3/102}=",exp(mpf(3)/102),"<=1.03")
print("e^-2=",exp(-2)," 1.545 e^-1=",mpf('1.545')*exp(-1))
print("2y+2 >= 4.2 => 0.1353*(102)-0.5684=",mpf('0.1353')*102-mpf('0.5684'))
# d=3 case
print("1.2 check: 2*1.5*1.03/e=", 2*mpf('1.5')*mpf('1.03')/e)
print("0.2/e=",mpf('0.2')/e)
print("2e^-2+e^-1-1.03e^-2/51=",2*exp(-2)+exp(-1)-mpf('1.03')*exp(-2)/51, " need >=0.6*(y+2)/(y+3) y=50:", mpf('0.6')*52/53)
print("0.2 e^-1 *0.6=", mpf('0.2')*exp(-1)*mpf('0.6'), "<=0.0441?")
# 0.0441 (y-1)/(y+3)^2 vs 1.8 * 1.2 (y+1)/((y+2)^2(y+3)) at y=50
y=mpf(50); lhs=mpf('0.0441')*(y-1)/(y+3)**2; rhs=mpf('1.2')*(y+1)/((y+2)**2*(y+3)); print("ratio at y=50:",lhs/rhs)
for y in (50,51,60,100,1000):
    y=mpf(y); print("y",y,"ratio",mpf('0.0441')*(y-1)/(y+3)**2/(mpf('1.2')*(y+1)/((y+2)**2*(y+3))))
print("d=y+2: e^{-1+3/102}/(2*51)=",exp(-1+mpf(3)/102)/102," 1/(5*51)=",mpf(1)/255)
# Cv(2)=(y^2+y+2)/(y+2) check
y=mpf(50); d=3; q=2
Cv=(d-1)*(y+1)-(q-1)*y*(y+1+q)/(y+q)-(y+1)*q/(y+q); print("Cv(2)=",Cv,"(y^2+y+2)/(y+2)=",(y*y+y+2)/(y+2))
print("Cs(2)=",(d-1)-(y+1)*q/(y+q)," 2/(y+2)=",2/(y+2))
