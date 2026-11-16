# I3: 보조정리 green-connection (가)(다)(라)와 정리 source-rep (가)(나)(다)를 작은 n에서 전수 계산으로 대조
from fractions import Fraction as Fr
from math import comb
from itertools import permutations, product
import sympy as sp
def p(n): return (n+1)**(n-1) if n>=1 else 1
def Gamma(d,y,n):
    g=[sp.Integer(1)]
    for dd in range(1,d+1):
        s=comb(n,dd)*p(dd)+y*sum(comb(n-dd+j,j)*p(j)*g[dd-1-j] for j in range(dd))
        g.append(sp.expand(s))
    return g[d]
y=sp.symbols('y')
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)
    return h
def K(n,k):
    tot=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); t=1
        for hi in h:
            t*= hi if hi<=k else y
        tot+=t
    return sp.expand(tot)
def park(a):
    n=len(a); occ=[False]*n; pos=[0]*n
    for c,pref in enumerate(a):
        s=pref
        while s<n and occ[s]: s+=1
        if s>=n: return None
        occ[s]=True; pos[c]=s
    return pos
def stats(n):
    # returns b[l], B[m], E[k], E2[k]
    b=[0]*n; B=[0]*n; E=[0]*(n+1)
    for a in product(range(n),repeat=n):
        pos=park(a)
        if pos is None: continue
        disp=[pos[c]-a[c] for c in range(n)]
        M=max(disp); cnt=disp.count(M)
        b[M]+=1
        if cnt%2==0: E[M]+=1
        # blocked: all cars with disp M at position i with h_i = M+1
        sig=[0]*n
        for c in range(n): sig[pos[c]]=c+1
        h=caps(sig)
        if all(h[pos[c]]==M+1 for c in range(n) if disp[c]==M): B[M]+=1
    return b,B,E
for n in range(2,8):
    b,B,E=stats(n)
    Ks={k:K(n,k) for k in range(1,n+1)}
    for k in range(1,n+1):
        # 2-28 check
        if k<=n-1:
            d=b[k]-b[k-1]
            assert d==2*E[k]-B[k-1],(n,k)
        # green (다): K_{n,k}(y)-K_{n,k+1}(y) = (y-k-1) p_k Gamma_{n-k-1}(y;n), k+1<=n<=2k+1
        if k+1<=n<=2*k+1 and k+1<=n:
            lhs=sp.expand(Ks[k]-Ks[k+1]) if k+1<=n else None
            rhs=sp.expand((y-k-1)*p(k)*Gamma(n-k-1,y,n))
            assert sp.simplify(lhs-rhs)==0,(n,k,'다')
        # B_{n,l} = p_l Gamma_{n-l-1}(l;n), l+1<=n<=2l+1
        l=k
        if l+1<=n<=2*l+1 and l<=n-1:
            assert B[l]==p(l)*Gamma(n-l-1,l,n),(n,l,'B')
    # (라)
    def A(m,l):
        # cumulative count via b of row m — compute directly small
        if m==0: return 1
        bb,_,_=stats(m)
        return sum(bb[:l+1])
    for l in range(1,n):
        if l+1<=n<=2*l+1:
            s=sum(A(m,l)*Gamma(n-m-1,l,n) for m in range(l,n))
            assert s==b[l],(n,l,'라')
    # source-rep (가): K_{n,k}(y) = phi_n + y sum_{m=k}^{n-1} phi_m Gamma_{n-m-1}(y;n), n<=2k+1 ; phi_m = K_{m,k}(0)
    for k in range(1,n+1):
        if n<=2*k+1:
            phi=lambda m: (K(m,k).subs(y,0) if m>=1 else 1)
            rhs=sp.expand(phi(n)+y*sum(phi(m)*Gamma(n-m-1,y,n) for m in range(k,n)))
            assert sp.simplify(Ks[k]-rhs)==0,(n,k,'가')
            # (나): second difference at k equals 2E
            sdiff=Ks[k].subs(y,k+1)-2*Ks[k].subs(y,k)+Ks[k].subs(y,k-1)
            if k<=n-1: assert sdiff==2*E[k],(n,k,'나')
    print('n',n,'ok')
