# R3 check 4: 5.2.3 and 5.4.1 (kernel bounds, chain weights, marked recursions, tails).
import itertools, random
import mpmath as mp
from fractions import Fraction as Fr
from math import comb
mp.mp.dps=40
ok=True
def Ren(m): return mp.exp(m*mp.log(m)-m-mp.loggamma(m+1))
def cb(m): return mp.binomial(2*m,m)/mp.mpf(4)**m
o=1/mp.sqrt(2)
# kernel-C-bound, kernel-bounds, kernel-crude
prev=None
for m in range(1,3001):
    q=Ren(m)/(o*cb(m))
    if not (1<=q<=1+mp.mpf(1)/(12*(2*m-1))): ok=False; print("kernel-C FAIL",m)
    if not q>=1+mp.mpf(1)/(25*(2*m-1)): ok=False; print("kernel-bounds FAIL",m)
    rr=Ren(m)/cb(m)
    if prev is not None and rr>=prev: ok=False; print("crude monotone FAIL",m)
    prev=rr
print("Ren(1)/(o cb_1)=",Ren(1)/(o*cb(1)),"26/25=",1.04,"181/174=",mp.mpf(181)/174)
print("312m^2-374m+25 at m=2:",312*4-374*2+25)
# nf log coefficients
def nf(n,d): return mp.exp(d+mp.loggamma(n+1)-mp.loggamma(n-d+1)+(n-d-2)*mp.log(n-d)-(n-2)*mp.log(n))
def lc(i,d): return Fr(1,i)*(Fr(d**(i+1),i+1)+2*d**i-sum(Fr(r**i) for r in range(d)))
for d in (0,1,3,7):
    assert lc(1,d)==Fr(5,2)*d and lc(2,d)==Fr(5,4)*d*d-Fr(d,12)
    n=mp.mpf(10)**6
    approx=sum(mp.mpf(lc(i,d).numerator)/lc(i,d).denominator*n**(-i) for i in range(1,6))
    if abs(mp.log(nf(n,d))-approx)>mp.mpf(10)**(-30): ok=False; print("lc FAIL",d,mp.log(nf(n,d))-approx)
# chain weights W_n(gamma), L, N, envelope
def W(n,g):
    ds=list(itertools.accumulate(g)); j=len(g)
    w=nf(n,ds[-1]-1)
    for i in range(j-1): w*=mp.mpf(n)/(n+1-ds[i])
    return w
def LN(g):
    ds=list(itertools.accumulate(g)); j=len(g)
    L=Fr(5,2)*(ds[-1]-1)+sum(ds[i]-1 for i in range(j-1))
    Nn=L*L/2+Fr(5,4)*(ds[-1]-1)**2-Fr(ds[-1]-1,12)+Fr(1,2)*sum((ds[i]-1)**2 for i in range(j-1))
    return L,Nn
random.seed(1)
for _ in range(300):
    j=random.randint(1,6); g=[random.randint(1,5) for _ in range(j)]
    L,Nn=LN(g)
    if j>=2:
        L1,N1=LN(g[1:]); ga=g[0]
        if L!=L1+(j+Fr(3,2))*ga-1: ok=False; print("L rec FAIL",g)
        if Nn!=N1+((j+Fr(5,2))*ga-1)*L1+Fr(1,2)*(j+Fr(3,2))*(j+Fr(5,2))*ga*ga-(j+Fr(31,12))*ga+1: ok=False; print("N rec FAIL",g)
    else:
        ga=g[0]
        if L!=Fr(5,2)*(ga-1) or Nn!=Fr(35,8)*(ga-1)**2-Fr(ga-1,12): ok=False; print("j=1 FAIL")
    n=10**7; w=W(n,g); Lf=mp.mpf(L.numerator)/L.denominator; Nf=mp.mpf(Nn.numerator)/Nn.denominator
    dj=sum(g); tol=2*mp.binomial(j+mp.mpf(7)/2,3)*(dj-1)**3/n+mp.mpf(10)**(-9)   # third-order term bound from (ga) of the all-orders theorem
    if not (-mp.mpf(10)**(-9)<=(w-1-Lf/n)*n*n-Nf<=tol): ok=False; print("W expansion FAIL",g,(w-1-Lf/n)*n*n,Nf)
    # envelope at moderate n
    r=sum(g)-1+random.randint(0,3); n=2*r+1+random.randint(0,40)
    if r+1<n:
        w=W(n,g); rq=mp.mpf(r)/n
        Rm=(1-rq)**(-j-mp.mpf(3)/2)-1-(j+mp.mpf(3)/2)*rq; Rm2=Rm-(j+1.5)*(j+2.5)/2*rq**2
        e1=w-1-Lf/n; e2=e1-Nf/n**2
        if not (0<=e1<=Rm and -1e-30<=e2<=Rm2): ok=False; print("envelope FAIL",g,n,r,e1,Rm,e2,Rm2)
