# H12 검산 2: 부록 D 3장 항목 (로그오목성 n=80, 누적 로그오목성 n=780)
import math, json, sys, time
from fractions import Fraction
t0=time.time()
# --- n<=80 rows via last-car recurrence, all columns
N=80
binom=[[math.comb(n,j) for j in range(n+1)] for n in range(N+1)]
A={}  # A[(n,l)]
for l in range(0,N):
    col=[1]
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=binom[n-1][j]*min(j+1,l+1)*col[j]*col[n-1-j]
        col.append(s)
    for n in range(N+1): A[(n,l)]=col[n]
def b(n,l):
    if l<0: return 0
    return A[(n,l)]-A[(n,l-1)] if l>=1 else A[(n,0)]
fails=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1), n
    assert A[(n,0)]==math.factorial(n)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1): fails.append((n,l))
print("row LC failures n<=80:", fails)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print("b39",b39); print("b40",b40); print("b41",b41)
print("b39*b41-b40^2>0:", b39*b41-b40**2>0, " b39<b40<b41:", b39<b40<b41)
print("ratios", float(Fraction(b40,b39)), float(Fraction(b41,b40)))
print("separator 25928/25000=",25928/25000, " b40*25000<25928*b39:", b40*25000<25928*b39, " 25928*b40<25000*b41:", 25928*b40<25000*b41)
print("time",time.time()-t0)
# --- cumulative LC near n=780 for columns 573..580
M=780
binomM=[math.comb(M-1,j) for j in range(M)]
cols={}
for l in range(573,581):
    col=[1]
    for n in range(1,M+1):
        s=0; nb=n-1
        for j in range(n):
            s+=math.comb(nb,j)*min(j+1,l+1)*col[j]*col[n-1-j]
        col.append(s)
    cols[l]=col
    print("col",l,"done",round(time.time()-t0,1),"s; digits A_780:",len(str(col[780])), "A_{l+1,l}==(l+2)^l:", col[l+1]==(l+2)**l if l+1<=M else None)
for n in (779,780):
    for l in range(574,580):
        if l-1 in cols and l+1 in cols:
            x=cols[l][n]**2-cols[l-1][n]*cols[l+1][n]
            rel=Fraction(x,cols[l][n]**2)
            print(n,l,"sign",(x>0)-(x<0),"rel %.4e"%float(rel))
print("time",time.time()-t0)
