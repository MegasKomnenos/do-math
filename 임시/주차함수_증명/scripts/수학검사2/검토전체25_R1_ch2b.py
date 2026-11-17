# R1 검산: 2장 2.7(생성함수), 2.8-2.12
import itertools, math
from fractions import Fraction as Fr
from math import comb, factorial
def p(n): return 1 if n==0 else (n+1)**(n-1)
ORD=26
def mul(a,b):
    r=[Fr(0)]*ORD
    for i,x in enumerate(a):
        if x==0: continue
        for j,y in enumerate(b):
            if i+j>=ORD: break
            r[i+j]+=x*y
    return r
def add(a,b): return [x+y for x,y in zip(a,b)]
def sc(c,a): return [c*x for x in a]
def integ(a): return [Fr(0)]+[a[i]/(i+1) for i in range(ORD-1)]
def deriv(a): return [a[i+1]*(i+1) for i in range(ORD-1)]+[Fr(0)]
def expo(a):
    assert a[0]==0
    r=[Fr(0)]*ORD; r[0]=Fr(1); da=deriv(a)
    # r' = a' r
    for n in range(1,ORD):
        r[n]=sum(da[i]*r[n-1-i] for i in range(n))/n
    return r
T=[Fr(0)]+[Fr(t**(t-1),factorial(t)) for t in range(1,ORD)]
eT=[Fr(p(m),factorial(m)) for m in range(ORD)]
assert expo(T)==eT
Gr=add(T,sc(Fr(-1,2),mul(T,T)))
assert deriv(Gr)[:ORD-1]==eT[:ORD-1]
# permutation-recursion for K_{n,k}(eta,y): weights wg_t = t (t<k), eta (t=k), y (t>k)
def Kseq(k,eta,y,N):
    wg=lambda t: Fr(t) if t<k else (Fr(eta) if t==k else Fr(y))
    Aw=[Fr(1)]
    for n in range(1,N+1):
        Aw.append(sum(comb(n-1,j)*wg(j+1)*Aw[j]*Aw[n-1-j] for j in range(n)))
    return Aw
def Atab(N):
    A={}
    for l in range(-1,N+2):
        A[(0,l)]=1 if l>=0 else 0
        for n in range(1,N+1):
            A[(n,l)]=0 if l<0 else sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
    return A
