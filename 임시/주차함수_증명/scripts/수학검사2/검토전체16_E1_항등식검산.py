# E1 검산: 2장 항등식들을 작은 n에서 정확 정수로 확인
# (1) 정리 2-28 d=2E-B, 따름 2-29, 보조 2-30 (B<=J, n<=2k-1 등식, n=2k의 Xi), 보조 2-14 섬유 부호식  [n<=7 전수]
# (2) 정리 2-13 사슬 공식, (3) 정리 2-40 다섯 몫 분해, (4) 정리 moving-tail (사)(아)
from math import comb, factorial, exp, e, sqrt
from fractions import Fraction
from itertools import product, permutations
def park(a):
    n=len(a); occ=[0]*(n+2); pos=[0]*n
    for i,ai in enumerate(a):
        j=ai
        while j<=n and occ[j]: j+=1
        if j>n: return None
        occ[j]=i+1; pos[i]=j
    return pos, occ
def caps(sigma):
    c=[]
    for j in range(len(sigma)):
        m=0
        while j-1-m>=0 and sigma[j-1-m]<sigma[j]: m+=1
        c.append(m+1)
    return c
p=lambda m:(m+1)**(m-1) if m>=1 else 1
# ---- (1) brute force
for n in range(1,8):
    pfs=[]
    for a in product(range(1,n+1),repeat=n):
        r=park(a)
        if r is None: continue
        pos,occ=r
        d=[pos[i]-a[i] for i in range(n)]
        M=max(d); Mh=d.count(M)
        sigma=occ[1:n+1]; h=caps(sigma)
        blocked=all(h[pos[i]-1]==M+1 for i in range(n) if d[i]==M)
        pfs.append((M,Mh,blocked))
    assert len(pfs)==p(n)
    b=[sum(1 for x in pfs if x[0]==l) for l in range(n+1)]
    for k in range(1,n+1):
        d_nk=b[k]-b[k-1]
        E=sum(1 for x in pfs if x[0]==k and x[1]%2==0 and x[1]>0)
        E2=sum(1 for x in pfs if x[0]==k and x[1]==2)
        B=sum(1 for x in pfs if x[0]==k-1 and x[2])
        assert d_nk==2*E-B,(n,k)
        assert 2*E2-B<=d_nk
        # J_n(k-1)
        J=0
        for s in permutations(range(1,n+1)):
            h=caps(s); H=h.count(k); Z=sum(1 for x in h if x>k); P=1
            for x in h:
                if x<k: P*=x
            J+=H*k**(H-1)*(k-1)**Z*P if H>0 else 0
        assert B<=J,(n,k,B,J)
        if n<=2*k-1: assert B==J,(n,k)
        if n==2*k: assert J-B==comb(2*k-1,k-1)*p(k-1)**2,(n,k,J-B)
    # 2-14 fiber sign identity
    for s in permutations(range(1,n+1)):
        h=caps(s)
        A=lambda l:eval('*'.join(str(min(x,l+1)) for x in h)) if l>=0 else 0
        for k in range(1,n+1):
            Z=sum(1 for x in h if x>k); H=h.count(k)
            lhs=Fraction((A(k)-A(k-1))-(A(k-1)-A(k-2)))
            v=(1+Fraction(1,k))**Z+(1-Fraction(1,k))**(Z+H)-2
            assert lhs==A(k-1)*v
print("(1) 2-28/2-29/2-30/2-14 OK for n<=7")
# ---- A table via recursion
def A_of(n,l):
    if l<0: return 0
    f=[1]+[0]*n
    for m in range(1,n+1):
        f[m]=sum(comb(m-1,q-1)*f[q-1]*f[m-q]*min(q,l+1) for q in range(1,m+1))
    return f[n]
# (2) 2-13
for l in range(0,6):
    for n in range(1,2*l+4):
        pi=lambda m:Fraction(comb(n,m)*m**(m-1)*p(n-m),p(n))
        pi0=1-sum(pi(m) for m in range(l+2,n+1))
        rhs=p(n)*pi0+sum(comb(n,m)*(l+1)*A_of(m-1,l)*p(n-m) for m in range(l+2,n+1))
        assert rhs==A_of(n,l),(l,n)
print("(2) 2-13 OK")
# (3) 2-40
for k in range(2,7):
    for n in range(2*k+1,3*k):
        A={l:[A_of(m,l) for m in range(n+1)] for l in (k-2,k-1,k)}
        b=lambda m,l:A[l][m]-(A[l-1][m] if l-1 in A else A_of(m,l-1))
        bTk=lambda t:(k+1)*A[k][t-1]-k*A[k-1][t-1] if t>=k+1 else 0
        bTk1=lambda t:k*A[k-1][t-1]-(k-1)*A[k-2][t-1] if t>=k else 0
        delta=lambda t:bTk(t)-bTk1(t)
        Theta=comb(n,k)*k**(k-2)*A[k-1][n-k]
        FL=sum(comb(n,t)*delta(t)*A[k-1][n-t] for t in range(k+1,2*k+2))
        BV=sum(comb(n,m+1)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
        KD=sum(comb(n,m+1)*p(n-1-m)*k*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        PAIR=Fraction(0)
        for t1 in range(1,n+1):
            for t2 in range(1,n-t1+1):
                PAIR+=Fraction(factorial(n),factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bTk(t1)*bTk(t2)+bTk1(t1)*bTk1(t2))*p(n-t1-t2)
        PAIR/=2
        d=b(n,k)-b(n,k-1)
        assert d==-Theta+FL+BV+KD+PAIR,(k,n)
        assert delta(k)==-k**(k-2)
print("(3) 2-40 OK for k=2..6")
# (4) moving tail
Ren=lambda j:j**j*exp(-j)/factorial(j) if j>=1 else 1.0
worst=0
for n in range(3,61):
    row=[A_of(n,l) for l in range(n)]; bb=[row[0]]+[row[l]-row[l-1] for l in range(1,n)]
    for r in range(1,(n-1)//2+1):
        dd=bb[n-r]-bb[n-r-1]
        lhs=abs(-dd/n**(n-2)-e*Ren(r+1)); bound=60*(r+1)/n
        assert lhs<=bound,(n,r,lhs,bound)
        worst=max(worst,lhs/bound)
    for D in range(2,n):
        if n>=20*D**1.5:
            assert all(bb[n-j]>bb[n-j+1] for j in range(D,1,-1)),(n,D)
print("(4) moving-tail (사)(아) OK n<=60; max |err|/bound =",round(worst,4))
