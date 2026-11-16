# H3 검산: 5.1절 수치 (정리 old-5-1, old-5-2, 명제 witness-position-bound), 보조정리 cayley-ratio
from fractions import Fraction
from math import comb, factorial, ceil, floor, e, pi, sqrt, exp, log
import itertools, sys

# 1) 작은 n 브루트포스: 최대 변위별 주차함수 수 b_{n,l}
def brute_rows(n):
    row=[0]*n
    for a in itertools.product(range(1,n+1), repeat=n):
        occ=[False]*(n+1); ok=True; md=0
        for i,p in enumerate(a):
            q=p
            while q<=n and occ[q]: q+=1
            if q>n: ok=False;break
            occ[q]=True; md=max(md,q-p)
        if ok: row[md]+=1
    return row

# 2) 재귀 (정리 2-6을 n!로 나눈 꼴): n a_n = sum_{j=1}^n min(j,k) a_{j-1} a_{n-j},  a_n = A_{n,k-1}/n!
def A_column(k, N):
    # returns list A[n]=A_{n,k-1} for n=0..N (exact integers), using A_n = sum_j min(j,k) C(n-1,j-1) A_{j-1} A_{n-j}
    A=[1]+[0]*N
    for n in range(1,N+1):
        s=0
        for j in range(1,n+1):
            s+=min(j,k)*comb(n-1,j-1)*A[j-1]*A[n-j]
        A[n]=s
    return A

N=300
cols={}
for k in range(1,N+1):
    cols[k]=A_column(k,N)   # cols[k][n] = A_{n,k-1}
def A(n,l):  # A_{n,l}
    if l<0: return 0
    return cols[l+1][n]
def row(n):
    return [A(n,l)-A(n,l-1) for l in range(n)]
for n in range(1,8):
    assert row(n)==brute_rows(n), n
print("recursion matches brute force for n<=7")

# 3) 첫째 조각 사슬 b_{n,0}<...<b_{n,k_n-1} 이 깨지는 n (n<=300)
broken=[]
for n in range(1,N+1):
    b=row(n); kn=ceil(n/2)
    if any(not(b[i]<b[i+1]) for i in range(0,kn-1)): broken.append(n)
print("chain b_{n,0}<..<b_{n,k_n-1} broken at n =",broken)

# 4) 모든 n<=300 단봉, 봉우리 한 칸, 중앙 d_{n,k_n} 부호
def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i==len(b)-1
bad=[n for n in range(1,N+1) if not unimodal(row(n))]
print("non-unimodal n<=300:",bad)
negc=[n for n in range(2,N+1) if row(n)[ceil(n/2)]-row(n)[ceil(n/2)-1]<=0]
print("d_{n,k_n}<=0 at n =",negc)
# 봉우리 한 칸 여부 (n>=16)
plateau=[n for n in range(16,N+1) if row(n).count(max(row(n)))>1]
print("plateau n in [16,300]:",plateau)
# 오른쪽 절반 인접 쌍 모두 엄격 (5<=n<=300)
ties=[n for n in range(5,N+1) if any(row(n)[l]==row(n)[l+1] for l in range(ceil((n-1)/2),n-1))]
print("right-half ties n:",ties)
# Q_R(n) 5<=n<=300
def QR(n):
    b=row(n)
    for l in range(ceil((n-1)/2), n-2):
        if b[l]>b[l+1] and not (b[l+1]**2>=b[l]*b[l+2]): return False
    return True
print("Q_R fails:",[n for n in range(5,N+1) if not QR(n)])

# 5) 증인 위치 상계 (50<=n<=300)
vals=[]
for n in range(50,N+1):
    b=row(n); ls=b.index(max(b))
    v=n+1-ls-0.59963*(n+1)**(2/3)-1.24847*(n+1)**(1/3)
    vals.append(v)
print("witness residual range n in [50,300]: [%.4f, %.4f]"%(min(vals),max(vals)))

# 6) 개수 셈
cnt=sum(n-2-ceil((n-1)/2) for n in range(5,20001)); print("positions 5..20000:",cnt)
cnt2=sum(n-2-ceil((n-1)/2) for n in range(20001,50001)); print("positions 20001..50000:",cnt2)
cnt3=sum(ceil(n/2)-1 for n in range(10001,20001)); print("comparisons k=2..k_n, 10001..20000:",cnt3)
# 첫째 조각 열 범위 확인
for k in (141,142):
    print(k, 2*ceil(k*k/4))
# 7) (n-1)n!/2 > n! 및 b_{n,1} 하계 확인
for n in range(4,8):
    assert row(n)[1] >= (n-1)*factorial(n)//2, n
print("b_{n,1} >= (n-1)n!/2 holds n=4..7; b_{n,1}:",[row(n)[1] for n in range(2,8)],"(n-1)n!/2:",[(n-1)*factorial(n)//2 for n in range(2,8)])
# 8) Cayley 비 k<=9
for k in range(1,10):
    cr=(1+1/k)**(k-2); v=cr*(1+5/(2*k)+2/k**2)
    print(k, "%.5f"%v, v>87/32)
print("87/32=",87/32," e<65/24+1/100:",e<65/24+0.01, 65/24+0.01)
# 정리 5-2 (나) m* 범위: n=20001
n=20001
ms=[m for m in range(171,2000) if m**1.5+9*m<=n]
print("m* for n=20001:",max(ms), "min n with nonempty set:", 171**1.5+9*171)
