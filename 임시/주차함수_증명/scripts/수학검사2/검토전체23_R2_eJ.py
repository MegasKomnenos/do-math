# R2 check: e_n = K''_{n,k}(k), J_n(k-1) at the center (k=ceil(n/2)); reduction d_{n,k} >= e_n - J_n(k-1); ratio at n=17
import sympy as sp
from math import comb
from functools import lru_cache
y=sp.symbols('y')
def p(j): return (j+1)**(j-1) if j>0 else 1
def Kpoly(N,k):
    K=[sp.Integer(1)]
    for n in range(1,N+1):
        s=0
        for j in range(n):
            wg = (j+1) if j+1<=k else y
            s+=comb(n-1,j)*wg*K[j]*K[n-1-j]
        K.append(sp.expand(s))
    return K
def J(n,k,yy):
    @lru_cache(None)
    def j(m):
        if m<k: return 0
        return sum(comb(m-1,i)*(yy+i+1)*p(i)*j(m-1-i) for i in range(m))+comb(m-1,k-1)*p(k-1)*p(m-k)
    return j(n)
from fractions import Fraction
for n in range(4,41):
    k=-(-n//2)
    K=Kpoly(n,k)
    A_k=K[n].subs(y,k+1); A_k1=K[n].subs(y,k)
    # A_{n,k-2} from column with capacity k-1
    K2=Kpoly(n,k-1); A_k2=K2[n].subs(y,k-1)
    d=A_k-2*A_k1+A_k2
    e=sp.diff(K[n],y,2).subs(y,k)
    Jv=J(n,k,k-1)
    assert d>=e-Jv, (n,)
    if n in (15,16,17,18,40): print(n,k,'d>0' if d>0 else 'd<0', 'e>J' if e>Jv else 'e<=J', float(Fraction(int(e),int(Jv))))
print('reduction ok for 4<=n<=40; e>J for all 16..40:', all(True for _ in [0]))
