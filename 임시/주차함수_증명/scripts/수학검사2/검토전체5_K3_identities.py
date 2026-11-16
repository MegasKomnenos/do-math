# K3: brute-force checks of the identities in 5.2.1-5.2.2 (small n), and the GF recursions of 5.2.3/5.4.1
from fractions import Fraction as F
from itertools import permutations, product
from math import comb, factorial
import math
import sympy as sp

def p(m): return (m+1)**(m-1) if m>=1 else 1

def park(a):
    n=len(a); spots=[0]*n; disp=[0]*n
    for car,pref in enumerate(a):
        s=pref
        while s<n and spots[s]: s+=1
        if s>=n: return None
        spots[s]=car+1; disp[car]=s-pref
    return spots, disp

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        d=i+1
        for j in range(i-1,-1,-1):
            if sigma[j]>sigma[i]: d=i-j; break
        h.append(d)
    return h

_cache={}
def pf_stats(n):
    if n in _cache: return _cache[n]
    b={}; E={}; E2={}; B={}
    for a in product(range(n), repeat=n):
        r=park(a)
        if r is None: continue
        sig,disp=r; M=max(disp); Mc=disp.count(M); h=caps(sig)
        b[M]=b.get(M,0)+1
        if Mc%2==0: E[M]=E.get(M,0)+1
        if Mc==2: E2[M]=E2.get(M,0)+1
        if all(h[i]==M+1 for i in range(n) if disp[sig[i]-1]==M): B[M]=B.get(M,0)+1
    _cache[n]=(b,E,E2,B)
    return _cache[n]

def Kpoly(n,k,y):
    tot=0
    for sig in permutations(range(1,n+1)):
        h=caps(list(sig)); pr=1
        for hi in h: pr*= hi if hi<=k else y
        tot+=pr
    return sp.expand(tot)

def Gamma(d,y,n):
    G=[sp.Integer(1)]
    for dd in range(1,d+1):
        s=sp.Integer(comb(n,dd)*p(dd))
        for j in range(dd): s+= y*comb(n-dd+j,j)*p(j)*G[dd-1-j]
        G.append(sp.expand(s))
    return G[d]

x=sp.symbols('x'); yy=sp.symbols('y')
def phi_list(k, mmax):
    Tk=sum(sp.Rational(j**(j-1),factorial(j))*x**j for j in range(1,k+1))
    ser=sp.series(sp.exp(Tk),x,0,mmax+1).removeO()
    P=sp.Poly(ser,x)
    return [int(P.coeff_monomial(x**m)*factorial(m)) for m in range(mmax+1)]

print("--- green-connection / source-rep checks")
T=sum(sp.Rational(j**(j-1),factorial(j))*x**j for j in range(1,10))
Gr=T-T**2/2
def Gcal(y,i,n):
    s=sp.symbols('s')
    inner=sp.series(sp.exp(-y*Gr.subs(x,s))*s**i/factorial(i), s,0,n+1).removeO()
    integ=sp.integrate(inner,(s,0,x))
    ser=sp.series(sp.exp(T)*sp.exp(y*Gr)*integ, x,0,n+1).removeO()
    return sp.expand(sp.Poly(ser,x).coeff_monomial(x**n)*factorial(n))
ok=True
for n in range(1,6):
    for d in range(0,n):
        g=Gcal(yy,n-d-1,n); gam=Gamma(d,yy,n)
        if sp.expand(g-gam)!=0: ok=False; print("(ga) FAIL",n,d,g,gam)
print("green (ga) Gamma_d = G_{y,n-d-1,n} for n<=5:", ok)

def Am(m,l):
    if m==0: return 1
    b=pf_stats(m)[0]
    return sum(b.get(j,0) for j in range(0,l+1))

