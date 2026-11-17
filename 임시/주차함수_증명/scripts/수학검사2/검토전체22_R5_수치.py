# 검토 22차 R5: 장6의 수치 상수 재계산 (mpmath 없이 decimal/float)
from math import *
from fractions import Fraction
from decimal import Decimal, getcontext
getcontext().prec = 40
pi2 = (2*pi)**-0.5
print("== 6.1 ==")
print("2/sqrt(pi)", 2/sqrt(pi))
print("(1.15*2000)^(2/3)", (1.15*2000)**(2/3))
def coef(chi,q=175):
    return 2*pi2*(0.25*(1-1/(2*q))**-1.5 + (1+chi+chi*chi)*(1-chi)**-0.5*(1+chi)**-1.5)
for chi in (0.9,0.99,0.9999):
    print("coef",chi,coef(chi))
print("Mn(0.9)",2*pi2*3*sqrt(1-0.81),"Mn(0.99)",2*pi2*3*sqrt(1-0.99**2))
print("1.1284+2.82/175",1.1284+2.82/175,"9.3/175",9.3/175,"85/175",85/175)
print("1-0.9999^3",1-0.9999**3, "gain(0.02)",0.98**-1.5-1, "1.28/sqrt50",1.28/sqrt(50), "2pi2*sqrt(50/.77)",2*pi2*sqrt(50/0.77))
# tau_1
f=lambda t:(1-t)**2.5-1+2*t
lo,hi=0.1,0.5
for _ in range(80):
    mid=(lo+hi)/2
    if f(mid)<0: lo=mid
    else: hi=mid
print("tau_1",lo)
print("== 6.2 ==")
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)",B2(43),"B2(2000)",B2(2000),"1-B2(2000)",1-B2(2000))
print("== 6.4 ==")
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def ub(k): return 1.15/0.35*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(2001)",u(2001),"ub(2001)",ub(2001),"u(10001)",u(10001),"ub(6667)",ub(6667))
wp=lambda n:1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
print("wp(20000)",wp(20000), "(4002)^(2/3)",4002**(2/3), "9*(1.5)^1.5",9*1.5**1.5, "16.54*4/3",16.54*4/3)
print("== 6.5 ==")
print("3*1.3752/sqrt(pi)",3*1.3752/sqrt(pi),"21/(5sqrt(pi))",21/(5*sqrt(pi)))
print("1.3778^2(1+2/2001)^2/6",1.3778**2*(1+2/2001)**2/6)
print("crit const",(1+1/2001)*(1+2/2001)/(1-3/(4*2001))*1.3752, "0.5(e^{3/(2k)}+1)",0.5*(exp(3/4002)+1))
print("7(3-log3)+42/sqrt3",7*(3-log(3))+42/sqrt(3))
def DDLn(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k))+37.6/(5*sqrt(pi)*k)
for k in (2001,6667,6668,8065,9551,9705): print("DDLnat",k,DDLn(k))
def v(k): return 2-4.6/sqrt(k+1)-2*ub(k)-0.5*DDLn(k)
for k in (2001,6667): print("v",k,v(k),"parts",4.6/sqrt(k+1),2*ub(k),0.5*DDLn(k))
print("== 6.6 ==")
eps=2001**(-1/3); Dbar=3*eps/(6-2*eps)
print("eps",eps,"Dbar",Dbar)
UB=pi2*(1+Dbar)**1.5*(4/3*(3/(6-2*eps))**1.5+sqrt(Dbar)*eps**1.5)
sbar=lambda k:1.15*sqrt(2)*(3*k-1)*k**-1.5
print("UB(2001)",UB,"sbar(2001)",sbar(2001),"4000/6002",4000/6002)
print("final",4000/6002*(1-UB-sbar(2001))-ub(2001), "with rounded",0.6664*(1-0.2099-0.1091)-0.2808)
dd=lambda k:1/e+u(k)/(e*2**1.5)
print("d(2001)",dd(2001),"d(10001)",dd(10001),"u/(e2^1.5)",u(2001)/(e*2**1.5),u(10001)/(e*2**1.5))
def Low(k,rho):
    ep=k**(-1/3)
    br=pi2*(2*sqrt(rho)-2.218*ep)
    return k**(1/3)*br/(1+rho*ep)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*ep)**1.5*exp(1/(4*(k+1)))/br)
print("Low(10001,1.4)",Low(10001,1.4),"Low(2001,0.75)",Low(2001,0.75))
k=10001
print("Obar far (with +1/k)",dd(k)*exp(1+1/(12*k))*(1+1.4*k**(-1/3)+1/k)**1.5, "(without)",dd(k)*exp(1+1/(12*k))*(1+1.4*k**(-1/3))**1.5)
k=2001
print("Obar small",dd(k)*exp(1+1/(12*k))*(1+0.75*k**(-1/3)+1/k)**1.5)
print("B=2.218eps",2.218*eps,"R(1/2)",0.75-2*0.1761*0.5**1.5-2*pi2*sqrt(0.5)+pi2*0.1761)
uu=2001**(1/3)
print("u",uu,"quad",0.15037*uu**2-1.54829*uu-1.3365,"root",(1.54829+sqrt(1.54829**2+4*0.15037*1.3365))/(2*0.15037))
print("direct (6.45) diff",0.75*2001**(2/3)-(wp(2001+0.75*2001**(2/3))-1))
print("1.30212+0.39976/u+0.41616/u^2",1.30212+0.39976/12.601+0.41616/12.601**2)
print("10*10001^(2/3)",10*10001**(2/3),"10/2^(2/3)",10/2**(2/3), "1.4*10001^(2/3)",1.4*10001**(2/3))
print("2+2.61238/12",2+2.61238/12)
