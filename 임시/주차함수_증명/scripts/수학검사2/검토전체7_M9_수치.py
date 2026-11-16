# M9 검산: 9장의 손 계산 수치 재확인 (배정밀도; 지적의 근거용)
import math
from math import exp, sqrt, log, pi, floor, ceil

def check(name, val, claim):
    print(f"{name}: {val!r}  (글: {claim})")

# --- 정리 A+ (4)
check("e^{-1/12}-e^{1/4}/4", exp(-1/12)-exp(0.25)/4, ">=0.5990")
check("(2/pi)^{1/2}*0.5990", sqrt(2/pi)*0.5990, "0.4779")
check("3/(2*0.477)", 3/(2*0.477), "<=3.15")

# --- psi-two-sided
check("(2pi)^{-1/2}*2", 2/sqrt(2*pi), "0.797885")
check("(2pi)^{-1/2}*(2+2.61238/12)", (2+2.61238/12)/sqrt(2*pi), "0.884733")

# --- head-sum-1
k=3132; u0=k**(-1/3); l=k-1
check("upsilon_0", u0, "0.068348")
check("k^{2/3}/(k-1)", k**(2/3)/(k-1), "<=0.0684")
c1max=(1+k**(2/3)/(k-1))**1.5*exp(1/(12*l))
check("c1 max", c1max, "<=1.105")
check("4/3 (2pi)^{-1/2}", 4/3/sqrt(2*pi), "<=0.5320")
check("0.5320*1.105", 0.5320*1.105, "<0.59")
for c,nm in [(2/sqrt(2*pi)/7,"0.11399"),(2/sqrt(2*pi)/5,"0.15958"),(2/sqrt(2*pi)*3.2/3,"0.85108")]:
    check("const",c,nm)
check("0.8848/sqrt2", 0.8848/sqrt(2), "0.6257")
check("0.7978-0.6257", 0.7978-0.6257, "0.1721")
# step 4
xi=0.03
qoverl=xi*u0*(1+1/l)
check("q/l at xi=0.03", qoverl, "<0.00206")
c1=(1+qoverl)**1.5*exp(1/(12*l)); check("c1 at xi=.03", c1, "<=1.0035")
uq=(1+1/l)**2*(xi*u0+u0**3)**2/2; check("u_q", uq, "<=3e-6")
Phi_coef=(1+1/l)*1.0035*1.0001*(0.11399*0.03+0.15958*u0**2+0.85108*sqrt(0.03)*u0)
check("Phi coef", Phi_coef, "<=0.01434")
num=(0.5320*xi**1.5*u0+0.7979*sqrt(xi)*u0**3+c1*(0.625*xi**2+xi*u0**2))
E=c1*(1+1/l)*num/(0.1721*sqrt(xi)); check("E at xi=.03", E, "<=0.0317")
den=1+(0.03*u0+u0**3)*1.0004; check("L denom", den, "<=1.0024")
check("0.1721*e^{-0.0317}/1.0024", 0.1721*exp(-0.0317)/1.0024, ">=0.1662")
check("0.1662/0.01434", 0.1662/0.01434, ">=11.5")
# step 5 thresholds
for p in [1,1.5,2,2.5,3,3.5]:
    thr=(p*0.8848*u0/((p-0.5)*0.7978))**2
    print("  p=",p," xi threshold ",thr)
check("0.7978*sqrt(0.03)", 0.7978*sqrt(0.03), ">=0.1381")
check("0.8848*u0", 0.8848*u0, "0.0605")
c5=0.7979*sqrt(0.03)*u0**3/(0.7978*sqrt(0.03)-0.8848*u0); check("c5", c5, "5.68e-4")
# step 6
l0=3131
ql=u0*(1+1/l0); check("q/l", ql, "0.068370")
c1=(1+ql)**1.5*exp(1/(12*l0)); check("c1", c1, "1.10432")
uq=(1+1/l0)**2*(u0+u0**3)**2/2; check("u_q", uq, "<=0.002360")
br=0.11399+0.15958*u0**2+0.85108*u0; check("bracket", br, "0.17291")
Phi=(1+1/l0)*c1*exp(uq)*br; check("Phi", Phi, "0.19145")
den=0.7978-0.8848*u0; check("Ebar denom", den, "0.737325")
nb=0.5320*u0+c1*(0.625+u0**2); check("Ebar num bracket", nb, "0.731719")
Eb=c1*(1+1/l0)*(nb/den+5.68e-4); check("Ebar", Eb, "1.09689")
Ld=1+(u0+u0**3)*(1+1/l0); check("Lbar denom", Ld, "1.068689")
Lb=den*exp(-Eb)/Ld; check("Lbar", Lb, "0.23037")
check("Rbar(1)", Phi/Lb, "0.83106")

