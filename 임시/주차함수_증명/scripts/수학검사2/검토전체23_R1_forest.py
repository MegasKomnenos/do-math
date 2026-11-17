# 검토 23차 R1: 숲 열거로 정리 2:old-2-10, 2:chain-law(가)(나)(라), 2:old-2-45 확인 (n<=6)
import sys, itertools, math
from fractions import Fraction as Fr
from math import comb, factorial, exp
sys.stdout.reconfigure(encoding='utf-8')
def p(n): return 1 if n==0 else (n+1)**(n-1)
def forests(n):
    # parent[v] in 0..n (0 = root), acyclic
    for par in itertools.product(range(0,n+1),repeat=n):
        ok=True
        for v in range(1,n+1):
            if par[v-1]==v: ok=False;break
        if not ok: continue
        # check acyclic
        depth_ok=True
        for v in range(1,n+1):
            u=v;steps=0
            while u!=0:
                u=par[u-1];steps+=1
                if steps>n: depth_ok=False;break
            if not depth_ok:break
        if depth_ok: yield par
def Bor(m): return Fr(m**(m-1),factorial(m))  # times e^{-m} (track separately)
def Ren(j): return Fr(j**j,factorial(j)) if j>0 else Fr(1)
A={}
for n in range(1,7):
    cnt=0; Mdist={}
    chain={}  # key (t1,t2,link1,link2) -> count of (forest,chain) pairs
    single={}
    trees2={}
    for par in forests(n):
        cnt+=1
        # subtree sizes, descendants
        anc={v:[] for v in range(1,n+1)}
        for v in range(1,n+1):
            u=par[v-1]
            while u!=0:
                anc[v].append(u); u=par[u-1]
        t={v:1 for v in range(1,n+1)}
        I={v:0 for v in range(1,n+1)}
        for v in range(1,n+1):
            for a in anc[v]:
                t[a]+=1
                if v<a: I[a]+=1
        M=max(I.values()); Mdist[M]=Mdist.get(M,0)+1
        for v1 in range(1,n+1):
            for l1 in ('c','d'):
                if l1=='c' and par[v1-1]!=0: continue
                single[(t[v1],l1)]=single.get((t[v1],l1),0)+1
                for v2 in range(1,n+1):
                    if v1 not in anc[v2]: continue
                    for l2 in ('c','d'):
                        if l2=='c' and par[v2-1]!=v1: continue
                        key=(t[v1],t[v2],l1,l2)
                        chain[key]=chain.get(key,0)+1
        roots=[v for v in range(1,n+1) if par[v-1]==0]
        for a in roots:
            for b_ in roots:
                if a!=b_:
                    trees2[(t[a],t[b_])]=trees2.get((t[a],t[b_]),0)+1
    assert cnt==p(n)
    A[n]=Mdist
    # chain law (가): pairs = p_n * Bor(t_j)/Bor(n+1) * prod ; e-powers cancel
    for (t1,l1),c in single.items():
        g1=n+1-t1
        f=(Bor(g1) if l1=='c' else Ren(g1))
        assert c==p(n)*Bor(t1)/Bor(n+1)*f,(n,t1,l1)
    for (t1,t2,l1,l2),c in chain.items():
        g1=n+1-t1; g2=t1-t2
        f=(Bor(g1) if l1=='c' else Ren(g1))*(Bor(g2) if l2=='c' else Ren(g2))
        assert c==p(n)*Bor(t2)/Bor(n+1)*f,(n,t1,t2,l1,l2,c)
    for (a,b_),c in trees2.items():
        assert c==p(n)*Bor(a)*Bor(b_)*Bor(n+1-a-b_)/Bor(n+1)
    print(n,cnt,sorted(Mdist.items()))
# compare M(F) distribution with parking rows
rows={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],6:[720,3963,4594,3688,2546,1296]}
for n in rows:
    assert [A[n].get(l,0) for l in range(n)]==rows[n]
print('forest checks ok')
