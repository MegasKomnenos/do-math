from fractions import Fraction as Q
from math import comb, factorial
N=14
def p(n): return (n+1)**(n-1) if n>=1 else 1
def mul(a,b): return [sum(a[i]*b[n-i] for i in range(n+1)) for n in range(N+1)]
def expser(a):
    assert a[0]==0
    e=[Q(1)]+[Q(0)]*N
    for n in range(1,N+1):
        e[n]=sum(i*a[i]*e[n-i] for i in range(1,n+1))/n
    return e
def inv(a):
    b=[Q(1)/a[0]]+[Q(0)]*N
    for n in range(1,N+1): b[n]=-sum(a[i]*b[n-i] for i in range(1,n+1))/a[0]
    return b
def col(l):
    A=[1]+[0]*N
    for n in range(1,N+1): A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
ok=True
for y in range(1,7):
    T=[Q(0)]+[Q(j**(j-1),factorial(j)) if j<=y else Q(0) for j in range(1,N+1)]
    G=expser(T)
    Qs=[Q(p(j),factorial(j)) if j<y else Q(0) for j in range(N+1)]
    # H' = y Q H + y (G-Q), H(0)=0
    H=[Q(0)]*(N+1)
    for n in range(0,N):
        rhs=y*sum(Qs[i]*H[n-i] for i in range(n+1))+y*(G[n]-Qs[n])
        H[n+1]=rhs/(n+1)
    oneH=[Q(1)-H[0]]+[-h for h in H[1:]]
    E=mul(G,inv(oneH))
    A=col(y-1)
    good=all(E[n]==Q(A[n],factorial(n)) for n in range(N+1))
    ok&=good
    if not good: print("mismatch y",y,[n for n in range(N+1) if E[n]!=Q(A[n],factorial(n))])
print("E_k=G_k/(1-H_k) equals sum A_{n,y-1}x^n/n! for y=1..6, n<=14:",ok)
# overflow recursion (ㄹ)
ok2=True
for k in range(1,8):
    A=col(k-1)
    Ac=[p(n)-A[n] for n in range(N+1)]
    for n in range(k+1,min(2*k+1,N)+1):
        rhs=sum(comb(n-1,i)*(n-k-i)*p(i)*p(n-1-i) for i in range(0,n-k))+sum(comb(n-1,i)*(k+i+1)*p(i)*Ac[n-1-i] for i in range(0,n-k-1))
        if rhs!=Ac[n]: ok2=False; print("mismatch",k,n)
    # n=2k+2 should fail?
    n=2*k+2
    if n<=N:
        rhs=sum(comb(n-1,i)*(n-k-i)*p(i)*p(n-1-i) for i in range(0,n-k))+sum(comb(n-1,i)*(k+i+1)*p(i)*Ac[n-1-i] for i in range(0,n-k-1))
        print("k",k,"n=2k+2 equal?",rhs==Ac[n])
print("overflow recursion ok for k+1<=n<=2k+1:",ok2)
