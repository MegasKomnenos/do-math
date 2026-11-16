from fractions import Fraction as F
import math
def hb_coeffs(d):
    # [rho^j] hb_d = (j+1)(d+1)^(d-j-1)/(d-j)!
    return [F((j+1)*(d+1)**(d-j-1) if d-j-1>=0 else 0, math.factorial(d-j)) if j<d else F(1) for j in range(d+1)]
def tm(d,rho):
    c=hb_coeffs(d); num=sum(j*cj*F(rho)**j for j,cj in enumerate(c)); den=sum(cj*F(rho)**j for j,cj in enumerate(c)); return num/den
worst=0
for d in range(1,400):
    t=float(tm(d,1)); b=math.sqrt(math.pi*d/2)
    if t>b: print("FAIL",d,t,b)
    worst=max(worst,t/b)
print("max ratio tm_d(1)/sqrt(pi d/2):",worst)
# check hb_d(1)=(d+1)^d/d!
print(all(sum(hb_coeffs(d))==F((d+1)**d,math.factorial(d)) for d in range(1,30)))
# tm monotone in rho
print(all(tm(d,F(i,10))<=tm(d,F(i+1,10)) for d in (1,5,20) for i in range(0,30)))
# direct check of recursion-defined hb vs formula for small d
tw=lambda j: F(1) if j==1 else F((j-1)**(j-1), math.factorial(j))
def hb_rec(d,rho):
    h=[F(1)]
    for m in range(1,d+1):
        h.append((1+rho)*h[m-1]+sum(tw(j)*h[m-j] for j in range(2,m+1)))
    return h[d]
print(all(hb_rec(d,F(3,7))==sum(cj*F(3,7)**j for j,cj in enumerate(hb_coeffs(d))) for d in range(1,15)))