# --- head-sum-2
check("597^1.5+9*597", 597**1.5+9*597, "19959.9")
check("598^1.5+9*598", 598**1.5+9*598, "20005.5")
n=20001; check("n^{2/3}-6n^{1/3}", n**(2/3)-6*n**(1/3), ">=573 (floor)")
check("phi(7/16)", 1-1.5*(7/16)+(7/16)**2/2-(1-7/16)**1.5, ">=0")
k=19404; q0=floor(k**(2/3)); check("floor(19404^{2/3})", q0, "722")
check("k^{1/3} 19404", k**(1/3), ">=7.4")
k=3132; check("floor(0.75*3132^{2/3})", floor(0.75*k**(2/3)), "")

# --- H-star-plus t=k+1
check("3/5 e^{-1}", 0.6*exp(-1), ">0.22")

# --- centroid
check("sqrt(8/(pi*6669))", sqrt(8/(pi*6669)), "<=0.0196")

# --- 9.3 AR step (2)
k=6668
check("(2pi)^{-1/2}e^{-1/24}e^{-1/(12*3334)}", exp(-1/24)*exp(-1/(12*3334))/sqrt(2*pi), ">=0.3826")
js=ceil((3*k)**(2/3)); check("j_*", js, "")
check("4.85[sqrt k ((3k)^{2/3}+2)^{-1/2} - sqrt2]", 4.85*(sqrt(k)/sqrt((3*k)**(2/3)+2)-sqrt(2)), "7.7")
check("6.1224*0.95^{-1.5}", 6.1224*0.95**-1.5, "<=6.62")
check("12/0.734", 12/0.734, "16.35")
check("16.35*((k+1)/(0.95k))^{1.5}/(0.05k) * k", 16.35*((k+1)/(0.95*k))**1.5/(0.05*k)*k, "353.3")
check("5.45 (1+1/k)^{1.5} k/(k-j*-1)", 5.45*(1+1/k)**1.5*k/(k-js-1), "<=6.62")
def ratio(q):
    N=k+q
    num=min(1,3*k*q**-1.5)
    first=0.734*max(0,(q+1)**-0.5-(ceil(N/2)+1)**-0.5)
    den=k*(first+0.98/(N+1))
    return num/den
mx=max((ratio(q)*sqrt(k),q) for q in range(1,k))
check("max over q of ratio*sqrt k", mx, "6.069 at q=6666")
# AR step (3)
dbar=6.62/sqrt(k)
check("band requirement", (1+dbar/2)/(1-dbar/2), "<=1.0845")
bulk=1+(1+1/1.48)*dbar/(2-dbar)+(1/1.48)*(0.8825/sqrt(k)+0.72/k+41.2*(2/(0.48*k-102))**1.5)
check("bulk requirement", bulk, "<=1.0787")
check("103*(2pi)^{-1/2}", 103/sqrt(2*pi), "<=41.2")
check("(2pi)^{-1/2}(2/0.48)^{1.5}", (2/0.48)**1.5/sqrt(2*pi), "<=3.394")
check("1/1.48", 1/1.48, "<0.676")
# AR integrals at k=6668 (midpoint rule)
def J1(k,n=400000):
    a,b=1/k,1.0; h=(b-a)/n; s=0.0
    for i in range(n):
        t=a+(i+0.5)*h
        s+=(1+t+2/k)**-3.5*max(0,1-3*k**-0.5*(t-1/k)**-1.5)
    return 2.5*s*h
def J2(k,n=400000):
    a,b=1/k,(k-1)/k; h=(b-a)/n; s=0.0
    for i in range(n):
        t=a+(i+0.5)*h
        s+=(1+t+1/k)**-3.5*max(0,1-3*(k-1)*k**-1.5*(t-1/k)**-1.5)
    return 2.5*s*h
J3=(k/(2*k+1))**2.5*(1-3*k**-0.5); J4=(k/(2*k+1))**2.5*(1-3*(k-1)**-0.5)
j1=J1(k); j2=J2(k)
check("J1",j1,"[0.432680,0.432707]"); check("J2",j2,"[0.432831,0.432857]"); check("J3",J3,"0.17025"); check("J4",J4,"0.17025")
check("L_*(6668)", j1+j2+J3+J4, ">=1.206")

