# R8: 8.2절 수치 상수 재계산
from mpmath import mp, mpf, sqrt, pi, exp, log
mp.dps = 30
k = mpf(6600); xi = mpf('0.2')
c = 1/sqrt(2*pi)
eps = k**(-mpf(1)/3); q = xi*k**(mpf(2)/3); p = q-1; mu = 1/q
print('eps', eps, 'k^-2/3', k**(-mpf(2)/3))
# first fact
print('D1-D3 lower', xi - k**(-mpf(2)/3) - 3*c*sqrt(xi)*eps, ' claim >0.168623')
print('(3/2)c eps', mpf(3)/2*c*eps, ' claim <=0.032')
# third fact
t1 = (1+xi*eps)/(12*xi**2*k**(mpf(1)/3)); t2 = 3/(8*sqrt(xi)*k**(mpf(1)/3))
print('t1', t1, '<0.112250 ; t2', t2, '<0.044703 ; sum', t1+t2, '<0.156953')
# (나)
f1 = (mpf(3)/2*sqrt(xi) - sqrt(xi)**-1/2*k**(-mpf(2)/3))/(2*c)
f2 = mpf(3)/4*eps*(1+(1-1/(xi*k**(mpf(2)/3)))**(-mpf(1)/2))
f3 = (k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**(-mpf(3)/2)/(xi**2*k**(mpf(2)/3))
print('f1', f1, '>0.8367662 ; f2', f2, '<0.0802540 ; f3', f3, '<0.0363026 ; diff', f1-f2-f3)
# pieces (나)
print('(1+1/(4p))/(1-mu)', (1+1/(4*p))/(1-mu), '<=1.018072')
print('3.5*k/(k+1)', mpf('3.5')*k/(k+1), '>=3.49946')
print('sum', mpf('2.5')+mpf('1.018072')-mpf('3.49946')-mpf(2)/3)
# pieces (다)
cpsi_up = mpf('1.46036') + mpf('2.61238')/12
print('cpsi up', cpsi_up, '<1.678059')
print('1-cpsi/(2sqrt p)', 1-mpf('1.678059')/(2*sqrt(p)), '>0.89926')
print('D3 total', mpf('0.319921')/3 + 1/(3*mpf('0.985789')*mpf('0.89926')) - mpf(2)/3, '< -0.184')
# pieces (가)
print('eps(1+xi eps) at xi=6.001', eps*(1+mpf('6.001')*eps), '<0.0704')
# 9i>=5(n+1) k threshold
for kk in [421,422]:
    kk=mpf(kk); print(kk, 9*(kk+2) - 5*(kk+6*kk**(mpf(2)/3)+1))
