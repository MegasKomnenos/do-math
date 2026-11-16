# P10: 10.4-10.6 상수·적분·단조 검산 (배정밀도/mpmath)
import mpmath as mp
mp.mp.dps=30
from math import *
import math
def Bor(m): return mp.e**(-m)*mp.mpf(m)**(m-1)/mp.factorial(m)
def g(x): return (x-1)*mp.log(1+mp.mpf(1)/x)
print("f1=4/(3sqrt(2pi))",4/(3*sqrt(2*pi)))
print("cR=(sqrt(2pi)/2)e^{1/12}",sqrt(2*pi)/2*exp(1/12))
print("3sqrt2*0.16696",3*sqrt(2)*0.16696," 2.5-log2-log0.485917",2.5-log(2)-log(0.485917))
print("(sqrt2*0.16696)^{1/2}",sqrt(sqrt(2)*0.16696))
print("vartheta0",(2*exp(-0.48)-1)*exp(-0.48))
print("2/sqrt(pi)",2/sqrt(pi), " 2(2pi)^{-1/2}sqrt2",2/sqrt(2*pi)*sqrt(2))
print("F at upsilon=0.9:",2/sqrt(2*pi)*(1+2*0.81)*sqrt(1-0.81), " 3*sqrt(0.19)*0.79788",2/sqrt(2*pi)*3*sqrt(0.19))
print("theta1 root of (1-t)^{5/2}-1+2t:",mp.findroot(lambda t:(1-t)**2.5-1+2*t,0.28))
# I(rho) closed form check vs numeric
for rho in [0.1,0.354,0.7,0.95]:
    ups=rho**(1/3); th=1-rho**(2/3)
    x=lambda t: t**-1.5*min(1-rho, rho*((1-t)**-1.5-1))
    num=mp.quad(x,[0,th,1])
    cf=2*(1+2*ups**2)*sqrt(1-ups**2)-2*(1-ups**3)
    print("I(rho)",rho,num,cf)
# E coefficient bound at ups<=0.9,q>=113
def Ecoef(ups,q): return 2/sqrt(2*pi)*(0.25*(1-1/(2*q))**-1.5+(1+ups+ups**2)*(1-ups)**-0.5*(1+ups)**-1.5)
print("Ecoef max ups<=0.9,q=113:",max(Ecoef(u,113) for u in [i/1000 for i in range(0,901)]))
print("Ecoef at 0.99:",Ecoef(0.99,113), "at .9999",Ecoef(0.9999,113))
print("F(0.99)",2/sqrt(2*pi)*(1+2*0.99**2)*sqrt(1-0.99**2))
print("(1.15*6666)^{2/3}",(1.15*6666)**(2/3)," (1.2*1000)^{2/3}",(1.2*1000)**(2/3))
print("1.1284+2.82/389",1.1284+2.82/389," 9.3/389",9.3/389," 85/389",85/389," 2.82/113",2.82/113, "9.3/113",9.3/113,"85/113",85/113)
print("1.6*0.8/sqrt50",1.6*0.8/sqrt(50)," 2(2pi)^-.5 sqrt(50/.77)",2/sqrt(2*pi)*sqrt(50/0.77))
# j1,j2
q=lambda r:1+0.7501*r/(1+r)
j2=mp.quad(lambda r: mp.sqrt((1+r)/r)*0.70836*q(r)**3,[0,0.01,1])
j1=mp.quad(lambda r: mp.sqrt((1+r)/r)*0.70836*q(r)**3*(2.528571-mp.log(q(r))+1.5*mp.log(r)),[0,1e-6,0.01,1])
print("j2",j2,"j1",j1)
def DDLn(k):
    k=mp.mpf(k); dn=2*k**(mp.mpf(2)/3)
    eps=-mp.log(1-mp.sqrt(k+1)/(0.485917*k)); epsp=2.26/k+0.47/(dn-1)
    gam=2.6047*(2.53+0.5*mp.log(k)+eps+1.5/k)/k
    c=1/mp.sqrt(2*mp.pi)
    return 0.457143*c*q(dn/k)*mp.sqrt(1+dn/k)*(dn+1)**3.5/k**3+2*c/mp.sqrt(k)*(1+epsp)*(j1+(0.5*mp.log(k)+eps)*j2+gam)+3.9*c/k
