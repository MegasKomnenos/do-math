# R3 check 1: 5.2.1 identities by brute force (small n), exact arithmetic.
import itertools, sys
from fractions import Fraction as Fr
from math import comb, factorial

def p(n): return 1 if n==0 else (n+1)**(n-1)

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j if j>=0 else i+1)
    return h

def polymul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]+=x*y
    return r
def polyadd(a,b):
    m=max(len(a),len(b)); return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(m)]
def peval(a,y): return sum(c*y**i for i,c in enumerate(a))

def Kpoly(n,k):
    # coefficients in y
    res=[0]*(n+1)
    for s in itertools.permutations(range(n)):
        h=caps(s); w=1; z=0
        for x in h:
            if x<=k: w*=x
            else: z+=1
        res[z]+=w
    return res
def A(n,l):
    if l<0: return 0
    tot=0
    for s in itertools.permutations(range(n)):
        w=1
        for x in caps(s): w*=min(x,l+1)
        tot+=w
    return tot

def Gam(d,n):
    # list of polys Gamma_0..Gamma_d in y
    G=[[1]]
    for dd in range(1,d+1):
        acc=[0]
        for j in range(dd):
            acc=polyadd(acc,[comb(n-dd+j,j)*p(j)*c for c in G[dd-1-j]])
        G.append(polyadd([comb(n,dd)*p(dd)],[0]+acc))
    return G

def phi(m,k):
    # forests on [m] with all trees of size<=k : m![x^m] exp(sum_{j<=k} j^{j-1}x^j/j!)
    # via recursion f_m = sum_{j=1}^{min(k,m)} C(m-1,j-1) j^{j-1} f_{m-j}
    f=[1]
    for mm in range(1,m+1):
        f.append(sum(comb(mm-1,j-1)*j**(j-1)*f[mm-j] for j in range(1,min(k,mm)+1)))
    return f[m]

# direct enumeration of parking functions: displacement stats
def pf_stats(n):
    # returns dict: for each PF: (M, count of cars achieving M, blocked?) aggregated
    from collections import Counter
    b=Counter(); E=Counter(); B=Counter()
    for a in itertools.product(range(1,n+1),repeat=n):
        occ=[0]*(n+2); ok=True; disp=[0]*n; pos=[0]*n
        for i,x in enumerate(a):
            s=x
            while s<=n and occ[s]: s+=1
            if s>n: ok=False;break
            occ[s]=i+1; disp[i]=s-x; pos[i]=s
        if not ok: continue
        M=max(disp); cnt=disp.count(M)
        sigma=[occ[s] for s in range(1,n+1)]
        h=caps(sigma)
        blocked=all(h[pos[i]-1]==M+1 for i in range(n) if disp[i]==M)
        b[M]+=1
        if cnt%2==0: E[M]+=1
        if blocked: B[M]+=1
    return b,E,B

ok=True
for n in range(1,8):
    Acache={l:A(n,l) for l in range(-1,n+2)}
    if n<=6:
        b,E,B=pf_stats(n)
    for k in range(1,n+1):
        K=Kpoly(n,k)
        # corollary 2.4 specializations
        assert peval(K,k)==Acache[k-1] and peval(K,k+1)==Acache[k]
        G=Gam(n-1,n)
        # (ga) source-rep: n<=2k+1
        if n<=2*k+1:
            rhs=[phi(n,k)]
            for m in range(k,n):
                rhs=polyadd(rhs,[0]+[phi(m,k)*c for c in G[n-m-1]])
            L=K+[0]*(len(rhs)-len(K)); R=rhs+[0]*(len(K)-len(rhs))
            if L!=R: ok=False; print("source-rep(ga) FAIL",n,k)
        # green-connection (da): k+1<=n<=2k+1
        if k+1<=n<=2*k+1:
            K1=Kpoly(n,k+1)
            diff=polyadd(K,[-c for c in K1])
            rhs=polymul([-(k+1),1],[p(k)*c for c in G[n-k-1]])
            m=max(len(diff),len(rhs)); 
            if [ (diff[i] if i<len(diff) else 0) for i in range(m)]!=[(rhs[i] if i<len(rhs) else 0) for i in range(m)]:
                ok=False; print("green(da) FAIL",n,k)
        # Gamma^- = B_{n,k-1} for k>=2, k<=n<=2k-1
        if k>=2 and k<=n<=2*k-1:
            gm=p(k-1)*peval(G[n-k],k-1)
            if gm!=peval(K,k-1)-Acache[k-2]: ok=False; print("Gamma- FAIL",n,k)
            if n<=6 and gm!=B[k-1]: ok=False; print("Gamma- vs B enumeration FAIL",n,k,gm,B[k-1])
        if n<=6:
            d=Acache[k]-2*Acache[k-1]+Acache[k-2]
            if d!=2*E[k]-B[k-1]: ok=False; print("tie-block FAIL",n,k)
            if peval(K,k+1)-2*peval(K,k)+peval(K,k-1)!=2*E[k]: ok=False; print("2E FAIL",n,k)
        # (da) of source-rep: k+2<=n<=2k-1
        if k+2<=n<=2*k-1:
            r=n-k
            gp=p(k)*peval(G[r-1],k+2); gm=p(k-1)*peval(G[r],k-1)
            dk=Acache[k]-2*Acache[k-1]+Acache[k-2]; dk1=Acache[k+1]-2*Acache[k]+Acache[k-1]
            S=gp*dk-gm*dk1
            def sd(d,y):
                hg=lambda t: t*peval(G[d],t)
                return hg(y+1)-2*hg(y)+hg(y-1)
            S2=sum(phi(n-d-1,k)*(gp*sd(d,k)-gm*sd(d,k+1)) for d in range(1,r))
            if S!=S2: ok=False; print("S formula FAIL",n,k)
            print("n,k,r",n,k,r,"S>0:",S>0, "(G)_d all strict:",all(Fr(p(k),p(k-1))*peval(G[r-1],k+2)*sd(d,k)>peval(G[r],k-1)*sd(d,k+1) for d in range(1,r)))
print("ALL OK" if ok else "SOME FAIL")
