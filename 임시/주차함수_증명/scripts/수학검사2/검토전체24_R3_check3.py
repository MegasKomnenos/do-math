# R3 check 3: exact rows n<=N (theorem 5.1 structure, witness bound), and (G)_d at boundary points of theorem 5.5.
import sys, time
from math import comb, factorial
from fractions import Fraction as Fr
N=int(sys.argv[1]) if len(sys.argv)>1 else 260
def p(n): return 1 if n==0 else (n+1)**(n-1)
t0=time.time()
binom=[[comb(n,j) for j in range(n+1)] for n in range(N+1)]
# A[k][n] = A_{n,k-1}
A=[None]*(N+2)
A[0]=[1]+[0]*N
for k in range(1,N+1):
    col=[1]
    for n in range(1,N+1):
        if n<=k: col.append(p(n)); continue
        s=0; bn=binom[n-1]
        for j in range(n):
            s+=bn[j]*min(j+1,k)*col[j]*col[n-1-j]
        col.append(s)
    A[k]=col
print("columns done",time.time()-t0)
def row(n): return [A[l+1][n]-A[l][n] for l in range(n)]
ok=True; broken=[]; wmin=(9,0); wmax=(-9,0); wmin2=(9,0); wmax2=(-9,0)
import mpmath as mp
mp.mp.dps=30
for n in range(1,N+1):
    b=row(n); kn=(n+1)//2
    assert sum(b)==p(n)
    # unimodal
    lst=max(range(n),key=lambda i:(b[i],-i))
    if any(b[i]>b[i+1] for i in range(lst)) or any(b[i]<b[i+1] for i in range(lst,n-1)): ok=False; print("not unimodal",n)
    if n>=2 and not all(b[i]<b[i+1] for i in range(kn-1)): broken.append(n)
    if n>=4 and not b[1]>=(n-1)*factorial(n)//2: ok=False; print("b1 bound FAIL",n)
    if n>=16 and not b[kn-1]<b[kn]: ok=False; print("middle FAIL",n)
    if 2<=n<=15 and not b[kn]-b[kn-1]<0: print("note: d_{n,k_n}>=0 at n=",n)
    if n>=5:
        first=-(-(n-1)//2)
        seen_dec=False
        for l in range(first,n-2):
            if b[l]<=b[l+1]:
                if seen_dec: ok=False; print("excluded after dec",n,l)
            else:
                seen_dec=True
                if not (b[l+1]**2>b[l]*b[l+2] and b[l]+b[l+2]<2*b[l+1]): ok=False; print("QR strict FAIL",n,l)
        if any(b[l]==b[l+1] for l in range(first,n-1)): print("tie in right half",n)
    if n>=50:
        v=n+1-lst-mp.mpf('0.59963')*mp.mpf(n+1)**(mp.mpf(2)/3)-mp.mpf('1.24847')*mp.mpf(n+1)**(mp.mpf(1)/3)
        if v<wmin[0]: wmin=(v,n)
        if v>wmax[0]: wmax=(v,n)
print("chain b0<..<b_{kn-1} broken exactly at",broken)
print("witness offset range n in [50,%d]:"%N, wmin, wmax)
print("rows OK" if ok else "rows FAIL")
# (G)_d at boundary points of theorem 5.5
def Gam(dmax,n,y):
    G=[1]
    for d in range(1,dmax+1):
        G.append(comb(n,d)*p(d)+y*sum(comb(n-d+j,j)*p(j)*G[d-1-j] for j in range(d)))
    return G
def checkG(r,k):
    n=k+r
    Gs={y:Gam(r,n,y) for y in range(k-2,k+4)}
    hg=lambda d,y: y*Gs[y][d]
    sd=lambda d,y: hg(d,y+1)-2*hg(d,y)+hg(d,y-1)
    worst=None
    for d in range(1,r):
        lhs=p(k)*Gs[k+2][r-1]*sd(d,k); rhs=p(k-1)*Gs[k-1][r]*sd(d,k+1)
        q=Fr(lhs,rhs)
        if worst is None or q<worst[0]: worst=(q,d)
    return float(worst[0]),worst[1]
for (r,k) in [(64,1024),(65,int(65**1.5+8*65)+1),(100,1800),(2,19999),(10,19991),(60,19941),(170,19831),(171,int(171**1.5+8*171)+1)]:
    t=time.time(); w=checkG(r,k)
    print("(G)_d min ratio lhs/rhs at r=%d,k=%d (n=%d):"%(r,k,k+r),w,"time %.1f"%(time.time()-t))
