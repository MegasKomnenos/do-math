# J5: 6.1, 6.2 numeric checks
from fractions import Fraction as Fr
import math
# 6.1 constants
print("12000^(2/3) =", 12000**(2/3), "ceil", math.ceil(12000**(2/3)))
print("1-1.6/sqrt525 =", 1-1.6/math.sqrt(525))
print("0.8*sqrt2/3*(1+1/1048) =", 0.8*math.sqrt(2)/3*(1+1/1048))
print("3.923*3^(-4/3)*4000^(-1/3) =", 3.923*3**(-4/3)*4000**(-1/3))
print("1.5/(3 sqrt525) =", 1.5/(3*math.sqrt(525)))
print("1.2(1-2/525)^-2.5 =", 1.2*(1-2/525)**-2.5)
print("1.2(1+2/525)^.5 =", 1.2*(1+2/525)**0.5)
print("1.5(1-1/525)^-2.5 =", 1.5*(1-1/525)**-2.5)
print("2/sqrt(2pi)=",2/math.sqrt(2*math.pi), "3/sqrt(2pi)=",3/math.sqrt(2*math.pi))
# 6.2 B_2
def B2(k): return (1-1/math.e)+(math.exp(1.5+1/k)-1)*2*(math.sqrt(k+1)-1)/(math.sqrt(2*math.pi)*(k+1))
print("B2(43)=",B2(43),"B2(2000)=",B2(2000),"B2(42)=",B2(42))
print("e^{3/2+1/43}-1=",math.exp(1.5+1/43)-1, "2(sqrt44-1)=",2*(math.sqrt(44)-1), "sqrt(2pi)*44=",math.sqrt(2*math.pi)*44)
# exact tilt-sum for 2<=k<=42: sum_{n=2}^{k+1} Bor(n) q^n with q = e x_k ; Bor(n) q^n = n^{n-1}/n! * x_k^n (e cancels)
def tiltsum(k):
    x=Fr(k,k+1)**(k-1)
    return sum(Fr(n**(n-1),math.factorial(n))*x**n for n in range(2,k+2))
vals=[(k,tiltsum(k)) for k in range(2,43)]
mx=max(vals,key=lambda t:t[1])
print("max over 2..42:",mx[0],float(mx[1]),mx[1] if mx[0]==2 else "")
print("all <1:",all(v<1 for k,v in vals))
print("k=42:",float(vals[-1][1]),"k=43 exact:",float(tiltsum(43)),"k=10:",float(tiltsum(10)))
# g bounds
g=lambda x:(x-1)*math.log(1+1/x)
for k in [2,3,10,100]:
    print(k, 1-1.5/k+0.5/k**2, g(k), 1-1.5/k+5/(6*k*k))
# g'(j) bound check
gp=lambda j: math.log(1+1/j)-(j-1)/(j*(j+1))
for j in [2,3,5,10,100,2000]:
    print(j, gp(j), 1.5/j**2-5/(3*j**3)-1/(4*j**4), 1.5/j**2*(1-1.2/j))
# k(1-g(k)) <= 3k/(2k+1)
for k in [2,10,2000]: print(k, k*(1-g(k)), 3*k/(2*k+1))
