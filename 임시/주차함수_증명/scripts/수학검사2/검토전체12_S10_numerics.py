# S10 검산: 10장의 상수·적분·표 값 재계산 (배정밀도; 확인 목적)
import math
from math import log, exp, sqrt, pi, e

def integrate(f, a, b, n=200000):
    # 합성 Simpson (n 짝수)
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n):
        s+= (4 if i%2 else 2)*f(a+i*h)
    return s*h/3

q=lambda r: 1+0.7501*r/(1+r)
# j2, j1 with substitution rho=sigma^2 to remove singularity
j2=integrate(lambda s: 2*sqrt(1+s*s)*0.70836*q(s*s)**3, 1e-12, 1)
j1=integrate(lambda s: 2*sqrt(1+s*s)*0.70836*q(s*s)**3*(2.528571-log(q(s*s))+3*log(s)) if s>0 else 0, 1e-12, 1)
print("j2",j2,"j1",j1)
print("2.5-log2-log0.485917",2.5-log(2)-log(0.485917), "3*sqrt2*0.16696",3*sqrt(2)*0.16696)
def DDLnat(k):
    dn=2*k**(2/3)
    eps=-log(1-sqrt(k+1)/(0.485917*k))
    epsp=2.26/k+0.47/(dn-1)
    gam=2.6047*(2.53+0.5*log(k)+eps+1.5/k)/k
    t1=0.457143*(2*pi)**-0.5*q(dn/k)*sqrt(1+dn/k)*(dn+1)**3.5/k**3
    t2=2*(2*pi)**-0.5*k**-0.5*(1+epsp)*(j1+(0.5*log(k)+eps)*j2+gam)
    t3=3.9*(2*pi)**-0.5/k
    return t1+t2+t3
for k in (6667,6668,8065,9551,9705): print("DDLnat",k,DDLnat(k))
print("decrease cond", j1+j2*(0.5*log(6667)-1))
# 3.9/k claim: sum over d>d_nat of 2*0.72888*q_d^2*sqrt(k-1+d)/k^2.5
for k in (6667,20000):
    dn=2*k**(2/3); s=0
    for d in range(int(dn)+1,k+2):
        qd=1+0.7501*(d-1)/(k-1+d); s+=2*0.72888*qd*qd*sqrt(k-1+d)/k**2.5
    print("last-term sum*k",k,s*k," vs 3.9")
# constants
print("cR",sqrt(2*pi)/2*exp(1/12),"f1",4/(3*sqrt(2*pi)),"theta0",(2*exp(-0.48)-1)*exp(-0.48))
cAb=lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
print("2cAb(0.6)-4/sqrt0.6",2*cAb(0.6)-4/sqrt(0.6))
print("Sub max",integrate(lambda s: 2*(1+s*s)/(1-s*s)**2, 0, sqrt(0.6)))  # rho=s^2: (1+rho)rho^{-1/2}(1-rho)^{-2} drho = 2(1+s^2)/(1-s^2)^2 ds
r=0.48; print("0.54577",r**-0.5-1+(1-sqrt(r))/3)
print("Acrit factor k=6667",(1+1/6667)*(1+2/6667)/(1-3/(4*6667)))
print("cd factor",(1.00057**2)*(1+2/6667)**2/6)
# sign lemma
k=6667; dn=2*k**(2/3); D=int(dn); rho0=D/k
print("rho0",rho0,"q(rho0)",q(rho0),"bracket min",2.528571-log(q(rho0))+log(D**1.5/k))
s0=exp(-3.4964/1.5); print("sigma0",s0,"bracket",2*3.4964-6-0.1728*sqrt(s0))
# Theorem old-8-25 constants
F=lambda u: 2*(2*pi)**-0.5*(1+2*u*u)*sqrt(1-u*u)
print("Fmax",F(sqrt(0.5)),2/sqrt(pi))
E=lambda u,qq: 2*(2*pi)**-0.5*(0.25*(1-1/(2*qq))**-1.5+(1+u+u*u)*(1-u)**-0.5*(1+u)**-1.5)
print("E coef u=0.9",E(0.9,389)*389,"u=0.99",E(0.99,389)*389,"u=0.9999",E(0.9999,389)*389)
print("F(0.99)",2*(2*pi)**-0.5*3*sqrt(1-0.81),"F(0.9999)",2*(2*pi)**-0.5*3*sqrt(1-0.9801))
# theta1 root of (1-t)^2.5-1+2t
lo,hi=0.2,0.4
for _ in range(60):
    mid=(lo+hi)/2
    if (1-mid)**2.5-1+2*mid<0: lo=mid
    else: hi=mid
