# N12: chapter 3 appendix D items recheck (log-concavity n=80; cumulative lc at n=779/780 columns 573..580)
import sys,io,math,time
from fractions import Fraction
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
t0=time.time()
def column(l,N):
    # A_{m,l} for m=0..N via last-car recurrence
    A=[1]
    binom=[[1]]
    for m in range(1,N+1):
        row=[1]*(m)  # binom(m-1,j)
        for j in range(1,m-1): row[j]=binom[-1][j-1]+binom[-1][j]
        if m>1: row[m-1]=1
        binom.append(row)
        s=0
        for j in range(m):
            s+=row[j]*min(j+1,l+1)*A[j]*A[m-1-j]
        A.append(s)
    return A
# part 1: n<=80 all columns, check row lc
N=80
cols=[column(l,N) for l in range(0,N)]
viol=[]
for n in range(1,N+1):
    b=[cols[0][n]]+[cols[l][n]-cols[l-1][n] for l in range(1,n)]
    assert sum(b)==(n+1)**(n-1) and cols[0][n]==math.factorial(n)
    for l in range(1,n-1):
        if b[l]**2<b[l-1]*b[l+1]: viol.append((n,l))
print('row lc violations n<=80:',viol)
b=[cols[0][80]]+[cols[l][80]-cols[l-1][80] for l in range(1,80)]
print('b80_39',b[39]); print('b80_40',b[40]); print('b80_41',b[41])
print('b39*b41-b40^2>0:',b[39]*b[41]-b[40]**2>0)
print('ratios',float(Fraction(b[40],b[39])),float(Fraction(b[41],b[40])))
print('separator', b[40]*25000<25928*b[39], b[41]*25000>25928*b[40])
print('t',time.time()-t0)
# part 2: cumulative lc n=779,780 for columns 573..580
N=780
cols={l:column(l,N) for l in range(573,581)}
print('t cols',time.time()-t0)
for n in (779,780):
    for l in range(574,580):
        d=cols[l][n]**2-cols[l-1][n]*cols[l+1][n]
        rel=d/cols[l][n]**2
        print(n,l,'sign',(d>0)-(d<0),'rel %.4e'%rel, 'digits',len(str(cols[l][n])))
print('b80 from col: ', cols[573][80]-cols[573][80]==0)
print('t',time.time()-t0)
