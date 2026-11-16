# S3 검산: 5장A의 수치 몇 개를 다시 센다.
from fractions import Fraction as Fr
from math import ceil, floor, sqrt, exp, log, pi, e, factorial
import sympy as sp

# 1) 정리 old-5-1 둘째 조각 비교 수, 넷째 조각 위치 수
sec = sum(ceil(n/2)-1 for n in range(10001,20001))
print("second piece comparisons", sec)
fourth = sum((n-3) - ceil((n-1)/2) + 1 for n in range(5,20001))
print("fourth piece positions", fourth)
# 2) 정리 old-5-2 위치 수 (20001..50000), 인접 쌍 b_{ceil((n-1)/2)}..b_{n-1}
c50 = sum((n-1) - ceil((n-1)/2) for n in range(20001,50001))
print("old-5-2 positions", c50)
# 3) m(n)
def m_of(n):
    best=170
    m=171
    while m**1.5+9*m<=n:
        best=m; m+=1
    return best
print("m(20001)", m_of(20001), "m(50001)", m_of(50001))
print("597 check", 597**1.5+9*597, "598:", 598**1.5+9*598)
# 4) Cayley 비 아홉 값
for k in range(1,10):
    cr = Fr(k+1,k)**(k-2)
    v = cr*(1+Fr(5,2*k)+Fr(2,k*k))
    print(k, float(v), v> Fr(87,32))
print("e<65/24+1/100<87/32:", e < 65/24+0.01, 65/24+0.01 < 87/32)
# 5) cayley 다항식 전개 확인
t=sp.symbols('t')
expr = (2+sp.Rational(5,2)*t+2*t**2)*(-sp.Rational(5,2)*t+sp.Rational(4,3)*t**2-sp.Rational(11,12)*t**3+sp.Rational(1,2)*t**4)+5*t+4*t**2
print(sp.expand(expr))
print(sp.expand(t**2*(sp.Rational(5,12)-sp.Rational(7,2)*t+sp.Rational(11,8)*t**2-sp.Rational(7,12)*t**3+t**4)))
# 6) et(1/2)
phi=0.5
et = e*phi*exp(-phi/ sp.tan(phi).evalf() if False else -phi/ (sp.tan(phi).evalf()))/sp.sin(phi).evalf()
print("log et(1/2)", float(sp.log(et)))
# 7) L(10^4)
import mpmath as mp
mp.mp.dps=30
f=lambda i: mp.quad(lambda y: y**i*mp.e**(-y-y*y/2),[0,mp.inf])
M=[f(i) for i in range(6)]
M26=mp.quad(lambda y: y**2*mp.e**(-y-y*y/2),[0,6])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y = (-1+sqrt(1+4i))/2
    y=(-1+mp.sqrt(1+4*i))/2
    return y**i*mp.e**(-y-y*y/2)
Ms={i:Mstar(i) for i in range(2,6)}
C1=2*Ms[2]+M[3]/2+M[5]/3
C2=Ms[3]/2+Ms[5]/3+M[4]/2
C3=Ms[4]/2+M[3]/6
C4=Ms[3]/6
s=mp.mpf(100)
L=(M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+mp.e**(-0.5))/s+1/s**2)
print("L(1e4)", L)
# 8) 정리 old-5-5 끝 수치
print("sqrt(3pi/2)", mp.sqrt(3*mp.pi/2), 0.5+2*0.845204-mp.sqrt(3*mp.pi/2))
br=1/(3*s)+8/(3*s**2)+2.507/s**2+(1+2.1709*s)/s**3
print("bracket at s=100", br)
# 9) 정리 old-5-7 비 0.28
j=13; r=529
ratio = Fr(9,16)*Fr(169,400)*Fr(144,121)*Fr(2*(3*j+5),3*j*(3*j-2))*(Fr(5,2)+Fr(9,2*r))**3
print("ratio", float(ratio))
# 10) 5.3 진입 지표 수치
print("27.14^3", 27.14**3, "20001^(2/3)", 20001**(2/3), floor(0.75*20001**(2/3)))
print("(149/200)^3", (149/200)**3, "(16/25)^2", (16/25)**2, "(3/4)^3", 0.75**3, "(13/20)^2", 0.65**2)
# 11) 5.4 수치
print("30001.5^(2/3)", 30001.5**(2/3), "5/12*sqrt(598)", 5/12*sqrt(598))
for x,rr in [(1.2,598),(1.5,833),(1.8,966),(2.1,2164),(2.4,10000)]:
    print(x/sqrt(rr))
print("1/(1+9/sqrt(598))", 1/(1+9/sqrt(598)))
print("(6/5*20001)^(2/3)", (1.2*20001)**(2/3))
print("1.8^(2/3)", 1.8**(2/3), "10/2^(2/3)", 10/2**(2/3))
print("10001^(-1/3)", 10001**(-1/3), 29*0.0015+0.00141, 0.0015/1.25**12)
print("1-cos1", 1-mp.cos(1))
print("(0.64)^(2/3),(0.65)^(2/3)", 0.64**(2/3), 0.65**(2/3))
# 12) r^3 24^{-r} at 598
print("log10(1.15*598^3)", log(1.15*598**3,10), "598 log10 24", 598*log(24,10))
