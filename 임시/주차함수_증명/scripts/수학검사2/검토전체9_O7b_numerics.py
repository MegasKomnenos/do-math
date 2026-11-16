# 7.6-7.7절 수치 재계산 (O7b)
from math import *
# theorem-W (나)
k=3131
print("k^(1/6)", k**(1/6), "k^(1/3)", k**(1/3), "sqrt k", sqrt(k))
D2 = 0.08329*sqrt(k)-2-42.14/k
print("D_k(2) at 3131:", D2, " 0.33316/4=",0.33316/4)
R = 0.33316*(k**0.5-2*k**(1/6)+k**(-1/6)) - 1.0005*k**(1/3) - 1.0145
print("right-end bound at 3131:", R)
t=k**(1/6)
print("deriv wrt k^(1/6):", 0.33316*(3*k**(1/3)-2-k**(-1/3)) - 2.001*t)
print("(1+1/k)^(4/3)", (1+1/k)**(4/3), "1+2/k", 1+2/k)
print("0.14*2.38*0.9999=",0.14*2.38*0.9999, " 0.14*301=",0.14*301)
n=6263
i_n = n*log(n/(n+1))+1
print("i_n at 6263:", i_n, "e^-i_n", exp(-i_n), "bound 1/(2(n+1))+1/(6n(n+1))", 1/(2*(n+1))+1/(6*n*(n+1)))
# explicit-bounds
print("0.8/sqrt(301)", 0.8/sqrt(301), "1-that", 1-0.8/sqrt(301))
print("(2pi)^-1/2", (2*pi)**-0.5, " 0.9538/0.398943", 0.9538/0.398943, " 2/sqrt(2pi)", 2/sqrt(2*pi))
# n_PD
for kk in [2001,3131]:
    nPD = ceil((kk+1)**(4/3))+kk+1
    print("k",kk,"n_PD",nPD,"3k+2",3*kk+2, "n_PD/k", nPD/kk, "k^(1/3)", kk**(1/3), "bound", kk**(1/3)*(1+1/kk)**(4/3)+1+2/kk)
# threshold-unit-ratio
k=6667
j0=floor(0.3*k)
print("j0",j0)
val = (0.3*k-1)*(0.3*k)/(2*(1.3*k+1))
print("-(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667:", -val)
exact = sum(i/(k+1+i) for i in range(1,j0+1))
print("exact sum i/(k+1+i):", exact, " j0(j0+1)/(2(k+1+j0)):", j0*(j0+1)/(2*(k+1+j0)))
print("1+1.5 log k - val:", 1+1.5*log(k)-val)
print("e^0.3", exp(0.3), " e^(3/(2k))", exp(3/(2*k)), " product", 1.00023*1.34986)
print("2*0.7654-1.3502", 2*0.7654-1.3502)
# exact log Pi^up_{j0+1}
lp = -sum(log(1+i/(k+1)) for i in range(1,j0+1))
print("exact log Pi^up:", lp, " log(e k^1.5):", 1+1.5*log(k), " total:", 1+1.5*log(k)+lp)
# s_{2k-1}(k) lower bound check: binom(2k-1,k) k^{k-1}(k-1)^{k-2}/(2k)^{2k-2} >= e^-1 k^-1.5
from fractions import Fraction
for kk in [10,50,200]:
    lb = comb(2*kk-1,kk)*kk**(kk-1)*(kk-1)**(kk-2)/ (2*kk)**(2*kk-2)
    print(kk, "forest lb", lb, " e^-1 k^-1.5", exp(-1)*kk**-1.5)
# x_k n > 368
k=501
xk=(k/(k+1))**(k-1)
print("x_k(501)",xk,"x_k*1003",xk*1003)
