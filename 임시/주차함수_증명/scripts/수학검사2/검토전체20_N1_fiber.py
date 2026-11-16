# 명제 2-20 유한 n 상계 재계산 (닫힌 꼴; 로그로 계산, n=17·100은 정확 유리수로도)
import sys,io
from fractions import Fraction as Fr
from math import factorial, lgamma, log, exp
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def v(k,Z,H): return (1+1.0/k)**Z+(1-1.0/k)**(Z+H)-2
def ok(n,b):
    return all(v(k,i-1,1)<0 for i in range(3,b+1) for k in range(n//2+1,n+1))
def lf(m): return lgamma(m+1)
def bound_float(n,b):
    if not ok(n,b): return None
    tot=0.0; res=0.0
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        lbase=lf(n)+(c-1)*log(c)-lf(c)-(n-1)*log(n+1)
        tot+=exp(lbase+log(b)+(n-c-b)*log(n-c+1)-lf(kap))
        res+=exp(lbase+log(2)+(n-c-b)*log(n-c-b+3)-lf(kap))
    return 1-tot+res
def bound_exact(n,b):
    if not ok(n,b): return None
    pn=(n+1)**(n-1); tot=Fr(0); res=Fr(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fr(factorial(n)*c**(c-1),factorial(c)*pn)
        tot+=base*b*Fr(n-c+1)**(n-c-b)/factorial(kap)
        res+=base*2*Fr(n-c-b+3)**(n-c-b)/factorial(kap)
    return 1-tot+res
for n in [17,100,1000,10000]:
    cands=[(b,bound_float(n,b)) for b in range(3,14)]
    cands=[(b,r) for b,r in cands if r is not None]
    b,r=min(cands,key=lambda t:t[1])
    line=f'n={n}: best b={b}, bound={r:.6f}'
    if n<=100: line+=f'  exact={float(bound_exact(n,b)):.6f}'
    print(line, ' all:',[(bb,round(rr,4)) for bb,rr in cands])
