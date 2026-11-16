# 검토전체19 M10: 10장 상수 재계산(배정밀도/ mpmath 50자리). 결과는 파일로.
from mpmath import mp, mpf, quad, log, sqrt, exp, pi, e, factorial, power, findroot
mp.dps = 40

def q(r): return 1 + mpf('0.7501')*r/(1+r)
j2 = quad(lambda r: sqrt((1+r)/r)*mpf('0.70836')*q(r)**3, [0, mpf('1e-8'), mpf('0.01'), 1])
j1 = quad(lambda r: sqrt((1+r)/r)*mpf('0.70836')*q(r)**3*(mpf('2.528571')-log(q(r))+mpf('1.5')*log(r)), [0, mpf('1e-8'), mpf('0.01'), 1])
print('j2', j2); print('j1', j1)

def DDLnat(k):
    k = mpf(k); dn = 2*k**(mpf(2)/3)
    eps = -log(1 - sqrt(k+1)/(mpf('0.485917')*k))
    epsp = mpf('2.26')/k + mpf('0.47')/(dn-1)
    gam = mpf('2.6047')*(mpf('2.53') + log(k)/2 + eps + mpf('1.5')/k)/k
    c = 1/sqrt(2*pi)
    return mpf('0.457143')*c*q(dn/k)*sqrt(1+dn/k)*(dn+1)**mpf('3.5')/k**3 + 2*c/sqrt(k)*(1+epsp)*(j1+(log(k)/2+eps)*j2+gam) + mpf('3.9')*c/k
for k in [6667, 6668, 8065, 9551, 9705, 9949]:
    print('DDLnat', k, DDLnat(k))
print('decrease cond', j1 + j2*(log(6667)/2 - 1))

# 5단계 상수
iota0 = mpf('2.528571') - log(mpf('1.0722')) + log(2**mpf('1.5')*(1-1/(2*mpf(6667)**(mpf(2)/3)))**mpf('1.5'))
print('iota0 lower', iota0)
s0 = exp(-mpf('3.4964')/mpf('1.5')); print('sigma0', s0)
print('bracket', 2*mpf('3.4964')-6-mpf('0.1728')*sqrt(s0))
# theta_1 root of (1-t)^{5/2} - 1 + 2t
print('theta1', findroot(lambda t: (1-t)**mpf('2.5') - 1 + 2*t, mpf('0.28')))
# vartheta_0
v0 = (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')); print('vartheta0', v0)
# two-tree constant
print('pi_two const', 1/sqrt(2*pi)/e*2**mpf('1.5'), 1/mpf('0.41508'))
# bulk e-bar at 6668
def ebar(k):
    k = mpf(k); xi = (sqrt(5*k*log(k))+2)/k
    return exp(mpf(3)/(2*k))*(exp(sqrt(5*log(k)/k)+1/k) + mpf('2.40918')*k**(mpf('1.5')-mpf('2.5')/(1+xi)))
print('ebar 6668', ebar(6668), 'mhit', sqrt(5*6668*log(mpf(6668))))
# u(k), BdT, abar, bbar, dbar
def u(k): k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**mpf('-1.5')/sqrt(k)
def BdT(k,nu): k=mpf(k); nu=mpf(nu); return (k+nu)*u(k)*(1/(k-1)+1/k) + 3*(k+1)*(k-1)**mpf('-1.5')
k0=6668
print('abar', 3*mpf('1.15')*(mpf('1.48')*k0+2)/(mpf('0.48')*k0+1)**mpf('1.5'))
print('bbar', BdT(k0,k0), 'dbar', mpf('72.217')/sqrt(k0))
print('bracket 0.54577', mpf('0.48')**mpf('-0.5')-1+(1-sqrt(mpf('0.48')))/3, 132.32*0.54577)
# 1a pieces at 9705
k=mpf(9705); nup=mpf('1.3')*k**(mpf(2)/3)
ec = 3*nup**2/((k-1)*k) + mpf('4.8')*sqrt(nup)/k + nup**2/(2*(k-1)**2)
print('ec 1a', ec, 'BdT 1a', BdT(9705, nup), 'nu_min 9705', 20001-2*9705, nup)
# family 1b, 2 pieces
k=mpf(9551); print('1b: 3 s_up', 3*min(1, mpf('1.15')*(k+1+mpf('1.3')*k**(mpf(2)/3)+1)/(mpf('1.3')*k**(mpf(2)/3)+1)**mpf('1.5')), 'theta part', (2*exp(-2*k**(mpf(2)/3)/(k-1))-1)*exp(-2*k**(mpf(2)/3)/(k-1)), 'BdT', BdT(9551, 2*k**(mpf(2)/3)), '2k^2/3', 2*k**(mpf(2)/3), 20001-2*9551)
k=mpf(8065); print('2: 3 s_up', 3*min(1, mpf('1.15')*(k+1+2*k**(mpf(2)/3)+1)/(2*k**(mpf(2)/3)+1)**mpf('1.5')), 'BdT', BdT(8065, mpf('0.48')*k), 0.48*8065, 20001-2*8065)
# Robbins check on Bor bound constant 2(2pi)^{-1/2}
print('2/sqrt(2pi)', 2/sqrt(2*pi), '2/sqrt(pi)', 2/sqrt(pi))
# E coefficient checks (old-8-25 step 7)
def Ecoef(ups, qq=389):
    ups=mpf(ups); qq=mpf(qq)
    return 2/sqrt(2*pi)*((1-1/(2*qq))**mpf('-1.5')/4 + (1+ups+ups**2)*(1-ups)**mpf('-0.5')*(1+ups)**mpf('-1.5'))
print('Ecoef 0.9', Ecoef('0.9'), 'Ecoef 0.99', Ecoef('0.99'), 'Ecoef 0.9999', Ecoef('0.9999'))
print('F at 0.99', 2/sqrt(2*pi)*3*sqrt(1-mpf('0.99')**2), 'F at .9', 2/sqrt(2*pi)*3*sqrt(1-mpf('0.81')))
# (1.15*6666)^(2/3)
print('(1.15*6666)^(2/3)', (mpf('1.15')*6666)**(mpf(2)/3))
# cR, beta0 etc.
cR = sqrt(2*pi)/2*exp(mpf(1)/12); print('cR', cR, 'beta0 min', cR*mpf('1.04')**mpf('1.5')/sqrt(2), 'g_e(1.0216)', exp(-mpf('1.0216'))*(1+1.5*mpf('1.0216')), 'iota q0 max', cR*2**(mpf(2)/3)*mpf(6669)**(-mpf(1)/3))
print('cAb(0.6) etc', 2*(2*sqrt(mpf('0.6'))/(0.4)+2*log((1+sqrt(mpf('0.6')))/(1-sqrt(mpf('0.6')))))-4/sqrt(mpf('0.6')), 2*sqrt(mpf('0.6'))/mpf('0.4'))
print('eps0s', [int((2**(mpf(2)/3)*(k+1)**(mpf(2)/3))) for k in [6668,8065,9551,9705]])
print('1.5(2k+3)^(2/3) at 6667', 1.5*(2*6667+3)**(2/3), 0.48*6667)
print('3.9 check', 2*0.72888*1.3751**2*2**0.5)
print('0.70836 check', 3*2**0.5*0.16696, '2.528571 check', 2.5 - float(log(2)) - float(log(mpf('0.485917'))))
print('0.16696 check', 1.00057**2*(1+2/6667)**2/6)
print('u(6667) and 2*0.7654 vs 1.3502', 2*0.7654)
