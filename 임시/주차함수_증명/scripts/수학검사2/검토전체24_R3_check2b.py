from fractions import Fraction as Fr
from math import comb, factorial
def p(n): return 1 if n==0 else (n+1)**(n-1)
def tw(j): return Fr(1) if j==1 else Fr((j-1)**(j-1),factorial(j))
def ff(n,d):
    r=1
    for i in range(d): r*=n-i
    return r
def Gam(dmax,n,y):
    G=[Fr(1)]
    for d in range(1,dmax+1):
        G.append(comb(n,d)*p(d)+y*sum(comb(n-d+j,j)*p(j)*G[d-1-j] for j in range(d)))
    return G
for n in (14,20):
  for y in (Fr(7,2),Fr(3),Fr(14)):
    G=Gam(n-1,n,y); gn=[G[d]/ff(n,d) for d in range(n)]
    bad=[]
    for d in range(1,n):
        rhs=(1+y/(n-d+1))*gn[d-1]+sum(tw(j)*gn[d-j] for j in range(2,d+1))
        if rhs!=gn[d]: bad.append((d,float(gn[d]-rhs)))
    print(n,y,"recursion mismatches:",bad)
    # e^{-T} coefficient check
from math import factorial as f
# coefficients of e^{-T}: compute series T up to 15, exp(-T)
N=16
T=[Fr(0)]+[Fr(j**(j-1),f(j)) for j in range(1,N)]
E=[Fr(1)]+[Fr(0)]*(N-1)
# exp(-T): E' = -T' E
for m in range(1,N):
    E[m]=-sum(j*T[j]*E[m-j] for j in range(1,m+1))/m
print([E[j]==-tw(j) for j in range(1,N)])
