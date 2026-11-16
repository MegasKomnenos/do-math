# N12 검산: D.newton-m170의 Nw_{r,d} 전진 차분 판정을 정의에서 새로 구현 (2<=r<=14)
from math import comb, factorial
from fractions import Fraction as Fr
import time
t0=time.time()
def p(m): return (m+1)**(m-1) if m>=1 else 1
def Gamma(d,y,n):
    G=[1]
    for dd in range(1,d+1):
        s=comb(n,dd)*p(dd)
        s+=y*sum(comb(n-dd+j,j)*p(j)*G[dd-1-j] for j in range(0,dd))
        G.append(s)
    return G[d]
def hg(d,y,n): return y*Gamma(d,y,n)
def sd(d,y,n): return hg(d,y+1,n)-2*hg(d,y,n)+hg(d,y-1,n)
e15=sum(Fr(1,factorial(j)) for j in range(16)); F15=factorial(15); E15=F15*e15; assert E15.denominator==1; E15=int(E15)
def Nw(r,d,nv):
    k=r+1+nv; n=k+r
    return 2*E15*k*k*(k+1)*Gamma(r-1,k+2,n)*sd(d,k,n)-F15*(2*k*k+5*k+4)*Gamma(r,k-1,n)*sd(d,k+1,n)
fails=[]; maxdeg_excess=0; count=0
for r in range(2,15):
    for d in range(1,r):
        count+=1
        vals=[Nw(r,d,nv) for nv in range(0,2*r+3)]
        diffs=[]; cur=vals[:]
        for i in range(0,2*r+3):
            diffs.append(cur[0]); cur=[cur[j+1]-cur[j] for j in range(len(cur)-1)]
        if not (diffs[0]>0 and all(x>=0 for x in diffs[1:])): fails.append((r,d))
        nz=max(i for i,x in enumerate(diffs) if x!=0)
        if nz>r+d+1: maxdeg_excess=max(maxdeg_excess,nz-(r+d+1))
        if nz>r+d+3: fails.append((r,d,'deg'))
print("polynomials checked:",count," failures:",fails," max degree over r+d+1:",maxdeg_excess)
# sanity: Gamma_d(y;n) total degree d; sd_d(y)>0 for y>=1
print("sd_d(y)>0 samples:",all(sd(d,y,n)>0 for n in range(5,15) for d in range(1,n) for y in range(1,8)))
print("elapsed %.1fs"%(time.time()-t0))
