# (a) 정리 2-6 재귀로 A_{n,l}를 정확히 세고 1.4절의 가운데 비교 부호(2<=n<=15 음, n>=16 양)와 1.3절 l*_n을 본다.
# (b) 정리 2-5 마지막 문장: n<=7의 섬유 행 단봉성.  (c) 명제 2-20 유한 n 상계(부동소수, 유효숫자 3자리 확인용).
import itertools, math, sys
from math import comb, lgamma, log, exp
NMAX=30
p=[1]+[(n+1)**(n-1) for n in range(1,NMAX+1)]
def Arow(l):
    A=[1]
    for n in range(1,NMAX+1):
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
A={l:Arow(l) for l in range(0,NMAX)}
def b(n,l): return A[l][n]-(A[l-1][n] if l>=1 else 0)
out=[]
for n in range(2,NMAX+1):
    k=(n+1)//2; d=b(n,k)-b(n,k-1); row=[b(n,l) for l in range(n)]; pk=row.index(max(row))
    uni=all(row[i]<=row[i+1] for i in range(pk)) and all(row[i]>=row[i+1] for i in range(pk,n-1))
    out.append(f"n={n} k_n={k} sign(d_{{n,k_n}})={'+' if d>0 else '-' if d<0 else '0'} l*={pk} unimodal={uni} sum_ok={sum(row)==p[n]}")
def caps(s):
    c=[]
    for j in range(len(s)):
        t=1;i=j-1
        while i>=0 and s[i]<s[j]: t+=1;i-=1
        c.append(t)
    return c
for n in range(1,8):
    bad=0
    for s in itertools.permutations(range(n)):
        c=caps(s); As=[math.prod(min(h,l+1) for h in c) for l in range(n)]
        bs=[As[0]]+[As[l]-As[l-1] for l in range(1,n)]; pk=bs.index(max(bs))
        if not (all(bs[i]<=bs[i+1] for i in range(pk)) and all(bs[i]>=bs[i+1] for i in range(pk,n-1))): bad+=1
    out.append(f"fibers n={n}: non-unimodal={bad}")
def v(k,Z,H): return (1+1/k)**Z+(1-1/k)**(Z+H)-2
def lfact(n): return lgamma(n+1)
def bound(n):
    best=None
    for bb in range(3,60):
        if not all(v(k,i-1,1)<0 for i in range(3,bb+1) for k in range(n//2+1,n+1)): continue
        s1=s2=0.0
        for c in range(n//2+1,n+1):
            kap=n-c-bb+1
            if kap<0: continue
            lbase=lfact(n)+(c-1)*log(c)-lfact(c)-(n-1)*log(n+1)
            e=n-c-bb
            s1+=exp(lbase+log(bb)+e*log(n-c+1)-lfact(kap))
            s2+=exp(lbase+log(2)+e*log(n-c-bb+3)-lfact(kap))
        val=1-s1+s2
        if best is None or val<best[1]: best=(bb,val)
    return best
for n in [17,100,1000,10000]:
    bb,val=bound(n); out.append(f"Prop2-20 n={n}: best b={bb} bound={val:.6f}")
open(sys.argv[1],"w",encoding="utf-8").write("\n".join(out)+"\n")
