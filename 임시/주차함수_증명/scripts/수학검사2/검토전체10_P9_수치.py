# P9: 9장 수치 재계산 (정리 A+, 보조정리 psi, 정리 1·2, H*+, AR, 띠, 쌍)
from mpmath import mp, mpf, sqrt, exp, e, pi, floor, ceil, quad, zeta
mp.dps = 30
def P(*a): print(*a)

# --- 정리 A+ (4) 상수 ---
br = exp(-mpf(1)/12) - exp(mpf(1)/4)/4
P("A+ bracket e^{-1/12}-e^{1/4}/4 =", br, " (2/pi)^{1/2}*br =", sqrt(2/pi)*br, " 3/(2*0.477)=", 3/(2*mpf('0.477')))

# --- 보조정리 psi-two-sided ---
P("2(2pi)^{-1/2} =", 2/sqrt(2*pi), " (2pi)^{-1/2}(2+z32/12) z32=2.61238 =", (2+mpf('2.61238')/12)/sqrt(2*pi))

# --- 정리 head-sum-1 ---
u1 = mpf(3132)**(-mpf(1)/3); u2 = mpf(19404)**(-mpf(1)/3)
P("upsilon1 =", u1, " upsilon2 =", u2)
P("3132^{2/3} =", mpf(3132)**(mpf(2)/3), " 3131/6 =", mpf(3131)/6, " k^{2/3}/(k-1) =", mpf(3132)**(mpf(2)/3)/3131)
def c1f(xi,u):
    l1=1/(1-u**3); return (1+xi*u*l1)**mpf('1.5')*exp(l1*u**3/12)
def uq(xi,u):
    l1=1/(1-u**3); return l1**2*(xi*u+u**3)**2/2
def Phi(xi,u):
    l1=1/(1-u**3)
    return l1*c1f(xi,u)*exp(uq(xi,u))*(mpf('0.11399')*xi**mpf('3.5')+mpf('0.15958')*xi**mpf('2.5')*u**2+mpf('0.85108')*xi**3*u)
def Ecal(xi,u):
    l1=1/(1-u**3); c1=c1f(xi,u)
    return c1*l1*(mpf('0.5320')*xi**mpf('1.5')*u+mpf('0.7979')*sqrt(xi)*u**3+c1*(mpf('0.625')*xi**2+xi*u**2))/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u)
def Lcal(xi,u):
    l1=1/(1-u**3)
    return (mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u)*exp(-Ecal(xi,u))/(1+(xi*u+u**3)*l1)
P("2(2pi)^{-1/2}/7,/5,*3.2/3 =", 2/sqrt(2*pi)/7, 2/sqrt(2*pi)/5, 2/sqrt(2*pi)*mpf('3.2')/3)
P("(4/3)(2pi)^{-1/2} =", mpf(4)/3/sqrt(2*pi))
xi=mpf('0.03')
P("step4: q/l <=", xi*u1*(1+mpf(1)/3131), " c1 <=", c1f(xi,u1), " u_q <=", uq(xi,u1), " 1+1/l =", 1+mpf(1)/3131)
P("step4 Phi/xi^{5/2} bound =", mpf('1.0040')*(mpf('0.11399')*xi+mpf('0.15958')*u1**2+mpf('0.85108')*sqrt(xi)*u1), " actual Phi(0.03,u1)/xi^2.5 =", Phi(xi,u1)/xi**mpf('2.5'))
num_over_sqrt = c1f(xi,u1)*(1+mpf(1)/3131)*(mpf('0.5320')*xi*u1+mpf('0.7979')*u1**3+c1f(xi,u1)*(mpf('0.625')*xi**mpf('1.5')+sqrt(xi)*u1**2))
P("step4 E bound (num/sqrt xi)/0.1721 =", num_over_sqrt/mpf('0.1721'), " actual E(0.03,u1)=", Ecal(xi,u1))
P("step4 L denom <=", 1+(xi*u1+u1**3)*mpf('1.0004'), " L/sqrt(xi) >=", mpf('0.1721')*exp(-mpf('0.0317'))/mpf('1.0024'), " L/Phi at 0.03:", Lcal(xi,u1)/Phi(xi,u1), " 11.5/xi^2=", mpf('11.5')/xi**2)
for p in [mpf(7)/2, mpf(5)/2, mpf(3), mpf(3)/2, mpf(2), mpf(1)]:
    thr = (p*mpf('0.8848')*u1/((p-mpf('0.5'))*mpf('0.7978')))**2
    P("  p=",p," threshold xi =",thr)
