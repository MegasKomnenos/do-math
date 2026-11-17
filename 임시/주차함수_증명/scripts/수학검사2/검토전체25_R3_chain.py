# R3 검산: 5.2.3절 — W^{[1]}=L, W^{[2]}=N의 식, 전달 다항식, 표시 사슬 합의 생성함수 재귀(Z^{(2)}_j, Y_j, O_j)를
# 간격 수열의 직접 열거와 대조한다. 또 핵 상하계, Laurent 계수, 거친 꼬리 상수를 수치로 본다.
import sympy as sp, itertools, math
from fractions import Fraction as Fr
u=sp.symbols('u')  # u=1/n
def logW(g):
    j=len(g); dd=list(itertools.accumulate(g)); d=dd[-1]-1
    # log nf(n,d) = d + sum_{rho<d} log(1-rho u) + (1/u-d-2) log(1-d u)
    e=d+sum(sp.log(1-rho*u) for rho in range(d))+(1/u-d-2)*sp.log(1-d*u)
    e-=sum(sp.log(1-(dd[i]-1)*u) for i in range(j-1))
    return e
def Wcoef(g,order=3):
    s=sp.series(sp.exp(sp.series(logW(g),u,0,order+1).removeO()),u,0,order).removeO()
    return [sp.nsimplify(s.coeff(u,i)) for i in range(order)]
def L(g):
    dd=list(itertools.accumulate(g)); return sp.Rational(5,2)*(dd[-1]-1)+sum(x-1 for x in dd[:-1])
def N(g):
    dd=list(itertools.accumulate(g)); 
    return L(g)**2/2+sp.Rational(5,4)*(dd[-1]-1)**2-sp.Rational(dd[-1]-1,12)+sp.Rational(1,2)*sum((x-1)**2 for x in dd[:-1])
ok=True
for g in [(1,),(2,),(5,),(1,1),(2,3),(3,1,2),(1,4,2,2),(2,2,2,1,3)]:
    c=Wcoef(g)
    if c[0]!=1 or sp.simplify(c[1]-L(g))!=0 or sp.simplify(c[2]-N(g))!=0: ok=False; print("W coef mismatch",g,c,L(g),N(g))
    j=len(g)
    if j>=2:
        gam=g[0]; gp=g[1:]
        if L(g)!=L(gp)+(j+sp.Rational(3,2))*gam-1: ok=False; print("L transfer mismatch",g)
        if sp.simplify(N(g)-(N(gp)+((j+sp.Rational(5,2))*gam-1)*L(gp)+sp.Rational(1,2)*(j+sp.Rational(3,2))*(j+sp.Rational(5,2))*gam**2-(j+sp.Rational(31,12))*gam+1))!=0: ok=False; print("N transfer mismatch",g)
print("W^{[1]},W^{[2]} and transfer formulas:",ok)
# generating function recursion vs direct enumeration (exact rationals impossible because Ren is transcendental -> use symbolic placeholders R_m)
D=11
R=sp.symbols('R1:%d'%(D+1))
z=sp.symbols('z')
C=sum(R[m-1]*z**m for m in range(1,D+1))
def trunc(e): 
    e=sp.expand(e); return sum(e.coeff(z,i)*z**i for i in range(D+1))
def inv1mz(pw):  # (1-z)^{-pw} truncated
    return sum(sp.binomial(pw+i-1,i)*z**i for i in range(D+1))
def op(F,iota=2): # z (F' + iota F/(1-z))
    return trunc(z*(sp.diff(F,z)+iota*F*inv1mz(1)))
zC1=trunc(z*sp.diff(C,z)); zC2=trunc(z*sp.diff(zC1,z))
Z={1:trunc(z*C)}; Y={1:trunc(sp.Rational(5,2)*z*(zC1-C))}; O={1:trunc(z*(sp.Rational(35,8)*(zC2-2*zC1+C)-sp.Rational(1,12)*(zC1-C)))}
for j in range(2,4):
    Z[j]=trunc(C*op(Z[j-1]))
    Y[j]=trunc(C*op(Y[j-1])+((j+sp.Rational(3,2))*zC1-C)*op(Z[j-1]))
    O[j]=trunc(C*op(O[j-1])+((j+sp.Rational(5,2))*zC1-C)*op(Y[j-1])+(sp.Rational((2*j+3)*(2*j+5),8)*zC2-(j+sp.Rational(31,12))*zC1+C)*op(Z[j-1]))
