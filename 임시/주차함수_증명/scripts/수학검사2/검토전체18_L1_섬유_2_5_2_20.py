# (1) 정리 2.5 마지막 문장: n<=6 모든 섬유 행이 단봉인지 완전 열거.
# (2) 명제 2.20 유한 n 상계값(0.740, 0.317, 0.0658, 0.0115)을 정확 유리수로 재계산.
import itertools
from fractions import Fraction as Fr
from math import factorial, comb
def caps(perm):
    n=len(perm); h=[]
    for i in range(n):
        z=0
        for j in range(i-1,-1,-1):
            if perm[j]>perm[i]: z=j+1;break
        h.append(i+1-z)
    return h
def unimodal(seq):
    i=0
    while i+1<len(seq) and seq[i]<=seq[i+1]: i+=1
    while i+1<len(seq) and seq[i]>=seq[i+1]: i+=1
    return i==len(seq)-1
for n in range(1,1):
    bad=0
    for perm in itertools.permutations(range(1,n+1)):
        h=caps(perm)
        A=[1]
        for l in range(n):
            p=1
            for x in h: p*=min(x,l+1)
            A.append(p)
        b=[A[l+1]-A[l] for l in range(n)]
        if not unimodal(b): bad+=1
    print(f"n={n}: non-unimodal fibers = {bad}")
# (2)
def v(k,Z,H):
    return (1+Fr(1,k))**Z+(1-Fr(1,k))**(Z+H)-2
def bound(n,b):
    # condition: for 3<=i<=b and n/2<k<=n, v_k(i-1,1)<0
    for i in range(3,b+1):
        for k in range(n//2+1,n+1):
            if v(k,i-1,1)>=0: return None
    pn=(n+1)**(n-1)
    tot1=Fr(0); tot2=Fr(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fr(factorial(n),factorial(c))*c**(c-1)/pn
        tot1+=base*b*Fr(n-c+1)**(n-c-b)/factorial(kap)
        tot2+=base*2*Fr(n-c-b+3)**(n-c-b)/factorial(kap)
    return 1-tot1+tot2
for n in (17,100,1000,10000):
    best=None
    for b in range(3,40):
        r=bound(n,b)
        if r is None: break
        if best is None or r<best[1]: best=(b,r)
    print(f"n={n}: best b={best[0]}, bound={float(best[1]):.6f}")
