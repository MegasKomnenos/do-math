# 7.6-7.7절의 항등식·부등식을 작은 k에서 정확 유리수로 검산한다.
from fractions import Fraction as Fr
from math import comb, exp, log, factorial
import itertools

def p(m): return (m+1)**(m-1) if m>=1 else 1
MAXN=40
A={}  # A[(m,l)]
def Aval(m,l):
    if l<0: return 0
    if m==0: return 1
    if (m,l) in A: return A[(m,l)]
    if l>=m-1:
        A[(m,l)]=p(m); return p(m)
    s=0
    for j in range(1,m+1):
        s+=comb(m-1,j-1)*min(j,l+1)*Aval(j-1,l)*Aval(m-j,l)
    A[(m,l)]=s; return s
def b(m,l): return Aval(m,l)-Aval(m,l-1)
def s(m,y): return Fr(Aval(m,y-1),p(m))
def c(m,Y): return Fr(b(m,Y),p(m))
def Pk(k,m,j): return Fr(min(j,k)*comb(m-1,j-1)*Aval(j-1,k-1)*Aval(m-j,k-1),Aval(m,k-1))
def P(m,j): return Fr(j*comb(m-1,j-1)*p(j-1)*p(m-j),p(m))
def clp(k,m): return Fr(b(m,k),Aval(m,k-1))
def clm(k,m): return Fr(b(m,k-1),Aval(m,k-1))
def mu(k,m): return clp(k,m)-clm(k,m)
def chi(k,m,j):
    v=Fr(0)
    if j==k: v+=-Fr(1,k)*(1-clm(k,m-k))
    if j>k: v+=Fr(1,k)*(clp(k,j-1)+clm(k,j-1)+clp(k,m-j)+clm(k,m-j))
    ind=1 if j>k else 0
    v+=(1+Fr(ind,k))*clp(k,j-1)*clp(k,m-j)+(1-Fr(ind,k))*clm(k,j-1)*clm(k,m-j)
    return v
def src(k,m): return sum(Pk(k,m,j)*chi(k,m,j) for j in range(1,m+1))
def inh(k,m): return sum(Pk(k,m,j)*(mu(k,j-1)*(k<=j-1<=2*k)+mu(k,m-j)*(k<=m-j<=2*k)) for j in range(1,m+1))
def inhlin(k,n): return Fr(1,k)*sum(Pk(k,n,j)*((clp(k,j-1)+clm(k,j-1))*(k<=j-1<=2*k)+(clp(k,n-j)+clm(k,n-j))*(k<=n-j<=2*k)) for j in range(1,n+1))
def rw(k,n,q):
    return Fr(k,k+1+q)*P(n,k+1+q)/P(n,k)
def gfun(x): return (x-1)*log(1+1/x)
ok=True
def chk(cond,msg):
    global ok
    if not cond: ok=False; print("FAIL:",msg)