P("0.7978*sqrt(0.03) =", mpf('0.7978')*sqrt(mpf('0.03')), " 0.8848*u1 =", mpf('0.8848')*u1)
c5 = mpf('0.7979')*sqrt(mpf('0.03'))*u1**3/(mpf('0.7978')*sqrt(mpf('0.03'))-mpf('0.8848')*u1)
P("c5 =", c5)
xi=mpf(1); l0=mpf(3131)
P("step6: 1+1/l0 =", 1+1/l0, " q/l =", xi*u1*(1+1/l0), " c1 =", c1f(xi,u1), " u_q <=", uq(xi,u1), " e^uq =", exp(uq(xi,u1)))
brk = mpf('0.11399')+mpf('0.15958')*u1**2+mpf('0.85108')*u1
P("  bracket =", brk, " Phi =", Phi(xi,u1))
den = mpf('0.7978')-mpf('0.8848')*u1
c1=c1f(xi,u1)
numbr = mpf('0.5320')*u1 + c1*(mpf('0.625')+u1**2)
Ebar = c1*(1+1/l0)*(numbr/den + c5)
Lbar = den*exp(-Ebar)/(1+(u1+u1**3)*(1+1/l0))
P("  den =", den, " numbr =", numbr, " c1(1+1/l0)=", c1*(1+1/l0), " Ebar =", Ebar, " Lbar =", Lbar, " Rbar(1) =", Phi(xi,u1)/Lbar)
# 직접 비교 R(1), 그리고 격자에서 Phi<=L 확인
P("  direct R(1,u1) =", Phi(mpf(1),u1)/Lcal(mpf(1),u1))
worst = 0
for i in range(1,2001):
    x = mpf(i)/2000
    if x < 2*u1**2: continue
    r = Phi(x,u1)/Lcal(x,u1)
    if r > worst: worst = r
P("  max Phi/L on grid xi in [2u1^2,1], u=u1:", worst)

# --- 정리 head-sum-2 ---
P("597^1.5+9*597 =", mpf(597)**mpf('1.5')+9*597, " 598:", mpf(598)**mpf('1.5')+9*598)
P("floor(19404^{2/3}) =", floor(mpf(19404)**(mpf(2)/3)), " 20001^{2/3}-6*20001^{1/3} =", mpf(20001)**(mpf(2)/3)-6*mpf(20001)**(mpf(1)/3))
P("16/3*7.3125 =", mpf(16)/3*mpf('7.3125'), " floor(0.75*3132^{2/3}) =", floor(mpf('0.75')*mpf(3132)**(mpf(2)/3)))

# --- H*+ t=k+1 ---
P("(3/5)e^{-1} =", mpf(3)/5/e)
def u_fun(k):
    k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf('1.5'))/sqrt(k)
def Ups(k):
    k=mpf(k); return (k-1)*u_fun(k)/(2*k+1)
P("u(3131)/2 =", u_fun(3131)/2, " Ups(48966)=", Ups(48966), " (1/20)(1-1/k)^103 =", (1-mpf(1)/48966)**103/20, " Ups(48965)=", Ups(48965), " rhs(48965)=", (1-mpf(1)/48965)**103/20)

