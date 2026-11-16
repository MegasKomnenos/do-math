# S5 검산: 6장의 명시 상수 재계산 (mpmath 고정밀)
from mpmath import mp, mpf, sqrt, exp, log, e, pi, ceil, floor, findroot
mp.dps = 30

def u(k):
    k = mpf(k)
    return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)

print("u(3131) =", u(3131), " 2u =", 2*u(3131))
print("u(6667) =", u(6667), " 2u =", 2*u(6667))
print("u(10000)=", u(10000), " 2u =", 2*u(10000))
print("u(3131)/2 =", u(3131)/2)
print("hatUps(3131) =", (3131-1)*u(3131)/(2*3131+1))

def surv_term(k):
    k = mpf(k)
    vp = max(k+1, 4000)
    io = 2*k+1-vp
    return 2*min(1, 3*vp*io**(-mpf(3)/2))
for k in (3131, 6667, 10000):
    print("k=",k," 2min(...) =", surv_term(k), " 50.62/sqrt(k-1) =", mpf('50.62')/sqrt(k-1))
    v = 2 - surv_term(k) - 2*u(k) - mpf('50.62')/sqrt(k-1)
    print("   v(k) =", v)
print("24000/2263^1.5 =", 24000/mpf(2263)**mpf('1.5'))
print("50.62/sqrt(3130) =", mpf('50.62')/sqrt(3130))

# m(0.55, 2.4978)
tp = mpf('0.55'); kap = mpf('2.4978')
# tp chi^2 - (kap tp + 2) chi + kap = 0
a=tp; b=-(kap*tp+2); c=kap
chi = (-b+sqrt(b*b-4*a*c))/(2*a)
print("large root chi =", chi, " m =", (chi**2-kap*chi)*exp(-tp*chi))
x = mpf(3132)/3130
G = x/((1+x)**(1-tp)-1)
print("Gamma_tp at x=3132/3130 =", G)
print("kappa_d lower 1.498+2*3130/6261 =", mpf('1.498')+2*mpf(3130)/6261)
print("ex_max 3131/6261 =", mpf(3131)/6261, " 2-exmax-20/(9*3130)=", 2-mpf(3131)/6261-mpf(20)/(9*3130))

# B2
def B2(k):
    k=mpf(k)
    return (1-1/e)+(exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43) =", B2(43), " B2(2000) =", B2(2000), " 1-B2(2000)=", 1-B2(2000))
print("B2(42) =", B2(42))

# (6.8) numerics
C=mpf(3); k=mpf(4000)
qs = ceil((C*k)**(mpf(2)/3)); print("q* at k=4000:", qs, (C*k)**(mpf(2)/3))
lhs = 1-mpf('1.6')/sqrt(525)+mpf('0.8')/525
print("LHS (6.8) at q=525:", lhs, " without 0.8/q:", 1-mpf('1.6')/sqrt(525))
t1 = mpf('0.8')*sqrt(2)/3*(1+mpf(1)/(2*524))
t2 = mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3)
t3 = mpf('1.5')/(3*sqrt(525))
print("bracket terms:", t1, t2, t3, " sum:", t1+t2+t3, " x2:", 2*(t1+t2+t3))
print("1.2(1-2/525)^-2.5 =", mpf('1.2')*(1-mpf(2)/525)**(-mpf('2.5')))
print("1.2(1+2/525)^0.5 =", mpf('1.2')*(1+mpf(2)/525)**(mpf('0.5')))
print("1.5(1-1/525)^-2.5 =", mpf('1.5')*(1-mpf(1)/525)**(-mpf('2.5')))
print("2(2pi)^-1/2 =", 2/sqrt(2*pi))

# small k tilt sum exact rational check k=2..42
from fractions import Fraction
from math import factorial
def bor_times_e_n(n):  # e^n Bor(n) = n^{n-1}/n!
    return Fraction(n**(n-1), factorial(n))
mx=0
for kk in range(2,43):
    xk = Fraction(kk, kk+1)**(kk-1)
    s = sum(bor_times_e_n(n)*xk**n for n in range(2,kk+2))
    mx=max(mx,s)
    if kk in (2,3,42): print("k=",kk," sum =", float(s), s if kk==2 else "")
print("max over 2..42:", float(mx), " all<1:", mx<1)

# theorem U final constants
cc = 1/sqrt(2*pi)
JI, YI, JX, YX = mpf('8.133'), mpf('10.301'), mpf('17.951'), mpf('23.462')
A = 3*cc*(JI+cc*YI); Bv = mpf('1.5')*mpf('2.7323')*mpf('0.8051')*cc*(JX+cc*YX)
print("3c(JI+cYI)=",A," second=",Bv," sum=",A+Bv)
# 6.3 numerics
print("e^{1/24+1/612}=", exp(mpf(1)/24+mpf(1)/612), " 1+1/51=",1+mpf(1)/51, " tl^-1 bound 1/(1-3/204)=",1/(1-mpf(3)/204))
print("u-product:", exp(mpf(1)/24+mpf(1)/612)*(1/(1-mpf(3)/204))*(1+mpf(1)/51)*mpf(4)/3)
print("0.5282*1.449=", mpf('0.5282')*mpf('1.449'))
X=(5-sqrt(7))/6; print("X*=",X," max=",X*(1-X)*(3-2*X), (10+7*sqrt(7))/54)
print("L/G V>=2:", mpf('1.5')/53*mpf(4)/3*mpf('0.5')*mpf('1.01961')*mpf('1.0150'))
print("L/G V=1:", mpf('1.5')/52*mpf('2.02')*mpf('0.51')*mpf('1.01961')*mpf('1.0150'))
print("e^{3/102}=", exp(mpf(3)/102))
print("Omega(3,2)c lower const 0.2/e*0.6=", mpf('0.2')/e*mpf('0.6'))
print("c_{y+2} const: 2e^-2+e^-1-1.03e^-2/51 =", 2*exp(-2)+exp(-1)-mpf('1.03')*exp(-2)/51)
y=mpf(50); print("ratio at y=50:", mpf('0.0441')*(y-1)*(y+2)**2/(mpf('1.2')*(y+1)*(y+3)))
print("1.03e^-1/(2*51)=", mpf('1.03')*exp(-1)/(2*51))
# witness bound at n=20000
n=mpf(20000); print("wp(20000)=", mpf('1.99')+mpf('0.59963')*(n+1)**(mpf(2)/3)+mpf('1.24847')*(n+1)**(mpf(1)/3))
print("(6262)^(2/3)=", mpf(6262)**(mpf(2)/3), " 0.65*3131-1=", mpf('0.65')*3131-1)
print("9*(1.5)^1.5=", 9*mpf('1.5')**mpf('1.5'), " *4/3=", 9*mpf('1.5')**mpf('1.5')*4/3)
print("12000^(2/3)=", mpf(12000)**(mpf(2)/3))