for k in range(2,7):
    for nu in range(1,2*k+2):
        n=2*k+nu
        if n>MAXN: break
        # (7.13)
        chk(mu(k,n)==src(k,n)+sum(Pk(k,n,j)*(mu(k,j-1)+mu(k,n-j)) for j in range(1,n+1)),f"(7.13) k={k} n={n}")
        # root-symmetry
        chk(rw(k,n,nu)==1,f"rw(nu)=1 k={k} n={n}")
        for q in range(0,k+nu-1):
            lhs=float(rw(k,n,q+1)/rw(k,n,q)); rhs=exp(gfun(k+1+q)-gfun(k+nu-1-q))
            chk(abs(lhs-rhs)<1e-9*max(1,abs(rhs)),f"rw ratio k={k} n={n} q={q} {lhs} {rhs}")
        for q in range(nu,k+nu): chk(rw(k,n,q)>=1,f"rw>=1 k={k} n={n} q={q}")
        # (7.22)
        rhs722=sum(Fr(k,j)*P(n,j)*((c(j-1,k-1)+c(j-1,k))*s(n-j,k)+s(j-1,k)*(c(n-j,k-1)+c(n-j,k))) for j in range(k+1,n+1))-P(n,k)*s(n-k,k-1)
        chk(k*s(n,k)*src(k,n)>=rhs722,f"(7.22) k={k} n={n}")
        # also: equality when quadratic dropped -> check k s src - rhs722 == k s * quad part
        quad=sum(Pk(k,n,j)*((1+Fr(1 if j>k else 0,k))*clp(k,j-1)*clp(k,n-j)+(1-Fr(1 if j>k else 0,k))*clm(k,j-1)*clm(k,n-j)) for j in range(1,n+1))
        chk(k*s(n,k)*src(k,n)-rhs722==k*s(n,k)*quad,f"(7.22) exact k={k} n={n}")
        br1=sum(rw(k,n,q)*(c(k+q,k-1)+c(k+q,k)) for q in range(nu,k+nu))-s(k+nu,k-1)
        chk(rhs722>=P(n,k)*br1,f"(7.23a) k={k} n={n}")
        br2=c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1)
        chk(br1>=br2,f"(7.23b) k={k} n={n}")
        # top-roots
        for U0 in range(0,k):
            mid=br2+sum((rw(k,n,k+nu-1-U)-1)*(s(n-1-U,k)-s(n-U,k)) for U in range(0,U0+1))
            chk(br1>=mid,f"top-roots 2nd k={k} n={n} U0={U0}")
            hzpart=sum((rw(k,n,k+nu-1-U)-1)*(1-s(n-U,k)/s(n-1-U,k)) for U in range(0,U0+1))-1
            chk(mid>=s(n,k)*hzpart,f"top-roots 3rd k={k} n={n} U0={U0}")
        # apex^H identity: k s_n(k) apex = P_n(k) br1
        apex=Fr(1,k)*(sum(Pk(k,n,j)*(clp(k,j-1)+clm(k,j-1)) for j in range(n-k+1,n+1))-Pk(k,n,k)*(1-clm(k,n-k)))
        chk(k*s(n,k)*apex==P(n,k)*br1,f"apex identity k={k} n={n}")
        # (7.25) for 2k+1<=n<=3k
        if n<=3*k:
            KDp=sum((k+n-m)*comb(n-1,m)*p(n-1-m)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
            chk(Aval(n,k-1)*(src(k,n)+inh(k,n))==(b(n,k)-b(n,k-1))-KDp,f"(7.25) k={k} n={n}")
        # (7.24) and old-6-20 for n>=3k+1
        if n>=3*k+1:
            w=lambda m: Fr(comb(n-1,m)*p(m)*Aval(n-1-m,k-1),Aval(n,k-1))
            pm=lambda m: Fr((k+1)*b(m,k)-(k-1)*b(m,k-1),p(m))
            Left=sum(w(m)*pm(m) for m in range(k,2*k+1))
            chk(inhlin(k,n)+inh(k,n)==2*Left,f"(7.24) k={k} n={n}")
            for m in range(k,2*k): chk(w(m+1)>=w(m),f"w nondecr k={k} n={n} m={m}")
        if n==3*k:
            w=lambda m: Fr(comb(n-1,m)*p(m)*Aval(n-1-m,k-1),Aval(n,k-1))
            pm=lambda m: Fr((k+1)*b(m,k)-(k-1)*b(m,k-1),p(m))
            Left=sum(w(m)*pm(m) for m in range(k,2*k+1))
            u=w(2*k)*s(2*k,k+1)
            Quad=sum(Pk(k,n,j)*((1+Fr(1,k))*clp(k,j-1)*clp(k,n-j)+(1-Fr(1,k))*clm(k,j-1)*clm(k,n-j)) for j in range(k+1,n+1))
            Stem=Fr(1,k)*sum(Pk(k,n,j)*((clp(k,j-1)+clm(k,j-1))*(j-1>2*k)+(clp(k,n-j)+clm(k,n-j))*(n-j>2*k)) for j in range(k+1,n+1))
            chk(src(k,n)+inh(k,n)==2*Left-u+Quad+Stem,f"(7.26) k={k}")
            # threshold-unit-ratio first equality
            lhs=float(u/w(k)); rhs=exp(gfun(2*k)-gfun(k))*float(s(2*k,k+1)/s(2*k-1,k))
            chk(abs(lhs-rhs)<1e-9,f"u/w_k identity k={k} {lhs} {rhs}")
            # threshold-root identity in (7.26) proof
            lhs2=Pk(k,n,k)*(mu(k,2*k)-Fr(1,k)*(1-clm(k,2*k)))
            chk(lhs2==w(2*k)*pm(2*k)-u,f"threshold root term k={k}")
            chk(Pk(k,n,k)==k*w(2*k)*Fr(Aval(2*k,k-1),p(2*k)),f"P(k) = k w A/p k={k}")
# explicit-bounds (나) numerically
from mpmath import mp, mpf, binomial, factorial as mfac, e as me, log as mlog, exp as mexp
mp.dps=40
def Bor(d): return mexp(-d)*mpf(d)**(d-1)/mfac(d)
def Ren(j): return mpf(j)**(j-1)*mexp(-j)/mfac(j-1)
def Pm(m,j): return mpf(j)*binomial(m-1,j-1)*mpf(p(j-1))*mpf(p(m-j))/mpf(p(m))
for m in [1,2,3,5,10,30,80,200]:
    sg=m*mlog(mpf(m)/(m+1))+1
    chk(0<=sg<=1/(2*mpf(m+1))+1/(6*mpf(m)*(m+1)),f"sg bound m={m}")
    for U in range(0,m):
        chk(Pm(m,m-U)<=Bor(U+1)*mexp(sg)*mpf(m+1)/(m-U)*(1+mpf(10)**-30),f"EB(na)1 m={m} U={U}")
    for j in range(1,m+1):
        chk(Pm(m,j)<=Ren(j)*mexp(sg)*mpf(m+1)/mpf(m+1-j)**2*(1+mpf(10)**-30),f"EB(na)2 m={m} j={j}")
for d in range(1,200): chk(Bor(d)<=(2*mp.pi)**-0.5*mpf(d)**-1.5,f"Bor bound d={d}")
for m in range(1,200): chk(1-sum(Bor(d) for d in range(1,m+1))<=0.8/mpf(m)**0.5,f"Bor tail m={m}")
print("ALL OK" if ok else "SOME FAIL")
