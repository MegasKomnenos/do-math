# H1 검산: 1.3절 표(n<=10 행), 1.3절 증인, 정리 2.5의 섬유 행과 n<=6 섬유 단봉성, 정리 2.6 재귀.
import itertools, math
from functools import lru_cache

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(1,n+1):
        z=0
        for j in range(1,i):
            if sigma[j-1]>sigma[i-1]: z=j
        h.append(i-z)
    return h

def row_from_perms(n):
    # A_{n,l} = sum_sigma prod min(h_i, l+1)
    A=[0]*(n)
    for s in itertools.permutations(range(1,n+1)):
        h=caps(s)
        for l in range(n):
            A[l]+=math.prod(min(x,l+1) for x in h)
    b=[A[0]]+[A[l]-A[l-1] for l in range(1,n)]
    return A,b

def brute_row(n):
    # 직접 주차 시뮬레이션 (n<=7)
    b=[0]*n
    for a in itertools.product(range(1,n+1),repeat=n):
        occ=[False]*(n+1); M=0; ok=True
        for ai in a:
            p=ai
            while p<=n and occ[p]: p+=1
            if p>n: ok=False;break
            occ[p]=True; M=max(M,p-ai)
        if ok: b[M]+=1
    return b

table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],6:[720,3963,4594,3688,2546,1296],
7:[5040,42253,62145,57398,46142,32359,16807],8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}

for n in range(1,8):
    assert brute_row(n)==table[n], (n, brute_row(n))
print("brute force n<=7: 표와 일치")

# 정리 2.6 마지막 차 재귀로 n<=10 검산:
# A_{n,l} = sum_{m=0}^{n-1} binom(n-1,m) A_{m,l} A_{n-1-m,l} * min(m+1, l+1)  (마지막 차가 자리 m+1에 설 때 왼쪽 블록 m, 오른쪽 n-1-m)
@lru_cache(None)
def A(n,l):
    if l<0: return 0
    if n==0: return 1
    return sum(math.comb(n-1,m)*A(m,l)*A(n-1-m,l)*min(m+1,l+1) for m in range(n))
for n in range(1,11):
    b=[A(n,l)-A(n,l-1) for l in range(n)]
    assert b==table[n], (n,b)
    assert sum(b)==(n+1)**(n-1)
print("재귀(정리 2.6 꼴) n<=10: 표와 일치, 합 p_n 일치")

def witness(b):
    peaks=[i for i in range(len(b)) if all(b[j]<=b[j+1] for j in range(i)) and all(b[j]>=b[j+1] for j in range(i,len(b)-1))]
    return peaks
for n in range(1,11):
    print(n, "증인(최소)", min(witness(table[n])), "k_n", -(-n//2), "d_{n,k_n}", table[n][-(-n//2)]-table[n][-(-n//2)-1] if n>=2 else None)

# 정리 2.5
s=(1,2,3,5,4,6,7); h=caps(s); As=[math.prod(min(x,l+1) for x in h) for l in range(7)]
bs=[As[0]]+[As[l]-As[l-1] for l in range(1,7)]
print("sigma=(1,2,3,5,4,6,7) h=",h," row=",bs)
def unimodal(b):
    return len(witness(b))>0
for n in range(1,7):
    bad=[s for s in itertools.permutations(range(1,n+1)) if not unimodal((lambda h:[math.prod(min(x,1) for x in h)]+[math.prod(min(x,l+1) for x in h)-math.prod(min(x,l) for x in h) for l in range(1,n)])(caps(s)))]
    print("n=",n,"비단봉 섬유 수", len(bad))
bad7=[s for s in itertools.permutations(range(1,8)) if not unimodal((lambda h:[math.prod(min(x,1) for x in h)]+[math.prod(min(x,l+1) for x in h)-math.prod(min(x,l) for x in h) for l in range(1,7)])(caps(s)))]
print("n=7 비단봉 섬유 수", len(bad7), "보기", bad7[:3])