# --- centroid ---
P("sqrt(8/(pi*6669)) =", sqrt(8/(pi*6669)), " sqrt(8/(pi*6670)) =", sqrt(8/(pi*6670)))

# --- AR (1) 적분 ---
k=mpf(6668)
def J1(k):
    f=lambda t: (1+t+2/k)**(-mpf('3.5'))*max(0,1-3/sqrt(k)*(t-1/k)**(-mpf('1.5')))
    t0 = 1/k + (3/sqrt(k))**(mpf(2)/3)
    return mpf('2.5')*quad(f,[t0,1])
def J2(k):
    f=lambda t: (1+t+1/k)**(-mpf('3.5'))*max(0,1-3*(k-1)/k**mpf('1.5')*(t-1/k)**(-mpf('1.5')))
    t0 = 1/k + (3*(k-1)/k**mpf('1.5'))**(mpf(2)/3)
    return mpf('2.5')*quad(f,[t0,(k-1)/k])
J3=(k/(2*k+1))**mpf('2.5')*(1-3/sqrt(k)); J4=(k/(2*k+1))**mpf('2.5')*(1-3/sqrt(k-1))
j1=J1(k); j2=J2(k)
P("J1,J2,J3,J4 =", j1, j2, J3, J4, " sum =", j1+j2+J3+J4)
P("(2pi)^{-1/2}e^{-1/24}e^{-1/(12*3334)} =", exp(-mpf(1)/24-mpf(1)/(12*3334))/sqrt(2*pi), " 0.734*6.62=", mpf('0.734')*mpf('6.62'))
js = ceil((3*k)**(mpf(2)/3))
P("j* =", js, " 4.85[sqrt k ((3k)^{2/3}+2)^{-1/2}-sqrt2] =", mpf('4.85')*(sqrt(k)*((3*k)**(mpf(2)/3)+2)**(-mpf('0.5'))-sqrt(2)))
P("second 6.1224*0.95^{-1.5} =", mpf('6.1224')*mpf('0.95')**(-mpf('1.5')), " 6/0.98=", 6/mpf('0.98'), " 12/0.734=", 12/mpf('0.734'))
P("third iota=0.05k: 16.35*((k+1)/(0.95k))^{1.5}/0.05 (times 1/k) =", mpf('16.35')*((k+1)/(mpf('0.95')*k))**mpf('1.5')/mpf('0.05'))
P("third iota=k-j*-1: 5.45(1+1/k)^{1.5} k/(k-j*-1) =", mpf('5.45')*(1+1/k)**mpf('1.5')*k/(k-js-1), " vs 6.62")
dbar = mpf('6.62')/sqrt(k)
P("103*(2pi)^{-1/2}e^{1/(12*6670)} =", 103/sqrt(2*pi)*exp(mpf(1)/(12*6670)), " (2pi)^{-1/2}e^{..}(2/0.48)^{1.5} =", exp(mpf(1)/(12*6670))/sqrt(2*pi)*(2/mpf('0.48'))**mpf('1.5'), " 0.26*3.394=", mpf('0.26')*mpf('3.394'), " 1/1.48=", 1/mpf('1.48'))
bulk = 1+mpf('1.676')*dbar/(2-dbar)+mpf('0.676')*(mpf('0.8825')/sqrt(k)+mpf('0.72')/k+mpf('41.2')*(2/(mpf('0.48')*k-102))**mpf('1.5'))
P("dbar=",dbar," bulk requirement =", bulk, " band requirement =", (1+dbar/2)/(1-dbar/2))
P("0.5*3.394/sqrt(6668) =", (mpf('0.5')*mpf('3.394'))/sqrt(k))

