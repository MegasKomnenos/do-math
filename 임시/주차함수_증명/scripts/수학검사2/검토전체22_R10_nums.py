# -*- coding: utf-8 -*-
# R10: recompute constants quoted in appendix A / C rows.
import mpmath as mp, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mp.mp.dps = 30
def ub(k): return mp.mpf('1.15')/mp.mpf('0.35')*(2+mp.mpf(1)/k)*(mp.mpf('0.65')-mp.mpf(1)/k)**(-1.5)*mp.mpf(k)**(-0.5)
def ddl(k): return 14*(mp.log(3*k)-1)/(5*mp.sqrt(mp.pi*k))+mp.mpf('37.6')/(5*mp.sqrt(mp.pi)*k)
def v(k): return 2-mp.mpf('4.6')/mp.sqrt(k+1)-2*ub(k)-ddl(k)/2
print('v(6667)=', v(6667), ' v(2001)=', v(2001), ' v(6668)=', v(6668))
print('v increasing on 2001..20000 step:', all(v(k+1) > v(k) for k in range(2001, 20000, 7)))
print('DDLnat decreasing k>=7:', all(ddl(k+1) < ddl(k) for k in range(7, 5000)), ' ddl(6)->ddl(7):', ddl(6), ddl(7), 'ddl(5)', ddl(5))
print('f1=4/(3sqrt(2pi))=', 4/(3*mp.sqrt(2*mp.pi)))
print('s_B=e/sqrt(2pi)=', mp.e/mp.sqrt(2*mp.pi))
print('theta0=(2e^-0.48-1)e^-0.48=', (2*mp.e**mp.mpf('-0.48')-1)*mp.e**mp.mpf('-0.48'))
z12 = mp.zeta(mp.mpf(1)/2); z32 = mp.zeta(mp.mpf(3)/2); zm12 = mp.zeta(-mp.mpf(1)/2)
print('zeta(1/2),zeta(-1/2),zeta(3/2)=', z12, zm12, z32)
print('c_Psi=-z12+z32/12=', -z12+z32/12)
print('a0=', mp.quad(lambda w: mp.e**(-w**3/3), [0, mp.inf]), ' 3^(-2/3)Gamma(1/3)=', 3**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3))
print('a1=', mp.quad(lambda w: w*mp.e**(-w**3/3), [0, mp.inf]), ' Gamma(2/3)3^(-1/3)=', mp.gamma(mp.mpf(2)/3)*3**(-mp.mpf(1)/3))
print('n_inf=2/sqrt(pi)=', 2/mp.sqrt(mp.pi))
print('(2pi)^-1/2=', 1/mp.sqrt(2*mp.pi), ' 4/3*(2pi)^-1/2=', mp.mpf(4)/3/mp.sqrt(2*mp.pi))
# n^sharp_k <= k^2+2k <= 19880 for k<=140
def tk(k):
    j = 0
    while (k+1)**j*k**(j+1)+(k-1)**(2*j+1) < 2*k**(2*j+1): j += 1
    return j
mx = max(k+(k+1)*tk(k) for k in range(2, 141))
print('max n^sharp_k (2<=k<=140)=', mx, ' 140^2+280=', 140*140+280, ' all <= k^2+2k:', all(k+(k+1)*tk(k) <= k*k+2*k for k in range(2, 141)), ' k=141:', 141+(142)*tk(141), 141*141+282)
# kappa: x_k = (k/(k+1))^(k-1)
print('x_k at 2000:', (mp.mpf(2000)/2001)**1999, ' 1/e=', 1/mp.e)
# m(n) at 20001
def mfun(n):
    m = 170; c = 171
    while c**1.5+9*c <= n: m = c; c += 1
    return m
print('m(20001)=', mfun(20001), ' m(50001)=', mfun(50001))
# R_2 first column: 3k-1>=20001 -> k>=6668 ; 6667 = min{k:3k>=20001}
print(min(k for k in range(1, 10000) if 3*k >= 20001), min(k for k in range(1, 10000) if 3*k-1 >= 20001))
# q_fb and m_fb sanity at k=6668
import math
k = 6668; qmax = math.floor(6*k**(2/3)); print('qmax(6668)=', qmax, ' q_fb=', math.floor((3*(k-1)/4-qmax-3)/8), ' m_fb=', math.ceil(5*k/4)+qmax)
