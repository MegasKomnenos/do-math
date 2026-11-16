# L9 검산: 9장 수치 상수 재계산 (python -I)
from mpmath import mp, mpf, sqrt, exp, log, pi, quad, floor, ceil
mp.dps = 30
def P(*a): print(*a)

# --- 정리 A+ 상수
P("A+: e^{-1/12}-e^{1/4}/4 =", exp(-mpf(1)/12)-exp(mpf(1)/4)/4, " sqrt(2/pi)*0.5990=", sqrt(2/pi)*mpf('0.5990'), " 1.5/0.477=", 1.5/mpf('0.477'))
# --- psi-two-sided
z32 = mpf('2.61238')
P("psi: 2(2pi)^-1/2 =", 2/sqrt(2*pi), " (2pi)^-1/2*(2+z32/12)=", (2+z32/12)/sqrt(2*pi))
# --- head-sum-1
k = mpf(3132); l = k-1; u0 = k**(-mpf(1)/3)
P("u0=", u0, " k^(2/3)=", k**(mpf(2)/3), " (k-1)/6=", l/6, " k^(2/3)/(k-1)=", k**(mpf(2)/3)/l)
c1max = (1+mpf('0.0684'))**1.5*exp(1/(12*l)); P("c1 max=", c1max)
P("4/3/sqrt(2pi)=", mpf(4)/3/sqrt(2*pi), " 0.5320*1.105=", mpf('0.5320')*mpf('1.105'))
c = 2/sqrt(2*pi); P("consts:", c/7, c/5, c*mpf('3.2')/3, " with 0.7979:", mpf('0.7979')*mpf('3.2')/3)
# step 4
xi=mpf('0.03'); l0=mpf(3131); one=1+1/l0
P("step4: q/l<=", xi*u0*one, " c1<=", (1+xi*u0*one)**1.5*exp(one*u0**3/12), " u_q<=", one**2*(xi*u0+u0**3)**2/2)
br = mpf('0.11399')*xi + mpf('0.15958')*u0**2 + mpf('0.85108')*sqrt(xi)*u0
P("  Phi/xi^2.5 <=", mpf('1.0004')*mpf('1.0035')*mpf('1.0001')*br, "(text 0.01434)")
num = one*mpf('1.0035')*(mpf('0.5320')*xi*u0+mpf('0.7979')*u0**3+mpf('1.0035')*(mpf('0.625')*xi**1.5+sqrt(xi)*u0**2))
P("  E <=", num/mpf('0.1721'), "(text 0.0317)", " L>=", mpf('0.1721')*exp(-mpf('0.0317'))/mpf('1.0024'), "(0.1662)", " 0.1662/0.01434=", mpf('0.1662')/mpf('0.01434'))
# step 5
P("step5: 0.7978*sqrt(.03)=", mpf('0.7978')*sqrt(xi), " 0.8848*u0=", mpf('0.8848')*u0)
for p in [mpf(7)/2, mpf(5)/2, 3, mpf(3)/2, 2, 1]:
    P("   p=",p," xi threshold=", (p*mpf('0.8848')*u0/((p-mpf(1)/2)*mpf('0.7978')))**2)
