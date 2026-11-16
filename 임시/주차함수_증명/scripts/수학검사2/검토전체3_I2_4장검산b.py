# 검토전체3 I2: 4장 4.3절 검산 (둘째 파일: 중앙 상쇄 항등식, 조립 산술, k=10000 Hermite, 정리 4-7 수치)
import mpmath as mp, numpy as np, sys
from fractions import Fraction as Fr
from math import comb, lgamma, log, sqrt, pi, exp
def Bor(j): return exp(-j+(j-1)*log(j)-lgamma(j+1))
a0=3**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3); a1=3**(-mp.mpf(1)/3)*mp.gamma(mp.mpf(2)/3)

print("== (E) 중앙 상쇄 항등식 int F0 = 0, int F1 = 46 sqrt2 - 12 (numpy Gauss-Legendre) ==")
xs,ws=np.polynomial.legendre.leggauss(240); s_n=(xs+1)/2; s_w=ws/2       # s in [0,1]
r_n,r_w=s_n,s_w                                                           # rho in [0,1]
zx,zw=np.polynomial.legendre.leggauss(600); z_n=(zx+1)*6; z_w=zw*6        # z in [0,12]
def borld_R(beta):  # 2 + int_0^1 iota^{-3/2}(1-e^{beta^2 iota/2}) d iota, iota=s^2
    b=np.asarray(beta)[...,None]
    integrand=2*(1-np.exp(b**2*s_n**2/2))/s_n**2
    return 2+np.sum(integrand*s_w,axis=-1)
# Dawson 표현 대조 (mpmath)
for bt in (0.5,2.0,5.0):
    daw=mp.e**(-bt**2/2)*mp.sqrt(mp.pi/2)*mp.erfi(bt/mp.sqrt(2)); ref=mp.e**(bt**2/2)*(2-2*bt*daw)
    print(f"  Bor^ld_R({bt}) 직접={borld_R(np.array([bt]))[0]:.10f}  Dawson식={mp.nstr(ref,12)}")
ninf=2/sqrt(pi)
Z,Rr=np.meshgrid(z_n,r_n,indexing='ij'); W=np.outer(z_w,r_w)
mu=1-Rr**2; Pq=mu*Z**2+mu**2*Z**4/4
BL=borld_R(Rr*Z)
F0=-ninf*Z**4*np.exp(-Z**2)*Rr**2*np.exp(mu*Z**2/2)*Pq*BL/sqrt(2*pi)
F1=-ninf*Z**4*np.exp(-Z**2)*Rr**2*np.exp(mu*Z**2/2)*Pq*(4/3*Rr**2*Z**2-2/3*Rr*Z**4)
I0=2*np.sum(F0*W); I1=2*np.sum(F1*W)
print(f" int F0 = {I0:.3e} (0이어야 함)   int F1 = {I1:.8f}   46sqrt2-12 = {46*sqrt(2)-12:.8f}")
cJ=np.sum(np.outer(z_w,r_w)*Z**3*np.exp(-Z**2/2)*Rr*((2-Rr**3)/3*Z**3-Rr*Z))*2
print(f" J 선도 적분 = {cJ:.8f}   3sqrt(2pi) = {3*sqrt(2*pi):.8f}")

print("== (F) 따름정리의 유리수, a0, a1, 조립 산술 ==")
print(" a0 =",a0," a1 =",a1)
w=Fr(699,100); val=w-Fr(7,2)-(4*w+Fr(1,2))*Fr(3,2)/31-Fr(13,2)*w/961-12*w/30000
print(" (나) 값 =",val, val==Fr(495594511,240250000), float(val))
w=Fr(698,100); kc=mp.mpf(10000)**(-mp.mpf(1)/3)
val2=float(w)-3.5-(4*float(w)+0.5)*1.2879*float(kc)-6.5*float(w)*0.939*float(kc)**2-12*float(w)/10000
print(" (다) 값 =",val2, " k^-1/3 =",kc)
print(" 조립 k>=30000:", 5.5*0.39*2-3.5, " k>=10000:", 5.642*1.6809*0.39893-0.0163-3.554)
print(" n_inf=2/sqrt(pi)=",2/sqrt(pi)," sqrt2/pi e^{1/30000}=",sqrt(2)/pi*exp(1/30000)," sqrt2/pi e^{1/10000}=",sqrt(2)/pi*exp(1/10000))
print(" Bor(k)k^{3/2}(k=10000)=",Bor(10000)*10000**1.5," (2pi)^-1/2=",1/sqrt(2*pi))
print(" 46sqrt2-12-5000/173-0.02 =",46*sqrt(2)-12-5000/173-0.02, " 46sqrt2-12-54.6828 =",46*sqrt(2)-12-54.6828)
print(" 0.451*3*2.51+0.056+0.01=",0.451*3*2.51+0.056+0.01, " 0.4503*3*2.50663+0.16752=",0.4503*3*2.50663+0.16752)
print(" 호: 130(k/256)^6 e^{-k/512} at 30000 =", 130*(30000/256)**6*exp(-30000/512), " k^5 e^{-k/520} =", 30000**5*exp(-30000/520))
print(" 수축 계수 (2/9)/(4/9-144x^2), x=1.12e-5:", (2/9)/(4/9-144*(1.12e-5)**2), " 잔차 합:", 468018+291+1+(1/3+4e-5)*11328660)
print(" 4sqrt2(1-26/k): k=10000:",4*sqrt(2)*(1-26/10000)," k=30000:",4*sqrt(2)*(1-26/30000))
print(" 11/2 x + 350 n x^2 (nu=0 상계): 5.5/9 + 700/81 =",5.5/9+700/81)

