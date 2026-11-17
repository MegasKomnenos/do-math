# R1 검산: 1장 표와 수치, 2장 항등식의 작은 n 전수 대조
import itertools, math
from fractions import Fraction
from math import comb, factorial

def park(a):
    n=len(a); occ=[0]*(n+2); disp=[]
    for i,x in enumerate(a):
        p=x
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=i+1; disp.append(p-x)
    return disp, occ[1:n+1]

def p(n): return 1 if n==0 else (n+1)**(n-1)

# exact A via last-car recursion
def Atab(N):
    A={}
    for l in range(-1,N+2):
        A[(0,l)]=1 if l>=0 else 0
    for l in range(-1,N+2):
        if l<0:
            for n in range(1,N+1): A[(n,l)]=0
            continue
        for n in range(1,N+1):
            A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
    return A
N=40
A=Atab(N)
def b(n,l):
    if l<0: return 0
    return A[(n,l)]-A[(n,l-1)]
# brute force n<=7
for n in range(1,8):
    cnt=[0]*n; tot=0
    for a in itertools.product(range(1,n+1),repeat=n):
        r=park(a)
        if r is None: continue
        tot+=1; cnt[max(r[0])]+=1
    assert tot==p(n)
    assert cnt==[b(n,l) for l in range(n)],(n,cnt)
print("brute n<=7 ok")
table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],6:[720,3963,4594,3688,2546,1296],
7:[5040,42253,62145,57398,46142,32359,16807],8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
sums={1:1,2:3,3:16,4:125,5:1296,6:16807,7:262144,8:4782969,9:100000000,10:2357947691}
for n in table:
    row=[b(n,l) for l in range(n)]
    assert row==table[n],(n,row)
    assert sum(row)==p(n)==sums[n]
print("table n<=10 ok")
def witness(row):
    m=len(row)-1
    for ls in range(m+1):
        if all(row[i]<=row[i+1] for i in range(ls)) and all(row[i]>=row[i+1] for i in range(ls,m)): return ls
    return None
print("min witnesses", {n:witness([b(n,l) for l in range(n)]) for n in range(1,11)})
# middle comparison sign for n=2..40
kn=lambda n:(n+1)//2
print("d_{n,k_n} sign:", [(n, (b(n,kn(n))-b(n,kn(n)-1))>0) for n in range(2,22)])
# log-concavity for n<=40
for n in range(1,N+1):
    row=[b(n,l) for l in range(n)]
    bad=[l for l in range(1,n-1) if row[l]**2<row[l-1]*row[l+1]]
    if bad: print("logconcavity fails",n,bad)
print("p small",[p(i) for i in range(5)])
# 추가: 2<=n<=15 에서 d_{n,k_n}<0 (엄격), n=16..40 에서 >0; 표의 유도 수
print("strict neg 2..15:", all(b(n,kn(n))-b(n,kn(n)-1)<0 for n in range(2,16)), " pos 16..40:", all(b(n,kn(n))-b(n,kn(n)-1)>0 for n in range(16,41)))
import math
print("6667:",min(k for k in range(1,10000) if 3*k>=20001),"6668:",min(k for k in range(1,10000) if 3*k-1>=20001),"25001:",math.ceil((50001+1)/2),"8065:",min(k for k in range(1,20000) if 20001-2*k<=0.48*k),"140^2+280=",140*140+280,"141^2+282=",141*141+282)
# 마지막 항 b_{n,n-1}=p_{n-1}
print("last term = p_{n-1}:", all(b(n,n-1)==p(n-1) for n in range(1,41)))
