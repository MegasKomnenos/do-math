# K13: check the three recurrences and the scaled last-car recurrence of D.column-certification-k500
from fractions import Fraction as F
from math import factorial
from itertools import product
def pf_count_maxdisp(n, l):
    cnt=0
    for pref in product(range(1,n+1), repeat=n):
        spots=[False]*(n+1); ok=True; md=0
        for p in pref:
            q=p
            while q<=n and spots[q]: q+=1
            if q>n: ok=False;break
            spots[q]=True; md=max(md,q-p)
        if ok and md<=l: cnt+=1
    return cnt
def three_rec(y,N):
    a=[F(1)]+[F((n+1)**(n-1), factorial(n)) for n in range(1,N+1)]
    g=[F(0)]*(N+1); g[0]=F(1)
    for n in range(1,N+1):
        g[n]=sum(F(j*j**(j-1),factorial(j))*g[n-j] for j in range(1,min(y,n)+1))/n
    h=[F(0)]*(N+1)
    for n in range(1,N+1):
        s=y*sum(a[j-1]*h[n-j] for j in range(1,min(y,n)+1))
        if n>=y+1: s+=y*g[n-1]
        h[n]=s/n
    e=[F(0)]*(N+1); e[0]=F(1)
    for n in range(1,N+1):
        e[n]=g[n]+sum(h[j]*e[n-j] for j in range(1,n+1))
    return e
def lastcar(y,N):
    e=[F(0)]*(N+1); e[0]=F(1)
    for n in range(1,N+1):
        e[n]=sum(min(j+1,y)*e[j]*e[n-1-j] for j in range(n))/n
    return e
N=6
for y in (2,3,4,5):
    ex=[F(pf_count_maxdisp(n,y-1),factorial(n)) for n in range(N+1)]
    print(y, 'three==brute', three_rec(y,N)==ex, 'lastcar==brute', lastcar(y,N)==ex)
for y in (3,7,10):
    print(y, 'three==lastcar N=25', three_rec(y,25)==lastcar(y,25))
