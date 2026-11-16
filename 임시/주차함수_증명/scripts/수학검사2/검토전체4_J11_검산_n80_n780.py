import sys, io, math
from fractions import Fraction
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from math import comb
def column(l, nmax):
    A=[0]*(nmax+1); A[0]=1
    for n in range(1,nmax+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
# n<=80 all columns
N=80
cols=[column(l,N) for l in range(N+1)]  # cols[l][n]
fails=[]
for n in range(1,N+1):
    b=[cols[l][n]-(cols[l-1][n] if l>=1 else 0) for l in range(n)]
    assert sum(b)==(n+1)**(n-1)
    for l in range(1,n-1):
        if b[l]*b[l]<b[l-1]*b[l+1]: fails.append((n,l))
print('LC failures n<=80:',fails)
b=[cols[l][80]-(cols[l-1][80] if l>=1 else 0) for l in range(80)]
b39,b40,b41=b[39],b[40],b[41]
print('digits',len(str(b40)))
print('b40^2 < b39*b41 :', b40*b40<b39*b41, ' diff positive:', b39*b41-b40*b40>0)
r=Fraction(b39*b41,b40*b40)
print('ratio b39*b41/b40^2 =',float(r))
sep=Fraction(25928,25000)
print('separator 25928/25000=',float(sep),' ratio>sep?',r>sep, ' 25000*b39*b41 > 25928*b40^2 ?',25000*b39*b41>25928*b40*b40)
# check direction: maybe separator compares b40^2/(b39*b41)
print('b40^2/(b39 b41)=',float(1/r))
# n=780 cumulative LC at l=574..579 ; also n=779
cols780={l:column(l,780) for l in range(573,581)}
for n in (779,780):
    for l in range(574,580):
        Al,Am,Ap=cols780[l][n],cols780[l-1][n],cols780[l+1][n]
        d=Al*Al-Am*Ap
        rel=Fraction(d,Al*Al)
        print(n,l,'viol' if d<0 else 'ok', '%.4e'%float(rel))
print('digits A_780,575:',len(str(cols780[575][780])))
