# -*- coding: utf-8 -*-
# 검토전체15 F4: 장5B(5.5절) 수치·항등식 검산. python -I 로 실행.
import math, sys
from fractions import Fraction as Fr
from math import lgamma, exp, log, sqrt, pi, erfc, floor, ceil

out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

# ---------- 정확 개수 A_{n,l}=V_{n,l} (허용 숲 수), p_n ----------
NMAX = 130
pn = [ (n+1)**(n-1) if n>=1 else 1 for n in range(NMAX+2) ]
binom = [[0]*(NMAX+2) for _ in range(NMAX+2)]
for n in range(NMAX+2):
    binom[n][0]=1
    for k in range(1,n+1): binom[n][k]=binom[n-1][k-1]+binom[n-1][k]
Acache = {}
def A(n,l):
    # 허용 숲 수 V_{n,l}: V' = V T', T'_j = min(j+1,l+1) V_j
    if l < 0: return 0
    if n == 0: return 1
    key=(n,l)
    if key in Acache: return Acache[key]
    if l not in Acache:
        pass
    # 열 l 전체를 한 번에 채운다
    V=[1]
    for m in range(1,NMAX+2):
        s=0
        for j in range(0,m):
            s += binom[m-1][j]*min(j+1,l+1)*V[j]*V[m-1-j]
        V.append(s)
    for m in range(NMAX+2): Acache[(m,l)]=V[m]
    return Acache[key]
def b(n,l): return A(n,l)-A(n,l-1)
def s(m,y): return Fr(A(m,y-1), pn[m])          # 생존 확률
def c(m,Y): return Fr(b(m,Y), pn[m])             # 수준 질량
def sT(t,Y):                                     # 나무 생존 확률
    if t<=Y: return Fr(1)
    return Fr(Y*A(t-1,Y-1), t**(t-1))
def xt(t,y): return sT(t,y+1)-2*sT(t,y)+sT(t,y-1)
def pi_n(n,t): return Fr(binom[n][t]*t**(t-1)*pn[n-t], pn[n])
def pi0(n,y):                                    # 쪼개짐 확률: 모든 나무 크기 <= y
    W=[1]
    for m in range(1,n+1):
        W.append(sum(binom[m-1][s_-1]*s_**(s_-1)*W[m-s_] for s_ in range(1,min(m,y)+1)))
    return Fr(W[n], pn[n])
def Bor(m): return exp(-m+(m-1)*log(m)-lgamma(m+1))
def BorT(z,D):                                   # Borel-Tanner
    if D<z: return 0.0
    return z/D*exp(-D+(D-z)*log(D)-lgamma(D-z+1)) if D>z else z/D*exp(-D)
def Ren(j): return j*Bor(j)