def comps(j,maxsum):
    def rec(pref,s):
        if len(pref)==j: yield tuple(pref); return
        for g in range(1,maxsum-s-(j-len(pref)-1)+1):
            yield from rec(pref+[g],s+g)
    yield from rec([],0)
def Ch(j,d,wfun):
    tot=0
    for g in comps(j,d-1):
        dd=list(itertools.accumulate(g))
        pr=1
        for x in dd: pr*=max(d-x,0)
        if pr==0: continue
        w=wfun(g)
        for x in g: w*=R[x-1]
        tot+=w*pr
    return sp.expand(tot)
ok2=True
for j in (1,2,3):
    for r in range(1,D-2+1):
        for nm,wf,gf in (("Ch",lambda g:1,Z),("U",L,Y),("N",N,O)):
            d2=sp.expand(Ch(j,r+2,wf)-2*Ch(j,r+1,wf)+Ch(j,r,wf))
            if sp.expand(d2-gf[j].coeff(z,r+2))!=0: ok2=False; print("GF mismatch",nm,j,r)
print("generating-function recursions vs enumeration (j<=3, r<=%d):"%(D-2),ok2)
# kernel bounds
import mpmath as mp
mp.mp.dps=40
Ren=lambda m: mp.mpf(m)**m*mp.e**(-m)/mp.factorial(m)
cb=lambda m: mp.binomial(2*m,m)/mp.mpf(4)**m
o=1/mp.sqrt(2)
ok3=True
for m in range(1,3000):
    q=Ren(m)/(o*cb(m))
    if not (1<=q<=1+mp.mpf(1)/(12*(2*m-1))): ok3=False; print("kernel-C fails",m)
    if not (q>=1+mp.mpf(1)/(25*(2*m-1))): ok3=False; print("kernel-bounds fails",m)
    if m>1 and not (Ren(m)/cb(m)<Ren(m-1)/cb(m-1)): ok3=False
print("kernel bounds m<3000:",ok3, " Ren(1)/(o cb_1)=",mp.nstr(Ren(1)/(o*cb(1)),10)," 26/25=1.04")
# sum_{m>=5} 2m l_m 2^{2-2m}
lm=lambda m:(2+mp.mpf(1)/m)*mp.zeta(2*m)/mp.pi**(2*m)
print("l1,l2,l3=",lm(1),lm(2),lm(3), " sum_{m>=5}2m l_m 2^{2-2m}=",mp.nsum(lambda m:2*m*lm(m)*mp.mpf(2)**(2-2*m),[5,mp.inf]))
print("log et(1/2)=",mp.nsum(lambda m:lm(m)*mp.mpf(4)**(-m),[1,mp.inf]), " sum 2m l_m 4^{1-m}=",mp.nsum(lambda m:2*m*lm(m)*mp.mpf(4)**(1-m),[1,mp.inf]))
# Laurent coefficient cases
w=lambda i,U: mp.taylor(lambda t:(1-t)**(mp.mpf(i)/2),0,U)[U]
for U in (1,2,5,9):
    for Up in (1,2,3):
        a=w(-2*Up,U); b=mp.binomial(U+Up-1,Up-1)
        c=w(-1-2*Up,U); d=cb(U)*mp.fprod([U+mp.mpf(1)/2+t for t in range(Up)])/mp.fprod([mp.mpf(1)/2+t for t in range(Up)])
        e=w(2*Up-1,U); f=cb(U)*mp.fprod([-(mp.mpf(1)/2+t) for t in range(Up)])/mp.fprod([U-mp.mpf(1)/2-t for t in range(Up)])
        assert abs(a-b)<1e-25 and abs(c-d)<1e-25 and abs(e-f)<1e-25,(U,Up,a,b,c,d,e,f)
    assert abs(w(-1,U)-cb(U))<1e-25 and abs(w(1,U)+cb(U)/(2*U-1))<1e-25
print("Laurent coefficient formulas ok")
