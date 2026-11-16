# O4: 5.5.5-5.5.9 의 상수·닫힌 꼴 검산 (mpmath 50자리)
from mpmath import mp, mpf, sqrt, exp, log, pi, erfc, quad, inf, floor, ceil, e as E
mp.dps = 50
# --- 5.5.2: rho_0 <= 0.75(1.1y)^{2/3}+1 의 t-1 <= 1.1y 조건, t_0<=n 조건
y=mpf(25000); print("0.75(1.1y)^(2/3) at y=25000:", 0.75*(1.1*y)**(mpf(2)/3), " 0.1y=",0.1*y)
n=mpf(50001); print("10((n+1)/2)^(2/3) - (6n^(2/3)+2) =", 10*((n+1)/2)**(mpf(2)/3)-(6*n**(mpf(2)/3)+2))
# --- 5-30 상수
n=mpf(50001)
v1 = (2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
print("5-30 y<=2n/3 case:", v1, "<=0.0133", v1<=0.0133)
v2 = (mpf(1.5)/10)**1.5; print("(0.15)^1.5=",v2, "<=0.0581", v2<=0.0581)
v3 = (2*pi)**-0.5*mpf('0.0581')*(1+1/n)**1.5*exp(1/(12*(n+1))); print("top_pi bound:",v3,"<=0.0232",v3<=0.0232)
v4 = exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n-1))); print("pi_n(n-1) bound:",v4,"<0.1354",v4<0.1354)
print("bracket:", exp(-1)-mpf('0.1354')-mpf('0.0232'))
# --- bt-tail ti 닫힌 꼴 수치 대조
def ti_int(s,b,W0): return quad(lambda u: u**-1.5*exp(-s*u-b/u), [W0, inf])
def ti_cf(s,b,W0): return 0.5*sqrt(pi/b)*(exp(-2*sqrt(s*b))*erfc(sqrt(s*W0)-sqrt(b/W0))-exp(2*sqrt(s*b))*erfc(sqrt(s*W0)+sqrt(b/W0)))
for (s,b,W0) in [(mpf('0.01'),mpf(2),mpf(5)),(mpf('0.5'),mpf('0.5'),mpf(1)),(mpf(0),mpf(8),mpf(3)),(mpf('1e-6'),mpf(50),mpf(40))]:
    print("ti", s,b,W0, ti_int(s,b,W0), ti_cf(s,b,W0))
# --- bt-tail (가) 수치
from math import factorial
def BT(z,D): return mpf(z)/D*exp(-D)*mpf(D)**(D-z)/factorial(D-z)
bad=0
for z in range(1,40):
    for D in range(z+1, 200):
        W=D-z; ub = z/sqrt(2*pi)/D*W**-0.5*exp(-mpf(z)**2/(2*W)+mpf(z)**3/(3*W**2))
        if BT(z,D) > ub*(1+mpf('1e-30')): bad+=1
print("bt-tail(가) 위반:", bad)
# --- stop-lower 하계 at Y=25000 (정확식: pi0_{Y+j}(Y)=1-sum_{i<=j} Bor(i)Bor(U-i)/Bor(U))
def Bor(m): m=mpf(m); return exp(-m)*m**(m-1)/exp(mp.loggamma(m+1))
Y=25000; bad=0; worst=mpf(0)
for j in [1,2,5,10,50,100,500,1000,3000,6000,6250]:
    U=Y+j+1
    pi0 = 1-sum(Bor(i)*Bor(U-i)/Bor(U) for i in range(1,j+1))
    tail = 1-sum(Bor(i) for i in range(1,j+1))
    lb = tail-mpf('1.6')*sqrt(j)/Y
    if pi0 < lb: bad+=1
    worst=max(worst, (tail-pi0)*Y/sqrt(j))