P("== 1. 보조정리 5-19 열 재귀와 5-27 기저 항등식 (정확 유리수) ==")
bad=0
for n in range(3,41):
    for y in range((n+1)//2 + ((n+1)%2), n):
        if 2*y < n+1: continue
        lhs = c(n,y)-c(n,y-1)
        rhs = sum(pi_n(n,t)*xt(t,y) for t in range(y,n+1))
        if lhs!=rhs: bad+=1; P("  5-19 불일치", n,y)
        Pn = sum(xt(t,y) for t in range(y,n+1))
        rhs2 = Fr(-1,y)+sum(((y+1)*c(m,y)-(y-1)*c(m,y-1))/(m+1) for m in range(y,n))
        if Pn!=rhs2: bad+=1; P("  5-27 불일치", n,y)
P("  n<=40 전부 확인, 불일치", bad)

P("== 2. x_y(y)=-1/y, t>=y+1 식, 5-24 방문확률=문턱 부분나무 기대수 ==")
bad=0
for y in range(2,30):
    if xt(y,y)!=Fr(-1,y): bad+=1
    for t in range(y+1,2*y+5):
        if xt(t,y)!=Fr(1,t)*((y+1)*c(t-1,y)-(y-1)*c(t-1,y-1)): bad+=1
for t in range(3,60):
    for s_ in range(t//2+1,t):
        v1 = Fr(binom[t][s_]*s_**(s_-1)*(t-s_)**(t-s_), t**(t-1))
        v2 = Ren(t-s_)*Bor(s_)/Bor(t)
        if abs(float(v1)-v2)>1e-9*max(1,v2): bad+=1
P("  불일치", bad)

P("== 3. 따름정리 6:cor-L  yP_n(y) >= -1 - y(y-1)c_{n-1}(y-1)/n ==")
bad=0; minslack=None
for y in range(2,45):
    for n in range(y+1,2*y+2):
        Pn = sum(xt(t,y) for t in range(y,n+1))
        slack = y*Pn+1+Fr(y*(y-1),n)*c(n-1,y-1)
        if slack<0: bad+=1; P("  위반",n,y,float(slack))
        if minslack is None or slack<minslack: minslack=slack
P("  위반", bad, " 최소 여유", float(minslack))

P("== 4. 정리 5-28  c_{m+1}(w+1) >= (1-z_m(d)) c_m(w) ,  1<=d<=m/2 ==")
bad=0; worst=1e9
for m in range(2,100):
    for d in range(1,m//2+1):
        w=m-d
        z = exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))
        lhs=float(c(m+1,w+1)); rhs=(1-z)*float(c(m,w))
        if rhs>0:
            r=lhs/rhs
            if r<1-1e-12: bad+=1; P("  위반",m,d,r)
            worst=min(worst,r)
P("  위반",bad," 최소 비 lhs/((1-z)c_m(w)) =",worst)
# 손실률 비교: (m+d+2)/((w+2)(m+1)) <= z_m(d)
bad=0
for m in range(2,400):
    for d in range(1,m//2+1):
        w=m-d
        if (m+d+2)/((w+2)*(m+1)) > exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))+1e-15: bad+=1
P("  (m+d+2)/((w+2)(m+1)) <= z_m(d) 위반", bad)

P("== 5. 명제 5-22 Abel 환원 (IH 성립하는 (n,y)에서, 정확 유리수) ==")
def t0(y):
    t=y+2
    while not (y <= (t-1)-floor(0.75*(t-1)**(2/3))): t+=1
    return t
bad=0; cnt=0
for n in range(6,60):
    for y in range((n+1)//2+((n+1)%2), n):
        if 2*y<n+1: continue
        T0=t0(y)
        if T0>n: continue
        IH = all(b(m,y)>=b(m,y-1) for m in range(T0-1,n))
        lhs=c(n,y)-c(n,y-1)
        Pn=sum(xt(t,y) for t in range(y,n+1))
        tail=lambda s_: sum(xt(t,y) for t in range(s_+1,n+1))
        ident=pi_n(n,y)*Pn+sum((pi_n(n,s_+1)-pi_n(n,s_))*tail(s_) for s_ in range(y,n))
        if ident!=lhs: bad+=1; P("  재배열 항등식 불일치",n,y)
        if not IH: continue
        cnt+=1
        first=pi_n(n,y)*Pn
        win=sum((pi_n(n,t)-pi_n(n,y))*max(-xt(t,y),0) for t in range(y+1,T0))
        pos=sum((pi_n(n,m+1)-pi_n(n,T0-1))*(c(m,y)+c(m,y-1))/(m+1) for m in range(T0-1,n))
        if lhs < first-win+pos: bad+=1; P("  위반",n,y)
P("  재배열 항등식 전부 확인; IH 성립 (n,y) 수",cnt," 위반",bad)

P("== 6. 보조정리 5-25 항별 상계 (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t)) ==")
bad=0
for t in range(3,80):
    for y in range(t//2+1,t):
        lhs=max(-float(xt(t,y)),0); rhs=Ren(t-y)*Bor(y)/(y*Bor(t))
        if lhs>rhs*(1+1e-12): bad+=1
P("  위반",bad)

P("== 7. stop-lower 상계 pi^0_{Y+j}(Y) <= Pr(beta>j) (정확 pi^0) ==")
bad=0
for Y in range(1,25):
    for j in range(0,Y+3):
        lhs=float(pi0(Y+j,Y)); rhs=1-sum(Bor(i) for i in range(1,j+1))
        if lhs>rhs+1e-12: bad+=1; P("  위반",Y,j,lhs,rhs)
P("  위반",bad)

P("== 8. bt-tail (가), hover-tail 두 하계 (Borel-Tanner 직접 합) ==")
bad=0
for z in range(1,31):
    for D in range(z+1,600):
        W=D-z
        ex=-z*z/(2*W)+z**3/(3*W*W)
        if ex>600: continue
        bound=z/sqrt(2*pi)/D/sqrt(W)*exp(ex)
        if BorT(z,D)>bound*(1+1e-10): bad+=1
P("  bt-tail(가) 위반",bad)
bad1=bad2=0
for z in range(1,25):
    for chi in range(2,400):
        pr = sum(BorT(z,D) for D in range(z,chi))    # Pr(R_z<=chi-1)
        lb1 = max(1-2/sqrt(pi)*z**1.5/sqrt(chi-1),0)
        if pr<lb1-1e-12: bad1+=1
        if chi>=4:
            hv = chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi))
            if 1-pr > z*hv+1e-12: bad2+=1