for k in [6667,6668,8065,9551,9705,9949]: print("DDL^nat",k,DDLn(k))
print("j1+j2(0.5log6667-1)",j1+j2*(0.5*mp.log(6667)-1))
print("11.3137 vs 2^{7/2}",2**3.5)
# step5 constants
k=6667; dn=2*k**(2/3); D=floor(dn); rho0=D/k
print("rho0",rho0,"q(rho0)",q(rho0), "iota0?", 2.528571-log(q(rho0))+1.5*log(D**1.5/k)+0 , "  with floor correction:",2.528571-log(1.0722)+1.5*log(2**1.5*(1-1/dn)**1.5))
print("exp(-3.4964/1.5)",exp(-3.4964/1.5))
print("step5 bracket: 2*iota0-6+6sqrt(s0)-1.0288*6sqrt(s0)", 2*3.4964-6+6*sqrt(0.0972)-1.0288*6*sqrt(0.0972))
# check d^nat(rho) q(rho)^3 <= 1.0288 rho^{-1/2} on (0, rho0*0.0972) and >= rho^{-1/2} elsewhere up to rho0
mx=max(sqrt((1+r)/r)*q(r)**3*sqrt(r) for r in [rho0*0.0972*i/1000 for i in range(1,1001)])
print("max d q^3 sqrt(rho) on young part",mx, " min on rest",min(sqrt((1+r)/r)*q(r)**3*sqrt(r) for r in [rho0*0.0972+ (rho0-rho0*0.0972)*i/1000 for i in range(0,1001)]))
# step4: bracket >=3.246 in far region (rho>=rho0 at k=6667) with log k /2 + eps
eps=-log(1-sqrt(6668)/(0.485917*6667))
print("bracket at rho0,k=6667:",2.528571-log(q(rho0))+1.5*log(rho0)+0.5*log(6667)+eps)
# step3: g_d, b^nat>=1: d^{3/2}>2^{3/2}k? at d>2k^{2/3}: d^{3/2}>2^{1.5}k yes. g_d k/sqrt d >=1?
print("g_d max",0.485917*q(1)," check 2^{3/2}k >= 2 g_d k:",2**1.5, 2*0.485917*q(1))
# Acrit bound 1.00057: (k-1)(k+1+q)/(k-1+q)^2 <=1+1/k ; (k+1+d)/(k-1+d)<=1+2/k; 1-e^{-x}>=x(1-x/2)
# lemma 8.32 constants
print("cR*1.04^{1.5}/sqrt2",sqrt(2*pi)/2*exp(1/12)*1.04**1.5/sqrt(2))
ge=lambda t: exp(-t)*(1+1.5*t)
print("ge(1.0216)",ge(1.0216)," cR xi^{3/2} range",sqrt(2*pi)/2*exp(1/12)*1.04**1.5, sqrt(2*pi)/2*exp(1/12)*2**(1.0))
print("min |ge'| on [1.02,2.73]:",min(abs(exp(-t)*(0.5-1.5*t)) for t in [1.02+i*(2.73-1.02)/1000 for i in range(1001)]))
print("sqrt(1/2+1/562)",sqrt(0.5+1/562)," 0.234*0.2916*1.444",0.234*0.2916*1.444, " e^-1/564",exp(-1)/564)
print("iota q0 max: cR*2^{2/3}*6669^{-1/3}",sqrt(2*pi)/2*exp(1/12)*2**(2/3)*6669**(-1/3))
# 8.33 constants
cAb=lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
print("2cAb(0.6)-4/sqrt(0.6)",2*cAb(0.6)-4/sqrt(0.6))
print("int_0^0.6 (1+r)r^-.5(1-r)^-2",mp.quad(lambda r:(1+r)/mp.sqrt(r)/(1-r)**2,[0,0.6]))
print("2-0.6y/k>=1.39? y=k:",2-0.6)
# 8.34: 0.7999 vs 2(2pi)^-.5 (1-1/206)^-.5
print("0.7979*(1-1/206)^-0.5",2/sqrt(2*pi)*(1-1/206)**-0.5)
# 8.35 bulk: pi^two >= 0.41508 k^{-3/2}
def pitwo_lb(k,nu):
    N=k+nu
    return Bor(k)*Bor(nu-1)/(mp.e*Bor(k+nu))*mp.mpf(k)**1.5
