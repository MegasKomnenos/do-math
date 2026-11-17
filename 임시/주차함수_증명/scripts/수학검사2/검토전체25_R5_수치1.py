# 검토전체25 R5: 6.1~6.5절 수치 재계산 (mpmath 없이 decimal/fractions)
from decimal import Decimal as D, getcontext
import math
getcontext().prec = 40
pi = D('3.14159265358979323846264338327950288419716939937510')
def sqrt(x): return D(x).sqrt()
def ln(x): return D(x).ln()
def exp(x): return D(x).exp()
def pw(x, a): return exp(D(a) * ln(D(x)))
print('--- 6.1')
c = 2 / sqrt(2 * pi)
print('2/sqrt(2pi)=', c, ' 2/sqrt(pi)=', 2 / sqrt(pi))
print('(1.15*2000)^(2/3)=', pw(D('2300'), D(2) / 3))
def coef(q, chi):
    chi = D(chi)
    return c * (D(1) / 4 * pw(1 - D(1) / (2 * q), D(-3) / 2) + (1 + chi + chi * chi) * pw(1 - chi, D(-1) / 2) * pw(1 + chi, D(-3) / 2))
for chi in ['0.9', '0.99', '0.9999']:
    print('chi', chi, 'coef(q=175)=', coef(175, chi))
print('Mn bound chi>0.9:', c * 3 * sqrt(D('0.19')), ' chi>0.99:', c * 3 * sqrt(1 - D('0.99') ** 2))
print('1-0.9999^3=', 1 - D('0.9999') ** 3)
print('gain(0.02)/0.02=', (pw(D('0.98'), D(-3) / 2) - 1) / D('0.02'))
print('1.28/sqrt50=', D('1.28') / sqrt(50), ' c*sqrt(50/0.77)=', c * sqrt(D(50) / D('0.77')))
print('c*(1-1/350)^-1/2=', c * pw(1 - D(1) / 350, D(-1) / 2))
print('cases:', D('1.1284') + D('2.82') / 175, D('1.044') + D('9.3') / 175, D('0.34') + D(85) / 175)
print('--- 6.2 B2')
def B2(k):
    k = D(k)
    return (1 - exp(D(-1))) + (exp(D(3) / 2 + 1 / k) - 1) * 2 * (sqrt(k + 1) - 1) / (sqrt(2 * pi) * (k + 1))
print('B2(43)=', B2(43), ' B2(2000)=', B2(2000), ' 1-B2(2000)=', 1 - B2(2000))
print('--- 6.3')
X = (5 - sqrt(7)) / 6
print('X*=', X, ' max=', X * (1 - X) * (3 - 2 * X), (10 + 7 * sqrt(7)) / 54)
tlinv = 1 / (1 - D('0.75') / 51)
e1 = exp(D(1) / 24 + D(1) / 612)
print('tl^-1<=', tlinv, ' e^(1/24+1/612)=', e1, ' 1+1/51=', 1 + D(1) / 51)
u = e1 * tlinv * (1 + D(1) / 51) * 4 / 3
print('u<=', u, ' M/G<=', D('0.5282') * D('1.449'))
print('L/G V>=2:', D('1.5') / 53 * 4 / 3 / 2 * D('1.01961') * D('1.0150'), ' V=1:', D('1.5') / 52 * D('2.02') * D('0.51') * D('1.01961') * D('1.0150'))
print('e^(3/102)=', exp(D(3) / 102), ' 1.545/e=', D('1.545') * exp(D(-1)), ' e^-2=', exp(D(-2)))
y = D(50)
print('d=3 ratio at y=50:', D('0.0441') * (y - 1) * (y + 2) ** 2 / (D('1.2') * (y + 1) * (y + 3)))
print('0.2*0.6/e=', D('0.12') * exp(D(-1)), ' c_{y+2} lower*(y+2) at y=50:', 2 * exp(D(-2)) + exp(D(-1)) - D('1.03') * exp(D(-2)) / 51)
print('d=y+2 ratio coefficient: e^(-1+3/102)/2=', exp(D(-1) + D(3) / 102) / 2)
print('--- 6.4')
def uu(k):
    k = D(k)
    return D(3) / D('0.35') * (D('1.35') + 1 / k) * pw(D('0.65') - 1 / k, D(-3) / 2) / sqrt(k)
def ub(k):
    k = D(k)
    return D('1.15') / D('0.35') * (2 + 1 / k) * pw(D('0.65') - 1 / k, D(-3) / 2) / sqrt(k)
print('u(2001)=', uu(2001), ' ub(2001)=', ub(2001), ' ub(6667)=', ub(6667))
print('9*(1.5)^1.5=', 9 * pw(D('1.5'), D('1.5')), ' *4/3=', 12 * pw(D('1.5'), D('1.5')))
n = D(20001)
print('witness bound at n=20000:', D('1.99') + D('0.59963') * pw(n, D(2) / 3) + D('1.24847') * pw(n, D(1) / 3))
print('(4002)^(2/3)=', pw(D(4002), D(2) / 3), ' (2k)^(2/3) vs 0.65k-1 at k=2001:', D('0.65') * 2001 - 1)
print('--- 6.5')
def DDLn(k):
    k = D(k)
    return 14 * (ln(3 * k) - 1) / (5 * sqrt(pi * k)) + D('37.6') / (5 * sqrt(pi) * k)
for k in [2001, 6667, 6668, 8065, 9551, 9705]:
    print('DDLnat(%d)=' % k, DDLn(k))
print('7(3-log3)+42/sqrt3=', 7 * (3 - ln(3)) + 42 / sqrt(3))
print('3*1.3752/sqrt(pi)=', 3 * D('1.3752') / sqrt(pi), ' 21/(5sqrtpi)=', D(21) / (5 * sqrt(pi)))
k = D(2001)
print('Acrit factor:', (1 + 1 / k) * (1 + 2 / k) / (1 - 3 / (4 * k)) * D('1.3752'), ' 1.3778^2(1+2/k)^2/6=', D('1.3778') ** 2 * (1 + 2 / k) ** 2 / 6)
print('(e^(3/2k)+1)/2=', (exp(3 / (2 * k)) + 1) / 2)
def v(k):
    k = D(k)
    return 2 - D('4.6') / sqrt(k + 1) - 2 * ub(k) - DDLn(k) / 2
for k in [2001, 6667]:
    kk = D(k)
    print('v(%d)=' % k, v(k), ' parts:', D('4.6') / sqrt(kk + 1), 2 * ub(k), DDLn(k) / 2)
