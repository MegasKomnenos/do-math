# s_m(y) = A_{m,y-1}/p_m via last-car recursion A_{m,l} = sum_j C(m-1,j-1) min(j,l+1) A_{j-1,l} A_{m-j,l}
from math import comb
from fractions import Fraction
import sys
def A_table(l, M):
    A=[1]*(M+1)
    for m in range(1,M+1):
        A[m]=sum(comb(m-1,j-1)*min(j,l+1)*A[j-1]*A[m-j] for j in range(1,m+1))
    return A
def p(m): return (m+1)**(m-1)
for k in [20,50,100,200]:
    n=2*k+1
    Akm1=A_table(k-1,n); Ak=A_table(k,n); Akm2=A_table(k-2,n)
    s=lambda m,y: Fraction({k-1:Akm1,k:Ak,k-2:Akm2}[y-1][m], p(m))
    br = (s(k+1,k)-s(k+1,k-1)) + s(k+1,k+1) - s(n,k) - s(n,k+1)
    print(k, "s_n(k)=%.4f s_n(k+1)=%.4f s_{k+1}(k+1)=%.4f c_{k+1}(k-1)=%.4f bracket(nu=1)=%.4f" % (s(n,k), s(n,k+1), s(k+1,k+1), s(k+1,k)-s(k+1,k-1), br))
    # for nu = 5, 20
    for nu in [5, 20]:
        n2=2*k+nu
        if n2<=n:
            pass
    sys.stdout.flush()
