# R2 check: lemma 4:e-integral (4.1) e_n/n! = [x^n] Phi(T(x)) for n<=2k+1 ; proposition 4:old-4-6 Green form = J_n(k-1) for n<=2k
import sympy as sp
from math import comb, factorial
from functools import lru_cache
Y,Z,y=sp.symbols('Y Z y')
def p(j): return (j+1)**(j-1) if j>0 else 1
def Kpoly(N,k):
    K=[sp.Integer(1)]
    for n in range(1,N+1):
        s=0
        for j in range(n):
            wg=(j+1) if j+1<=k else y
            s+=comb(n-1,j)*wg*K[j]*K[n-1-j]
        K.append(sp.expand(s))
    return K
def J(n,k,yy):
    @lru_cache(None)
    def j(m):
        if m<k: return 0
        return sum(comb(m-1,i)*(yy+i+1)*p(i)*j(m-1-i) for i in range(m))+comb(m-1,k-1)*p(k-1)*p(m-k)
    return j(n)
def ser(expr,var,N):
    return sp.series(expr,var,0,N+1).removeO()
for k in (2,3):
    N=2*k+2
    V=lambda t:(1-t)**2/2
    Bt=1-sum(sp.exp(-j*Z)*(j*Z)**(j-1)/sp.factorial(j) for j in range(1,k+1))
    JJ=V(Z)-V(Y)
    integrand=(1-Z)**2*Bt*sp.exp(k*JJ)*(2*JJ+k*JJ**2)
    # expand integrand as polynomial in Z up to order N (Y symbolic), integrate 0..Y
    integ=sp.expand(ser(integrand,Z,N))
    inner=sp.integrate(integ,(Z,0,Y))
    Phi=sp.exp(Y)*inner
    K=Kpoly(N,k)
    for n in range(1,N+1):
        coef=sp.series(Phi*(1-Y)*sp.exp(n*Y),Y,0,n+1).removeO().coeff(Y,n)
        e=sp.diff(K[n],y,2).subs(y,k)
        print('k',k,'n',n,'e_n',e,' n![x^n]Phi(T)=',sp.nsimplify(coef*factorial(n)), 'equal' if sp.simplify(coef*factorial(n)-e)==0 else 'DIFF')
    # proposition 4-6: p_{k-1} n! [x^n] e^T e^{(k-1)Gr} int_0^x e^{-(k-1)Gr} w^{k-1}/(k-1)! dw, in Y variable:
    G=sp.exp(Y)*sp.exp(-(k-1)*V(Y))*sp.integrate(sp.expand(ser((1-Z)*Z**(k-1)*sp.exp(k*(1-Z)+(k-1)*V(Z)),Z,N)),(Z,0,Y))*sp.exp(-k)*k**(k-1)/sp.factorial(k)
    for n in range(k,N+1):
        coef=sp.series(G*(1-Y)*sp.exp(n*Y),Y,0,n+1).removeO().coeff(Y,n)
        print('   J: n',n,'J_n(k-1)',J(n,k,k-1) if n<=2*k else '(n>2k) true J recursion n/a','Green',sp.nsimplify(coef*factorial(n)))
