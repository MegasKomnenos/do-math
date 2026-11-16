# 7.6-7.7절 수치 상수 검산 (L7b)
from math import log, exp, sqrt, pi, ceil, floor
print("--- explicit-bounds / theorem-W (가) ---")
tail = 0.8/sqrt(301); print("0.8/sqrt(301) =", tail, " 1-tail =", 1-tail, ">=0.9538:", 1-tail>=0.9538)
print("(2pi)^-1/2 =", (2*pi)**-0.5, "<=0.398943:", (2*pi)**-0.5<=0.398943)
print("0.9538/0.398943 =", 0.9538/0.398943, ">=2.38:", 0.9538/0.398943>=2.38)
print("0.307/(n-U)>=0.14/n trivially; 2/sqrt(2pi)=",2/sqrt(2*pi),"<=0.8")
print("--- theorem-W (나) ---")
k=3131; n=2*k+1
i_n = n*log(n/(n+1))+1
print("i_n(6263)=",i_n," bound=",1/(2*(n+1))+1/(6*n*(n+1))," e^-i_n=",exp(-i_n),">=0.9999:",exp(-i_n)>=0.9999)
print("0.14*2.38*0.9999=",0.14*2.38*0.9999,">=0.33316:",0.14*2.38*0.9999>=0.33316, " 0.14*301=",0.14*301)
D2 = 0.08329*sqrt(k)-2-42.14/k; print("D_k(2) at 3131 =",D2, " 0.33316/4=",0.33316/4)
print("(1+1/k)^(4/3)=",(1+1/k)**(4/3),"<=1.0005:",(1+1/k)**(4/3)<=1.0005," 2/k=",2/k)
nPD = ceil((k+1)**(4/3))+k+1; z=nPD/k
print("n_PD(3131)=",nPD," z=",z," <=1.0005k^(1/3)+1.001:",z<=1.0005*k**(1/3)+1.001," z>=k^(1/3):",z>=k**(1/3)," n_PD>=3k+2:",nPD>=3*k+2)
u=k**(1/6); print("u=k^(1/6)=",u)
low = 0.33316*(u**3-2*u+1/u)-1.0005*u**2-1.0145
print("lower bound at k=3131:",low," (text 0.529)")
der = 0.33316*(3*u*u-2-u**-2)-2.001*u; print("derivative wrt u at 3.8248:",der,">0:",der>0)
Dz = 0.33316*sqrt(k)*(1-1/z)**2 - z - 42.14/k; print("D_k(z_max) actual =",Dz)
# check D_k(z)>0 on grid for several k
for kk in [3131,5000,10**4,10**5]:
    nP=ceil((kk+1)**(4/3))+kk+1
    mn=min(0.33316*sqrt(kk)*(1-kk/nn)**2-nn/kk-42.14/kk for nn in range(2*kk+1,nP, max(1,(nP-2*kk)//2000)))
    print("k=",kk," min D over grid n in [2k+1,n_PD-1]:",mn)
# direct check G_k(n)>1 at k=3131, n=n_PD-1
def G(k,n):
    i=n*log(n/(n+1))+1
    return 0.14/n*(2.38*k**1.5*(n-k+1)**2/(exp(i)*n*(n+1))-301)
print("G_3131(n_PD-1)=",G(3131,nPD-1)," G_3131(2k+1)=",G(3131,2*3131+1))
print("--- threshold-unit-ratio ---")
k=6667; j0=floor(0.3*k)
val=(0.3*k-1)*(0.3*k)/(2*(1.3*k+1)); print("(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 =",val)
exact=sum(log(1+i/(k+1)) for i in range(1,j0+1)); print("exact -log Pi_up(j0+1) =",exact," (record 273.9)")
rhs=1+1.5*log(k)-val; print("1+1.5log k - val =",rhs,"<= -215:",rhs<=-215)
print("e^0.3=",exp(0.3),"<1.34986:",exp(0.3)<1.34986)
print("e^(3/(2k))=",exp(3/(2*k)),"<=1.00023:",exp(3/(2*k))<=1.00023)
print("1.00023*1.34986=",1.00023*1.34986,"<1.3502:",1.00023*1.34986+exp(-215)<1.3502)
print("2*0.7654-1.3502=",2*0.7654-1.3502,">=0.18:",2*0.7654-1.3502>=0.18)
# C(2k,k)>=4^k/(2 sqrt k) check small k
from math import comb
print("C(2k,k)>=4^k/(2sqrt k) for k=1..60:", all(comb(2*k,k)>=4**k/(2*sqrt(k)) for k in range(1,61)))
print("(1-1/k)^(k-2)>=1/e for k=2..200:", all((1-1/k)**(k-2)>=exp(-1) for k in range(2,201)))
print("--- old-6-22 P=>LRP2 ---")
print("1003/e=",1003/exp(1),">368:",1003/exp(1)>368)
print("--- 잔여 ---")
print("3*3333-1=",3*3333-1," 3*6666-1=",3*6666-1," 3*6667-1=",3*6667-1)
