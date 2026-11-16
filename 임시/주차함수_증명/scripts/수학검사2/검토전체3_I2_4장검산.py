# 검토전체3 I2: 4장 4.3절 해석적 연쇄의 독립 검산
import sympy as sp
from fractions import Fraction as Fr
import mpmath as mp
from math import comb, lgamma, log, sqrt, pi, exp
import sys

print("== (A) (4.9), M4/M0 식: 정확 유리수로 k=30,31 검산 ==")
def He_list(n, N, y):
    H=[Fr(1), Fr(N)]
    for j in range(2,n+1):
        H.append(N*H[j-1]-(j-1)*y*H[j-2])
    return H
def Mr_scaled(r, n, H):
    # n! [Y^n] (1-Y)^{r+1} B(Y)  (공통 인자 e^{-y/2}/p_n 은 비에서 소거)
    s=Fr(0); ff=Fr(1)
    for i in range(0,r+2):
        s+= comb(r+1,i)*(-1)**i*ff*H[n-i]
        ff*= (n-i)
    return s
for k in (30,31):
    for nu in (0,-1):
        n=2*k+nu
        for y in (Fr(k), Fr(k)-Fr(1,2), Fr(k-1)):
            N=n+y+1; H=He_list(n,N,y)
            M0=Mr_scaled(0,n,H); M2=Mr_scaled(2,n,H); M4=Mr_scaled(4,n,H)
            th=H[n]/H[n-1]-n
            rhs=(th*((n-y)**2+n)-n*(n+1))/(y*y*th)
            assert M2/M0==rhs, (k,nu,y)
            if y==k:
                if nu==0: f=1+Fr(16,k)+Fr(18,k**2)+Fr(2,k**3)-(4+Fr(38,k)+Fr(22,k**2)+Fr(2,k**3))/th
                else:     f=1+Fr(12,k)-Fr(6,k**2)-(4+Fr(26,k)-Fr(14,k**2))/th
                assert M4/M0==f,(k,nu)
print("(4.9)와 M4/M0 두 식: 정확히 성립")

print("== (B) g(kappa) 급수, 잔차 계수, (라)의 항등식, P의 전개 (sympy) ==")
kap,nu,th,xx=sp.symbols('kappa nu theta x')
Nt=3+(nu+1-th)*kap
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
x_=(1-th*kap)*kap/Nt**2
gam=sp.sqrt(1-4*xn)
ups=(1+gam)/2
C1=(1-ups)/gam**2; C2=-(1-ups)*(2+ups)/gam**5; C3=5*(1-ups)*(6+gam-gam**2)/(2*gam**8)
uhat=ups+x_*C1+x_**2*C2+x_**3*C3
gk=(Nt*uhat-2-nu*kap)/kap
ser=sp.expand(sp.series(gk,kap,0,3).removeO())
c0=ser.coeff(kap,0); c1=ser.coeff(kap,1); c2=ser.coeff(kap,2)
print(" c0-4 =",sp.simplify(c0-4)," c1+(26+4nu+8th) =",sp.simplify(c1+(26+4*nu+8*th)))
print(" c2-(506+97nu+5nu^2+(168+16nu)th+12th^2) =",sp.simplify(c2-(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2)))
G=sp.symbols('G',positive=True)
def coeffs(Gv):
    u=(1+Gv)/2
    return (1-u)/Gv**2, -(1-u)*(2+u)/Gv**5, 5*(1-u)*(6+Gv-Gv**2)/(2*Gv**8)
c1_,c2_,c3_=coeffs(G)
uh_i=(1+G)/2+xx*c1_+xx**2*c2_+xx**3*c3_
Gm=sp.sqrt(G**2+4*xx)   # gamma(iota-x)
d1,d2,d3=coeffs(Gm)
uh_im=(1+Gm)/2+xx*d1+xx**2*d2+xx**3*d3
iota_=(1-G**2)/4
R=(uh_i-1)*uh_im+iota_
Rs=sp.expand(sp.series(R,xx,0,5).removeO())
for p in range(0,4):
    print(" R x^%d 계수 ="%p, sp.simplify(Rs.coeff(xx,p)))
