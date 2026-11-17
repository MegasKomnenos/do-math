# R8: 정리 closed-form-envelope (가)(나)(다)(라) 수치 재계산
from mpmath import mp, mpf, sqrt, pi, exp, log, zeta
mp.dps = 30
c = 1/sqrt(2*pi)
z12 = zeta(mpf(1)/2); zm12 = zeta(-mpf(1)/2); z32 = zeta(mpf(3)/2)
print('zeta', z12, zm12, z32)
cpsi = -z12 + z32/12
def Psilow(x):
    if x < 1: return mpf(0)
    return c*(2*sqrt(x) - cpsi + 1/(2*sqrt(x)) - x**(-mpf(3)/2)/24)
def pieces(xi, k):
    eps = k**(-mpf(1)/3); q = xi*k**(mpf(2)/3); p = q-1; n = k+q; kk = k+1
    H = mpf(2)/3*p**1.5 + p**0.5/2 + zm12 + p**(-0.5)/24
    E = 2*c*exp(-1/(12*q))*xi**(-0.5)*(1+xi*eps)
    R1 = mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    R2 = mpf(15)/8*c*n**2.5*H/(kk**3.5*k**(mpf(2)/3))
    D1 = p/k**(mpf(2)/3)
    D2 = kk*sqrt(2/pi)*p**(-0.5)*k**(-mpf(2)/3)
    D3 = mpf(3)/2*kk*Psilow(p)/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3 = pieces(xi,k)
    return (E-R1-R2)/(D1+D2-D3)
k = mpf(6600)
# (가)
qmin = mpf('0.2')*k**(mpf(2)/3); pmin = qmin-1
print('phi low', exp(-1/(12*qmin)), '>0.998816')
xi = mpf('6.001'); eps = k**(-mpf(1)/3)
print('rho1 up', mpf(3)/2*xi*eps, '<0.4798811')
rho2 = mpf(5)/8*(1+3/(4*pmin))*(1+xi*eps)**2.5*xi**2*k**(-mpf(2)/3)
print('rho2 up', rho2, '<=0.129421')
print('V low', mpf('0.998816')-mpf('0.4798811')-mpf('0.129421'))
print('theta1 up', xi**1.5/(2*c), '<=18.42449', ' upsilon', (k+1)/k*(1-1/qmin)**-0.5, '<=1.00734')
print('quot', mpf('0.3895139')/mpf('19.43183'), '>=0.020044')
# actual V,U at 6.001
E,R1,R2,D1,D2,D3 = pieces(xi,k); E0 = 2*c*xi**-0.5
print('actual V', (E-R1-R2)/E0, 'U', (D1+D2-D3)/E0, 'q', qkk(xi,k))
# (나)
def br(xi,k): return (mpf('0.4')*xi**1.5 + mpf('0.5775')*xi**0.5*k**(-mpf(2)/3))*(1+xi*k**(-mpf(1)/3))**1.5
print('bracket 0.1', br(mpf('0.1'),k), '<=0.013274 ; sum', mpf('1.46035')-mpf('0.103945')-mpf('0.041667')-mpf('0.013274'))
q01 = mpf('0.1')*k**(mpf(2)/3); p01=q01-1
print('q at 0.1', q01, 'p', p01, ' |z-1/2|/q', mpf('0.20789')/q01, '<=0.005909', ' p^-1.5/(12q)', p01**-1.5/(12*q01), '<=0.000012')
print('bracket 2.1', br(mpf('2.1'),k), '<=1.430101 ; sum', mpf('1.46035')-mpf('0.005909')-mpf('0.000012')-mpf('1.430101'))
# (다)
q2 = 2*k**(mpf(2)/3); p2=q2-1; mu2=1/q2
print('q at 2', q2, '>703.708')
val = (sqrt(1-mu2) - (1+p2**-0.5)*eps/sqrt(2))/2
print('-drho1 coeff', val, '>=0.480085', ' dV', val-mpf(1)/3, '>0.146751')
print('dtheta1 coeff', eps/sqrt(2)/(3*c), '<=0.0314973')
print('dtheta3 coeff', (1+1/(4*p2))/2, '<=0.5001779')
print('V coeff', mpf(1)/2 - mpf(3)/2*mu2 - mpf(3)/4*eps/sqrt(2), '>=0.46959')
print('U low at 2', 1 + (2**1.5 - 2**0.5*k**(-mpf(2)/3))/(2*c) - mpf(3)/2*2*eps, '>=4.37993')
print('log q coeff', mpf('0.146751') - mpf('0.5316752')/mpf('4.37993'), '>=0.02536')
# (라) joints
jinf = lambda xi: mpf(4)/3*c*xi**1.5
print('q6600(2)', qkk(mpf(2),k), '<=0.213721 ; e^-j(2)', exp(-jinf(mpf(2))), '>=0.222127')
print('q6600(2.1)', qkk(mpf('2.1'),k), '>=0.200904 ; e^-j(2.1)', exp(-jinf(mpf('2.1'))), '<=0.198148')
# other checks
print('6600^(2/3)', k**(mpf(2)/3), ' 10^5^(2/3)*6', 6*mpf(10)**(mpf(10)/3))
print('1.15/6^1.5', mpf('1.15')/6**1.5)
print('(2pi)^-1/3', (2*pi)**(-mpf(1)/3), ' (4c)^(2/3)', (4*c)**(mpf(2)/3))
print('V,U at 0.2', [(x/ (2*c*mpf('0.2')**-0.5)) for x in [sum(pieces(mpf('0.2'),k)[0:1])-pieces(mpf('0.2'),k)[1]-pieces(mpf('0.2'),k)[2]]], qkk(mpf('0.2'),k))