print("theta1",lo)
# Stays^up(9705;1.3k^{2/3}) reproduction
mS=1.15
def stays_up(k,nubar):
    tot=0
    for y in (k-1,k):
        abar=(mS*(y+2*y**(2/3)))**(2/3)
        flat=2*(abar-1)/(y+2-abar)
        z=0.6+1/y
        xi=(nubar+4)/(k-1)
        if xi>=0.6: sub=0
        else:
            sub=(k-1)/k*integrate(lambda s: 2*(s*s-xi)*(1+s*s)/(s*s*(1-s*s)**2)*s*s if s>0 else 0, sqrt(xi), sqrt(0.6))  # rho=s^2: (rho-xi)(1+rho)rho^{-3/2}(1-rho)^{-2} drho = (s^2-xi)(1+s^2)/(s^3 (1-s^2)^2) 2s ds
        ab=mS*(1+1/y)*(4*((mS*y)**(2/3)-1)**-0.5+y**-0.5*(2*cAb(z)-4*z**-0.5-sub))
        tot+=flat+ab
    top=integrate(lambda r: min(2,2+(nubar+1)/k-r)*(1+r/3)*r**-1.5, 0.6-2.6/k, 1)
    tot+=2*16.54*k**-0.5*top
    return tot,flat,ab,2*16.54*k**-0.5*top
print("Stays_up 1a",stays_up(9705,1.3*9705**(2/3)))
print("Stays_up 1b",stays_up(9551,2*9551**(2/3)))
print("Stays_up 2",stays_up(8065,0.48*8065))
# Bd^T
u=lambda k: 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
BdT=lambda k,nu: (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
print("BdT 1a",BdT(9705,1.3*9705**(2/3)),"1b",BdT(9551,2*9551**(2/3)),"2",BdT(8065,0.48*8065))
print("R'_1b sum",BdT(9551,2*9551**(2/3))+DDLnat(9551)+stays_up(9551,2*9551**(2/3))[0])
print("R'_1a sum",BdT(9705,1.3*9705**(2/3))+DDLnat(9705)+stays_up(9705,1.3*9705**(2/3))[0])
# s^up values
sup=lambda d,y: min(1,mS*(y+d)/d**1.5)
print("3s_up 1b",3*sup(1.3*9551**(2/3)+1,9552),"2",3*sup(2*8065**(2/3)+1,8066))
xi2=2*9551**(2/3)/9550; print("theta part 1b",(2*exp(-xi2)-1)*exp(-xi2))
# e^c
ec=lambda k,n: 3*n*n/((k-1)*k)+4.8*sqrt(n)/k+n*n/(2*(k-1)**2)
print("ec 1a",ec(9705,1.3*9705**(2/3)))
# bulk ebar
def ebar(k):
    xp=(sqrt(5*k*log(k))+2)/k
    return exp(1.5/k)*(exp(sqrt(5*log(k)/k)+1/k)+2.40918*k**(1.5-2.5/(1+xp)))
print("4-ebar",4-ebar(6668))
abar=lambda k: 3*1.15*(1.48*k+2)/(0.48*k+1)**1.5
bbar=lambda k: 2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**-1.5
print("abar",abar(6668),"bbar",bbar(6668),"dbar",72.217/sqrt(6668))
# pi_two constant
print("pi_two const",(2*pi)**-0.5/e*2**1.5)
# Q(y,xi) edge check bulk
def slow(d,y): return exp(-4/(3*sqrt(2*pi))*((y+d-1)/y)**1.5*d**1.5/y)
def Qf(y,xi):
    k=y-1; q0=xi*y**(2/3); cR=sqrt(2*pi)/2*exp(1/12)
    pref=k/(k+1)*(1-q0/(2*k))*2*(2*pi)**-0.5*exp(-1/12)*y/(cR*q0)
    A=exp(-q0/y)*slow(q0,y)*(exp(-cR*q0/y)-exp(-cR*q0*sqrt(q0/2)/y))
    B=exp(-q0/(2*y))*slow(q0/2,y)*(exp(-cR*q0*sqrt(q0/2+1)/y)-exp(-cR*q0**1.5/y))
    return pref*(A+B)
k0=6668; xic=2**(2/3)
print("edge bulk",4*slow(xic*(k0+1)**(2/3)+1,k0)+2*Qf(k0+1,xic)-2.3237)
k0=9705
print("edge 1a",4*slow(1.3*(k0+1)**(2/3)+1,k0)+2*Qf(k0+1,1.3)-4.7703, "1a m0>N",Qf(k0+1,xic)+slow(xic*(k0+1)**(2/3)+1,k0)-1.7703)
k0=9551
print("edge 1b",4*slow(xic*(k0+1)**(2/3)+1,k0)+2*Qf(k0+1,xic)-4.2790, "1b m0>N",Qf(k0+1,xic)+slow(xic*(k0+1)**(2/3)+1,k0)-1.8146)
# gamma coefficient
k=6667; print("gamma coef",sqrt(2)*0.70836*q(1+1/k)**3)
# 2.6047 vs
# family thresholds
for k in (9704,9705,9550,9551,8064,8065): print(k, 20001-2*k, 1.3*k**(2/3), 2*k**(2/3), 0.48*k)
for k in (6668,8065,9551,9705): print("eps0",k,int((2*(k+1))**(2/3)))
