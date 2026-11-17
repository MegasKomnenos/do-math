# -*- coding: utf-8 -*-
"""D.central-gap-integer의 네 재귀를 정의(가중 분배 재귀의 두 변수 다항식)에서 직접 검산한다."""
from math import comb, factorial
from fractions import Fraction
import sys
def p(n): return (n+1)**(n-1) if n>=1 else 1
# polynomial in (eta,y) as dict {(a,b):coef}
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
def K_polys(k,N):
    K=[{(0,0):1}]
    for n in range(1,N+1):
        S={}
        for j in range(n):
            t=j+1
            wg={(0,0):t} if t<k else ({(1,0):1} if t==k else {(0,1):1})
            term=pmul(wg,pmul(K[j],K[n-1-j]))
            S=padd(S,term,comb(n-1,j))
        K.append(S)
    return K
def ev(P,eta,y,de=0,dy=0):
    s=0
    for (a,b),v in P.items():
        if a<de or b<dy: continue
        ca=1
        for i in range(de): ca*= (a-i)
        cb=1
        for i in range(dy): cb*= (b-i)
        s+=v*ca*cb*eta**(a-de)*y**(b-dy)
    return s
ok=True
for k in range(2,8):
    N=2*k
    K=K_polys(k,N)
    A=[ev(K[n],k,k) for n in range(N+1)]
    D=[ev(K[n],k,k,0,1) for n in range(N+1)]
    E=[ev(K[n],k,k,0,2) for n in range(N+1)]
    J=[ev(K[n],k,k-1,1,0) for n in range(N+1)]
    # init
    assert all(A[i]==p(i) for i in range(k+1))
    assert all(D[i]==0 and E[i]==0 for i in range(k+1))
    assert all(J[i]==0 for i in range(k)) and J[k]==p(k-1)
    for n in range(k+1,2*k+1):
        r=n-k
        a=sum(comb(n-1,i)*(k+i+1)*p(i)*A[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*min(i+1,k)*p(i)*p(n-1-i) for i in range(r-1,k+1))
        d=sum(comb(n-1,i)*(k+i+1)*p(i)*D[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*p(i)*A[n-1-i] for i in range(0,r))
        e=sum(comb(n-1,i)*(k+i+1)*p(i)*E[n-1-i] for i in range(0,r-1))+2*sum(comb(n-1,i)*p(i)*D[n-1-i] for i in range(0,r-1))
        j=sum(comb(n-1,i)*(k+i)*p(i)*J[n-1-i] for i in range(0,r))+comb(n-1,k-1)*p(k-1)*p(n-k)
        if (a,d,e,j)!=(A[n],D[n],E[n],J[n]):
            ok=False; print("MISMATCH",k,n,(a==A[n],d==D[n],e==E[n],j==J[n]))
print("four recursions match definitions for k=2..7, k<n<=2k:", ok)
# 넷째 재귀의 일반 y 꼴
for k in range(2,6):
    N=2*k; K=K_polys(k,N)
    for y in (k-1,k,3):
        J=[ev(K[n],k,y,1,0) for n in range(N+1)]
        for n in range(1,N+1):
            rhs=sum(comb(n-1,i)*(y+i+1)*p(i)*J[n-1-i] for i in range(n))+(comb(n-1,k-1)*p(k-1)*p(n-k) if n>=k else 0)
            assert rhs==J[n],(k,y,n)
print("J_n(y) recursion ok (n<=2k)")
