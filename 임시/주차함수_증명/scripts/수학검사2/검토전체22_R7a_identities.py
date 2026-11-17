# 검토전체22 R7a: 7.4·7.5절 항등식의 정확 산술 대조 (python -I)
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial
import sympy as sp

def p(n): return (n+1)**(n-1) if n>=1 else 1

def Acol(l, N):
    # A_{n,l}, n=0..N  (정리 2:old-2-6)
    A=[1]
    for n in range(1,N+1):
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A

def caps(s):
    n=len(s); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and s[j]<s[i]: j-=1
        h.append(i-j)   # i,j 0-기준: 자리 i+1, 가장 가까운 큰 자리 j+1 (없으면 0)
    return h

def moments_bruteforce(n,k):
    # Pr^sigma_{n,k} 아래 E[Z], E[H], E[Z(Z-1)]
    tot=0; sZ=0; sH=0; sZZ=0
    for s in permutations(range(1,n+1)):
        h=caps(s); w=1
        for x in h: w*=min(x,k)
        Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        tot+=w; sZ+=w*Z; sH+=w*H; sZZ+=w*Z*(Z-1)
    return tot, F(sZ,tot), F(sH,tot), F(sZZ,tot)

def moments_recursion(k,N):
    A=Acol(k-1,N)
    a=[F(A[n],factorial(n)) for n in range(N+1)]
    Zf=[F(0)]; ZH=[F(0)]; ZZ=[F(0)]
    for n in range(1,N+1):
        P=[None]+[min(pp,k)*a[pp-1]*a[n-pp]/(n*a[n]) for pp in range(1,n+1)]
        assert sum(P[1:])==1
        zf=sum(P[pp]*((1 if pp>k else 0)+Zf[pp-1]+Zf[n-pp]) for pp in range(1,n+1))
        zh=sum(P[pp]*((1 if pp==k else 0)+ZH[pp-1]+ZH[n-pp]) for pp in range(1,n+1))
        zz=sum(P[pp]*(ZZ[pp-1]+ZZ[n-pp]+2*Zf[pp-1]*Zf[n-pp]+2*(1 if pp>k else 0)*(Zf[pp-1]+Zf[n-pp])) for pp in range(1,n+1))
        Zf.append(zf); ZH.append(zh); ZZ.append(zz)
    return A,Zf,ZH,ZZ

print("== (7.1)(7.2) 모멘트 재귀 대 전수 ==")
for k in [2,3,4]:
    N=8
    A,Zf,ZH,ZZ=moments_recursion(k,N)
    for n in range(1,N+1):
        tot,eZ,eH,eZZ=moments_bruteforce(n,k)
        assert tot==A[n] and eZ==Zf[n] and eH==ZH[n] and eZZ==ZZ[n],(k,n)
    # 시작값
    assert all(Zf[j]==0 for j in range(0,k+1)) and all(ZH[j]==0 for j in range(0,k)) and all(ZZ[j]==0 for j in range(0,k+2))
    assert Zf[k+1]!=0 and ZH[k]!=0 and ZZ[k+2]!=0
print("ok")

print("== (7.10) 한 걸음 항등식 ==")
for k in [2,3,4,5,7]:
    N=4*k+3
    Am=Acol(k-2,N); A0=Acol(k-1,N); Ap=Acol(k,N)
    clp=[F(Ap[m]-A0[m],A0[m]) for m in range(N+1)]
    clm=[F(A0[m]-Am[m],A0[m]) for m in range(N+1)]
    mu=[clp[m]-clm[m] for m in range(N+1)]
    assert all(clp[m]==0 and clm[m]==0 for m in range(0,k)) and clp[k]==0
    assert mu[k]==-F(p(k-1),p(k)), (k, mu[k])
    for m in range(1,N+1):
        P=[None]+[F(min(j,k)*comb(m-1,j-1)*A0[j-1]*A0[m-j],A0[m]) for j in range(1,m+1)]
        assert sum(P[1:])==1
        def chi(j):
            hv=1 if j>k else 0
            v=F(0)
            if j==k: v-=F(1,k)*(1-clm[m-k])
            if j>k: v+=F(1,k)*(clp[j-1]+clm[j-1]+clp[m-j]+clm[m-j])
            v+=(1+F(hv,k))*clp[j-1]*clp[m-j]+(1-F(hv,k))*clm[j-1]*clm[m-j]
            return v
        src=sum(P[j]*chi(j) for j in range(1,m+1))
        rhs=src+sum(P[j]*(mu[j-1]+mu[m-j]) for j in range(1,m+1))
        assert rhs==mu[m],(k,m)
        if m<=k-1: assert src==0 and mu[m]==0
print("ok")

print("== 2.7/7.4 급수 항등식 (k=2,3) ==")
z,x=sp.symbols('z x')
def trunc(e,N):
    e=sp.expand(e)
    return sum(e.coeff(x,i)*x**i for i in range(N+1))
def ser_exp(f,N):
    # f(0)=0
    r=sp.Integer(1); term=sp.Integer(1)
    for i in range(1,N+1):
        term=trunc(term*f/i,N); r+=term
    return trunc(r,N)
