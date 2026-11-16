from mpmath import mp, mpf, sqrt, exp, log, quad, pi, ceil, floor
mp.dps = 25
out=[]
def P(*a): out.append(" ".join(str(x) for x in a))
k=mpf(6668)
# old-7-16 (1) integrals
def J1(k):
    f=lambda t: (1+t+2/k)**(-mpf(3.5))*max(0,1-3/sqrt(k)*(t-1/k)**(-mpf(1.5)))
    t0=1/k+(3/sqrt(k))**(mpf(2)/3)
    return mpf(2.5)*quad(f,[t0,0.1,0.3,0.6,1])
def J2(k):
    c=3*(k-1)*k**(-mpf(1.5))
    f=lambda t: (1+t+1/k)**(-mpf(3.5))*max(0,1-c*(t-1/k)**(-mpf(1.5)))
    t0=1/k+c**(mpf(2)/3)
    return mpf(2.5)*quad(f,[t0,0.1,0.3,0.6,(k-1)/k])
J3=(k/(2*k+1))**mpf(2.5)*(1-3/sqrt(k)); J4=(k/(2*k+1))**mpf(2.5)*(1-3/sqrt(k-1))
P("J1,J2,J3,J4=",J1(k),J2(k),J3,J4," sum=",J1(k)+J2(k)+J3+J4)
# (2)
js=ceil((3*k)**(mpf(2)/3)); P("j*=",js)
P("first interval lhs 4.85[...]=",mpf('4.85')*(sqrt(k)/sqrt((3*k)**(mpf(2)/3)+2)-sqrt(2)))
P("0.3826*2=",mpf('0.3826')*2, " (2pi)^-1/2 e^-1/24 e^-1/(12*3334)=",exp(-mpf(1)/24-mpf(1)/(12*3334))/sqrt(2*pi))
P("second: 6.1224*0.95^-1.5=",mpf('6.1224')*mpf('0.95')**(-mpf(1.5)), " 6/0.98=",mpf(6)/mpf('0.98'))
P("16.35 vs 12/0.734=",12/mpf('0.734'))
e1=mpf('16.35')*((k+1)/(mpf('0.95')*k))**mpf(1.5)/(mpf('0.05')*k); P("third endpoint1 *k=",e1*k, " 6.62/sqrt k *k=",mpf('6.62')/sqrt(k)*k)
e2=mpf('5.45')/sqrt(k)*(1+1/k)**mpf(1.5)*k/(k-js-1); P("third endpoint2 *sqrt k=",e2*sqrt(k))
P("exact endpoint2 ratio*sqrtk=",mpf('16.35')*((k+1)/(js+1))**mpf(1.5)/(k-js-1)*sqrt(k))
# (3)
db=mpf('6.62')/sqrt(k); P("dbar=",db," band req=",(1+db/2)/(1-db/2))
cov=103*exp(1/(12*(mpf('1.48')*k+1)))/sqrt(2*pi); P("cover coef=",cov, " (2/(0.48k-102))^1.5=",(2/(mpf('0.48')*k-102))**mpf(1.5))
P("3.394 check:",exp(1/(12*(1.48*k+1)))/sqrt(2*pi)*(2*k/(mpf('0.48')*k**2))**mpf(1.5)*k**mpf(1.5))
P("pi0 bound:",(mpf('0.26')*k+0.5)*mpf('3.394')*k**(-mpf(1.5))+mpf('0.676')/k, " vs 0.8825/sqrt k+0.72/k=",mpf('0.8825')/sqrt(k)+mpf('0.72')/k)
bulk=1+(1+1/mpf('1.48'))*db/(2-db)+(1/mpf('1.48'))*(mpf('0.8825')/sqrt(k)+mpf('0.72')/k+mpf('41.2')*(2/(mpf('0.48')*k-102))**mpf(1.5))
P("bulk req=",bulk)
# 9.4 old-7-26 numbers
def u(k): return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(1.5))/sqrt(k)
def Ups(k): return (k-1)*u(k)/(2*k+1)
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**(-mpf(1.5)))-2*u(k)-mpf('50.62')/sqrt(k-1)
P("u(6668)=",u(k)," Ups=",Ups(k)," v(6668)=",v(k)," v(6667)=",v(mpf(6667)), " Ups(3131)=",Ups(mpf(3131)), " u(3131)/2=",u(mpf(3131))/2)
def mu(k): return Ups(k)/(mpf(1.5)*(1-mpf('1.2')/k)*(v(k)+Ups(k)*(k+1)/k))
m=mu(k); P("k mu/(1-mu)=",k*m/(1-m)," 0.1113k=",mpf('0.1113')*k, " k^1/3 mu/(1-mu)=",k**(mpf(1)/3)*m/(1-m))
for kk in [6668,10000,30000,100000,1e6]:
    kk=mpf(kk); mm=mu(kk); P("  k=",kk," k^1/3 mu/(1-mu)=",kk**(mpf(1)/3)*mm/(1-mm), " (1/mu-1)/k^1/3=",(1/mm-1)/kk**(mpf(1)/3))
rhoH=lambda k,nu: (1/k)*((1-mpf(1.5)/k)*mpf('0.307')*k/(k+nu-1)-mpf(47)/(24*k))
rhoL=lambda k,nu: mpf(1.5)*nu/(k*(k+nu))*(1-mpf('1.2')/k)
nu=mpf('0.112')*k; P("(i) k rhoL=",k*rhoL(k,nu)," k rhoH=",k*rhoH(k,nu))
Y=lambda k,nu,rho: k*rho*v(k)-Ups(k)*(1-(k+1)*rho)
P("(iii) k rhoH(3k+1)=",k*rhoH(k,k+1)," Y(3k+1)=",Y(k,k+1,rhoH(k,k+1)))
for kk in [6668,10000,50000]:
    kk=mpf(kk); P("  Y(3k+1) k=",kk,Y(kk,kk+1,rhoH(kk,kk+1)))
# old-7-28 (3)
for kk in [48965,48966]:
    kk=mpf(kk); P("k=",kk," Ups=",Ups(kk)," (1/20)(1-1/k)^103=",(1-1/kk)**103/20)
# dY/dnu bound
P("1.5*(1-1.2/k)*v/1.2366=",mpf(1.5)*(1-mpf('1.2')/k)*mpf('0.7654')/mpf('1.2366'))
# old-7-38
P("0.48k-1-8k^(2/3) at 6668=",mpf('0.48')*k-1-8*k**(mpf(2)/3), " 11.1^3=",mpf('11.1')**3, " (16/3)/0.48 cubed=",(mpf(16)/3/mpf('0.48'))**3)
P("e^-1/(12*366)=",exp(-1/(12*mpf(366))))
# old-7-41
P("(2/3)/6667=",mpf(2)/3/6667)
# old-7-42
P("0.08*k^(2/3)-1=",mpf('0.08')*k**(mpf(2)/3)-1, " root of Psi^lb: (1.678/2)^2=",(mpf('1.678')/2)**2)
# pair-one-variable Ii/k derivative constant
P("1.678*0.08/3=",mpf('1.678')*mpf('0.08')/3, " 1.678/0.0447=",mpf('1.678')/mpf('0.0447'))
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L9_행정리검산_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
