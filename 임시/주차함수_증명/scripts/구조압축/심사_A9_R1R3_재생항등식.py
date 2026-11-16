# A9 R1·R3·R2·N1 검산(정확 정수): 작은 k에서 명제 9.25(다)의 항등식이 모든 n>=2k+1에서 성립하는지,
# O_n=PAIR_n이 n<=3k-1에서만 성립하고 n=3k에서 R2의 항 (3k)!/(6(k!)^3) k^{3(k-2)}만큼 어긋나는지,
# 9.26의 A->p 치환이 n<=3k+2까지 유효한지, N1의 regen_n - A_{n,k-1}(*)(n) = sum L_{n,m} d_{m,k} (L>=0)를 확인한다.
from fractions import Fraction
from math import comb, factorial
import sys
sys.setrecursionlimit(10000)
A={}
def Aval(n,l):
    if n==0: return 1
    if l<0: return 0
    if (n,l) in A: return A[(n,l)]
    s=0
    for j in range(1,n+1):
        s+=comb(n-1,j-1)*min(j,l+1)*Aval(j-1,l)*Aval(n-j,l)
    A[(n,l)]=s; return s
def p(n): return (n+1)**(n-1) if n>=1 else 1
def b(n,l): return Aval(n,l)-Aval(n,l-1)
def N(l,t): return min(t,l+1)*Aval(t-1,l)
def bT(t,l): return N(l,t)-N(l-1,t)
def multinom(n,t1,t2): return factorial(n)//(factorial(t1)*factorial(t2)*factorial(n-t1-t2))
for k in (3,4,5):
    print("== k =",k)
    for n in range(2*k+1, 3*k+5):
        d=b(n,k)-b(n,k-1)
        Theta=comb(n,k)*k**(k-2)*Aval(n-k,k-1)
        delta=lambda t: bT(t,k)-bT(t,k-1)
        FL=sum(comb(n,t)*delta(t)*Aval(n-t,k-1) for t in range(k+1,2*k+2))
        Kr=sum(k*comb(n,m+1)*Aval(n-m-1,k-1)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        BVA=sum(comb(n,t)*Aval(n-t,k-1)*(b(t-1,k)+b(t-1,k-1)) for t in range(2*k+2,n+1))
        O=d-sum(comb(n,t)*delta(t)*Aval(n-t,k-1) for t in range(k,n+1))
        ident = (d == O-Theta+FL+Kr+BVA)
        PAIR=Fraction(1,2)*sum(multinom(n,t1,t2)*(bT(t1,k)*bT(t2,k)+bT(t1,k-1)*bT(t2,k-1))*p(n-t1-t2) for t1 in range(1,n) for t2 in range(1,n-t1+1))
        ga = all(delta(t)==k*(b(t-1,k)-b(t-1,k-1))+b(t-1,k)+b(t-1,k-1) for t in range(k+2,n+1))
        subst = all(Aval(n-t,k-1)==p(n-t) for t in range(2*k+2,n+1))
        regen = d - Kr
        KDp = sum((k+n-m)*comb(n-1,m)*p(n-1-m)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        Lsum = sum(Fraction(1)*(1+(n-m-1)*(1-Fraction(k,m+1)))*comb(n-1,m)*Aval(n-m-1,k-1)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        n1 = (regen - (d-KDp) == Lsum)
        R2term = Fraction(factorial(3*k),6*factorial(k)**3)*k**(3*(k-2))
        tag = ("  [n=3k: PAIR-O = %s, R2 항 = %s]"%(PAIR-O, R2term)) if n==3*k else ""
        print(f" n={n:3d} (n-3k={n-3*k:+d}) d={d:>14d} 항등식(다)={ident} (가)={ga} O>=0={O>=0} O==PAIR={O==PAIR} A=p치환={subst} N1={n1} O_n-PAIR_n={O-PAIR}{tag}")
