# 검토전체18 L2: 3장 수치 재계산 (마지막 차 재귀로 A_{n,l})
from fractions import Fraction
from math import comb, isqrt
import sys, time

def column(l, nmax):
    A=[0]*(nmax+1); A[0]=1
    for n in range(1,nmax+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A

out=[]
# 1.3절 표 n<=10
cols={l:column(l,10) for l in range(-1,11)}
for l in cols:
    if l==-1: cols[l]=[0]*11
for n in range(1,11):
    row=[cols[l][n]-cols[l-1][n] for l in range(n)]
    pn=(n+1)**(n-1)
    # witness(es)
    mx=max(row); w=[i for i,v in enumerate(row) if v==mx]
    out.append(f"n={n} row={row} sum_ok={sum(row)==pn} witnesses={w} ceil(n/2)={-(-n//2)}")
# n=80, l=39..41
t=time.time()
c={l:column(l,80) for l in (38,39,40,41)}
b={l:c[l][80]-c[l-1][80] for l in (39,40,41)}
out.append(f"b80: {b[39]}\n{b[40]}\n{b[41]}")
out.append(f"b39<b40<b41: {b[39]<b[40]<b[41]}; b40^2<b39*b41: {b[40]**2<b[39]*b[41]}")
out.append(f"ratios {Fraction(b[40],b[39])*1.0:.11f} {Fraction(b[41],b[40])*1.0:.11f}; separator 25928/25000: {b[40]*25000<25928*b[39]} {25928*b[40]<25000*b[41]}")
out.append(f"time n80 {time.time()-t:.1f}s")
# E_n omega_n for n<=5
for n in range(1,6):
    pn=(n+1)**(n-1)
    s=Fraction(0)
    for j in range(1,n//2+1):
        pj=(n-j+1)**(n-j-1) if n-j>0 else 1
        s+=Fraction(comb(n,j)*j**j*pj,pn)
    out.append(f"E_{n} omega = {s}  sqrt(n)={n**0.5:.3f}")
# J=8 numerics
lam=Fraction(751,1000)
t1=lam**8; s1=sum(i*lam**(i-1) for i in range(1,9)); s2=sum((i-1)*lam**(i-1) for i in range(1,9))
out.append(f"lam^8={float(t1):.6f} sum_i i lam^(i-1)={float(s1):.5f} sum (i-1)lam^(i-1)={float(s2):.5f}; /31={float(s1/31):.5f} /1000={float(s2/1000):.5f}; total<{0.1012+0.3628+0.0077}")
# 9n^2-48n-32 at n=6, lambda bound
out.append(f"9*36-48*6-32={9*36-48*6-32}; max over n>=1000 of ceil(3n/4)/n - 3/4 = {max(Fraction(-(-3*n//4),n)-Fraction(3,4) for n in range(1000,1100))}")
open(sys.argv[1],'w',encoding='utf-8').write("\n".join(out))
