# N1 검산: 1.3절 표(n<=10)와 증인, 정리 2.5(n<=6 섬유 단봉, n=7 반례), 2.4절 보기 나무, 보조정리 zeta-constants, 명제 2.20 상계값
import sys
from math import comb, factorial
from itertools import permutations, product
import mpmath as mp
def out(*a): print(*a); sys.stdout.flush()

def A_table(N):
    A=[[0]*(N+2) for _ in range(N+1)]
    for l in range(N+2): A[0][l]=1
    for n in range(1,N+1):
        for l in range(N+2):
            A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A
N=10; A=A_table(N)
out("== 1.3 표")
for n in range(1,N+1):
    row=[A[n][l]-(A[n][l-1] if l>0 else 0) for l in range(n)]
    assert sum(row)==(n+1)**(n-1)
    wit=next(w for w in range(n) if all(row[i]<=row[i+1] for i in range(w)) and all(row[i]>=row[i+1] for i in range(w,n-1)))
    out(n,row,sum(row),"ell*=",wit)
def park(a):
    n=len(a); occ=[False]*(n+1); pos=[0]*n
    for i,ai in enumerate(a):
        p=ai
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=True; pos[i]=p
    return pos
for n in (3,4):
    cnt={}
    for a in product(range(1,n+1),repeat=n):
        pos=park(a)
        if pos is None: continue
        M=max(pos[i]-a[i] for i in range(n)); cnt[M]=cnt.get(M,0)+1
    out("brute n=",n,[cnt.get(l,0) for l in range(n)])
out("== 정리 2.5")
def hcap(sig):
    n=len(sig); h=[]
    for i in range(n):
        z=0
        for j in range(i):
            if sig[j]>sig[i]: z=j+1
        h.append(i+1-z)
    return h
def fiber_row(h):
    n=len(h); Al=[0]  # A^sigma_{-1}=0
    for l in range(n):
        p=1
        for x in h: p*=min(x,l+1)
        Al.append(p)
    return [Al[l+1]-Al[l] for l in range(n)]
def unimodal(r):
    m=len(r)
    return any(all(r[i]<=r[i+1] for i in range(w)) and all(r[i]>=r[i+1] for i in range(w,m-1)) for w in range(m))
out("sigma=(1,2,3,5,4,6,7): h=",hcap((1,2,3,5,4,6,7)),"row=",fiber_row(hcap((1,2,3,5,4,6,7))))
for n in range(1,8):
    bad=[s for s in permutations(range(1,n+1)) if not unimodal(fiber_row(hcap(s)))]
    out("n=",n,"non-unimodal fibers:",len(bad), (bad[:2] if n==7 else ""))
sizes=[7,6,4,3,2,1,1]; mult=factorial(7)
for t in sizes: mult//=t
dist={}
for Iv in product(*[range(t) for t in sizes]):
    M=max(Iv); dist[M]=dist.get(M,0)+mult
out("2.4 tree mult=",mult,"M dist:",[dist.get(l,0) for l in range(7)])
mp.mp.dps=30
out("== zeta:",mp.zeta(mp.mpf(1)/2), mp.zeta(-mp.mpf(1)/2), mp.zeta(mp.mpf(3)/2))
out("== 명제 2.20 상계값")
def cond_ok(n,b):
    # k^i v_k(i-1,1) = (k+1)^(i-1) k + (k-1)^i - 2k^i < 0 for all 3<=i<=b, n/2<k<=n
    for i in range(3,b+1):
        for k in range(n//2+1,n+1):
            if (k+1)**(i-1)*k+(k-1)**i-2*k**i>=0: return False
    return True
def logterm(n,c,b,base,sh):
    # n!/c! * c^(c-1) * base*(sh)^(n-c-b) / ((n-c-b+1)! (n+1)^(n-1)), sh=n-c+1 or n-c-b+3
    kap=n-c-b+1
    if kap<0: return None
    L=mp.loggamma(n+1)-mp.loggamma(c+1)+(c-1)*mp.log(c)+mp.log(base)+(n-c-b)*mp.log(sh)-mp.loggamma(kap+1)-(n-1)*mp.log(n+1)
    return mp.e**L
for n in (17,100,1000,10000):
    best=None; b=3
    while b<=n//2+1 and cond_ok(n,b):
        s1=mp.mpf(0); s2=mp.mpf(0)
        for c in range(n//2+1,n+1):
            t1=logterm(n,c,b,b,n-c+1); t2=logterm(n,c,b,2,n-c-b+3)
            if t1 is not None: s1+=t1
            if t2 is not None: s2+=t2
        val=1-s1+s2
        if best is None or val<best[0]: best=(val,b)
        b+=1
    out(n,"first failing b=",b,"best bound",mp.nstr(best[0],7),"at b=",best[1])
