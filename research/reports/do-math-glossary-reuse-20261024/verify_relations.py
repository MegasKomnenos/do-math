from itertools import permutations, product
from collections import defaultdict
from math import prod, comb
from pathlib import Path
import json
def forest_sizes(n):
    for parents in product(*([0]+list(range(v+1,n+1)) for v in range(1,n+1))):
        sizes=[1]*(n+1)
        for v,p in enumerate(parents,1):
            if p:sizes[p]+=sizes[v]
        yield sizes[1:]
def widths(p):
    return [j-max([-1]+[i for i in range(j) if p[i]>p[j]]) for j in range(len(p))]
def evaluate(c,u,y):
    return sum(v*u**a*y**e for (a,e),v in c.items())
def polynomial(n,q):
    f=defaultdict(int)
    for ts in forest_sizes(n):
        f[sum(t>q for t in ts),ts.count(q)]+=prod(t for t in ts if t<q)
    return f
def main():
    output={'coefficient_checks':[],'original_parking_checks':[]}
    for n in range(8):
        for q in range(2,6):
            f=polynomial(n,q);theta=defaultdict(int);damp=0
            for pi in permutations(range(1,n+1)):
                hs=widths(pi);a=sum(h>q for h in hs);e=hs.count(q)
                theta[a,e]+=prod(min(h,q) for h in hs)
                damp+=prod(h if h<q else q if h==q else q-1 for h in hs)
            assert dict(theta)=={(a,e):v*q**(a+e) for (a,e),v in f.items()}
            assert damp==evaluate(f,q-1,q)
            # Independent permutation sums check the moment/damping substitutions.
            m1=m2=hit=damped_hit=damped_pair=0
            for pi in permutations(range(1,n+1)):
                hs=widths(pi);a=sum(h>q for h in hs);e=hs.count(q)
                weight=prod(min(h,q) for h in hs)
                dw=prod(h if h<q else q if h==q else q-1 for h in hs)
                m1+=weight*a;m2+=weight*a*(a-1);hit+=weight*e
                damped_hit+=dw*e;damped_pair+=dw*comb(e,2)
            assert m1==sum(v*a*q**(a+e) for (a,e),v in f.items())
            assert m2==sum(v*a*(a-1)*q**(a+e) for (a,e),v in f.items())
            assert hit==sum(v*e*q**(a+e) for (a,e),v in f.items())
            assert damped_hit==sum(v*e*(q-1)**a*q**e for (a,e),v in f.items())
            assert damped_pair==sum(v*comb(e,2)*(q-1)**a*q**e for (a,e),v in f.items())
            assert evaluate(f,0,q)==sum(prod(ts) for ts in forest_sizes(n) if all(t<=q for t in ts))

            output['coefficient_checks'].append({'n':n,'q':q,'coefficients':len(f)})
    for n in range(1,6):
        A=[0]*6
        for prefs in product(range(1,n+1),repeat=n):
            occupied=set();ds=[]
            for a in prefs:
                place=next((j for j in range(a,n+1) if j not in occupied),None)
                if place is None:break
                occupied.add(place);ds.append(place-a)
            if len(ds)==n:
                for l in range(6):A[l]+=max(ds)<=l
        for q in range(2,6):
            f=polynomial(n,q)
            assert evaluate(f,q,q)==A[q-1]
            assert evaluate(f,q+1,q)-2*evaluate(f,q,q)+evaluate(f,q-1,q-1)==A[q]-2*A[q-1]+A[q-2]
        output['original_parking_checks'].append({'n':n,'A':A})
    T=lambda n:1 if n==0 else (n+1)**(n-1)
    B=T(4)-sum(comb(4,s+1)*T(3-s)*(s+1)*T(s) for s in range(1,4))
    J=sum(prod(ts) for ts in forest_sizes(4) if all(t<=1 for t in ts))
    assert B==-11 and J==1
    output['domain_counterexample']={'k':1,'n':4,'B_cmp':B,'J_cmp':J}
    output['scope']='Finite exact checks only; no general or Lean certification.'
    Path(__file__).with_suffix('.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS: 32 coefficient comparisons; original parking n=1..5; distinct extensions.')
if __name__=='__main__':main()
