from fractions import Fraction as F
import math
e=math.e
# cr_k(1+5/(2k)+2/k^2) for k=1..9
for k in range(1,10):
    cr=F(k+1,k)**(k-2)
    v=cr*(1+F(5,2*k)+F(2,k*k))
    print(k, math.floor(float(v)*10000)/10000, float(v)>87/32)
print("e<65/24+1/100:", e<65/24+1/100, "65/24+1/100<87/32:", 65/24+1/100<87/32)
# inequality cr_k > e k^2/(k^2+2.5k+2) for k up to 2000
bad=[k for k in range(1,2001) if not (1+1/k)**(k-2) > e*k*k/(k*k+2.5*k+2)]
print("bad",bad[:5])
# e15
e15=sum(F(1,math.factorial(j)) for j in range(16)); print("e15<e", float(e15)<e, (math.factorial(15)*e15).denominator)
# bracket at theta=1/10
th=F(1,10); print(F(5,12)-F(7,2)*th+F(11,8)*th**2-F(7,12)*th**3+th**4 >= F(1,15))
