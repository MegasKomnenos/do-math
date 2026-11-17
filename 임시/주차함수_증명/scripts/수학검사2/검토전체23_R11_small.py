from math import comb, factorial
from fractions import Fraction
def p(n): return (n+1)**(n-1) if n>=1 else 1
N=120
def col(l,N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
cols=[col(l,N) for l in range(N)]
def b(n,l):
    if l<0 or l>n-1: return 0
    return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
neg=[]; 
for n in range(1,61):
    k=(n+1)//2
    d=b(n,k)-b(n,k-1)
    if d<0: neg.append(n)
    if d==0: print("zero",n)
print("d_{n,k_n}<0 for n in", neg)
for n in range(2,16):
    k=(n+1)//2
    assert all(b(n,j)>=b(n,j+1) for j in range(k,n-1)), n
print("right half nonincreasing for 2<=n<=15 ok")
# e_n, J_n(k-1) by recursions; ratio
def eJ(k):
    A=[p(i) for i in range(k+1)]+[0]*k
    D=[0]*(2*k+1); E=[0]*(2*k+1); J=[0]*(2*k+1); J[k]=p(k-1)
    for n in range(k+1,2*k+1):
        r=n-k
        A[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*A[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*min(i+1,k)*p(i)*p(n-1-i) for i in range(r-1,k+1))
        D[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*D[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*p(i)*A[n-1-i] for i in range(0,r))
        E[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*E[n-1-i] for i in range(0,r-1))+2*sum(comb(n-1,i)*p(i)*D[n-1-i] for i in range(0,r-1))
        J[n]=sum(comb(n-1,i)*(k+i)*p(i)*J[n-1-i] for i in range(0,r))+comb(n-1,k-1)*p(k-1)*p(n-k)
    return A,E,J
res=[]
for k in range(4,61):
    A,E,J=eJ(k)
    for n in (2*k-1,2*k):
        assert A[n]==cols[k-1][n]
        res.append((float(Fraction(E[n],J[n])),n,E[n]>J[n]))
        # d >= e - J
        d=b(n,k)-b(n,k-1)
        assert d>=E[n]-J[n]
res.sort()
print(res[:6])
print("e_n>J_n(k-1) fails at n:", sorted(n for _,n,ok in res if not ok))
# l=0: b_{n,1} >= (n-1) n!/2
for n in range(2,40):
    assert b(n,1)>=(n-1)*factorial(n)//2
print("b_{n,1}>=(n-1)n!/2 ok; equality?", [n for n in range(2,12) if b(n,1)*2==(n-1)*factorial(n)])
# (ㅁ) unimodal & breaks
brk=[]
for n in range(1,121):
    k=(n+1)//2
    row=[b(n,l) for l in range(n)]
    pk=row.index(max(row))
    assert all(row[i]<=row[i+1] for i in range(pk)) and all(row[i]>=row[i+1] for i in range(pk,n-1)),n
    if not all(row[i]<row[i+1] for i in range(0,k-1)): brk.append(n)
print("b_{n,0}<...<b_{n,k_n-1} breaks at", brk)
# d_{n,k}<0 at out-of-statement positions 2k+1<=n<=11
print([(n,k) for k in range(2,6) for n in range(2*k+1,12) if b(n,k)-b(n,k-1)<0], [(n,k) for k in range(2,6) for n in range(2*k+1,12) if b(n,k)-b(n,k-1)==0])
# witness offset for small n
from mpmath import mp, mpf
mp.dps=30
def peak(n):
    row=[b(n,l) for l in range(n)]
    return next(l for l in range(n-1) if row[l]>row[l+1])
for n in (50,51,52,100,120):
    ls=peak(n)
    v=n+1-ls-mpf('0.59963')*mpf(n+1)**(mpf(2)/3)-mpf('1.24847')*mpf(n+1)**(mpf(1)/3)
    print(n,ls,v)
print([ (round(x,7),n) for x,n,ok in res if n>=16][:4])
