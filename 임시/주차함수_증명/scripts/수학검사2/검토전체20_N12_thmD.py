# N12 검산: 정리 theorem-D (6.45)의 결손 갱신 항등식을 정수로 새로 구현해 마지막 차 재귀(m<=300)와 대조하고,
# 4<=m<=700, 1<=d<=floor(m^(2/3)/2)에서 비 q(m,d)=m b_{m,m-d}/(p_m Psi(d))의 최솟값·최댓값을 구한다.
from math import comb, factorial
from mpmath import mp, mpf, exp, floor
import time
t0=time.time()
def p(m): return (m+1)**(m-1) if m>=1 else 1
DMAX=41; M=700
b={}  # b[(m,d)] = b_{m,m-d} for 1<=d<=min(DMAX,(m+1)//2)
def bget(j,dd):  # b_{j,j-dd}; dd=0 -> c_j(j)=0
    if dd<=0: return 0
    return b[(j,dd)]
def Aget(j,l):  # A_{j,l} for j-1-l small: p_j - sum_{dd=1}^{j-1-l} b_{j,j-dd}
    return p(j)-sum(bget(j,dd) for dd in range(1,j-l))
for m in range(1,M+1):
    for d in range(1,min(DMAX,(m+1)//2)+1):
        l=m-d; s=0
        for J in range(0,d):
            j=m-J-1
            # s_j(l+1)=A_{j,l}/p_j ; c_j(l)=b_{j,l}/p_j with j-l = d-J-1
            Aj = Aget(j,l) if j>=1 else 1   # s_0 := 1
            cj = bget(j,j-l) if j>=1 else 0
            s+=comb(m,J+1)*(J+1)**J*(Aj+l*cj)
        for Q in range(1,min(d-1,m-d)+1):
            s+=Q*comb(m,Q)*Q**(Q-1)*bget(m-Q,(m-Q)-l)
        assert s%m==0, (m,d)
        b[(m,d)]=s//m
print("band recursion built to m=%d (%.0fs)"%(M,time.time()-t0))
# compare with last-car full table for m<=300
N=300; A={}
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        A[(n,l)]=(n+1)**(n-1) if l>=n-1 else sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
def bfull(n,l): return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
mism=[(m,d) for m in range(1,N+1) for d in range(1,min(DMAX,(m+1)//2)+1) if b[(m,d)]!=bfull(m,m-d)]
print("(6.45) vs last-car recursion, m<=300: pairs",sum(min(DMAX,(m+1)//2) for m in range(1,N+1))," mismatches",mism[:5])
mp.dps=50
def Psi(d): return sum(mpf(j)**j*exp(-j)/factorial(j) for j in range(1,d+1))
best_min=(None,10); best_max=(None,0); cnt=0
for m in range(4,M+1):
    dmax=int(floor(mpf(m)**(mpf(2)/3)/2))
    for d in range(1,dmax+1):
        cnt+=1
        q=mpf(m)*mpf(b[(m,d)])/(mpf(p(m))*Psi(d))
        if q<best_min[1]: best_min=((m,d),q)
        if q>best_max[1]: best_max=((m,d),q)
print("pairs",cnt," min q",best_min," max q",best_max)
q31=mpf(3)*mpf(b[(3,1)])/(mpf(p(3))*Psi(1)); print("q(3,1)=",q31)
print("in [1/2,3/2]:",best_min[1]>0.5 and best_max[1]<1.5, " in [0.856,1.392]:",best_min[1]>=0.856 and best_max[1]<=1.392)
print("elapsed %.0fs"%(time.time()-t0))
