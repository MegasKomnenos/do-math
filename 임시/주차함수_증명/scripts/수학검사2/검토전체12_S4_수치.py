# 검토전체12 S4: 장5B의 수치 주장 재계산
from math import *
n=50001
print("5.5.2: 10*((n+1)/2)^(2/3) vs 6n^(2/3)+2 :", 10*((n+1)/2)**(2/3), 6*n**(2/3)+2)
y=25000
print("rho0 bound: 0.75*(1.1y)^(2/3)+1 =",0.75*(1.1*y)**(2/3)+1, " 0.1y=",0.1*y)
# 5-30
v1=(2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
print("top_pi case y<=2n/3:",v1)
print("(0.15)^(3/2)=",0.15**1.5, " *(2pi)^-1/2 * corr =",(2*pi)**-0.5*0.0581*(1+1/n)**1.5*exp(1/(12*(n+1))))
print("pi_n(n-1) bound:",exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n+1))))
print("bracket:",exp(-1)-0.1354-0.0232)
# loss rate claim: (m+d+2)/((w+2)(m+1)) <= z_m(d) for 1<=d<=m/2
bad=0
for m in range(2,400):
    for d in range(1,m//2+1):
        w=m-d
        lhs=(m+d+2)/((w+2)*(m+1)); z=exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))
        if lhs>z: bad+=1
print("loss-rate claim violations (m<400):",bad)
# h0
print("0.0342^3=",0.0342**3, "1/25000=",1/25000)
ups=sqrt(6*0.0342); c3=1/sqrt(2)-ups/3
print("ups_max=",ups,"c2=",1/(2*(1-ups)),"c3=",c3)
f=lambda th: c3*th**1.5-th-log(sqrt(2)*(1+6*0.0342)*th/c3)
print("f(12)=",f(12), " arg log=",sqrt(2)*(1+6*0.0342)*12/c3)
# stop-lower constants
print("1.5*0.95^-2.5=",1.5*0.95**-2.5, " chord:",(0.8**-1.5-1)/0.2, " 4/sqrt(2pi)=",4/sqrt(2*pi))
# right-part
y=33334; r=10357
print("10y^(2/3)-1=",10*y**(2/3)-1)
print("chi_w >= 0.2r-7.3 =",0.2*r-7.3)
print("e^-c4 >=",exp(-1/156-1/(12*y)-1/(12*(n+1))))
hv=2064**-0.5*(2/sqrt(pi)*(1+1/2064)+1/sqrt(pi)); print("hv coef:",hv*sqrt(2064))
t=y**(1/3); print("eps_hov:",1.6932*(t/10+1)/sqrt(2*t*t-7.5))
print("sqrt(2/pi)/sqrt(2064)=",sqrt(2/pi)/sqrt(2064))
print("0.75*1.1^(2/3)=",0.75*1.1**(2/3))
print("pi_n(t0-1) coef:",(2*pi)**-0.5*(1.50003/0.9199)**1.5*exp(1/(12*50002)))
print("chi2 pi:",0.24924/sqrt(r+1))
print("(r+1)/(r-rho0):",1/(0.92007-2/(r+1)))
print("(0.7993y^(2/3)+2)^(3/2)/y:",(0.7993*y**(2/3)+2)**1.5/y)
print("eps0:",1.5*(0.07993*(r+1)+1)/(0.92007*(r+1)-1))
print("(1+rho0/y)^1.5:",(1+(0.7993*y**(2/3)+1)/y)**1.5)
W=(2*pi)**-0.5*2/3*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008); print("W bound:",W)
print("0.8427*0.71216*0.9936*1.9366-0.3678=",0.8427*0.71216*0.9936*1.9366-0.3678)
print("Psi_R at 2/3:",0.7869*2/3-1/3-2.5e-5)
# band-inequality conditions at n=50001, y=2n/3
y=2*n/3; print("0.4(n-y)=",0.4*(n-y)," 6y^(2/3)+1=",6*y**(2/3)+1)
print("c4 denom deriv at lb=2/3:",0.4*(1/3)-4*(2/3)**(2/3)*n**(-1/3))
# 5-20 convexity sanity & 5-19 identity numeric check small n
from fractions import Fraction as F
def p(m): return 1 if m==0 else (m+1)**(m-1)
from functools import lru_cache
@lru_cache(None)
def A(n,l):
    if l<0: return 0
    if n==0: return 1
    # V_{n,l}=sum_j C(n-1,j) min(j+1,l+1) V_j V_{n-1-j}
    return sum(comb(n-1,j)*min(j+1,l+1)*A(j,l)*A(n-1-j,l) for j in range(n))
def c(m,Y): return F(A(m,Y)-A(m,Y-1),p(m))
def sT(t,Y): return F(1) if t<=Y else F(Y*A(t-1,Y-1),t**(t-1))
def x(t,y): return sT(t,y+1)-2*sT(t,y)+sT(t,y-1)
def pin(n,t): return F(comb(n,t)*t**(t-1)*p(n-t),p(n))
ok=True
for nn in range(5,16):
    for yy in range((nn+1+1)//2, nn):
        lhs=c(nn,yy)-c(nn,yy-1); rhs=sum(pin(nn,t)*x(t,yy) for t in range(yy,nn+1))
        if lhs!=rhs: ok=False; print("5-19 fail",nn,yy)
        # 5-27 identity
        P=sum(x(t,yy) for t in range(yy,nn+1))
        P2=-F(1,yy)+sum(((yy+1)*c(m,yy)-(yy-1)*c(m,yy-1))/(m+1) for m in range(yy,nn))
        if P!=P2: ok=False; print("5-27 fail",nn,yy)
print("5-19/5-27 identities exact check:",ok)
# 5-28 numeric check
bad=0
for m in range(2,14):
    for d in range(1,m//2+1):
        w=m-d
        z=exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))
        if float(c(m+1,w+1)) < (1-z)*float(c(m,w))-1e-15: bad+=1; print("5-28 fail",m,d)
print("5-28 violations:",bad)
