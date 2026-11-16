# P3: 5.1절 개수·값 재계산
import math
from fractions import Fraction as F

# 둘째 조각: 10001<=n<=20000, 비교 k=2..k_n  (k_n-1개)
s2 = sum(math.ceil(n/2)-1 for n in range(10001,20001))
# 넷째 조각: 5<=n<=20000, ell from ceil((n-1)/2) to n-3
s4 = sum(max(0,(n-3)-math.ceil((n-1)/2)+1) for n in range(5,20001))
# 5-2: 20001..50000 positions ell in [ceil((n-1)/2), n-3]
s5 = sum((n-3)-math.ceil((n-1)/2)+1 for n in range(20001,50001))
s5b = sum((n-2)-math.ceil((n-1)/2)+1 for n in range(20001,50001))  # pairs up to n-2
print("둘째 조각 비교 수", s2, "문면 74,995,000")
print("넷째 조각 위치 수", s4, "문면 99,970,002")
print("5-2 위치 수 (ell<=n-3)", s5, "(ell<=n-2)", s5b, "문면 524,955,000")
# 14365
print("Newton 다항식 수", sum(r-1 for r in range(2,171)))
# m(n)
def m_of(n):
    best=170
    m=171
    while m**1.5+9*m<=n:
        best=m; m+=1
    return best
print("m(20001)=",m_of(20001),"m(50001)=",m_of(50001))
# 597 check
print(597**1.5+9*597, 598**1.5+9*598)
# cayley nine values
for k in range(1,10):
    cr=F(k+1,k)**(k-2) if k>=2 else F(1,2)
    v=cr*(1+F(5,2*k)+F(2,k*k))
    print(k, float(v), v>F(87,32))
# e bounds
print(math.e, 65/24+1/100, 87/32)
# 27.14^3
print(27.14**3, 20001**(2/3), math.floor(0.75*20001**(2/3)))
print((149/200)**3, (16/25)**2, (3/4)**3, (13/20)**2)
print("0.64^(2/3)",0.64**(2/3),0.65**(2/3))
# rq*
print("rq*",13/20*(1+3/529)/23, 1/12)
# A+ second piece r>=966
print((1.5*20001)**(2/3), (1.2*20001)**(2/3))
# rq five values
print([1.2/598**.5,1.5/833**.5,1.8/966**.5,2.1/2164**.5,2.4/100], 1/16)
print("5/12 sqrt598", 5/12*598**.5)
# omitted tail (나)
print(2.4*(1+1/598)/598**.5, (12/11)**1.5, math.log10(1.15*598**3), 598*math.log10(24), 12/(110*math.e), 1/24)
# cover-edge
print(1/(1+9/598**.5))
# 5-15
print(1.8**(2/3), 10/2**(2/3))
# 1-cos
print((1-math.cos(1)))
# boxes
print(10001**(-1/3), 0.0015/1.25**12, (10-1.4)/0.2)
# 10^4 bracket
s=100
print(1/(3*s)+8/(3*s*s)+2.507/s**2+(1+2.1709*s)/s**3, 0.5+2*0.845204-math.sqrt(3*math.pi/2), math.sqrt(math.pi/2), math.sqrt(3*math.pi/2))
# et(1/2)
l=[ (2+1/m)*sum(1/j**(2*m) for j in range(1,200000))/math.pi**(2*m) for m in range(1,8)]
print("l_m",l[:3], 1/2,1/36,1/405)
print("log et(1/2)", sum(l[m-1]*(0.5)**(2*m) for m in range(1,8)))
# nf ratio / 2sqrt2/e
print(2*2**.5/math.e, 26/25, 181/128, 2**.5)
