# T1: 2.7절 동률-막힘 항등식, 따름정리 2-29, 보조정리 2-30, J-egf 재귀를 n<=8 전수로 검산
from itertools import permutations, product
from math import comb, factorial
from fractions import Fraction as Fr
def hcap(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=max([j for j in range(1,i) if sig[j-1]>sig[i-1]]+[0]); h.append(i-z)
    return h
def p(n): return (n+1)**(n-1) if n>0 else 1
def stats(n):
    # 전수: 섬유별 변위 벡터
    perms=list(permutations(range(1,n+1)))
    H={s:hcap(s) for s in perms}
    out={}
    for k in range(1,n+1):
        b_k=b_km1=E=E2=B=0
        for s in perms:
            h=H[s]
            for d in product(*[range(x) for x in h]):
                M=max(d); cnt=d.count(M)
                if M==k:
                    b_k+=1
                    if cnt%2==0: E+=1
                    if cnt==2: E2+=1
                if M==k-1:
                    b_km1+=1
                    if all(h[i]==k for i in range(n) if d[i]==M): B+=1
        # J_n(k-1), 보조정리 2-30 첫 식
        J=0; Bform=0
        for s in perms:
            h=H[s]; Hk=sum(1 for x in h if x==k); Zk=sum(1 for x in h if x>k)
            pr=1
            for x in h:
                if x<k: pr*=x
            J+= Hk*k**(Hk-1)*(k-1)**Zk*pr if Hk>0 else 0
            Bform+= pr*(k-1)**Zk*(k**Hk-(k-1)**Hk)
        Xi = comb(2*k-1,k-1)*p(k-1)**2 if n==2*k else 0
        out[k]=dict(d=b_k-b_km1, two_E_minus_B=2*E-B, ineq=(2*E2-B<=b_k-b_km1), B=B, Bform=Bform, J=J, BleJ=(B<=J), Hle1_eq=(B==J) if n<=2*k-1 else None, center=(B==J-Xi) if n in (2*k-1,2*k) else None)
    return out
for n in range(1,8):
    o=stats(n)
    bad=[(k,v) for k,v in o.items() if v['d']!=v['two_E_minus_B'] or not v['ineq'] or v['B']!=v['Bform'] or not v['BleJ'] or v['Hle1_eq'] is False or v['center'] is False]
    print("n=",n,"문제:",bad)
# J-egf (가) 재귀 검산: J_n(z)를 z 다항식(계수 리스트)으로
def Jpoly(n,k):
    # returns dict power->coef
    from collections import defaultdict
    D=defaultdict(int)
    for s in permutations(range(1,n+1)):
        h=hcap(s); Hk=sum(1 for x in h if x==k); Zk=sum(1 for x in h if x>k)
        pr=1
        for x in h:
            if x<k: pr*=x
        if Hk>0: D[Zk]+= Hk*k**(Hk-1)*pr
    return dict(D)
def padd(a,b):
    r=dict(a)
    for e,c in b.items(): r[e]=r.get(e,0)+c
    return {e:c for e,c in r.items() if c!=0}
def pscale(a,c): return {e:c*v for e,v in a.items()}
def pmulz(a): return {e+1:v for e,v in a.items()}
for k in (2,3):
    for n in range(0,2*k):
        if n+1>8: break
        lhs=Jpoly(n+1,k)
        rhs={}
        for i in range(0,n+1):
            Jn=Jpoly(n-i,k)
            term=padd(pmulz(Jn), pscale(Jn,i+1))
            rhs=padd(rhs, pscale(term, comb(n,i)*p(i)))
        if n>=k-1: rhs=padd(rhs,{0:comb(n,k-1)*p(k-1)*p(n-k+1)})
        print("k",k,"n",n,"J_{n+1}",lhs,"재귀",rhs, lhs==rhs)