# --- 띠: old-7-26 (i) ---
P("1.5*0.112/1.112 =", mpf('1.5')*mpf('0.112')/mpf('1.112'), " (1-1.5/k)*0.307/1.112-47/(24k) =", (1-mpf('1.5')/k)*mpf('0.307')/mpf('1.112')-47/(24*k))
P("(iii) kH(3k+1) =", (1-3/(2*k))*mpf('0.1535')-47/(24*k))
P("old-7-28(2): 1.112^2 =", mpf('1.112')**2, " 1.5*(1-1.2/k)*0.7654/1.2366 =", mpf('1.5')*(1-mpf('1.2')/k)*mpf('0.7654')/mpf('1.2366'), " 0.05*k/(k-1)=", mpf('0.05')*k/(k-1))
# v(k), mu(k), 경계값
def v_fun(k):
    k=mpf(k); vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**(-mpf('1.5')))-2*u_fun(k)-mpf('50.62')/sqrt(k-1)
def mu_fun(k):
    k=mpf(k); return Ups(k)/(mpf('1.5')*(1-mpf('1.2')/k)*(v_fun(k)+Ups(k)*(k+1)/k))
for kk in [6667,6668,10000]:
    P("k=",kk," v(k)=",v_fun(kk)," Ups=",Ups(kk)," mu=",mu_fun(kk)," k mu/(1-mu)=",kk*mu_fun(kk)/(1-mu_fun(kk))," k^{1/3}mu/(1-mu)=",mpf(kk)**(mpf(1)/3)*mu_fun(kk)/(1-mu_fun(kk)))
k=mpf(6668)
rhoH = (1-3/(2*k))*mpf('0.1535')-47/(24*k)
P("Y(3k+1) at 6668 =", rhoH*v_fun(6668)-Ups(6668)*(1-(1+1/k)*rhoH))
# 감소성 표본
prev=None
for kk in [6668,7000,8000,10000,20000,50000,100000,1000000]:
    val = mpf(kk)**(mpf(1)/3)*mu_fun(kk)/(1-mu_fun(kk))
    P("  k^{1/3}mu/(1-mu) at",kk,"=",val)

# --- 쌍: old-7-38 ---
P("0.48k-1-8k^{2/3} at 6668 =", mpf('0.48')*k-1-8*k**(mpf(2)/3), " integer floor(0.48k)-2floor(4k^{2/3}) =", floor(mpf('0.48')*k)-2*floor(4*k**(mpf(2)/3)), " e^{-1/(12*366)} =", exp(-mpf(1)/(12*366)), " (16/3/0.48)^3 =", (mpf(16)/3/mpf('0.48'))**3)
P("1.46036+2.61238/12 =", mpf('1.46036')+mpf('2.61238')/12, " 0.398942*1.67806 =", mpf('0.398942')*mpf('1.67806'), " 0.3989*1.678=", mpf('0.3989')*mpf('1.678'), " Psi(1)=e^-1=", 1/e, " 0.3989*0.322=", mpf('0.3989')*mpf('0.322'))
P("(2pi)^{-1/2}e^{-1/12} =", exp(-mpf(1)/12)/sqrt(2*pi), " zeta(1/2)=", zeta(mpf('0.5')), " zeta(3/2)=", zeta(mpf('1.5')))
P("old-7-41: (1+1/6667)^{2/3}-1 =", (1+mpf(1)/6667)**(mpf(2)/3)-1)
P("old-7-42: 0.08*6668^{2/3} =", mpf('0.08')*k**(mpf(2)/3), " Psi^lb zero at (1.678/2)^2 =", (mpf('1.678')/2)**2)
P("pair-one-variable: 0.08*1.678/3 =", mpf('0.08')*mpf('1.678')/3, " 1.678/0.0447 =", mpf('1.678')/mpf('0.0447'), " ^1.5:", (mpf('1.678')/mpf('0.0447'))**mpf('1.5'))
P("1/(12*(k+1)) at 6668:", 1/(12*(k+1)))
# 보조정리 old-7-2 뒤: N+1>=6669 -> 0.98
P("1-sqrt(8/(pi*6669)) =", 1-sqrt(8/(pi*6669)))
