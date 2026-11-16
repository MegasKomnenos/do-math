# 부록 D.central-gap-integer 「식」의 네 재귀를 정확 유리수로 그대로 실행해, 기록 v_exact_small_out.json의 e_n, J_n(k-1)와 비교한다.
from fractions import Fraction as F
from math import factorial
import json
S=2918732888; s=F(S,2**30)
def p(i): return (i+1)**(i-1) if i>=1 else 1
d=json.load(open('C:/math/임시/주차함수_증명/원고_자료/rce3dc75/v_exact_small_out.json'))
for kk,v in d.items():
    k=int(kk); N=2*k
    r=[F(p(i),factorial(i))/s**i for i in range(N+1)]
    A=[None]*(N+1); D=[None]*(N+1); Z=[None]*(N+1); J=[None]*(N+1)
    for i in range(k+1): A[i]=r[i]; D[i]=F(0); Z[i]=F(0)
    for i in range(k): J[i]=F(0)
    J[k]=r[k-1]/(s*k)
    for n in range(k+1,N+1):
        rr=n-k
        A[n]=(sum((k+i+1)*r[i]*A[n-1-i] for i in range(0,rr-1))+sum(min(i+1,k)*r[i]*r[n-1-i] for i in range(rr-1,k+1)))/(s*n)
        D[n]=(sum((k+i+1)*r[i]*D[n-1-i] for i in range(0,rr-1))+sum(r[i]*A[n-1-i] for i in range(0,rr)))/(s*n)
        Z[n]=(sum((k+i+1)*r[i]*Z[n-1-i] for i in range(0,rr-1))+2*sum(r[i]*D[n-1-i] for i in range(0,rr-1)))/(s*n)
        J[n]=(sum((k+i)*r[i]*J[n-1-i] for i in range(0,rr))+r[k-1]*r[n-k])/(s*n)
    for nn,w in v.items():
        n=int(nn); norm=factorial(n)*s**n
        e=Z[n]*norm; j=J[n]*norm
        print(f"k={k} n={n}: e_rec={e} (int? {e.denominator==1}) e_rec==e_file {e==int(w['e'])};  J_rec={j} (int? {j.denominator==1}) J_rec==J_file {j==int(w['J'])}")
# A_{n,k-1} 도 마지막 차 재귀와 대조 (k=4, n=7,8)
from math import comb
def Acol(l,N):
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1): A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
k=4; N=8; r=[F(p(i),factorial(i))/s**i for i in range(N+1)]
A=[None]*(N+1)
for i in range(k+1): A[i]=r[i]
for n in range(k+1,N+1):
    rr=n-k
    A[n]=(sum((k+i+1)*r[i]*A[n-1-i] for i in range(0,rr-1))+sum(min(i+1,k)*r[i]*r[n-1-i] for i in range(rr-1,k+1)))/(s*n)
Ac=Acol(k-1,N)
print("A check k=4:", [A[n]*factorial(n)*s**n==Ac[n] for n in range(5,9)])