# --- 9.4 lemma old-7-26 and theorem old-7-28
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def Uhat(k): return (k-1)*u(k)/(2*k+1)
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/sqrt(k-1)
k=6668
check("v(6668)", v(k), ">0.7654"); check("v(6667)", v(6667), ">0.7654"); check("Uhat(6668)", Uhat(k), "")
check("Uhat(3131)<0.198", Uhat(3131), "<0.198")
def rhoH(k,nu): return (1/k)*((1-1.5/k)*0.307*k/(k+nu-1)-47/(24*k))
def rhoL(k,nu): return 1.5*nu/(k*(k+nu))*(1-1.2/k)
check("k rhoL(0.112k)", k*rhoL(k,0.112*k), "<=0.152"); check("k rhoH(0.112k)", k*rhoH(k,0.112*k), ">=0.275")
mu=Uhat(k)/(1.5*(1-1.2/k)*(v(k)+Uhat(k)*(k+1)/k))
check("k mu/(1-mu)", k*mu/(1-mu), "741.8 <= 0.1113k=742.15"); check("k^{1/3} mu/(1-mu)", k**(1/3)*mu/(1-mu), "2.094")
rh=rhoH(k,k+1); check("k rhoH(3k+1)", k*rh, ">=0.1531")
Y=k*rh*v(k)-Uhat(k)*(1-(k+1)*rh); check("Y_k(3k+1)", Y, "0.00273")
check("1.5*(1-1.2/k)*v/1.2366", 1.5*(1-1.2/k)*v(k)/1.2366, ">=0.928")
for kk in [48965,48966]:
    print("k=",kk," Uhat=",Uhat(kk)," (1/20)(1-1/k)^103=",(1-1/kk)**103/20, " ok" if Uhat(kk)<=(1-1/kk)**103/20 else " FAIL")
def Y_of(k,nu):
    rm=max(0,min(rhoH(k,nu),rhoL(k,nu))) if nu<=k else max(0,rhoH(k,nu))
    return k*rm*v(k)-Uhat(k)*(1-(k+1)*rm)
nu0=next(nu for nu in range(1,k+2) if Y_of(k,nu)>=0); check("nu0(6668)", nu0, "<=742; 3.6k^{2/3}="+str(3.6*k**(2/3)))
for kk in [38886,38887]:
    F=Y_of(kk,103)+(1-1/kk)**103/20
    print("k=",kk," F_k(103)=",F)

# --- 9.5
k=6668
check("4k^{2/3} floor", floor(4*k**(2/3)), "")
check("0.48k-1-8k^{2/3}", 0.48*k-1-8*k**(2/3), "365.5")
check("e^{-1/(12*366)}", exp(-1/(12*366)), ">=1-2.3e-4")
check("(1+1/6667)^{2/3}", (1+1/6667)**(2/3), "<=1.0001")
check("psi-low const", (1.46036+2.61238/12), "1.67806")
check("0.3989*0.322", 0.3989*0.322, "<0.3679")
check("0.08k^{2/3}-1", 0.08*k**(2/3)-1, ">=27")
check("Psi^lb zero", (1.678/2)**2, "0.704")
Sm=0.5417366; Sp=0.5416178
def Aup(k,j):
    nu=j*k; N=k+nu; e=1/(12*(k+1))
    Psilb=0.3989*(2*sqrt(nu)-1.678)
    pi0=0.7979/sqrt(nu)-(1-e)*(1.5*Psilb/(N+1)+15/8*0.367*2/3*nu**1.5/(N+1)**2+35/16*0.367*0.4*nu**2.5/(N+1)**3)+e*((1+2*j)/(1+j))**1.5
    merge=103/sqrt(2*pi)*(k+1)**-1.5*(nu-102)**-1.5*(N+1)**1.5*exp(1/(12*(N+1)))
    return pi0+merge, pi0, merge
def F(k,j):
    nu=j*k; N=k+nu
    A,_,_=Aup(k,j)
    return ((N+1)/(nu+1))**1.5*(1-2.3e-4)/sqrt(2*pi)*exp(-1/(12*k))*0.5*(Sm**2+Sp**2)/(sqrt(k)*A)
for j in [0.48,0.5,0.6,0.75,1.0]:
    print("F(6668,",j,")=",F(k,j), " Aup=",Aup(k,j))