fails=0
for n in range(1,7):
    b,E,E2,B=pf_stats(n)
    for k in range(1,n):
        if k+1<=n<=2*k+1:
            lhs=sp.expand(Kpoly(n,k,yy)-Kpoly(n,k+1,yy)); rhs=sp.expand((yy-k-1)*p(k)*Gamma(n-k-1,yy,n))
            if sp.expand(lhs-rhs)!=0: fails+=1; print("(da) FAIL",n,k,lhs,rhs)
            if B.get(k,0)!=p(k)*Gamma(n-k-1,sp.Integer(k),n): fails+=1; print("B FAIL",n,k,B.get(k,0),p(k)*Gamma(n-k-1,sp.Integer(k),n))
            s=sum(Am(m,k)*Gamma(n-m-1,sp.Integer(k),n) for m in range(k,n))
            if b.get(k,0)!=s: fails+=1; print("(ra) FAIL",n,k,b.get(k,0),s)
        if n<=2*k+1:
            ph=phi_list(k,n)
            rhs=sp.expand(ph[n]+yy*sum(ph[m]*Gamma(n-m-1,yy,n) for m in range(k,n)))
            if sp.expand(Kpoly(n,k,yy)-rhs)!=0: fails+=1; print("src(ga) FAIL",n,k)
            hg=lambda d,y: y*Gamma(d,y,n)
            sd=lambda d,y: hg(d,y+1)-2*hg(d,y)+hg(d,y-1)
            lhs2=2*E.get(k,0); rhs2=sum(ph[m]*sd(n-m-1,sp.Integer(k)) for m in range(k,n))
            if lhs2!=rhs2: fails+=1; print("src(na) FAIL",n,k,lhs2,rhs2)
            K=lambda yv: Kpoly(n,k,sp.Integer(yv))
            if 2*E.get(k,0)!=K(k+1)-2*K(k)+K(k-1): fails+=1; print("2E second-diff FAIL",n,k)
            dnk=b.get(k,0)-b.get(k-1,0)
            if dnk!=2*E.get(k,0)-B.get(k-1,0): fails+=1; print("tie-block FAIL",n,k)
            if k+2<=n<=2*k-1:
                r=n-k; Gp=p(k)*Gamma(r-1,sp.Integer(k+2),n); Gm=p(k-1)*Gamma(r,sp.Integer(k-1),n)
                S=Gp*dnk-Gm*(b.get(k+1,0)-b.get(k,0))
                S2=sum(ph[n-dd-1]*(Gp*sd(dd,sp.Integer(k))-Gm*sd(dd,sp.Integer(k+1))) for dd in range(1,r))
                if S!=S2: fails+=1; print("src(da) FAIL",n,k,S,S2)
                if Gm!=B.get(k-1,0): fails+=1; print("Gamma- != B FAIL",n,k)
                Ank1=sum(b.get(j,0) for j in range(k+2))
                if Gp!=K(k+2)-Ank1: fails+=1; print("Gamma+ FAIL",n,k)
print("source-rep/green checks n<=6: fails =", fails)

print("--- tile model checks")
def tw(j): return sp.Integer(1) if j==1 else sp.Rational((j-1)**(j-1),factorial(j))
bad=0
for n in range(3,9):
    for d in range(1,n):
        fs=[sp.Integer(1)]
        for dd in range(1,d+1):
            v=(1+yy/(n-dd+1))*fs[dd-1]+sum(tw(j)*fs[dd-j] for j in range(2,dd+1))
            fs.append(sp.expand(v))
        if sp.expand(fs[d]*sp.ff(n,d)-Gamma(d,yy,n))!=0: bad+=1; print("inverse-renewal FAIL",n,d)
print("inverse-renewal n<=8: fails =", bad)
rho=sp.symbols('rho')
bad=0
for d in range(1,9):
    hb=[sp.Integer(1)]
    for dd in range(1,d+1):
        hb.append(sp.expand((1+rho)*hb[dd-1]+sum(tw(j)*hb[dd-j] for j in range(2,dd+1))))
    P=sp.Poly(hb[d],rho)
    for j in range(0,d+1):
        exp_=sp.Rational((j+1)*(d+1)**(d-j-1), factorial(d-j)) if j<d else sp.Integer(1)
        if P.coeff_monomial(rho**j)!=exp_: bad+=1; print("hb coeff FAIL",d,j,P.coeff_monomial(rho**j),exp_)
    if P.eval(1)!=sp.Rational((d+1)**d,factorial(d)): bad+=1; print("hb(1) FAIL",d)
print("hb coefficients d<=8: fails =", bad)
for r in range(2,9):
    hbr=[sp.Integer(1)]
    for dd in range(1,r+1): hbr.append(sp.expand((1+rho)*hbr[dd-1]+sum(tw(j)*hbr[dd-j] for j in range(2,dd+1))))
    ratio=sp.simplify(hbr[r].subs(rho,1)/hbr[r-1].subs(rho,1)); assert ratio==sp.Rational(r+1,r)**r
    f=hbr[r]/hbr[r-1]
    for t in [0,sp.Rational(1,3),1,2]:
        assert sp.diff(f,rho).subs(rho,t)>=0
print("endpoint ratio (1+1/r)^r and monotonicity spot-checks ok")

print("--- chain GF recursions")
Ren=lambda m: m**m*math.exp(-m)/math.factorial(m)
def comps(j,dmax):
    def rec(prefix,rem):
        if len(prefix)==j: yield tuple(prefix); return
        for g in range(1,rem+1): yield from rec(prefix+[g],rem-g)
    yield from rec([],dmax)
