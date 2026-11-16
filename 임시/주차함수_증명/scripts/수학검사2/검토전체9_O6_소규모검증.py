# O6: 7.1-7.2 진술의 소규모 전수 검증 (n<=7)
from itertools import permutations
from fractions import Fraction as F
from math import factorial, log
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and s[j]<s[i]: j-=1
        h.append(i-j)
    return h
def A(n,l):
    if n==0: return 1
    return sum(eval_prod(caps(s),l+1) for s in permutations(range(1,n+1)))
def eval_prod(h,c):
    p=1
    for x in h: p*=min(x,c)
    return p
ok=True
for n in range(1,8):
    for k in range(2,n+1):
        W=[(s,caps(s)) for s in permutations(range(1,n+1))]
        tot=sum(eval_prod(h,k) for s,h in W)
        EZ=F(sum(eval_prod(h,k)*sum(1 for x in h if x>k) for s,h in W),tot)
        EH=F(sum(eval_prod(h,k)*sum(1 for x in h if x==k) for s,h in W),tot)
        EZZ=F(sum(eval_prod(h,k)*(lambda z:z*(z-1))(sum(1 for x in h if x>k)) for s,h in W),tot)
        # old-6-6
        if EZ < F(n-k,k+1): ok=False; print("6-6 FAIL",n,k,EZ)
        # factorial moment
        m=F(n-k,k+1)
        if n>=2*k+1 and EZZ < m*(m-1): ok=False; print("fact FAIL",n,k)
        # old-6-10
        if n>=k and k*EH > F(k**(k-1),(k+1)**(k-1))*n: ok=False; print("6-10 FAIL",n,k,k*EH)
        if n==k and k*EH != F(k**(k-1),(k+1)**(k-1))*n: ok=False; print("6-10 eq FAIL",n,k)
        # old-6-2
        Ak,Ak1,Ak2=A(n,k),A(n,k-1),A(n,k-2)
        mu=F(Ak-2*Ak1+Ak2,Ak1)
        mu2=sum(F(eval_prod(h,k),tot)*((F(k+1,k))**sum(1 for x in h if x>k)+(F(k-1,k))**(sum(1 for x in h if x>=k))-2) for s,h in W)
        if mu!=mu2: ok=False; print("6-2 FAIL",n,k)
        # old-6-7
        R=F(Ak,Ak1); Z=F(Ak2,Ak1)
        ok_=-2*log(1-1/k)/log(1+1/k)
        if not (float(Z) > (1-1/k)*float(R)**(-ok_)): ok=False; print("6-7 FAIL",n,k)
        # 6-4: d >= T/k^2
        T=sum(eval_prod(h,k)*((lambda z,hh:z*(z-1)-k*hh)(sum(1 for x in h if x>k),sum(1 for x in h if x==k))) for s,h in W)
        if (Ak-2*Ak1+Ak2) < F(T,k*k): ok=False; print("6-4 FAIL",n,k)
print("all ok" if ok else "FAILURES")
# level-chain sanity: prime counts C_{n,n}=(n-1)^(n-1) for n<=6 by brute force
def is_pf(a):
    n=len(a); return all(sum(1 for x in a if x<=b)>=b for b in range(1,n+1))
def prime(a):
    n=len(a); return all(sum(1 for x in a if x<=b)!=b for b in range(1,n))
from itertools import product
for n in range(1,7):
    c=sum(1 for a in product(range(1,n+1),repeat=n) if is_pf(a) and prime(a))
    print("C_nn",n,c,(n-1)**(n-1))