N=ORD-1; A=Atab(N)
def b(n,l): return 0 if l<0 else A[(n,l)]-A[(n,l-1)]
def d(n,k): return b(n,k)-b(n,k-1)
def s(m,y): return Fr(A[(m,y-1)],p(m)) if y>=1 else Fr(0)
def c(m,Y): return Fr(b(m,Y),p(m))
for k in range(1,9):
    K_kk=Kseq(k,k,k,N); K_kk1=Kseq(k,k,k+1,N); K_m=Kseq(k,k-1,k-1,N)
    for n in range(N+1):
        assert K_kk[n]==A[(n,k-1)] and K_kk1[n]==A[(n,k)] and K_m[n]==(A[(n,k-2)] if k>=2 else (1 if n==0 else 0)),(k,n)
    # closed form (ㄱ): K = e^adj / (1 - y int e^adj)
    for (eta,y) in [(k,k),(k,k-1),(Fr(3,2),Fr(5,7)),(k,k+1)]:
        adj=[Fr(0)]*ORD
        for t in range(1,k):
            adj[t]=(t-Fr(y))*p(t-1)/factorial(t)
        adj[k]=(Fr(eta)-Fr(y))*p(k-1)/factorial(k)
        ea=expo(adj); den=add([Fr(1)]+[Fr(0)]*(ORD-1),sc(-Fr(y),integ(ea)))
        Kser=[Kseq(k,eta,y,N)[n]/factorial(n) for n in range(ORD)]
        assert mul(Kser,den)==ea,(k,eta,y)
    # J_n(z) = d/d eta K at eta=k ; via finite difference exactness (polynomial in eta of degree <= n/k): use symbolic derivative via interpolation
    def Jn(z,n):
        deg=n//k
        if deg==0: return Fr(0)
        xs=[Fr(k)+i for i in range(deg+1)]
        ys=[Kseq(k,x,z,n)[n] for x in xs]
        # derivative of Lagrange interpolant at x=k (=xs[0])
        tot=Fr(0)
        for i in range(deg+1):
            # L_i'(x0)
            if i==0:
                der=sum(Fr(1)/(xs[0]-xs[j]) for j in range(1,deg+1))
            else:
                der=math.prod([(xs[0]-xs[j]) for j in range(1,deg+1) if j!=i] or [Fr(1)])/math.prod([(xs[i]-xs[j]) for j in range(deg+1) if j!=i])
            tot+=ys[i]*der
        return tot
    for z in [Fr(k-1),Fr(k),Fr(2,3)]:
        ezg=expo(sc(z,Gr)); emzg=expo(sc(-z,Gr))
        mon=[Fr(0)]*ORD; mon[k-1]=Fr(1,factorial(k-1))
        Y=sc(p(k-1),mul(mul(eT,ezg),integ(mul(emzg,mon))))
        firstbad=None
        for n in range(0,min(N,3*k+2)+1):
            jn=Jn(z,n); yn=Y[n]*factorial(n)
            if jn!=yn and firstbad is None: firstbad=n
            if n<=2*k: assert jn==yn,(k,z,n,jn,yn)
            if 0<=z<=k+1: assert jn<=yn
        if k<=6: print("k",k,"z",z,"J_n = p_{k-1}G first differs at n=",firstbad,"(2k+1=%d)"%(2*k+1))
    # B_{n,k-1} = K(k,k-1)-K(k-1,k-1), d = 2E - B consistency with e_n >= ...
    Kb=Kseq(k,k,k-1,N)
    for n in range(1,N+1):
        if k<=n:
            B=Kb[n]-K_m[n]
            J=Jn(Fr(k-1),n) if n<=3*k+2 else None
            if J is not None:
                assert B<=J
                if n<=2*k-1: assert B==J
                if n==2*k: assert J-B==comb(2*k-1,k-1)*p(k-1)**2
    # volterra (ㄱ): K_k(y;x) = e^T e^pd, residual order
    for y in [Fr(k),Fr(k-1),Fr(k+1),Fr(1,3)]:
        Ks=[Kseq(k,k,y,N)[n]/factorial(n) for n in range(ORD)]
        Elt=[eT[j] if j<k else Fr(0) for j in range(ORD)]
        Tgt=[T[t] if t>k else Fr(0) for t in range(ORD)]
        Tle=[T[t] if t<=k else Fr(0) for t in range(ORD)]
        pd=add(sc(y,integ(add(Ks,sc(-1,Elt)))),sc(-1,Tgt))
        assert all(pd[i]==0 for i in range(min(k+1,ORD)))
        for t in range(k+1,ORD):
            assert pd[t]*factorial(t)==y*Kseq(k,k,y,N)[t-1]-t**(t-1)
        assert mul(eT,expo(pd))==Ks
        one=[Fr(1)]+[Fr(0)]*(ORD-1)
        sm=mul(add(one,sc(-1,T)),add(eT,sc(-1,Elt)))
        assert add(Elt,sm)==mul(eT,add(one,sc(-1,Tgt)))
        eTle=expo(Tle)
        assert add(Elt,sm)[:min(2*k+2,ORD)]==eTle[:min(2*k+2,ORD)]
        Gs=add(add(Elt,sm),sc(y,mul(mul(eT,expo(sc(y,Gr))),integ(mul(sm,expo(sc(-y,Gr)))))))
        X=add(Ks,sc(-1,Gs))
        assert all(X[i]==0 for i in range(min(2*k+2,ORD))),(k,y)
        epd=expo(pd)
        rhs=mul(eT,add(sc(y,integ(X)),add(add(epd,sc(-1,one)),sc(-1,pd))))
        assert rhs==X
        rhs2=mul(eTle,add(sc(y,integ(X)),sc(Fr(1,2),mul(pd,pd))))
        m=min(3*k+3,ORD); assert rhs2[:m]==X[:m]
        if 0<=y<=k+1: assert all(Ks[i]<=eT[i] for i in range(ORD))
print("2.7 generating functions ok")
