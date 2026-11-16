# 검토전체7 M3: 5.1절·5.2절의 수치 재계산
from fractions import Fraction as F
import math

# 1) 둘째 조각 비교 수: 10001<=n<=20000, 1<=l<=k_n-1
c2 = sum(math.ceil(n/2)-1 for n in range(10001, 20001))
print("둘째 조각 비교 수", c2, c2 == 74_995_000)
# 2) 넷째 조각 위치 수: 5<=n<=20000, ceil((n-1)/2)<=l<=n-3
def qr_count(a, b):
    return sum(max(0, (n-3) - math.ceil((n-1)/2) + 1) for n in range(a, b+1))
c4 = qr_count(5, 20000)
print("넷째 조각 위치 수", c4, c4 == 99_970_002)
c50 = qr_count(20001, 50000)
print("5-2 위치 수", c50, c50 == 524_955_000)
pairs50 = sum((n-2) - math.ceil((n-1)/2) + 1 for n in range(20001, 50001))
print("5-2 인접 쌍 수", pairs50, pairs50 == 524_985_000)
pairs20 = sum((n-2) - math.ceil((n-1)/2) + 1 for n in range(5, 20001))
print("재인증 인접 쌍 수", pairs20, pairs20 == 99_989_998)
# 3) 첫째 조각 열 경계: 2*ceil(k^2/4) >= 10000 iff k>=142
for k in (141, 142):
    print("k", k, "2ceil(k^2/4)", 2*math.ceil(k*k/4))
# 4) 14,365 다항식
print("Newton 다항식 수", sum(r-1 for r in range(2, 171)))
# 5) Cayley 비 아홉 값 (유리수 정확)
for k in range(1, 10):
    cr = F(k+1, k)**(k-2)
    v = cr*(1 + F(5, 2*k) + F(2, k*k))
    print("k", k, "cr*(1+5/2k+2/k^2) =", v, float(v), "> 87/32:", v > F(87, 32))
print("e < 65/24+1/100 < 87/32:", math.e < 65/24+0.01 < 87/32)
# 6) 다항식 전개 확인: (2+5t/2+2t^2)(-5t/2+4t^2/3-11t^3/12+t^4/2)+5t+4t^2
import sympy as sp
t = sp.symbols('t')
expr = sp.expand((2+sp.Rational(5,2)*t+2*t**2)*(-sp.Rational(5,2)*t+sp.Rational(4,3)*t**2-sp.Rational(11,12)*t**3+sp.Rational(1,2)*t**4)+5*t+4*t**2)
print("전개:", expr)
target = sp.expand(t**2*(sp.Rational(5,12)-sp.Rational(7,2)*t+sp.Rational(11,8)*t**2-sp.Rational(7,12)*t**3+t**4))
print("일치:", sp.simplify(expr-target) == 0)
# 7) 𝔪(n)
def mfrak(n):
    best = 170
    m = 171
    while m**1.5 + 9*m <= n:
        best = m; m += 1
    return best
print("m(20001) =", mfrak(20001), " m(50001) =", mfrak(50001))
# 8) 5-11 (가) 수치
print("27.14^3 =", 27.14**3, " 20001^(2/3) =", 20001**(2/3), " r0(20001) =", math.floor(0.75*20001**(2/3)))
print("(149/200)^3 =", (149/200)**3, " (16/25)^2 =", (16/25)**2, " (3/4)^3 =", 0.75**3, " (13/20)^2 =", 0.65**2)
print("27/(4*27.14) =", 27/(4*27.14), " (3/4)^1.5 =", 0.75**1.5)
# 9) parity-tail rq_* 
print("rq_* =", 13/20*(1+3/529)/23, "< 1/12:", 13/20*(1+3/529)/23 < 1/12)
# 10) kernel-crude / K1 수치
print("2*sqrt2/e =", 2*math.sqrt(2)/math.e, " 181/174 =", 181/174, " 26/25 =", 1.04)
print("312m^2-374m+25 at m=1,2:", 312-374+25, 312*4-374*2+25)
# 11) 5-5 증명 수치
print("sqrt(pi/2) =", math.sqrt(math.pi/2), " sqrt(3pi/2) =", math.sqrt(3*math.pi/2))
print("1/2+2*0.845204-sqrt(3pi/2) =", 0.5+2*0.845204-math.sqrt(3*math.pi/2))
s = 100
br = 1/(3*s)+8/(3*s*s)+2.507/(s*s)+(1+2.1709*s)/s**3
print("대괄호(s=100) =", br, "< 0.0041:", br < 0.0041)
