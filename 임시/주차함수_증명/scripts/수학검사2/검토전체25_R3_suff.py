# R3 검산: 정리 suff-cond의 (가)(나)(다)(라)(마), 보조정리 tilted-birthday-mean, 정리 old-5-5의 경계 값과 m(n)의 값을 수치로 본다.
import mpmath as mp
mp.mp.dps=40
def tw(j): return mp.mpf(1) if j==1 else mp.mpf(j-1)**(j-1)/mp.factorial(j)
TW=[None]+[tw(j) for j in range(1,400)]
def Vlist(co):
    d=len(co); v=[mp.mpf(1)]
    for m in range(1,d+1):
        s=(1+co[m-1])*v[m-1]
        for j in range(2,m+1): s+=TW[j]*v[m-j]
        v.append(s)
    return v
def Vd(d,yy,n): return Vlist([mp.mpf(yy)/(n-i+1) for i in range(1,d+1)])[d]
def hg_derivs(d,yy,n):
    # hg_d(y)=(n)_d y V_d(y): get polynomial coefficients in y numerically via colored-count distribution
    # V_d(y)=sum_j c_j y^j ; compute c_j by DP over tiles tracking colored count
    co=[mp.mpf(1)/(n-i+1) for i in range(1,d+1)]
    v=[[mp.mpf(1)]]
    for m in range(1,d+1):
        new=[mp.mpf(0)]*(m+1)
        for j,c in enumerate(v[m-1]):
            new[j]+=c; new[j+1]+=c*co[m-1]
        for L in range(2,m+1):
            for j,c in enumerate(v[m-L]): new[j]+=TW[L]*c
        v.append(new)
    c=v[d]
    ff=mp.ff(n,d)
    h2=sum(ff*c[j]*(j+1)*j*mp.mpf(yy)**(j-1) for j in range(1,d+1))
    h3=sum(ff*c[j]*(j+1)*j*(j-1)*mp.mpf(yy)**(j-2) for j in range(2,d+1))
    hgv=lambda t: ff*sum(c[j]*mp.mpf(t)**(j+1) for j in range(0,d+1))
    return h2,h3,hgv,c
def tm(d,rho):
    # tilted birthday mean
    num=den=mp.mpf(0)
    for j in range(0,d+1):
        w=(j+1)*mp.mpf(d+1)**(d-j-1)/mp.factorial(d-j)*mp.mpf(rho)**j
        num+=j*w; den+=w
    return num/den
def check(r,k,verbose=True):
    n=k+r
    A=Vd(r,k-1,n); B=Vd(r-1,k,n)
    okA = A<=(1+mp.mpf(1)/r)**r*B
    # (ra)
    lhs=mp.log(Vd(r-1,k+2,n)/Vd(r-1,k,n)); rhs=tm(r-1,mp.mpf(k)/n)*mp.log(1+mp.mpf(2)/k)
    okR= lhs>=rhs
    # (G)_d
    pk_ratio=k*(1+mp.mpf(1)/k)**(k-1)
    Gp=mp.ff(n,r-1)*Vd(r-1,k+2,n); Gm=mp.ff(n,r)*Vd(r,k-1,n)
    worst=None; okD=True
    for d in range(1,r):
        h2,h3,hgv,c=hg_derivs(d,k+2,n)
        sd=lambda v: hgv(v+1)-2*hgv(v)+hgv(v-1)
        ratio=sd(k+1)/sd(k)
        bound=mp.e**((1+mp.sqrt(3*mp.pi*(r-1)/2))/(k-1))
        if ratio>bound: okD=False
        m=mp.log(pk_ratio*Gp/Gm)-mp.log(ratio)   # >0  <=> (G)_d strict
        if worst is None or m<worst[0]: worst=(m,d)
        # first inequality of (da) at y=k+2
        if h3/h2 > (1+mp.sqrt(3*mp.pi*d/2))/(k+2): okD=False
    if verbose: print("r=%d k=%d n=%d: (ga)%s (ra)%s (da)%s  min_d log[(G)_d LHS/RHS]=%s at d=%d ; tm=%s"%(r,k,n,okA,okR,okD,mp.nstr(worst[0],6),worst[1],mp.nstr(tm(r-1,mp.mpf(k)/n),6)))
    return worst[0]
import math
check(2,3); check(3,4); check(5,6); check(10,11)
check(64,1024)            # (가) 분기의 구석: r=64, k=r^{3/2}+8r
check(170,19831)          # (나) 분기의 구석
check(2,19999)
check(100,100**1.5.__int__()+800 if False else 1800)
# (나) of suff-cond: tm_d(1)<=sqrt(pi d/2)
for d in (1,2,5,50,300):
    assert tm(d,1)<=mp.sqrt(mp.pi*d/2)
# tilted-birthday (i),(ii),(iii)
def tb(r,k):
    n=k+r; rho=mp.mpf(k)/n
    pr=[(j+1)*rho**j*mp.rf(1,0)*mp.fprod([1-mp.mpf(i)/r for i in range(1,j+1)]) for j in range(0,r)]
    Z=sum(pr); pr=[x/Z for x in pr]
    mu=sum(j*x for j,x in enumerate(pr)); m2=sum(j*j*x for j,x in enumerate(pr))
    return mu, m2, m2-mu, m2+(3+mp.mpf(r)**2/k)*mu+2-2*r
for (r,k) in [(2,3),(7,9),(64,1024),(170,19831),(400,400*20+8*400)]:
    mu,m2,f2,ident=tb(r,k)
    print("tb r=%d k=%d: mu=%s tm=%s  E[j(j-1)]/(1.5mu^2)=%s  (ii) residual=%s  mu/sqrt(r)=%s"%(r,k,mp.nstr(mu,8),mp.nstr(tm(r-1,mp.mpf(k)/(k+r)),8),mp.nstr(f2/(1.5*mu*mu),6),mp.nstr(ident,3),mp.nstr(mu/mp.sqrt(r),6)))
# m(n)
def mm(n):
    best=170; m=171
    while m**3<=(n-9*m)**2 and n-9*m>=0:
        best=m; m+=1
    return best
print("m(20001)=",mm(20001),"m(50001)=",mm(50001), "m(3776)=",mm(3776),"m(3775)=",mm(3775))
for n in (20001,50001,10**6,10**7):
    m=mm(n); print(n,m, n**(2/3)-6*n**(1/3)-1, n**(2/3)-6*n**(1/3)+37)