P("  c5=", mpf('0.7979')*sqrt(xi)*u0**3/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u0))
# step 6
xi=mpf(1); ql = u0*one; c1=(1+ql)**1.5*exp(1/(12*l0)); uq=one**2*(u0+u0**3)**2/2
br=mpf('0.11399')+mpf('0.15958')*u0**2+mpf('0.85108')*u0
Phi=one*c1*exp(uq)*br
den=mpf('0.7978')-mpf('0.8848')*u0
Ebar=c1*one*((mpf('0.5320')*u0+c1*(mpf('0.625')+u0**2))/den+mpf('5.68e-4'))
Lbar=den*exp(-Ebar)/(1+(u0+u0**3)*one)
P("step6: one=",one," q/l=",ql," c1=",c1," uq=",uq," br=",br," Phi=",Phi," den=",den," Ebar=",Ebar," Lbar=",Lbar," R=",Phi/Lbar)
# --- H* t=k+1
P("H* 3/5 e^-1 =", mpf(3)/5*exp(-1))
# --- head-sum-2
P("hs2: 597:", mpf(597)**1.5+9*597, " 598:", mpf(598)**1.5+9*598)
n=mpf(20001); P("  m0(20001)=", floor(n**(mpf(2)/3)-6*n**(mpf(1)/3)), " 6/n^(1/3)=", 6/n**(mpf(1)/3))
P("  phi(7/16)=", 1-mpf('1.5')*mpf(7)/16+(mpf(7)/16)**2/2-(1-mpf(7)/16)**mpf('1.5'))
k=mpf(19404); P("  floor(19404^(2/3))=", floor(k**(mpf(2)/3)), " 16/3 k^(1/3) >= 39 iff k^(1/3)>=", mpf(39)*3/16)
k=mpf(3132); P("  floor(0.75*3132^(2/3))=", floor(mpf('0.75')*k**(mpf(2)/3)))
# --- 9.2 pi_2 bound
P("pi2: sqrt(8/(pi*6669))=", sqrt(8/(pi*6669)))
# --- AR (1): L_*(6668)
k=mpf(6668)
def J1(k):
    c=3/sqrt(k); t0=1/k+c**(mpf(2)/3)
    f=lambda t: (1+t+2/k)**(-mpf(7)/2)*max(0,1-c*(t-1/k)**(-mpf(3)/2))
    return mpf(5)/2*quad(f,[t0,(t0+1)/2,1])
def J2(k):
    c=3*(k-1)*k**(-mpf(3)/2); t0=1/k+c**(mpf(2)/3)
    f=lambda t: (1+t+1/k)**(-mpf(7)/2)*max(0,1-c*(t-1/k)**(-mpf(3)/2))
    return mpf(5)/2*quad(f,[t0,(t0+(k-1)/k)/2,(k-1)/k])
J3=(k/(2*k+1))**mpf('2.5')*(1-3/sqrt(k)); J4=(k/(2*k+1))**mpf('2.5')*(1-3/sqrt(k-1))
j1=J1(k); j2=J2(k)
P("AR: J1=",j1," J2=",j2," J3=",J3," J4=",J4," L*=",j1+j2+J3+J4)
# --- AR (2)
P("AR2: (2pi)^-1/2 e^-1/24 e^-1/(12*3334)=", exp(-mpf(1)/24-mpf(1)/(12*3334))/sqrt(2*pi), " 0.3826*2=",mpf('0.3826')*2)
jstar=ceil((3*k)**(mpf(2)/3)); P("  j*=",jstar," 4.85[sqrt k ((3k)^(2/3)+2)^-1/2 - sqrt2]=", mpf('4.85')*(sqrt(k)/sqrt((3*k)**(mpf(2)/3)+2)-sqrt(2)), " 0.734*6.62=",mpf('0.734')*mpf('6.62'))
P("  range2: 6/0.98*0.95^-1.5=", 6/mpf('0.98')*mpf('0.95')**(-mpf('1.5')))
P("  range3 a: 16.35/(0.05*0.95^1.5)*(1+1/k)^1.5=", mpf('16.35')/(mpf('0.05')*mpf('0.95')**mpf('1.5'))*(1+1/k)**mpf('1.5'), " 353.3/k vs 6.62/sqrt k:", mpf('353.3')/k, mpf('6.62')/sqrt(k))
P("  range3 b: 5.45 k^-1/2 (1+1/k)^1.5 k/(k-j*-1)=", mpf('5.45')/sqrt(k)*(1+1/k)**mpf('1.5')*k/(k-jstar-1), " vs", mpf('6.62')/sqrt(k))
best=0; bq=0
for q in range(1,6668):
    N=k+q; num=min(1,3*k*mpf(q)**(-mpf('1.5'))); den=k*(mpf('0.734')*max(0,mpf(q+1)**(-mpf('0.5'))-(ceil(N/2)+1)**(-mpf('0.5')))+mpf('0.98')/(N+1))
    v=num/den*sqrt(k)
    if v>best: best=v; bq=q
