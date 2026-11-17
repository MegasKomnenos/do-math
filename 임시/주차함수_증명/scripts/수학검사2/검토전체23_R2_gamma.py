# R2 check: 4.2 boundary response polynomial Gamma_d(y;n) vs boundary polynomial J_n(k-1) (n<=2k-1), and
# S_{n,k}>=0 => Q(n,k-1) sanity on small rows (sign of Gamma^+-, positivity)
from math import comb
from fractions import Fraction
from functools import lru_cache
def p(j): return (j+1)**(j-1) if j>0 else 1
def Gam(d,y,n):
    @lru_cache(None)
    def g(d):
        if d==0: return 1
        return comb(n,d)*p(d)+y*sum(comb(n-d+j,j)*p(j)*g(d-1-j) for j in range(d))
    return g(d)
def J(n,k,y):
    @lru_cache(None)
    def j(m):
        if m<k: return 0
        s=sum(comb(m-1,i)*(y+i+1)*p(i)*j(m-1-i) for i in range(m))
        return s+comb(m-1,k-1)*p(k-1)*p(m-k)
    return j(n)
bad=0
for k in range(2,12):
    for n in range(k+1,2*k+1):
        r=n-k
        if p(k-1)*Gam(r,k-1,n)!=J(n,k,k-1): bad+=1; print('mismatch',n,k)
print('Gamma^- = J_n(k-1) for k<n<=2k, k<=11: mismatches',bad)
# rows
N=40
def col(l,N):
    a=[1]
    for n in range(1,N+1):
        a.append(sum(comb(n-1,j)*min(j+1,l+1)*a[j]*a[n-1-j] for j in range(n)))
    return a
cols=[col(l,N) for l in range(N+2)]
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>0 else 0)
neg=0;tot=0
for n in range(5,N+1):
    for k in range(-(-(n+1)//2),n-1):   # k+2<=n<=2k-1
        if not (k+2<=n<=2*k-1): continue
        r=n-k
        Gp=p(k)*Gam(r-1,k+2,n); Gm=p(k-1)*Gam(r,k-1,n)
        S=Gp*(b(n,k)-b(n,k-1))-Gm*(b(n,k+1)-b(n,k))
        tot+=1
        if S<0: neg+=1
        # check implication S>=0 => Q(n,k-1)
        if S>=0 and b(n,k-1)>b(n,k) and not b(n,k)**2>=b(n,k-1)*b(n,k+1): print('implication fails',n,k)
print('positions',tot,'S<0 count',neg)
