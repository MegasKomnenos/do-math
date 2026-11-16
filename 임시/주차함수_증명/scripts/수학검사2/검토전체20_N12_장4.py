# N12 검산: D.central-gap-integer의 네 재귀(A, K', K''=e_n, J_n(k-1))를 정의(순열 전수)와 대조하고,
# 정확 정수로 16<=n<=400에서 e_n > J_n(k-1)을 확인하며, n<=60의 정확한 행에서 (ㄴ)을 확인한다.
from math import comb, factorial
from itertools import permutations
from fractions import Fraction
import time
t0=time.time()
def p(m): return (m+1)**(m-1) if m>=1 else 1
def hvec(sig):
    n=len(sig); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)   # positions 1-based: h_i = i - (index of nearest larger to the left), 0 if none
    return h
def brute(n,k):
    A=e=J=0
    for sig in permutations(range(1,n+1)):
        h=hvec(sig)
        Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        small=1
        for x in h:
            if x<k: small*=x
        A+=small*(k**H)*(k**Z)
        e+=Z*(Z-1)*(k**(Z-2) if Z>=2 else 0)*small*(k**H)
        J+=H*(k**(H-1) if H>=1 else 0)*((k-1)**Z)*small
    return A,e,J
def recur(k,nmax):
    A={i:p(i) for i in range(0,k+1)}; D={i:0 for i in range(0,k+1)}; Zz={i:0 for i in range(0,k+1)}
    J={i:0 for i in range(0,k)}; J[k]=p(k-1)
    for n in range(k+1,nmax+1):
        r=n-k
        A[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*A[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*min(i+1,k)*p(i)*p(n-1-i) for i in range(r-1,k+1))
        D[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*D[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*p(i)*A[n-1-i] for i in range(0,r))
        Zz[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*Zz[n-1-i] for i in range(0,r-1))+2*sum(comb(n-1,i)*p(i)*D[n-1-i] for i in range(0,r-1))
        J[n]=sum(comb(n-1,i)*(k+i)*p(i)*J[n-1-i] for i in range(0,r))+comb(n-1,k-1)*p(k-1)*p(n-k)
    return A,Zz,J
# 1. 재귀 vs 전수 (k<n<=2k, n<=9)
bad=0; cnt=0
for k in range(1,5):
    A,Zz,J=recur(k,2*k)
    for n in range(k+1,min(2*k,9)+1):
        Ab,eb,Jb=brute(n,k); cnt+=1
        if (Ab,eb,Jb)!=(A[n],Zz[n],J[n]):
            bad+=1; print("MISMATCH k,n",k,n,(Ab,eb,Jb),(A[n],Zz[n],J[n]))
# k=5 n<=9 only
A,Zz,J=recur(5,10)
for n in range(6,10):
    Ab,eb,Jb=brute(n,5); cnt+=1
    if (Ab,eb,Jb)!=(A[n],Zz[n],J[n]): bad+=1; print("MISMATCH k=5 n",n)
print("recursion vs brute force: compared",cnt,"(n,k) pairs, mismatches",bad, " t=%.1fs"%(time.time()-t0))
# 2. 정확 정수로 e_n > J_n(k-1), 16<=n<=400
fails=[]; ratios={}
for k in range(1,201):
    A,Zz,J=recur(k,2*k)
    for n in (2*k-1,2*k):
        if n<2: continue
        if J[n]>0: ratios[n]=Fraction(Zz[n],J[n])
        if n>=16 and not Zz[n]>J[n]: fails.append(n)
print("e_n > J_n(k-1) failures in 16..400:",fails)
print("min ratio e_n/J_n(k-1) over 16<=n<=400: n=%d ratio=%.8f"%min(((n,float(r)) for n,r in ratios.items() if n>=16), key=lambda t:t[1]))
print("ratio n=17: %.8f ; n=16: %.8f ; n=15: %.6f n=14: %.6f"%(float(ratios[17]),float(ratios[16]),float(ratios[15]),float(ratios[14])))
# 3. (ㄴ) 정확한 행 n<=60 (마지막 차 재귀), k_n=ceil(n/2)
N=60
Afull={}
for l in range(0,N):
    Afull[(0,l)]=1
    for n in range(1,N+1):
        Afull[(n,l)]=(n+1)**(n-1) if l>=n-1 else sum(comb(n-1,j)*min(j+1,l+1)*Afull[(j,l)]*Afull[(n-1-j,l)] for j in range(n))
def b(n,l): return Afull[(n,l)]-(Afull[(n,l-1)] if l>=1 else 0)
neg=[]; nonmono=[]; pos=[]
for n in range(2,N+1):
    kn=(n+1)//2
    d=b(n,kn)-b(n,kn-1)
    if d<0:
        neg.append(n)
        if any(b(n,j)<b(n,j+1) for j in range(kn,n-1)): nonmono.append(n)
    elif d>0: pos.append(n)
    else: print("d=0 at n",n)
print("d_{n,k_n}<0 exactly for n in:",neg," right half non-increasing fails:",nonmono)
print("d>0 for all 16<=n<=60:", pos==list(range(16,N+1)))
# 4. e_n - J_n(k-1) <= d_{n,k_n} for n<=60 (따름정리 old-2-29)
viol=[]
for n in range(2,N+1):
    kn=(n+1)//2; A,Zz,J=recur(kn,2*kn)
    if not Zz[n]-J[n] <= b(n,kn)-b(n,kn-1): viol.append(n)
print("e_n-J_n(k-1) <= d_{n,k_n} violations n<=60:",viol)
print("s = 2918732888/2^30 =",2918732888/2**30)
print("elapsed %.1fs"%(time.time()-t0))
