from fractions import Fraction as Fr
from math import comb, factorial, exp, gamma
import mpmath as mp
mp.mp.dps=30
print("s=S/2^30 =", mp.mpf(2918732888)/2**30, " e=", mp.e)
a0=mp.quad(lambda w: mp.exp(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.exp(-w**3/3),[0,mp.inf])
print("a0",a0,"a1",a1)
print("sum7 G=1/16:",176+2304+118+935+533+455+243," G=1/8:",round(183.51+2303.07+203.57+983.74+920.70+454.86+418.83,2))
print("495594511/240250000=",Fr(495594511,240250000),float(Fr(495594511,240250000)))
print("margin 5.642*1.6809*0.39893-0.0163-3.554 =",5.642*1.6809*0.39893-0.0163-3.554)
print("k^5 e^{-k/520} k=30000:",30000**5*exp(-30000/520))
print("46sqrt2-12 =",46*2**0.5-12, " -5468.28/100 =",46*2**0.5-12-54.6828)
# exact rows via last-car recursion, n<=N
N=260
p=[(n+1)**(n-1) if n>0 else 1 for n in range(N+1)]
C=[[comb(m,j) for j in range(m+1)] for m in range(N)]
def column(l):
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1):
        if n-1<=l: A[n]=p[n]; continue
        s=0
        for j in range(n):
            s+=C[n-1][j]*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
cols=[column(l) for l in range(N)]
def b(n,l): return (cols[l][n] if l>=0 else 0)-(cols[l-1][n] if l>=1 else 0)
import math
neg=[n for n in range(2,61) if b(n,math.ceil(n/2))-b(n,math.ceil(n/2)-1)<0]
print("d_{n,k_n}<0 for n in 2..60:",neg)
ok=all(all(b(n,j)>=b(n,j+1) for j in range(math.ceil(n/2),n-1)) for n in range(2,16))
print("2<=n<=15 right half nonincreasing from k_n:",ok)
cross=[n for n in range(5,N+1) if not (b(n,math.ceil(n/2))<b(n,math.ceil(n/2)+1))]
print("crossing b_{n,k_n}<b_{n,k_n+1} FALSE for n in 5..%d:"%N,cross)
# Q_L for 3<=n<=15
bad=[]
for n in range(3,16):
    for l in range(0,n-2):
        if 2*l<=n-2 and b(n,l)>b(n,l+1) and not (b(n,l+1)**2>=b(n,l)*b(n,l+2)): bad.append((n,l))
print("Q_L failures 3..15:",bad)
# count decreasing levels and strict unimodality n<=N
dec=sum(1 for n in range(1,N+1) for l in range(0,n-1) if b(n,l)>b(n,l+1))
print("decreasing levels n<=%d:"%N,dec)
ties=[(n,l) for n in range(1,N+1) for l in range(0,n-1) if b(n,l)==b(n,l+1)]
print("ties:",ties[:5])
