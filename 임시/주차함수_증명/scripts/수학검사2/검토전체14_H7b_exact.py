# 7.6-7.7절 항등식·부등식의 정확 유리수 재확인 (H7b)
from fractions import Fraction
from math import comb, exp, log, lgamma
from functools import lru_cache
def p(m): return Fraction((m+1)**(m-1)) if m>=1 else Fraction(1)
def P(n,j): return Fraction(j*comb(n-1,j-1))*p(j-1)*p(n-j)/p(n)
def sg(m): return m*log(m/(m+1))+1
def logBor(d): return -d+(d-1)*log(d)-lgamma(d+1)
def logRen(j): return j*log(j)-j-lgamma(j+1)
def logP(n,j): return log(j)+lgamma(n)-lgamma(j)-lgamma(n-j+1)+(j-2)*log(j)+(n-j-1)*log(n-j+1)-(n-1)*log(n+1) if j<n else log(n)+(n-2)*log(n)-(n-1)*log(n+1)
bad=0
for m in [5,10,50,200,1000]:
    for U in range(0,m):
        if logP(m,m-U)>logBor(U+1)+sg(m)+log(m+1)-log(m-U)+1e-9: bad+=1
    for j in range(1,m+1):
        if logP(m,j)>logRen(j)+sg(m)+log(m+1)-2*log(m+1-j)+1e-9: bad+=1
print("explicit-bounds (나) violations:",bad)
@lru_cache(None)
def A(m,l):
    if l<0: return 0
    if m==0: return 1
    return sum(comb(m-1,j-1)*min(j,l+1)*A(j-1,l)*A(m-j,l) for j in range(1,m+1))
def s(m,y): return Fraction(A(m,y-1))/p(m)
def c(m,Y): return Fraction(A(m,Y)-A(m,Y-1))/p(m)
def Pk(n,j,k): return Fraction(min(j,k)*comb(n-1,j-1)*A(j-1,k-1)*A(n-j,k-1),A(n,k-1))
def cl(m,k,sgn): return c(m,k if sgn>0 else k-1)/s(m,k) if m>=k else Fraction(0)
def chi(n,j,k):
    L=j-1;R=n-j;lin=Fraction(0)
    if j==k: lin-=Fraction(1,k)*(1-cl(R,k,-1))
    if j>k: lin+=Fraction(1,k)*(cl(L,k,1)+cl(L,k,-1)+cl(R,k,1)+cl(R,k,-1))
    h=1 if j>k else 0
    return lin+(1+Fraction(h,k))*cl(L,k,1)*cl(R,k,1)+(1-Fraction(h,k))*cl(L,k,-1)*cl(R,k,-1)
def src(n,k): return sum(Pk(n,j,k)*chi(n,j,k) for j in range(1,n+1))
viol=0
for k in [3,4,5]:
    for nu in range(1,k+3):
        n=2*k+nu
        lhs=k*s(n,k)*src(n,k)
        rhs=sum(Fraction(k,j)*P(n,j)*((c(j-1,k-1)+c(j-1,k))*s(n-j,k)+s(j-1,k)*(c(n-j,k-1)+c(n-j,k))) for j in range(k+1,n+1))-P(n,k)*s(n-k,k-1)
        rw=lambda q:Fraction(k,k+1+q)*P(n,k+1+q)/P(n,k)
        if rw(nu)!=1: viol+=1
        b1=P(n,k)*(sum(rw(q)*(c(k+q,k-1)+c(k+q,k)) for q in range(nu,k+nu))-s(k+nu,k-1))
        b2=P(n,k)*(c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1))
        if not (lhs>=rhs>=b1>=b2): viol+=1; print("viol",k,nu)
        # top-roots second/third with U0=k-1
        hz=lambda N:1-s(N+1,k)/s(N,k)
        U0=k-1
        b3=P(n,k)*(c(k+nu,k-1)+s(k+nu,k+1)-s(n,k)-s(n,k+1)+sum((rw(k+nu-1-U)-1)*(s(n-1-U,k)-s(n-U,k)) for U in range(U0+1)))
        b4=P(n,k)*s(n,k)*(sum((rw(k+nu-1-U)-1)*hz(n-1-U) for U in range(U0+1))-1)
        if not (b1>=b3>=b4): viol+=1; print("top-roots viol",k,nu)
        # apex identity: k s_n(k) apex^H = P_n(k)*bracket1
        apex=Fraction(1,k)*(sum(Pk(n,j,k)*(cl(j-1,k,1)+cl(j-1,k,-1)) for j in range(n-k+1,n+1))-Pk(n,k,k)*(1-cl(n-k,k,-1)))
        if k*s(n,k)*apex!=b1: viol+=1; print("apex viol",k,nu)
