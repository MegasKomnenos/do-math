# O9: numeric re-check of 9.1 head-sum constants (head-sum-1 step 6, H*+ regions), 9.3 constants.
from mpmath import mp, mpf, sqrt, exp, log, quad, pi
mp.dps = 30
def ell_fac(u): return 1/(1-u**3)          # 1+1/ell
def c1(xi,u): return (1+xi*u*ell_fac(u))**mpf('1.5')*exp(ell_fac(u)*u**3/12)
def uq(xi,u): return ell_fac(u)**2*(xi*u+u**3)**2/2
def Phi(xi,u): return ell_fac(u)*c1(xi,u)*exp(uq(xi,u))*(mpf('0.11399')*xi**mpf('3.5')+mpf('0.15958')*xi**mpf('2.5')*u**2+mpf('0.85108')*xi**3*u)
def E(xi,u):
    c=c1(xi,u); den=mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u
    return c*ell_fac(u)*(mpf('0.5320')*xi**mpf('1.5')*u+mpf('0.7979')*sqrt(xi)*u**3+c*(mpf('0.625')*xi**2+xi*u**2))/den
def Lf(xi,u):
    den=mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u
    return den*exp(-E(xi,u))/(1+(xi*u+u**3)*ell_fac(u))
def G(xi,u): return Phi(xi,u)+u*(mpf('0.5320')*c1(xi,u)*xi**mpf('1.5')+mpf(1)/5)
u0=mpf(3132)**(-mpf(1)/3); u2=mpf(19404)**(-mpf(1)/3)
print("u0",u0,"u2",u2)
print("step6: Phi(1,u0)",Phi(1,u0)," L(1,u0)",Lf(1,u0)," ratio",Phi(1,u0)/Lf(1,u0))
# scan Phi/L over admissible domain
worst=0
for i in range(1,2001):
    xi=mpf(i)/2000
    for j in range(1,41):
        u=u0*j/40
        if xi<2*u*u: continue
        r=Phi(xi,u)/Lf(xi,u)
        worst=max(worst,r)
print("max Phi/L on grid",worst)
# regions for H*+
import itertools
mA=max(G(mpf('2')*u0**2+(mpf('0.75')-2*u0**2)*i/20000,u0)/Lf(mpf('2')*u0**2+(mpf('0.75')-2*u0**2)*i/20000,u0) for i in range(0,20001))
mB=max(G(mpf('0.75')+mpf('0.25')*i/4000,u2)/Lf(mpf('0.75')+mpf('0.25')*i/4000,u2) for i in range(0,4001))
mC=max(G(2*u*u,u)/Lf(2*u*u,u) for u in [u0*i/2000 for i in range(1,2001)])
print("G/L max A,B,C:",mA,mB,mC)
# C limit u->0: (1/5)/(0.7978*sqrt2-0.8848)
print("C limit",(mpf(1)/5)/(mpf('0.7978')*sqrt(2)-mpf('0.8848')))
# small-xi step 4 constants
print("c1 at xi=0.03,u0",c1(mpf('0.03'),u0)," uq",uq(mpf('0.03'),u0)," E bound", E(mpf('0.03'),u0)*(mpf('0.7978')*sqrt(mpf('0.03'))-mpf('0.8848')*u0)/(mpf('0.1721')*sqrt(mpf('0.03'))))
# H*+ t=k+1 : -1 - (k-1)/(k+1)*(k/(k+1))^(k-1)
k=mpf(3132); print("kP_{k+1}", -1-(k-1)/(k+1)*(k/(k+1))**(k-1))
# I2 constant
print("e^{-1/12}-e^{1/4}/4", exp(-mpf(1)/12)-exp(mpf(1)/4)/4, " times sqrt(2/pi)", (exp(-mpf(1)/12)-exp(mpf(1)/4)/4)*sqrt(2/pi))
# head-sum-2: 597, 598 ; 19404^{2/3}; 3132^{2/3}
print("597:",mpf(597)**mpf('1.5')+9*597, " 598:",mpf(598)**mpf('1.5')+9*598)
print("19404^(2/3)",mpf(19404)**(mpf(2)/3)," 3132^(2/3)",mpf(3132)**(mpf(2)/3), " 6*3132^(2/3)", 6*mpf(3132)**(mpf(2)/3))
print("m0(20001)", mpf(20001)**(mpf(2)/3)-6*mpf(20001)**(mpf(1)/3))
