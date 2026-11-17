# R11 검산: a0, a1의 양쪽 유리수 끝 (D.central-gap-rational-audit (ㄱ))과 (ㅅ)의 산술
from fractions import Fraction as Q
from math import factorial
def series_int(a, p, M=200):
    terms = [Q(a)**(3*m+p+1)/(3**m*factorial(m)*(3*m+p+1)) for m in range(M+1)]
    m0 = max(i for i in range(1, M+1) if terms[i] > terms[i-1]) + 1
    s = sum(((-1)**m*terms[m] for m in range(M)), Q(0))
    return s-terms[M], s+terms[M]
def exp_lower(x, n=200):
    s = Q(0); t = Q(1)
    for j in range(n):
        s += t; t = t*x/(j+1)
    return s
a = Q(4); eA = 1/exp_lower(a**3/3)
lo0, hi0 = series_int(a, 0); hi0 += eA/16
lo1, hi1 = series_int(a, 1); hi1 += eA/4
print("a0:", Q(1287899, 10**6) < lo0, hi0 < Q(12879, 10**4), float(lo0), float(hi0))
print("a1:", Q(938892, 10**6) < lo1, hi1 < Q(939, 1000), float(lo1), float(hi1))
# (C3) at omega=6.98, k^{-1/3}<=0.0464159
w = Q(698, 100); x = Q(464159, 10**7)
print("x^3*10000>=1:", x**3*10000 >= 1)
LB = w - Q(7, 2) - (4*w+Q(1, 2))*Q(12879, 10**4)*x - Q(13, 2)*w*Q(939, 1000)*x*x - 12*w/10000
print("kR/Bor >=", float(LB), LB >= Q(16809, 10**4))
print("assembly:", float(Q(5642, 1000)*Q(16809, 10**4)*Q(39893, 10**5) - Q(163, 10**4) - Q(3554, 1000)))
print("sum of seven:", float(sum(map(Q, ["183.51", "2303.07", "203.57", "983.74", "920.70", "454.86", "418.83"]))))
import math
print("bD:", (46*math.sqrt(2)-12-54.6828-1e-22)*math.exp(1e-4)-1e-19, " bJ:", 0.4503*3*2.50663+1675.2/10000+2e-20)
