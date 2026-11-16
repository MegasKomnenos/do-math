# F5 검산 2: 6.4 u(k), 6.5 m*, Gamma*, v(k) 값, 증인 상계 478, theorem-U 네 적분의 대략값(mpmath quad)
from math import e, sqrt, pi, exp, log, ceil
import mpmath as mp
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
for k in (3131,6667,10000): print("u(%d)="%k,u(k),"2u=",2*u(k))
print("witness bound n=20000:",1.99+0.59963*20001**(2/3)+1.24847*20001**(1/3))
print("(2k)^(2/3) at k=3131:",6262**(2/3),"0.65k-1=",0.65*3131-1)
# 6.5 constants
tp=0.55; kap=1.498+2*3130/6261; print("kappa_d min",kap)
a=tp;b=-(kap*tp+2);c=kap; r=(-b+sqrt(b*b-4*a*c))/(2*a); print("root",r,"m=",(r*r-kap*r)*exp(-tp*r))
x=3132/3130; print("Gamma=",x/((1+x)**(1-tp)-1))
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/sqrt(k-1)
for k in (3131,6667,10000): 
    vp=max(k+1,4000); io=2*k+1-vp
    print("v(%d)="%k,v(k),"terms",2*min(1,3*vp*io**-1.5),2*u(k),50.62/sqrt(k-1))
print("Bd lower at 3131:",2-24000/2263**1.5-2*u(3131))
print("50.62/sqrt(3130)=",50.62/sqrt(3130))
cc=1/sqrt(2*pi)
print("combo:",3*cc*(8.133+cc*10.301),1.5*2.7323*0.8051*cc*(17.951+cc*23.462))
# theorem-U integrals, rough quad (double precision), to compare with D item values 8.1250,10.2786,17.9336,23.4221
mp.mp.dps=15
V0=mp.mpf(1)/3130
def FI(L): return mp.e**(1.5*L)*L*(1+0.75*L)
def FX(L): return mp.e**(1.5*L)*L
def Ical(F,T):
    # I(T)=int_0^1 u^{-1/2} phi(T u)/(T u) du
    f=lambda up: F(-mp.log(1-T*up))/(T*up)*up**(-0.5)
    return mp.quad(f,[0,0.5,1])
def integrals(F,G,E,Ep):
    def In(U):
        Vh=min(U,V0); return mp.sqrt(U+Vh)*Ical(F,(U+Vh)/(1+U))/(1+U-Vh)
    def om(U): return 1-cc+4*cc*mp.sqrt(G*(G+U))/U
    def N(U):
        Vh=min(U,V0); P=G*(G+U)*E/(U**2*mp.sqrt(1+U-Vh)); Gg=mp.sqrt(1+U)*Ep
        return min(P/mp.sqrt(3130), mp.sqrt(P*Gg))
    pts=[0,V0,0.01,0.1,0.5,1+2*V0]
    J=mp.quad(lambda U: In(U)*om(U),pts); Y=mp.quad(lambda U: In(U)*N(U),pts)
    return J,Y
print("J_I,Y_I:",integrals(FI,1,12.15,4.908))
print("J_X,Y_X:",integrals(FX,2.7323,7.25,2.75))
