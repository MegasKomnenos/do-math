# 검토 23차 R1: 2.7절 얼린 용량 다항식, 경계 다항식, 연쇄 해, 잔차의 차수 확인 (순열 열거 n<=8, sympy 급수)
import sys, itertools
import sympy as sp
from math import comb, factorial
sys.stdout.reconfigure(encoding='utf-8')
x,y,eta,z=sp.symbols('x y eta z')
NMAX=8
def p(n): return 1 if n==0 else (n+1)**(n-1)
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        zz=0
        for j in range(i-1,-1,-1):
            if sig[j]>sig[i]: zz=j+1;break
        h.append(i+1-zz)
    return h
K={}  # K[(n,k)] polynomial in eta,y
perms={n:[caps(s) for s in itertools.permutations(range(1,n+1))] for n in range(0,NMAX+1)}
def Kpoly(n,k):
    if (n,k) in K: return K[(n,k)]
    tot=0
    for h in perms[n]:
        term=1
        for hi in h:
            term*= hi if hi<k else (eta if hi==k else y)
        tot+=term
    K[(n,k)]=sp.expand(tot); return K[(n,k)]
def ser(expr,N=NMAX):
    return sp.series(expr,x,0,N+1).removeO()
def coeffs(expr,N=NMAX):
    e=sp.expand(expr)
    return [sp.expand(e.coeff(x,i)) for i in range(N+1)]
T=sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1,NMAX+2))
def trunc(e,N=NMAX):
    e=sp.expand(e)
    return sum(e.coeff(x,i)*x**i for i in range(N+1))
def pexp(f,N=NMAX):
    # exp of series with zero constant term
    res=1; term=1
    for i in range(1,N+1):
        term=trunc(term*f/i,N); res+=term
    return trunc(res,N)
eT=pexp(T)
assert all(coeffs(eT)[m]==sp.Rational(p(m),factorial(m)) for m in range(NMAX+1))
Gr=trunc(T-T**2/2)
assert trunc(sp.diff(Gr,x)-eT,NMAX-1)==0
for k in (1,2,3):
    Kk=sum(Kpoly(n,k)*x**n/sp.factorial(n) for n in range(NMAX+1))
    # two-variable closed form ODE: dK = y K^2 + d adj K
    adj=sum((t-y)*p(t-1)*x**t/sp.factorial(t) for t in range(1,k))+(eta-y)*p(k-1)*x**k/sp.factorial(k)
    lhs=sp.diff(Kk,x); rhs=trunc(y*Kk**2+sp.diff(adj,x)*Kk,NMAX-1)
    assert sp.expand(trunc(lhs,NMAX-1)-rhs)==0,k
    Ky=Kk.subs(eta,k)
    E=sum(sp.Rational(p(j),factorial(j))*x**j for j in range(k))
    Tle=sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1,k+1))
    Tgt=trunc(T-Tle)
    sm=trunc((1-T)*(eT-E))
    assert sp.expand(trunc(E+sm-eT*(1-Tgt)))==0
    eyG=pexp(y*Gr); emyG=pexp(-y*Gr)
    integ=sp.integrate(trunc(sm*emyG),x)
    Gst=trunc(E+sm+y*eT*eyG*integ)
    X=sp.expand(trunc(Ky-Gst))
    low=[i for i in range(NMAX+1) if sp.expand(X.coeff(x,i))!=0]
    print('k',k,'residual lowest degree',low[:1],'(claim >=',2*k+2,')')
    assert all(i>=2*k+2 for i in low)
    # J
    J=sp.diff(Kk,eta).subs(eta,k)
    Y=trunc(p(k-1)*eT*eyG*sp.integrate(trunc(emyG*x**(k-1)/sp.factorial(k-1)),x))
    D=sp.expand(trunc(Y-J))
    lowD=[i for i in range(NMAX+1) if sp.expand(D.coeff(x,i))!=0]
    print('   J-egf first disagreement degree',lowD[:1],'(claim >=',2*k+1,')')
    assert all(i>=2*k+1 for i in lowD)
    # B_{n,k-1} and J_n(k-1), Xi
    for n in range(1,NMAX+1):
        Kn=Kpoly(n,k)
        B=Kn.subs({eta:k,y:k-1})-Kn.subs({eta:k-1,y:k-1})
        Jn=sp.diff(Kn,eta).subs({eta:k,y:k-1})
        assert B<=Jn
        if n<=2*k-1: assert B==Jn
        if n==2*k:
            assert Jn-B==comb(2*k-1,k-1)*p(k-1)**2,(n,k,Jn-B)
        # (ㄹ) J_n(y)<=p_{k-1}G for integer y in 0..k+1
        for yy in range(0,k+2):
            jn=sp.diff(Kn,eta).subs({eta:k,y:yy})
            g=sp.factorial(n)*Y.coeff(x,n).subs(y,yy)
            assert jn<=g,(n,k,yy)
            assert Kn.subs({eta:k,y:yy})<=p(n)
print('frozen checks ok')