P("  첫 하계 위반",bad1," 둘째(hv) 위반",bad2)

P("== 9. borel-gf (다): sqrt(2s)-2s/3 <= u(s) <= sqrt(2s) ==")
import mpmath as mp
bad=0
for i in range(1,2000):
    sg=i/100
    u=1-float(-mp.lambertw(-mp.e**(-sg-1)))
    if not (sqrt(2*sg)-2*sg/3-1e-12<=u<=sqrt(2*sg)+1e-12): bad+=1
P("  위반",bad)

P("== 10. 보조정리 5-30 상수 ==")
n=50001
v1=(2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
v2=(0.15)**1.5
v3=(2*pi)**-0.5*v2*(1+1/n)**1.5*exp(1/(12*(n+1)))
v4=exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n+1)))
P("  y<=2n/3:",v1,"<=0.0133", v1<=0.0133, " (0.15)^1.5=",v2,"<=0.0581",v2<=0.0581, " top_pi<=",v3,"<=0.0232",v3<=0.0232)
P("  pi_n(n-1)<=",v4,"<0.1354",v4<0.1354, " 괄호>=",exp(-1)-0.1354-0.0232)
# top_pi 상계식 전체 검사: W^sharp 위치에서 (y-1)pi_n(y) <= 0.0232 ? 격자
worst=0
for nn in [50001,60000,100000,10**6]:
    y=(nn+1)//2+((nn+1)%2)
    while nn-y+1>10*y**(2/3):
        v=y*(2*pi)**-0.5*((nn+1)/(y*(nn+1-y)))**1.5*exp(1/(12*(nn+1)))
        worst=max(worst,v); y+=max(1,(nn-y)//50)
P("  top_pi 상계 격자 최대", worst)

P("== 11. 5.5.2 varrho_0 <= 0.75(1.1y)^{2/3}+1 ; t_0<=n ==")
bad=0
for y in [25000,25001,30000,50000,10**5,10**6]:
    T0=t0(y); r0=T0-1-y
    if r0>0.75*(1.1*y)**(2/3)+1: bad+=1
    if ceil(0.75*(1.1*y)**(2/3))>0.1*y: bad+=1
P("  위반",bad, " 예 y=25000: varrho_0=",t0(25000)-1-25000," 상계",0.75*(1.1*25000)**(2/3)+1)
n=50001
P("  10((n+1)/2)^{2/3}=",10*((n+1)/2)**(2/3)," 6n^{2/3}+2=",6*n**(2/3)+2)

P("== 12. 보조정리 5-26 닫힌 꼴 상계 (중간 n에서 WIN^V_0 직접 합과 비교) ==")
bad=0; cnt=0
for n in [200,400,800,1600]:
    for y in range((n+1)//2+((n+1)%2), n):
        T0=t0(y)
        if T0>n: continue
        r0=T0-1-y
        if r0<1: continue
        def pin(t): return Bor(t)*Bor(n+1-t)/Bor(n+1)
        winv=sum((pin(t)-pin(y))*Ren(t-y)*Bor(y)/Bor(t) for t in range(y+1,T0))/y
        c1=1.5*(2*y+2*r0-n)/(y*(n-y-r0)); e0=1.5*r0*(2*y+2*r0-2-n)/((y+r0-1)*(n-y-r0+1))
        bound=pin(y)/y/sqrt(2*pi)*2/3*(r0+1)**1.5*c1*(1+r0/y)**1.5*exp(e0+1/(12*y))
        cnt+=1
        if winv>bound*(1+1e-12): bad+=1; P("  위반",n,y)
P("  검사",cnt," 위반",bad)

P("== 13. 정리 5-31  c_{Y+q}(Y) >= Lc(Y,q) (정확 c, 부동소수 Lc) ==")
bad=0; cnt=0; worst=1e9
for Y in range(2,26):
    pi0cache={}
    for q in range(1,Y+2):
        Lc=0.0
        for z in range(1,q+1):
            for D in range(z,q+1):
                j=q-D
                if j not in pi0cache: pi0cache[j]=float(pi0(Y+j,Y))
                Lc+= z*BorT(z,D)*Bor(Y+q+1-D)/Bor(Y+q+1)*pi0cache[j]*exp(-(z*(q+1)-D*(z+1)/2)/Y)
        Lc/=Y
        lhs=float(c(Y+q,Y)); cnt+=1
        if lhs<Lc*(1-1e-10): bad+=1; P("  위반",Y,q,lhs,Lc)
        if Lc>0: worst=min(worst,lhs/Lc)
P("  검사",cnt," 위반",bad," 최소 비 c/Lc",worst)

P("== 14. stop-lower 하계 (Y=25000, 정확 pi^0 = 1-sum Bor(i)Bor(U-i)/Bor(U)) ==")
Y=25000; bad=0; U=Y+1
for j in range(0, Y//4+1):
    U=Y+j+1
    p0=1-sum(Bor(i)*Bor(U-i)/Bor(U) for i in range(1,j+1)) if j<=400 else None
    if p0 is None: break
    lb=(1-sum(Bor(i) for i in range(1,j+1)))-1.6*sqrt(j)/Y
    if p0<lb-1e-13: bad+=1
P("  j<=400 위반",bad)
# 비 상계 Bor(U-i)/Bor(U) <= 1+2i/Y
bad=0
for Y in [25000,40000,10**5]:
    for j in [Y//4]:
        U=Y+j+1
        for i in range(1,j+1,7):
            if Bor(U-i)/Bor(U) > 1+2*i/Y: bad+=1
P("  Bor(U-i)/Bor(U)<=1+2i/Y 위반",bad)
P("  1.5*0.95^-2.5=",1.5*0.95**-2.5," (0.8^-1.5-1)/0.2=",(0.8**-1.5-1)/0.2," 4/sqrt(2pi)=",4/sqrt(2*pi))

P("== 15. scaled-integrand 상수, hover-tail 상수 ==")
h0=0.0342; up=sqrt(6*h0); c2=1/(2*(1-up)); c3=1/sqrt(2)-up/3
P("  h0^3=",h0**3,">=4e-5",h0**3>=4e-5," upsilon_max=",up," c2=",c2," c3=",c3)
f12=c3*12**1.5-12-log(sqrt(2)*(1+6*h0)*12/c3)
P("  f(12)=",f12," sqrt2(1+6h0)12/c3=",sqrt(2)*(1+6*h0)*12/c3, " 2/sqrt(pi)*2sqrt2=",2/sqrt(pi)*2*sqrt(2))

P("== 16. 오른쪽 부분(right-part) 상수 ==")
y=33334; r=10357
P("  10*33334^{2/3}-1=",10*y**(2/3)-1)
P("  0.2r-7.3=",0.2*r-7.3)
P("  e^{-c4}>=",exp(-(1/156+1/(12*y)+1/(12*50002))))
chi=2064
P("  hv(2064)/chi^-1/2=",2/sqrt(pi)*(1+1/chi)+1/sqrt(pi))
t=y**(1/3); P("  eps_hov<=",1.6932*(t/10+1)/sqrt(2*t*t-7.5))
P("  sqrt(2/pi)/sqrt(2064)=",sqrt(2/pi)/sqrt(2064))
P("  0.75*1.1^{2/3}=",0.75*1.1**(2/3))
P("  (2pi)^-1/2 (1.50003/0.9199)^1.5=",(2*pi)**-0.5*(1.50003/0.9199)**1.5, " *e^{1/(12*50002)}=",(2*pi)**-0.5*(1.50003/0.9199)**1.5*exp(1/(12*50002)))
P("  0.3*0.8308/sqrt(10358)=",0.3*0.8308/sqrt(10358))
rp=10358
P("  (r+1)/(r-varrho0) <=",rp/(0.92007*rp-2), " (0.7993y^{2/3}+2)^{1.5}/y=",(0.7993*y**(2/3)+2)**1.5/y)
P("  eps0<=",1.5*(0.07993*rp+1)/(0.92007*rp-1), " (1+varrho0/y)^1.5<=",(1+(0.7993*y**(2/3)+1)/y)**1.5)
W=(2*pi)**-0.5*2/3*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008)
P("  (r+1)/y W <=",W)
P("  0.8427*0.71216*0.9936*1.9366-0.3678=",0.8427*0.71216*0.9936*1.9366-0.3678)
P("  Psi_R(2/3)>=",0.7869*2/3-(1/3)-2.5e-5)

P("== 17. 조립 범위 (band) 점 평가 lambda=1/2, n=50001 ==")
n=50001; la=lb_=0.5
rho=la-1/n; chi=floor(0.3*(1-lb_)*n-1)-1
hov=0.0; z=0
while True:
    term=(1-2/sqrt(pi)*z**1.5/sqrt(chi))
    if term<=0: break
    hov+=rho**z*term; z+=1
vr=0.75*(1.1*lb_*n)**(2/3)+1
second=1-sqrt(2/pi)/sqrt(0.3*(1-lb_)*n-1)-0.3*(1-la)*n*(2*pi)**-0.5*((n+1)/(la*n*((1-lb_)*n-vr)))**1.5*exp(1/(12*(n+1)))
toppi=(2*pi)**-0.5*(1+1/n)**1.5*la**-0.5*(1-lb_)**-1.5*n**-0.5*exp(1/(12*n))
K=la*exp(-1/(12*(0.4*(1-lb_)*n-6*(lb_*n)**(2/3)+1))-1/(12*la*n)-1/(12*(n+1)))
cb=1.5*((2*lb_-1)*n+2*vr)/(la*n*((1-lb_)*n-vr)); eb=1.5*vr*((2*lb_-1)*n+2*vr)/((la*n-1)*((1-lb_)*n-vr))
Wb=(2*pi)**-0.5*2/3*(vr+1)**1.5*cb*(1+vr/(la*n))**1.5*exp(eb+1/(12*la*n))
lhs=hov*0.71216*K*(2*second-toppi)-Wb
P("  hov=",hov," second=",second," top_pi=",toppi," K=",K," W=",Wb," LHS=",lhs)
P("  조건 n/3 > 10(2n/3)^{2/3}:",n/3,10*(2*n/3)**(2/3)," 0.4n/3 vs 6(2n/3)^{2/3}+1:",0.4*n/3,6*(2*n/3)**(2/3)+1)

P("== 18. 정리 5-32 상수의 부동소수 근사 (g 적분, rho-bar 적분) ==")
def ti(sg,bb,mu):
    T1=sqrt(sg*mu); T2=sqrt(bb/mu)
    return 0.5*sqrt(pi/bb)*(exp(-2*sqrt(sg*bb))*erfc(T1-T2)-exp(2*sqrt(sg*bb))*erfc(T1+T2))
def Tmax(th,mu):
    sg=max(th-h0,0)/2; bb=th*th/2
    return th/sqrt(2*pi)*exp(th**3*h0/(3*mu*mu))*(h0*h0*mu**-1.5*exp(-sg*mu-bb/mu)+ti(sg,bb,mu))
def Pmin(ka): return max(sqrt(2/pi)*(ka+h0*h0)**-0.5*exp(-h0*h0/(12*(ka+h0*h0)))-1.6*h0*sqrt(ka),0)
def bmin(th): return exp(-th**1.5-c2*th*th*h0)
def Q(th,ka):
    mu=6-ka-th*h0
    if mu<th*th/3: last=0.0
    else: last=max(bmin(th)-Tmax(th,mu),0)
    return Pmin(ka)*exp(-th*ka-th*h0*h0)*(1-ka*h0-h0**3)*last
def g(th):
    top=6-th*h0
    if top<=0: return 0.0
    N=600; hstep=top/N
    # kappa=omega^2 치환으로 0 근처 특이성 완화
    om_top=sqrt(top); dom=om_top/N; sm=0.0
    for i in range(N):
        om=(i+0.5)*dom; sm+=Q(th,om*om)*2*om*dom
    return th*sm
def rhobar(th):
    yy=max(th/2,th-h0)
    return sqrt(2)*th**1.5*exp(-th*sqrt(yy)+min(th*th*h0,up*th**1.5)/3)*(1+min(th*h0*h0,6*h0))/(sqrt(yy)-min(th*h0,up*sqrt(th))/3)
N=820; d=4.1/N; gi=0.0; gmax=0.0
for i in range(N):
    th=(i+0.5)*d; v=g(th); gi+=v*d; gmax=max(gmax,v)
N2=2400; d2=12/N2; ri=0.0; rmax=0.0
for i in range(N2):
    th=(i+0.5)*d2
    if th<=0: continue
    v=rhobar(th); ri+=v*d2; rmax=max(rmax,v)
O=1/25000**2*sqrt(12/pi)*25000**(1/3)*sqrt(2/25000)*25001
est=(gi-h0*gmax)-h0*(ri+h0*rmax+exp(-12+h0))-O
P("  int g=",gi," max g=",gmax," int rhobar=",ri," max rhobar=",rmax," O(25000)=",O)
P("  추정 하계(계단함수 전 피적분함수의 중점 적분)=",est," 본문 w0=0.71216")

P("== 19. 정리 5-33 (Y=250, chi_w=2,5: 정확 c_m(Y) vs hov*V*Lambda_w) ==")
Y=250; qmax=floor(6*Y**(2/3))
def pi0f(j):   # Y+j<=2Y+... 정확 식: 1-sum_{t>Y} pi_{Y+j}(t) (t>(Y+j)/2 보장 j<=Y)
    m=Y+j
    return 1-sum(Bor(t)*Bor(m+1-t)/Bor(m+1) for t in range(Y+1,m+1))
pi0c={j:pi0f(j) for j in range(0,qmax+1)}
Lam=0.0
for q in range(1,qmax+1):
    Lc=0.0
    for z in range(1,q+1):
        for D in range(z,q+1):
            j=q-D
            Lc+= z*BorT(z,D)*Bor(Y+q+1-D)/Bor(Y+q+1)*pi0c[j]*exp(-(z*(q+1)-D*(z+1)/2)/Y)
    Lam+= Y/(Y+q+1)*Lc/Y
P("  qmax=",qmax," Lambda_w(250)=",Lam)
# 정확 c_m(Y) for m up to 2Y+1=501 : 큰 n 재귀 (NMAX 초과) -> 별도 계산
def A_col(l, nmax):
    V=[1]
    for m in range(1,nmax+1):
        s_=0
        for j in range(0,m):
            s_ += math.comb(m-1,j)*min(j+1,l+1)*V[j]*V[m-1-j]
        V.append(s_)
    return V
VY=A_col(Y,2*Y+1); VY1=A_col(Y-1,2*Y+1)
def cY(m): return Fr(VY[m]-VY1[m],(m+1)**(m-1))
for chi in [2,5]:
    bad=0; cnt=0; worst=1e9
    for m in range(Y+qmax+chi+1, 2*Y+2):
        rho=Y/(m+1)
        hov = 1.0 + sum(rho**z*sum(BorT(z,D) for D in range(z,chi)) for z in range(1,60))
        V=(2*pi)**-0.5*((m+1)/((Y+1)*(m-Y)))**1.5*exp(-1/(12*(m-chi-Y-qmax+1))-1/(12*(Y+1)))
        rhs=hov*V*Lam; lhs=float(cY(m)); cnt+=1
        if lhs<rhs: bad+=1
        worst=min(worst,lhs/rhs)
    P("  chi_w=",chi," 행 수",cnt," 위반",bad," 최소 비 c/하계",worst)

open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_F4_검산_out.txt","w",encoding="utf-8").write("\n".join(out))
