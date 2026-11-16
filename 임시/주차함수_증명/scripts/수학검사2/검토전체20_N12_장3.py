# N12 검산: D.logconcavity-failure-n80 세 정수·비·분리자, D.zeta-constants의 성긴 방법 하단
from math import comb
from fractions import Fraction
import sys
N=80
A={}  # A[(n,l)]
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        if l>=n-1:
            A[(n,l)]=(n+1)**(n-1)
        else:
            s=0
            for j in range(n):
                s+=comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)]
            A[(n,l)]=s
def b(n,l): return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print("b39",b39); print("b40",b40); print("b41",b41)
print("b39*b41-b40^2>0:", b39*b41-b40**2>0)
print("increasing:", b39<b40<b41)
print("25000*b40<25928*b39:",25000*b40<25928*b39, " 25928*b40<25000*b41:",25928*b40<25000*b41)
from decimal import Decimal,getcontext; getcontext().prec=30
print("ratios", Decimal(b40)/Decimal(b39), Decimal(b41)/Decimal(b40))
# first failure scan
fails=[(n,l) for n in range(1,N+1) for l in range(1,n-1) if b(n,l)**2<b(n,l-1)*b(n,l+1)]
print("failures n<=80:",fails)
# zeta coarse method lower end at C=2000
from mpmath import mp,mpf
mp.dps=30
C=2000
S=sum(mpf(j)**mpf(-1.5) for j in range(1,C+1))
print("coarse lower C=2000:", S+2*mpf(C+1)**mpf(-0.5), " coarse upper:", S+2*mpf(C+0.5)**mpf(-0.5))
S2=sum(mpf(j)**mpf(-1.5) for j in range(1,C))
print("trap lower:", S2+2*mpf(C)**mpf(-0.5)+mpf(C)**mpf(-1.5)/2, " mid upper:", S2+2*(mpf(C)-mpf(0.5))**mpf(-0.5))
