# Q12: D.exact-n20000 (ㄱ)의 세 급수(T_k, G_k, H_k, E_k) 식이 열 k의 지수 생성함수를 주는지 작은 n에서 검사
from fractions import Fraction as Fr
from math import comb, factorial
N=18
A=[[0]*(N+1) for _ in range(N+1)]
for l in range(N+1): A[0][l]=1
for n in range(1,N+1):
    for l in range(N+1):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
p=[A[n][N] for n in range(N+1)]
def mul(a,b):
    c=[Fr(0)]*(N+1)
    for i,x in enumerate(a):
        if x==0: continue
        for j in range(N+1-i): c[i+j]+=x*b[j]
    return c
def exp_series(t):  # t[0]=0
    g=[Fr(0)]*(N+1); g[0]=Fr(1)
    for n in range(1,N+1):
        g[n]=sum(Fr(j)*t[j]*g[n-j] for j in range(1,n+1))/n
    return g
ok=True
for k in range(1,8):
    T=[Fr(0)]*(N+1)
    for j in range(1,k+1): T[j]=Fr(j**(j-1),factorial(j))
    G=exp_series(T)
    Q=[Fr(p[j],factorial(j)) if j<k else Fr(0) for j in range(N+1)]
    # H' = k Q H + k (G-Q), H(0)=0
    H=[Fr(0)]*(N+1)
    QH=[Fr(0)]*(N+1)
    for n in range(0,N):
        # coefficient of x^n in RHS
        rhs=k*sum(Q[i]*H[n-i] for i in range(n+1))+k*(G[n]-Q[n])
        H[n+1]=rhs/(n+1)
    # E = G/(1-H)
    inv=[Fr(0)]*(N+1); inv[0]=Fr(1)
    for n in range(1,N+1):
        inv[n]=sum(H[i]*inv[n-i] for i in range(1,n+1))
    E=mul(G,inv)
    for n in range(N+1):
        if E[n]!=Fr(A[n][k-1],factorial(n)): ok=False; print("mismatch k",k,"n",n,E[n],Fr(A[n][k-1],factorial(n))); break
print("EGF three-series recurrence matches A_{n,k-1}/n! for k<=7, n<=18:",ok)
