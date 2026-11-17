# 검토전체25 R7a: (7.1)(7.2)(7.6)(7.10)과 흡수 귀납 주변 사실의 작은 크기 정확 검산
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial
import sys
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        z=0
        for j in range(i-1,-1,-1):
            if s[j]>s[i]: z=j+1;break
        h.append(i+1-z)
    return h
def A_table(N,l):
    # A_{n,l} by last-car recursion
    A=[1]
    for n in range(1,N+1):
        A.append(sum(comb(n-1,j-1)*min(j,l+1)*A[j-1]*A[n-j] for j in range(1,n+1)))
    return A
ok=True
# (7.2) brute force
for k in (2,3):
    Ak=A_table(8,k-1)
    Zb={0:F(0)};ZH={0:F(0)};Z2={0:F(0)}
    brute={}
    for n in range(1,8):
        tot=0;sz=0;sh=0;s2=0
        for s in permutations(range(1,n+1)):
            h=caps(s); w=1
            for x in h: w*=min(x,k)
            Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
            tot+=w;sz+=w*Z;sh+=w*H;s2+=w*Z*(Z-1)
        assert tot==Ak[n]
        brute[n]=(F(sz,tot),F(sh,tot),F(s2,tot))
        P=lambda j: F(min(j,k)*comb(n-1,j-1)*Ak[j-1]*Ak[n-j],Ak[n])
        assert sum(P(j) for j in range(1,n+1))==1
        zb=sum(P(j)*((1 if j>k else 0)+Zb[j-1]+Zb[n-j]) for j in range(1,n+1))
        zh=sum(P(j)*((1 if j==k else 0)+ZH[j-1]+ZH[n-j]) for j in range(1,n+1))
        z2=sum(P(j)*(Z2[j-1]+Z2[n-j]+2*Zb[j-1]*Zb[n-j]+2*(1 if j>k else 0)*(Zb[j-1]+Zb[n-j])) for j in range(1,n+1))
        Zb[n]=zb;ZH[n]=zh;Z2[n]=z2
        if (zb,zh,z2)!=brute[n]: ok=False;print('7.2 mismatch',k,n)
print('(7.2) brute n<=7, k=2,3:',ok)
# (7.10)
ok=True
for k in range(2,9):
    N=5*k+3
    Am=A_table(N,k-1);Ap=A_table(N,k);Amm=A_table(N,k-2)
    clp=[F(Ap[m]-Am[m],Am[m]) for m in range(N+1)]
    clm=[F(Am[m]-Amm[m],Am[m]) for m in range(N+1)]
    mu=[clp[m]-clm[m] for m in range(N+1)]
    for m in range(1,N+1):
        P=lambda j: F(min(j,k)*comb(m-1,j-1)*Am[j-1]*Am[m-j],Am[m])
        def chi(j):
            hv=1 if j>k else 0
            v=F(1,k)*(-(1 if j==k else 0)*(1-clm[m-k] if m>=k else 0)+hv*(clp[j-1]+clm[j-1]+clp[m-j]+clm[m-j]))
            v+=(1+F(hv,k))*clp[j-1]*clp[m-j]+(1-F(hv,k))*clm[j-1]*clm[m-j]
            return v
        src=sum(P(j)*chi(j) for j in range(1,m+1))
        rhs=src+sum(P(j)*(mu[j-1]+mu[m-j]) for j in range(1,m+1))
        if rhs!=mu[m]: ok=False;print('7.10 mismatch',k,m)
        if m<=k-1 and (mu[m]!=0 or src!=0): ok=False;print('small m',k,m)
    # mu_k(k) = -p_{k-1}/p_k
    pk=lambda n:(n+1)**(n-1)
    if mu[k]!=-F(pk(k-1),pk(k)): ok=False;print('mu_k',k)
