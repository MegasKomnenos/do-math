# H8: 8.2절 상수 문단과 단조성 증명의 수치 상수 재계산
from mpmath import mp, mpf, sqrt, exp, pi, log
mp.dps = 30
k = mpf(6600)
k13 = k**(mpf(1)/3); k23 = k**(mpf(2)/3)
qmin = mpf('0.2')*k23; pmin = qmin-1
mu = 1/qmin
print("6600^(1/3)", k13, "6600^(2/3)", k23)
print("qmin", qmin, "pmin", pmin, "sqrt pmin", sqrt(pmin))
print("mu", mu, "xi*eps max", mpf('6.001')/k13, "eps0", 1/k13, "k^-2/3", 1/k23)
print("(1-mu)^-1/2", (1-mu)**(-mpf(1)/2), "(1-mu)^-3/2", (1-mu)**(-mpf(3)/2))
# R2 term
print("R2 second term", (1+1/(4*pmin))/(1-mu), "third", mpf(7)/2*k/(k+1))
print("R2 sum", mpf('2.5')+mpf('1.018072')-mpf('3.49946')-mpf(2)/3)
# D3
z12lo = mpf('-1.46036'); z32hi = mpf('2.61238')
cpsi = -z12lo + z32hi/12
print("cPsi max", cpsi, "1-cPsi/(2sqrt p)", 1-cpsi/(2*sqrt(pmin)))
print("D3 bound", mpf('0.319921')/3 + 1/(3*mpf('0.985789')*mpf('0.89926')) - mpf(2)/3)
# (나) 0.168623
c = 1/sqrt(2*pi)
print("D1-D3 min", mpf('0.2') - 1/k23 - 3*c*sqrt(mpf('0.2'))/k13)
print("3/2 c k^-1/3", mpf(3)/2*c/k13)
# (라)
xi = mpf('0.2')
t1 = (mpf(3)/2*sqrt(xi) - sqrt(xi)**-1/2/k23)/(2*c)
t2 = mpf(3)/4/k13*(1+(1-1/(xi*k23))**(-mpf(1)/2))
t3 = (k+1)/(2*k)*(1-1/(xi*k23))**(-mpf(3)/2)/(xi**2*k23)
print("U' terms", t1, t2, t3, t1-t2-t3)
# (마)
eps = 1/k13
a = (1+xi*eps)/(12*xi**2*k13); b = 3/(8*sqrt(xi)*k13)
print("V' terms", a, b, a+b, -mpf(1)/2+a+b)
# Lambda'(1), bracket at p=1
print("Lambda'(1)", mpf('2.75')+z12lo, "bracket p=1", -mpf(1)/6 + mpf(2)/3*mpf('1.46035') - mpf('0.20789'))
# 9i>=5(n+1) threshold
for kk in [420,421,422]:
    kk=mpf(kk); print(kk, 9*(kk+2) - 5*(kk+6*kk**(mpf(2)/3)+1))
# zeta values
from mpmath import zeta
print("zeta(1/2)", zeta(mpf(1)/2), "zeta(-1/2)", zeta(-mpf(1)/2), "zeta(3/2)", zeta(mpf(3)/2))
print("2/6600^(2/3)", 2/k23, "(2pi)^-1/3", (2*pi)**(-mpf(1)/3))
print("j_inf coefficient check: 4/3 c", mpf(4)/3*c, "sqrt(2/pi)", sqrt(2/pi), "2c", 2*c, "0.7979?", 2*c)
