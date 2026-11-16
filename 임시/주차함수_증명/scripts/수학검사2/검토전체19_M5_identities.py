# exact checks of identities in chapter 6 with small sizes
from fractions import Fraction as Fr
from math import comb, factorial
import sys
NMAX=70
# A[n][l] via last-car recursion (thm 2-6)
A=[[Fr(0)]*(NMAX+2) for _ in range(NMAX+1)]
for l in range(NMAX+2): A[0][l]=Fr(1)
for n in range(1,NMAX+1):
    for l in range(NMAX+2):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
p=lambda n: Fr((n+1)**(n-1)) if n>0 else Fr(1)
def s(m,y):  # Pr_m(M<=y-1)=A[m][y-1]/p_m ; y>=1
    return A[m][y-1]/p(m) if y>=1 else Fr(0)
def c(m,Y): return (A[m][Y]-(A[m][Y-1] if Y>=1 else 0))/p(m)
def b(m,Y): return A[m][Y]-(A[m][Y-1] if Y>=1 else 0)
# Bor-based kernels as exact rationals times e-powers cancel: pi_n(m)=C(n,m) m^{m-1} p_{n-m}/p_n
def pi(n,m): return Fr(comb(n,m)*m**(m-1))*p(n-m)/p(n)
def pi0(n,y): # prob no tree of size > y, for n<=2y+1 unique
    return 1-sum(pi(n,m) for m in range(y+1,n+1))
ok=True
def chk(name,cond):
    global ok
    if not cond: ok=False; print("FAIL",name)
# (6.22) chain recursion: s_d(y)=s_{y+d-1}(y)
for y in range(1,12):
    for d in range(1,y+3):
        N=y+d-1
        if N>NMAX: continue
        lhs=s(N,y)
        rhs=(1-sum(pi(N,y+q) for q in range(1,d)))+sum(pi(N,y+q)*Fr(y,y+q)*s(y+q-1,y) for q in range(1,d))
        chk(f"6.22 y={y} d={d}", lhs==rhs)
    # d=y+3 correction
    d=y+3; N=y+d-1
    if N<=NMAX:
        t=Fr(comb(2*y+2,y+1)*(y+1)**(2*y),2)/p(2*y+2)
        rhs=(1-sum(pi(N,y+q) for q in range(1,d)))+sum(pi(N,y+q)*Fr(y,y+q)*s(y+q-1,y) for q in range(1,d))+t/(y+1)**2
        chk(f"6.22 corr y={y}", s(N,y)==rhs)
# (6.21) stay law for y>=50? too big for NMAX=70: test y=50,d<=20 needs N=y+d-1<=69 -> d<=20
y=50
for d in range(2,21):
    vs=s(y+d,y+1)-s(y+d-1,y); cc=c(y+d,y)
    chk(f"6.21 d={d}", (y+1)*vs<=(d-1)*cc)
# (6.31) diag inequality for d>=1, m>=max(2,2d-1), m<=NMAX-1
for d in range(1,15):
    for m in range(max(2,2*d-1),NMAX):
        w=m-d
        chk(f"6.31 d={d} m={m}", (w+2)*(m+1)*c(m+1,w+1)>w*(m+2)*c(m,w))
# (6.45) theorem-D (a): c_m(m-d) identity, 2d<=m+1
def P(m,j): return Fr(j)*pi(m,j)/m
for m in range(1,45):
    for d in range(1,(m+1)//2+1):
        lhs=c(m,m-d)
        first=sum(pi(m,J+1)/m*((s(m-J-1,m-d+1) if m-J-1>0 else 1)+(m-d)*(c(m-J-1,m-d) if m-J-1>m-d else 0)) for J in range(0,d))
        second=sum(P(m,Q)*(c(m-Q,m-d) if m-Q>m-d else 0) for Q in range(1,min(d-1,m-d)+1))
        chk(f"6.45 m={m} d={d}", lhs==first+second)
# path-shift (가): Bor(n) c_{n-1}(k-1) = sum wt_n ; use Bor(n)=e^{-n} n^{n-1}/n! -> multiply both sides by e^{n}: wt has prod Bor(gaps)*Bor(S_L): total exponent e^{-(n-S_L)} e^{-S_L}=e^{-n}, so ratios exact
def borx(n): return Fr(n**(n-1),factorial(n))  # Bor(n)*e^n
from itertools import combinations
for k in range(2,9):
    for n in range(k+1,2*k+1):
        lhs=borx(n)*c(n-1,k-1)
        tot=Fr(0)
        sizes=list(range(k,n))  # S in [k, n-1]
        for L in range(1,len(sizes)+1):
            for path in combinations(sizes[::-1],L):  # decreasing
                S=list(path); S0=[n]+S
                wt=Fr(1)
                for i in range(L): wt*=borx(S0[i]-S0[i+1])
                wt*=borx(S[-1])*pi0(S[-1]-1,k-1)
                pr=Fr(1)
                for Sj in S: pr*=Sj
                wt*=Fr(k**L-(k-1)**L)/pr
                tot+=wt
        chk(f"path-shift k={k} n={n}", lhs==tot)
# (6.32)/(6.29) pair-rearrange: varphi_flat = Ppair - Upsilon
def x(t,k): return ((k+1)*b(t-1,k)-(k-1)*b(t-1,k-1))/Fr(t**(t-1)) if t>=k+1 else None
for k in range(2,20):
    phi=k*sum(x(t,k) for t in range(k+1,2*k+2))
    Pp=k*sum(Fr(k+1)*c(m+1,k)/(m+2)-Fr(k-1)*c(m,k-1)/(m+1) for m in range(k,2*k))
    Ups=Fr(k*(k-1))*b(2*k,k-1)/((2*k+1)*p(2*k))
    chk(f"6.29 k={k}", phi==Pp-Ups)
    # x_k(k) = -1/k
    chk(f"x_k(k) k={k}", Fr((k+1)*b(k-1,k)-(k-1)*b(k-1,k-1),k**(k-1))==Fr(-1,k))
# (6.41): V_k(k) = Bd + sum DD
for k in range(2,30):
    V=sum((k+1)*c(m,k)-(k-1)*c(m,k-1) for m in range(k,2*k+1))
    Bd=2-2*s(2*k+1,k+1)-(k-1)*(s(2*k+1,k+1)-s(2*k,k))-(k-1)*c(2*k,k-1)
    DD=lambda m,y:(y+2)*s(m+2,y+2)-2*(y+1)*s(m+1,y+1)+y*s(m,y)
    chk(f"6.41 k={k}", V==Bd+sum(DD(m,k-1) for m in range(k,2*k)))
# b_{m,m-1}=m^{m-2}
for m in range(2,40): chk(f"b_mm-1 {m}", b(m,m-1)==m**(m-2))
print("ALL OK" if ok else "SOME FAIL")