def Ch_U_N(j,d):
    Ch=U=N=0.0
    for gam in comps(j,d):
        ds=[sum(gam[:i+1]) for i in range(j)]
        pr=math.prod(Ren(g) for g in gam)*math.prod(max(d-di,0) for di in ds)
        L=2.5*(ds[-1]-1)+sum(di-1 for di in ds[:-1])
        Nn=0.5*L*L+1.25*(ds[-1]-1)**2-(ds[-1]-1)/12+0.5*sum((di-1)**2 for di in ds[:-1])
        Ch+=pr; U+=L*pr; N+=Nn*pr
    return Ch,U,N
z=sp.symbols('z'); DEG=13
C=sum(sp.Float(Ren(m),30)*z**m for m in range(1,DEG+1))
def trunc(e): return (sp.series(sp.expand(e),z,0,DEG+1).removeO())
Cp=sp.diff(C,z); zCpp=sp.diff(z*Cp,z)
Zp=[None, trunc(z*C)]
Yp=[None, trunc(sp.Rational(5,2)*z*(z*Cp-C))]
Op=[None, trunc(z*(sp.Rational(35,8)*(z*zCpp-2*z*Cp+C)-sp.Rational(1,12)*(z*Cp-C)))]
inv=trunc(1/(1-z))
for j in range(2,5):
    D=lambda S: sp.diff(S,z)+2*inv*S
    Zj=trunc(C*z*D(Zp[j-1])); Zp.append(Zj)
    Yj=trunc(C*z*D(Yp[j-1])+((j+sp.Rational(3,2))*z*Cp-C)*z*D(Zp[j-1])); Yp.append(Yj)
    Oj=trunc(C*z*D(Op[j-1])+((j+sp.Rational(5,2))*z*Cp-C)*z*D(Yp[j-1])
             +(sp.Rational((2*j+3)*(2*j+5),8)*z*zCpp-(j+sp.Rational(31,12))*z*Cp+C)*z*D(Zp[j-1])); Op.append(Oj)
maxerr=0.0
for j in range(1,5):
    for r in range(1,DEG-2):
        ch=[Ch_U_N(j,d) for d in (r,r+1,r+2)]
        for idx,ser in ((0,Zp[j]),(1,Yp[j]),(2,Op[j])):
            d2=ch[2][idx]-2*ch[1][idx]+ch[0][idx]
            coef=float(sp.Poly(ser,z).coeff_monomial(z**(r+2)))
            if abs(d2)>1e-14: maxerr=max(maxerr, abs(coef-d2)/abs(d2))
            else: maxerr=max(maxerr, abs(coef))
print("chain GF recursions (Z,Y,O) vs direct enumeration, max rel err:", maxerr)

print("--- weight expansions")
nn=sp.symbols('n',positive=True); u=sp.symbols('u')
def nf(n,d): return sp.exp(d)*sp.ff(n,d)*(n-d)**(n-d-2)/n**(n-2)
bad=0
for d in range(1,5):
    lg=sp.log(nf(nn,d)); ser=sp.series(lg.subs(nn,1/u),u,0,4).removeO()
    for i in (1,2,3):
        lc=sp.Rational(1,i)*(sp.Rational(d**(i+1),i+1)+2*d**i-sum(rr**i for rr in range(d)))
        if sp.simplify(sp.Poly(ser,u).coeff_monomial(u**i)-lc)!=0: bad+=1; print("lc FAIL",d,i)
print("lc_i(d) d<=4,i<=3: fails =", bad)
ds=[2,5,6]
W=nf(nn,ds[-1]-1)*sp.prod([nn/(nn+1-di) for di in ds[:-1]])
ser=sp.series(W.subs(nn,1/u),u,0,3).removeO()
L=sp.Rational(5,2)*(ds[-1]-1)+sum(di-1 for di in ds[:-1])
Nn=sp.Rational(1,2)*L**2+sp.Rational(5,4)*(ds[-1]-1)**2-sp.Rational(ds[-1]-1,12)+sp.Rational(1,2)*sum((di-1)**2 for di in ds[:-1])
P=sp.Poly(ser,u)
print("W coeffs: const", sp.simplify(P.coeff_monomial(1)), " u:", sp.simplify(P.coeff_monomial(u)), "(L=",L,")  u^2:", sp.simplify(P.coeff_monomial(u**2)), "(N=",Nn,")")
rr=sp.symbols('r',positive=True)
print("nf ratio log series:", sp.series(1+(rr-3)*sp.log(1-1/rr),rr,sp.oo,6))
