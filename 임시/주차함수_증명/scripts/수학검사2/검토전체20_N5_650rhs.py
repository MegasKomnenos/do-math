from mpmath import mp, mpf, exp, e, factorial
mp.dps=30
def Bor(n): n=mpf(n); return exp(-n)*n**(n-1)/factorial(n)
def Ren(n): return n*Bor(n)
k=mpf(3131)
for d in (5,6,12,13):
    m=k+d
    rhs=2*(1+sum(e*Ren(r+1)+60*(r+1)/m for r in range(1,d)))
    lhs=(k-1)*(e*Ren(d+1)-60*(d+1)/m)
    print(d, mp.nstr(lhs,9), mp.nstr(rhs,9))
