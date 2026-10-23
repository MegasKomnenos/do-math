from pathlib import Path
from itertools import product,permutations
from math import factorial,comb,prod
from collections import Counter
from fractions import Fraction as Q
import json
out=Path('output'); checks=[]
def forests(n):
 for pars in product(*[[0]+list(range(i+1,n+1)) for i in range(1,n+1)]):
  p=(0,)+pars; t=[0]+[1]*n
  for v in range(1,n+1):
   if p[v]:t[p[v]]+=t[v]
  yield p,t[1:]
def widths(pi):return [j-max([0]+[i for i in range(1,j) if pi[i-1]>pi[j-1]]) for j in range(1,len(pi)+1)]
def poly(n,q):
 c=Counter()
 for p,t in forests(n):c[sum(s>q for s in t),t.count(q)]+=prod(s for s in t if s<q)
 return c
def pp(n,q):
 c=Counter()
 for pi in permutations(range(1,n+1)):
  h=widths(pi);c[sum(s>q for s in h),h.count(q)]+=prod(s for s in h if s<q)
 return c
def evalp(c,u,y):return sum(b*u**a*y**e for (a,e),b in c.items())
rows={}
for n in range(1,7):
 b=[0]*n; fails=0
 for pref in product(range(1,n+1),repeat=n):
  free=set(range(1,n+1));ds=[]
  for a in pref:
   opts=[s for s in free if s>=a]
   if not opts:fails+=1;break
   s=min(opts);free.remove(s);ds.append(s-a)
  else:b[max(ds)]+=1
 rows[n]=b
 for q in range(2,6):
  c=poly(n,q)
  assert evalp(c,q,q)==sum(b[:min(q,n)])
  assert evalp(c,q+1,q)==sum(b[:min(q+1,n)])
  assert evalp(c,q-1,q-1)==sum(b[:min(q-1,n)])
  uu=sum(w*a*(a-1)*q**(a+e-2) for (a,e),w in c.items() if a>=2)
  yy=sum(w*e*(q-1)**a*q**(e-1) for (a,e),w in c.items() if e)
  loss=evalp(c,q-1,q)-evalp(c,q-1,q-1)
  delta=(b[q] if q<n else 0)-(b[q-1] if q-1<n else 0)
  assert loss<=yy and uu-yy<=delta
 checks.append({'n':n,'b':b,'failed':fails})
for n in range(8):
 for q in range(1,6):assert poly(n,q)==pp(n,q)
T=lambda n:1 if n==0 else (n+1)**(n-1)
def B(k,n):return T(n)-sum(comb(n,s+1)*T(n-s-1)*(s+1)*T(s) for s in range(k,n))
def J(k,n):
 a=[1]
 for m in range(n):a.append(sum(comb(m,i)*(i+1)*T(i)*a[m-i] for i in range(min(k,m+1))))
 return a[n]
for k in range(10):
 for n in range(2*k+2):assert B(k,n)==J(k,n)
assert (B(1,4),J(1,4))==(-11,1)
# General labelled rooted forests: exact cmp polynomial at n=2,x=1.
# Empty marking contributes T2=3; root marking in either oriented chain contributes c/2-1.
cmp=lambda c:Q(3)+2*(Q(c,2)-1)
assert cmp(1)==2 and cmp(2)==3
res={'parking_checks':checks,'permutation_forest':{'n':'0..7','q':'1..5','pairs':40},'lower_checks':{'n':'1..6','q':'2..5','pairs':24},'B_J':{'k':'0..9','n':'0..2k+1','pairs':110,'outside':{'B_1_4':-11,'J_1_4':1}},'cmp_missing_diagonal':{'n':2,'x':1,'c1':str(cmp(1)),'c2':str(cmp(2)),'T_minus_linearDeficit_at_l0':2}}
(out/'independent-checks.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
