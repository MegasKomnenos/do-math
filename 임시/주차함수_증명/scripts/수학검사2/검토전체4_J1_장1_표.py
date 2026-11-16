# J1 검산: 1.3절 표(b_{n,l}, n<=10), 증인 위치, 1.2절 n=3 보기, 2.2절 섬유 행, n<=6 섬유 단봉성, 2.5절 숲 보기
from itertools import product, permutations
from math import comb

def park(pref):
    n=len(pref); occ=[False]*(n+1); pos=[0]*n
    for i,a in enumerate(pref):
        p=a
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=True; pos[i]=p
    return pos

def brute_rows(n):
    b=[0]*n
    for pref in product(range(1,n+1),repeat=n):
        pos=park(pref)
        if pos is None: continue
        M=max(pos[i]-pref[i] for i in range(n))
        b[M]+=1
    return b

# 마지막 차 재귀 (정리 2-6)
def A_rec(N,L):
    A=[[0]*(L+1) for _ in range(N+1)]
    for l in range(L+1):
        A[0][l]=1
        for n in range(1,N+1):
            A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A

def rows_rec(N):
    A=A_rec(N,N)
    out={}
    for n in range(1,N+1):
        row=[A[n][0]]+[A[n][l]-A[n][l-1] for l in range(1,n)]
        out[n]=row
    return out

def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        z=0
        for j in range(i):
            if sig[j]>sig[i]: z=j+1
        h.append(i+1-z)
    return h

def fiber_rows(n):
    # 따름정리 2-4
    A=[0]*n
    for sig in permutations(range(1,n+1)):
        h=caps(sig)
        for l in range(n):
            p=1
            for x in h: p*=min(x,l+1)
            A[l]+=p
    return [A[0]]+[A[l]-A[l-1] for l in range(1,n)]

def unimodal(z):
    m=len(z); 
    for s in range(m):
        if all(z[i]<=z[i+1] for i in range(s)) and all(z[i]>=z[i+1] for i in range(s,m-1)): return s
    return None

table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],6:[720,3963,4594,3688,2546,1296],
7:[5040,42253,62145,57398,46142,32359,16807],8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
R=rows_rec(10)
for n in range(1,11):
    ok = R[n]==table[n]; s=sum(R[n]); print(n, "표 일치" if ok else ("불일치", R[n]), "합", s, "=p_n" if s==(n+1)**(n-1) else "합 불일치", "최소증인", unimodal(R[n]))
for n in range(1,8):
    print("brute", n, brute_rows(n)==R[n])
for n in range(1,9):
    print("fiber", n, fiber_rows(n)==R[n])
# 1.2절 n=3 보기
grp={0:[],1:[],2:[]}
for pref in product(range(1,4),repeat=3):
    pos=park(pref)
    if pos: grp[max(pos[i]-pref[i] for i in range(3))].append(pref)
print(grp)
# 2.2절 섬유
sig=(1,2,3,5,4,6,7); h=caps(sig); print("h",h)
A=[1]
A=[eval('*'.join(str(min(x,l+1)) for x in h)) for l in range(7)]; print("A^sigma",A, "row",[A[0]]+[A[l]-A[l-1] for l in range(1,7)])
for n in range(7,10):
    sp=tuple(list(range(n-6,n-3))+[n-2,n-3,n-1,n]+list(range(n-7,0,-1)))
    hh=caps(sp); AA=[eval('*'.join(str(min(x,l+1)) for x in hh)) for l in range(n)]
    print(n, sp, hh, [AA[0]]+[AA[l]-AA[l-1] for l in range(1,n)])
# n<=6 모든 섬유 단봉?
for n in range(1,8):
    bad=0
    for sg in permutations(range(1,n+1)):
        hh=caps(sg); AA=[eval('*'.join(str(min(x,l+1)) for x in hh)) for l in range(n)]
        row=[AA[0]]+[AA[l]-AA[l-1] for l in range(1,n)]
        if unimodal(row) is None: bad+=1
    print("n",n,"비단봉 섬유 수",bad)
