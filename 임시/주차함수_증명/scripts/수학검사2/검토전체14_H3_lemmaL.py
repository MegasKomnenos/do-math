# H3 검산: 보조정리 lemma-L(나)의 상수와 L(10^4), 정리 old-5-5 증명의 수치, 5.2.1 Newton 다항식 표본 재검
from mpmath import mp, quad, exp, sqrt, pi, inf, findroot, mpf, e as E
mp.dps=30
def M(i): return quad(lambda y: y**i*exp(-y-y**2/2),[0,inf])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y^2+y-i=0
    y=(-1+sqrt(1+4*i))/2
    return y**i*exp(-y-y**2/2)
M26=quad(lambda y: y**2*exp(-y-y**2/2),[0,6])
Ms=[M(i) for i in range(6)]; Mst={i:Mstar(i) for i in range(2,6)}
C1=2*Mst[2]+Ms[3]/2+Ms[5]/3; C2=Mst[3]/2+Mst[5]/3+Ms[4]/2; C3=Mst[4]/2+Ms[3]/6; C4=Mst[3]/6
def L(r):
    s=sqrt(r)
    return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(Ms[1]+(Ms[0]+exp(-mpf(1)/2))/s+1/s**2)
print("M_i:",[mp.nstr(m,10) for m in Ms]); print("M2^(6):",mp.nstr(M26,10)); print("M*_i:",{i:mp.nstr(v,10) for i,v in Mst.items()})
print("L(10^4)=",mp.nstr(L(10**4),10), ">=0.845204:", L(10**4)>=mpf('0.845204'))
print("L nondecreasing sample:",[mp.nstr(L(r),8) for r in (10**4,2*10**4,10**5,10**6)])
print("sqrt(3pi/2)=",mp.nstr(sqrt(3*pi/2),10), "sqrt(pi/2)=",mp.nstr(sqrt(pi/2),10))
print("0.5+2*0.845204-sqrt(3pi/2)=",mp.nstr(mpf('0.5')+2*mpf('0.845204')-sqrt(3*pi/2),8))
s=mpf(100); br=1/(3*s)+8/(3*s**2)+mpf('2.507')/s**2+(1+mpf('2.1709')*s)/s**3
print("bracket at s=100:",mp.nstr(br,6))
# tm_{r-1}(rho_r) direct for r=171 and Pc(k_r)
from math import ceil
def tm(r,rho):
    bt=mpf(1); Nu=mpf(0); De=mpf(0)
    for j in range(0,r):
        w=(j+1)*rho**j*bt
        Nu+=j*w; De+=w
        bt*= (1-mpf(j+1)/r)
    return Nu/De
for r in (171,1000,9999,10000):
    kr=ceil(r**1.5+8*r); rho=mpf(kr)/(kr+r); t=tm(r-1,rho)  # length r-1 birthday law
    eb=t
    Pc=kr*(mpf(1)/(2*r)-mpf(1)/(3*r**2))-mpf(5)/2+2*eb*(1-mpf(1)/kr)-mpf(kr)/(kr-1)*(1+sqrt(3*pi*(r-1)/2))
    print("r=%d k_r=%d rho_r=%s tm=%s Pc=%s Pc/sqrt r=%s  s*L(r)=%s"%(r,kr,mp.nstr(rho,8),mp.nstr(t,8),mp.nstr(Pc,8),mp.nstr(Pc/sqrt(r),6), mp.nstr(sqrt(r)*L(r),8) if r>=144 else '-'))
# m(n) examples
def mfun(n):
    ms=[m for m in range(171,5000) if m**1.5+9*m<=n]
    return max([170]+ms)
print("m(20001)=",mfun(20001),"m(50001)=",mfun(50001))
