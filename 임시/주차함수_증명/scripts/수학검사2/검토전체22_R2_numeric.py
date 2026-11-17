# R2 검산: 수치 대조 (mpmath) — a_0,a_1; F_0,F_1 적분; 둘째 조각 구간; 전변동 상계; Janson 멜린 변환 정합; (라) 조립 산술
from mpmath import mp, mpf, quad, exp, sqrt, pi, gamma, erfi, inf, log, loggamma, mpc, fabs, cos, sin
mp.dps = 30
a0 = quad(lambda w: exp(-w**3/3), [0, 1, 4, inf]); a1 = quad(lambda w: w*exp(-w**3/3), [0, 1, 4, inf])
print('a0', a0, ' a1', a1)
# Dawson: D(b) = e^{-b^2/2} int_0^b e^{v^2/2} dv = sqrt(pi/2) e^{-b^2/2} erfi(b/sqrt2)
def Dw(b): return sqrt(pi/2)*exp(-b*b/2)*erfi(b/sqrt(2))
def BldR_e(b):  # Bor^ld_R(b) e^{-b^2/2} = 2 - 2 b D(b)
    return 2 - 2*b*Dw(b)
# check against definition at b=1.3
b = mpf('1.3'); lhs = (2 + quad(lambda w: w**mpf(-1.5)*(1-exp(b*b*w/2)), [0, 1]))*exp(-b*b/2)
print('Bor^ld_R e^{-b^2/2} def vs Dawson:', lhs, BldR_e(b))
print('max b*D(b):', max(bb*Dw(bb) for bb in [mpf(i)/20 for i in range(1, 400)]))
ninf = 2/sqrt(pi)
def Pq(z, r): return (1-r*r)*z*z + (1-r*r)**2*z**4/4
def F0(z):
    return -ninf*z**4*exp(-z*z)*quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z, r)*(2*pi)**-0.5*BldR_e(r*z)*exp(r*r*z*z/2), [0, 1])
def F1(z):
    return -ninf*z**4*exp(-z*z)*quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z, r)*(mpf(4)/3*r*r*z*z - mpf(2)/3*r*z**4), [0, 1])
mp.dps = 20
I0 = 2*quad(F0, [0, 1, 2, 4, 8, 14]); I1 = 2*quad(F1, [0, 1, 2, 4, 8, 14])
print('int F0 =', I0, '  int F1 =', I1, '  46sqrt2-12 =', 46*sqrt(2)-12)
print('J leading 3 sqrt(2pi) =', 3*sqrt(2*pi), quad(lambda z: z**3*exp(-z*z/2)*(mpf(4)/15*z**3 - z/3), [-inf, 0, inf]))
# 둘째 조각: S_k = sum_{j<=k} j Bor(j) - 2(2pi)^{-1/2} sqrt k + 2/3 in [0, (2/3)(2pi)^{-1/2} k^{-1/2}]
mp.dps = 30
s = mpf(0); ok = True; worst = None
for j in range(1, 20001):
    s += exp(-j + (j-1)*log(j) - loggamma(j+1))*j
    S = s - 2*(2*pi)**-0.5*sqrt(j) + mpf(2)/3
    up = mpf(2)/3*(2*pi)**-0.5/sqrt(j)
    if not (0 <= S <= up): ok = False; print('fail at k=', j, S, up); break
    if j in (1, 2, 10, 100, 10000, 20000): print('k=%d S_k=%s upper=%s' % (j, mp.nstr(S, 10), mp.nstr(up, 10)))
print('second piece interval holds for k<=20000:', ok)
# 첫 조각: 0 <= 2(2pi)^{-1/2} k^{-1/2} - tail_k(1) <= (5/9)(2pi)^{-1/2} k^{-3/2}
s = mpf(0); ok = True
for j in range(1, 5001):
    s += exp(-j + (j-1)*log(j) - loggamma(j+1))
    v = 2*(2*pi)**-0.5/sqrt(j) - (1 - s)
    if not (0 <= v <= mpf(5)/9*(2*pi)**-0.5*j**mpf(-1.5)): ok = False; print('fail1', j, v); break
print('first piece interval holds for k<=5000:', ok)
# 전변동: G(w) = w^{-3/2}(e^{-phi w}-1+phi w) on [0,1], TV <= |phi|^2 e^{-Re phi}?  (Re phi<=0, |phi|<=2(-Re phi))
mp.dps = 15
worst = 0
import itertools
for a in [mpf(x) for x in ('0.01', '0.1', '0.5', '1', '2', '4', '8', '16', '30')]:
    for frac in [0, 0.25, 0.5, 0.75, 0.9, 1.0]:
        im = frac*sqrt(3)*a
        for sgn in (1,):
            phi = mpc(-a, sgn*im)
            def Gp(w):
                # G'(w)
                e = exp(-phi*w)
                return -mpf(1.5)*w**mpf(-2.5)*(e-1+phi*w) + w**mpf(-1.5)*(-phi*e+phi)
            pts = [mpf(i)/200 for i in range(0, 201)]
            tv = quad(lambda w: fabs(Gp(w)), pts[1:])  + fabs((pts[1]**mpf(-1.5))*(exp(-phi*pts[1])-1+phi*pts[1]))
            ratio = tv/(abs(phi)**2*exp(a))
            worst = max(worst, ratio)
print('max TV(G)/(|phi|^2 e^{-Re phi}) on grid:', worst)
# Janson Theorem 1.12 셋째 식과 글의 식의 상수 대조, E B = E X^... 정합
mp.dps = 30
c1 = gamma(mpf(1)/3)/(2**(mpf(1)/3)*pi); c2 = gamma(mpf(2)/3)/(gamma(mpf(5)/6)*gamma(mpf(1)/2))
print('constants', c1, c2)
def EX(s): return (mpf(3)/2)**(s/3)*gamma(1+2*s/3)*gamma(mpf(5)/6-s/3)/gamma(mpf(5)/6)*gamma(mpf(1)/2-s/3)*gamma(mpf(2)/3)/(gamma(mpf(1)/2)*gamma(mpf(2)/3-s/3))
print('E X =', EX(1), ' 2Gamma(1/3)/3^(2/3) =', 2*gamma(mpf(1)/3)/3**(mpf(2)/3))
# (라) 조립
k = mpf(10000); om = mpf('6.98')
c3 = om - mpf(7)/2 - (4*om+mpf(1)/2)*mpf('1.2879')*k**(-mpf(1)/3) - mpf(13)*om/2*mpf('0.939')*k**(-mpf(2)/3) - 12*om/k
print('C3 lower', c3, ' M0 lower', 4*sqrt(2)*(1-mpf('23.75')/k), ' C5', (2*pi)**-0.5*(1-1/(12*k)))
print('bD', (46*sqrt(2)-12-mpf('54.6828'))*exp(1/k), ' bJ', mpf('0.4503')*3*sqrt(2*pi)+mpf('1675.2')/k, ' Bn bound', sqrt(2)/pi*exp(1/k))
print('final', mpf('5.642')*mpf('1.6809')*mpf('0.39893')-mpf('0.0163')-mpf('3.554'))
