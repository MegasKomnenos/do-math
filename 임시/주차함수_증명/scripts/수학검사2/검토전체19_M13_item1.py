# M13 item D.column-certification-k500: verify the three recurrences for e^{(y)}_n against brute force.
from fractions import Fraction as F
from itertools import product
from math import factorial
def brute_A(nmax):
    # A[n][l] = # parking functions length n with max displacement <= l
    A={}
    for n in range(0,nmax+1):
        cnt={}
        if n==0:
            A[0]={l:1 for l in range(0,nmax+2)}; continue
        for pref in product(range(1,n+1),repeat=n):
            occ=[False]*(n+2); md=0; ok=True
            for p in pref:
                q=p
                while q<=n and occ[q]: q+=1
                if q>n: ok=False;break
                occ[q]=True; md=max(md,q-p)
            if ok: cnt[md]=cnt.get(md,0)+1
        A[n]={l:sum(v for m,v in cnt.items() if m<=l) for l in range(0,nmax+2)}
    return A
nmax=7
A=brute_A(nmax)
assert all(sum(1 for _ in []) == 0 for _ in [0])
print("p_n:", [A[n][nmax+1] for n in range(nmax+1)])
def pw(m): return F(m**(m-1)) if m>=1 else F(1)
def acirc(n): return F(1) if n==0 else F((n+1)**(n-1),factorial(n))  # p_n/n!
def three_rec(y,x,nmax):
    g=[F(0)]*(nmax+1); g[0]=F(1)
    for n in range(1,nmax+1):
        g[n]=sum(F(j)*F(j**(j-1),factorial(j))*x**j*g[n-j] for j in range(1,min(y,n)+1))/n
    h=[F(0)]*(nmax+1)
    for n in range(1,nmax+1):
        s=y*x*sum(acirc(j-1)*x**(j-1)*h[n-j] for j in range(1,min(y,n)+1))
        if n>=y+1: s+=y*x*g[n-1]
        h[n]=s/n
    e=[F(0)]*(nmax+1)
    for n in range(0,nmax+1):
        e[n]=g[n]+sum(h[j]*e[n-j] for j in range(1,n+1))
    return g,h,e
def lastcar(y,x,nmax):
    e=[F(0)]*(nmax+1); e[0]=F(1)
    for n in range(1,nmax+1):
        e[n]=x*sum(min(j+1,y)*e[j]*e[n-1-j] for j in range(0,n))/n
    return e
ok=True
for y in range(1,8):
    for x in [F(1),F(3,7)]:
        g,h,e=three_rec(y,x,nmax); e2=lastcar(y,x,nmax)
        for n in range(nmax+1):
            tgt=F(A[n][y-1])*x**n/factorial(n)
            if e[n]!=tgt or e2[n]!=tgt: ok=False; print("mismatch",y,x,n,e[n],e2[n],tgt)
        # g_n = acirc(n) x^n for n<=y
        for n in range(0,min(y,nmax)+1):
            if g[n]!=acirc(n)*x**n: ok=False; print("g mismatch",y,n)
print("all three recurrences and last-car recurrence match brute force, n<=7, y<=7:",ok)
