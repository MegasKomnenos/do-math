# 검토전체3 I9: 9장 수치 재계산 (배정밀도 점검용)
from math import *
import numpy as np

print("== A+ 정리 상수")
br = exp(-1/12) - exp(0.25)/4
print("e^-1/12 - e^1/4/4 =", br, "; (2/pi)^1/2*0.5990 =", sqrt(2/pi)*0.5990, "; 3/(2*0.477)=", 3/(2*0.477))
print("== psi-two-sided: 2*(2pi)^-1/2 =", 2/sqrt(2*pi), "; 0.398942*(2+2.61238/12)=", (2+2.61238/12)/sqrt(2*pi))
print("== head-sum-1 상수: 0.79788/7,5, *3.2/3 =", 2/sqrt(2*pi)/7, 2/sqrt(2*pi)/5, 2/sqrt(2*pi)*3.2/3, "; 4/3*(2pi)^-1/2=", 4/3/sqrt(2*pi))
u0 = 3132**(-1/3); print("upsilon0 =", u0, "; k^(2/3)/(k-1) at 3132 =", 3132**(2/3)/3131)
# step 4
print("q/l at xi=.03:", 0.03*u0*(1+1/3131), "; c1<=", (1+0.00206)**1.5*exp(1/(12*3131)), "; u_q<=", (1+1/3131)**2*(0.03*u0+u0**3)**2/2)
br4 = 0.11399*0.03 + 0.15958*u0**2 + 0.85108*sqrt(0.03)*u0
print("Phi bracket/xi^2.5 at .03:", br4, "*1.0040 =", br4*1.0040)
num = 1.0035*1.0004*(0.5320*0.03*u0 + 0.7979*u0**3 + 1.0035*(0.625*0.03**1.5 + sqrt(0.03)*u0**2))
print("E <= ", num/0.1721, "; L denom", 1+(0.03*u0+u0**3)*1.0004, "; 0.1721*e^-.0317/1.0024 =", 0.1721*exp(-0.0317)/1.0024)
print("p=1 threshold xi:", (2*1.109*u0)**2, "; p=3/2:", (1.5/1*1.109*u0)**2, "; c5:", 0.7979*sqrt(0.03)*u0**3/(0.7978*sqrt(0.03)-0.8848*u0))
# step 6
l0=3131; ql = u0*(1+1/l0); c1 = (1+ql)**1.5*exp(1/(12*l0)); uq=(1+1/l0)**2*(u0+u0**3)**2/2
brk = 0.11399+0.15958*u0**2+0.85108*u0
Phi = (1+1/l0)*c1*exp(uq)*brk
den = 0.7978-0.8848*u0; nb = 0.5320*u0 + c1*(0.625+u0**2)
Ebar = c1*(1+1/l0)*(nb/den + 5.68e-4)
Lbar = den*exp(-Ebar)/(1+(u0+u0**3)*(1+1/l0))
print("step6: q/l", ql, "c1", c1, "uq", uq, "e^uq", exp(uq), "bracket", brk, "Phi", Phi)
print("  den", den, "nb", nb, "nb/den", nb/den, "Ebar", Ebar, "Lbar", Lbar, "Rbar(1)", Phi/Lbar)
print("== head-sum-2 (ii):", 597**1.5+9*597, 598**1.5+9*598, "; m0 at 20001:", 20001**(2/3)-6*20001**(1/3))
print("  19404^(2/3)=", 19404**(2/3), "; 16/3 k^1/3>=39 iff k^1/3>=", 39*3/16)
print("== H*+ t=k+1: 3/5 e^-1 =", 0.6*exp(-1))

# H*+ regions
def Hfun(xi, u):
    il = 1/(1-u**3)  # 1+1/l
    c1 = (1+xi*u*il)**1.5*exp(il*u**3/12)
    uq = il**2*(xi*u+u**3)**2/2
    Phi = il*c1*exp(uq)*(0.11399*xi**3.5+0.15958*xi**2.5*u**2+0.85108*xi**3*u)
    den = 0.7978*sqrt(xi)-0.8848*u
    E = c1*il*(0.5320*xi**1.5*u+0.7979*sqrt(xi)*u**3+c1*(0.625*xi**2+xi*u**2))/den
    L = den*exp(-E)/(1+(xi*u+u**3)*il)
    G = Phi + u*(0.5320*c1*xi**1.5+0.2)
    return Phi, L, G
u1 = 3132**(-1/3); u2 = 19404**(-1/3)
xs = np.linspace(2*u1**2, 0.75, 200001); rA = max(Hfun(x,u1)[2]/Hfun(x,u1)[1] for x in xs)
xs = np.linspace(0.75, 1, 20001); rB = max(Hfun(x,u2)[2]/Hfun(x,u2)[1] for x in xs)
us = np.linspace(1e-4, u1, 20001); rC = max(Hfun(2*u*u,u)[2]/Hfun(2*u*u,u)[1] for u in us)
print("H*+ 영역 A,B,C 최대 (float 표본):", rA, rB, rC, "; head-sum-1 Phi/L max over A-range:", max(Hfun(x,u1)[0]/Hfun(x,u1)[1] for x in np.linspace(2*u1**2,1,100001)))

