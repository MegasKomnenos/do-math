from math import comb
from fractions import Fraction
N=780
C=[[comb(n,j) for j in range(n+1)] for n in range(N)]
def column(l):
    A=[1]+[0]*N
    for n in range(1,N+1):
        s=0; half=(n-1)//2
        for j in range(half+1):
            t=C[n-1][j]*min(j+1,l+1)*A[j]*A[n-1-j]
            if j!=n-1-j:
                t+=C[n-1][n-1-j]*min(n-j,l+1)*A[n-1-j]*A[j]
            s+=t
        A[n]=s
    assert A[l+1]==(l+2)**l
    return A
cols={l:column(l) for l in range(573,581)}
for n in (779,780):
    for l in range(574,580):
        d=cols[l][n]**2-cols[l-1][n]*cols[l+1][n]
        print(n,l, "neg" if d<0 else "pos", float(Fraction(d,cols[l][n]**2)))
