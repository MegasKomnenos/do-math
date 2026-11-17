# R3 검산: 5.2.1–5.2.2절의 항등식과 부등식을 작은 경우에 정확 유리수로, 큰 경우에 mpmath로 대조한다.
import itertools, math
from fractions import Fraction as F
from math import comb, factorial
import sympy as sp

y=sp.symbols('y')
p=lambda n:(n+1)**(n-1) if n>=1 else 1

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        d=i+1
        for j in range(i-1,-1,-1):
            if sigma[j]>sigma[i]:
                d=i-j; break
        h.append(d)
    return h
_K={}
def Kpoly(n,k):
    # frozen capacity polynomial K_{n,k}(y)
    if (n,k) in _K: return _K[(n,k)]
    tot=0
    for s in itertools.permutations(range(1,n+1)):
        t=1
        for x in caps(s):
            t*= x if x<=k else y
        tot+=t
    _K[(n,k)]=sp.expand(tot); return _K[(n,k)]
def Gamma(d,n):
    G=[sp.Integer(1)]
    for dd in range(1,d+1):
        G.append(sp.expand(comb(n,dd)*p(dd)+y*sum(comb(n-dd+j,j)*p(j)*G[dd-1-j] for j in range(dd))))
    return G[d]
def phi(k,M):
    # number of rooted forests on m labelled vertices with all trees of size<=k : m! [x^m] exp(T^{<=k})
    x=sp.symbols('x')
    T=sum(sp.Rational(t**(t-1),factorial(t))*x**t for t in range(1,k+1))
    ser=sp.series(sp.exp(T),x,0,M+1).removeO()
    return [sp.Integer(ser.coeff(x,m)*factorial(m)) for m in range(M+1)]
def A(n,l):
    if l<0: return 0
    return sum(math.prod(min(x,l+1) for x in caps(s)) for s in itertools.permutations(range(1,n+1)))

ok=True
for k in range(1,4):
    ph=phi(k,8)
    for n in range(1,8):
        lhs=Kpoly(n,k)
        rhs=sp.expand(ph[n]+y*sum(ph[m]*Gamma(n-m-1,n) for m in range(k,n)))
        good=(sp.expand(lhs-rhs)==0)
        if (n<=2*k+1) and not good: ok=False; print("source-rep (ga) FAILS",n,k)
        if (n>2*k+1) and good: print("  (note) source-rep (ga) also holds at n=%d,k=%d beyond 2k+1"%(n,k))
        # green-connection (da)
        if n<=7 and k+1<=n:
            d1=sp.expand(Kpoly(n,k)-Kpoly(n,k+1)-(y-k-1)*p(k)*Gamma(n-k-1,n))
            if n<=2*k+1 and d1!=0: ok=False; print("green (da) FAILS",n,k)
            if n>2*k+1 and d1==0: print("  (note) green (da) holds beyond range at",n,k)
print("source-rep(ga), green-connection(da) within stated ranges:",ok)
# Gamma^- = B_{n,k-1} = K_{n,k}(k-1)-A_{n,k-2} ; Gamma^+ = K_{n,k}(k+2)-A_{n,k+1}; S decomposition
for k in range(2,5):
    for n in range(k,min(2*k-1,7)+1):
        Gm=p(k-1)*Gamma(n-k,n).subs(y,k-1)
        assert Gm==Kpoly(n,k).subs(y,k-1)-A(n,k-2),(n,k)
for k in range(1,5):
    for n in range(k+1,min(2*k+1,7)+1):
        Gp=p(k)*Gamma(n-k-1,n).subs(y,k+2)
        assert Gp==Kpoly(n,k).subs(y,k+2)-A(n,k+1),(n,k)
print("Gamma^-, Gamma^+ identities ok")
for k in range(3,5):
    for n in range(k+2,min(2*k-1,7)+1):
        r=n-k
        b=lambda l:A(n,l)-A(n,l-1)
        dk=b(k)-b(k-1); dk1=b(k+1)-b(k)
        Gp=p(k)*Gamma(r-1,n).subs(y,k+2); Gm=p(k-1)*Gamma(r,n).subs(y,k-1)
        S=Gp*dk-Gm*dk1
        ph=phi(k,8)
        hg=lambda d,v:(y*Gamma(d,n)).subs(y,v)
        sd=lambda d,v:hg(d,v+1)-2*hg(d,v)+hg(d,v-1)
        S2=sum(ph[n-d-1]*(Gp*sd(d,k)-Gm*sd(d,k+1)) for d in range(1,r))
        assert S==S2,(n,k)
        print("  S_{%d,%d}=%s (decomposition ok); d_{n,k}=%s"%(n,k,S,dk))
# tile model
def tw(j): return F(1) if j==1 else F((j-1)**(j-1),factorial(j))
def V(co):
    d=len(co); v=[F(1)]
    for m in range(1,d+1):
        s=(1+co[m-1])*v[m-1]+sum(tw(j)*v[m-j] for j in range(2,m+1))
        v.append(s)
    return v[d]
for n in range(2,9):
    for d in range(0,n):
        for yy in (F(1),F(3),F(7,2)):
            lhs=F(Gamma(d,n).subs(y,sp.Rational(yy.numerator,yy.denominator)).p,Gamma(d,n).subs(y,sp.Rational(yy.numerator,yy.denominator)).q)
            ff=F(factorial(n),factorial(n-d))
            assert lhs==ff*V([yy/(n-i+1) for i in range(1,d+1)]),(n,d,yy)
print("tile model identity ok")
# homogeneous coefficients
rho=sp.symbols('rho')
def hb(d):
    v=[sp.Integer(1)]
    for m in range(1,d+1):
        v.append(sp.expand((1+rho)*v[m-1]+sum(sp.Rational((j-1)**(j-1),factorial(j))*v[m-j] for j in range(2,m+1))))
    return v[d]
for d in range(1,9):
    h=hb(d)
    for j in range(0,d+1):
        assert h.coeff(rho,j)==sp.Rational((j+1)*(d+1)**(d-j-1)*1,factorial(d-j)) if d-j-1>=0 else h.coeff(rho,j)==1
    assert h.subs(rho,1)==sp.Rational((d+1)**d,factorial(d))
print("hb coefficients ok")
