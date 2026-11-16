# L12 검산: 마지막 차 재귀로 n<=80 열을 채워 b_{80,39..41}과 비·교차곱·분리자를 다시 센다. zeta32(C=2000) 구간도 다시 계산한다.
from math import comb
from fractions import Fraction
N=80
A=[[1]*N]
for n in range(1,N+1):
    w=[comb(n-1,j) for j in range(n)]
    row=[sum(w[j]*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n)) for l in range(n-1)]
    row+=[(n+1)**(n-1)]*(N-len(row))
    A.append(row)
b=lambda n,l: A[n][l]-(A[n][l-1] if l>0 else 0)
first=None; fails=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1): fails.append((n,l))
print("failures n<=80:",fails)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print(b39);print(b40);print(b41)
print("b39<b40<b41:",b39<b40<b41, " b39*b41-b40^2>0:", b39*b41-b40**2>0, "digits", len(str(b39*b41-b40**2)))
print("25000*b40<25928*b39:",25000*b40<25928*b39, " 25928*b40<25000*b41:",25928*b40<25000*b41)
from decimal import Decimal, getcontext; getcontext().prec=30
print("ratios", Decimal(b40)/Decimal(b39), Decimal(b41)/Decimal(b40))
# zeta32 at C=2000
from mpmath import mp, mpf
mp.dps=40
C=2000
S=sum(mpf(j)**mpf(-1.5) for j in range(1,C))
lo=S+2*mpf(C)**mpf(-0.5)+mpf(C)**mpf(-1.5)/2
hi=S+2*(mpf(C)-mpf('0.5'))**mpf(-0.5)
print("zeta32 C=2000 lo,hi:",mp.nstr(lo,14),mp.nstr(hi,14))
# coarser: sum_{j<=C} + 2(C+1)^{-1/2}
S2=S+mpf(C)**mpf(-1.5)
print("coarse lower:",mp.nstr(S2+2*(mpf(C)+1)**mpf(-0.5),12), "coarse upper:", mp.nstr(S2+2*(mpf(C)+mpf('0.5'))**mpf(-0.5),12))
