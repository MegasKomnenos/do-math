# D.exact-n20000 (ㄱ) 식: E_k=G_k/(1-H_k), H_k'=k Q_k H_k + k(G_k-Q_k) 의 계수가 A_{n,k-1}/n! 인지 k=2,3,4, n<=9 대조
import sympy as sp
from math import comb, factorial
x=sp.symbols('x')
N=9
p=[1]+[(n+1)**(n-1) for n in range(1,N+2)]
def A_col(l):
    A=[1]
    for n in range(1,N+1):
        if l>=n-1: A.append(p[n]); continue
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
for k in (2,3,4):
    T=sum(sp.Integer(j)**(j-1)*x**j/sp.factorial(j) for j in range(1,k+1))
    G=sp.series(sp.exp(T),x,0,N+1).removeO()
    Q=sum(sp.Integer(p[j])*x**j/sp.factorial(j) for j in range(0,k))
    # solve H' = kQH + k(G-Q), H(0)=0 by power series
    h=[sp.Integer(0)]*(N+1)
    Gc=[G.coeff(x,i) for i in range(N+1)]; Qc=[Q.coeff(x,i) if i<k else 0 for i in range(N+1)]
    for n in range(0,N):
        # coefficient of x^n in RHS
        rhs=k*sum(Qc[i]*h[n-i] for i in range(n+1))+k*(Gc[n]-Qc[n])
        h[n+1]=rhs/(n+1)
    H=sum(h[i]*x**i for i in range(N+1))
    E=sp.series(G/(1-H),x,0,N+1).removeO()
    A=A_col(k-1)
    ok=all(sp.nsimplify(E.coeff(x,n))==sp.Rational(A[n],factorial(n)) for n in range(0,N+1))
    print("k",k,"E_k coefficients == A_{n,k-1}/n! for n<=9:",ok, [sp.nsimplify(E.coeff(x,n))*factorial(n) for n in range(0,6)], A[:6])