print("== old-7-16 (2)")
k=6668; js=ceil((3*k)**(2/3))
print(" j*=",js," 4.85[...]=",4.85*(sqrt(k)*((3*k)**(2/3)+2)**-0.5-sqrt(2)), " 0.734*6.62=",0.734*6.62)
print(" (2pi)^-1/2 e^-1/24 e^-1/(12*3334)=", exp(-1/24-1/(12*3334))/sqrt(2*pi))
print(" 2nd:", 6/0.98*0.95**-1.5, " 3rd ends:", 16.35*((k+1)/(0.95*k))**1.5/(0.05*k)*k, 5.45*(1+1/k)**1.5*k/(k-js-1), " vs 6.62")
print(" 12/0.734=",12/0.734)
print("== old-7-16 (3)")
d=6.62/sqrt(k); print(" dbar=",d," band req=",(1+d/2)/(1-d/2))
print(" 103*(2pi)^-1/2*e^(1/(12*6669))=",103/sqrt(2*pi)*exp(1/(12*6669)), " (2/.48)^1.5*(2pi)^-1/2*e..=",(2/0.48)**1.5/sqrt(2*pi)*exp(1/(12*6669)))
bulk = 1+1.676*d/(2-d)+0.676*(0.8825/sqrt(k)+0.72/k+41.2*(2/(0.48*k-102))**1.5)
print(" bulk req=",bulk, " 0.26*3.394=",0.26*3.394, " 1.697/k^1.5*k=",1.697/sqrt(k))

print("== old-7-26")
def uhat(k): return (k-1)/(2*k+1)*3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def vfun(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*(3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5)-50.62/sqrt(k-1)
def mu(k): return uhat(k)/(1.5*(1-1.2/k)*(vfun(k)+uhat(k)*(k+1)/k))
k=6668; m=mu(k)
print(" v(6668)=",vfun(k)," uhat=",uhat(k)," k mu/(1-mu)=",k*m/(1-m)," 0.1113k=",0.1113*k," k^1/3 mu/(1-mu)=",k**(1/3)*m/(1-m))
rhoH = ((1-1.5/k)*0.1535-47/(24*k)); print(" k rhoH(3k+1)=",rhoH," Y(3k+1)=",rhoH*vfun(k)-uhat(k)*(1-(1+1/k)*rhoH))
print(" (i) k rhoL(.112k)=",1.5*0.112/1.112*(1-1.2/k)," k rhoH>=",(1-1.5/k)*0.307/1.112-47/(24*k))
mus=[mu(kk) for kk in range(3131,30000)]; print(" mu decreasing from 3131?", all(mus[i]>mus[i+1] for i in range(len(mus)-1)), " from 3999?", all(mus[i]>mus[i+1] for i in range(3999-3131,len(mus)-1)))
def f1(k): return 1.5*(1-1.2/k)*vfun(k)/(uhat(k)*k**(1/3))
def f2(k): return (1.5*(1-1.2/k)*(1+1/k)-1)/k**(1/3)
for kk in [6668,10000,100000,1000000]:
    h=1e-3*kk; print("  k",kk," d f1/dk / k^-5/6 =",(f1(kk+h)-f1(kk-h))/(2*h)/kk**(-5/6)," -d f2/dk / k^-4/3 =",-(f2(kk+h)-f2(kk-h))/(2*h)/kk**(-4/3))
print(" uhat(48966)=",uhat(48966)," 1/20(1-1/k)^103=",(1-1/48966)**103/20, " uhat(48965) vs", uhat(48965),(1-1/48965)**103/20)
print(" uhat(3131)=",uhat(3131)," u(3131)/2=", 3/0.35*(1.35+1/3131)*(0.65-1/3131)**-1.5*3131**-0.5/2)
print(" dY/dnu bound 1.5*0.7654/1.2366=",1.5*0.7654/1.2366, " 1/(20(k-1))*k=",k/(20*(k-1)))
print("== old-7-38: 0.48k-1-8k^(2/3) at 6668 =",0.48*6668-1-8*6668**(2/3)," e^-1/(12*366)=",exp(-1/(12*366)))
print("== psi-low: 1.46036+2.61238/12=",1.46036+2.61238/12," diff const:",(1/sqrt(2*pi)-0.3989)*2, 1/sqrt(2*pi)*1.67806-0.3989*1.678, " Psi(1)=",exp(-1)," 0.3989*0.322=",0.3989*0.322)
print("== old-7-39: (2pi)^-1/2 e^-1/12=",exp(-1/12)/sqrt(2*pi))
print("== centroid: sqrt(8/(pi*6669))=",sqrt(8/(pi*6669)))
print("== old-7-41: (1+1/6667)^(2/3)-1=",(1+1/6667)**(2/3)-1)
print("== old-7-42: 0.08*6668^(2/3)-1=",0.08*6668**(2/3)-1, " Psi_low zero at", (1.678/2)**2)
print("== 9.2: 0.98: 1-sqrt(8/(pi*6669))=",1-sqrt(8/(pi*6669)))
print("== x_k: 3/0.35=",3/0.35)
