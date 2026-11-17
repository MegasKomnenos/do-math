# R3 check 2: 5.2.2 (tile model, birthday law, sufficient condition, constants), tail cells, cover-edge constants.
from fractions import Fraction as Fr
from math import comb, factorial, sqrt, pi, log, exp, isqrt
import random
def p(n): return 1 if n==0 else (n+1)**(n-1)
def tw(j): return Fr(1) if j==1 else Fr((j-1)**(j-1),factorial(j))
def V(co):
    # tile sum for coordinates list co (co[0] is position 1)
    d=len(co); v=[Fr(1)]
    for i in range(1,d+1):
        s=(1+co[i-1])*v[i-1]
        for j in range(2,i+1): s+=tw(j)*v[i-j]
        v.append(s)
    return v[d]
def Gam(dmax,n,y):
    G=[Fr(1)]
    for d in range(1,dmax+1):
        G.append(comb(n,d)*p(d)+y*sum(comb(n-d+j,j)*p(j)*G[d-1-j] for j in range(d)))
    return G
def ff(n,d):
    r=1
    for i in range(d): r*=n-i
    return r
ok=True
# inverse-renewal: Gamma_d(y;n) = (n)_d V_d(y/n,...,y/(n-d+1))
for n in (5,9,14):
    for y in (Fr(0),Fr(1),Fr(7,2),Fr(n)):
        G=Gam(n-1,n,y)
        for d in range(n):
            if G[d]!=ff(n,d)*V([y/(n-i) for i in range(d)]): ok=False; print("tile FAIL",n,y,d)
# log-convexity of tw
for j in range(1,60):
    if tw(j+2)/tw(j+1)<tw(j+1)/tw(j): ok=False; print("logconvex FAIL",j)
# hb coefficients
def hbcoef(d):
    # polynomial in rho: via recursion hb_d=(1+rho)hb_{d-1}+sum tw_j hb_{d-j}
    H=[[Fr(1)]]
    for i in range(1,d+1):
        acc=[Fr(0)]*(i+1)
        for t,c in enumerate(H[i-1]): acc[t]+=c; acc[t+1]+=c
        for j in range(2,i+1):
            for t,c in enumerate(H[i-j]): acc[t]+=tw(j)*c
        H.append(acc)
    return H
H=hbcoef(14)
for d in range(1,15):
    for j in range(d+1):
        if H[d][j]!=Fr((j+1)*(d+1)**(d-j-1) if d-j-1>=0 else 1,1)/factorial(d-j) * (1 if d-j-1>=0 else 1):
            # handle j=d: (d+1)^(-1)*(d+1) =1
            if not (j==d and H[d][j]==1): ok=False; print("hb coef FAIL",d,j,H[d][j])
    if sum(H[d])!=Fr((d+1)**d,factorial(d)): ok=False; print("hb(1) FAIL",d)
    for j in range(d+1):
        tail=sum(H[d][j:])/sum(H[d])
        if tail!=Fr(ff(d,j),(d+1)**j): ok=False; print("bd tail FAIL",d,j)
# suff-cond (ga),(ra),(da) numerically for small r,k
def tm(d,rho):
    num=sum(j*H[d][j]*rho**j for j in range(d+1)); den=sum(H[d][j]*rho**j for j in range(d+1)); return num/den
worst_ga=0
for r in range(2,11):
    for k in range(r+1,r+25):
        n=k+r
        Vr=V([Fr(k-1,n-i) for i in range(r)]); Vr1=V([Fr(k,n-i) for i in range(r-1)])
        ratio=Vr/(Fr(r+1,r)**r*Vr1)
        worst_ga=max(worst_ga,float(ratio))
        if ratio>1: ok=False; print("(ga) FAIL",r,k)
        # (ra) first inequality
        Vp=V([Fr(k+2,n-i) for i in range(r-1)])
        lhs=log(Vp/Vr1); rhs=float(tm(r-1,Fr(k,n)))*log(1+2/k)
        if lhs<rhs-1e-13: ok=False; print("(ra) FAIL",r,k,lhs,rhs)
        # (da) second inequality
        G1=None
        for d in range(1,r):
            def hg(y): return y*Gam(d,n,Fr(y))[d]
            sd=lambda y: hg(y+1)-2*hg(y)+hg(y-1)
            if float(sd(k+1)/sd(k))>exp((1+sqrt(3*pi*(r-1)/2))/(k-1)): ok=False; print("(da) FAIL",r,k,d)
print("worst (ga) ratio",worst_ga)
# (na): E_tl[j]<=tm_d(1)<=sqrt(pi d/2)
for d in range(1,15):
    t1=float(tm(d,Fr(1)))
    if t1>sqrt(pi*d/2): ok=False; print("(na) FAIL",d)
    for _ in range(20):
        co=[Fr(random.randint(0,100),100) for _ in range(d)]
        # E[j]= sum_i co_i dV/dco_i / V  (numerical derivative exactly: V linear in each co_i)
        Vv=V(co); Ej=Fr(0)
        for i in range(d):
            c2=list(co); c2[i]=co[i]+1
            Ej+=co[i]*(V(c2)-Vv)
        Ej/=Vv
        if Ej>tm(d,Fr(1)): ok=False; print("(na) mono FAIL",d)
