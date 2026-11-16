# K5: 6장 수치 재계산 (6.1 (6.8), 6.2 B_2, 6.4 u(3131))
from mpmath import mp, mpf, sqrt, e, pi, exp, log, ceil
mp.dps = 30
# 6.1
C = mpf(3); k = mpf(4000)
qstar = ceil((C*k)**(mpf(2)/3)); print("q* at k=4000:", qstar, (C*k)**(mpf(2)/3))
lhs = 1 - mpf('1.6')/sqrt(525); print("LHS 6.8:", lhs)
t1 = mpf('0.8')*sqrt(2)/3*(1+mpf(1)/1048); t2 = mpf('3.923')*3**(-mpf(4)/3)*4000**(-mpf(1)/3); t3 = mpf('1.5')/(3*sqrt(525))
print("RHS terms:", t1, t2, t3, "sum", t1+t2+t3, "x2", 2*(t1+t2+t3))
print("1.2(1-2/525)^-2.5 =", mpf('1.2')*(1-mpf(2)/525)**(-mpf(5)/2))
print("1.2(1+2/525)^0.5 =", mpf('1.2')*(1+mpf(2)/525)**(mpf(1)/2))
print("1.5(1-1/525)^-2.5 =", mpf('1.5')*(1-mpf(1)/525)**(-mpf(5)/2))
print("2/sqrt(2pi)=", 2/sqrt(2*pi), " 3/sqrt(2pi)=", 3/sqrt(2*pi))
# 6.2 B_2
def B2(k):
    k = mpf(k)
    return (1-1/e) + (exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(42)", B2(42), "B2(43)", B2(43), "B2(2000)", B2(2000), "1-B2(2000)", 1-B2(2000))
print("e^{1.5+1/43}-1", exp(mpf(3)/2+mpf(1)/43)-1, "2(sqrt44-1)", 2*(sqrt(44)-1), "sqrt(2pi)*44", sqrt(2*pi)*44)
# tilt sum exact small k check (k=2,3,42,43)
from fractions import Fraction
from math import factorial
def tiltsum(k):
    x = Fraction(k, k+1)**(k-1)
    s = Fraction(0)
    for n in range(2, k+2):
        s += Fraction(n**(n-1), factorial(n)) * x**n
    return s
for kk in (2,3,10,20,42,43):
    v = tiltsum(kk); print("tiltsum", kk, float(v))
# 6.4 u(3131)
def u(k):
    k = mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)/sqrt(k)
print("u(3131)=", u(3131), " 8.5715*1.35032*1.9097*0.017872=", mpf('8.5715')*mpf('1.35032')*mpf('1.9097')*mpf('0.017872'))
print("(0.65-1/3131)^-1.5", (mpf('0.65')-mpf(1)/3131)**(-mpf(3)/2), "3131^-0.5", 3131**(-mpf(1)/2))
print("1.35*3131", mpf('1.35')*3131, "(6262)^(2/3)", mpf(6262)**(mpf(2)/3), "0.65*3131-1", mpf('0.65')*3131-1)
print("witness bound at n=20000:", mpf('1.99')+mpf('0.59963')*mpf(20001)**(mpf(2)/3)+mpf('1.24847')*mpf(20001)**(mpf(1)/3))
print("9(3/2)^1.5 =", 9*mpf(1.5)**mpf(1.5), " *4/3=", 9*mpf(1.5)**mpf(1.5)*4/3)
# 6.3 constants
print("e^(1/24+1/612)", exp(mpf(1)/24+mpf(1)/612), "1/(1-3/204)", 1/(1-mpf(3)/204), "1+1/51", 1+mpf(1)/51)
print("u bound:", exp(mpf(1)/24+mpf(1)/612)*(1/(1-mpf(3)/204))*(1+mpf(1)/51)*mpf(4)/3)
print("(10+7sqrt7)/54", (10+7*sqrt(7))/54, "(5-sqrt7)/6", (5-sqrt(7))/6)
print("L/G V>=2:", mpf(1.5)/53*mpf(4)/3*mpf(0.5)*(1+mpf(1)/51)*(1/(1-mpf(3)/204)))
print("L/G V=1:", mpf(1.5)/52*mpf('2.02')*mpf('0.51')*(1+mpf(1)/51)*(1/(1-mpf(3)/204)))
print("e^{3/102}", exp(mpf(3)/102), "1.545/e", mpf('1.545')/e, "e^-2", exp(-2), "2e^-2+e^-1", 2*exp(-2)+exp(-1))
print("ratio d=3 at y=50:", mpf('0.0441')*49*52**2/(mpf('1.2')*51*53))
print("1.03/e/2", mpf('1.03')/e/2)
# 6.5 V-핵심 수치
def vv(k):
    k = mpf(k); vp = max(k+1, mpf(4000)); io = 2*k+1-vp
    a = 2*min(mpf(1), 3*vp*io**(-mpf(3)/2)); b = 2*u(k); c = mpf('50.62')/sqrt(k-1)
    return a, b, c, 2-a-b-c
for kk in (3131, 3998, 3999, 6667, 10000):
    print("v", kk, [str(x)[:10] for x in vv(kk)])
print("12000*3997^-1.5", 12000*mpf(3997)**(-mpf(3)/2), "12000*3999^-1.5", 12000*mpf(3999)**(-mpf(3)/2))
