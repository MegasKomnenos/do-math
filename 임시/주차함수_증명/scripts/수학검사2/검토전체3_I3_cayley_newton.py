# I3: 보조정리 cayley-ratio의 k=1..9 값과 정리 old-5-4의 Newton 인증을 작은 r에서 재현
from fractions import Fraction as Fr
from math import comb, factorial
import sys
def p(n): return (n+1)**(n-1) if n>=1 else 1
# cayley ratio
for k in range(1,10):
    cr=Fr(k+1,k)**(k-2)
    v=cr*(1+Fr(5,2*k)+Fr(2,k*k))
    print(k, float(v), v>Fr(87,32))
# Gamma recursion
from functools import lru_cache
def Gamma(d,y,n):
    g=[Fr(1)]
    for dd in range(1,d+1):
        s=comb(n,dd)*p(dd)
        s+= y*sum(comb(n-dd+j,j)*p(j)*g[dd-1-j] for j in range(dd))
        g.append(Fr(s))
    return g[d]
e15=sum(Fr(1,factorial(j)) for j in range(16))
def hg(d,y,n): return y*Gamma(d,y,n)
def sd(d,y,n): return hg(d,y+1,n)-2*hg(d,y,n)+hg(d,y-1,n)
def Nw(r,d,nv):
    k=r+1+nv; n=k+r
    return factorial(15)*(2*e15*k*k*(k+1)*Gamma(r-1,k+2,n)*sd(d,k,n)-(2*k*k+5*k+4)*Gamma(r,k-1,n)*sd(d,k+1,n))
rmax=int(sys.argv[1]) if len(sys.argv)>1 else 12
bad=0; maxdeg={}
for r in range(2,rmax+1):
    for d in range(1,r):
        vals=[Nw(r,d,nv) for nv in range(0,2*r+3)]
        assert all(v.denominator==1 for v in vals)
        # forward differences
        diffs=[]; cur=vals[:]
        for i in range(2*r+3):
            diffs.append(cur[0]); cur=[cur[j+1]-cur[j] for j in range(len(cur)-1)]
        ok = diffs[0]>0 and all(x>=0 for x in diffs[1:])
        nz=max(i for i,x in enumerate(diffs) if x!=0)
        maxdeg[(r,d)]=nz
        if not ok: bad+=1; print('FAIL',r,d)
print('bad',bad,'max nonzero diff degree minus (r+d+1):',max(maxdeg[(r,d)]-(r+d+1) for (r,d) in maxdeg))
# check: sd_d(y)>0, c>=0 small cases; and p_k/p_{k-1} vs bound
for k in range(1,30):
    assert Fr(p(k),p(k-1))==(k+1)*Fr(k+1,k)**(k-2)
    assert Fr(p(k),p(k-1))>2*e15*k*k*(k+1)/Fr(2*k*k+5*k+4)
print('ratio ok')
