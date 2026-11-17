# R11 검산: D.central-gap-integer의 네 재귀를 정의에서 직접 계산한 값과 대조 (작은 k)
from fractions import Fraction as F
from math import comb, factorial
from itertools import permutations
import sys

def p(n): return (n+1)**(n-1) if n>=1 else 1

# two-variable polynomial K_{n,k}(eta,y) as dict {(a,b):coef}
def padd(P,Q,c=1):
    R=dict(P)
    for m,v in Q.items(): R[m]=R.get(m,0)+c*v
    return R
def pmul(P,Q):
    R={}
    for (a,b),v in P.items():
        for (c,d),w in Q.items():
            R[(a+c,b+d)]=R.get((a+c,b+d),0)+v*w
    return R
def Kpoly(N,k):
    K=[{(0,0):1}]
    for n in range(1,N+1):
        S={}
        for j in range(n):
            t=j+1
            wg={(0,0):t} if t<k else ({(1,0):1} if t==k else {(0,1):1})
            term=pmul(pmul(wg,K[j]),K[n-1-j])
            S=padd(S,term,comb(n-1,j))
        K.append(S)
    return K
def ev(P,eta,y,de=0,dy=0):
    s=0
    for (a,b),v in P.items():
        ca=1
        for i in range(de): ca*= (a-i)
        cb=1
        for i in range(dy): cb*= (b-i)
        if ca==0 or cb==0: continue
        s+= v*ca*cb*F(eta)**(a-de)*F(y)**(b-dy)
    return s

# brute force check of K poly against definition via capacities h_i (small n)
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)
    return h
def brute(n,k):
    P={}
    for sig in permutations(range(1,n+1)):
        h=caps(sig); c=1; a=b=0
        for x in h:
            if x<k: c*=x
            elif x==k: a+=1
            else: b+=1
        P[(a,b)]=P.get((a,b),0)+c
    return P
for k in (1,2,3):
    K=Kpoly(7,k)
    for n in range(1,8):
        B=brute(n,k)
        assert {m:v for m,v in K[n].items() if v}=={m:v for m,v in B.items() if v},(n,k)
print("weighted last-car recursion == brute-force definition for k<=3, n<=7")

S=2918732888; s=F(S,2**30)
ok=True; minratio=None
for k in range(2,13):
    N=2*k
    K=Kpoly(N,k)
    A=[ev(K[n],k,k) for n in range(N+1)]
    D=[ev(K[n],k,k,dy=1) for n in range(N+1)]
    E=[ev(K[n],k,k,dy=2) for n in range(N+1)]
    J=[ev(K[n],k,k-1,de=1) for n in range(N+1)]
    nrm=lambda v,n: F(v)/(factorial(n)*s**n)
    r=[nrm(p(i),i) for i in range(N+2)]
    fA=[nrm(A[n],n) for n in range(N+1)]; fD=[nrm(D[n],n) for n in range(N+1)]
    fE=[nrm(E[n],n) for n in range(N+1)]; fJ=[nrm(J[n],n) for n in range(N+1)]
    # initial values
    for i in range(k+1):
        assert fA[i]==r[i] and fD[i]==0 and fE[i]==0
    for i in range(k): assert fJ[i]==0
    assert fJ[k]==r[k-1]/(s*k)
    for n in range(k+1,2*k+1):
        rr=n-k
        a=(sum((k+i+1)*r[i]*fA[n-1-i] for i in range(0,rr-1))+sum(min(i+1,k)*r[i]*r[n-1-i] for i in range(rr-1,k+1)))/(s*n)
        d=(sum((k+i+1)*r[i]*fD[n-1-i] for i in range(0,rr-1))+sum(r[i]*fA[n-1-i] for i in range(0,rr)))/(s*n)
        z=(sum((k+i+1)*r[i]*fE[n-1-i] for i in range(0,rr-1))+2*sum(r[i]*fD[n-1-i] for i in range(0,rr-1)))/(s*n)
        j=(sum((k+i)*r[i]*fJ[n-1-i] for i in range(0,rr))+r[k-1]*r[n-k])/(s*n)
        if not (a==fA[n] and d==fD[n] and z==fE[n] and j==fJ[n]):
            ok=False; print("MISMATCH",k,n,a==fA[n],d==fD[n],z==fE[n],j==fJ[n])
    for n in (2*k-1,2*k):
        if n>=3:
            print(k,n,"e_n/J_n(k-1)=%.7f"%float(F(E[n])/F(J[n])), "e>J:",E[n]>J[n])
print("four recursions exact for k=2..12, k<n<=2k:",ok)
