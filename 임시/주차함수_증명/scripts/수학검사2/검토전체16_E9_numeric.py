# E9 numeric re-checks for chapter 9 (float; sanity-level)
import math
pi=math.pi
print("== 9.1 head-sum-1 constants")
u1=3132**(-1/3); print("upsilon1",u1, "<0.06835", u1<0.06835)
print("k^{2/3}/(k-1) at 3132", 3132**(2/3)/3131, "k^{2/3}<=(k-1)/6", 3132**(2/3)<=3131/6)
c1max=(1+0.0684)**1.5*math.exp(1/(12*3131)); print("c1max",c1max)
print("4/3 (2pi)^-1/2", 4/3*(2*pi)**-0.5, " 0.5320*1.105", 0.5320*1.105)
print("consts", 2*(2*pi)**-0.5/7, 2*(2*pi)**-0.5/5, 2*(2*pi)**-0.5*3.2/3)
print("e^{-1/12}-e^{1/4}/4", math.exp(-1/12)-math.exp(0.25)/4, (2/pi)**0.5*0.599)
print("3/(2*0.477)", 3/(2*0.477))
print("psi: 2(2pi)^-1/2", 2*(2*pi)**-0.5, (2*pi)**-0.5*(2+2.61238/12))
# step 4
l0=3131; a=1+1/l0
Phi4=a*1.0035*1.0001*(0.11399*0.03+0.15958*u1**2+0.85108*math.sqrt(0.03)*u1); print("Phi4 coeff",Phi4)
c1s=1.0035
E4=c1s*a*(0.5320*0.03*u1+0.7979*u1**3+c1s*(0.625*0.03**1.5+math.sqrt(0.03)*u1**2))/0.1721; print("E4",E4)
print("L denom",1+(0.03*u1+u1**3)*a, 0.1721*math.exp(-0.0317)/1.0024)
# step 5 thresholds
for p in [1,1.5,2,2.5,3,3.5]: print("p",p,"xi thr",(1.11*p*u1/(p-0.5))**2)
print("c2", 0.7979*math.sqrt(0.03)*u1**3/(0.7978*math.sqrt(0.03)-0.8848*u1))
# step 6
ql=u1*a; c1=(1+ql)**1.5*math.exp(1/(12*l0)); uq=a*a*(u1+u1**3)**2/2
br=0.11399+0.15958*u1**2+0.85108*u1
Phi6=a*c1*math.exp(uq)*br; print("c1",c1,"uq",uq,"br",br,"Phi6",Phi6)
den=0.7978-0.8848*u1; num=0.5320*u1+c1*(0.625+u1**2); Eb=c1*a*(num/den+0.000568)
Lb=den*math.exp(-Eb)/(1+(u1+u1**3)*a); print("den",den,"num",num,"Ebar",Eb,"Lbar",Lb,"R",Phi6/Lb)
print("== H-star-plus region scan")
def funcs(xi,u):
    a=1/(1-u**3); c1=(1+xi*u*a)**1.5*math.exp(a*u**3/12); uq=a*a*(xi*u+u**3)**2/2
    Phi=a*c1*math.exp(uq)*(0.11399*xi**3.5+0.15958*xi**2.5*u**2+0.85108*xi**3*u)
    den=0.7978*math.sqrt(xi)-0.8848*u
    E=c1*a*(0.5320*xi**1.5*u+0.7979*math.sqrt(xi)*u**3+c1*(0.625*xi**2+xi*u**2))/den
    L=den*math.exp(-E)/(1+(xi*u+u**3)*a)
    G=Phi+u*(0.5320*c1*xi**1.5+0.2)
    return Phi,L,G
