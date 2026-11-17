# R8: 보조정리 hazard-H1 과 정리 old-6-33 의 수치 재계산
from mpmath import mp, mpf, log, exp, floor, ceil
mp.dps = 25
k = mpf(6667)
print('3/2-0.307(1-3/(2k))', mpf(3)/2 - mpf('0.307')*(1-3/(2*k)), '<=1.1935')
def G(z): return mpf(3)/2*(1-z) - mpf('1.1935')*log(2/(1+z)) - 1/(1+z) + mpf(1)/2
for z in ['0.0537','0.49']:
    z=mpf(z); print('G(',z,')=',G(z), ' log(2/(1+z))',log(2/(1+z)), ' 1/(1+z)',1/(1+z))
print('3.2/k', mpf('3.2')/k, '<=0.0005', ' 47/24+1.1935', mpf(47)/24+mpf('1.1935'))
# log bound: log((1-1/(2k))/(1-1/(k(1+z)))) <= 1/k ?
for z in ['0.0537','0.49']:
    z=mpf(z); print('log ratio', log((1-1/(2*k))/(1-1/(k*(1+z)))), '<=', 1/k)
# q_fb etc at k=6668
for kk in [6668, 13824, 13825, 20000]:
    kk = mpf(kk); qmax = floor(6*kk**(mpf(2)/3)); qfb = floor((3*(kk-1)/4 - qmax - 3)/8); mfb = ceil(5*kk/4)+qmax
    print('k',kk,'qmax',qmax,'qfb',qfb,'mfb',mfb,'2k+1-8qfb',2*kk+1-8*qfb, ' qfb<k/4', qfb<kk/4, ' k/4', kk/4, ' 0.48k', mpf('0.48')*kk, ' (qfb+2)/k', (qfb+2)/kk)
    print('   bound 3/32-3/4 k^-1/3+0.53/k', mpf(3)/32 - mpf(3)/4*kk**(-mpf(1)/3) + mpf('0.53')/kk)
    print('   6k^2/3-6(k-1)^2/3', 6*kk**(mpf(2)/3)-6*(kk-1)**(mpf(2)/3))
    print('   n-k-qmax >= k/4 at nu=103:', kk+103-qmax, kk/4)