print("stop-lower 하계 위반:", bad, " max (Pr(beta>j)-pi0)*Y/sqrt(j) =", worst)
# --- scaled-integrand (마) 상수
h0=mpf('0.0342'); umax=sqrt(6*h0); c3=1/sqrt(2)-umax/3
print("h0^3>=1/25000:", h0**3>=mpf(1)/25000, " umax=",umax," c3=",c3, ">=0.556", c3>=0.556)
f12 = c3*mpf(12)**1.5-12-log(sqrt(2)*(1+6*h0)*12/c3); print("f(12)=",f12)
def rhobar(th):
    yv=max(th/2, th-h0)
    return sqrt(2)*th**1.5*exp(-th*sqrt(yv)+min(th**2*h0, umax*th**1.5)/3)*(1+min(th*h0**2,6*h0))/(sqrt(yv)-min(th*h0,umax*sqrt(th))/3)
print("rhobar(12), e^-12:", rhobar(mpf(12)), exp(-12), " rhobar(20)<=e^-20:", rhobar(mpf(20))<=exp(-20))
O = lambda Yv: 1/Yv**2*sqrt(12/pi)*Yv**(mpf(1)/3)*sqrt(2/Yv)*(Yv+1)
print("O(25000)=", O(mpf(25000)))
# --- hover-tail hv at 2064, right-part constants
chi=mpf(2064); hv = chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi)); print("hv*sqrt(chi)=",hv*sqrt(chi),"<=1.6932",hv*sqrt(chi)<=1.6932)
y=mpf(33334); t=y**(mpf(1)/3)
eh = mpf('1.6932')*(t/10+1)*(2*t**2-mpf('7.5'))**-0.5; print("eps_hov at y=33334:",eh,"<=0.1573",eh<=0.1573)
r=mpf(10356); print("r>=10y^(2/3)-1 at y=33334:", 10*y**(mpf(2)/3)-1)
print("0.2r-7.3 at r=10356:", 0.2*r-7.3)
print("sqrt(2/pi)/sqrt(2064)=", sqrt(2/pi)/sqrt(2064))
print("(2pi)^-1/2 (1.50003/0.9199)^1.5 =", (2*pi)**-0.5*(mpf('1.50003')/mpf('0.9199'))**1.5)
print("0.24924/sqrt(10357)=", mpf('0.24924')/sqrt(10357))
rr=mpf(10357)  # r+1
print("0.92007(r+1)-1 >= 0.9199(r+1)?", mpf('0.92007')*rr-1 >= mpf('0.9199')*rr)
print("(r+1)/(r-rho0) max:", 1/(1-mpf('0.07993')-2/rr))
print("(0.7993+2 y^-2/3)^1.5 =", (mpf('0.7993')+2*y**(-mpf(2)/3))**1.5)
rho0max = mpf('0.07993')*rr+1
print("eps0 bound:", mpf(1.5)*rho0max/(rr-rho0max))
print("(1+rho0/y)^1.5:", (1+(mpf('0.7993')*y**(mpf(2)/3)+1)/y)**1.5)
W = (2*pi)**-0.5*mpf(2)/3*mpf('0.7172')*mpf(1.5)*mpf('1.0872')*mpf('1.0376')*exp(mpf('0.1305')+mpf(1)/400008)
print("(r+1)W/y bound:", W, "<=0.3678", W<=0.3678)
c4 = mpf(1)/156+1/(12*y)+1/(12*mpf(50002)); print("e^-c4=",exp(-c4),">=0.9936",exp(-c4)>=0.9936)
val = (1-mpf('0.1573'))*mpf('0.71216')*mpf('0.9936')*mpf('1.9366')-mpf('0.3678'); print("0.7869 check:",val, val>=0.7869)
print("Psi_R at 2/3:", mpf('0.7869')*2/3-mpf('0.3334')-mpf('0.0001'))
# 2n/3 at n=50001
print("2*50001/3=", mpf(2)*50001/3)
# band-inequality 조건
n=mpf(50001); print("0.4n/3=",0.4*n/3," 6(2n/3)^(2/3)+1=",6*(2*n/3)**(mpf(2)/3)+1)
print("0.75(1.1*2n/3)^(2/3)+1=",0.75*(1.1*2*n/3)**(mpf(2)/3)+1," 0.7n/3=",0.7*n/3)
lb=mpf(2)/3; print("deriv 0.4(1-lb)-4 lb^(2/3) n^(-1/3) =", 0.4*(1-lb)-4*lb**(mpf(2)/3)*n**(-mpf(1)/3))
