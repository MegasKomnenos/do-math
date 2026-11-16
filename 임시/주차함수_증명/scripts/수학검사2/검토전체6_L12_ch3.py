# L12 ch3 checks: log-concavity failure n=80; cumulative LC n=780 columns 573..580
import math, time, sys
from math import comb
def column(l, N):
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1):
        if l>=n-1: A[n]=(n+1)**(n-1); continue
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
t=time.time()
N=80
cols=[column(l,N) for l in range(0,N)]  # cols[l][n]=A_{n,l}
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
fails=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1): fails.append((n,l))
print("row LC fails n<=80:",fails)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print(b39);print(b40);print(b41)
print("b39*b41-b40^2>0:", b39*b41-b40**2>0, "ratios", b40/b39, b41/b40, "sep", b40*25000<25928*b39, 25928*b40<25000*b41)
print("time",time.time()-t)
# cumulative LC near n=780
t=time.time()
cols2={l:column(l,780) for l in range(573,581)}
print("col time",time.time()-t)
A=lambda n,l: cols2[l][n]
print("digits A_780_575:", len(str(A(780,575))), "A_780_580:",len(str(A(780,580))), "p780 digits", len(str(781**779)))
for n in (779,780):
    for l in range(574,580):
        num=A(n,l)**2-A(n,l-1)*A(n,l+1)
        print(n,l, "sign", (num>0)-(num<0), "rel %.4e"%(num/A(n,l)**2))