print("pi^two k^{3/2} at k=6668 nu=0.48k+1..k-1:",min(pitwo_lb(6668,nu) for nu in [3202,4000,5000,6667]))
print("m_hit at 6667:",ceil(sqrt(5*6667*log(6667))), 0.09*6667)
print("xi'_k, exponent 1.5-2.5/(1+xi') at 6668:",(sqrt(5*6668*log(6668))+2)/6668, 1.5-2.5/(1+(sqrt(5*6668*log(6668))+2)/6668))
# bulk-majorants constants
print("4*16.54*2=",4*16.54*2, " bracket at 0.48:",0.48**-0.5-1+(1-sqrt(0.48))/3, " 132.32*0.54577",132.32*0.54577)
print("abar(6668)",3*1.15*(1.48*6668+2)/(0.48*6668+1)**1.5)
u=lambda k:3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("bbar(6668)",2*u(6668)*(2*6668-1)/(6668-1)+3*6669*6667**-1.5, " dbar",72.217/sqrt(6668))
# family thresholds
for name,phi in [("1a",1.3),("1b",2.0)]:
    for k in range(9000,10000):
        if 20001-2*k<=phi*k**(2/3): print(name,"first k",k,20001-2*k,phi*k**(2/3)); break
for k in range(8000,8100):
    if 20001-2*k<=0.48*k: print("2 first k",k,20001-2*k,0.48*k); break
print("eps0:",[floor(2**(2/3)*(k+1)**(2/3)) for k in [6668,8065,9551,9705]])
print("(2k)^{2/3} at 6667",(2*6667)**(2/3), " 0.99+0.59963*20001^{2/3}+1.24847*20001^{1/3}",0.99+0.59963*20001**(2/3)+1.24847*20001**(1/3))
print("0.8*1.3",0.8*1.3,"(k*/(k*+1))^{2/3} min",(6668/6669)**(2/3))
print("1.3*6669^{2/3}",1.3*6669**(2/3))
print("1.5(2k+3)^{2/3} at 6667",1.5*(2*6667+3)**(2/3), 0.48*6667)
print("(2k)^{2/3}<2^{2/3}(k+1)^{2/3} trivially; m(i)<=i^{2/3}; check 1.3*6667^{2/3}>6:",1.3*6667**(2/3))
# Bd^T(k, phi k^{2/3}) formula: (k+nu)u(k)[1/(k-1)+1/k] = (1+phi k^{-1/3}) * k*u*(2k-1)/(k(k-1))
print("Bd^T algebra ok: (k+nu)(1/(k-1)+1/k)=(k+nu)(2k-1)/(k(k-1))=(1+nu/k)(2k-1)/(k-1)")
# 8.35 monotonic s^up_{phi k^{2/3}+1}(k+1): log-derivative sign 1.5 sqrt(theta)-0.5 phi^2 theta -2 phi? check numerically
for phi in [1.3,2.0]:
    f=lambda k: 1.15*(k+1+phi*k**(2/3)+1)/(phi*k**(2/3)+1)**1.5
    print("s^up phi",phi,[f(k) for k in [6667,10000,1e5,1e7]])
