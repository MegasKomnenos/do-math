# J7b 정확 검산: 7.6-7.7절의 항등식·부등식을 작은 k에서 정확 유리수로 확인한다.
from fractions import Fraction as Fr
from math import comb, log, exp
from functools import lru_cache

def p(m): return (m+1)**(m-1) if m>=1 else 1
@lru_cache(None)
def A(n,l):
    if l<0: return 0
    if n==0: return 1
    if l>=n-1: return p(n)
    return sum(comb(n-1,j-1)*min(j,l+1)*A(j-1,l)*A(n-j,l) for j in range(1,n+1))
def b(n,l): return A(n,l)-A(n,l-1)
def s(m,y): return Fr(A(m,y-1),p(m))
def c(m,Y): return Fr(b(m,Y),p(m))
def Pk(n,j,k): return Fr(min(j,k)*comb(n-1,j-1)*A(j-1,k-1)*A(n-j,k-1), A(n,k-1))
def Pn(n,j): return Fr(j*comb(n-1,j-1)*p(j-1)*p(n-j), p(n))
def clp(m,k): return Fr(b(m,k),A(m,k-1))
def clm(m,k): return Fr(b(m,k-1),A(m,k-1))
def mu(m,k): return clp(m,k)-clm(m,k)
def chi(m,j,k):
    L,R=j-1,m-j
    lin=Fr(0)
    if j==k: lin=-(1-clm(R,k))/k
    if j>k: lin=(clp(L,k)+clm(L,k)+clp(R,k)+clm(R,k))/k
    h=1 if j>k else 0
    return lin+(1+Fr(h,k))*clp(L,k)*clp(R,k)+(1-Fr(h,k))*clm(L,k)*clm(R,k)
def src(n,k): return sum(Pk(n,j,k)*chi(n,j,k) for j in range(1,n+1))
def inh(n,k): return sum(Pk(n,j,k)*(mu(j-1,k)*(k<=j-1<=2*k)+mu(n-j,k)*(k<=n-j<=2*k)) for j in range(1,n+1))
def inhlin(n,k): return sum(Pk(n,j,k)*((clp(j-1,k)+clm(j-1,k))*(k<=j-1<=2*k)+(clp(n-j,k)+clm(n-j,k))*(k<=n-j<=2*k)) for j in range(1,n+1))/k
def rw(n,k,q): return Fr(k,k+1+q)*Pn(n,k+1+q)/Pn(n,k)
def w(n,k,m): return Fr(comb(n-1,m)*p(m)*A(n-1-m,k-1), A(n,k-1)) if m>=k else Fr(0)
def pw(m,k): return (k+1)*c(m,k)-(k-1)*c(m,k-1)   # 𝔭_m
bad=0
for k in [3,4,5]:
    for nu in range(1,3*k+3):
        n=2*k+nu
        lhs=k*s(n,k)*src(n,k)
        r722=sum(Fr(k,j)*Pn(n,j)*((c(j-1,k-1)+c(j-1,k))*s(n-j,k)+s(j-1,k)*(c(n-j,k-1)+c(n-j,k))) for j in range(k+1,n+1))-Pn(n,k)*s(n-k,k-1)
        r723a=Pn(n,k)*(sum(rw(n,k,q)*(c(k+q,k-1)+c(k+q,k)) for q in range(nu,k+nu))-s(k+nu,k-1))
        r723b=Pn(n,k)*(c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1))
        ok = lhs>=r722>=r723a>=r723b
        # top-roots first bracket
        for U0 in range(0,k):
            tr=Pn(n,k)*(c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1)+sum((rw(n,k,k+nu-1-U)-1)*(s(n-1-U,k)-s(n-U,k)) for U in range(0,U0+1)))
            hz=lambda N: 1-s(N+1,k)/s(N,k)
            tr2=Pn(n,k)*s(n,k)*(sum((rw(n,k,k+nu-1-U)-1)*hz(n-1-U) for U in range(0,U0+1))-1)
            ok = ok and (r723a>=tr>=tr2)
        # rw(nu)=1 and rw>=1 for q>=nu
        ok = ok and rw(n,k,nu)==1 and all(rw(n,k,q)>=1 for q in range(nu,k+nu))
        # apex^H identity: k s_n apex = P_n(k) * first bracket
        apex=(sum(Pk(n,j,k)*(clp(j-1,k)+clm(j-1,k)) for j in range(n-k+1,n+1))-Pk(n,k,k)*(1-clm(n-k,k)))/k
        ok = ok and k*s(n,k)*apex==r723a
        if n>=3*k+1:
            ok = ok and src(n,k)-inhlin(n,k)-apex>=0
            Left=sum(w(n,k,m)*pw(m,k) for m in range(k,2*k+1))
            ok = ok and inhlin(n,k)+inh(n,k)==2*Left
            ok = ok and all(w(n,k,m+1)>=w(n,k,m) for m in range(k-1,2*k))
        if n<=3*k:
            KDp=sum((k+n-m)*comb(n-1,m)*p(n-1-m)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
            ok = ok and A(n,k-1)*(src(n,k)+inh(n,k))==(b(n,k)-b(n,k-1))-KDp
            ok = ok and all(w(n,k,m+1)>=w(n,k,m) for m in range(k-1,2*k))
        if n==3*k:
            Left=sum(w(n,k,m)*pw(m,k) for m in range(k,2*k+1))
            u=w(n,k,n-k)*s(n-k,k+1)
            Quad=sum(Pk(n,j,k)*((1+Fr(1,k))*clp(j-1,k)*clp(n-j,k)+(1-Fr(1,k))*clm(j-1,k)*clm(n-j,k)) for j in range(k+1,n+1))
            Stem=sum(Pk(n,j,k)*((clp(j-1,k)+clm(j-1,k))*(j-1>2*k)+(clp(n-j,k)+clm(n-j,k))*(n-j>2*k)) for j in range(k+1,n+1))/k
            ok = ok and src(n,k)+inh(n,k)==2*Left-u+Quad+Stem
            # threshold unit ratio telescoping: u/w_k = e^{g(2k)-g(k)} s_{2k}(k+1)/s_{2k-1}(k); e^{g(x)}=(1+1/x)^{x-1}
            eg=lambda x: Fr(x+1,x)**(x-1)
            ok = ok and u/w(n,k,k)==eg(2*k)/eg(k)*s(2*k,k+1)/s(2*k-1,k)
        if not ok:
            bad+=1; print("FAIL k=%d n=%d"%(k,n))
print("exact checks done; failures =", bad)
# explicit-bounds (나) numeric check
from math import lgamma, pi
def Bor(d): return exp(-d+(d-1)*log(d)-lgamma(d+1))
def Ren(j): return j*Bor(j)
worst=1e9
for m in [3,10,50,200,1000]:
    i_m=m*log(m/(m+1))+1
    assert 0<=i_m<=1/(2*(m+1))+1/(6*m*(m+1))
    for U in range(0,m):
        lhs=float(Pn(m,m-U)); rhs=Bor(U+1)*exp(i_m)*(m+1)/(m-U)
        worst=min(worst,rhs/lhs)
    for j in range(1,m+1):
        lhs=float(Pn(m,j)); rhs=Ren(j)*exp(i_m)*(m+1)/(m+1-j)**2
        worst=min(worst,rhs/lhs)
print("explicit-bounds (나) min(bound/actual) over tested m =", worst, "(>=1 required)")
