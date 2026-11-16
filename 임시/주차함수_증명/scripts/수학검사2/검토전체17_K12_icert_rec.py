# K12: D.central-gap-integer의 네 재귀(식 줄)를 정확 유리수로 구현해
#  (1) 𝔄_n·n!s^n == A_{n,k-1}(마지막 차 재귀), (2) 𝔷_n·n!s^n == e_n = 2·E2 (전수 주차, n<=7),
#  (3) 𝔧_n·n!s^n == J_n(k-1) (순열 정의식, n<=7), (4) d_{n,k} >= e_n - J_n(k-1), (5) e_17/J_17(8) 비
import itertools
from fractions import Fraction as F
from math import comb, factorial
S=2918732888; s=F(S,2**30)
def p(m): return (m+1)**(m-1) if m>=1 else 1
def Acol(l,N):
    A=[1]*(N+1)
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
def four(k):
    N=2*k
    r_=[F(p(i),factorial(i)*s**i) for i in range(N+1)]
    A=[None]*(N+1); d=[None]*(N+1); z=[None]*(N+1); j=[None]*(N+1)
    for i in range(k+1): A[i]=r_[i]; d[i]=F(0); z[i]=F(0)
    for i in range(k): j[i]=F(0)
    j[k]=r_[k-1]/(s*k)
    for n in range(k+1,N+1):
        r=n-k
        A[n]=(sum((k+i+1)*r_[i]*A[n-1-i] for i in range(0,r-1))+sum(min(i+1,k)*r_[i]*r_[n-1-i] for i in range(r-1,k+1)))/(s*n)
        d[n]=(sum((k+i+1)*r_[i]*d[n-1-i] for i in range(0,r-1))+sum(r_[i]*A[n-1-i] for i in range(0,r)))/(s*n)
        z[n]=(sum((k+i+1)*r_[i]*z[n-1-i] for i in range(0,r-1))+2*sum(r_[i]*d[n-1-i] for i in range(0,r-1)))/(s*n)
        j[n]=(sum((k+i)*r_[i]*j[n-1-i] for i in range(0,r))+r_[k-1]*r_[n-k])/(s*n)
    un=lambda v,n: v*factorial(n)*s**n
    return {n:(un(A[n],n),un(d[n],n),un(z[n],n),un(j[n],n)) for n in range(k+1,N+1)}
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        m=0
        for jj in range(1,i):
            if sig[jj-1]>sig[i-1]: m=jj
        h.append(i-m)
    return h
def J_brute(n,k):
    tot=0
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); H=sum(1 for x in h if x==k); Z=sum(1 for x in h if x>k)
        pr=1
        for x in h:
            if x<k: pr*=x
        if H>0: tot+=H*k**(H-1)*(k-1)**Z*pr
    return tot
def e_brute(n,k):
    cnt=0; bk=0; bk1=0
    for pref in itertools.product(range(1,n+1),repeat=n):
        occ=[0]*(n+2); disp=[]; ok=True
        for car,a in enumerate(pref,1):
            t=a
            while t<=n and occ[t]: t+=1
            if t>n: ok=False;break
            occ[t]=1; disp.append(t-a)
        if not ok: continue
        M=max(disp)
        if M==k:
            bk+=1
            if disp.count(k)==2: cnt+=1
        elif M==k-1: bk1+=1
    return 2*cnt, bk-bk1
for k in (3,4):
    res=four(k)
    for n in range(k+1,2*k+1):
        A,d,z,j=res[n]
        Aexact=Acol(k-1,n)[n]
        line=f"k={k} n={n}: A ok={A==Aexact}"
        if n<=7:
            e,dd=e_brute(n,k); Jb=J_brute(n,k)
            line+=f"  e_n ok={z==e} (e={e})  J ok={j==Jb} (J={Jb})  d_nk={dd}  e-J={e-Jb}  d>=e-J:{dd>=e-Jb}"
        print(line)
# k=9: n=17,18 ratio and the exact A check
res=four(9)
for n in (17,18):
    A,d,z,j=res[n]
    print(f"k=9 n={n}: A ok={A==Acol(8,n)[n]}  e/J = {float(z/j):.8f}  e-J>0: {z>j}")
# also n=16 (k=8) and n=15 (k=8)
res=four(8)
for n in (15,16):
    A,d,z,j=res[n]; print(f"k=8 n={n}: e/J={float(z/j):.8f}  e>J: {z>j}")