# generating functions vs direct sums
D=22
c=[mp.mpf(0)]+[Ren(m) for m in range(1,D+1)]
def mul(a,b):
    r=[mp.mpf(0)]*(D+1)
    for i,x in enumerate(a):
        if x==0: continue
        for jx,y in enumerate(b):
            if i+jx>D: break
            r[i+jx]+=x*y
    return r
def add(*xs): return [sum(x[i] for x in xs) for i in range(D+1)]
def sc(s,a): return [s*x for x in a]
def der(a): return [(i+1)*a[i+1] for i in range(D)]+[mp.mpf(0)]
def zmul(a): return [mp.mpf(0)]+a[:D]
def theta(a): return [i*a[i] for i in range(D+1)]   # z d/dz
inv1mz=[mp.mpf(1)]*(D+1)
def op(F): return zmul(add(der(F),sc(2,mul(inv1mz,F))))   # z(F' + 2F/(1-z))
zC1=theta(c); zC2=theta(theta(c))
Z={1:zmul(c)}
Y={1:sc(mp.mpf(5)/2,zmul(add(zC1,sc(-1,c))))}
O={1:zmul(add(sc(mp.mpf(35)/8,add(zC2,sc(-2,zC1),c)),sc(-mp.mpf(1)/12,add(zC1,sc(-1,c)))))}
for j in range(2,5):
    Z[j]=mul(c,op(Z[j-1]))
    Y[j]=add(mul(c,op(Y[j-1])),mul(add(sc(j+mp.mpf(3)/2,zC1),sc(-1,c)),op(Z[j-1])))
    O[j]=add(mul(c,op(O[j-1])),mul(add(sc(j+mp.mpf(5)/2,zC1),sc(-1,c)),op(Y[j-1])),
             mul(add(sc(mp.mpf((2*j+3)*(2*j+5))/8,zC2),sc(-(j+mp.mpf(31)/12),zC1),c),op(Z[j-1])))
def comps(j,maxsum):
    def rec(pref,s):
        if len(pref)==j: yield pref; return
        for g in range(1,maxsum-s-(j-len(pref)-1)+1):
            yield from rec(pref+[g],s+g)
    yield from rec([],0)
def direct(j,d,which):
    tot=mp.mpf(0)
    for g in comps(j,d-1):
        ds=list(itertools.accumulate(g)); pr=mp.mpf(1)
        for i in range(j): pr*=c[g[i]]*(d-ds[i])
        L,Nn=LN(g)
        wt=1 if which==0 else (mp.mpf(L.numerator)/L.denominator if which==1 else mp.mpf(Nn.numerator)/Nn.denominator)
        tot+=wt*pr
    return tot
for j in range(1,5):
    for r in range(1,D-2-4):
        if r>10 and j>=3: continue
        for which,GF in ((0,Z),(1,Y),(2,O)):
            dd=direct(j,r+2,which)-2*direct(j,r+1,which)+direct(j,r,which)
            if abs(dd-GF[j][r+2])>mp.mpf(10)**(-25)*(1+abs(dd)): ok=False; print("GF FAIL",j,r,which,dd,GF[j][r+2])
    if any(x< -mp.mpf(10)**(-30) for x in Z[j]+Y[j]+O[j]): ok=False; print("negativity FAIL",j)
