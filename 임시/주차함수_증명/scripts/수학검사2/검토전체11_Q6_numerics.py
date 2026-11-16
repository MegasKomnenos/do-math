from fractions import Fraction as F
from math import log, exp, e, comb, factorial
# 1. column-lemma integer inequality
L = 10**21 * 400**10
R = 17**21 * 123**10
print("int ineq", L > R, L, R, R/1e46)
print("17^21", 17**21, 17**21 < 6.95e25, "123^10", 123**10, 123**10 < 7.93e20)
# hf(1.7) bound
val = 40/41*(10/17)**2.1
print("40/41*(10/17)^2.1 =", val, val > 0.3)
print("1-2.1*(10/17)^3 =", 1-2.1*(10/17)**3)
# 2. t_k, n_sharp for some k, o_k > 2
def tk(k):
    j=0
    while True:
        if (k+1)**j * k**(j+1) + (k-1)**(2*j+1) >= 2*k**(2*j+1): return j
        j+=1
for k in [2,3,5,10,41,100,501,840,841,2000,2001]:
    t=tk(k); print(k, "t_k", t, "n_sharp", k+(k+1)*t, "o_k", -2*log(1-1/k)/log(1+1/k))
# 3. x_k and n_flat for k = 501, 2000, 2001, 3131
def xk(k): return (k/(k+1))**(k-1)
def phi(n,k):
    m=(n-k)/(k+1); H=xk(k)*n/k
    return (1+1/k)**m+(1-1/k)**(m+H)-2
def nflat(k):
    n=2*k+1
    while phi(n,k)<0: n+=1
    return n
for k in [501,840,841,2000,2001,3131,6667]:
    print(k,"n_flat",nflat(k),"n_sharp",k+(k+1)*tk(k),"3k",3*k, "2k^1.5", 2*k**1.5)
