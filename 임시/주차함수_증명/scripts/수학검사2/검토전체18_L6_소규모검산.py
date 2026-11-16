# L6 검산: 7장 A의 여러 진술을 n<=8에서 결과 순열 전수 열거로 확인
from fractions import Fraction as Fr
from itertools import permutations
from math import factorial, log
import sys
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        j=i
        while j>0 and s[j-1]<s[i]: j-=1
        # nearest larger to left
        m=0
        for t in range(i-1,-1,-1):
            if s[t]>s[i]: m=t+1; break
        h.append(i+1-m)
    return h
def A(n,l):  # cumulative count via cor 2-4
    if n==0: return 1
    if l<0: return 0
    tot=0
    for s in permutations(range(1,n+1)):
        p=1
        for hi in caps(s): p*=min(hi,l+1)
        tot+=p
    return tot
bad=[]
for n in range(1,8):
    perms=list(permutations(range(1,n+1)))
    H=[caps(s) for s in perms]
    for k in range(2,n+1):
        w=[1]*len(perms)
        for idx,h in enumerate(H):
            for hi in h: w[idx]*=min(hi,k)
        Ak1=sum(w)
        Z=[sum(1 for hi in h if hi>k) for h in H]; Hk=[sum(1 for hi in h if hi==k) for h in H]
        EZ=Fr(sum(w[i]*Z[i] for i in range(len(w))),Ak1)
        EH=Fr(sum(w[i]*Hk[i] for i in range(len(w))),Ak1)
        EZZ=Fr(sum(w[i]*Z[i]*(Z[i]-1) for i in range(len(w))),Ak1)
        # Thm 6-6
        if EZ < Fr(n-k,k+1): bad.append(("6-6",n,k))
        # factorial moment (n>=2k+1)
        if n>=2*k+1:
            m=Fr(n-k,k+1)
            if EZZ < m*(m-1): bad.append(("fm",n,k))
        # Thm 6-10 (n>=k)
        xk=Fr(k,k+1)**(k-1)
        if k*EH > xk*n: bad.append(("6-10",n,k))
        if n==k and k*EH != xk*n: bad.append(("6-10eq",n,k))
        # Thm 6-2 / 6-4
        Ak=A(n,k); Ak2=A(n,k-2); d=Ak-2*Ak1+Ak2
        Tnk=sum(w[i]*(Z[i]*(Z[i]-1)-k*Hk[i]) for i in range(len(w)))
        if d*k*k < Tnk: bad.append(("6-4",n,k))
        # Prop 6-7
        Rs=Ak/Ak1; Rf=Ak2/Ak1; ok=-2*log(1-1/k)/log(1+1/k)
        if not (Rf > (1-1/k)*Rs**(-ok)): bad.append(("6-7",n,k,Rf,(1-1/k)*Rs**(-ok)))
        # 2E2 identity: A E[Z(Z-1)]/k^2 == K''(k) = 2 E2
        # Prop 6-5: Conv - Kink = d, with Kink = A E[H]/k
        Kink=Fr(Ak1*EH,k)
        # Conv via integral: sum over sigma (prod_{h<=k} h) * [ int_0^1 (1-f) Z(Z-1) (k+f)^{Z-2} df ] + lower side
        # skip Conv (needs symbolic); check Kink<=... just report
print("bad:",bad)
# Thm 6-11 (가) check: E[H_k] = (n+1) a_{k-1} sum_j K_j a_{n+1-j}/a_n , small n,k
import sympy as sp
x=sp.symbols('x')
def Aegf(l,N):
    return sum(sp.Rational(A(n,l),factorial(n))*x**n for n in range(N+1))
for k in [2,3]:
    N=7
    p=lambda j:(j+1)**(j-1) if j>=1 else 1
    Q=sum((k-1-j)*p(j)*x**(j+1)/sp.factorial(j+1) for j in range(k-1))
    Qp=sp.diff(Q,x)
    # K coefficients via recursion
    Kc=[sp.Integer(0)]*(N+3)
    a0=lambda m:sp.Rational(p(m),factorial(m))
    for j in range(k+1,N+3):
        s=sum((k-m)*a0(m-1)*Kc[j-m] for m in range(1,k) if j-m>=0)
        Kc[j]=(s+(1 if j==k+1 else 0))/sp.Integer(j)
    a=[sp.Rational(A(n,k-1),factorial(n)) for n in range(N+2)]
    for n in range(1,N+1):
        perms=list(permutations(range(1,n+1)))
        num=0;den=0
        for s in perms:
            h=caps(s); w=1
            for hi in h: w*=min(hi,k)
            num+=w*sum(1 for hi in h if hi==k); den+=w
        lhs=sp.Rational(num,den)
        rhs=(n+1)*a[k-1]*sum(Kc[j]*a[n+1-j] for j in range(k+1,n+2))/a[n]
        if sp.simplify(lhs-rhs)!=0: print("6-11 mismatch",k,n,lhs,rhs)
print("6-11 checked k=2,3 n<=7")