# parity-tail
dc={2:mp.mpf(2)}
for j in range(2,4): dc[j+1]=mp.mpf(3)/4*(mp.mpf(3*j)/2-1+2)*dc[j]
for j in range(2,5):
    th=mp.mpf(3*j)/2-1
    for U in range(0,D+1):
        coef=mp.gamma(U+th)/(mp.gamma(th)*mp.factorial(U))
        if Z[j][U]>dc[j]*coef: ok=False; print("parity-tail FAIL",j,U)
# omitted-tail ratio formula
def Tl(j,n,r):
    th=mp.mpf(3*j)/2-1
    dcj=mp.mpf(2)
    for i in range(2,j): dcj*=mp.mpf(3)/4*(mp.mpf(3*i)/2+1)
    return mp.e*mp.mpf(n)**(1-j)*(1-mp.mpf(r)/n)**(-j-mp.mpf(3)/2)*dcj*mp.gamma(r+2+th)/(mp.gamma(th)*mp.factorial(r+2))
for (j,n,r) in [(3,30000,700),(25,40000,900),(31,10**6,5000)]:
    th=mp.mpf(3*j)/2-1; x32=mp.mpf(r)**1.5/n; rq=mp.mpf(r)/n
    form=mp.mpf(9)/16*x32**2/(1-rq)**2*mp.mpf(2*(3*j+5))/(3*j*(3*j-2))*mp.fprod((r+2+th+i)/r for i in range(3))
    if abs(Tl(j+2,n,r)/Tl(j,n,r)/form-1)>1e-25: ok=False; print("Tl ratio FAIL",j,n,r)
print("(12/11)^1.5*(1+1/598)=",(mp.mpf(12)/11)**1.5*(1+mp.mpf(1)/598),"110e/12=",110*mp.e/12,"log10(1.15*598^3)=",mp.log10(1.15*598**3),"598log10(24)=",598*mp.log10(24))
print("(r+1)/n bound:",mp.mpf(9)/5*(1+mp.mpf(1)/598)/mp.sqrt(598))
# laurent-coeff
for i in (-5,-3,-1,1,3,5,-2,-4,2,4):
    for U in range(1,12):
        true=mp.binomial(mp.mpf(i)/2,U)*(-1)**U
        h=-mp.mpf(i)/2
        if i%2==0:
            form=mp.binomial(U+int(h)-1,int(h)-1) if h>0 else (0 if U>i/2 else None)
        else:
            if h>0:
                Up=int(h-mp.mpf(1)/2); form=cb(U)*mp.fprod(U+mp.mpf(1)/2+t for t in range(Up))/mp.fprod(mp.mpf(1)/2+t for t in range(Up))
            else:
                Up=int(mp.mpf(1)/2-h); form=cb(U)*mp.fprod(-mp.mpf(1)/2-t for t in range(Up))/mp.fprod(U-mp.mpf(1)/2-t for t in range(Up))
        if form is not None and abs(true-form)>1e-30: ok=False; print("laurent FAIL",i,U,true,form)
# cut-rep constants
l=lambda m:(2+mp.mpf(1)/m)*mp.zeta(2*m)/mp.pi**(2*m)
print("l1,l2,l3=",l(1),l(2)*36,l(3)*405)
print("sum_{m>=5} 2m l_m 2^(2-2m)=",mp.nsum(lambda m:2*m*l(m)*mp.mpf(2)**(2-2*m),[5,mp.inf]))
print("log et(1/2)=",mp.nsum(lambda m:l(m)*mp.mpf(1)/4**m,[1,mp.inf]), "direct:",1+mp.log(mp.mpf(1)/2/mp.sin(0.5))-0.5*mp.cot(0.5))
print("1-cos1=",1-mp.cos(1))
print("ku boxes: top",mp.mpf(10001)**(-mp.mpf(1)/3),"after 29*0.0015+0.00141:",mp.mpf(10001)**(-mp.mpf(1)/3)-29*0.0015-0.00141,"0.0015/1.25^12=",0.0015/1.25**12)
print("ALL OK" if ok else "SOME FAIL")
