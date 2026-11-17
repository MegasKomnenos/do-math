import sys, re
from math import comb
from fractions import Fraction
sys.set_int_max_str_digits(100000)
N=80
# A[l][n]
def col(l, N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
cols=[col(l,N) for l in range(N)]
def b(n,l): return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
fails=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
    assert cols[0][n]==__import__('math').factorial(n)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1): fails.append((n,l))
print("fails", fails)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
txt=open(r"C:\math\임시\주차함수_증명\장v2\부록D_장3.md",encoding="utf-8").read()
ints=re.findall(r"=(\d{100,})\$",txt)
print(len(ints), [int(x)==y for x,y in zip(ints,(b39,b40,b41))])
print(float(Fraction(b40,b39)), float(Fraction(b41,b40)))
from decimal import Decimal, getcontext
getcontext().prec=30
print(Decimal(b40)/Decimal(b39), Decimal(b41)/Decimal(b40))
print(b40*25000 < 25928*b39, 25928*b40 < 25000*b41, 25928/25000)
print(b39<b40<b41, b39*b41-b40*b40>0)