print(" R x^4 계수 at gamma=1/3 =", sp.simplify(Rs.coeff(xx,4)).subs(G,sp.Rational(1,3)))
k_=sp.symbols('k')
Nn=3*k_+nu+1-th
print(" (라) 항등식 잔차 =", sp.expand(2*Nn**2-9*(2*k_+nu)*(k_-th)-((3*nu+12+6*th)*k_+2*(nu+1-th)**2+9*nu*th)))
a=26+4*nu+8*th; b=506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2
vt=4-a/k_+b/k_**2
n_=2*k_+nu; y_=k_-th
P=sp.expand(vt*((n_-y_)**2+n_)-n_*(n_+1))
print(" P k^2:",sp.simplify(P.coeff(k_,2))," k^1:",sp.simplify(P.coeff(k_,1)))
print(" P k^0 (nu=0):",sp.expand(P.coeff(k_,0).subs(nu,0))," (nu=-1):",sp.expand(P.coeff(k_,0).subs(nu,-1)))
Q1=sp.expand(k_*P+5*y_**2*vt); print(" kP+5y^2vt k^2:",sp.simplify(Q1.coeff(k_,2))," k^1 nu=0:",sp.expand(Q1.coeff(k_,1).subs(nu,0))," nu=-1:",sp.expand(Q1.coeff(k_,1).subs(nu,-1)))
Q2=sp.expand(100*k_*P+499*y_**2*vt); print(" 100kP+499y^2vt k^2:",sp.simplify(Q2.coeff(k_,2)))
for nuv,fexpr in ((0, 1+16/k_+18/k_**2+2/k_**3-(4+38/k_+22/k_**2+2/k_**3)/vt), (-1, 1+12/k_-6/k_**2-(4+26/k_-14/k_**2)/vt)):
    e=sp.series(fexpr.subs({nu:nuv,th:0}),k_,sp.oo,4)
    print(" M4/M0 중심 전개 nu=%d:"%nuv, e)

print("== (C) Borel 합 상수와 첫 조각 ==")
def Bor(j): return exp(-j+(j-1)*log(j)-lgamma(j+1))
K=200000
B=[0.0]+[Bor(j) for j in range(1,K+1)]
cum_j=0.0; cum=0.0
for j in range(1,K+1):
    cum_j+=j*B[j]; cum+=B[j]
    if j in (10,100,1000,10000,30000,100000,200000):
        dev=cum_j-(2*sqrt(j/(2*pi))-2/3); ub=(2/3)/sqrt(2*pi*j)
        tail=1-cum; dev1=2/sqrt(2*pi*j)-tail; ub1=(5/9)/sqrt(2*pi)*j**-1.5
        print(f" k={j}: 둘째조각 dev={dev:.3e} in [0,{ub:.3e}] -> {0<=dev<=ub};  첫조각 dev={dev1:.3e} in [0,{ub1:.3e}] -> {0<=dev1<=ub1}")
s=sum(j*B[j]-j**-0.5/sqrt(2*pi) for j in range(1,K+1))
print(" (2pi)^-1/2 zeta(1/2) + sum_{j<=K} =", float(mp.zeta(0.5))/sqrt(2*pi)+s, " (참값 -2/3; 꼬리 ~ (2pi)^-1/2 (1/12) sum j^-3/2 ... 차 작음)")

print("== (D) (4.14) 수직선 위 Borel 꼬리 전개의 수치 검증 k=30000 ==")
mp.mp.dps=30
def bortail(k, Z):
    lw=mp.log(Z)+1-Z
    s=mp.mpf(0)
    for j in range(1,k+1):
        s+= mp.e**(-j+(j-1)*mp.log(j)-mp.loggamma(j+1)+j*lw)
    return 1-s/Z
def borld_R(beta):
    beta=mp.mpf(beta)
    daw=mp.e**(-beta**2/2)*mp.sqrt(mp.pi/2)*mp.erfi(beta/mp.sqrt(2))
    return mp.e**(beta**2/2)*(2-2*beta*daw)
k=30000; eps=1/mp.sqrt(k); Gg=mp.mpf(1)/16
for beta in (0.5,1,2,4,8,float(Gg*mp.sqrt(k))):
    Z=1+1j*beta*eps
    v=mp.sqrt(k)*bortail(k,Z)
    TR=mp.mpf(3)/5+mp.mpf(12)/5*beta**2+mp.mpf(3)/2*beta**4+mp.mpf(1)/25*beta**6
    TI=mp.mpf(1)/100+mp.mpf(201)/100*beta+mp.mpf(7)/10*beta**3+beta**4/500+beta**5/50000+beta**7/500000
    errR=abs(mp.re(v)-borld_R(beta)/mp.sqrt(2*mp.pi)-mp.mpf(4)/3*beta**2*eps); bR=eps**2*mp.e**(beta**2/2)*TR/mp.sqrt(2*mp.pi)
    errI=abs(mp.im(v)-beta); bI=eps*mp.e**(beta**2/2)*TI/mp.sqrt(2*mp.pi)
    print(f" beta={beta:.3f}: Re err={mp.nstr(errR,4)} <= {mp.nstr(bR,4)} {errR<=bR};  Im err={mp.nstr(errI,4)} <= {mp.nstr(bI,4)} {errI<=bI}")