P("  max over q of ratio*sqrt(k):", best, " at q=", bq)
# --- AR (3)
dbar=mpf('6.62')/sqrt(k)
P("AR3: band req=", (1+dbar/2)/(1-dbar/2))
cover=103/sqrt(2*pi)*exp(1/(12*(mpf('1.48')*k+1)))
P("  cover const=", cover, " 41.2*(2/(0.48k-102))^1.5=", mpf('41.2')*(2/(mpf('0.48')*k-102))**mpf('1.5'))
P("  3.394 check:", (2*k/(mpf('0.48')*k**2))**mpf('1.5')*exp(1/(12*(mpf('1.48')*k+1)))/sqrt(2*pi)*k**mpf('1.5'), " 1/1.48=",1/mpf('1.48'))
pi0=mpf('0.8825')/sqrt(k)+mpf('0.72')/k
bulk=1+(1+1/mpf('1.48'))*dbar/(2-dbar)+(pi0+mpf('41.2')*(2/(mpf('0.48')*k-102))**mpf('1.5'))/mpf('1.48')
P("  bulk req=", bulk, " (0.26k+0.5)*3.394k^-1.5+0.676/k =", (mpf('0.26')*k+mpf('0.5'))*mpf('3.394')*k**(-mpf('1.5'))+mpf('0.676')/k, " vs ", pi0)
# --- old-7-26
u = lambda k: 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf('1.5'))/sqrt(k)
Ups = lambda k: (k-1)*u(k)/(2*k+1)
k=mpf(6668); P("7-26: u(6668)=",u(k)," Ups=",Ups(k), " k rhoL(.112k)=", mpf('1.5')*mpf('0.112')/mpf('1.112')*(1-mpf('1.2')/k), " k rhoH(.112k)>=", (1-mpf('1.5')/k)*mpf('0.307')/mpf('1.112')-47/(24*k))
v=mpf('0.7654')
mu=Ups(k)/(mpf('1.5')*(1-mpf('1.2')/k)*(v+Ups(k)*(k+1)/k))
P("  with v=0.7654: k mu/(1-mu)=", k*mu/(1-mu), " 0.1113k=", mpf('0.1113')*k, " k^(1/3) mu/(1-mu)=", k**(mpf(1)/3)*mu/(1-mu))
rH=((1-mpf('1.5')/k)*mpf('0.1535')-47/(24*k)); P("  k rhoH(3k+1)=", rH, " Y(3k+1) with v=.7654:", rH*v-Ups(k)*(1-(1+1/k)*rH))
# --- old-7-28
P("7-28: 1.5*(1-1.2/k)*0.7654/1.2366=", mpf('1.5')*(1-mpf('1.2')/k)*v/mpf('1.2366'), " k/(20(k-1))=", k/(20*(k-1)))
k=mpf(48966); P("  Ups(48966)=",Ups(k)," (1/20)(1-1/k)^103=", (1-1/k)**103/20); k=mpf(48965); P("  Ups(48965)=",Ups(k)," rhs=",(1-1/k)**103/20)
# --- 9.5
k=mpf(6668); P("9.5: 0.48k-1-8k^(2/3)=", mpf('0.48')*k-1-8*k**(mpf(2)/3), " e^{-1/(12*366)}=", exp(-1/mpf(12*366)))
P("  (2pi)^-1/2 e^-1/12=", exp(-mpf(1)/12)/sqrt(2*pi), " 1.46036+2.61238/12=", mpf('1.46036')+z32/12)
P("  0.3989*(2-1.678)=", mpf('0.3989')*(2-mpf('1.678')), " exp(-1)=", exp(-1), " 0.000084 sqrt d coef:", 2*(1/sqrt(2*pi)-mpf('0.3989')), " const:", -(mpf('1.67806')/sqrt(2*pi)-mpf('0.3989')*mpf('1.678')))
P("  (1+1/6667)^(2/3)=", (1+mpf(1)/6667)**(mpf(2)/3), " 0.08k^(2/3)-1=", mpf('0.08')*k**(mpf(2)/3)-1, " Psi^lb zero at", (mpf('1.678')/2)**2)
P("  4k^(2/3) vs 6(k-1)^(2/3):", 4*k**(mpf(2)/3), 6*(k-1)**(mpf(2)/3), " 0.08/3*1.678=", mpf('0.08')/3*mpf('1.678'))
P("  denominator positivity j=1:", mpf('0.7979')-mpf('1.5')*mpf('0.3989')*2/2-mpf(15)/8*mpf('0.367')*mpf(2)/3/4-mpf(35)/16*mpf('0.367')*mpf(2)/5/8)
