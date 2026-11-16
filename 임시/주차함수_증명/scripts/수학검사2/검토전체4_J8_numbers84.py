# J8 검토: 장8 8.4절(정리 old-6-29 (2), 보조정리 hazard-H1)의 수치 재계산
from mpmath import mp, mpf, sqrt, log, floor, ceil
mp.dps = 30
for k in [6667, 6668, 10**5]:
    k = mpf(k)
    qmax = floor(6*k**(mpf(2)/3))
    qfb = floor((3*(k-1)/4 - qmax - 3)/8)
    print(f"k={k}: q_max={qmax}, q_fb={qfb}, k-2399-(q_max+300)={k-2399-(qmax+300)}, 3k/4-(2398+q_max)={3*k/4-(2398+qmax)}, q_fb<k/4? {qfb<k/4}, (q_fb+2)/k={(qfb+2)/k}, 3/32-3/4k^-1/3+0.53/k={mpf(3)/32-mpf(3)/4*k**(-mpf(1)/3)+mpf('0.53')/k}, 2k+1-8q_fb-m_fb={2*k+1-8*qfb-(ceil(5*k/4)+qmax)}")
print("(k/(k-1))^(2/3) at 6668 =", (mpf(6668)/6667)**(mpf(2)/3))
print("6*6600^(2/3) =", 6*mpf(6600)**(mpf(2)/3), " <= 6603")
def G(z): return mpf(3)/2*(1-z) - mpf('1.1935')*log(2/(1+z)) - 1/(1+z) + mpf(1)/2
for z in ['0.0537','0.571']:
    z=mpf(z); print(f"G({z}) = {G(z)}; pieces: {mpf(3)/2*(1-z)}, {log(2/(1+z))}, {1/(1+z)}")
print("3/2-0.307(1-3/(2k)) at k=6667 =", mpf(3)/2-mpf('0.307')*(1-3/(2*mpf(6667))))
print("47/24+1.1935 =", mpf(47)/24+mpf('1.1935'), " 3.2/6667 =", mpf('3.2')/6667)
# hazard prefactor positivity at nu=104,k=6667
print("prefactor at nu=q_fb+2~? use nu=104:", 1-mpf('0.798')/sqrt(105)-mpf('0.81')/sqrt(6667))
# log bound check: log((2k-1)/(k+nu-1)) <= log(2/(1+z)) + 1/k at k=6667, z=0.0537
k=mpf(6667); nu=mpf('0.0537')*k
print("log diff:", log((2*k-1)/(k+nu-1)) - log(2/(1+nu/k)), " vs 1/k =", 1/k)
# old-6-30 (다) constant: e^{7/6}/(4 c)
from mpmath import e, pi
print("e^(7/6)/(4(2pi)^-1/2) =", e**(mpf(7)/6)/(4/sqrt(2*pi)))
