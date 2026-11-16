# T12: test the generating-function recipe of D.exact-n20000 (ㄱ):
#  T_k = sum_{j<=k} j^{j-1} x^j/j!, G = exp(T_k), Q = sum_{j<k} p_j x^j/j!, H' = k Q H + k (G - Q), E = G/(1-H)
#  claim: [x^n] E = A_{n,k-1}/n!  (column k).  Test H(0)=0 against exact last-car recursion.
from fractions import Fraction as F
from math import comb, factorial
N=40
def exact_A(l):
    A=[1]+[0]*N
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
def mul(a,b):
    c=[F(0)]*(N+1)
    for i,x in enumerate(a):
        if x==0: continue
        for j in range(N+1-i):
            c[i+j]+=x*b[j]
    return c
def exp_series(a):  # a[0]=0
    e=[F(0)]*(N+1); e[0]=F(1)
    # e' = a' e
    for n in range(1,N+1):
        e[n]=sum(F(j)*a[j]*e[n-j] for j in range(1,n+1))/n
    return e
def inv(a):
    b=[F(0)]*(N+1); b[0]=1/a[0]
    for n in range(1,N+1):
        b[n]=-sum(a[j]*b[n-j] for j in range(1,n+1))/a[0]
    return b
p=lambda m: (m+1)**(m-1) if m>=1 else 1
for k in (2,3,5,8):
    T=[F(0)]*(N+1)
    for j in range(1,k+1): T[j]=F(j**(j-1),factorial(j))
    G=exp_series(T)
    Q=[F(0)]*(N+1)
    for j in range(0,k): Q[j]=F(p(j),factorial(j))
    for H0 in (F(0),):
        H=[F(0)]*(N+1); H[0]=H0
        # H' = k Q H + k (G-Q):  (n+1) H[n+1] = k*sum_{i} Q[i] H[n-i] + k (G[n]-Q[n])
        for n in range(0,N):
            H[n+1]=(k*sum(Q[i]*H[n-i] for i in range(n+1)) + k*(G[n]-Q[n]))/(n+1)
        one_minus_H=[-h for h in H]; one_minus_H[0]+=1
        E=mul(G,inv(one_minus_H))
        A=exact_A(k-1)
        ok=all(E[n]==F(A[n],factorial(n)) for n in range(N+1))
        bad=[n for n in range(N+1) if E[n]!=F(A[n],factorial(n))][:5]
        print(f"k={k} H(0)={H0}: E matches A_(n,k-1)/n! for n<={N}: {ok}; first mismatches {bad}")
