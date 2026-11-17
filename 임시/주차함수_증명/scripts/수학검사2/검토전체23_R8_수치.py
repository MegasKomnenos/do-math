# 검토전체23 R8: 장8 본문 수치의 재계산 (mpmath 40자리)
import math
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, floor
mp.dps = 40
c = 1/sqrt(2*pi)
k0 = mpf(6600)
T3 = mpf(1)/3


def show(name, val, claim, rel):
    claim = mpf(claim)
    ok = {'>': val > claim, '<': val < claim, '>=': val >= claim, '<=': val <= claim}[rel]
    print("%-22s %s %s %s : %s" % (name, mp.nstr(val, 12), rel, mp.nstr(claim, 12), 'OK' if ok else 'FAIL'))


qmin = mpf('0.2')*k0**(2*T3)
show('q_min', qmin, '70.3708', '>')
pmin = qmin-1
show('sqrt p_min', sqrt(pmin), '8.32891', '>=')
mu = 1/qmin
show('mu', mu, '0.0142105', '<=')
eps0 = k0**(-T3)
xe = mpf('6.001')*eps0
show('xi*eps max', xe, '0.319921', '<')
show('eps0', eps0, '0.0533113', '<=')
show('k^-2/3', k0**(-2*T3), '0.00284209', '<=')
show('(1-mu)^-1/2', (1-mu)**(-mpf(1)/2), '1.007182', '<=')
show('(1-mu)^-3/2', (1-mu)**(-mpf(3)/2), '1.021701', '<=')
print('--- pieces-k-monotone')
show('(ga) lhs', mpf('0.0533113')*mpf('1.32'), '0.0704', '<')
show('(na) second', (1+1/(4*pmin))/(1-mu), '1.018072', '<=')
show('(na) third', mpf(7)/2*k0/(k0+1), '3.49946', '>=')
show('(na) sum', mpf('2.5')+mpf('1.018072')-mpf('3.49946')-mpf('0.666667'), '-0.64805', '<')
z12 = zeta(mpf(1)/2)
zm12 = zeta(-mpf(1)/2)
z32 = zeta(mpf(3)/2)
print('zeta', mp.nstr(z12, 10), mp.nstr(zm12, 10), mp.nstr(z32, 10))
show('c_Psi up', mpf('1.46036')+mpf('2.61238')/12, '1.678059', '<')
show('1-mu', 1-mu, '0.985789', '>=')
show('1-c/(2sqrtp)', 1-mpf('1.678059')/(2*mpf('8.32891')), '0.89926', '>')
show('(da) total', mpf('0.319921')/3+1/(3*mpf('0.985789')*mpf('0.89926'))-mpf(2)/3, '-0.184', '<')
print('--- escape-y-monotone')
show('first fact', mpf('0.2')-mpf('0.00284209')-3*c*sqrt(mpf('0.2'))*mpf('0.0533113'), '0.168623', '>')
show('1.5 c eps0', mpf(3)/2*c*eps0, '0.032', '<=')
xi = mpf('0.2')
show('third a', (1+xi*eps0)/(12*xi**2*k0**T3), '0.112250', '<')
show('third b', 3/(8*sqrt(xi)*k0**T3), '0.044703', '<')
show('(na) U first', (mpf(3)/2*sqrt(xi)-mpf(1)/2/sqrt(xi)*k0**(-2*T3))/(2*c), '0.8367662', '>')
show('(na) U second', mpf(3)/4*eps0*(1+(1-1/(xi*k0**(2*T3)))**(-mpf(1)/2)), '0.0802540', '<')
show('(na) U third', (k0+1)/(2*k0)*(1-1/(xi*k0**(2*T3)))**(-mpf(3)/2)/(xi**2*k0**(2*T3)), '0.0363026', '<')
print('--- closed-form (ga)')
show('phi', exp(-1/(12*qmin)), '0.998816', '>')
show('rho1', mpf(3)/2*xe, '0.4798811', '<')
xi = mpf('6.001')
show('rho2', mpf(5)/8*(1+3/(4*pmin))*(1+xi*eps0)**(mpf(5)/2)*xi**2*k0**(-2*T3), '0.129421', '<=')
show('U theta1', xi**(mpf(3)/2)/(2*c), '18.42449', '<=')
show('U ups', (k0+1)/k0*(1-mu)**(-mpf(1)/2), '1.00734', '<=')
show('quot', mpf('0.3895139')/mpf('19.43183'), '0.020044', '>=')
print('--- closed-form (na)')
xi = mpf('0.1')
br = (mpf('0.4')*xi**(mpf(3)/2)+mpf('0.5775')*sqrt(xi)*k0**(-2*T3))*(1+xi*eps0)**(mpf(3)/2)
show('br(0.1)', br, '0.013274', '<=')
show('0.20789/2', mpf('0.20789')/2, '0.103945', '<=')
q = xi*k0**(2*T3)
p = q-1
print('q,p at 0.1', mp.nstr(q, 10), mp.nstr(p, 10))
show('z/q', mpf('0.20789')/q, '0.005909', '<=')
show('p^-3/2/(12q)', p**(-mpf(3)/2)/(12*q), '0.000012', '<=')
xi = mpf('2.1')
br = (mpf('0.4')*xi**(mpf(3)/2)+mpf('0.5775')*sqrt(xi)*k0**(-2*T3))*(1+xi*eps0)**(mpf(3)/2)
show('br(2.1)', br, '1.430101', '<=')
print('margin(0.1..2.1)', mp.nstr(mpf('1.46035')-mpf('0.005909')-mpf('0.000012')-mpf('1.430101'), 8))
print('margin(<=0.1)', mp.nstr(mpf('1.46035')-mpf('0.103945')-mpf('0.041667')-mpf('0.013274'), 8))
print('--- closed-form (da)')
xi = mpf(2)
q = xi*k0**(2*T3)
p = q-1
mu2 = 1/q
show('q>=', q, '703.708', '>')
show('rho1 deriv', (sqrt(1-mu2)-(1+p**(-mpf(1)/2))*eps0/sqrt(xi))/2, '0.480085', '>=')
show('dtheta1', eps0/sqrt(2)/(3*c), '0.0314973', '<=')
show('dtheta3', (1+1/(4*p))/2, '0.5001779', '<=')
show('V coef', mpf(1)/2-mpf(3)/2*mu2-mpf(3)/4*eps0/sqrt(xi), '0.46959', '>=')
show('U low', 1+(xi**(mpf(3)/2)-sqrt(xi)*k0**(-2*T3))/(2*c)-mpf(3)/2*xi*eps0, '4.37993', '>=')
show('final', mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'), '0.02536', '>=')
print('--- (ra)')


def jinf(x):
    return mpf(4)/3*c*x**(mpf(3)/2)


show('e^-j(2)', exp(-jinf(mpf(2))), '0.222127', '>=')
show('e^-j(2.1)', exp(-jinf(mpf('2.1'))), '0.198148', '<=')
cpsi = -z12+z32/12


def Psilow(x):
    return c*(2*sqrt(x)-cpsi+1/(2*sqrt(x))-x**(-mpf(3)/2)/24)


def Hf(p):
    return mpf(2)/3*p**(mpf(3)/2)+sqrt(p)/2+zm12+p**(-mpf(1)/2)/24


def Esc(xi, k):
    q = xi*k**(2*T3)
    p = q-1
    n = k+q
    kk = k+1
    e = k**(-T3)
    E = 2*c*exp(-1/(12*q))*xi**(-mpf(1)/2)*(1+xi*e)
    R1 = mpf(3)/2*c*(2*sqrt(p)-1)*k**(-2*T3)
    R2 = mpf(15)/8*c*n**(mpf(5)/2)*Hf(p)/(kk**(mpf(7)/2)*k**(2*T3))
    D1 = p/k**(2*T3)
    D2 = kk*sqrt(2/pi)*p**(-mpf(1)/2)*k**(-2*T3)
    D3 = mpf(3)/2*kk*Psilow(p)/((n+1)*k**(2*T3))
    return (E-R1-R2)/(D1+D2-D3)


show('Esc6600(2)', Esc(mpf(2), k0), '0.213721', '<=')
show('Esc6600(2.1)', Esc(mpf('2.1'), k0), '0.200904', '>=')
print('Esc6600(6.001)', mp.nstr(Esc(mpf('6.001'), k0), 8), 'Esc6600(0.2)', mp.nstr(Esc(mpf('0.2'), k0), 8))
print('Esc_k(3) for k=6600,1e4,1e6,1e9:', [mp.nstr(Esc(mpf(3), mpf(kk)), 8) for kk in (6600, 10**4, 10**6, 10**9)])
print('--- 8.2 tail')
show('1.15/6^1.5', mpf('1.15')/mpf(6)**(mpf(3)/2), '0.079', '<')
print('--- hazard')
show('1.1935', mpf(3)/2-mpf('0.307')*(1-mpf(3)/(2*6667)), '1.1935', '<=')
show('log(2/1.0537)', log(2/mpf('1.0537')), '0.64084', '<')
show('1/1.0537', 1/mpf('1.0537'), '0.94904', '<')
show('log(2/1.49)', log(2/mpf('1.49')), '0.29438', '<')
show('1/1.49', 1/mpf('1.49'), '0.67115', '<')
show('G(.0537)', mpf('1.41945')-mpf('1.1935')*mpf('0.64084')-mpf('0.94904')+mpf('0.5'), '0.205', '>')
show('G(.49)', mpf('0.765')-mpf('1.1935')*mpf('0.29438')-mpf('0.67115')+mpf('0.5'), '0.242', '>')
show('3.2/k', mpf('3.2')/6667, '0.0005', '<=')
show('47/24+1.1935', mpf(47)/24+mpf('1.1935'), '3.2', '<=')
k = mpf(6667)
show('nu/k low', mpf(3)/32-mpf(3)/4*k**(-T3)+mpf('0.53')/k, '0.0537', '>=')
for kk in [6667, 6668, 7000, 10000, 13823, 13824, 10**5, 10**6, 10**9]:
    qmax = int(floor(6*mpf(kk)**(2*T3)))
    qfb = int(floor((mpf(3)*(kk-1)/4-qmax-3)/8))
    mfb = int(math.ceil(5*kk/4))+qmax
    print(kk, 'qmax', qmax, 'qfb', qfb, '(qfb+2)/k', float(mpf(qfb+2)/kk),
          '2k+1-8qfb>=mfb', 2*kk+1-8*qfb >= mfb, 'qfb<k/4', qfb < kk/4,
          'qmax<=0.48k', qmax <= 0.48*kk, 'qfb>=qmax', qfb >= qmax,
          'case(ii) nonempty', kk/4+1 <= min(qmax, 0.48*kk))
print('6k^(2/3)-6(k-1)^(2/3) at 6668:', mp.nstr(6*mpf(6668)**(2*T3)-6*mpf(6667)**(2*T3), 8))
print('K=1e5: 6*K^(2/3)=', mp.nstr(6*mpf(10)**(mpf(10)/3), 12), ' xi_12927=', mp.nstr(12927/mpf(10)**(mpf(10)/3), 12))
print('J16', 3000*2**16)
print('(4c)^(2/3)', mp.nstr((4*c)**(2*T3), 8), ' (2pi)^(-1/3)', mp.nstr((2*pi)**(-T3), 8))
print('2/(3 sqrt3)', mp.nstr(2/(3*sqrt(3)), 8))
# 9i >= 5(n+1) 문턱
for kk in (411, 412, 413, 421, 422):
    print(kk, 9*(kk+2) >= 5*(kk+6*mpf(kk)**(2*T3)+1))
