# 검토 23차 R1: 1.3절 표, 1.4절 수치, 2장 항등식의 재계산 (정확 정수)
import sys, itertools, math
from fractions import Fraction as Fr
from math import comb, factorial
sys.stdout.reconfigure(encoding='utf-8')
def p(n): return 1 if n==0 else (n+1)**(n-1)
def park(a):
    n=len(a); occ=[0]*(n+2); d=[]; pos=[]
    for x in a:
        y=x
        while y<=n and occ[y]: y+=1
        if y>n: return None
        occ[y]=1; d.append(y-x); pos.append(y)
    return d,pos
# brute force rows n<=7
def brute(n):
    row=[0]*n; E={}; B={}; E2={}
    for a in itertools.product(range(1,n+1),repeat=n):
        r=park(a)
        if r is None: continue
        d,pos=r; M=max(d); row[M]+=1
        # outcome perm & capacities
        sig=[0]*(n+1)
        for car,(pp) in enumerate(pos,1): sig[pp]=car
        h=[0]*(n+1)
        for i in range(1,n+1):
            z=0
            for j in range(i-1,0,-1):
                if sig[j]>sig[i]: z=j;break
            h[i]=i-z
        cnt=sum(1 for x in d if x==M)
        if cnt%2==0: E[M]=E.get(M,0)+1
        if cnt==2: E2[M]=E2.get(M,0)+1
        blocked=all(h[pos[c]]==M+1 for c in range(n) if d[c]==M)
        if blocked: B[M]=B.get(M,0)+1
    return row,E,B,E2
# recursion
N=120
A=[[0]*(N+2) for _ in range(N+1)]  # A[n][l], l=0..N
for l in range(N+1):
    A[0][l]=1
