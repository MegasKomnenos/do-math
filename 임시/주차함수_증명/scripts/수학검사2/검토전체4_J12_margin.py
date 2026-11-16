# J12: 상대 여유의 정규화 비교 — (13,6), (241,120), (1001,500)에서 d/b_{n,k-1}, d/A_{n,k-1}, d/(A_k+2A_{k-1}+A_{k-2})
import sys
from math import comb
from fractions import Fraction as F
sys.set_int_max_str_digits(0)
def column(ell,N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,ell+1)*A[j]*A[n-1-j] for j in range(n))
    return A
for (n,k) in [(13,6),(241,120),(1001,500)]:
    C={l:column(l,n) for l in (k-2,k-1,k)}
    Ak,Ak1,Ak2=C[k][n],C[k-1][n],C[k-2][n]
    d=Ak-2*Ak1+Ak2; b=Ak1-Ak2
    print((n,k),"d/b=%.4e"%float(F(d,b)),"d/A_{k-1}=%.4e"%float(F(d,Ak1)),"d/(A_k+2A_{k-1}+A_{k-2})=%.4e"%float(F(d,Ak+2*Ak1+Ak2)), "b/A=%.3e"%float(F(b,Ak1)))
