# 7.6-7.7절의 수치 상수 검산
from math import log, exp, sqrt, pi, factorial, comb, ceil, floor
from fractions import Fraction as Fr
from math import lgamma
def Bor(d): return exp(-d+(d-1)*log(d)-lgamma(d+1))
from math import log1p
def i_m(m): return m*log1p(-1/(m+1))+1
def g(x): return (x-1)*log(1+1/x)
print("== explicit-bounds")
worst=0
for m in list(range(1,200))+[1000,6263,10**5]:
    im=i_m(m); ub=1/(2*(m+1))+1/(6*m*(m+1))
    assert 0<=im<=ub, m
for d in range(1,170):
    assert Bor(d)<=(2*pi)**-0.5*d**-1.5
    # tail
for m in range(1,60):
    tail=sum(Bor(d) for d in range(m+1,400))
    assert tail<=0.8/sqrt(m), m
# (나) P_m(m-U) <= Bor(U+1) e^{i_m} (m+1)/(m-U); P_m(j)<=Ren(j)e^{i_m}(m+1)/(m+1-j)^2
def Pm(m,j): return Fr(j*comb(m-1,j-1)*(j)**(j-2)*(m-j+1)**(m-j-1), (m+1)**(m-1)) if j>=1 else 0
def pp(x): return (x+1)**(x-1) if x>=1 else 1
def Pm(m,j): return Fr(j*comb(m-1,j-1)*pp(j-1)*pp(m-j), pp(m))
for m in range(2,80):
    for U in range(0,m):
        assert float(Pm(m,m-U))<=Bor(U+1)*exp(i_m(m))*(m+1)/(m-U)*(1+1e-12),(m,U)
    for j in range(1,m+1):
        Ren=j*Bor(j)
        assert float(Pm(m,j))<=Ren*exp(i_m(m))*(m+1)/(m+1-j)**2*(1+1e-12),(m,j)
print("explicit-bounds numeric OK")
print("== theorem-W constants")
print("1-0.8/sqrt(301)=",1-0.8/sqrt(301))
print("0.9538/0.398943=",0.9538/0.398943)
print("(2pi)^-1/2=",(2*pi)**-0.5)
print("0.14*2.38*0.9999=",0.14*2.38*0.9999, " 0.14*301=",0.14*301)
print("e^{-i_6263}=",exp(-i_m(6263)))
k=3131
print("D_k(2) at 3131:",0.08329*sqrt(k)-2-42.14/k, " 0.33316/4=",0.33316/4)
print("(1+1/3131)^{4/3}=",(1+1/k)**(4/3), " 2/k=",2/k)
t=k**(1/6); print("k^{1/6}=",t)
val=0.33316*(t**3-2*t+1/t)-1.0005*t*t-1.0145
print("right-end value at 3131:",val)
der=0.33316*(3*t*t-2-1/t**2)-2.001*t
print("derivative at 3131:",der)
# direct check of D_k at n_PD/k
nPD=ceil((k+1)**(4/3))+k+1
rho=nPD/k
print("n_PD=",nPD," n_PD/k=",rho," D_k(n_PD/k)=",0.33316*sqrt(k)*(1-1/rho)**2-rho-42.14/k)
# G_k(n) >1 check directly over k=3131.. sample, all n in [2k+1, n_PD-1]
def G(k,n): return 0.14/n*(2.38*k**1.5*(n-k+1)**2/(exp(i_m(n))*n*(n+1))-301)
for kk in [3131,3132,3500,5000,6667,10000,20000,50000]:
    nPD=ceil((kk+1)**(4/3))+kk+1
    mn=min(G(kk,n) for n in range(2*kk+1,nPD))
    print(" k=%d min G over [2k+1,nPD-1] = %.4f"%(kk,mn))
# is G>1 fails for k slightly below 3131?
for kk in [3000,3100,3120,3125,3130]:
    nPD=ceil((kk+1)**(4/3))+kk+1
    mn=min(G(kk,n) for n in range(2*kk+1,nPD))
    print(" k=%d min G = %.4f"%(kk,mn))
print("== threshold-unit-ratio constants")
k=6667
j0=floor(0.3*k)
v=-(0.3*k-1)*(0.3*k)/(2*(1.3*k+1)); print("bound at 6667:",v, " exact sum bound:", -j0*(j0+1)/(2*(k+1+j0)))
print("1+1.5log k + v =",1+1.5*log(k)+v)
print("e^0.3=",exp(0.3)," e^{3/(2k)}=",exp(3/(2*k)), " product:",1.00023*1.34986)
print("2*0.7654-1.3502=",2*0.7654-1.3502)
# binomial bound C(2k,k) >= 4^k/(2 sqrt k)
for kk in range(1,60):
    assert comb(2*kk,kk)>=4**kk/(2*sqrt(kk))
print("C(2k,k)>=4^k/(2sqrt k) ok small k")
print("== old-6-22 constants")
k=501; n=2*k+1
xk=(k/(k+1))**(k-1); print("x_k n at k=501:",xk*n, " x_k=",xk, " e^-1=",exp(-1))
# check v_k(m#, x_k n/k)<0 directly for k in 501..., n in [2k+1,3k]
def vk(k,Z,H): return (1+1/k)**Z+(1-1/k)**(Z+H)-2
for kk in [501,600,1000,3131,6667]:
    xk=(kk/(kk+1))**(kk-1)
    mx=max(vk(kk,(n-kk)/(kk+1),xk*n/kk) for n in range(2*kk+1,3*kk+1))
    print(" k=%d max v over [2k+1,3k] = %.3e"%(kk,mx))
print("R_2 small k: k=6668 ->",max(2*6668+103,20001),"..",3*6668-1)
print("k=6667: 3k-1=",3*6667-1)
