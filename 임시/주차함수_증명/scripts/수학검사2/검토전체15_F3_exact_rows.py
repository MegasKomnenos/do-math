# F3: exact rows n<=NMAX via last-car recurrence (Thm 2-6); checks for 5.1 claims and tail theorem consequences
import sys, math, time
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 300
t0=time.time()
binom=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for n in range(NMAX+1):
    binom[n][0]=1
    for j in range(1,n+1): binom[n][j]=binom[n-1][j-1]+(binom[n-1][j] if j<=n-1 else 0)
# A[l][n] for l in 0..NMAX-1 ; A_{n,l}
A=[]
for l in range(NMAX):
    col=[1]*(NMAX+1)
    for n in range(1,NMAX+1):
        s=0
        for j in range(1,n+1):
            s+=min(j,l+1)*binom[n-1][j-1]*col[j-1]*col[n-j]
        col[n]=s
    A.append(col)
print("rows computed in",round(time.time()-t0,1),"s")
def b(n,l):
    if l<0 or l>n-1: return 0
    return A[l][n]-(A[l-1][n] if l>=1 else 0)
def p(n): return (n+1)**(n-1)
# sanity: sum of row = p_n
assert all(sum(b(n,l) for l in range(n))==p(n) for n in range(1,NMAX+1))
# (i) unimodality
def unimodal(n):
    row=[b(n,l) for l in range(n)]
    i=0
    while i+1<n and row[i]<=row[i+1]: i+=1
    while i+1<n and row[i]>=row[i+1]: i+=1
    return i==n-1
print("all rows n<=%d unimodal:"%NMAX, all(unimodal(n) for n in range(1,NMAX+1)))
# (ii) chain b0<...<b_{k_n-1} breaks exactly at n in {5,7,9,11}
def kn(n): return -(-n//2)
breaks=[n for n in range(2,NMAX+1) if not all(b(n,l)<b(n,l+1) for l in range(0,kn(n)-1))]
print("chain strict-increase breaks at:",breaks,"(claim {5,7,9,11})")
# (iii) middle increase b_{k_n-1}<b_{k_n} for n>=16, and d_{n,k_n}<0 for 2<=n<=15
mid_ok=all(b(n,kn(n)-1)<b(n,kn(n)) for n in range(16,NMAX+1)); mid_neg=[n for n in range(2,16) if not b(n,kn(n)-1)>b(n,kn(n))]
print("middle increase n>=16:",mid_ok,"; n in 2..15 with d_{n,k_n}>=0:",mid_neg)
# (iv) Q_R fourth piece: positions (n-1)/2<=l<=n-3: premise excluded or strict dec+strict concave+strict logconcave; excluded ones before decreases
ok=True; first_dec={}
for n in range(5,NMAX+1):
    lo=-(-(n-1)//2); seen_dec=False
    for l in range(lo,n-2):
        if b(n,l)<=b(n,l+1):
            if seen_dec: ok=False; print("excluded after decrease",n,l)
        else:
            seen_dec=True
            if not (b(n,l+1)**2>b(n,l)*b(n,l+2) and b(n,l)+b(n,l+2)<2*b(n,l+1)): ok=False; print("not strict concave/logconcave",n,l)
print("fourth-piece structure 5..%d:"%NMAX,ok)
# (v) adjacent pairs in right half strict (5-2 (다))
print("right-half adjacent pairs strict:", all(b(n,l)!=b(n,l+1) for n in range(5,NMAX+1) for l in range(-(-(n-1)//2),n-1)))
# (vi) witness bound 50<=n<=NMAX: n+1-l* - 0.59963 (n+1)^{2/3} - 1.24847 (n+1)^{1/3} in [0.889,1.987]
offs=[]
for n in range(50,NMAX+1):
    row=[b(n,l) for l in range(n)]; m=max(row); ls=row.index(m)
    offs.append((n+1-ls-0.59963*(n+1)**(2/3)-1.24847*(n+1)**(1/3),n))
print("witness offset range 50..%d: min %.6f (n=%d) max %.6f (n=%d)"%(NMAX,min(offs)[0],min(offs)[1],max(offs)[0],max(offs)[1]))
# (vii) Theorem 5-4 consequence: S_{n,k}>0 for 2<=r<=170, k>=r+1, n=k+r<=NMAX ; Gamma via recurrence
def Gamma_list(dmax,yv,n):
    G=[1]
    pj=[ (j+1)**(j-1) if j>=1 else 1 for j in range(dmax+1)]
    for dd in range(1,dmax+1):
        G.append(binom[n][dd]*pj[dd]+yv*sum(binom[n-dd+j][j]*pj[j]*G[dd-1-j] for j in range(dd)))
    return G
okS=True; cnt=0
for n in range(5,NMAX+1):
    for k in range(3,n):
        r=n-k
        if not (2<=r<=170 and k>=r+1): continue
        Gm=Gamma_list(r,k-1,n)[r]*p(k-1); Gp=Gamma_list(r-1,k+2,n)[r-1]*p(k)
        d1=b(n,k)-b(n,k-1); d2=b(n,k+1)-b(n,k)
        S=Gp*d1-Gm*d2; cnt+=1
        if S<=0: okS=False; print("S<=0 at",n,k)
        # Gamma^- == K(k-1)-A_{n,k-2}? cannot without K; check Gamma^- > 0 and Gamma^- >= -d1 when d1<0 (since d1 = 2E - Gamma^-)
        if d1<0 and Gm < -d1: okS=False; print("Gamma^- < -d_{n,k}",n,k)
print("S_{n,k}>0 for all right positions with r<=170 (count %d):"%cnt, okS)
# (viii) moving-tail (아) sanity: D>=2, n>=20 D^{3/2}: b_{n,n-D}>...>b_{n,n-1}
ok=True
for D in range(2,7):
    for n in range(math.ceil(20*D**1.5),NMAX+1):
        if not all(b(n,n-j)>b(n,n-j+1) for j in range(D,1,-1)): ok=False
print("moving-tail (아) for D<=6:",ok)