print("(7.22)/(7.23)/top-roots/apex violations:",viol)
def mu(m,k): return Fraction(A(m,k)-2*A(m,k-1)+A(m,k-2),A(m,k-1))
def inh(n,k): return sum(Pk(n,j,k)*(mu(j-1,k)*(k<=j-1<=2*k)+mu(n-j,k)*(k<=n-j<=2*k)) for j in range(1,n+1))
v2=0
for k in [3,4,5,6]:
    for n in range(2*k+1,3*k+1):
        KD=sum((k+n-m)*comb(n-1,m)*int(p(n-1-m))*(A(m,k)-2*A(m,k-1)+A(m,k-2)) for m in range(2*k+1,n))
        if A(n,k-1)*(src(n,k)+inh(n,k))!=(A(n,k)-2*A(n,k-1)+A(n,k-2))-KD: v2+=1; print("7.25 viol",k,n)
    n=3*k
    w=lambda m:Fraction(comb(n-1,m)*A(n-1-m,k-1),A(n,k-1))*p(m)
    pp=lambda m:Fraction((k+1)*(A(m,k)-A(m,k-1))-(k-1)*(A(m,k-1)-A(m,k-2)))/p(m)
    Left=sum(w(m)*pp(m) for m in range(k,2*k+1))
    u=w(2*k)*s(2*k,k+1)
    Quad=sum(Pk(n,j,k)*((1+Fraction(1,k))*cl(j-1,k,1)*cl(n-j,k,1)+(1-Fraction(1,k))*cl(j-1,k,-1)*cl(n-j,k,-1)) for j in range(k+1,n+1))
    Stem=Fraction(1,k)*sum(Pk(n,j,k)*((cl(j-1,k,1)+cl(j-1,k,-1))*(j-1>2*k)+(cl(n-j,k,1)+cl(n-j,k,-1))*(n-j>2*k)) for j in range(k+1,n+1))
    if src(n,k)+inh(n,k)!=2*Left-u+Quad+Stem: v2+=1; print("7.26 viol",k)
    g=lambda x:(x-1)*log(1+1/x)
    if abs(float(u/w(k))-exp(g(2*k)-g(k))*float(s(2*k,k+1)/s(2*k-1,k)))>1e-9: v2+=1; print("thr-ratio viol",k)
    # w nondecreasing on [k,2k]
    if any(w(m+1)<w(m) for m in range(k,2*k)): v2+=1; print("w monotone viol",k)
print("7.24-7.26/thr-ratio violations:",v2)
v3=0
for k in [3,4]:
    for n in range(3*k+1,3*k+4):
        w=lambda m:Fraction(comb(n-1,m)*A(n-1-m,k-1),A(n,k-1))*p(m)
        pp=lambda m:Fraction((k+1)*(A(m,k)-A(m,k-1))-(k-1)*(A(m,k-1)-A(m,k-2)))/p(m)
        Left=sum(w(m)*pp(m) for m in range(k,2*k+1))
        inhlin=Fraction(1,k)*sum(Pk(n,j,k)*((cl(j-1,k,1)+cl(j-1,k,-1))*(k<=j-1<=2*k)+(cl(n-j,k,1)+cl(n-j,k,-1))*(k<=n-j<=2*k)) for j in range(1,n+1))
        if inhlin+inh(n,k)!=2*Left: v3+=1; print("7.24 viol",k,n)
        if Pk(n,k+1,k)!=k*s(k,k)*w(k): v3+=1
print("(7.24) violations:",v3)
