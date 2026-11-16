# T12: last-car recursion, n<=80, check D.logconcavity-failure-n80 numbers
from math import comb
from fractions import Fraction
N=80
A={}  # A[(n,l)]
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)]
        A[(n,l)]=s
def b(n,l):
    return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
fails=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(0,n))==(n+1)**(n-1)
    assert A[(n,0)]==__import__('math').factorial(n)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1): fails.append((n,l))
print("fails:",fails)
b39,b40,b41=b(80,39),b(80,40),b(80,41)
print(b39);print(b40);print(b41)
print("b39*b41-b40^2>0:", b39*b41-b40**2>0)
print("ratios:", Fraction(b40,b39)*1.0, Fraction(b41,b40)*1.0)
print("sep 25928/25000:", b40*25000 < 25928*b39, b41*25000 > 25928*b40)
print("b39<b40<b41:", b39<b40<b41)
