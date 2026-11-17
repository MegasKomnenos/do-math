# R1 검산: 2장 2.1-2.7 항등식 (작은 n 전수)
import itertools, math
from fractions import Fraction as Fr
from math import comb, factorial

def p(n): return 1 if n==0 else (n+1)**(n-1)
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        z=0
        for j in range(i-1,-1,-1):
            if s[j]>s[i]: z=j+1; break
        h.append(i+1-z)
    return h
def Atab(N):
    A={}
    for l in range(-1,N+2):
        A[(0,l)]=1 if l>=0 else 0
        for n in range(1,N+1):
            A[(n,l)]=0 if l<0 else sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
    return A
N=30; A=Atab(N)
def b(n,l): return 0 if l<0 else A[(n,l)]-A[(n,l-1)]
def d(n,k): return b(n,k)-b(n,k-1)
# Prop 2-5
h=caps((1,2,3,5,4,6,7)); assert h==[1,2,3,4,1,6,7]
Al=[math.prod(min(x,l+1) for x in h) for l in range(7)]
assert Al==[1,32,162,384,600,864,1008]
assert [Al[0]]+[Al[i]-Al[i-1] for i in range(1,7)]==[1,31,130,222,216,264,144]
for n in (8,9,10):
    s=tuple([n-6,n-5,n-4,n-2,n-3,n-1,n]+list(range(n-7,0,-1)))
    hh=caps(s); assert hh[:7]==h and all(x==1 for x in hh[7:]),(n,hh)
print("prop 2-5 ok")
# Cor 2-4, K polys, tie-block identity, B, J, Xi via permutations
def perm_stats(n):
    return [caps(s) for s in itertools.permutations(range(1,n+1))]
for n in range(1,8):
    H=perm_stats(n)
    for l in range(0,n+1):
        assert sum(math.prod(min(x,l+1) for x in h) for h in H)==A[(n,l)]
    for k in range(1,n+1):
        # E_{n,k}, E2, B_{n,k-1} by fibre product structure
        E=0;E2=0;B=0;J=0;Xi2=0
        for h in H:
            Z=sum(1 for x in h if x>k); Hk=sum(1 for x in h if x==k)
            low=math.prod(x for x in h if x<k)
            # number with M=k and M#=i : low*k^Hk * C(Z,i) k^(Z-i)
            for i in range(1,Z+1):
                c=low*k**Hk*comb(Z,i)*k**(Z-i)
                if i%2==0: E+=c
                if i==2: E2+=c
            B+=low*(k-1)**Z*(k**Hk-(k-1)**Hk)
            J+=low*(k-1)**Z*(Hk*k**(Hk-1) if Hk>0 else 0)
            Xi2+=low*(k-1)**Z*comb(Hk,2)*(k**(Hk-2) if Hk>=2 else 0)
        assert d(n,k)==2*E-B,(n,k)
        assert 2*E2-B<=d(n,k)
        assert B<=J
        if n<=2*k-1: assert B==J
        if n==2*k:
            assert J-B==comb(2*k-1,k-1)*p(k-1)**2==Xi2,(n,k,J-B)
        if k==1: assert B==1
        if k==n: assert B==b(n,n-1)
print("tie-block, B<=J, Xi ok (n<=7)")
# brute force E,B directly from parking functions n<=6
def park(a):
    n=len(a); occ=[0]*(n+2); disp=[0]*n
    for i,x in enumerate(a):
        q=x
        while q<=n and occ[q]: q+=1
        if q>n: return None
        occ[q]=i+1; disp[i]=q-x
    return disp,occ[1:n+1]
for n in range(1,7):
    Ecnt={};Bcnt={}
    for a in itertools.product(range(1,n+1),repeat=n):
        r=park(a)
        if r is None: continue
        disp,sig=r; h=caps(tuple(sig)); M=max(disp)
        cars=[i for i in range(n) if disp[i]==M]
        if len(cars)%2==0: Ecnt[M]=Ecnt.get(M,0)+1
        pos={c:i for i,c in enumerate(sig)}  # car number->position index
        if all(h[pos[c+1]]==M+1 for c in cars): Bcnt[M]=Bcnt.get(M,0)+1
    for k in range(1,n+1):
        assert d(n,k)==2*Ecnt.get(k,0)-Bcnt.get(k-1,0),(n,k)
print("tie-block direct brute ok (n<=6)")
# weighted partition (가)(나) on forests: enumerate rooted forests via parent arrays
def forests(n):
    for par in itertools.product(range(0,n+1),repeat=n):
        ok=True
        for v in range(1,n+1):
            u=v;steps=0
            while u!=0 and steps<=n:
                u=par[u-1];steps+=1
            if u!=0: ok=False;break
        if ok: yield par
def stats(par):
    n=len(par); desc={v:[] for v in range(1,n+1)}
    for v in range(1,n+1):
        u=par[v-1]
        while u!=0:
            desc[u].append(v); u=par[u-1]
    t={v:1+len(desc[v]) for v in desc}; I={v:sum(1 for w in desc[v] if w<v) for v in desc}
    return t,I,desc
