# P10: 10.1-10.2 항등식 검산 (정확 유리수). 장부 항등식(old-8-2), 분할 무게 (a)(d)(e), 꼬리합 꼴(old-8-6), 머묾 꼴(old-8-8), DD 항등식
from fractions import Fraction as F
from math import comb
import sys
KMAX=int(sys.argv[1]) if len(sys.argv)>1 else 9
def pf(m): return (m+1)**(m-1) if m>=1 else 1
A={}
def Acnt(m,l):
    if l<0: return 0
    if m==0: return 1
    key=(m,l)
    if key in A: return A[key]
    v=sum(comb(m-1,j-1)*min(j,l+1)*Acnt(j-1,l)*Acnt(m-j,l) for j in range(1,m+1))
    A[key]=v; return v
def s(m,y): return F(Acnt(m,y-1),pf(m))
def c(m,Y): return F(Acnt(m,Y)-Acnt(m,Y-1),pf(m))
def b(m,Y): return Acnt(m,Y)-Acnt(m,Y-1)
bad=0
for k in range(3,KMAX+1):
    for nu in range(1,k+1):
        n=2*k+nu; N=k+nu
        An=Acnt(n,k-1)
        def P(j): return F(min(j,k)*comb(n-1,j-1)*Acnt(j-1,k-1)*Acnt(n-j,k-1),An)
        def cl(m,sgn):
            if m<=k-1: return F(0)
            return F(b(m,k) if sgn>0 else b(m,k-1), Acnt(m,k-1))
        def mu(m): return F(b(m,k)-b(m,k-1),Acnt(m,k-1)) if m>=1 else F(0)
        def chi(j):
            v=F(0)
            if j==k: v-=F(1,k)*(1-cl(n-j,-1))
            if j>k: v+=F(1,k)*(cl(j-1,1)+cl(j-1,-1)+cl(n-j,1)+cl(n-j,-1))
            h=F(1,k) if j>k else F(0)
            v+=(1+h)*cl(j-1,1)*cl(n-j,1)+(1-h)*cl(j-1,-1)*cl(n-j,-1)
            return v
        src=sum(P(j)*chi(j) for j in range(1,n+1))
        inh=sum(P(j)*(mu(j-1)*(k<=j-1<=2*k)+mu(n-j)*(k<=n-j<=2*k)) for j in range(1,n+1))
        star=src+inh
        # 7.25 check
        KDp=sum((k+n-m)*comb(n-1,m)*pf(n-1-m)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        assert An*star==(b(n,k)-b(n,k-1))-KDp, ("7.25",k,nu)
        def w(m): return F(comb(n-1,m)*pf(m)*Acnt(n-1-m,k-1),An)
        u=w(N)*s(N,k+1)
        Quad=sum(P(j)*((1+F(1,k))*cl(j-1,1)*cl(n-j,1)+(1-F(1,k))*cl(j-1,-1)*cl(n-j,-1)) for j in range(k+1,n+1))
        Stem=sum(P(j)*F(1,k)*((cl(j-1,1)+cl(j-1,-1))*(j-1>2*k)+(cl(n-j,1)+cl(n-j,-1))*(n-j>2*k)) for j in range(k+1,n+1))
        Stem2=sum(w(m)*(c(m,k)+c(m,k-1)) for m in range(2*k+1,n))
        assert Stem==Stem2,("Stem",k,nu)
        def f(m):
            if m<=N: return 2*((k+1)*c(m,k)-(k-1)*c(m,k-1))
            return (k+n-m+1)*c(m,k)-(k+n-m-1)*c(m,k-1)
        def T(m): return sum(f(i) for i in range(m,2*k+1))
        rhs=sum(w(m)*f(m) for m in range(k,2*k+1))-u+Quad+Stem
        if star!=rhs: bad+=1; print("old-8-2 FAIL",k,nu)
        # (a)
        def g(x): 
            from math import log
            return (x-1)*log(1+1/x)
        for m in range(k,n-1):
            r=F(Acnt(n-1-m,k-1),(n-1-m)*Acnt(n-2-m,k-1))
            # e^{g(m+1)} = p_{m+1}/((m+1)p_m)
            eg=F(pf(m+1),(m+1)*pf(m))
            assert w(m+1)/w(m)==eg/r,("(a)",k,nu,m)
        # (c)
        for m in range(k,2*k):
            assert w(m+1)>=w(m),("(c)",k,nu,m)
        # (e) telescoping with s
        for m in range(k,N+1):
            gl=F(1)
            for i in range(k,m):
                gl*=F(pf(i+1),(i+1)*pf(i))/F(pf(n-1-i),(n-1-i)*pf(n-2-i))
            assert w(m)/w(k)==gl*s(n-1-m,k)/s(N-1,k),("(e)",k,nu,m)
        # old-8-6
        lhs=sum(w(m)*f(m) for m in range(k,2*k+1))
        assert lhs==w(k)*T(k)+sum((w(m)-w(m-1))*T(m) for m in range(k+1,2*k+1)),("old-8-6",k,nu)
        # old-8-8 (nu<=k-1)
        if nu<=k-1:
            def vs(m,l): return s(m+1,l+1)-s(m,l)
            def DD(m): return (k+1)*s(m+1,k+1)-2*k*s(m,k)+(k-1)*s(m-1,k-1)
            for m in range(k+1,2*k+1):
                assert DD(m)==(k+1)*vs(m,k)-(k-1)*vs(m-1,k-1),("DDid",k,nu,m)
            def om(m): return F(2) if m<=N+1 else 2-F(m-N,k)
            Stays=2*vs(N+1,k)+sum((2-F(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(N+2,2*k+1))
            Bd=-(k+nu)*(vs(2*k,k)+c(2*k,k-1))-s(2*k,k-1)
            for m0 in range(k,N+1):
                rhs=2*k*c(m0,k)+2*s(m0,k+1)+2*s(m0,k)+(2*k+2)*vs(m0,k)-2*s(N+1,k+1)-s(N+2,k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-Stays
                if T(m0)!=rhs: bad+=1; print("old-8-8(가) FAIL",k,nu,m0,float(T(m0)-rhs))
            for m0 in range(N+1,2*k+1):
                mf=3*k+nu-m0
                rhs=mf*c(m0,k)+s(m0,k)+(s(m0,k+1)-s(m0+1,k+1))+(mf+1)*vs(m0,k)+Bd+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-sum((2-F(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(m0+1,2*k+1))
                if T(m0)!=rhs: bad+=1; print("old-8-8(나) FAIL",k,nu,m0,float(T(m0)-rhs))
            # T_{k+1}=T_k+2(k-1)c_k(k-1)
            assert T(k+1)==T(k)+2*(k-1)*c(k,k-1)
print("done, bad=",bad, "k up to",KMAX)