print('(7.10), mu_k(k)=-p_{k-1}/p_k, k=2..8, m<=5k+3:',ok)
# (7.6): K_{n,k}(z) polynomial via weighted recursion, pd_t, derivative values vs moments
def polymul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]+=x*y
    return r
def polyadd(a,b):
    n=max(len(a),len(b));return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(n)]
ok=True
for k in (2,3,4):
    N=3*k+3
    K=[[1]]
    for n in range(1,N+1):
        acc=[0]
        for j in range(1,n+1):
            w=[j] if j<=k else [0,1]
            term=polymul(polymul(w,K[j-1]),K[n-j])
            acc=polyadd(acc,[comb(n-1,j-1)*c for c in term])
        K.append(acc)
    ev=lambda p,z:sum(c*z**i for i,c in enumerate(p))
    d1=lambda p:[i*c for i,c in enumerate(p)][1:] or [0]
    Am=A_table(N,k-1);Ap=A_table(N,k)
    # moments via (7.2)
    Zb=[F(0)];Z2=[F(0)]
    for n in range(1,N+1):
        P=lambda j: F(min(j,k)*comb(n-1,j-1)*Am[j-1]*Am[n-j],Am[n])
        Zb.append(sum(P(j)*((1 if j>k else 0)+Zb[j-1]+Zb[n-j]) for j in range(1,n+1)))
        Z2.append(sum(P(j)*(Z2[j-1]+Z2[n-j]+2*Zb[j-1]*Zb[n-j]+2*(1 if j>k else 0)*(Zb[j-1]+Zb[n-j])) for j in range(1,n+1)))
    for n in range(N+1):
        if ev(K[n],k)!=Am[n] or ev(K[n],k+1)!=Ap[n]: ok=False;print('K special',k,n)
    pd={};pd1={};pd2={};ex={}
    for t in range(k+1,N+1):
        p=polyadd(polymul([0,1],K[t-1]),[-t**(t-1)])
        pd[t]=ev(p,k);pd1[t]=ev(d1(p),k);pd2[t]=ev(d1(d1(p)),k)
        A=Am[t-1]
        ex[t]=F(t*t**(t-2),A)-k
        if pd[t]!=-A*ex[t] or pd1[t]!=A*(1+Zb[t-1]) or F(pd2[t])!=F(A,k)*(2*Zb[t-1]+Z2[t-1]): ok=False;print('pd values',k,t)
        q=t-k
        # heavy-block: ex>=q, moments bounds
        if not(ex[t]>=q and 0<=Zb[t-1]<=q-1 and 0<=Z2[t-1]<=(q-1)*(q-2)): ok=False;print('heavy-block',k,t)
    for t in range(k+1,N+1):
        for t2 in range(k+1,N+1):
            for j in range(0,4):
                ps=F(j*(j-1),2*k*k)*pd[t]*pd[t2]+F(j,k)*(pd[t]*pd1[t2]+pd1[t]*pd[t2])+pd1[t]*pd1[t2]+F(1,2)*(pd[t]*pd2[t2]+pd2[t]*pd[t2])
                lhs=ps/(Am[t-1]*Am[t2-1])
                a,b=Zb[t-1],Zb[t2-1]
                rhs=(1+a)*(1+b)+F(j*(j-1),2*k*k)*ex[t]*ex[t2]-F(j,k)*(ex[t]*(1+b)+ex[t2]*(1+a))-F(1,2*k)*(ex[t]*(2*b+Z2[t2-1])+ex[t2]*(2*a+Z2[t-1]))
                if lhs!=rhs: ok=False;print('7.6',k,t,t2,j)
                q,q2=t-k,t2-k
                low=1-F(j,k)*(ex[t]+ex[t2])-(ex[t]*(q2-1)+ex[t2]*(q-1))/(2*k)
                if lhs/((1+a)*(1+b))<low: ok=False;print('7.8',k,t,t2,j)
print('(7.6) values, heavy-block, (7.8) with exact ex, k=2,3,4:',ok)
