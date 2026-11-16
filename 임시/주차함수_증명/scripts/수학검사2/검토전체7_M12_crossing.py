# D.crossing-small-n 재계산: 넘는 수 A^c 재귀로 5<=n<=1000의 b_{n,k_n}<b_{n,k_n+1} 판정
import sys, math, time
from math import comb
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 1000
p=[1]+[(n+1)**(n-1) for n in range(1,NMAX+2)]
t0=time.time()
def Ac_column(l, nmax):
    # A^c_{n,l} for n<=min(nmax, 2l+4)
    top=min(nmax,2*l+4)
    Ac=[0]*(top+1)
    for n in range(l+2, top+1):
        s=0
        for j in range(l+1, n):
            s+=comb(n-1,j)*(j-l)*p[j]*p[n-1-j]
        for i in range(l+2, n):
            s+=Ac[i]*comb(n-1,i)*p[n-1-i]*((l+1)+min(n-i,l+1))
        Ac[n]=s
    return Ac
cols={}
need=set()
for n in range(5,NMAX+1):
    kn=math.ceil(n/2)
    for l in (kn-1,kn,kn+1): need.add(l)
for l in sorted(need):
    cols[l]=Ac_column(l,NMAX)
false=[]
for n in range(5,NMAX+1):
    kn=math.ceil(n/2)
    b1=cols[kn-1][n]-cols[kn][n]
    b2=cols[kn][n]-cols[kn+1][n]
    if not b1<b2: false.append(n)
print("false n:",false, "time",round(time.time()-t0,1))
