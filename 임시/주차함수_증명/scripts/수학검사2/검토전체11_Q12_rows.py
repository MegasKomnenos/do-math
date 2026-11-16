# Q12: 부록 D 장2·장3·장4 항목의 작은 수치 재계산 (마지막 차 재귀, 전수 주차)
import sys, itertools
from math import comb
from fractions import Fraction
sys.set_int_max_str_digits(0)

def park(pref):
    n=len(pref); spots=[0]*n; order=[0]*n; disp=[0]*n
    for car,a in enumerate(pref,1):
        p=a-1
        while p<n and spots[p]: p+=1
        if p>=n: return None
        spots[p]=car; order[p]=car; disp[car-1]=p-(a-1)
    return tuple(order), max(disp)

# (1) 전수 주차 n<=7: 섬유 행, 용량 다중집합 수, 비단봉 섬유
def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i==len(b)-1
def caps(sigma):
    n=len(sigma); h=[]
    for i in range(1,n+1):
        m=0
        for j in range(1,i):
            if sigma[j-1]>sigma[i-1]: m=j
        h.append(i-m)
    return h
for n in range(1,8):
    fibers={}
    total=0
    for pref in itertools.product(range(1,n+1),repeat=n):
        r=park(pref)
        if r is None: continue
        total+=1
        sig,M=r
        fibers.setdefault(sig,[0]*n)[M]+=1
    assert total==(n+1)**(n-1)
    assert len(fibers)==len(list(itertools.permutations(range(1,n+1))))
    capsets=set()
    nonuni=[]
    for sig in sorted(fibers):
        h=caps(sig)
        capsets.add(tuple(sorted(h)))
        # 곱 공식
        A=[0]
        for l in range(n):
            A.append(1)
            for hi in h: A[-1]*=min(hi,l+1)
        row=[A[l+1]-A[l] for l in range(n)]
        assert row==fibers[sig],(sig,row,fibers[sig])
        if not unimodal(row): nonuni.append((sig,h,row))
    print("n",n,"pf",total,"capsets",len(capsets),"nonuni",len(nonuni), nonuni[0] if nonuni else "")

# (2) 마지막 차 재귀 n<=80 전 열
N=80
A=[[0]*(N+1) for _ in range(N+1)]  # A[n][l]
for l in range(N+1):
    A[0][l]=1
for n in range(1,N+1):
    for l in range(N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
        A[n][l]=s
def b(n,l):
    return A[n][l]-(A[n][l-1] if l>=1 else 0)
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
    assert A[n][0]==__import__('math').factorial(n)
print("row n=4:",[b(4,l) for l in range(4)])
# 로그오목 실패
fails=[(n,l) for n in range(1,N+1) for l in range(1,n-1) if b(n,l)**2<b(n,l-1)*b(n,l+1)]
print("logconcave fails n<=80:",fails)
print("b80_39=",b(80,39)); print("b80_40=",b(80,40)); print("b80_41=",b(80,41))
print("diff>0:",b(80,39)*b(80,41)-b(80,40)**2>0)
print("ratios:",float(Fraction(b(80,40),b(80,39))),float(Fraction(b(80,41),b(80,40))))
print("separator:",b(80,40)*25000<25928*b(80,39), b(80,41)*25000>25928*b(80,40))
# (3) crossing: b_{n,k_n}<b_{n,k_n+1}
cross=[n for n in range(5,N+1) if b(n,(n+1)//2)<b(n,(n+1)//2+1)]
print("crossing true for n in 5..80:",[n for n in range(5,N+1) if n not in cross],"false;")
# (4) Q_L(n) 3<=n<=15; d_{n,k_n}<0 for 2<=n<=15; right half nonincreasing
def QL(n):
    for l in range(0,n-2):
        if 2*l<=n-2 and b(n,l)>b(n,l+1):
            if b(n,l+1)**2<b(n,l)*b(n,l+2): return False
    return True
print("QL 3..15:",all(QL(n) for n in range(3,16)))
dneg=[n for n in range(2,N+1) if b(n,(n+1)//2)-b(n,(n+1)//2-1)<0]
print("d_{n,k_n}<0 for n:",dneg)
print("right half nonincreasing for 2..15:",all(all(b(n,j)>=b(n,j+1) for j in range((n+1)//2,n-1)) for n in range(2,16)))
# left strict increase b_{n,1}<...<b_{n,k_n-1} fails where (n<=80)
lf=[n for n in range(2,N+1) if not all(b(n,l)<b(n,l+1) for l in range(0,(n+1)//2-1))]
print("left strict increase b_{n,0}<..<b_{n,k_n-1} fails:",lf)
# unimodal all rows
print("all rows unimodal n<=80:",all(unimodal([b(n,l) for l in range(n)]) for n in range(1,N+1)))
# 넘는 수 재귀 검사 (D:crossing-small-n 식) n<=2l+4
p=[(m+1)**(m-1) if m>0 else 1 for m in range(N+2)]
ok=True
for l in range(0,30):
    for n in range(l+2, min(2*l+4,N)+1):
        Ac=lambda i: p[i]-A[i][l]
        s=sum(comb(n-1,j)*(j-l)*p[j]*p[n-1-j] for j in range(l+1,n))
        s+=sum(Ac(i)*comb(n-1,i)*p[n-1-i]*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        if s!=p[n]-A[n][l]: ok=False; print("Ac recurrence mismatch",n,l,s,p[n]-A[n][l]); break
    if not ok: break
print("Ac recurrence (D:crossing-small-n) ok:",ok)
# D:exact-n20000 (ㄹ) 식: A^c_{n,k-1}, k+1<=n<=2k+1
ok=True
for k in range(1,30):
    l=k-1
    for n in range(k+1, min(2*k+1,N)+1):
        s=sum(comb(n-1,i)*(n-k-i)*p[i]*p[n-1-i] for i in range(0,n-k))
        s+=sum(comb(n-1,i)*(k+i+1)*p[i]*(p[n-1-i]-A[n-1-i][l]) for i in range(0,n-k-1))
        if s!=p[n]-A[n][l]: ok=False; print("exact-n20000 (ㄹ) mismatch",n,k,s,p[n]-A[n][l]); break
    if not ok: break
print("Ac recurrence (D:exact-n20000 ㄹ) ok:",ok)