u2=19404**(-1/3)
import numpy as np
mA=max(funcs(x,u1)[2]/funcs(x,u1)[1] for x in np.linspace(2*u1**2,0.75,20001)); print("A max",mA)
mB=max(funcs(x,u2)[2]/funcs(x,u2)[1] for x in np.linspace(0.75,1,4001)); print("B max",mB)
mC=max(funcs(2*u*u,u)[2]/funcs(2*u*u,u)[1] for u in np.linspace(1e-4,u1,20001)); print("C max",mC)
print("R(1) head-sum-1", funcs(1,u1)[0]/funcs(1,u1)[1])
print("== head-sum-2")
print(597**1.5+9*597, 598**1.5+9*598, math.floor(19404**(2/3)), 19404+722)
n=20001; print("m0", math.floor(n**(2/3)-6*n**(1/3)))
print("== H*+ t=k+1: 3/5 e^-1", 0.6*math.exp(-1))
print("== old-7-26 / Upsilon")
def uk(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def Uh(k): return (k-1)*uk(k)/(2*k+1)
def vk(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*uk(k)-50.62/math.sqrt(k-1)
k=6668; print("u",uk(k),"Uhat",Uh(k),"v(6668)",vk(k),"v(6667)",vk(6667))
mu=Uh(k)/(1.5*(1-1.2/k)*(vk(k)+Uh(k)*(k+1)/k)); print("mu",mu,"k mu/(1-mu)",k*mu/(1-mu),"0.1113k",0.1113*k,"k^{1/3}mu/(1-mu)",k**(1/3)*mu/(1-mu))
rH=((1-1.5/k)*0.1535-47/(24*k)); print("k rhoH(3k+1)",rH, "Y(3k+1)", rH*vk(k)-Uh(k)*(1-(1+1/k)*rH))
print("rhoL(0.112k)*k",1.5*0.112/1.112,"rhoH",(1-1.5/k)*0.307/1.112-47/(24*k))
for kk in [48965,48966]: print(kk,"Uhat",Uh(kk),"(1/20)(1-1/k)^103",0.05*(1-1/kk)**103)
print("== old-7-16 (2) d_k bound")
k=6668; js=math.ceil((3*k)**(2/3)); print("j*",js, "4.85[...]",4.85*(math.sqrt(k)*((3*k)**(2/3)+2)**-0.5-math.sqrt(2)))
print("second region",6.1224*0.95**-1.5, "(2pi)^-1/2 e^-1/24",(2*pi)**-0.5*math.exp(-1/24))
print("third endpoints",16.35*((k+1)/(0.95*k))**1.5/(0.05*k)*k, 5.45*(1+1/k)**1.5*k/(k-js-1))
def ratio(q):
    N=k+q; num=min(1,3*k*q**-1.5)
    den=k*(max(0,0.734*((q+1)**-0.5-(math.ceil(N/2)+1)**-0.5))+0.98/(N+1))
    return num/den
mx=max(ratio(q) for q in range(1,k)); print("max ratio*sqrt(k)",mx*math.sqrt(k))
print("== old-7-16 (3) requirement")
db=6.62/math.sqrt(k); print("band req",(1+db/2)/(1-db/2))
S=41.2*(2/(0.48*k-102))**1.5; p0=0.8825/math.sqrt(k)+0.72/k
print("bulk req",1+(1+1/1.48)*db/(2-db)+(1/1.48)*(p0+S), "pieces",S,p0, 103*(2*pi)**-0.5, (2*pi)**-0.5*(2/0.48)**1.5)
print("== L*(6668)")
def simpson(f,a,b,n=400000):
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n): s+= (4 if i%2 else 2)*f(a+i*h)
    return s*h/3
def J1(k):
    f=lambda t:(1+t+2/k)**-3.5*max(0,1-3*k**-0.5*(t-1/k)**-1.5)
    t0=1/k+(3*k**-0.5)**(2/3)
    return 2.5*simpson(f,t0,1)
def J2(k):
    c=3*(k-1)*k**-1.5
    f=lambda t:(1+t+1/k)**-3.5*max(0,1-c*(t-1/k)**-1.5)
    t0=1/k+c**(2/3)
    return 2.5*simpson(f,t0,(k-1)/k)
J3=(k/(2*k+1))**2.5*(1-3*k**-0.5); J4=(k/(2*k+1))**2.5*(1-3*(k-1)**-0.5)
print("J1",J1(k),"J2",J2(k),"J3",J3,"J4",J4,"sum",J1(k)+J2(k)+J3+J4)
print("== old-7-38", 0.48*k-1-8*k**(2/3), math.floor(0.48*k)+1-2-2*math.floor(4*k**(2/3)))
print("== psi-low consts",(2*pi)**-0.5*1.67806-0.3989*1.678, 1.46036+2.61238/12, (2*pi)**-0.5*math.exp(-1/12))
print("== 9.2: 0.0196 check", math.sqrt(8/(pi*6669)))
print("== pair lemma 37: 4k^{2/3}<6(k-1)^{2/3}", 4*k**(2/3), 6*(k-1)**(2/3))
