# R12: n=2k+1 근처에서 b_{n,k-1}/A_{n,k-1} 과 d/A, d/b 의 크기 (정확 정수; 작은 k)
from math import comb
from fractions import Fraction as F
def A_col(l, N):
    A=[1]
    for n in range(1,N+1):
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
for k in (20,40,80):
    n=2*k+1
    a2=A_col(k-2,n)[n]; a1=A_col(k-1,n)[n]; a0=A_col(k,n)[n]
    b_km1=a1-a2; b_k=a0-a1; d=b_k-b_km1
    print(k,n,'b_{n,k-1}/A_{n,k-1}=%.3e'%float(F(b_km1,a1)),'d/A_{n,k-1}=%.3e'%float(F(d,a1)),'d/b_{n,k-1}=%.3e'%float(F(d,b_km1)))
