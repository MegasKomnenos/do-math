# -*- coding: utf-8 -*-
"""X1 G1 검산: 가중 분배함수 Z_n(w)의 순열 표현 = 숲 표현, 공통 재귀, 지수 생성함수,
그리고 국소 역전 수 표시 a(t,d)의 세분(F2 §4)과 2.10·평균 2.11의 귀결. 정확 유리수."""
import itertools, random, sys
from fractions import Fraction as Fr
from math import comb, factorial

random.seed(20261117)

def capacities(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j)
    return h

def forests(n):
    """뿌리 라벨 숲: 부모 배열 par[v] in {0}∪[n]\{v}, 비순환."""
    for par in itertools.product(range(0,n+1), repeat=n):
        ok=True
        for v in range(1,n+1):
            if par[v-1]==v: ok=False;break
            # 순환 검사
            seen=set(); u=v
            while u!=0:
                if u in seen: ok=False;break
                seen.add(u); u=par[u-1]
            if not ok: break
        if ok: yield par

def forest_stats(par):
    n=len(par)
    children={v:[] for v in range(0,n+1)}
    for v in range(1,n+1): children[par[v-1]].append(v)
    t={}; I={}
    def dfs(v):
        desc=[]
        for c in children[v]:
            desc+=dfs(c)
        t[v]=1+len(desc); I[v]=sum(1 for d in desc if d<v)
        return desc+[v]
    for r in children[0]: dfs(r)
    return t,I

NMAX_PERM=7; NMAX_FOR=6
w=[None]+[Fr(random.randint(1,40),random.randint(1,9)) for _ in range(NMAX_PERM)]
a={}  # a(t,d), 0<=d<t
for t in range(1,NMAX_FOR+1):
    for d in range(t): a[(t,d)]=Fr(random.randint(0,30),random.randint(1,7))
w_a=[None]+[sum(a[(t,d)] for d in range(t)) for t in range(1,NMAX_FOR+1)]

out=[]
def log(s): out.append(s); print(s)

# (1) 순열 쪽 Z_n(w) (n<=7), 재귀, EGF
Zperm={0:Fr(1)}
for n in range(1,NMAX_PERM+1):
    s=Fr(0)
    for sig in itertools.permutations(range(1,n+1)):
        p=Fr(1)
        for h in capacities(sig): p*=w[h]
        s+=p
    Zperm[n]=s
ok_rec=all(Zperm[n]==sum(comb(n-1,j)*w[j+1]*Zperm[j]*Zperm[n-1-j] for j in range(n)) for n in range(1,NMAX_PERM+1))
log(f"[G1(나)] 공통 재귀 Z_n=sum C(n-1,j) w_{{j+1}} Z_j Z_{{n-1-j}}, n<=7: {ok_rec}")
# EGF exp(sum w_t Z_{t-1} x^t/t!)
N=NMAX_PERM
inner=[Fr(0)]*(N+1)
for t in range(1,N+1): inner[t]=w[t]*Zperm[t-1]/factorial(t)
# exp 급수
def series_exp(c,N):
    e=[Fr(0)]*(N+1); e[0]=Fr(1)
    # e' = c' e
    for n in range(1,N+1):
        s=Fr(0)
        for j in range(1,n+1): s+=j*c[j]*e[n-j]
        e[n]=s/n
    return e
E=series_exp(inner,N)
ok_egf=all(E[n]==Zperm[n]/factorial(n) for n in range(N+1))
log(f"[G1(다)] Z(x)=exp(sum_t w_t Z_{{t-1}} x^t/t!), n<=7: {ok_egf}")

# (2) 숲 쪽 (n<=6): sum_F prod w_{t_v}/t_v, 그리고 a(t,d) 세분
for n in range(0,NMAX_FOR+1):
    sF=Fr(0); sA=Fr(0); sperm_a=None
    if n==0:
        sF=Fr(1); sA=Fr(1)
    else:
        for par in forests(n):
            t,I=forest_stats(par)
            p=Fr(1); q=Fr(1)
            for v in range(1,n+1):
                p*=w[t[v]]/t[v]; q*=a[(t[v],I[v])]
            sF+=p; sA+=q
    # a 세분의 순열 쪽
    s=Fr(0)
    for sig in itertools.permutations(range(1,n+1)):
        p=Fr(1)
        for h in capacities(sig): p*=w_a[h]
        s+=p
    log(f"[G1(가)] n={n}: sum_F prod w/t == Z_n(w)? {sF==Zperm[n]} ; a(t,d) 세분: sum_F prod a(t_v,I_v) == Z_n(sum_d a)? {sA==s}")

# (3) 2.10: a(t,d)=1[d<=l]  → #{F: M(F)<=l} == A_{n,l} (순열 쪽 w=min(t,l+1)); 2.11 둘째 식
for n in range(1,NMAX_FOR+1):
    for l in range(0,n):
        cnt=0; prodsum=Fr(0)
        for par in forests(n):
            t,I=forest_stats(par)
            if max(I.values())<=l: cnt+=1
            p=Fr(1)
            for v in range(1,n+1): p*=Fr(min(t[v],l+1),t[v])
            prodsum+=p
        A=0
        for sig in itertools.permutations(range(1,n+1)):
            p=1
            for h in capacities(sig): p*=min(h,l+1)
            A+=p
        assert cnt==A==prodsum, (n,l,cnt,A,prodsum)
log("[2.10 / 2.11 둘째 식] n<=6, 모든 l: #{F: M(F)<=l} == A_{n,l} == sum_F prod min(t_v,l+1)/t_v : True")

# (4) 평균 2.11: 다중집합 {(t_v,I_v)}의 법칙 == {(t_v, floor(U_v t_v))}의 법칙 (n<=5, 전수)
from collections import Counter
for n in range(1,6):
    c1=Counter(); c2=Counter()
    for par in forests(n):
        t,I=forest_stats(par)
        key=tuple(sorted((t[v],I[v]) for v in range(1,n+1)))
        c1[key]+=Fr(1)
        # 독립 균등: 각 꼭짓점 I_v 균등 {0..t_v-1} → 가중 1/prod t_v
        verts=list(range(1,n+1))
        for choice in itertools.product(*[range(t[v]) for v in verts]):
            key2=tuple(sorted((t[v],choice[i]) for i,v in enumerate(verts)))
            c2[key2]+=Fr(1,1)
            for v in verts: c2[key2]/=1  # placeholder
    # 올바른 가중: 1/prod t_v
    c2=Counter()
    for par in forests(n):
        t,I=forest_stats(par)
        verts=list(range(1,n+1)); wgt=Fr(1)
        for v in verts: wgt/=t[v]
        for choice in itertools.product(*[range(t[v]) for v in verts]):
            key2=tuple(sorted((t[v],choice[i]) for i,v in enumerate(verts)))
            c2[key2]+=wgt
    log(f"[평균 2.11] n={n}: 법칙 일치 {dict(c1)==dict(c2)}")

open("심사_X1_G1_가중분배_out.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
