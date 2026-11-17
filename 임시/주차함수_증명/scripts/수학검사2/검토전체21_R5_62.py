from mpmath import mp, mpf, sqrt, pi, e, log, exp
mp.dps=25
def B2(k):
    k=mpf(k)
    return (1-1/e)+(exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)",B2(43),"B2(2000)",B2(2000),"B2(4)",B2(4))
def g(x): return (x-1)*log(1+1/mpf(x))
for k in [2,3,5,43,2000]:
    print(k,"g",g(k),"lower",1-mpf(3)/(2*k)+1/(2*mpf(k)**2), g(k)>=1-mpf(3)/(2*k)+1/(2*mpf(k)**2))
# exact sum check of (6.16) at k=43
from mpmath import factorial
def Bor(n): n=mpf(n); return n**(n-1)*exp(-n)/factorial(n)
k=43; xk=(mpf(k)/(k+1))**(k-1); q=e*xk
S=sum(Bor(n)*q**n for n in range(2,k+2))
print("exact sum k=43:",S, "B2:",B2(43))
k=2000; xk=(mpf(k)/(k+1))**(k-1); q=e*xk
S=sum(Bor(n)*q**n for n in range(2,k+2))
print("exact sum k=2000:",S)
# bracket second term increasing in chi?
h=lambda c:(1+c+c**2)*(1-c)**(-mpf(1)/2)*(1+c)**(-mpf(3)/2)
print([h(mpf(c)) for c in ['0.0','0.2','0.4','0.6','0.8','0.9','0.99']])