print("== (G) k=10000 정확 Hermite 수로 M0, M2/M0, M4/M0, vartheta, He_n 하계 검산 ==")
if hasattr(sys,'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
def He_int(n,N,y):
    H=[1,N]
    for j in range(2,n+1): H.append(N*H[-1]-(j-1)*y*H[-2])
    return H
mp.mp.dps=50
k=10000
for nu in (0,-1):
    n=2*k+nu; y=k; N=n+y+1
    H=He_int(n,N,y)
    def Mr(r):
        s=0; ff=1
        for i in range(0,r+2):
            s+=comb(r+1,i)*(-1)**i*ff*H[n-i]; ff*=(n-i)
        return s
    M0i,M2i,M4i=Mr(0),Mr(2),Mr(4)
    logM0=-mp.mpf(k)/2+mp.log(mp.mpf(M0i))-(n-1)*mp.log(n+1)
    M0=mp.e**logM0
    vt=mp.mpf(H[n])/mp.mpf(H[n-1])-n
    center=4-mp.mpf(26+4*nu)/k+mp.mpf(506+97*nu+5*nu*nu)/k**2
    r2=mp.mpf(M2i)/M0i*k; r4=mp.mpf(M4i)/M0i*k*k
    print(f" nu={nu}: M0={mp.nstr(M0,10)} (>=5.642: {M0>=5.642}); k*M2/M0={mp.nstr(r2,8)} in (-5,-4.98): {-5<r2<-4.98}; k^2*M4/M0={mp.nstr(r4,8)}; vartheta={mp.nstr(vt,12)}, k^2|vt-center|={mp.nstr(abs(vt-center)*k*k,5)}")
    q=mp.mpf(n*y)/N**2; up=(1+mp.sqrt(1-4*q))/2; U=N*up; Wn=N*(2*up-1)
    lb=mp.log(mp.sqrt(U/Wn))+n*mp.log(U)+(N-U)**2/(2*y)-mp.mpf(10)/k
    print(f"   log He_n = {mp.nstr(mp.log(mp.mpf(H[n])),15)} >= 하계 {mp.nstr(lb,15)} : {mp.log(mp.mpf(H[n]))>=lb}")

print("== (H) 정리 4-7의 하계를 k=10000에서 수치로 (numpy; 꼬리는 급수꼴로 로그 공간 계산) ==")
k=10000; JMAX=300000
jj=np.arange(1,k+JMAX+1,dtype=float)
logBor_all=-jj+(jj-1)*np.log(jj)-np.array([lgamma(j+1) for j in range(1,k+JMAX+1)])
logBor=logBor_all[:k]; js=jj[:k]
M=8000; vs=(np.arange(1,M)+0.0)/M
g=np.empty_like(vs)   # g(v) = e^{k v^2/2} Bor^tail_k(1-v)
for i,v in enumerate(vs):
    F=-np.log(1-v)-v; rho=F-v*v/2
    if v<=0.05:
        Zz=1-v; tail=1-np.sum(np.exp(logBor+js*(np.log(Zz)+1-Zz)))/Zz
        g[i]=np.exp(k*v*v/2)*tail
    else:
        J=min(JMAX,int(40/F)+1)
        lb=logBor_all[k:k+J]; jv=np.arange(1,J+1,dtype=float)
        g[i]=np.exp(-k*rho)/(1-v)*np.sum(np.exp(lb-jv*F))
h=1.0/M
f=g*vs**2
Wi=[h*np.sum(f*(vs**2/2)**j) for j in range(3)]
rho_v=-np.log(1-vs)-vs-vs**2/2
Ik=h*np.sum(vs/(1-vs)*np.exp(-vs**2/2)*np.exp(-k*rho_v))
Bk=Bor(k)
for om in (6.98,6.99):
    R=k*Wi[2]+om*Wi[1]-Bk*Ik
    lbnd=om-3.5-(4*om+.5)*float(a0)*k**(-1/3)-6.5*om*float(a1)*k**(-2/3)-12*om/k
    print(f" omega={om}: k R/Bor(k) = {k*R/Bk:.5f}  (정리 4-7 하계 {lbnd:.5f}) 성립: {k*R/Bk>=lbnd}")
print(" Wi0,Wi1,Wi2 =",Wi," Bor(k)I_k=",Bk*Ik, " k Wi2 =",k*Wi[2])
# 이음새 연속성 확인: v=0.05 양쪽