# tilted birthday (i),(ii)
for r in range(2,15):
    for k in range(r+1,r+40,3):
        n=k+r; rho=Fr(k,n); d=r-1
        w=[H[d][j]*rho**j for j in range(d+1)]; Z=sum(w)
        mu=sum(j*w[j] for j in range(d+1))/Z; m2=sum(j*j*w[j] for j in range(d+1))/Z
        if m2+(3+Fr(r*r,k))*mu+2!=2*r: ok=False; print("(ii) FAIL",r,k)
        if m2-mu>Fr(3,2)*mu*mu: ok=False; print("(i) FAIL",r,k)
# (iii) at r>=64,k>=r^1.5+8r : mu>=6/7 sqrt r (float; hb coefficients via closed form, logs)
from math import lgamma
def mu_float(r,k):
    d=r-1; n=k+r; lr=log(k/n)
    lw=[log(j+1)+(d-j-1)*log(d+1)-lgamma(d-j+1)+j*lr for j in range(d+1)]
    m=max(lw); w=[exp(x-m) for x in lw]; Z=sum(w)
    return sum(j*w[j] for j in range(d+1))/Z
mn=10
for r in (64,65,100,170,171,400,598,1000,3000):
    k=int(r**1.5+8*r)+1
    for kk in (k,2*k,10*k,1000*k):
        q=mu_float(r,kk)/sqrt(r); mn=min(mn,q)
        if q<6/7: ok=False; print("(iii) FAIL",r,kk,q)
print("min mu/sqrt r over samples",mn,"(6/7=%.5f)"%(6/7))
# Pc(k) numerics, branch (ga)
def Pc(k,r,eb): return k*(1/(2*r)-1/(3*r*r))-2.5+2*eb*(1-1/k)-k/(k-1)*(1+sqrt(3*pi*(r-1)/2))
mn=1e9
for r in list(range(64,3000))+[10**4,10**5,10**6]:
    k=int(r**1.5+8*r)+1
    mn=min(mn,Pc(k,r,6/7*sqrt(r)))
print("min Pc branch (ga), eb=6/7 sqrt r:",mn)
print("Pc branch (na) at k=19831,r=170:",Pc(19831,170,0), " min over r<=170:",min(Pc(20001-r,r,0) for r in range(2,171)))
print("sqrt(3pi/2)=",sqrt(1.5*pi),"31/14-2.1709=",31/14-2.1709,"bracket at s=8:",1/24+8/(3*64)+12/(7*64)+(1+2.1709*8)/1023)
print("19831*127/43350=",19831*127/43350, "19831/19830*(1+13*2.1709)=",19831/19830*(1+13*2.1709))
# tail cells
def mfun(n):
    m=170
    # integer test m^3 <= (n-9m)^2 with n-9m>=0
    lo=171
    while lo**3<=(n-9*lo)**2 and n-9*lo>=0: m=lo; lo+=1
    return m
print("m(20001)=",mfun(20001),"m(50001)=",mfun(50001),"m(3776)=",mfun(3776),"m(3775)=",mfun(3775))
print("597^1.5+9*597=",597**1.5+9*597,"598^1.5+9*598=",598**1.5+9*598,"171^1.5+9*171=",171**1.5+9*171)
bad=0; mind=1e9; maxd=-1e9; minz=10
for n in list(range(20001,200001,37))+[10**6,10**7+3,10**8+11]:
    # fast m via float then adjust
    m=int(n**(2/3)-6*n**(1/3))
    while (m+1)**3<=(n-9*(m+1))**2: m+=1
    while m**3>(n-9*m)**2: m-=1
    dlt=m-(n**(2/3)-6*n**(1/3)); mind=min(mind,dlt); maxd=max(maxd,dlt)
    z=m+1; q=z**1.5/n; minz=min(minz,q)
    if not (-1<=dlt<=37) or not (0.73<q<=1) or z<598: bad+=1
print("tail-cells (na) violations:",bad,"delta range",mind,maxd,"min z*^1.5/n",minz, "1/(1+9/sqrt598)=",1/(1+9/sqrt(598)))
print("832^1.5=",832**1.5,"833^1.5=",833**1.5,"1.2*20001=",1.2*20001,"965^1.5=",965**1.5,"966^1.5=",966**1.5,"1.5*20001=",1.5*20001)
print("rq bounds:",1.2/sqrt(598),1.5/sqrt(833),1.8/sqrt(966),"1/16=",1/16)
print("(9/5)^(2/3)=",1.8**(2/3),"10/2^(2/3)=",10/2**(2/3))
print("ALL OK" if ok else "SOME FAIL")
