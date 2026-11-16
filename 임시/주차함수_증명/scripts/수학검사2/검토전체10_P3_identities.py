# P3: green-connection / source-rep 항등식의 소규모 전수 검산 (n<=7)
import itertools, math
from fractions import Fraction as F
import sympy as sp

def park(pref):
    n=len(pref); spot=[0]*n; occ=[False]*n
    for i,a in enumerate(pref):
        j=a-1
        while j<n and occ[j]: j+=1
        if j>=n: return None
        occ[j]=True; spot[i]=j
    return spot
def data(n):
    # returns dict: list of (maxdisp, outcome permutation capacities multiset)
    pfs=[]
    for pref in itertools.product(range(1,n+1),repeat=n):
        s=park(pref)
        if s is None: continue
        M=max(s[i]-(pref[i]-1) for i in range(n))
        pfs.append(M)
    return pfs
def caps(n):
    # outcome permutations sigma: car at spot j; capacity h_j = number of possible displacements = j+1 - (position of ... ) 
    # capacity of spot j for outcome sigma: largest d such that car there could have preferred j-d.. : h_j = number of consecutive occupied spots ending at j... 
    # Use known: fiber size = prod h_j with h_j = j+1 - (start of block)?? Here: car parked at spot j must have preferred spot in (previous spot where a later-arriving... ) -- compute directly by brute force: for each sigma, count preferences producing it.
    res={}
    for pref in itertools.product(range(1,n+1),repeat=n):
        s=park(pref)
        if s is None: continue
        sig=tuple(s)
        res.setdefault(sig,[]).append(pref)
    out=[]
    for sig,L in res.items():
        # h_i for spot i: number of distinct preferences of the car at spot i among fiber
        h=[len(set(p[sig.index(i)] for p in L)) for i in range(n)]
        assert math.prod(h)==len(L)
        out.append(h)
    return out
def A(n,l,pfs): return sum(1 for M in pfs if M<=l) if l>=0 else 0
def Gamma(d,y,n):
    g=[sp.Integer(1)]
    p=lambda j: (j+1)**(j-1) if j>0 else 1
    for dd in range(1,d+1):
        v=sp.binomial(n,dd)*p(dd)+y*sum(sp.binomial(n-dd+j,j)*p(j)*g[dd-1-j] for j in range(dd))
        g.append(sp.expand(v))
    return g[d]
y=sp.Symbol('y')
pp=lambda j: (j+1)**(j-1) if j>0 else 1
ok=True
for n in range(1,8):
    pfs=data(n); H=caps(n)
    def K(k): return sp.expand(sum(sp.prod([h if h<=k else y for h in hs]) for hs in H))
    def phi(m,k):
        # forests on m vertices with all trees size<=k = K_{m,k}(0)
        if m==0: return 1
        Hm=caps(m)
        return sum(1 for hs in Hm if all(h<=k for h in hs)) if False else sum(sp.prod([h if h<=k else 0 for h in hs]) for hs in Hm)
    for k in range(1,n+1):
        # (다) K_{n,k}-K_{n,k+1} = (y-k-1) p_k Gamma_{n-k-1} for k+1<=n<=2k+1
        if k+1<=n<=2*k+1:
            lhs=sp.expand(K(k)-K(k+1)); rhs=sp.expand((y-k-1)*pp(k)*Gamma(n-k-1,y,n))
            if lhs!=rhs: ok=False; print("(다) fail",n,k,lhs,rhs)
        # source-rep (가): K_{n,k}(y)=phi_n+y sum_{m=k}^{n-1} phi_m Gamma_{n-m-1}, n<=2k+1
        if n<=2*k+1:
            rhs=phi(n,k)+y*sum(phi(m,k)*Gamma(n-m-1,y,n) for m in range(k,n))
            if sp.expand(K(k)-rhs)!=0: ok=False; print("source(가) fail",n,k)
        # 2-4: K_{n,k}(k+1)=A_{n,k}, K(k)=A_{n,k-1}
        if K(k).subs(y,k+1)!=A(n,k,pfs) or K(k).subs(y,k)!=A(n,k-1,pfs): ok=False; print("2-4 fail",n,k)
    # (라): b_{n,l} = sum_{m=l}^{n-1} A_{m,l} Gamma_{n-m-1}(l;n), l+1<=n<=2l+1
    for l in range(1,n):
        if l+1<=n<=2*l+1:
            b=A(n,l,pfs)-A(n,l-1,pfs)
            rhs=sum(A(m,l,data(m))*Gamma(n-m-1,l,n) for m in range(l,n))
            if b!=rhs: ok=False; print("(라) fail",n,l,b,rhs)
print("all ok" if ok else "FAIL")