for n in range(1,N+1):
    for l in range(N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
        A[n][l]=s
def b(n,l):
    if l<0: return 0
    return A[n][l]-(A[n][l-1] if l>=1 else 0)
for n in range(1,8):
    row,E,B,E2=brute(n)
    assert row==[b(n,l) for l in range(n)],(n,row)
    assert sum(row)==p(n)
    for k in range(1,n+1):
        d=b(n,k)-b(n,k-1)
        assert d==2*E.get(k,0)-B.get(k-1,0),(n,k)
        assert 2*E2.get(k,0)-B.get(k-1,0)<=d
    if n<=7: print(n,row,'B=',[B.get(l,0) for l in range(n)])
print('table rows n<=10:')
for n in range(1,11):
    print(n,[b(n,l) for l in range(n)],p(n))
def minwit(n):
    row=[b(n,l) for l in range(n)]
    for w in range(n):
        if all(row[i]<=row[i+1] for i in range(w)) and all(row[i]>=row[i+1] for i in range(w,n-1)): return w
    return None
print('min witnesses',[(n,minwit(n)) for n in range(1,21)])
print('unimodal all n<=120:',all(minwit(n) is not None for n in range(1,N+1)))
kn=lambda n:(n+1)//2
print('sign d_{n,k_n}:',[(n,(b(n,kn(n))-b(n,kn(n)-1)>0)-(b(n,kn(n))-b(n,kn(n)-1)<0)) for n in range(2,25)])
print('all n in 16..120 positive:',all(b(n,kn(n))-b(n,kn(n)-1)>0 for n in range(16,N+1)))
# after middle comparison decreasing for 2..15
for n in range(2,16):
    assert all(b(n,j)>=b(n,j+1) for j in range(kn(n),n-1)),n
# log-concavity
def lc(n):
    row=[b(n,l) for l in range(n)]
    return [l for l in range(1,n-1) if row[l]**2<row[l-1]*row[l+1]]
first=[n for n in range(1,N+1) if lc(n)]
print('first non-logconcave n:',first[:5], lc(80))
print('b80:',b(80,39)<b(80,40)<b(80,41))
# row last term b_{k,k-1}=p_{k-1}
assert all(b(k,k-1)==p(k-1) for k in range(1,60))
# A_{n,0}=n!, A_1 egf 1/(2-e^x): Fubini numbers
assert all(A[n][0]==factorial(n) for n in range(0,20))
fub=[1]
for n in range(1,15): fub.append(sum(comb(n,j)*fub[n-j] for j in range(1,n+1)))
assert [A[n][1] for n in range(15)]==fub
# Bor, Ren, theta, pi
def pi_(n,m): return Fr(comb(n,m)*m**(m-1)*p(n-m),p(n))
def theta(t,k): return Fr(comb(t,k)*k**(k-1)*(t-k)**(t-k),t**(t-1))
def s(m,y): return Fr(A[m][y-1],p(m)) if y>=1 else Fr(0)
def c(m,Y): return Fr(b(m,Y),p(m))
# one-tree recursion
for y in range(1,12):
    for n in range(1,2*y+2):
        rhs=sum(pi_(n,m)/m*(s(m-1,y+1)+y*c(m-1,y)) for m in range(y+1,n+1))
        assert rhs==c(n,y),(n,y)
# Thm 2-13 (나) first eq with pi0
def pi0(n,y):
    # prob all trees size<=y : egf exp(T^{<=y})
    # compute number of forests on n with all trees <= y
    f=[0]*(n+1); f[0]=1
    for m in range(1,n+1):
        f[m]=sum(comb(m-1,t-1)*t**(t-1)*f[m-t] for t in range(1,min(y,m)+1))
    return Fr(f[n],p(n))
for y in range(1,10):
    for n in range(1,2*y+2):
        rhs=pi0(n,y)+sum(pi_(n,m)*Fr(y,m)*s(m-1,y) for m in range(y+1,n+1))
        assert rhs==s(n,y),(n,y)
# union bound
for n in range(1,40):
    for y in range(1,n+1):
        ub=sum(theta(n+1,t)*Fr(t-y,t) for t in range(y+1,n+1))
        assert 1-s(n,y)<=ub
# SM, DM0
for m in range(0,60):
    for y in range(1,62):
        assert s(m+1,y)<=s(m,y) and s(m,y)<=s(m+1,y+1)
# b-top / delta / Theta, BV definitions sanity: tree expansion coefficient check
def Ncnt(l,t): return min(t,l+1)*A[t-1][l]
def bT(t,l): return Ncnt(l,t)-(Ncnt(l-1,t) if l>=1 else 0)
for k in range(2,9):
    for t in range(1,30):
        dl=bT(t,k)-bT(t,k-1)
        if t>=k+1:
            assert dl==k*(b(t-1,k)-b(t-1,k-1))+b(t-1,k)+b(t-1,k-1)
        elif t==k: assert dl==-k**(k-2)
        else: assert dl==0
    # (다) cut: b_{n,k}=n![x^n]A_{k-1}B_k for n<=2k+1
    for n in range(1,2*k+2):
        v=sum(comb(n,t)*bT(t,k)*A[n-t][k-1] for t in range(k+1,n+1))
        assert v==b(n,k),(n,k)
    for n in range(1,2*k):
        v=sum(comb(n,t)*bT(t,k-1)*A[n-t][k-1] for t in range(k,n+1))
        assert v==b(n,k-1),(n,k)
print('ch2 identities ok')
# moving tail: Q1 formula and inequalities, (아)
def Q1(n,r): return comb(n,r)*(n-r)**(n-r-2)*(r+1)**r
for n in range(3,121):
    for r in range(1,(n-1)//2+1):
        diff=b(n,n-r-1)-b(n,n-r)
        assert diff<=Q1(n,r),(n,r)
        # (마) upper
        nf=Fr(factorial(n)*(n-r)**(n-r-2),factorial(n-r)*n**(n-2))  # without e^r
        # (사): |diff/n^{n-2} - e Ren(r+1)| <= 60(r+1)/n ; float check
        eren=math.exp(-r)*(r+1)**r/math.factorial(r)
        assert abs(diff/n**(n-2)-eren)<=60*(r+1)/n
for D in range(2,5):
    n0=math.ceil(20*D**1.5)
    for n in range(n0,121):
        assert all(b(n,n-r-1)>b(n,n-r) for r in range(1,D)),(D,n)
print('moving tail ok')