FOR={}
for n in range(1,7):
    FOR[n]=[(par,)+stats(par) for par in forests(n)]
    assert len(FOR[n])==p(n)
    for l in range(0,n):
        assert sum(1 for (par,t,I,dd) in FOR[n] if max(I.values())<=l)==A[(n,l)]
    # shape product formula: A = sum_F prod min(1,(l+1)/t_v)
    for l in range(0,n):
        s=sum(math.prod(Fr(min(tv,l+1),tv) for tv in t.values()) for (par,t,I,dd) in FOR[n])
        assert s==A[(n,l)]
print("forest count agreement ok (n<=6)")
# chain law (가): count (forest, chain) pairs with given sizes and link types
# chain law (가): e^-m 인자는 t_j+sum(gamma)=n+1 로 소거되므로 Bor0(m)=m^(m-1)/m!, Ren0=m^m/m! 로 대조
def Bor0(m): return Fr(m**(m-1),factorial(m))
def Ren0(m): return Fr(m**m,factorial(m)) if m>0 else Fr(1)
for n in range(1,7):
    cnt1={}; cnt2={}
    for (par,t,I,dd) in FOR[n]:
        for v in t:
            for link in ("child","desc"):
                if link=="child" and par[v-1]!=0: continue
                cnt1[(t[v],link)]=cnt1.get((t[v],link),0)+1
            for w in dd[v]:
                for l1 in ("child","desc"):
                    if l1=="child" and par[v-1]!=0: continue
                    for l2 in ("child","desc"):
                        if l2=="child" and par[w-1]!=v: continue
                        cnt2[(t[v],t[w],l1,l2)]=cnt2.get((t[v],t[w],l1,l2),0)+1
    for (t1,link),c0 in cnt1.items():
        g1=n+1-t1
        pred=p(n)*Bor0(t1)/Bor0(n+1)*(Bor0(g1) if link=="child" else Ren0(g1))
        assert pred==c0,(n,t1,link,pred,c0)
    for (t1,t2,l1,l2),c0 in cnt2.items():
        g1=n+1-t1; g2=t1-t2
        pred=p(n)*Bor0(t2)/Bor0(n+1)*(Bor0(g1) if l1=="child" else Ren0(g1))*(Bor0(g2) if l2=="child" else Ren0(g2))
        assert pred==c0,(n,t1,t2,l1,l2,pred,c0)
    cntT={}
    for (par,t,I,dd) in FOR[n]:
        roots=[v for v in t if par[v-1]==0]
        for a in roots:
            for b2 in roots:
                if a!=b2: cntT[(t[a],t[b2])]=cntT.get((t[a],t[b2]),0)+1
    for (t1,t2),c0 in cntT.items():
        pred=p(n)*Bor0(t1)*Bor0(t2)*Bor0(n+1-t1-t2)/Bor0(n+1)
        assert pred==c0
    for tt in range(1,n+1):
        c0=sum(1 for (par,t,I,dd) in FOR[n] for v in t if t[v]==tt)
        th=Fr(comb(n+1,tt)*tt**(tt-1)*(n+1-tt)**(n+1-tt),(n+1)**n)
        assert Fr(c0,p(n))==th
print("chain law (가)(나), theta ok (n<=6)")
def pi(n,m): return Fr(comb(n,m)*m**(m-1)*p(n-m),p(n))
def s(m,y): return Fr(A[(m,y-1)],p(m)) if y>=1 else Fr(0)
def c(m,Y): return Fr(b(m,Y),p(m))
for n in range(1,7):
    for y in range(1,n+1):
        pi0=Fr(sum(1 for (par,t,I,dd) in FOR[n] if max(t[v] for v in t if par[v-1]==0)<=y),p(n))
        if n<=2*y+1:
            assert s(n,y)==pi0+sum(pi(n,m)*Fr(y,m)*s(m-1,y) for m in range(y+1,n+1)),(n,y)
            assert c(n,y)==sum(pi(n,m)/m*(s(m-1,y+1)+y*c(m-1,y)) for m in range(y+1,n+1)),(n,y)
            for ts in range(y,n+1):
                cnt=sum(1 for (par,t,I,dd) in FOR[n] if max(I.values())<=y-1 and max(t[v] for v in t if par[v-1]==0)<=ts)
                assert cnt==p(n)*pi0+sum(comb(n,m)*y*A[(m-1,y-1)]*p(n-m) for m in range(y+1,ts+1)),(n,y,ts)
print("thm 2-13 (가)(나)(다), one-tree recursion ok (n<=6)")
for n in range(1,N-1):
    for y in range(1,n+2):
        if n<=2*y+1:
            assert c(n,y)==sum(pi(n,m)/m*(s(m-1,y+1)+y*c(m-1,y)) for m in range(y+1,n+1)),(n,y)
print("one-tree recursion ok up to",N-2)
def theta(t,k): return Fr(comb(t,k)*k**(k-1)*(t-k)**(t-k),t**(t-1))
for n in range(1,N):
    for y in range(1,n+1):
        assert 1-s(n,y)<=sum(theta(n+1,t)*Fr(t-y,t) for t in range(y+1,n+1))
for m in range(0,N-1):
    for y in range(1,N):
        assert s(m+1,y)<=s(m,y) and s(m,y)<=s(m+1,y+1)
        for y2 in range(y,N):
            assert s(m,y)>=s(m,y2)*math.prod(Fr(min(i,y),min(i,y2)) for i in range(1,m+1))
print("union bound, SM, DM0, capacity shift ok")