def integ(f): return sp.integrate(sp.expand(f),x)
for k in [2,3]:
    N=3*k+2
    # K_{n,k}(z) : wg_t=t (t<=k), z (t>k)
    Kp=[sp.Integer(1)]
    for n in range(1,N+1):
        Kp.append(sp.expand(sum(comb(n-1,j)*((j+1) if j+1<=k else z)*Kp[j]*Kp[n-1-j] for j in range(n))))
    A0=Acol(k-1,N); Ap=Acol(k,N); Am=Acol(k-2,N)
    for n in range(N+1):
        assert Kp[n].subs(z,k)==A0[n] and Kp[n].subs(z,k+1)==Ap[n]
    Kser=sum(Kp[n]*x**n/factorial(n) for n in range(N+1))
    T=sum(sp.Integer(t)**(t-1)*x**t/factorial(t) for t in range(1,N+1))
    Tle=sum(sp.Integer(t)**(t-1)*x**t/factorial(t) for t in range(1,k+1)); Tgt=T-Tle
    eT=ser_exp(T,N)
    for n in range(N+1): assert eT.coeff(x,n)*factorial(n)==p(n)
    Elt=sum(sp.Integer(p(m))*x**m/factorial(m) for m in range(k))
    Gr=trunc(T-T**2/2,N)
    sm=trunc((1-T)*(eT-Elt),N)
    ezG=ser_exp(z*Gr,N); emzG=ser_exp(-z*Gr,N)
    Gst=trunc(Elt+sm+z*eT*ezG*integ(trunc(sm*emzG,N)),N)
    X=sp.expand(Kser-Gst)
    low=[n for n in range(N+1) if sp.simplify(X.coeff(x,n))!=0]
    print("k=%d: 잔차의 최저 차수 = %s (2k+2=%d)"%(k,low[0] if low else None,2*k+2))
    assert low and low[0]==2*k+2
    pd=trunc(z*integ(trunc(Kser-Elt,N))-Tgt,N)
    assert all(sp.expand(pd.coeff(x,t)*factorial(t)-(z*Kp[t-1]-sp.Integer(t)**(t-1)))==0 for t in range(k+1,N+1)) and all(pd.coeff(x,t)==0 for t in range(k+1))
    # (7.3)
    assert sp.expand(trunc(ser_exp(trunc(Tle+z*integ(trunc(Kser-Elt,N)),N),N)-Kser,N))==0
    # (7.4)
    eTle=ser_exp(Tle,N)
    rhs=trunc(eTle*(z*integ(X)+pd**2/2),N)
    assert sp.expand(trunc(X-rhs,N))==0
    # (7.5): d_{n,k} >= K''(k) - JG_n(k-1) ; J_n<=JG_n ; 등호 n<=2k
    JGser=trunc(p(k-1)*eT*ezG*integ(trunc(emzG*x**(k-1)/factorial(k-1),N)),N)
    # J_n(z) 전수
    for n in range(1,min(N,8)+1):
        Jn=0
        for s in permutations(range(1,n+1)):
            h=caps(s); H=sum(1 for v in h if v==k); Z=sum(1 for v in h if v>k)
            if H==0: continue
            w=1
            for v in h:
                if v<k: w*=v
            Jn+=H*k**(H-1)*z**Z*w
        JG=sp.expand(JGser.coeff(x,n)*factorial(n))
        for zz in range(0,k+2):
            assert sp.expand(Jn).subs(z,zz) <= JG.subs(z,zz),(k,n,zz)
        if n<=2*k: assert sp.expand(Jn-JG)==0,(k,n)
        else: assert sp.expand(Jn-JG)!=0
    for n in range(1,N+1):
        d=Ap[n]-2*A0[n]+Am[n]
        K2=sp.diff(Kp[n],z,2).subs(z,k)
        JGv=(JGser.coeff(x,n)*factorial(n)).subs(z,k-1)
        POS=(sp.diff(Gst.coeff(x,n),z,2)*factorial(n)).subs(z,k)
        X2=(sp.diff(X.coeff(x,n),z,2)*factorial(n)).subs(z,k)
        assert d>=K2-JGv,(k,n)
        assert K2==POS+X2
        if n<=2*k+1: assert X2==0
    # pair-terms: X''(k) = sum_j k^j Neu^j[e^{T<=k} Q_j]
    _,Zf,ZH,ZZ=moments_recursion(k,N)
    pdk=lambda t:(z*Kp[t-1]-sp.Integer(t)**(t-1))
    for t in range(k+1,N+1):
        ex=F(t*p(t-1),A0[t-1])-k
        assert pdk(t).subs(z,k)==-A0[t-1]*ex
        assert sp.diff(pdk(t),z).subs(z,k)==A0[t-1]*(1+Zf[t-1])
        assert sp.diff(pdk(t),z,2).subs(z,k)==F(A0[t-1],k)*(2*Zf[t-1]+ZZ[t-1])
    def ps(j,t,tp):
        ex=lambda u:F(u*p(u-1),A0[u-1])-k
        a=(1+Zf[t-1])*(1+Zf[tp-1])+F(j*(j-1),2*k*k)*ex(t)*ex(tp)-F(j,k)*(ex(t)*(1+Zf[tp-1])+ex(tp)*(1+Zf[t-1]))-F(1,2*k)*(ex(t)*(2*Zf[tp-1]+ZZ[tp-1])+ex(tp)*(2*Zf[t-1]+ZZ[t-1]))
        return a*A0[t-1]*A0[tp-1]
    tot=sp.Integer(0)
    for j in range(0,N+1):
        Q=sum(sum(comb(m,t)*ps(j,t,m-t) for t in range(k+1,m-k))*x**m/factorial(m) for m in range(2*k+2,N+1))
        if Q==0: continue
        f=trunc(eTle*Q,N)
        for _ in range(j): f=trunc(eTle*integ(f),N)
        tot+=sp.Integer(k)**j*f
    for n in range(N+1):
        X2=(sp.diff(X.coeff(x,n),z,2)).subs(z,k)
        assert sp.nsimplify(tot.coeff(x,n))==X2,(k,n,tot.coeff(x,n),X2)
    print("k=%d: (7.3)(7.4)(7.5)(7.6)·Green 원자·pd 값 모두 일치 (n<=%d)"%(k,N))
print("ok")
